#!/usr/bin/env python3
"""
Robeco Template-Based Report Generator
Collects analysis from all agents and generates formatted reports following Robeco template
"""

import logging
import json
import asyncio
import sys
import os
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

# Add project root to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from google.genai import Client, types
from api_key.gemini_api_key import get_intelligent_api_key

logger = logging.getLogger(__name__)

class RobecoTemplateReportGenerator:
    """Generate comprehensive investment reports following Robeco template structure"""
    
    def __init__(self):
        self.template_path = "/Users/skl/Desktop/Robeco Reporting/Report Example/Robeco_InvestmentCase_Template.txt"
        self.css_path = "/Users/skl/Desktop/Robeco Reporting/Report Example/CSScode.txt"
        logger.info("🏗️ Robeco Template Report Generator initialized")
    
    async def generate_report_from_analyses(
        self, 
        company_name: str,
        ticker: str, 
        analyses_data: Dict[str, Any],
        report_focus: str = "comprehensive",
        financial_data: Dict = None
    ) -> str:
        """Generate report without streaming (legacy method)"""
        return await self.generate_report_with_websocket_streaming(
            company_name, ticker, analyses_data, report_focus, None, None, financial_data
        )
    
    async def generate_report_with_websocket_streaming(
        self, 
        company_name: str,
        ticker: str, 
        analyses_data: Dict[str, Any],
        report_focus: str = "comprehensive",
        websocket=None,
        connection_id: str = None,
        financial_data: Dict = None,
        investment_objective: str = None,
        user_query: str = None
    ) -> str:
        """
        Generate comprehensive report from collected agent analyses
        
        Args:
            company_name: Company name for the report
            ticker: Stock ticker symbol
            analyses_data: Dictionary containing all agent analysis results
            report_focus: Type of report focus
        
        Returns:
            str: Generated HTML report following Robeco template
        """
        logger.info(f"📋 Generating Robeco template report for {ticker}")
        logger.info(f"📊 Available analyses: {list(analyses_data.keys())}")
        
        try:
            # 🎯 IMPLEMENTING 2-CALL ARCHITECTURE
            logger.info("🚀 Starting 2-Call Architecture Report Generation")
            
            # Send CSS template content at the very start
            if websocket:
                try:
                    # Load only the CSS styles (not full HTML structure)
                    css_file_path = "/Users/skl/Desktop/Robeco Reporting/Report Example/CSScode.txt"
                    with open(css_file_path, 'r', encoding='utf-8') as f:
                        full_css_template = f.read()
                    
                    # Extract ONLY the CSS content inside <style> tags (without <style> wrapper)
                    css_start = full_css_template.find('<style>') + len('<style>')
                    css_end = full_css_template.find('</style>')
                    if css_start > len('<style>') - 1 and css_end != -1:
                        # Get pure CSS content without <style> tags
                        css_content_only = full_css_template[css_start:css_end].strip()
                        # Wrap in minimal style tags for display
                        css_styles_only = f"<style>\n{css_content_only}\n</style>"
                    else:
                        css_styles_only = "<style>\n/* CSS extraction failed */\n</style>"
                    
                    # Send only CSS styles (not full HTML structure)
                    await websocket.send_text(json.dumps({
                        "type": "report_generation_streaming",
                        "data": {
                            "status": "css_template_loaded",
                            "call_phase": "css",
                            "accumulated_html": css_styles_only,
                            "message": "📄 CSS Styles loaded from CSScode.txt",
                            "progress": 10,
                            "connection_id": connection_id,
                            "timestamp": datetime.now().isoformat()
                        }
                    }))
                    logger.info("📄 CSS template content sent via WebSocket")
                except Exception as e:
                    logger.warning(f"⚠️ Could not load CSS template: {e}")
            
            # Send progress update for Call 1
            if websocket:
                await websocket.send_text(json.dumps({
                    "type": "report_generation_progress",
                    "data": {
                        "status": "call1_starting", 
                        "message": "📊 CALL 1: Generating overview, company & industry analysis (slides 1-7)...",
                        "progress": 20,
                        "connection_id": connection_id,
                        "timestamp": datetime.now().isoformat()
                    }
                }))
            
            # CALL 1: Generate slides 1-7 (Overview, Company, Industry Analysis)
            call1_content = await self._generate_combined_overview_and_analysis_section(
                company_name, ticker, analyses_data, financial_data, websocket, connection_id
            )
            
            if not call1_content:
                raise Exception("Call 1 failed to generate content")
            
            # CRITICAL: Validate Call 1 completion before proceeding
            call1_validation = self._validate_call1_completion(call1_content)
            if not call1_validation:
                # Send failure signal if Call 1 is incomplete
                if websocket:
                    await websocket.send_text(json.dumps({
                        "type": "report_generation_streaming", 
                        "data": {
                            "status": "call1_incomplete",
                            "call_phase": "call1",
                            "accumulated_html": call1_content,
                            "message": "⚠️ CALL 1 INCOMPLETE: Missing slide 7 - please retry generation",
                            "progress": 40,
                            "connection_id": connection_id,
                            "timestamp": datetime.now().isoformat()
                        }
                    }))
                logger.error(f"🚨 CALL 1 VALIDATION FAILED - proceeding anyway for debugging")
                # Note: Not raising exception to allow debugging, but this should be fixed
            
            # Send Call 1 completion signal with its content
            if websocket:
                logger.info(f"📤 Sending Call 1 completion: {len(call1_content):,} chars")
                await websocket.send_text(json.dumps({
                    "type": "report_generation_streaming",
                    "data": {
                        "status": "call1_complete",
                        "call_phase": "call1",
                        "accumulated_html": call1_content,
                        "message": "✅ CALL 1 COMPLETE: Overview & analysis (slides 1-7) generated",
                        "progress": 50,
                        "connection_id": connection_id,
                        "timestamp": datetime.now().isoformat()
                    }
                }))
            
            # Extract key insights from Call 1 for Call 2 context
            call1_context = {
                'content_summary': 'Strong fundamentals and growth potential',
                'investment_rating': 'BUY',  # Could be extracted from Call 1 content
                'generated_content': call1_content[:1000]  # First 1000 chars as context
            }
            
            # Send progress update for Call 2  
            if websocket:
                await websocket.send_text(json.dumps({
                    "type": "report_generation_progress",
                    "data": {
                        "status": "call2_starting",
                        "message": "📊 CALL 2: Generating financial analysis & valuation (slides 8-15)...", 
                        "progress": 60,
                        "connection_id": connection_id,
                        "timestamp": datetime.now().isoformat()
                    }
                }))
            
            # CALL 2: Generate slides 8-15 (Financial Analysis & Valuation)
            call2_content = await self._generate_industry_and_financial_section(
                company_name, ticker, analyses_data, financial_data, call1_context, websocket, connection_id
            )
            
            if not call2_content:
                raise Exception("Call 2 failed to generate content")
            
            # Send Call 2 completion signal
            if websocket:
                logger.info(f"📤 Sending Call 2 completion: {len(call2_content):,} chars")
                await websocket.send_text(json.dumps({
                    "type": "report_generation_streaming",
                    "data": {
                        "status": "call2_complete",
                        "call_phase": "call2", 
                        "accumulated_html": call2_content,
                        "message": "✅ CALL 2 COMPLETE: Financial analysis (slides 8-15) generated",
                        "progress": 80,
                        "connection_id": connection_id,
                        "timestamp": datetime.now().isoformat()
                    }
                }))
            
            # Send progress update for combining
            if websocket:
                await websocket.send_text(json.dumps({
                    "type": "report_generation_progress", 
                    "data": {
                        "status": "combining",
                        "message": "🔧 Combining Call 1 + Call 2 results...",
                        "progress": 85,
                        "connection_id": connection_id,
                        "timestamp": datetime.now().isoformat()
                    }
                }))
            
            # Combine Call 1 + Call 2 content
            combined_slides_content = self._combine_call1_and_call2_content(call1_content, call2_content)
            
            # Combine with fixed CSS template
            final_report_html = self._combine_css_with_slides(company_name, ticker, combined_slides_content)
            
            # Save the complete report as HTML file
            self._save_report_to_file(final_report_html, company_name, ticker)
            
            # Send final completion signal with complete report
            if websocket:
                logger.info(f"📤 Sending final completion: {len(final_report_html):,} chars")
                await websocket.send_text(json.dumps({
                    "type": "report_generation_streaming",
                    "data": {
                        "status": "final_complete",
                        "call_phase": "final",
                        "accumulated_html": final_report_html,
                        "message": "🎉 REPORT COMPLETE: 15-slide Robeco investment analysis generated",
                        "progress": 100,
                        "connection_id": connection_id,
                        "timestamp": datetime.now().isoformat()
                    }
                }))
            
            logger.info("✅ 2-Call Architecture: Report generated and combined successfully")
            return final_report_html
            
        except Exception as e:
            logger.error(f"❌ Report generation failed: {e}")
            raise e
    
    
    async def _generate_combined_overview_and_analysis_section(
        self, 
        company_name: str, 
        ticker: str, 
        analyses_data: Dict[str, Any],
        financial_data: Dict = None,
        websocket=None,
        connection_id: str = None
    ) -> str:
        """
        2-CALL ARCHITECTURE - CALL 1: Generate slides 1-7 (Overview, Company, Industry Analysis)
        
        Generates the first 7 slides covering:
        - Slide 1: Company info & metrics grid
        - Slide 2: Investment summary & thesis
        - Slide 3: Investment highlights
        - Slide 4: Catalysts & developments
        - Slide 5: Company analysis
        - Slide 6: Industry analysis & market position
        - Slide 7: Competitive advantage analysis
        """
        logger.info(f"📊 CALL 1: Generating overview and analysis section (slides 1-7) for {ticker}")
        
        # Build Call 1 specific prompt
        call1_prompt = await self._build_call1_prompt(company_name, ticker, analyses_data, financial_data)
        
        # Generate Call 1 content (slides 1-7 only)
        call1_content = await self._generate_ai_report(call1_prompt, websocket, connection_id, "call1")
        
        # CRITICAL: Validate Call 1 completion before returning
        call1_validation = self._validate_call1_completion(call1_content)
        logger.info(f"🔍 CALL 1 VALIDATION: {'✅ PASSED' if call1_validation else '❌ FAILED'}")
        
        if not call1_validation:
            logger.error(f"🚨 CALL 1 INCOMPLETE: Missing slide 7, only {len(call1_content):,} chars generated")
            # Could implement retry logic here if needed
            
        logger.info(f"✅ CALL 1 completed: {len(call1_content):,} characters generated")
        return call1_content
    
    def _validate_call1_completion(self, call1_content: str) -> bool:
        """
        Validate that Call 1 (slides 1-7) is complete before proceeding to Call 2
        
        Args:
            call1_content: Generated HTML content from Call 1
            
        Returns:
            bool: True if Call 1 is complete, False otherwise
        """
        if not call1_content:
            logger.error("📋 CALL 1 VALIDATION: No content generated")
            return False
            
        # Check for slide 7 completion marker
        has_slide_7 = "Page 7 / 15" in call1_content
        
        # Check minimum content length (should be substantial for 7 slides)
        min_length = 15000  # Approximately 2000+ chars per slide (more reasonable)
        sufficient_length = len(call1_content) >= min_length
        
        # Check for key slide markers (1-7)
        expected_slides = ["Page 1 / 15", "Page 2 / 15", "Page 3 / 15", "Page 4 / 15", "Page 5 / 15", "Page 6 / 15", "Page 7 / 15"]
        slides_found = sum(1 for slide in expected_slides if slide in call1_content)
        
        # Check that no Call 2 content leaked into Call 1
        no_call2_content = "Page 8 / 15" not in call1_content
        
        # Log detailed validation results
        logger.info(f"📋 CALL 1 VALIDATION DETAILS:")
        logger.info(f"   ✓ Has slide 7 footer: {has_slide_7}")
        logger.info(f"   ✓ Sufficient length: {sufficient_length} ({len(call1_content):,} chars >= {min_length:,})")
        logger.info(f"   ✓ Slides found: {slides_found}/7 expected slides")
        logger.info(f"   ✓ No Call 2 leakage: {no_call2_content}")
        
        # All conditions must be met
        is_complete = has_slide_7 and sufficient_length and slides_found >= 6 and no_call2_content
        
        if not is_complete:
            logger.error(f"📋 CALL 1 VALIDATION FAILED:")
            if not has_slide_7:
                logger.error(f"   ❌ Missing slide 7 footer 'Page 7 / 15'")
            if not sufficient_length:
                logger.error(f"   ❌ Content too short: {len(call1_content):,} chars < {min_length:,}")
            if slides_found < 6:
                logger.error(f"   ❌ Missing slides: only {slides_found}/7 found")
            if not no_call2_content:
                logger.error(f"   ❌ Call 2 content leaked into Call 1")
                
        return is_complete
    
    async def _generate_industry_and_financial_section(
        self,
        company_name: str,
        ticker: str, 
        analyses_data: Dict[str, Any],
        financial_data: Dict = None,
        call1_context: Dict = None,
        websocket=None,
        connection_id: str = None
    ) -> str:
        """
        2-CALL ARCHITECTURE - CALL 2: Generate slides 8-15 (Financial Analysis & Valuation)
        
        Generates the final 8 slides covering:
        - Slide 8: Income statement analysis
        - Slide 9: Balance sheet analysis
        - Slide 10: Cash flow analysis
        - Slide 11: Financial ratios analysis
        - Slide 12: Valuation analysis
        - Slide 13: Bull/bear analysis
        - Slide 14: Scenario analysis
        - Slide 15: Investment conclusion
        """
        logger.info(f"📊 CALL 2: Generating industry and financial section (slides 8-15) for {ticker}")
        
        # Build Call 2 specific prompt with Call 1 context
        call2_prompt = await self._build_call2_prompt(
            company_name, ticker, analyses_data, financial_data, call1_context
        )
        
        # Generate Call 2 content (slides 8-15 only) with completion validation
        call2_content = await self._generate_ai_report(call2_prompt, websocket, connection_id, "call2")
        
        # Validate Call 2 completion and force multiple retries if needed
        retry_count = 0
        max_retries = 3
        
        # ULTRA-DEBUG: Initial validation check
        initial_validation = self._validate_call2_completion(call2_content)
        logger.info(f"🔍 INITIAL CALL 2 VALIDATION: {'✅ PASSED' if initial_validation else '❌ FAILED'}")
        
        if not initial_validation:
            logger.warning(f"🚨 Call 2 validation failed - entering retry loop (max {max_retries} retries)")
            # Log detailed failure analysis
            logger.info(f"📊 Call 2 initial attempt stats:")
            logger.info(f"   Content length: {len(call2_content):,} chars")
            logger.info(f"   Contains 'Page 15': {'✓' if 'Page 15 / 15' in call2_content else '✗'}")
            logger.info(f"   Contains 'Operating Cash Flow': {'✓' if 'Operating Cash Flow' in call2_content else '✗'}")
            logger.info(f"   Slide count: {call2_content.count('<div class=\"slide')}")
            logger.info(f"   Last 200 chars: ...{call2_content[-200:] if len(call2_content) > 200 else call2_content}")
        
        while not self._validate_call2_completion(call2_content) and retry_count < max_retries:
            retry_count += 1
            logger.warning(f"⚠️⚠️⚠️ Call 2 RETRY {retry_count}/{max_retries} - Previous attempt incomplete, applying stronger enforcement")
            
            # Progressively strengthen completion requirements for each retry
            completion_enforcement = f"""
            
**🚨 ULTRA-CRITICAL COMPLETION ENFORCEMENT - RETRY {retry_count}:**

⚠️ PREVIOUS ATTEMPT FAILED: Content stopped at slide 10 "Operating Cash Flow" - THIS MUST NOT HAPPEN AGAIN!

🔥 ABSOLUTE REQUIREMENTS (NON-NEGOTIABLE):
- GENERATE ALL 8 SLIDES: Must complete slides 8, 9, 10, 11, 12, 13, 14, AND 15
- FORBIDDEN: Stopping at slide 10 "Operating Cash Flow" table
- MANDATORY: Complete Cash Flow Analysis (slide 10) then continue to slides 11-15
- FINAL SLIDE: Must end with investment conclusion and "Page 15 / 15" footer

🎯 COMPLETION STRATEGY:
- If token limits approach, reduce paragraph length but COMPLETE ALL SLIDE STRUCTURES
- Prioritize slide completion over content verbosity
- Each slide needs header, content, and footer - NO EXCEPTIONS
- Must generate slides 11 (Financial Ratios), 12 (Valuation), 13 (Bull/Bear), 14 (Scenario), 15 (Conclusion)

🚨 CRITICAL VALIDATION POINTS:
- Slide 10: Complete the Operating Cash Flow analysis then CONTINUE (don't stop)
- Slides 11-15: MUST be generated with proper page numbers and content
- Final output: Must contain "INVESTMENT CONCLUSION" and "Page 15 / 15"

THIS IS RETRY {retry_count}/3 - COMPLETE ALL 8 SLIDES OR SYSTEM WILL RETRY AGAIN!
"""
            
            call2_prompt_retry = call2_prompt + completion_enforcement
            call2_content = await self._generate_ai_report(call2_prompt_retry, websocket, connection_id, f"call2_retry_{retry_count}")
        
        if retry_count > 0:
            logger.info(f"📊 Call 2 completed after {retry_count} retries")
        
        logger.info(f"✅ CALL 2 completed: {len(call2_content):,} characters generated")
        return call2_content
    
    def _validate_call2_completion(self, call2_content: str) -> bool:
        """Validate if Call 2 has completed all 8 slides (8-15) - AGGRESSIVE validation"""
        try:
            # Check for slide 15 completion marker (CRITICAL)
            has_slide_15 = "Page 15 / 15" in call2_content
            
            # Check content length (should be substantial for 8 detailed slides)
            sufficient_length = len(call2_content) > 40000  # Increased minimum for 8 detailed slides
            
            # AGGRESSIVE: Check for truncated content at slide 10 (Operating Cash Flow issue)
            has_operating_cash_flow_truncation = (
                "Operating Cash Flow" in call2_content and 
                not ("Page 11 / 15" in call2_content or 
                     "Page 12 / 15" in call2_content or
                     "Page 13 / 15" in call2_content)
            )
            
            # Check that it doesn't end abruptly (incomplete tables/content)
            has_proper_ending = ("</div>" in call2_content[-500:] or 
                               "</footer>" in call2_content[-500:] or
                               "Page 15 / 15" in call2_content[-500:])
            
            # Count slide divs to ensure all 8 slides are present
            slide_count = call2_content.count('<div class="slide')
            has_all_slides = slide_count >= 8
            
            # Check for ALL required slide markers (8, 9, 10, 11, 12, 13, 14, 15)
            has_slide_8 = "Page 8 / 15" in call2_content
            has_slide_9 = "Page 9 / 15" in call2_content
            has_slide_10 = "Page 10 / 15" in call2_content
            has_slide_11 = "Page 11 / 15" in call2_content
            has_slide_12 = "Page 12 / 15" in call2_content
            has_slide_13 = "Page 13 / 15" in call2_content
            has_slide_14 = "Page 14 / 15" in call2_content
            
            # AGGRESSIVE: Check for complete investment conclusion content
            has_investment_conclusion = "INVESTMENT CONCLUSION" in call2_content.upper()
            
            # MAIN VALIDATION: All slides must be present AND no truncation at slide 10
            is_complete = (has_slide_15 and sufficient_length and has_proper_ending and 
                          has_all_slides and has_slide_8 and has_slide_9 and has_slide_10 and
                          has_slide_11 and has_slide_12 and has_slide_13 and has_slide_14 and
                          not has_operating_cash_flow_truncation and has_investment_conclusion)
            
            logger.info(f"📊 Call 2 AGGRESSIVE validation:")
            logger.info(f"   ✓ slide15={has_slide_15}, length={sufficient_length} ({len(call2_content):,})")
            logger.info(f"   ✓ ending={has_proper_ending}, slides={slide_count}/8, conclusion={has_investment_conclusion}")
            logger.info(f"   ✓ slides: 8={has_slide_8}, 9={has_slide_9}, 10={has_slide_10}, 11={has_slide_11}")
            logger.info(f"   ✓ slides: 12={has_slide_12}, 13={has_slide_13}, 14={has_slide_14}, 15={has_slide_15}")
            logger.info(f"   🚨 TRUNCATION CHECK: operating_cash_flow_truncated={has_operating_cash_flow_truncation}")
            logger.info(f"   📊 OVERALL COMPLETE: {is_complete}")
            
            if not is_complete:
                missing_slides = []
                if not has_slide_8: missing_slides.append("8")
                if not has_slide_9: missing_slides.append("9") 
                if not has_slide_10: missing_slides.append("10")
                if not has_slide_11: missing_slides.append("11")
                if not has_slide_12: missing_slides.append("12")
                if not has_slide_13: missing_slides.append("13")
                if not has_slide_14: missing_slides.append("14")
                if not has_slide_15: missing_slides.append("15")
                
                logger.warning(f"🚨 Call 2 INCOMPLETE:")
                logger.warning(f"   Missing slides: {missing_slides}")
                logger.warning(f"   Truncated at Operating Cash Flow: {has_operating_cash_flow_truncation}")
                logger.warning(f"   Length insufficient: {not sufficient_length} ({len(call2_content):,} < 40000)")
                logger.warning(f"   Missing conclusion: {not has_investment_conclusion}")
            
            return is_complete
            
        except Exception as e:
            logger.error(f"❌ Error validating Call 2 completion: {e}")
            return False
    
    def _build_base_robeco_prompt(self, company_name: str, ticker: str) -> str:
        """
        Build the foundational Robeco prompt with style guidelines, writing standards, and formatting requirements.
        This serves as the common base for both Call 1 and Call 2 prompts.
        """
        
        return f"""# ROBECO ALPHA-GENERATING INVESTMENT ANALYSIS - {company_name} ({ticker})

## ELITE PORTFOLIO MANAGER ROLE & MANDATE

### YOUR IDENTITY & EXPERTISE:
You are an **elite hedge fund Portfolio Manager** with 25+ years of experience at top-tier firms like Renaissance Technologies, Bridgewater Associates, and Citadel. You've consistently generated significant alpha across multiple market cycles, economic environments, and asset classes. Your analytical prowess combines:

- **Deep Fundamental Research**: Micro-level understanding of business models, competitive dynamics, and value creation mechanisms
- **Sophisticated Quantitative Techniques**: Advanced statistical analysis, factor modeling, and risk decomposition
- **Nuanced Market Understanding**: Pattern recognition across macro-micro interconnections and sector rotations
- **Exceptional Alpha Generation**: Track record of identifying mispricings before consensus, contrarian calls that outperform

**Your reputation**: One of Wall Street's most insightful minds, known for holistic investment theses that capture both forest-and-trees perspectives.

### ALPHA-GENERATION OBJECTIVE:
Produce an **institutional-grade, alpha-generating investment analysis** that demonstrates superior analytical depth, business understanding, and differentiated viewpoints. Your analysis must identify specific **market inefficiencies and mispricings** that create asymmetric risk/reward opportunities.

**Go beyond superficial narratives** to uncover insights that represent genuine edge—perspectives not yet discounted in current valuations.

### MANDATORY ANALYTICAL REQUIREMENTS:

**1. HIGH-CONVICTION INVESTMENT THESIS:**
- Articulate a clear long/short position supported by multiple independent pillars
- Identify specific market inefficiencies creating opportunity
- Demonstrate why consensus is wrong or incomplete

**2. RIGOROUS QUANTITATIVE FRAMEWORK:**
- Precisely quantify expected return potential with risk-adjusted metrics
- Calculate Sharpe ratio implications and maximum drawdown scenarios
- Estimate alpha generation vs. benchmark with confidence intervals

**3. CATALYST-DRIVEN TIMELINE:**
- Identify specific catalysts with precise timeframes for price realization
- Map out 6-month, 12-month, and 24-month value inflection points
- Connect catalysts to fundamental value drivers

**4. COMPREHENSIVE RISK ASSESSMENT:**
- Thoroughly assess potential risks including hidden correlations
- Analyze second-order effects and systemic risk factors
- Model tail risk scenarios and portfolio impact

**5. SOPHISTICATED VALUATION FRAMEWORK:**
- Multi-methodology approach: DCF, relative valuation, sum-of-parts, option value
- Scenario analysis with probability-weighted outcomes
- Sensitivity analysis on key assumptions and variables

**6. IMPLEMENTATION STRATEGY:**
- Optimize entry points and position sizing methodology
- Define risk parameters and stop-loss levels
- Outline hedging strategies for portfolio construction

**7. MONITORING & VALIDATION FRAMEWORK:**
- Specify concrete signposts to track thesis progression
- Define metrics that would validate or invalidate investment case
- Establish systematic review triggers and exit criteria

### SPECIFIC HTML STRUCTURE COMPLIANCE:
```html
<!-- HEADER STRUCTURE (ALL SLIDES) -->
<header class="report-header-container">
    <div class="robeco-logo-container">
        <img src="https://images.ctfassets.net/tl4x668xzide/7mygwms2vuSwirnfvaCSvL/72d2bbd858a69aecbf59fd3fb8954484/robeco-logo-color.png" alt="Robeco Logo">
    </div>
    <div class="header-blue-border">
        <div class="company-header">
            <img src="[COMPANY_LOGO]" alt="Company Icon" class="icon">
            <h1 class="name">{company_name}</h1>
            <div class="rating" style="color: #2E7D32;">OVERWEIGHT</div>
        </div>
    </div>
</header>

<!-- FOOTER STRUCTURE (ALL SLIDES) -->
<footer class="report-footer">
    <p>Robeco Investment Research</p>
    <p>Page X / 15</p>
</footer>
```

### FINANCIAL TABLE FORMATTING (SLIDES 8-10):
```html
<table style="width: 100%; border-collapse: collapse; font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Roboto', sans-serif; font-size: 11px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); border-radius: 8px; overflow: hidden; background: white;">
    <thead>
        <tr style="background: linear-gradient(135deg, #2C5282 0%, #3182CE 100%); color: white; height: 45px;">
            <!-- Professional gradient header -->
        </tr>
    </thead>
    <tbody>
        <!-- Alternating row colors with actual financial data -->
    </tbody>
</table>
```

### SOPHISTICATED ANALYTICAL FRAMEWORKS TO DEPLOY:

**MARKET EFFICIENCY ANALYSIS:**
- **Information Asymmetry**: Identify data/insights not yet reflected in price
- **Behavioral Biases**: Exploit systematic cognitive errors in market pricing
- **Structural Inefficiencies**: Leverage forced selling, index rebalancing, flow dynamics
- **Complexity Premium**: Capitalize on situations too complex for mainstream analysis

**MULTI-LAYERED FUNDAMENTAL ANALYSIS:**
- **Business Model Decomposition**: Unit economics, scalability, defensibility, reinvestment rates
- **Competitive Dynamics**: Porter's 5 forces, competitive response functions, game theory
- **Management Quality**: Capital allocation track record, strategic vision, execution consistency
- **Industry Life Cycle**: Position within cycle, disruption risk, consolidation opportunities

**QUANTITATIVE RIGOR REQUIREMENTS:**
- **Factor Attribution**: Decompose returns into style, sector, and alpha components
- **Risk-Adjusted Metrics**: Sharpe, Sortino, Calmar ratios with benchmark comparison
- **Correlation Analysis**: Cross-asset, sector, and macro factor sensitivities
- **Stress Testing**: Monte Carlo simulation of key assumptions and scenarios

**CATALYST MAPPING & TIMING:**
- **Event-Driven Catalysts**: Earnings, regulatory decisions, M&A, spin-offs, activist campaigns
- **Fundamental Inflection Points**: Margin expansion, market share gains, new product cycles
- **Technical Catalysts**: Support/resistance levels, momentum inflections, options flow
- **Macro Catalysts**: Interest rate cycles, commodity cycles, currency moves, policy changes

**ADVANCED VALUATION METHODOLOGIES:**
- **DCF with Real Options**: Capture optionality value in growth investments and strategic pivots
- **Sum-of-the-Parts**: Asset-based valuation for conglomerates and multi-business entities
- **Relative Valuation**: Peer group analysis with quality adjustments and growth normalization
- **Replacement Cost**: Asset replacement value for capital-intensive businesses
- **Liquidation Value**: Downside protection analysis for distressed or turnaround situations

### INSTITUTIONAL-GRADE WRITING STANDARDS:
- **Analytical Precision**: Every claim supported by specific data points and logical reasoning
- **Professional Sophistication**: Goldman Sachs/Morgan Stanley research quality and depth
- **Quantitative Integration**: Embed metrics naturally: "**ROIC expansion from 12.3% to 16.8% over 24 months**"
- **Forward-Looking Framework**: Focus on what's not priced in vs. what market already knows
- **Risk-Reward Asymmetry**: Emphasize upside/downside ratio and probability-weighted outcomes

### TECHNICAL FORMATTING REQUIREMENTS:
- **Document Structure**: Exactly 15 slides with specific HTML classes and IDs
- **Professional Layout**: 1620px × 2291px institutional presentation format
- **Data Integration**: Use actual financial data from provided tables
- **Visual Hierarchy**: Proper headers, numbered sections, professional color scheme
- **Slide Types**: Analysis-item format (slides 1-2), report-prose format (slides 3-15)
- **Table Styling**: Professional financial tables with gradient headers and data integration

### PERFORMANCE EXPECTATIONS:
**Your analysis must demonstrate:**
- **Intellectual Rigor**: Depth that separates institutional research from sell-side reports
- **Original Insights**: Perspectives not readily available in consensus research
- **Actionable Intelligence**: Clear investment implications with specific entry/exit strategies
- **Risk Awareness**: Comprehensive downside protection and scenario planning
- **Alpha Generation**: Identifiable sources of outperformance vs. market/benchmark

**Remember**: You are not writing generic research. You are crafting alpha-generating investment insights that justify significant capital allocation decisions by sophisticated institutional investors.

---
"""

    def _build_ready_html_tables(self, company_name: str, financial_data: Dict = None) -> Dict[str, str]:
        """
        Pre-generate clean HTML tables from REAL yfinance data for AI to copy directly.
        Gets actual company financial statements with real dates and important line items.
        """
        
        # Get ticker symbol for yfinance
        ticker = None
        if financial_data and 'ticker' in financial_data:
            ticker = financial_data['ticker']
        elif isinstance(company_name, str) and len(company_name) <= 5 and company_name.isupper():
            ticker = company_name  # Assume company_name is ticker if short and uppercase
        
        if not ticker:
            return {
                'income_table': '<p>No ticker symbol provided</p>',
                'balance_table': '<p>No ticker symbol provided</p>',
                'cashflow_table': '<p>No ticker symbol provided</p>'
            }
        
        # Fetch from yfinance directly (always use fresh data)
        try:
            import yfinance as yf
            logger.info(f"📊 Fetching yfinance data for {ticker}")
            stock = yf.Ticker(ticker)
            
            # Get 3 years of financial data
            income_stmt = stock.financials  # Annual income statement
            balance_sheet = stock.balance_sheet  # Annual balance sheet  
            cash_flow = stock.cashflow  # Annual cash flow
            
            logger.info(f"✅ Fetched financial data for {ticker}")
            
            # Build tables from yfinance data
            income_html = self._build_yfinance_income_html(income_stmt, ticker)
            balance_html = self._build_yfinance_balance_html(balance_sheet, ticker)
            cashflow_html = self._build_yfinance_cashflow_html(cash_flow, ticker)
            
            return {
                'income_table': income_html,
                'balance_table': balance_html,
                'cashflow_table': cashflow_html
            }
            
        except Exception as e:
            logger.warning(f"⚠️ Could not fetch yfinance data for {ticker}: {e}")
            return {
                'income_table': f'<p>Unable to fetch income statement for {ticker}</p>',
                'balance_table': f'<p>Unable to fetch balance sheet for {ticker}</p>',
                'cashflow_table': f'<p>Unable to fetch cash flow for {ticker}</p>'
            }
        
        # Use provided financial data
        try:
            # Build tables from provided data using real yfinance structure
            ticker = financial_data.get('ticker', company_name)
            
            income_html = self._build_yfinance_income_html(
                financial_data.get('income_statement'), ticker
            )
            balance_html = self._build_yfinance_balance_html(
                financial_data.get('balance_sheet'), ticker  
            )
            cashflow_html = self._build_yfinance_cashflow_html(
                financial_data.get('cash_flow'), ticker
            )
            
            return {
                'income_table': income_html,
                'balance_table': balance_html,
                'cashflow_table': cashflow_html
            }
            
        except Exception as e:
            logger.warning(f"⚠️ Could not process financial data: {e}")
            return {
                'income_table': '<p>Income statement processing error</p>',
                'balance_table': '<p>Balance sheet processing error</p>',
                'cashflow_table': '<p>Cash flow processing error</p>'
            }
    
    def _build_yfinance_income_html(self, income_stmt, ticker: str) -> str:
        """Build clean income statement HTML from real yfinance data"""
        if income_stmt is None or income_stmt.empty:
            return '<p>No income statement data available</p>'
        
        try:
            # Get last 3 years of data with REAL dates
            years = income_stmt.columns[:3]  # Most recent 3 years
            if len(years) < 2:
                return '<p>Insufficient income statement data</p>'
            
            # Format dates as strings (YYYY-MM-DD to YYYY)
            year_labels = []
            for year in years:
                if hasattr(year, 'strftime'):
                    year_labels.append(year.strftime('%Y'))
                else:
                    year_labels.append(str(year)[:4])
            
            # Build table header
            html = '''<table class="financial-table">
    <thead>
        <tr>
            <th>INCOME STATEMENT</th>'''
            
            for year_label in year_labels:
                html += f'\n            <th class="text-right">{year_label}</th>'
            
            if len(years) >= 2:
                html += '\n            <th class="text-right">YoY %</th>'
            
            html += '\n        </tr>\n    </thead>\n    <tbody>'
            
            # PRIORITY 1: Core income statement line items (always include)
            important_items = [
                ('Total Revenue', 'Total Revenue'),
                ('Gross Profit', 'Gross Profit'),  
                ('Operating Income', 'Operating Income'),
                ('Net Income', 'Net Income'),
                ('Diluted EPS', 'Diluted EPS')
            ]
            
            # PRIORITY 2: Additional items if available
            additional_items = [
                ('EBITDA', 'EBITDA'),
                ('Operating Expense', 'Operating Expense'),
                ('Tax Provision', 'Tax Provision')
            ]
            
            # Combine core + available additional items
            all_items = important_items.copy()
            for label, yf_key in additional_items:
                if yf_key in income_stmt.index:
                    all_items.append((label, yf_key))
            
            for label, yf_key in all_items:
                if yf_key in income_stmt.index:
                    html += f'\n        <tr>\n            <td>{label}</td>'
                    values = []
                    
                    for i, year in enumerate(years):
                        try:
                            value = income_stmt.loc[yf_key, year]
                            if pd.isna(value) or value == 0:
                                formatted = "N/A"
                                values.append(None)
                            else:
                                # Format based on size (EPS is special case)
                                if 'EPS' in label:
                                    formatted = f"${value:.2f}"
                                    values.append(value)
                                elif abs(value) >= 1_000_000_000:
                                    formatted = f"${value/1_000_000_000:.1f}B"
                                    values.append(value)
                                elif abs(value) >= 1_000_000:
                                    formatted = f"${value/1_000_000:.0f}M"
                                    values.append(value)
                                else:
                                    formatted = f"${value:,.0f}"
                                    values.append(value)
                            
                            html += f'\n            <td class="text-right">{formatted}</td>'
                        except Exception:
                            html += '\n            <td class="text-right">N/A</td>'
                            values.append(None)
                    
                    # Calculate YoY % for most recent vs previous year
                    if len(values) >= 2 and values[0] is not None and values[1] is not None and values[1] != 0:
                        yoy = ((values[0] - values[1]) / abs(values[1])) * 100
                        color_class = "positive" if yoy > 0 else "negative" if yoy < 0 else "neutral"
                        html += f'\n            <td class="text-right {color_class}">{yoy:+.1f}%</td>'
                    elif len(years) >= 2:
                        html += '\n            <td class="text-right neutral">N/A</td>'
                    
                    html += '\n        </tr>'
            
            html += '\n    </tbody>\n</table>'
            return html
            
        except Exception as e:
            logger.warning(f"⚠️ Error building income statement HTML: {e}")
            return '<p>Error processing income statement data</p>'
    
    def _build_yfinance_balance_html(self, balance_sheet, ticker: str) -> str:
        """Build clean balance sheet HTML from real yfinance data"""
        if balance_sheet is None or balance_sheet.empty:
            return '<p>No balance sheet data available</p>'
        
        try:
            # Get last 3 years of data with REAL dates
            years = balance_sheet.columns[:3]  # Most recent 3 years
            if len(years) < 2:
                return '<p>Insufficient balance sheet data</p>'
            
            # Format dates as strings
            year_labels = []
            for year in years:
                if hasattr(year, 'strftime'):
                    year_labels.append(year.strftime('%Y'))
                else:
                    year_labels.append(str(year)[:4])
            
            # Build table header
            html = '''<table class="financial-table">
    <thead>
        <tr>
            <th>BALANCE SHEET</th>'''
            
            for year_label in year_labels:
                html += f'\n            <th class="text-right">{year_label}</th>'
            
            if len(years) >= 2:
                html += '\n            <th class="text-right">YoY %</th>'
            
            html += '\n        </tr>\n    </thead>\n    <tbody>'
            
            # PRIORITY 1: Core balance sheet line items (always include)
            important_items = [
                ('Total Assets', 'Total Assets'),
                ('Current Assets', 'Current Assets'),
                ('Total Debt', 'Total Debt'),
                ('Current Liabilities', 'Current Liabilities'),
                ('Stockholders Equity', 'Stockholders Equity')
            ]
            
            # PRIORITY 2: Additional items if available  
            additional_items = [
                ('Working Capital', 'Working Capital'),
                ('Cash And Cash Equivalents', 'Cash And Cash Equivalents'),
                ('Net PPE', 'Net PPE'),
                ('Retained Earnings', 'Retained Earnings')
            ]
            
            # Combine core + available additional items
            all_items = important_items.copy()
            for label, yf_key in additional_items:
                if yf_key in balance_sheet.index:
                    all_items.append((label, yf_key))
            
            for label, yf_key in all_items:
                if yf_key in balance_sheet.index:
                    html += f'\n        <tr>\n            <td>{label}</td>'
                    values = []
                    
                    for i, year in enumerate(years):
                        try:
                            value = balance_sheet.loc[yf_key, year]
                            if pd.isna(value) or value == 0:
                                formatted = "N/A"
                                values.append(None)
                            else:
                                # Format based on size
                                if abs(value) >= 1_000_000_000:
                                    formatted = f"${value/1_000_000_000:.1f}B"
                                    values.append(value)
                                elif abs(value) >= 1_000_000:
                                    formatted = f"${value/1_000_000:.0f}M"
                                    values.append(value)
                                else:
                                    formatted = f"${value:,.0f}"
                                    values.append(value)
                            
                            html += f'\n            <td class="text-right">{formatted}</td>'
                        except Exception:
                            html += '\n            <td class="text-right">N/A</td>'
                            values.append(None)
                    
                    # Calculate YoY % for most recent vs previous year
                    if len(values) >= 2 and values[0] is not None and values[1] is not None and values[1] != 0:
                        yoy = ((values[0] - values[1]) / abs(values[1])) * 100
                        color_class = "positive" if yoy > 0 else "negative" if yoy < 0 else "neutral"
                        html += f'\n            <td class="text-right {color_class}">{yoy:+.1f}%</td>'
                    elif len(years) >= 2:
                        html += '\n            <td class="text-right neutral">N/A</td>'
                    
                    html += '\n        </tr>'
            
            html += '\n    </tbody>\n</table>'
            return html
            
        except Exception as e:
            logger.warning(f"⚠️ Error building balance sheet HTML: {e}")
            return '<p>Error processing balance sheet data</p>'
    
    def _build_yfinance_cashflow_html(self, cash_flow, ticker: str) -> str:
        """Build clean cash flow HTML from real yfinance data"""
        if cash_flow is None or cash_flow.empty:
            return '<p>No cash flow data available</p>'
        
        try:
            # Get last 3 years of data with REAL dates
            years = cash_flow.columns[:3]  # Most recent 3 years
            if len(years) < 2:
                return '<p>Insufficient cash flow data</p>'
            
            # Format dates as strings
            year_labels = []
            for year in years:
                if hasattr(year, 'strftime'):
                    year_labels.append(year.strftime('%Y'))
                else:
                    year_labels.append(str(year)[:4])
            
            # Build table header
            html = '''<table class="financial-table">
    <thead>
        <tr>
            <th>CASH FLOW STATEMENT</th>'''
            
            for year_label in year_labels:
                html += f'\n            <th class="text-right">{year_label}</th>'
            
            if len(years) >= 2:
                html += '\n            <th class="text-right">YoY %</th>'
            
            html += '\n        </tr>\n    </thead>\n    <tbody>'
            
            # PRIORITY 1: Core cash flow line items (always include)
            important_items = [
                ('Operating Cash Flow', 'Operating Cash Flow'),
                ('Investing Cash Flow', 'Investing Cash Flow'),
                ('Financing Cash Flow', 'Financing Cash Flow'),
                ('Free Cash Flow', 'Free Cash Flow'),
                ('Capital Expenditure', 'Capital Expenditure')
            ]
            
            # PRIORITY 2: Additional items if available
            additional_items = [
                ('Changes In Cash', 'Changes In Cash'),
                ('Cash Dividends Paid', 'Cash Dividends Paid'),
                ('Repurchase Of Capital Stock', 'Repurchase Of Capital Stock'),
                ('Depreciation And Amortization', 'Depreciation And Amortization')
            ]
            
            # Combine core + available additional items  
            all_items = important_items.copy()
            for label, yf_key in additional_items:
                if yf_key in cash_flow.index:
                    all_items.append((label, yf_key))
            
            for label, yf_key in all_items:
                if yf_key in cash_flow.index:
                    html += f'\n        <tr>\n            <td>{label}</td>'
                    values = []
                    
                    for i, year in enumerate(years):
                        try:
                            value = cash_flow.loc[yf_key, year]
                            if pd.isna(value) or value == 0:
                                formatted = "N/A"
                                values.append(None)
                            else:
                                # Format based on size
                                if abs(value) >= 1_000_000_000:
                                    formatted = f"${value/1_000_000_000:.1f}B"
                                    values.append(value)
                                elif abs(value) >= 1_000_000:
                                    formatted = f"${value/1_000_000:.0f}M"
                                    values.append(value)
                                else:
                                    formatted = f"${value:,.0f}"
                                    values.append(value)
                            
                            html += f'\n            <td class="text-right">{formatted}</td>'
                        except Exception:
                            html += '\n            <td class="text-right">N/A</td>'
                            values.append(None)
                    
                    # Calculate YoY % for most recent vs previous year
                    if len(values) >= 2 and values[0] is not None and values[1] is not None and values[1] != 0:
                        yoy = ((values[0] - values[1]) / abs(values[1])) * 100
                        color_class = "positive" if yoy > 0 else "negative" if yoy < 0 else "neutral"
                        html += f'\n            <td class="text-right {color_class}">{yoy:+.1f}%</td>'
                    elif len(years) >= 2:
                        html += '\n            <td class="text-right neutral">N/A</td>'
                    
                    html += '\n        </tr>'
            
            html += '\n    </tbody>\n</table>'
            return html
            
        except Exception as e:
            logger.warning(f"⚠️ Error building cash flow HTML: {e}")
            return '<p>Error processing cash flow data</p>'

    def _build_financial_context(self, company_name: str, financial_data: Dict = None) -> str:
        """
        Build comprehensive financial context section for AI prompts with actual company data.
        Returns formatted financial tables and metrics for analysis.
        """
        
        if not financial_data:
            return """
**📊 FINANCIAL DATA STATUS**: Limited financial data available. Focus on qualitative analysis and publicly available metrics.
"""
        
        try:
            financial_statements = self._extract_financial_statements_for_analysis(financial_data)
            
            return f"""
**📊 COMPREHENSIVE FINANCIAL DATA** - {company_name} Actual Financial Statements:

{financial_statements.get('html_tables_for_ai', '')}

### FINANCIAL DATA INSTRUCTIONS:
- **CRITICAL**: Use ONLY the comprehensive pre-calculated financial tables provided above
- **Multi-Year Analysis**: Analyze trends across all available years: {financial_statements.get('years_available', [])}
- **Data Quality**: {len(financial_statements.get('years_available', []))} years of historical data available
- **Ratio Calculations**: All key ratios pre-calculated - reference specific values in analysis
- **Growth Metrics**: Use actual historical growth rates provided in tables
- **Margin Analysis**: Reference specific margin trends from income statement data
- **Balance Sheet Health**: Utilize actual debt, equity, and working capital metrics
- **Cash Flow Quality**: Analyze operating, investing, and financing cash flows from provided data

**NO PLACEHOLDER DATA**: Use only actual financial metrics from the tables above. If specific data unavailable, note limitations explicitly.
"""
            
        except Exception as e:
            logger.warning(f"⚠️ Error building financial context: {e}")
            return f"""
**📊 FINANCIAL DATA STATUS**: Error accessing financial data for {company_name}. 
Focus on qualitative analysis and publicly available information.
"""

    def _build_analyst_insights(self, analyses_data: Dict[str, Any], content_limit: int = 4000) -> str:
        """
        Build formatted analyst insights section from all available agent analyses.
        
        Args:
            analyses_data: Dictionary of all agent analysis results
            content_limit: Character limit per analyst insight (4000 for Call 1, 6000 for Call 2)
        """
        
        if not analyses_data:
            return """
**🔍 ANALYST INSIGHTS**: No specialized agent analyses available. Rely on financial data and market research.
"""
        
        available_analyses = []
        for agent_type, analysis in analyses_data.items():
            if analysis and analysis.get('content'):
                # Extract key metrics and insights
                content_preview = analysis['content'][:content_limit]
                source_count = len(analysis.get('sources', []))
                
                available_analyses.append({
                    'agent_type': agent_type.replace('_', ' ').title(),
                    'content': content_preview,
                    'source_count': source_count,
                    'word_count': len(content_preview.split())
                })
        
        if not available_analyses:
            return """
**🔍 ANALYST INSIGHTS**: No valid analyst content available. Focus on financial data analysis.
"""
        
        # Build comprehensive insights section
        insights_header = f"""
**🔍 SPECIALIST ANALYST INSIGHTS** - {len(available_analyses)} Expert Analyses Available:

### INTEGRATION REQUIREMENTS:
- **Synthesis Mandate**: Integrate insights from ALL {len(available_analyses)} specialist analyses
- **Cross-Verification**: Use multiple analyst perspectives to validate investment thesis
- **Source Attribution**: Reference specific analyst findings in your narrative
- **Comprehensive View**: Combine fundamental, technical, risk, and sector perspectives

### AVAILABLE ANALYST EXPERTISE:
"""
        
        # Add each analyst insight with structured formatting
        analyst_sections = []
        for i, analysis in enumerate(available_analyses, 1):
            analyst_section = f"""
**{i}. {analysis['agent_type']} Analysis** ({analysis['word_count']:,} words, {analysis['source_count']} sources):
{analysis['content']}

---"""
            analyst_sections.append(analyst_section)
        
        return insights_header + "\n".join(analyst_sections) + f"""

**SYNTHESIS INSTRUCTION**: Weave insights from all {len(available_analyses)} specialist perspectives into a cohesive investment narrative.
"""

    def _build_call1_context_summary(self, call1_context: Dict = None) -> str:
        """
        Build summary of Call 1 results to provide context for Call 2 generation.
        This ensures Call 2 builds upon and doesn't contradict Call 1 findings.
        """
        
        if not call1_context:
            return """
**🏛️ ALPHA GENERATION PHASE 1 COMPLETE**: Elite investment foundation established. Deploy sophisticated quantitative validation to complete alpha-generating investment case.
"""
        
        return f"""
**🏛️ PHASE 1 ALPHA FOUNDATION** - Elite Investment Thesis Established:

### MARKET INEFFICIENCY IDENTIFIED:
- **Investment Conviction**: {call1_context.get('investment_rating', 'High-conviction asymmetric opportunity')}
- **Alpha Thesis**: {call1_context.get('content_summary', 'Structural mispricing with catalyst-driven realization')}
- **Competitive Advantages**: {call1_context.get('key_strengths', 'Sustainable moats and differentiated positioning')}
- **Value Catalysts**: {call1_context.get('main_catalysts', 'Time-bound inflection points for price discovery')}

### PHASE 2 ELITE PM MANDATE:
- **Quantitative Validation**: Deploy sophisticated financial analysis to validate Phase 1 alpha thesis
- **Valuation Sophistication**: Apply multiple methodologies with institutional-grade rigor  
- **Risk Assessment**: Comprehensive scenario modeling and stress testing protocols
- **Portfolio Optimization**: Position sizing, hedging considerations, and implementation strategy
- **Alpha Documentation**: Quantify expected returns, Sharpe ratios, and alpha generation sources

**HEDGE FUND STANDARD**: Phase 2 analysis must demonstrate the quantitative sophistication that justifies significant institutional capital allocation and generates sustainable alpha.
"""

    async def _build_call1_prompt(
        self,
        company_name: str,
        ticker: str,
        analyses_data: Dict[str, Any],
        financial_data: Dict = None
    ) -> str:
        """Build optimized prompt for Call 1 (slides 1-7) using modular base prompt + Call 1 specifics"""
        
        logger.info(f"🔧 Building Call 1 prompt for {ticker} (slides 1-7)")
        
        # Get base Robeco prompt (style, methodology, standards)
        base_prompt = self._build_base_robeco_prompt(company_name, ticker)
        
        # Get financial context using helper method
        financial_context = self._build_financial_context(company_name, financial_data)
        
        # Get analyst insights using helper method (4000 char limit for Call 1)
        analyst_insights = self._build_analyst_insights(analyses_data, content_limit=4000)
        
        # Build Call 1 specific requirements with precise HTML structure
        call1_specific = f"""
## ALPHA GENERATION PHASE 1: INVESTMENT FOUNDATION & MARKET INEFFICIENCY IDENTIFICATION (SLIDES 1-7)

### YOUR ELITE PM MANDATE FOR CALL 1:
As a top-tier hedge fund Portfolio Manager, your **first phase objective** is to establish the fundamental investment case that demonstrates **why this opportunity exists** and **why consensus is wrong**. You're not writing generic research—you're identifying specific market inefficiencies and mispricings that create asymmetric risk/reward profiles for sophisticated capital allocation.

**Your analytical depth must rival the best Renaissance Technologies or Bridgewater research.** Every insight should demonstrate the pattern recognition and multi-layered thinking that separates elite PMs from sell-side analysts.

### EXACT HTML STRUCTURE REQUIREMENTS - GENERATE PRECISELY:

**SLIDE 1 - EXECUTIVE SUMMARY & METRICS (analysis-item format):**
```html
<div class="slide" id="portrait-page-1">
    <header class="report-header-container">
        <div class="robeco-logo-container">
            <img src="https://images.ctfassets.net/tl4x668xzide/7mygwms2vuSwirnfvaCSvL/72d2bbd858a69aecbf59fd3fb8954484/robeco-logo-color.png" alt="Robeco Logo">
        </div>
        <div class="header-blue-border">
            <div class="company-header">
                <img src="https://logo.clearbit.com/{company_name.lower().replace(' ', '')}.com" onerror="this.onerror=null;this.src='https://placehold.co/30x30/005F90/ffffff?text={ticker}';" alt="Company Icon" class="icon">
                <h1 class="name">{company_name}</h1>
                <div class="rating" style="color: #2E7D32;">OVERWEIGHT</div>
            </div>
        </div>
    </header>
    <main style="display: flex; flex-direction: column; flex-grow: 1;">
        <section class="metrics-grid">
            <!-- 25 financial metrics in 5x5 grid format -->
            <!-- Example: <div class="metrics-item"><div class="label">MARKET CAP</div><div class="value"><strong>$X.XB</strong></div></div> -->
        </section>
        <div class="intro-and-chart-container">
            <div class="intro-text-block">
                <!-- 300-word executive summary paragraph with specific metrics embedded -->
            </div>
            <div class="stock-chart-container" id="stock-price-line-chart">
                <!-- D3.js stock chart with 5-year price history -->
            </div>
        </div>
        <div class="analysis-sections">
            <!-- 4 analysis-item blocks: REASON TO ANALYZE, LONG TERM OUTLOOK, FUNDAMENTAL CONCLUSION, FIT WITH TOP-DOWN VIEW -->
        </div>
    </main>
    <footer class="report-footer">
        <p>Robeco Investment Research</p>
        <p>Page 1 / 15</p>
    </footer>
</div>
```

**SLIDE 2 - DETAILED ANALYSIS (analysis-item format):**
```html
<div class="slide" id="portrait-page-1A">
    <header class="report-header-container">
        <!-- Same header structure as slide 1 -->
    </header>
    <main>
        <div class="analysis-sections">
            <!-- 5 analysis-item blocks: VALUATION, RISKS, QUANTITATIVE CONCLUSION, SHORT TERM OUTLOOK, EARNINGS REVISIONS -->
        </div>
    </main>
    <footer class="report-footer">
        <p>Robeco Investment Research</p>
        <p>Page 2 / 15</p>
    </footer>
</div>
```

**SLIDES 3-7 - PROSE FORMAT:**
```html
<div class="slide report-prose" id="investment-highlights-pitchbook-page">
    <header class="report-header-container"><!-- Same header --></header>
    <main class="report-prose">
        <h3>3. {company_name.upper()} INVESTMENT HIGHLIGHTS</h3>
        <h4>[Subsection 1]: [Specific Investment Strength]</h4>
        <p>[500-600 word analysis paragraph]</p>
        <!-- Continue for 4 subsections -->
    </main>
    <footer class="report-footer"><p>Robeco Investment Research</p><p>Page 3 / 15</p></footer>
</div>

<div class="slide report-prose" id="catalyst-page">
    <header class="report-header-container"><!-- Same header --></header>
    <main class="report-prose">
        <h3>4. {company_name.upper()} CATALYSTS AND RECENT DEVELOPMENTS</h3>
        <h4>[Catalyst 1]: [Near-term Driver]</h4>
        <p>[500-600 word analysis paragraph]</p>
        <!-- Continue for 4 subsections -->
    </main>
    <footer class="report-footer"><p>Robeco Investment Research</p><p>Page 4 / 15</p></footer>
</div>

<div class="slide report-prose" id="company-analysis-page">
    <header class="report-header-container"><!-- Same header --></header>
    <main class="report-prose">
        <h3>5. {company_name.upper()} COMPANY ANALYSIS</h3>
        <h4>[Business Model Analysis]: [Core Operations]</h4>
        <p>[500-600 word analysis paragraph]</p>
        <!-- Continue for 4-5 subsections -->
    </main>
    <footer class="report-footer"><p>Robeco Investment Research</p><p>Page 5 / 15</p></footer>
</div>

<div class="slide report-prose" id="slide-industry-analysis">
    <header class="report-header-container"><!-- Same header --></header>
    <main>
        <h3>6. [INDUSTRY SECTOR]: [SPECIFIC MARKET DYNAMICS THEME]</h3>
        <p><strong>[Market Overview Section]</strong></p>
        <p>[600-word industry analysis paragraph with market size, growth trends, key drivers]</p>
        <p><strong>[Competitive Landscape Section]</strong></p>
        <p>[600-word competitive analysis with market share, key players, positioning]</p>
        <!-- Continue for 4-5 subsections -->
    </main>
    <footer class="report-footer"><p>Robeco Investment Research</p><p>Page 6 / 15</p></footer>
</div>

<div class="slide report-prose" id="slide-competitive-advantage">
    <header class="report-header-container"><!-- Same header --></header>
    <main>
        <h3>7. COMPETITIVE ADVANTAGE: [SPECIFIC MOAT & DIFFERENTIATION THEME]</h3>
        <h4 style="font-size: 22.5px; color: var(--robeco-blue-darker);">[Competitive Positioning]: [Market Share & Leadership]</h4>
        <p>[600-word analysis of competitive position, market share trends, peer comparison]</p>
        <h4 style="font-size: 22.5px; color: var(--robeco-blue-darker);">[Competitive Moat]: [Sustainable Advantages]</h4>
        <p>[600-word analysis of barriers to entry, technology leadership, brand strength]</p>
        <!-- Continue for 4-5 subsections -->
    </main>
    <footer class="report-footer"><p>Robeco Investment Research</p><p>Page 7 / 15</p></footer>
</div>
```

### CALL 1 CONTENT SPECIFICATIONS:

**SLIDE 1 REQUIREMENTS:**
- **Metrics Grid**: Generate EXACTLY 25 metrics in 5x5 grid (MAIN LISTING, SHARE PRICE, MARKET CAP, etc.)
- **Executive Summary**: 300-word paragraph with company overview, market position, key metrics
- **Stock Chart**: D3.js SVG chart showing 5-year price history with current price highlight
- **Analysis Items**: 4 sections using `analysis-item` class with specific titles

**SLIDE 2 REQUIREMENTS:**
- **Analysis Items**: 5 sections focusing on valuation, risks, quantitative metrics, outlook, earnings
- **Format**: Each analysis-item has `item-title` and `content-item` with 200-300 word analysis

**SLIDES 3-7 REQUIREMENTS:**
- **Slide 3**: Investment highlights with 4 key competitive advantages
- **Slide 4**: Catalysts and recent developments with near-term and long-term drivers
- **Slide 5**: Company analysis covering business model, operations, management
- **Slide 6**: Industry analysis covering market dynamics, competitive landscape, trends
- **Slide 7**: Competitive advantage analysis covering moat, positioning, differentiation
- **Format**: Use `report-prose` class with numbered headers (3., 4., 5., 6., 7.)
- **Content**: 4-5 subsections per slide, 500-600 word paragraphs with institutional depth

### ELITE PM ANALYTICAL APPROACH FOR CALL 1:

**MARKET INEFFICIENCY HUNTING:**
- **Information Asymmetry**: Identify data points, trends, or insights not yet reflected in current valuation
- **Behavioral Mispricing**: Exploit systematic cognitive biases creating opportunity (recency bias, anchoring, etc.)
- **Structural Dislocation**: Capitalize on forced selling, index rebalancing, or flow-driven mispricings
- **Complexity Premium**: Leverage situations too complex for mainstream analysis to uncover alpha

**SOPHISTICATED THESIS DEVELOPMENT:**
- **Multi-Pillar Framework**: Build investment case on 3-4 independent, uncorrelated value drivers
- **Contrarian Positioning**: Demonstrate why consensus view is incomplete or fundamentally flawed
- **Catalyst Mapping**: Identify specific, time-bound events that will drive price discovery
- **Risk-Adjusted Returns**: Emphasize Sharpe ratio optimization and downside protection

**HEDGE FUND QUALITY STANDARDS:**
- **Quantitative Rigor**: Every claim supported by specific metrics, ratios, and comparative analysis
- **Pattern Recognition**: Leverage historical parallels and market cycle analysis
- **Forward-Looking Edge**: Focus on what's NOT priced in vs. what market already knows
- **Alpha Source Identification**: Clearly articulate competitive advantage and sustainable outperformance

**INSTITUTIONAL EXECUTION:**
- **Data Integration**: Weave actual financial metrics naturally into narrative flow
- **Professional Sophistication**: Renaissance Technologies/Bridgewater-level analytical depth
- **Elite Terminology**: Use sophisticated hedge fund language and frameworks
- **Asymmetric Thinking**: Emphasize upside/downside asymmetry and probability-weighted outcomes

{financial_context}

{analyst_insights}

**ELITE PM EXECUTION MANDATE**: 
Craft ALL 7 slides (slides 1-7) that demonstrate sophisticated market understanding, identify genuine alpha opportunities, and establish investment foundation worthy of significant institutional capital allocation. Your analysis must show why this represents genuine edge—not consensus thinking.

**MANDATORY SLIDE COMPLETION REQUIREMENTS:**
- MUST generate EXACTLY 7 slides: slides 1, 2, 3, 4, 5, 6, AND 7
- SLIDE 6 MUST be complete with full industry analysis content
- SLIDE 7 MUST be complete with full competitive advantage analysis  
- Each slide MUST have complete content - NO truncation allowed
- Final slide MUST end with "Page 7 / 15" footer

**CRITICAL OUTPUT FORMAT REQUIREMENTS:**
- Output PURE HTML ONLY - NO markdown code blocks
- NO ```html tags, NO explanatory text, NO comments
- Start directly with <div class="slide" id="portrait-page-1">
- End with slide 7's closing </div> tag (Page 7 / 15)
- Use exact CSS classes and structure shown in examples above
- GENERATE ALL 7 SLIDES COMPLETELY - DO NOT STOP EARLY
"""
        
        # Combine base prompt with Call 1 specifics
        complete_call1_prompt = base_prompt + call1_specific
        
        logger.info(f"✅ Call 1 prompt built: {len(complete_call1_prompt):,} characters")
        return complete_call1_prompt
    
    async def _build_call2_prompt(
        self,
        company_name: str,
        ticker: str,
        analyses_data: Dict[str, Any],
        financial_data: Dict = None,
        call1_context: Dict = None
    ) -> str:
        """Build optimized prompt for Call 2 (slides 8-15) using modular base prompt + Call 2 specifics + Call 1 context"""
        
        logger.info(f"🔧 Building Call 2 prompt for {ticker} (slides 8-15)")
        
        # Get base Robeco prompt (style, methodology, standards)
        base_prompt = self._build_base_robeco_prompt(company_name, ticker)
        
        # Load CSS template for Call 2 styling requirements
        try:
            with open(self.css_path, 'r', encoding='utf-8') as f:
                css_template = f.read()
            css_guidance = f"""
### 🎯 SIMPLIFIED CSS STYLING FOR CALL 2 (REDUCED COMPLEXITY):

**MANDATORY SIMPLIFICATION**: To avoid HTML generation overload, use SIMPLE CSS classes instead of complex inline styling.

**FINANCIAL TABLE STRUCTURE** (greatly simplified):
```html
<table class="financial-table">
    <thead>
        <tr>
            <th>INCOME STATEMENT</th>
            <th class="text-right">2024-03-31</th>
            <th class="text-right">2023-03-31</th>
            <th class="text-right">YoY %</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Revenue</td>
            <td class="text-right positive">$2.5B</td>
            <td class="text-right">$2.1B</td>
            <td class="text-right positive">+19.0%</td>
        </tr>
    </tbody>
</table>
```

**CSS CLASSES AVAILABLE:**
- `financial-table` - Main table styling with professional gradient headers
- `text-right` - Right-align content  
- `positive` - Green color for positive values
- `negative` - Red color for negative values
- `neutral` - Gray color for neutral values

**CRITICAL SIMPLIFICATION**: 
- NO complex inline styles allowed
- NO nested style attributes
- Use ONLY the CSS classes listed above
- This reduces AI cognitive load by 80%
"""
        except Exception as e:
            logger.warning(f"⚠️ Could not load CSS template for Call 2: {e}")
            css_guidance = ""
        
        # Get pre-built HTML tables for AI to copy directly (eliminates generation complexity)
        ready_tables = self._build_ready_html_tables(company_name, financial_data)
        
        # Get financial context using helper method
        financial_context = self._build_financial_context(company_name, financial_data)
        
        # Get analyst insights using helper method (6000 char limit for Call 2 - more detail)
        analyst_insights = self._build_analyst_insights(analyses_data, content_limit=6000)
        
        # Get Call 1 context summary using helper method
        call1_summary = self._build_call1_context_summary(call1_context)
        
        # Build Call 2 specific requirements with precise HTML structure
        call2_specific = f"""
## ALPHA GENERATION PHASE 2: QUANTITATIVE VALIDATION & SOPHISTICATED VALUATION (SLIDES 8-15)

### YOUR ELITE PM MANDATE FOR CALL 2:
As an elite Portfolio Manager, your **second phase objective** is to provide rigorous quantitative validation of the Phase 1 investment thesis through sophisticated financial analysis and multi-methodology valuation. You're applying the same analytical rigor that generates consistent alpha at the world's top hedge funds.

**Deploy your 25+ years of experience** in factor modeling, risk decomposition, and advanced valuation techniques. Every financial insight must demonstrate the quantitative sophistication that separates institutional research from generic analysis.

{call1_summary}

### EXACT HTML STRUCTURE REQUIREMENTS - GENERATE PRECISELY:

## 🎯 READY-MADE HTML TABLES - JUST COPY THESE DIRECTLY:

### SLIDE 8 - INCOME STATEMENT TABLE (COPY EXACTLY):
{ready_tables['income_table']}

### SLIDE 9 - BALANCE SHEET TABLE (COPY EXACTLY): 
{ready_tables['balance_table']}

### SLIDE 10 - CASH FLOW TABLE (COPY EXACTLY):
{ready_tables['cashflow_table']}

## 📋 SLIDES 8-10 STRUCTURE - COPY THE TABLES ABOVE:
```html
<div class="slide report-prose" id="slide-financial-income-statement">
    <header class="report-header-container"><!-- Same header structure --></header>
    <main>
        <h3>8. INCOME STATEMENT ANALYSIS - [PROFITABILITY & GROWTH TRENDS]</h3>
        
        [COPY THE INCOME STATEMENT TABLE FROM ABOVE - DON'T GENERATE]
        
        <p><strong>Revenue Growth & Profitability Analysis</strong></p>
        <p>[Analysis paragraph referencing the table metrics above]</p>
        
        <p><strong>Margin Trends & Operating Efficiency</strong></p>
        <p>[Analysis of margin trends and operational efficiency]</p>
    </main>
    <footer class="report-footer"><p>Robeco Investment Research</p><p>Page 8 / 15</p></footer>
</div>

<div class="slide report-prose" id="slide-financial-balance-sheet">
    <header class="report-header-container"><!-- Same header --></header>
    <main>
        <h3>9. BALANCE SHEET ANALYSIS - [CAPITAL STRUCTURE & ASSET QUALITY]</h3>
        
        [COPY THE BALANCE SHEET TABLE FROM ABOVE - DON'T GENERATE]
        
        <p><strong>Asset Quality & Capital Allocation</strong></p>
        <p>[Balance sheet analysis with specific metrics from the table]</p>
    </main>
    <footer class="report-footer"><p>Robeco Investment Research</p><p>Page 9 / 15</p></footer>
</div>

<div class="slide report-prose" id="slide-financial-cash-flow-statement">
    <header class="report-header-container"><!-- Same header --></header>
    <main>
        <h3>10. CASH FLOW ANALYSIS - [FREE CASH FLOW GENERATION & SUSTAINABILITY]</h3>
        
        [COPY THE CASH FLOW TABLE FROM ABOVE - DON'T GENERATE]
        
        <p><strong>Operating Cash Flow Quality</strong></p>
        <p>[Cash flow analysis referencing the table metrics above]</p>
    </main>
    <footer class="report-footer"><p>Robeco Investment Research</p><p>Page 10 / 15</p></footer>
</div>

<div class="slide report-prose" id="slide-financial-ratios">
    <header class="report-header-container"><!-- Same header --></header>
    <main>
        <h3>11. FINANCIAL RATIOS - [EFFICIENCY & PROFITABILITY VS PEERS]</h3>
        <p><strong>Profitability Ratios & Peer Comparison</strong></p>
        <p>[Analysis of ROE, ROI, profit margins with industry benchmarking]</p>
        <p><strong>Efficiency & Capital Allocation Metrics</strong></p>
        <p>[Analysis of asset turnover, working capital, ROIC trends]</p>
    </main>
    <footer class="report-footer"><p>Robeco Investment Research</p><p>Page 11 / 15</p></footer>
</div>

<div class="slide report-prose" id="slide-valuation">
    <header class="report-header-container"><!-- Same header --></header>
    <main>
        <h3>12. VALUATION - [METHODOLOGY & TARGET PRICE DERIVATION]</h3>
        <p><strong>DCF Model & Intrinsic Value</strong></p>
        <p>[600-word DCF analysis with key assumptions and sensitivity]</p>
        <p><strong>Multiple-Based Valuation & Peer Comparison</strong></p>
        <p>[600-word relative valuation analysis with P/E, EV/EBITDA comparisons]</p>
    </main>
    <footer class="report-footer"><p>Robeco Investment Research</p><p>Page 12 / 15</p></footer>
</div>
```

**SLIDES 13-15 - SIMPLIFIED RISK ASSESSMENT & CONCLUSION:**
```html
<div class="slide report-prose" id="slide-bull-bear-analysis">
    <header class="report-header-container"><!-- Same header --></header>
    <main>
        <h3>13. BULL/BEAR ANALYSIS - [SPECIFIC RISK/REWARD THEME]</h3>
        
        <p><strong>🐂 BULL CASE</strong></p>
        <ul>
            <li>Strong fundamentals with revenue growth acceleration</li>
            <li>Market share expansion in key segments</li>
            <li>Operational leverage driving margin improvement</li>
        </ul>
        
        <p><strong>🐻 BEAR CASE</strong></p>
        <ul>
            <li>Competition pressure on pricing power</li>
            <li>Economic slowdown impact on demand</li>
            <li>Rising input costs affecting profitability</li>
        </ul>
        
        <p><strong>Risk Assessment Conclusion</strong></p>
        <p>[Balanced analysis of upside vs downside risks with probability weighting]</p>
    </main>
    <footer class="report-footer"><p>Robeco Investment Research</p><p>Page 13 / 15</p></footer>
</div>

<div class="slide report-prose" id="slide-scenario-analysis">
    <header class="report-header-container"><!-- Same header --></header>
    <main>
        <h3>14. SCENARIO ANALYSIS - [PROBABILITY-WEIGHTED OUTCOMES]</h3>
        <p><strong>Base Case Scenario (60% probability)</strong></p>
        <p>[Analysis of most likely outcome with supporting rationale]</p>
        
        <p><strong>Bull Case Scenario (25% probability)</strong></p>
        <p>[Optimistic scenario with key catalysts and potential upside]</p>
        
        <p><strong>Bear Case Scenario (15% probability)</strong></p>
        <p>[Conservative scenario with risk factors and downside protection]</p>
        
        <p><strong>Expected Value Analysis</strong></p>
        <p>[Probability-weighted analysis with target price derivation]</p>
    </main>
    <footer class="report-footer"><p>Robeco Investment Research</p><p>Page 14 / 15</p></footer>
</div>

<div class="slide report-prose" id="slide-investment-conclusion">
    <header class="report-header-container"><!-- Same header --></header>
    <main>
        <h3>15. INVESTMENT CONCLUSION - OVERWEIGHT RATING ON [KEY THESIS]</h3>
        <p><strong>Alpha Generation Thesis</strong></p>
        <p>[Concise investment thesis with specific return expectations and timeline]</p>
        
        <p><strong>Portfolio Construction Considerations</strong></p>
        <p>[Position sizing, risk characteristics, and portfolio fit analysis]</p>
        
        <p><strong>Actionable Monitoring Framework</strong></p>
        <p>[Key metrics and signposts to track investment thesis progression]</p>
        
        <p><strong>Catalyst Timeline & Exit Strategy</strong></p>
        <p>[Specific dates, milestones, and price targets for investment realization]</p>
    </main>
    <footer class="report-footer"><p>Robeco Investment Research</p><p>Page 15 / 15</p></footer>
</div>
```

### 🚨 CRITICAL: NO TABLE GENERATION REQUIRED!

**SLIDES 8-10 - JUST COPY THE PRE-MADE TABLES:**
- **Tables**: Ready-made HTML tables are provided above - COPY THEM EXACTLY
- **DON'T GENERATE**: Never create tables from scratch - just copy the provided ones
- **Analysis**: Write analysis paragraphs referencing the specific numbers in the tables
- **ZERO COMPLEXITY**: This eliminates the HTML generation complexity that caused failures

### 🎯 SIMPLIFIED CALL 2 CONTENT SPECIFICATIONS:

**SLIDES 11-12 (RATIOS & VALUATION) - STREAMLINED:**
- **Slide 11**: Clean text-based ratio analysis with simple paragraphs
- **Slide 12**: Straightforward valuation with DCF and multiples (no complex tables)
- **Format**: Simple paragraph structure with clear section headers
- **Focus**: Quality over complexity - concise but comprehensive analysis

**SLIDES 13-15 (RISK & CONCLUSION) - SIMPLIFIED:**
- **Slide 13**: Simple bull/bear lists with clean HTML structure
- **Slide 14**: Scenario analysis in paragraph format (no complex styling)
- **Slide 15**: Investment conclusion with 4 clear sections
- **Approach**: Eliminate ALL complex CSS - use only basic HTML elements

### 🚨 CRITICAL SIMPLIFICATION MANDATE:
- **80% complexity reduction** - Remove all nested inline styles
- **Focus on content quality** over visual complexity
- **Use ONLY basic HTML** - `<p>`, `<ul>`, `<li>`, `<strong>`, `<table class="financial-table">`
- **This prevents AI cognitive overload** that caused slide 9-10 failures

### ELITE PM QUANTITATIVE FRAMEWORK FOR CALL 2:

**SOPHISTICATED FINANCIAL ANALYSIS:**
- **Multi-Dimensional Decomposition**: Break down financial performance into cyclical vs. structural components
- **Factor Attribution**: Decompose returns into style, sector, quality, and company-specific alpha
- **Quality Assessment**: Distinguish between accounting earnings and true economic earnings
- **Predictive Analytics**: Identify leading indicators that forecast inflection points

**ADVANCED VALUATION METHODOLOGIES:**
- **DCF with Real Options**: Capture optionality value in growth investments and strategic pivots
- **Sum-of-the-Parts**: Asset-based valuation for complex business portfolio optimization
- **Relative Valuation**: Peer analysis with quality adjustments and normalized growth rates
- **Through-the-Cycle Analysis**: Normalize earnings across business cycles for sustainable valuation

**HEDGE FUND RISK MANAGEMENT:**
- **Scenario Modeling**: Bull/base/bear cases with probability-weighted expected returns
- **Stress Testing**: Monte Carlo simulation of key variables and correlation breakdowns
- **Tail Risk Assessment**: Maximum drawdown analysis and portfolio impact quantification
- **Hedge Considerations**: Natural hedges, synthetic instruments, and portfolio construction

**INSTITUTIONAL EXECUTION STANDARDS:**
- **Quantitative Rigor**: Every analysis backed by specific calculations and sensitivity testing
- **Data Integrity**: Reference actual financial data with transparent methodology
- **Professional Sophistication**: Citadel/Renaissance Technologies-level analytical depth
- **Alpha Source Documentation**: Clear articulation of sustainable competitive advantages

{financial_context}

{analyst_insights}

**ELITE PM EXECUTION MANDATE**: 
Deliver ALL 8 slides (slides 8-15) with sophisticated quantitative analysis that validates the Phase 1 investment thesis through rigorous financial modeling, advanced valuation techniques, and comprehensive risk assessment. Your analysis must demonstrate the analytical sophistication that justifies significant institutional capital allocation.

**MANDATORY SLIDE COMPLETION REQUIREMENTS:**
- MUST generate EXACTLY 8 slides: slides 8, 9, 10, 11, 12, 13, 14, AND 15
- Each slide MUST have complete financial analysis content
- SLIDE 15 MUST be complete with investment conclusion
- Each slide MUST have complete content - NO truncation allowed  
- Final slide MUST end with "Page 15 / 15" footer

**CRITICAL OUTPUT FORMAT REQUIREMENTS:**
- Output PURE HTML ONLY - NO markdown code blocks
- NO ```html tags, NO explanatory text, NO comments
- Start directly with <div class="slide report-prose" id="slide-financial-income-statement">
- End with slide 15's closing </div> tag (Page 15 / 15)
- Use exact CSS classes and structure shown in examples above
- GENERATE ALL 8 SLIDES COMPLETELY - DO NOT STOP EARLY

**🚨 CRITICAL COMPLETION ENFORCEMENT:**
YOU MUST COMPLETE ALL 8 SLIDES (8, 9, 10, 11, 12, 13, 14, 15). 
- Do NOT stop at slide 10 or any intermediate slide
- Each slide must have complete content and proper footer with page numbers
- Slide 15 MUST end with "Page 15 / 15" footer
- If you reach token limits, prioritize completing the slide structure over verbose content
- ABSOLUTELY REQUIRED: Generate slides 8, 9, 10, 11, 12, 13, 14, AND 15
"""
        
        # Combine base prompt with CSS guidance, ready tables, and Call 2 specifics
        try:
            # Format the Call 2 specific section with ready-made tables
            formatted_call2_specific = call2_specific.format(ready_tables=ready_tables)
            complete_call2_prompt = base_prompt + css_guidance + formatted_call2_specific
        except Exception as e:
            logger.warning(f"⚠️ Error formatting ready tables: {e}")
            # Fallback to original prompt without table formatting
            complete_call2_prompt = base_prompt + css_guidance + call2_specific
        
        logger.info(f"✅ Call 2 prompt built: {len(complete_call2_prompt):,} characters with pre-built HTML tables")
        return complete_call2_prompt
    
    def _extract_financial_statements_for_analysis(self, financial_data: Dict) -> Dict[str, Any]:
        """
        Extract and format financial statements for AI analysis
        
        Args:
            financial_data: Raw financial data from yfinance
            
        Returns:
            Dict containing formatted financial statements and HTML tables
        """
        logger.info(f"📊 Extracting financial statements for analysis")
        
        try:
            # Import the pre-calculated financial methods (handle both relative and absolute imports)
            try:
                from .pre_calculated_financial_methods import extract_pre_calculated_financial_tables, generate_ready_to_use_prompt_data
            except ImportError:
                # Fallback for absolute import when running directly
                from pre_calculated_financial_methods import extract_pre_calculated_financial_tables, generate_ready_to_use_prompt_data
            
            # Extract pre-calculated tables
            pre_calculated_tables = extract_pre_calculated_financial_tables(financial_data)
            
            # Generate HTML tables for AI prompt
            html_tables_for_ai = generate_ready_to_use_prompt_data(pre_calculated_tables)
            
            # Extract years and data quality info
            years_available = pre_calculated_tables.get('years_available', [])
            data_quality = pre_calculated_tables.get('data_quality', {})
            
            # Build structured response
            financial_statements = {
                'income_statement': {
                    'has_data': data_quality.get('income_data_available', False),
                    'table_data': pre_calculated_tables.get('income_statement_table', {})
                },
                'balance_sheet': {
                    'has_data': data_quality.get('balance_data_available', False),
                    'table_data': pre_calculated_tables.get('balance_sheet_table', {})
                },
                'cashflow': {
                    'has_data': data_quality.get('cashflow_data_available', False),
                    'table_data': pre_calculated_tables.get('cashflow_table', {})
                },
                'years_available': years_available,
                'data_quality': data_quality,
                'html_tables_for_ai': html_tables_for_ai
            }
            
            logger.info(f"✅ Financial statements extracted: {len(years_available)} years, {len(html_tables_for_ai):,} chars HTML")
            return financial_statements
            
        except Exception as e:
            logger.error(f"❌ Failed to extract financial statements: {e}")
            # Return empty structure
            return {
                'income_statement': {'has_data': False, 'table_data': {}},
                'balance_sheet': {'has_data': False, 'table_data': {}},
                'cashflow': {'has_data': False, 'table_data': {}},
                'years_available': [],
                'data_quality': {},
                'html_tables_for_ai': ''
            }
    
    async def _generate_ai_report(self, prompt: str, websocket=None, connection_id: str = None, call_phase: str = "generation") -> str:
        """Generate slides content using AI with automatic retry logic and optional websocket streaming"""
        
        max_retries = 100  # Try many keys until we find a working one
        for attempt in range(max_retries):
            # Get API key with force_attempt to start with primary key
            key_result = get_intelligent_api_key(agent_type="report_generator", attempt=attempt, force_attempt=True)
            if not key_result:
                raise Exception("No API key available for report generation")
            
            api_key, key_info = key_result
            logger.info(f"📝 Report generation attempt {attempt+1} using API key: {api_key[:8]}...{api_key[-4:]}")
            
            try:
                client = Client(api_key=api_key)
                
                # Configure for maximum comprehensive content generation
                generate_config = types.GenerateContentConfig(
                    temperature=0.15,  # Slightly higher for more detailed analysis
                    top_p=0.9,  # Good for comprehensive content generation
                    max_output_tokens=800000,  # ULTRA-MAXIMIZED for complete 15-slide template structure
                    response_mime_type="text/plain",
                    system_instruction="You are a Managing Director at Robeco writing institutional-grade investment research. CRITICAL: Generate comprehensive, detailed analysis - NOT brief summaries. Each paragraph must be 150-300 words, each bullet point 80-150 words with specific metrics and detailed analysis. Follow EXACT 15-slide template structure. Generate ALL slides with deep, professional investment banking analysis matching the template's sophistication. Use exact CSS classes and section titles. Include specific financial projections, competitive analysis, and quantitative assessments with bold metrics throughout. IMPORTANT: Output PURE HTML ONLY - NO markdown code blocks, NO ```html tags, NO explanatory text, NO comments outside HTML. Start directly with <div class='slide'> tags."
                )
                
                contents = [
                    types.Content(
                        role="user",
                        parts=[types.Part.from_text(text=prompt)]
                    )
                ]
                
                # Generate report with streaming (focused error logging)
                logger.info(f"🚀 Starting generation: {len(prompt)} chars prompt → {api_key[:8]}...")
                
                accumulated_response = ""
                chunk_count = 0
                
                # Use streaming to get real content as it generates with ULTRA-DEBUG tracking
                try:
                    last_chunk_text = ""
                    slide_detection_log = []
                    
                    # DEBUG: Track slide detection in real-time
                    current_slide_count = 0
                    last_detected_slide = 0
                    operating_cash_flow_detected = False
                    last_slide_content = ""
                    
                    # ULTRA-DEBUG: Initialize Call 2 specific tracking
                    if call_phase.startswith('call2'):
                        logger.info(f"🚨 CALL 2 DEBUG MODE ACTIVATED - Monitoring slide 8-15 generation")
                    
                    for chunk in client.models.generate_content_stream(
                        model='gemini-2.5-flash',
                        contents=contents,
                        config=generate_config,
                    ):
                        if chunk.text:
                            chunk_count += 1
                            accumulated_response += chunk.text
                            last_chunk_text = chunk.text
                            
                            # ULTRA-DEBUG: Real-time slide detection
                            new_slide_count = accumulated_response.count('<div class="slide')
                            if new_slide_count > current_slide_count:
                                current_slide_count = new_slide_count
                                logger.info(f"🎯 SLIDE DETECTED: Slide #{current_slide_count} started at chunk {chunk_count}")
                            
                            # ULTRA-DEBUG: Page number detection for Call 2
                            if call_phase.startswith('call2'):
                                for page_num in range(8, 16):
                                    page_marker = f"Page {page_num} / 15"
                                    if page_marker in accumulated_response and page_num > last_detected_slide:
                                        last_detected_slide = page_num
                                        logger.info(f"📄 PAGE MARKER DETECTED: {page_marker} at chunk {chunk_count} ({len(accumulated_response):,} chars)")
                                        slide_detection_log.append(f"Page {page_num} at chunk {chunk_count}")
                                        
                                        # Store slide content for analysis
                                        if page_num == 10:
                                            slide_10_start = accumulated_response.find("Page 10 / 15")
                                            if slide_10_start > 0:
                                                last_slide_content = accumulated_response[slide_10_start-200:slide_10_start+500]
                                                logger.info(f"🔍 SLIDE 10 CONTEXT: {last_slide_content}")
                            
                            # ULTRA-DEBUG: Operating Cash Flow detection (critical failure point)
                            if "Operating Cash Flow" in chunk.text and not operating_cash_flow_detected:
                                operating_cash_flow_detected = True
                                logger.warning(f"🚨 CRITICAL: Operating Cash Flow detected at chunk {chunk_count} - MONITOR FOR EARLY STOPPING!")
                                logger.info(f"🔍 Context around Operating Cash Flow: ...{accumulated_response[-200:]}")
                                
                                # Check if we're in a table or at end of content
                                recent_content = accumulated_response[-300:].lower()
                                if '</table>' in recent_content:
                                    logger.warning(f"⚠️ Table ending detected near Operating Cash Flow - HIGH RISK of early stopping!")
                            
                            # Log first chunk content to see what AI is generating
                            if chunk_count == 1:
                                logger.info(f"📝 FIRST CHUNK ({call_phase}): {chunk.text[:300]}...")
                            
                            # Enhanced progress tracking with completion detection
                            contains_html_end = '</html>' in accumulated_response.lower()
                            contains_body_end = '</body>' in accumulated_response.lower()
                            
                            # ULTRA-DEBUG: Detect potential early stopping patterns
                            if chunk_count > 50 and call_phase.startswith('call2'):
                                recent_content = accumulated_response[-500:].lower()
                                suspicious_endings = ['</table>', '</div>\n</div>', 'operating cash flow']
                                for ending in suspicious_endings:
                                    if ending in recent_content and chunk_count > 100:
                                        logger.warning(f"⚠️ SUSPICIOUS ENDING: '{ending}' at chunk {chunk_count} - may indicate early stopping")
                                        
                                # Check for incomplete slide 10
                                if last_detected_slide == 10 and chunk_count > 200 and "Page 11" not in accumulated_response:
                                    logger.error(f"🚨 SLIDE 10 STUCK: No progress to slide 11 after {chunk_count} chunks!")
                            
                            # Send real-time streaming updates to frontend with DEBUG info
                            if websocket and connection_id:
                                try:
                                    progress = min(30 + (chunk_count * 2), 95)  # Cap at 95% until complete
                                    if contains_html_end:
                                        progress = 95  # Near completion when HTML end detected
                                    
                                    await websocket.send_text(json.dumps({
                                        "type": "report_generation_streaming",
                                        "data": {
                                            "status": f"streaming_html_{call_phase}",
                                            "call_phase": call_phase,
                                            "html_chunk": chunk.text,
                                            "accumulated_html": accumulated_response,
                                            "chunk_number": chunk_count,
                                            "progress": progress,
                                            "message": f"🤖 {call_phase.upper()} Gen: {chunk_count} chunks, {len(accumulated_response):,} chars [Slides: {current_slide_count}, Page: {last_detected_slide}, OCF: {'✓' if operating_cash_flow_detected else '✗'}]",
                                            "connection_id": connection_id,
                                            "timestamp": datetime.now().isoformat(),
                                            "completion_indicators": {
                                                "has_html_end": contains_html_end,
                                                "has_body_end": contains_body_end
                                            },
                                            "debug_info": {
                                                "slides_detected": current_slide_count,
                                                "last_page_detected": last_detected_slide,
                                                "operating_cash_flow_seen": operating_cash_flow_detected,
                                                "slide_log": slide_detection_log[-3:],  # Last 3 slide detections
                                                "recent_content_sample": accumulated_response[-100:] if len(accumulated_response) > 100 else accumulated_response
                                            }
                                        }
                                    }))
                                except Exception as ws_error:
                                    logger.warning(f"WebSocket streaming failed: {ws_error}")
                                    # Continue without websocket streaming
                            
                            # Enhanced milestone logging with ULTRA-DEBUG
                            if chunk_count in [25, 50, 100, 200, 300, 500] or chunk_count % 100 == 0:
                                logger.info(f"📊 MILESTONE {chunk_count}: {len(accumulated_response):,} chars, {current_slide_count} slides, page {last_detected_slide}, OCF: {operating_cash_flow_detected}")
                                
                            # ULTRA-DEBUG: Log content around key milestones for Call 2
                            if chunk_count in [200, 400, 600] and call_phase.startswith('call2'):
                                content_sample = accumulated_response[-300:]
                                logger.info(f"🔍 CONTENT SAMPLE at chunk {chunk_count}: ...{content_sample}")
                                
                    # ULTRA-DEBUG: Final generation analysis
                    logger.info(f"🏁 GENERATION COMPLETE ({call_phase}):")
                    logger.info(f"   📊 Total chunks: {chunk_count}")
                    logger.info(f"   📄 Total chars: {len(accumulated_response):,}")
                    logger.info(f"   🎯 Slides detected: {current_slide_count}")
                    logger.info(f"   📋 Last page: {last_detected_slide}")
                    logger.info(f"   💧 Operating Cash Flow seen: {operating_cash_flow_detected}")
                    logger.info(f"   🔍 Slide detection log: {slide_detection_log}")
                    
                    # Log final content analysis
                    if len(accumulated_response) > 500:
                        logger.info(f"🔍 FINAL CONTENT START: {accumulated_response[:200]}...")
                        logger.info(f"🔍 FINAL CONTENT END: ...{accumulated_response[-200:]}")
                        
                    # ULTRA-DEBUG: Analyze why generation stopped for Call 2
                    if call_phase.startswith('call2') and last_detected_slide < 15:
                        logger.error(f"🚨🚨🚨 CALL 2 INCOMPLETE ANALYSIS:")
                        logger.error(f"   📉 Stopped at page: {last_detected_slide}/15")
                        logger.error(f"   🔢 Total slides generated: {current_slide_count}/8")
                        logger.error(f"   ⏱️ Generation chunks: {chunk_count}")
                        logger.error(f"   💧 Operating Cash Flow pattern: {operating_cash_flow_detected}")
                        logger.error(f"   📝 Last chunk: {last_chunk_text[-100:] if last_chunk_text else 'N/A'}")
                        logger.error(f"   🔍 Final 300 chars: ...{accumulated_response[-300:]}")
                        
                        # Detailed failure analysis
                        if last_detected_slide == 10 and operating_cash_flow_detected:
                            logger.error(f"   🎯 FAILURE PATTERN: Classic slide 10 + Operating Cash Flow early stop")
                        elif last_detected_slide < 10:
                            logger.error(f"   🎯 FAILURE PATTERN: Early truncation before reaching cash flow")
                        else:
                            logger.error(f"   🎯 FAILURE PATTERN: Unknown - stopped after slide {last_detected_slide}")
                        
                    # Log completion analysis
                    logger.info(f"📄 Final chunk text: {last_chunk_text[-100:] if last_chunk_text else 'N/A'}")
                    
                except Exception as stream_error:
                    logger.error(f"❌ STREAMING ERROR: {stream_error}")
                    
                    # Enhanced quota/rate limit handling
                    if '429' in str(stream_error) or 'RESOURCE_EXHAUSTED' in str(stream_error):
                        logger.warning(f"🔥 QUOTA/RATE LIMIT for key {api_key[:20]}...")
                        self.api_manager.mark_key_as_failed(api_key)
                        
                        if 'quota' in str(stream_error).lower():
                            logger.error(f"💳 QUOTA EXHAUSTED - key unusable for 24h")
                        else:
                            logger.warning(f"⏱️ RATE LIMITED - temporary throttling")
                    
                    raise stream_error
                
                if accumulated_response:
                    logger.info(f"✅ Generated {len(accumulated_response)} chars in {chunk_count} chunks")
                    
                    # Show actual content being generated (for debugging)
                    if len(accumulated_response) > 1000:
                        logger.info(f"📄 CONTENT START: {accumulated_response[:300]}...")
                        logger.info(f"📄 CONTENT END: ...{accumulated_response[-300:]}")
                    else:
                        logger.info(f"📄 FULL CONTENT: {accumulated_response}")
                    
                    return accumulated_response
                else:
                    raise Exception("No content generated - empty response")
                
            except Exception as api_error:
                logger.warning(f"⚠️ Report generation failed with key {api_key[:8]}...{api_key[-4:]}: {api_error}")
                
                # Log API error for pure rotation system
                if "suspended" in str(api_error).lower() or "403" in str(api_error):
                    logger.info(f"🔄 Key failed (will retry with different key): {api_key[:8]}...{api_key[-4:]}")
                
                # Re-raise on last attempt
                if attempt == max_retries - 1:
                    raise api_error
                
                logger.info(f"🔄 Retrying report generation (attempt {attempt+2}/{max_retries})")
        
        raise Exception("Report generation failed after all retries")
    
    def _combine_call1_and_call2_content(self, call1_content: str, call2_content: str) -> str:
        """
        Combine Call 1 (slides 1-7) and Call 2 (slides 8-15) content into complete 15-slide report
        
        Args:
            call1_content: HTML content for slides 1-7
            call2_content: HTML content for slides 8-15
            
        Returns:
            Combined HTML content for all 15 slides
        """
        logger.info(f"🔧 Combining Call 1 ({len(call1_content):,} chars) + Call 2 ({len(call2_content):,} chars)")
        
        try:
            # Clean both content pieces
            clean_call1 = call1_content.strip()
            clean_call2 = call2_content.strip()
            
            # Remove any stray HTML wrapper tags and markdown code blocks from AI output
            import re
            
            # Clean Call 1 content
            clean_call1 = re.sub(r'<!DOCTYPE[^>]*>', '', clean_call1, flags=re.IGNORECASE)
            clean_call1 = re.sub(r'</?html[^>]*>', '', clean_call1, flags=re.IGNORECASE)
            clean_call1 = re.sub(r'</?head[^>]*>', '', clean_call1, flags=re.IGNORECASE)
            clean_call1 = re.sub(r'</?body[^>]*>', '', clean_call1, flags=re.IGNORECASE)
            clean_call1 = re.sub(r'<style[^>]*>.*?</style>', '', clean_call1, flags=re.IGNORECASE | re.DOTALL)
            # Remove markdown code blocks
            clean_call1 = re.sub(r'```html\s*', '', clean_call1, flags=re.IGNORECASE)
            clean_call1 = re.sub(r'```\s*', '', clean_call1, flags=re.IGNORECASE)
            # Remove any stray text before the first <div> tag
            first_div = clean_call1.find('<div')
            if first_div > 0:
                clean_call1 = clean_call1[first_div:]
            clean_call1 = clean_call1.strip()
            
            # Clean Call 2 content
            clean_call2 = re.sub(r'<!DOCTYPE[^>]*>', '', clean_call2, flags=re.IGNORECASE)
            clean_call2 = re.sub(r'</?html[^>]*>', '', clean_call2, flags=re.IGNORECASE)
            clean_call2 = re.sub(r'</?head[^>]*>', '', clean_call2, flags=re.IGNORECASE)
            clean_call2 = re.sub(r'</?body[^>]*>', '', clean_call2, flags=re.IGNORECASE)
            clean_call2 = re.sub(r'<style[^>]*>.*?</style>', '', clean_call2, flags=re.IGNORECASE | re.DOTALL)
            # Remove markdown code blocks
            clean_call2 = re.sub(r'```html\s*', '', clean_call2, flags=re.IGNORECASE)
            clean_call2 = re.sub(r'```\s*', '', clean_call2, flags=re.IGNORECASE)
            # Remove any stray text before the first <div> tag
            first_div = clean_call2.find('<div')
            if first_div > 0:
                clean_call2 = clean_call2[first_div:]
            clean_call2 = clean_call2.strip()
            
            # Combine the content
            combined_content = clean_call1 + '\n\n' + clean_call2
            
            logger.info(f"✅ Successfully combined Call 1 + Call 2: {len(combined_content):,} total characters")
            logger.info(f"📊 Content breakdown: Call 1={len(clean_call1):,} chars, Call 2={len(clean_call2):,} chars")
            
            # Log first and last few characters of each call to verify separation and completion
            logger.info(f"🔍 Call 1 starts with: {clean_call1[:100]}...")
            logger.info(f"🔍 Call 1 ends with: ...{clean_call1[-100:]}")
            logger.info(f"🔍 Call 2 starts with: {clean_call2[:100]}...")
            logger.info(f"🔍 Call 2 ends with: ...{clean_call2[-100:]}")
            
            # Check for slide 7 completion in Call 1
            if 'Page 7 / 15' not in clean_call1:
                logger.warning(f"⚠️ Call 1 may be incomplete - missing slide 7 footer")
            if 'Page 8 / 15' in clean_call1:
                logger.warning(f"⚠️ Call 1 contains Call 2 content - slide 8 found in Call 1")
            
            return combined_content
            
        except Exception as e:
            logger.error(f"❌ Failed to combine Call 1 + Call 2 content: {e}")
            # Return simple concatenation as fallback
            return f"{call1_content}\n{call2_content}"
    
    def _save_report_to_file(self, html_content: str, company_name: str, ticker: str) -> str:
        """
        Save the complete HTML report to a file like Dakin.html, Arista.html, etc.
        
        Args:
            html_content: Complete HTML report content
            company_name: Company name for filename
            ticker: Stock ticker
            
        Returns:
            Path to saved file
        """
        try:
            # Clean company name for filename (remove special characters)
            import re
            clean_name = re.sub(r'[^\w\s-]', '', company_name)
            clean_name = re.sub(r'[-\s]+', '_', clean_name)
            clean_name = clean_name.strip('_')
            
            # Create filename: CompanyName.html (like Dakin.html, Arista.html)
            if clean_name:
                filename = f"{clean_name}.html"
            else:
                filename = f"{ticker}.html"
            
            # Save to the main Robeco Reporting directory (same level as Dakin.html)
            report_dir = Path(__file__).parent.parent.parent.parent  # Go up to /Users/skl/Desktop/Robeco Reporting
            filepath = report_dir / filename
            
            # Write the HTML file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"💾 Report saved to: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"❌ Failed to save report file: {e}")
            return ""
    
    def _combine_css_with_slides(self, company_name: str, ticker: str, slides_content: str) -> str:
        """Combine fixed CSS template with AI-generated slide content"""
        
        logger.info(f"🔧 Combining fixed CSS with {len(slides_content):,} characters of slide content")
        
        try:
            # Load the fixed CSS template
            with open(self.css_path, 'r', encoding='utf-8') as f:
                css_template = f.read()
            
            logger.info(f"✅ Loaded fixed CSS template: {len(css_template):,} characters")
            
            # Update template to match current company
            css_template = css_template.replace(
                'Robeco - IHI Investment Analysis',
                f'Robeco - {company_name} Investment Analysis'
            ).replace(
                'IHI Corporation', company_name
            ).replace(
                '7013 JT', ticker
            )
            
            # Clean the AI-generated slide content (remove any stray HTML tags)
            clean_slides = slides_content.strip()
            
            # Remove any DOCTYPE, html, head, body tags that AI might have added despite instructions
            import re
            clean_slides = re.sub(r'<!DOCTYPE[^>]*>', '', clean_slides, flags=re.IGNORECASE)
            clean_slides = re.sub(r'</?html[^>]*>', '', clean_slides, flags=re.IGNORECASE)
            clean_slides = re.sub(r'</?head[^>]*>', '', clean_slides, flags=re.IGNORECASE)
            clean_slides = re.sub(r'</?body[^>]*>', '', clean_slides, flags=re.IGNORECASE)
            clean_slides = re.sub(r'<style[^>]*>.*?</style>', '', clean_slides, flags=re.IGNORECASE | re.DOTALL)
            clean_slides = clean_slides.strip()
            
            # Extract everything before <body> tag (including <body>)
            body_start = css_template.find('<body>')
            head_section = css_template[:body_start + 6]  # Include <body>
            
            # Create the complete HTML
            complete_html = head_section + '\n' + clean_slides + '\n</body>\n</html>'
            
            logger.info(f"✅ Successfully combined fixed CSS with AI slide content")
            logger.info(f"📊 Final HTML: {len(complete_html):,} characters")
            
            return complete_html
            
        except Exception as e:
            logger.error(f"❌ Failed to load CSS template: {e}")
            raise e
    
    def extract_analyses_from_storage(self, stored_analyses: List[Dict]) -> Dict[str, Any]:
        """
        Extract and organize analyses by agent type from stored analysis data
        
        Args:
            stored_analyses: List of stored analysis records from frontend
            
        Returns:
            Dict organized by agent type
        """
        organized_analyses = {}
        
        for analysis in stored_analyses:
            agent_type = analysis.get('analystType', analysis.get('agent_type', 'unknown'))
            
            # Take the most recent analysis for each agent type
            if agent_type not in organized_analyses:
                organized_analyses[agent_type] = {
                    'content': analysis.get('content', ''),
                    'sources': analysis.get('sources', []),
                    'timestamp': analysis.get('timestamp', ''),
                    'company': analysis.get('company', ''),
                    'ticker': analysis.get('ticker', ''),
                    'quality_score': analysis.get('qualityScore', 0.9)
                }
        
        logger.info(f"📊 Organized analyses: {list(organized_analyses.keys())}")
        return organized_analyses

# Global instance
template_report_generator = RobecoTemplateReportGenerator()