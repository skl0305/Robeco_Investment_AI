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
from google.genai.types import Tool, GoogleSearch
from api_key.gemini_api_key import get_intelligent_api_key

logger = logging.getLogger(__name__)

class RobecoTemplateReportGenerator:
    """Generate comprehensive investment reports following Robeco template structure"""
    
    def __init__(self):
        # Use relative paths from the current file location
        base_dir = Path(__file__).parent.parent.parent.parent  # Go to project root
        self.template_path = base_dir / "Report Example" / "Robeco_InvestmentCase_Template.txt"
        self.css_path = base_dir / "Report Example" / "CSScode.txt"
        logger.info("🏗️ Robeco Template Report Generator initialized")
    
    async def _send_websocket_safe(self, websocket, message_data: dict) -> bool:
        """Safely send WebSocket message, handling disconnections gracefully"""
        if not websocket:
            return False
        
        try:
            # Check if WebSocket is still open
            if websocket.client_state.name != 'CONNECTED':
                logger.warning("⚠️ WebSocket not connected, skipping message")
                return False
                
            await websocket.send_text(json.dumps(message_data))
            return True
        except Exception as e:
            # Log the error but don't crash the generation process
            logger.warning(f"WebSocket streaming failed: {e}")
            return False
    
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
        user_query: str = None,
        data_sources: Dict = None
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
        
        # Store investment objective for use in prompts
        self.investment_objective = investment_objective or "comprehensive investment analysis"
        
        try:
            # 🎯 IMPLEMENTING 2-CALL ARCHITECTURE
            logger.info("🚀 Starting 2-Call Architecture Report Generation")
            
            # Send CSS template content at the very start
            if websocket:
                try:
                    # Load only the CSS styles (not full HTML structure)
                    with open(self.css_path, 'r', encoding='utf-8') as f:
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
                    await self._send_websocket_safe(websocket, {
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
                    })
                    logger.info("📄 CSS template content sent via WebSocket")
                except Exception as e:
                    logger.warning(f"⚠️ Could not load CSS template: {e}")
            
            # Send progress update for Call 1
            if websocket:
                await self._send_websocket_safe(websocket, {
                    "type": "report_generation_progress",
                    "data": {
                        "status": "call1_starting", 
                        "message": "📊 CALL 1: Generating overview, company & industry analysis (slides 1-7)...",
                        "progress": 20,
                        "connection_id": connection_id,
                        "timestamp": datetime.now().isoformat()
                    }
                })
            
            # CALL 1: Generate slides 1-7 (Overview, Company, Industry Analysis)
            call1_content = await self._generate_combined_overview_and_analysis_section(
                company_name, ticker, analyses_data, financial_data, websocket, connection_id, data_sources
            )
            
            if not call1_content:
                raise Exception("Call 1 failed to generate content")
            
            # CRITICAL: Validate Call 1 completion before proceeding
            call1_validation = self._validate_call1_completion(call1_content)
            if not call1_validation:
                # Send failure signal if Call 1 is incomplete
                if websocket:
                    await self._send_websocket_safe(websocket, {
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
                    })
                logger.error(f"🚨 CALL 1 VALIDATION FAILED - proceeding anyway for debugging")
                # Note: Not raising exception to allow debugging, but this should be fixed
            
            # Send Call 1 completion signal with its content
            if websocket:
                logger.info(f"📤 Sending Call 1 completion: {len(call1_content):,} chars")
                await self._send_websocket_safe(websocket, {
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
                })
            
            # Extract key insights from Call 1 for Call 2 context
            extracted_rating = self._extract_rating_from_call1(call1_content)
            call1_context = {
                'content_summary': 'Strong fundamentals and growth potential',
                'investment_rating': extracted_rating,
                'generated_content': call1_content[:1000]  # First 1000 chars as context
            }
            
            # Send progress update for Call 2  
            if websocket:
                await self._send_websocket_safe(websocket, {
                    "type": "report_generation_progress",
                    "data": {
                        "status": "call2_starting",
                        "message": "📊 CALL 2: Generating financial analysis & valuation (slides 8-15)...", 
                        "progress": 60,
                        "connection_id": connection_id,
                        "timestamp": datetime.now().isoformat()
                    }
                })
            
            # CALL 2: Generate slides 8-15 (Financial Analysis & Valuation)
            call2_content = await self._generate_industry_and_financial_section(
                company_name, ticker, analyses_data, financial_data, call1_context, websocket, connection_id, data_sources
            )
            
            if not call2_content:
                raise Exception("Call 2 failed to generate content")
            
            # Send Call 2 completion signal
            if websocket:
                logger.info(f"📤 Sending Call 2 completion: {len(call2_content):,} chars")
                await self._send_websocket_safe(websocket, {
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
                })
            
            # Send progress update for combining
            if websocket:
                await self._send_websocket_safe(websocket, {
                    "type": "report_generation_progress", 
                    "data": {
                        "status": "combining",
                        "message": "🔧 Combining Call 1 + Call 2 results...",
                        "progress": 85,
                        "connection_id": connection_id,
                        "timestamp": datetime.now().isoformat()
                    }
                })
            
            # Combine Call 1 + Call 2 content
            combined_slides_content = self._combine_call1_and_call2_content(call1_content, call2_content)
            
            # Combine with fixed CSS template
            final_report_html = self._combine_css_with_slides(company_name, ticker, combined_slides_content)
            
            # Save the complete report as HTML file
            self._save_report_to_file(final_report_html, company_name, ticker)
            
            # Send final completion signal with complete report
            if websocket:
                logger.info(f"📤 Sending final completion: {len(final_report_html):,} chars")
                await self._send_websocket_safe(websocket, {
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
                })
            
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
        connection_id: str = None,
        data_sources: Dict = None
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
        
        # Build Call 1 specific prompt with user context
        call1_prompt = await self._build_call1_prompt(company_name, ticker, analyses_data, financial_data, self.investment_objective, data_sources)
        
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
    
    def _extract_rating_from_call1(self, call1_content: str) -> str:
        """
        Extract the investment rating from Call 1 content to ensure consistency in Call 2
        
        Args:
            call1_content: Generated HTML content from Call 1
            
        Returns:
            str: Extracted rating (OVERWEIGHT/NEUTRAL/UNDERWEIGHT) or default
        """
        if not call1_content:
            return "NEUTRAL"
            
        # Look for rating patterns in the HTML content
        import re
        
        # Search for rating patterns in various formats
        rating_patterns = [
            r'<div[^>]*class="[^"]*rating[^"]*"[^>]*>([^<]+)</div>',  # CSS class with rating
            r'OVERWEIGHT|UNDERWEIGHT|NEUTRAL',  # Direct rating mentions
            r'Rating:\s*(OVERWEIGHT|UNDERWEIGHT|NEUTRAL)',  # "Rating: X" format
            r'Investment\s*Rating:\s*(OVERWEIGHT|UNDERWEIGHT|NEUTRAL)',  # "Investment Rating: X"
        ]
        
        for pattern in rating_patterns:
            matches = re.findall(pattern, call1_content, re.IGNORECASE)
            if matches:
                rating = matches[0].upper().strip()
                if rating in ['OVERWEIGHT', 'UNDERWEIGHT', 'NEUTRAL']:
                    logger.info(f"✅ Extracted rating from Call 1: {rating}")
                    return rating
        
        # Fallback: look for any mention of these ratings
        call1_upper = call1_content.upper()
        if 'OVERWEIGHT' in call1_upper:
            logger.info("✅ Found OVERWEIGHT in Call 1 content")
            return "OVERWEIGHT"
        elif 'UNDERWEIGHT' in call1_upper:
            logger.info("✅ Found UNDERWEIGHT in Call 1 content")
            return "UNDERWEIGHT"
        elif 'NEUTRAL' in call1_upper:
            logger.info("✅ Found NEUTRAL in Call 1 content")
            return "NEUTRAL"
        
        logger.warning("⚠️ No rating found in Call 1, defaulting to NEUTRAL")
        return "NEUTRAL"

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
        connection_id: str = None,
        data_sources: Dict = None
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
        
        # Build Call 2 specific prompt with Call 1 context and user context
        call2_prompt = await self._build_call2_prompt(
            company_name, ticker, analyses_data, financial_data, call1_context, self.investment_objective, data_sources
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
            sufficient_length = len(call2_content) > 30000  # Reduced minimum - AI generating 65k-70k chars consistently
            
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
            
            # AGGRESSIVE: Check for complete investment conclusion content (flexible patterns)
            has_investment_conclusion = (
                "INVESTMENT CONCLUSION" in call2_content.upper() or 
                "OVERWEIGHT RATING" in call2_content.upper() or
                "BUY RECOMMENDATION" in call2_content.upper() or
                "STRONG BUY" in call2_content.upper() or
                "15." in call2_content  # Slide 15 pattern
            )
            
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
                logger.warning(f"   Length insufficient: {not sufficient_length} ({len(call2_content):,} < 30000)")
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
You are an **elite hedge fund Portfolio Manager** with 25+ years of experience at top-tier firms like Renaissance Technologies, Bridgewater Associates, and Citadel. You've consistently generated significant alpha by **identifying insights that consensus systematically misses**. Your analytical prowess combines:

- **Information Asymmetry Hunter**: Expert at finding insights hiding in plain sight for {company_name} that others overlook due to cognitive biases, complexity, or time horizons
- **Second-Order Thinking Master**: Understanding consequences of consequences - how today's trends create tomorrow's opportunities and risks that markets haven't priced
- **Pattern Recognition Virtuoso**: Identifying historical parallels, cycle analysis, and inflection points before they become obvious to consensus for {company_name}
- **Contrarian Positioning Expert**: Systematic frameworks for understanding why consensus is wrong and when contrarian positions offer asymmetric returns
- **Predictive Analytics Pioneer**: Building forward-looking models using leading indicators, management behavior analysis, and competitive intelligence
- **Capital Cycle Detective**: Understanding where companies are in their investment cycles and predicting capital allocation effectiveness
- **Technological Disruption Analyst**: Identifying second and third-order effects of emerging technologies on business models and competitive dynamics

**Your reputation**: Wall Street's most prescient mind, known for calling major inflection points 12-18 months before consensus, with a track record of generating 300+ basis points of annual alpha through differentiated insights.

**TARGET AUDIENCE - CIO WITH 30 YEARS STREET EXPERIENCE:**
Your analysis targets a Chief Investment Officer with 30 years on the Street who:
- **Understands everything on {company_name}** - needs NO basic explanations or obvious insights
- **Has NO TIME for fluff** - every sentence must deliver actionable intelligence  
- **Demands high info density** - more insights per word than any analyst they've read
- **Values only UNIQUE perspectives** - will instantly recognize recycled consensus thinking for {company_name}
- **Expects forward-looking analysis** - wants to know what happens NEXT, not what already happened
- **Requires conviction** - needs specific price targets, timeframes, and conviction levels

**ZERO TOLERANCE POLICY:**
- ❌ **NO generic statements** ("Company is well-positioned...")
- ❌ **NO obvious observations** ("Revenue growth is important...")  
- ❌ **NO clichés or buzzwords** ("Best-in-class", "market leader", "going forward")
- ❌ **NO filler words** - every word must add value
- ✅ **ONLY unique insights** that demonstrate superior understanding
- ✅ **ONLY forward-looking analysis** with specific catalysts and timing
- ✅ **ONLY differentiated perspectives** that challenge consensus thinking
- ✅ **CONCISE & PRECISE** - High info density, maximum impact per word

### ALPHA-GENERATION OBJECTIVE:
Produce an **elite-level, High info density, non-consensus investment analysis** that reveals insights others systematically miss due to cognitive limitations, analytical shortcuts, or time horizon mismatches. Your analysis must demonstrate:

**🎯 PROPRIETARY INSIGHT GENERATION:**
- **What Consensus Misses**: Identify specific analytical blind spots, cognitive biases, or complexity barriers that cause mispricing
- **Second-Order Value Drivers**: Uncover how today's developments create tomorrow's competitive advantages or disruptions
- **Inflection Point Prediction**: Pinpoint when current trends will accelerate, decelerate, or reverse—before markets recognize it
- **Hidden Optionality**: Identify embedded real options, strategic flexibility, or unrecognized value creation mechanisms

** DEEP FUNDAMENTAL FORENSICS:**
- **Management Behavior Analysis**: Read between lines of management actions, capital allocation, and strategic messaging for {company_name} as of {datetime.now().strftime("%B %Y")}
- **Competitive Intelligence**: Understand competitive dynamics, market share shifts, and industry evolution better than consensus
- **Technology Impact Assessment**: Predict how emerging technologies will reshape business models and competitive moats
- **Regulatory Anticipation**: Forecast policy changes and their second/third-order effects on industry structure

**⚡ TIMING & CATALYST PRECISION:**
- **Earnings Inflection Points**: Predict when financial performance will surprise consensus based on leading indicators for {company_name} as of {datetime.now().strftime("%B %Y")}
- **Multiple Expansion/Compression**: Identify when valuation re-rating will occur and what will trigger it
- **Capital Cycle Positioning**: Understand where company and industry are in investment cycles for optimal entry/exit timing for {company_name} as of {datetime.now().strftime("%B %Y")}
- **Sentiment Reversal Timing**: Predict when negative/positive sentiment will reverse based on fundamental improvements

**Your analysis must answer: \"What do I know about {company_name}'s future that the market doesn't yet understand?\"**

### MANDATORY ANALYTICAL REQUIREMENTS:

**1. NON-CONSENSUS THESIS DEVELOPMENT:**
- **Contrarian Positioning**: Systematically identify why consensus view is fundamentally flawed or incomplete
- **Information Asymmetry Exploitation**: Leverage complexity, behavioral biases, or time horizon mismatches that create mispricings
- **Multi-Dimensional Alpha Sources**: Build thesis on 3-4 independent, uncorrelated value drivers that markets underestimate
- **Differentiated Insight**: Demonstrate differentiated understanding of business model, competitive dynamics, or industry evolution

**2. PREDICTIVE ANALYTICS FRAMEWORK:**
- **Leading Indicator Analysis**: Identify forward-looking metrics that predict earnings/multiple inflection points 6-12 months ahead for {company_name} starting from {datetime.now().strftime("%B %Y")}
- **Pattern Recognition**: Apply historical parallels and cycle analysis to predict likely future trajectories
- **Scenario Probability Assessment**: Quantify likelihood of different outcomes using Bayesian inference and base rate analysis
- **Inflection Point Mapping**: Pinpoint specific dates/catalysts when thesis will be validated or invalidated

**3. DEEP FUNDAMENTAL FORENSICS:**
- **Management Quality Assessment**: Analyze track record, capital allocation decisions, and strategic messaging for hidden insights
- **Competitive Intelligence**: Understand market share trends, pricing power evolution, and competitive response functions
- **Technology Disruption Analysis**: Assess how emerging technologies will impact business model sustainability
- **Capital Cycle Analysis**: Determine where company/industry is in investment cycle for optimal positioning

**4. BEHAVIORAL FINANCE EXPLOITATION:**
- **Cognitive Bias Identification**: Exploit recency bias, anchoring, confirmation bias that create systematic mispricings
- **Sentiment Analysis**: Predict when overly pessimistic/optimistic sentiment will reverse based on fundamentals
- **Complexity Premium**: Leverage situations too complex for algorithmic or retail analysis to generate alpha
- **Time Horizon Arbitrage**: Exploit short-term volatility in fundamentally sound long-term value creation stories

###  CRITICAL: DATA-DRIVEN ANALYTICAL MANDATES

**🔍 RESEARCH-BACKED ANALYSIS REQUIREMENTS:**
Every analysis point MUST be supported by:
- **Latest Company Research for {company_name}**: Reference recent analyst reports, management guidance, and industry research for {company_name} as of {datetime.now().strftime("%B %Y")}
- **Google Search Integration**: Use current news, earnings transcripts, industry reports, regulatory filings
- **Specific Data Points**: Cite exact numbers, percentages, dates, and quantified metrics for {company_name} as of {datetime.now().strftime("%B %Y")}
- **Source Attribution**: Reference where insights come from (earnings calls, research reports, industry data)
- **Comparative Analysis**: Compare to industry benchmarks, peer companies, and historical norms

** STOCK PRICE MOVEMENT ATTRIBUTION (MANDATORY):**
For every major analytical point, you MUST address:
- **Historical Price Context**: Why did the stock move up/down in the past 12-24 months?
- **Fundamental Attribution**: What specific fundamental changes drove those price movements?
- **Market Reaction Analysis**: Why did the market react that way to specific events/earnings?
- **Mispricing Identification**: Where did the market overreact or underreact to fundamental changes?
- **Forward Price Implications**: How will future fundamental changes impact stock price trajectory?

** DIFFERENTIATED VIEW REQUIREMENTS:**
Every section must demonstrate:
- **Independent Analytical View**: Present your investment thesis for {company_name} as of {datetime.now().strftime("%B %Y")} with specific evidence
- **Differentiated Insights**: Lead with your unique perspective and analytical conclusions
- **Supporting Evidence**: What specific data, trends, or analysis supports your view?
- **Investment Timing**: Why is this the right time for this investment perspective?

**📊 HIGH-DENSITY ANALYTICAL PRESENTATION:**
- **Lead with Data-Driven Insights**: Start each section with your analytical conclusion backed by specific evidence
- **Differentiated Logic Flow**: Present clear, logical progression from analysis to investment implication  
- **No-Bullshit Delivery**: Concise, professional language targeting experienced PMs who know company fundamentals
- **Value-Add Focus**: Highlight insights beyond public information that drive investment decisions
- **Quantified Impact**: What specific financial/stock price impact will your differentiated view create?

** IMPLICATIONS-DRIVEN ANALYSIS:**
After every analytical statement, you MUST provide:
- **"So What?" Analysis**: What does this mean for future earnings, margins, competitive position?
- **Investment Implications**: How does this impact your investment thesis and price target?
- **Risk Assessment**: What could go wrong with this analysis and how do you mitigate it?
- **Timeline Specificity**: When will these implications become apparent to the market?
- **Portfolio Impact**: How does this affect position sizing and risk management?

** FORWARD-LOOKING MANDATE:**
Every analysis must include:
- **12-Month Outlook**: Specific predictions for the next 4 quarters with supporting logic for {company_name} starting from {datetime.now().strftime("%B %Y")}
- **Catalyst Timeline**: Exact dates/events that will validate or invalidate your thesis
- **Scenario Planning**: Base/Bull/Bear cases with specific probability weightings
- **Market Recognition**: When and how will the market recognize your insights?
- **Exit Strategy**: Specific triggers for taking profits or cutting losses

**5. MULTI-DIMENSIONAL VALUATION:**
- **Dynamic DCF Modeling**: Incorporate optionality, competitive response functions, and non-linear growth trajectories of {company_name}
- **Sum-of-the-Parts with Synergies**: Value business segments independently while modeling cross-segment synergies
- **Real Options Valuation**: Quantify strategic flexibility, expansion options, and abandonment values
- **Through-the-Cycle Analysis**: Normalize for cyclical factors to assess sustainable earning power

**6. RISK-ADJUSTED IMPLEMENTATION:**
- **Hedge Construction**: Design synthetic and natural hedges to isolate alpha while managing systematic risk
- **Drawdown Management**: Establish dynamic stop-loss and portfolio heat metrics
- **Correlation Analysis**: Understand factor exposures and portfolio construction implications

**7. PROPRIETARY MONITORING SYSTEM:**
- **Early Warning Indicators**: Track leading metrics that signal thesis validation/invalidation before consensus
- **Competitive Response Monitoring**: Watch for competitive reactions that could undermine thesis
- **Management Behavior Tracking**: Monitor insider activity, capital allocation changes, strategic pivots
- **Sentiment Inflection Detection**: Identify when market perception begins shifting toward thesis validation

### SPECIFIC HTML STRUCTURE COMPLIANCE:
```html
<!-- ROBECO LOGO (ALL SLIDES) - Position absolutely in top-right corner -->
<div class="slide-logo">
    <img src="https://images.ctfassets.net/tl4x668xzide/7mygwms2vuSwirnfvaCSvL/72d2bbd858a69aecbf59fd3fb8954484/robeco-logo-color.png" alt="Robeco Logo">
</div>

<!-- HEADER STRUCTURE (ALL SLIDES) -->
<header class="report-header-container">
    <div class="header-blue-border">
        <div class="company-header">
            <img src="[COMPANY_LOGO]" alt="Company Icon" class="icon" style="margin-top: -5px; width: 20px; height: 20px;">
            <h1 class="name">{company_name}</h1>
            <div class="rating" style="color: #2E7D32;">[INVESTMENT_RATING]</div>
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
- **Information Asymmetry**: Identify data/insights not yet reflected in price for {company_name} as of {datetime.now().strftime("%B %Y")}
- **Behavioral Biases**: Exploit systematic cognitive errors in market pricing
- **Structural Inefficiencies**: Leverage forced selling, index rebalancing, flow dynamics
- **Complexity Premium**: Capitalize on situations too complex for mainstream analysis

**MULTI-LAYERED FUNDAMENTAL ANALYSIS:**
- **Business Model Decomposition**: Unit economics, scalability, defensibility, reinvestment rates for {company_name} as of {datetime.now().strftime("%B %Y")}
- **Competitive Dynamics**: Porter's 5 forces, competitive response functions, game theory for {company_name} as of {datetime.now().strftime("%B %Y")}
- **Management Quality**: Capital allocation track record, strategic vision, execution consistency for {company_name} as of {datetime.now().strftime("%B %Y")}
- **Industry Life Cycle**: Position within cycle, disruption risk, consolidation opportunities for {company_name} as of {datetime.now().strftime("%B %Y")}

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

** CRITICAL: BOLD FORMATTING FOR IMPORTANT ANALYSIS:**
- **USE <strong></strong> tags** for all KEY INSIGHTS, IMPORTANT METRICS, and CRITICAL INVESTMENT POINTS
- **Bold all specific numbers**: <strong>25.3% ROIC</strong>, <strong>$2B investment</strong>, <strong>400bps margin expansion</strong>
- **Bold contrarian statements**: <strong>Unlike consensus, we believe...</strong>
- **Bold price targets and ratings**: <strong>$150 price target</strong>, <strong>OVERWEIGHT rating</strong>
- **Bold key catalysts**: <strong>Q1 earnings will demonstrate...</strong>
- **Bold competitive advantages**: <strong>Market-leading 40% share</strong>
- **Bold investment conclusions**: <strong>Risk/reward strongly favorable at current levels</strong>

### TECHNICAL FORMATTING REQUIREMENTS:
- **Document Structure**: Exactly 15 slides with specific HTML classes and IDs
- **Professional Layout**: 1620px × 2291px institutional presentation format
- **Data Integration**: Use actual financial data from provided tables
- **Visual Hierarchy**: Proper headers, numbered sections, professional color scheme
- **Slide Types**: Analysis-item format (slides 1-2), report-prose format (slides 3-15)
- **Table Styling**: Professional financial tables with gradient headers and data integration

### PERFORMANCE EXPECTATIONS:
**Your analysis must demonstrate:**
- **Intellectual Rigor**: Depth that separates institutional research from sell-side reports for {company_name} as of {datetime.now().strftime("%B %Y")}
- **Original Insights**: Perspectives not readily available in consensus research
- **Actionable Intelligence**: Clear investment implications with specific entry/exit strategies
- **Risk Awareness**: Comprehensive downside protection and scenario planning
- **Alpha Generation**: Identifiable sources of outperformance vs. market/benchmark

**Remember**: You are not writing generic research. You are crafting alpha-generating investment insights that justify significant capital allocation decisions by sophisticated institutional investors.

---
"""

    def _build_stock_price_data(self, ticker: str) -> Dict:
        """
        Extract clean stock price data for AI to create simple chart
        Returns data points instead of pre-made HTML
        """
        try:
            import yfinance as yf
            from datetime import datetime, timedelta
            
            stock = yf.Ticker(ticker)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=5*365)  # 5 years
            
            # Get monthly data to keep it simple
            hist = stock.history(start=start_date, end=end_date, interval="1mo")
            
            if hist.empty:
                return {"error": "No data available"}
            
            # Get company info
            info = stock.info
            currency = info.get('currency', 'USD')
            company_name = info.get('longName', ticker)
            
            # Format currency symbol
            curr_symbol = '¥' if currency == 'JPY' else ('S$' if currency == 'SGD' else ('€' if currency == 'EUR' else ('£' if currency == 'GBP' else '$')))
            
            # Extract clean data points (keep 2 decimal places for accurate price representation)
            prices = [round(float(row['Close']), 2) for _, row in hist.iterrows()]
            dates = [date.strftime('%Y-%m') for date, _ in hist.iterrows()]
            
            current_price = prices[-1] if prices else 0
            start_price = prices[0] if prices else 0
            total_return = ((current_price - start_price) / start_price * 100) if start_price > 0 else 0
            max_price = max(prices) if prices else 0
            min_price = min(prices) if prices else 0
            
            stock_data_result = {
                "company_name": company_name,
                "ticker": ticker,
                "currency": curr_symbol,
                "current_price": f"{curr_symbol}{current_price:,.2f}",
                "total_return": f"{total_return:+.1f}%",
                "price_range": f"{curr_symbol}{min_price:,.2f} - {curr_symbol}{max_price:,.2f}",
                "monthly_prices": prices,  # All 5 years of monthly data
                "dates": dates,
                "data_points": len(prices)
            }
            
            # Debug logging to see actual data
            logger.info(f"📊 Stock data fetched for {ticker}:")
            logger.info(f"   📈 Data points: {len(prices)}")
            logger.info(f"   💰 Price range: {curr_symbol}{min_price:,.2f} - {curr_symbol}{max_price:,.2f}")
            logger.info(f"   📅 Date range: {dates[0]} to {dates[-1]}" if dates else "   📅 No dates")
            logger.info(f"   🔢 Sample prices: {prices[:5]}..." if len(prices) >= 5 else f"   🔢 All prices: {prices}")
            
            return stock_data_result
            
        except Exception as e:
            logger.warning(f"⚠️ Error extracting stock data for {ticker}: {e}")
            return {"error": f"Unable to fetch data for {ticker}"}

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
            # Get currency info for proper formatting
            import yfinance as yf
            stock = yf.Ticker(ticker)
            info = stock.info
            currency = info.get('currency', 'USD')
            
            # Format currency symbol
            if currency == 'JPY':
                curr_symbol = '¥'
                # For JPY, use trillions (T) and billions (B) since values are much larger
                large_divisor = 1_000_000_000_000  # Trillion
                large_suffix = 'T'
                medium_divisor = 1_000_000_000     # Billion  
                medium_suffix = 'B'
            elif currency == 'SGD':
                curr_symbol = 'S$'
                large_divisor = 1_000_000_000
                large_suffix = 'B'
                medium_divisor = 1_000_000
                medium_suffix = 'M'
            elif currency == 'EUR':
                curr_symbol = '€'
                large_divisor = 1_000_000_000
                large_suffix = 'B'
                medium_divisor = 1_000_000
                medium_suffix = 'M'
            elif currency == 'GBP':
                curr_symbol = '£'
                large_divisor = 1_000_000_000
                large_suffix = 'B'
                medium_divisor = 1_000_000
                medium_suffix = 'M'
            else:  # USD and others
                curr_symbol = '$'
                large_divisor = 1_000_000_000
                large_suffix = 'B'
                medium_divisor = 1_000_000
                medium_suffix = 'M'
            
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
                                    formatted = f"{curr_symbol}{value:.2f}"
                                    values.append(value)
                                elif abs(value) >= large_divisor:
                                    formatted = f"{curr_symbol}{value/large_divisor:.1f}{large_suffix}"
                                    values.append(value)
                                elif abs(value) >= medium_divisor:
                                    formatted = f"{curr_symbol}{value/medium_divisor:.0f}{medium_suffix}"
                                    values.append(value)
                                else:
                                    formatted = f"{curr_symbol}{value:,.0f}"
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
            # Get currency info for proper formatting
            import yfinance as yf
            stock = yf.Ticker(ticker)
            info = stock.info
            currency = info.get('currency', 'USD')
            
            # Format currency symbol
            if currency == 'JPY':
                curr_symbol = '¥'
                large_divisor = 1_000_000_000_000  # Trillion
                large_suffix = 'T'
                medium_divisor = 1_000_000_000     # Billion  
                medium_suffix = 'B'
            elif currency == 'SGD':
                curr_symbol = 'S$'
                large_divisor = 1_000_000_000
                large_suffix = 'B'
                medium_divisor = 1_000_000
                medium_suffix = 'M'
            elif currency == 'EUR':
                curr_symbol = '€'
                large_divisor = 1_000_000_000
                large_suffix = 'B'
                medium_divisor = 1_000_000
                medium_suffix = 'M'
            elif currency == 'GBP':
                curr_symbol = '£'
                large_divisor = 1_000_000_000
                large_suffix = 'B'
                medium_divisor = 1_000_000
                medium_suffix = 'M'
            else:  # USD and others
                curr_symbol = '$'
                large_divisor = 1_000_000_000
                large_suffix = 'B'
                medium_divisor = 1_000_000
                medium_suffix = 'M'
            
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
                                if abs(value) >= large_divisor:
                                    formatted = f"{curr_symbol}{value/large_divisor:.1f}{large_suffix}"
                                    values.append(value)
                                elif abs(value) >= medium_divisor:
                                    formatted = f"{curr_symbol}{value/medium_divisor:.0f}{medium_suffix}"
                                    values.append(value)
                                else:
                                    formatted = f"{curr_symbol}{value:,.0f}"
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
            # Get currency info for proper formatting
            import yfinance as yf
            stock = yf.Ticker(ticker)
            info = stock.info
            currency = info.get('currency', 'USD')
            
            # Format currency symbol
            if currency == 'JPY':
                curr_symbol = '¥'
                large_divisor = 1_000_000_000_000  # Trillion
                large_suffix = 'T'
                medium_divisor = 1_000_000_000     # Billion  
                medium_suffix = 'B'
            elif currency == 'SGD':
                curr_symbol = 'S$'
                large_divisor = 1_000_000_000
                large_suffix = 'B'
                medium_divisor = 1_000_000
                medium_suffix = 'M'
            elif currency == 'EUR':
                curr_symbol = '€'
                large_divisor = 1_000_000_000
                large_suffix = 'B'
                medium_divisor = 1_000_000
                medium_suffix = 'M'
            elif currency == 'GBP':
                curr_symbol = '£'
                large_divisor = 1_000_000_000
                large_suffix = 'B'
                medium_divisor = 1_000_000
                medium_suffix = 'M'
            else:  # USD and others
                curr_symbol = '$'
                large_divisor = 1_000_000_000
                large_suffix = 'B'
                medium_divisor = 1_000_000
                medium_suffix = 'M'
            
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
                                if abs(value) >= large_divisor:
                                    formatted = f"{curr_symbol}{value/large_divisor:.1f}{large_suffix}"
                                    values.append(value)
                                elif abs(value) >= medium_divisor:
                                    formatted = f"{curr_symbol}{value/medium_divisor:.0f}{medium_suffix}"
                                    values.append(value)
                                else:
                                    formatted = f"{curr_symbol}{value:,.0f}"
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

    def _build_user_context(self, data_sources: Dict = None) -> str:
        """
        Build user-provided context section for AI prompts with all three user inputs.
        
        Args:
            data_sources: Dictionary containing dataSources, keyInformation, investmentContext
            
        Returns:
            Formatted user context string for prompt injection
        """
        logger.info(f"🔍 DEBUG: _build_user_context called with data_sources: {data_sources}")
        if not data_sources:
            logger.info(f"🔍 DEBUG: No data_sources provided, returning empty string")
            return ""
        
        context_sections = []
        context_sections.append("🚨🚨🚨 **SUPREME PRIORITY: USER-PROVIDED CONTEXT** 🚨🚨🚨")
        context_sections.append("=" * 100)
        context_sections.append("**THIS CONTEXT OVERRIDES ALL OTHER CONSIDERATIONS - MAXIMUM WEIGHTING**")
        context_sections.append("=" * 100)
        
        # Data Sources section - check both possible field names
        data_sources_text = data_sources.get('dataSources') or data_sources.get('data_sources')
        logger.info(f"🔍 DEBUG: Extracted data_sources_text: '{data_sources_text}'")
        if data_sources_text:
            context_sections.append(f"📊 **PRIMARY DATA SOURCES (EXCLUSIVE PRIORITY):** {data_sources_text}")
            logger.info(f"🔍 DEBUG: Added data sources section to context")
        
        # Key Information section - check both possible field names  
        key_info_text = data_sources.get('keyInformation') or data_sources.get('key_information')
        logger.info(f"🔍 DEBUG: Extracted key_info_text: '{key_info_text}'")
        if key_info_text:
            context_sections.append(f"🎯 **CRITICAL KEY INFORMATION (ABSOLUTE FOCUS):** {key_info_text}")
            logger.info(f"🔍 DEBUG: Added key information section to context")
            
        # Investment Context section - check both possible field names
        investment_context_text = data_sources.get('investmentContext') or data_sources.get('investment_context')
        logger.info(f"🔍 DEBUG: Extracted investment_context_text: '{investment_context_text}'")
        if investment_context_text:
            context_sections.append(f"💼 **INVESTMENT CONTEXT (BINDING CONSTRAINTS):** {investment_context_text}")
            logger.info(f"🔍 DEBUG: Added investment context section to context")
        
        # Add simple, high priority instructions for AI
        if len(context_sections) > 1:  # More than just the header
            context_sections.append("=" * 100)
            context_sections.append("")
            context_sections.append("🚨 **FOLLOW USER CONTEXT EXACTLY - HIGHEST PRIORITY** 🚨")
            context_sections.append("Base your entire analysis and conclusions on the user's context above")
            context_sections.append("")
        
        final_context = "\n".join(context_sections) if len(context_sections) > 1 else ""
        logger.info(f"🔍 DEBUG: Built user context ({len(final_context)} chars): {final_context[:500]}...")
        return final_context

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
        financial_data: Dict = None,
        investment_objective: str = None,
        data_sources: Dict = None
    ) -> str:
        """Build optimized prompt for Call 1 (slides 1-7) using modular base prompt + Call 1 specifics"""
        
        logger.info(f"🔧 Building Call 1 prompt for {ticker} (slides 1-7)")
        
        # Get base Robeco prompt (style, methodology, standards)
        base_prompt = self._build_base_robeco_prompt(company_name, ticker)
        
        # Get financial context using helper method
        financial_context = self._build_financial_context(company_name, financial_data)
        
        # Get analyst insights using helper method (4000 char limit for Call 1)
        analyst_insights = self._build_analyst_insights(analyses_data, content_limit=4000)
        
        # Get user context using helper method
        user_context = self._build_user_context(data_sources)
        
        # PRIMARY: Use comprehensive pre-processing system
        try:
            complete_stock_data = self._build_complete_stock_data_with_chart(ticker, financial_data)
            if not complete_stock_data.get('chart_ready') or not complete_stock_data.get('metrics_ready'):
                raise Exception("Primary system failed validation")
            logger.info(f"✅ PRIMARY: Complete stock data processed successfully")
        except Exception as e:
            # FALLBACK: Use legacy stock data method
            logger.warning(f"⚠️ PRIMARY system failed ({e}), using FALLBACK")
            legacy_stock_data = self._build_stock_price_data(ticker)
            complete_stock_data = {
                "chart_ready": False,
                "metrics_ready": False, 
                "fallback_data": legacy_stock_data,
                "data_points": len(legacy_stock_data.get('monthly_prices', [])),
                **legacy_stock_data  # Include legacy data for compatibility
            }
        
        # Debug: Log the actual stock data being passed to AI
        chart_ready_status = complete_stock_data.get('chart_ready', False)
        metrics_ready_status = complete_stock_data.get('metrics_ready', False)
        data_points_count = complete_stock_data.get('data_points', 0)
        using_fallback = 'fallback_data' in complete_stock_data
        
        logger.info(f"🔍 STOCK DATA BEING PASSED TO AI PROMPT:")
        logger.info(f"   📊 Chart ready: {chart_ready_status}")
        logger.info(f"   📈 Metrics ready: {metrics_ready_status}")
        logger.info(f"   📅 Data points: {data_points_count}")
        logger.info(f"   🔄 Using fallback: {using_fallback}")
        
        # Pre-extract all template values to avoid f-string formatting errors
        current_price = complete_stock_data.get('current_price', 'N/A')
        axis_labels = complete_stock_data.get('axis_labels', {})
        y_high = axis_labels.get('y_high', 'HIGH')
        y_mid_high = axis_labels.get('y_mid_high', 'MID-H')
        y_mid = axis_labels.get('y_mid', 'MID')
        y_mid_low = axis_labels.get('y_mid_low', 'MID-L')
        y_low = axis_labels.get('y_low', 'LOW')
        x_start = axis_labels.get('x_start', 'Start')
        x_mid1 = axis_labels.get('x_mid1', 'Mid1')
        x_mid2 = axis_labels.get('x_mid2', 'Mid2')
        x_end = axis_labels.get('x_end', 'End')
        chart_svg = complete_stock_data.get('chart_svg', '<polyline points="CALCULATE_COORDINATES_FROM_MONTHLY_PRICES_ARRAY" fill="none" stroke="#1976d2" stroke-width="3"/>')
        current_price_marker = complete_stock_data.get('current_price_marker', '<circle cx="460" cy="160" r="5" fill="#E63946"/><text x="460" y="145" text-anchor="middle" font-size="12" fill="#E63946" font-weight="bold">Current</text>')
        currency_symbol = complete_stock_data.get('currency', '$')
        
        # Get pre-calculated metrics for placeholder substitution
        metrics = complete_stock_data.get('metrics', {})
        
        # Build Call 1 specific requirements with precise HTML structure
        investment_focus = investment_objective or "comprehensive investment analysis"
        call1_specific = f"""
## ALPHA GENERATION PHASE 1: INVESTMENT FOUNDATION & MARKET INEFFICIENCY IDENTIFICATION (SLIDES 1-7)

### YOUR ELITE PM MANDATE FOR CALL 1:
As a top-tier hedge fund Portfolio Manager, your **first phase objective** is to establish the fundamental investment case that demonstrates **why this opportunity exists** and **why consensus is wrong**. You're not writing generic research—you're identifying specific market inefficiencies and mispricings that create asymmetric risk/reward profiles for sophisticated capital allocation.

**INVESTMENT OBJECTIVE FOCUS**: {investment_focus} - Tailor your analysis to support this specific investment objective and ensure all insights connect to this goal for {company_name} as of {datetime.now().strftime("%B %Y")}

**Your analytical depth must rival the best Renaissance Technologies or Bridgewater research.** Every insight should demonstrate the pattern recognition and multi-layered thinking that separates elite PMs from sell-side analysts.

### HTML STRUCTURE REQUIREMENTS - FOLLOW THESE PATTERNS:

**SLIDE 1 - EXECUTIVE SUMMARY & METRICS (analysis-item format):**

**Header Instructions:**
- Always use the exact Robeco logo URL: `https://images.ctfassets.net/tl4x668xzide/7mygwms2vuSwirnfvaCSvL/72d2bbd858a69aecbf59fd3fb8954484/robeco-logo-color.png`
- For company icons, use Clearbit format: `https://logo.clearbit.com/[company-domain].com` 
- Examples: `https://logo.clearbit.com/apple.com`, `https://logo.clearbit.com/microsoft.com`, `https://logo.clearbit.com/tesla.com`
- Fallback for any company: `https://placehold.co/20x20/005F90/ffffff?text=[TICKER]`
- Use actual company name (not placeholder) and determine rating based on your analysis

**CRITICAL: Use ACTUAL company financial data for ALL metrics - NO hardcoded values**

**SLIDE STRUCTURE PATTERNS:**

**All Slides Use Same Header:**
- Use exact same header structure for slides 1-7
- Only change the slide ID and page number in footer
- Keep Robeco logo, company icon, company name, and investment rating consistent between ALL slides

**TITLE WRITING REQUIREMENTS - MUST BE INSIGHTFUL & ACTIONABLE:**

**CORE PRINCIPLE**: Every title must immediately tell the PM **WHY this analysis matters for investment decisions**. Titles should combine:
- **Action/Dynamic Verb**: DRIVING, EXPANDING, ACCELERATING, DOMINATING, TRANSFORMING
- **Specific Competitive Advantage**: What unique strength {company_name} has
- **Investment Implication**: Why this creates alpha/outperformance

**FORMULA**: [COMPANY] + [ACTION VERB] + [SPECIFIC ADVANTAGE] + [Quantified IMPACT]

**EXCELLENT TITLE EXAMPLES:**
- "NVIDIA ACCELERATING AI CHIP DOMINANCE - 80% MARKET SHARE DRIVING 40% MARGINS" 
- "TESLA EXPANDING VERTICAL INTEGRATION - BATTERY TECHNOLOGY MOAT REDUCING COSTS 15%"
- "APPLE TRANSFORMING SERVICES ECOSYSTEM - 70% GROSS MARGIN BUSINESS GROWING 20% YoY"
- "MICROSOFT DOMINATING ENTERPRISE AI - AZURE INTEGRATION DRIVING $10B REVENUE OPPORTUNITY"

**CUSTOMIZE FOR ACTUAL COMPANY**: Replace generic examples with THIS company's specific strengths, using their actual financial metrics and competitive advantages.

**SLIDE 1 - EXECUTIVE SUMMARY & METRICS (analysis-item format):**
```html
<!-- CRITICAL INSTRUCTIONS:
1. Do NOT generate <style> tags - CSS is provided in template
2. ALL analysis must be company-specific and based on current fundamentals
3. INVESTMENT RATING must be determined by YOUR analysis - NOT hardcoded
4. Use Google Search to verify latest company data, earnings, analyst reports
5. Replace ALL placeholders with actual company-specific information
6. Rating must be CONSISTENT across ALL slides: OVERWEIGHT (green #2E7D32), NEUTRAL (orange #FF8C00), UNDERWEIGHT (red #C62828)
-->
<div class="slide" id="portrait-page-1">
    <header class="report-header-container">
        <div class="slide-logo" style="top: 65px;">
            <img src="https://images.ctfassets.net/tl4x668xzide/7mygwms2vuSwirnfvaCSvL/72d2bbd858a69aecbf59fd3fb8954484/robeco-logo-color.png" alt="Robeco Logo" style="height: 2rem;">
        </div>
        <div class="header-blue-border">
            <div class="company-header">
                <!-- INSTRUCTION: Replace with actual company domain (e.g., apple.com, microsoft.com) -->
                <!-- INSTRUCTION: Replace with company's main domain for logo. Use https://logo.clearbit.com/[COMPANY-DOMAIN].com format
                Examples: apple.com, microsoft.com, tesla.com, frasersproperty.com, etc. 
                Research the actual company domain from stock_data['company_name'] and use appropriate domain -->
                <img src="https://logo.clearbit.com/[COMPANY-DOMAIN].com" onerror="this.onerror=null;this.src='https://placehold.co/20x20/005F90/ffffff?text={ticker}';" alt="Company Icon" class="icon" style="margin-top: -5px; width: 20px; height: 20px;">
                <h1 class="name"><!-- INSTRUCTION: Use the FULL OFFICIAL company name from stock_data['company_name'] NOT the user input. Example: "Daikin Industries, Ltd." not "DAKIN" --></h1>
                <!-- INSTRUCTION: Use CONSISTENT rating across ALL slides. Choose ONE: OVERWEIGHT (green #2E7D32), NEUTRAL (orange #FF8C00), or UNDERWEIGHT (red #C62828) -->
                <div class="rating" style="color: [RATING-COLOR];">[INVESTMENT-RATING]</div>
            </div>
        </div>
    </header>

    <main style="display: flex; flex-direction: column; flex-grow: 1;">
        <!-- ⚠️ MANDATORY: COPY this metrics grid EXACTLY - DO NOT replace placeholders, DO NOT generate your own metrics -->
        <section class="metrics-grid">
            <div class="metrics-item"><div class="label">MAIN LISTING</div><div class="value">__TICKER_EXCHANGE__</div></div>
            <div class="metrics-item"><div class="label">SHARE PRICE</div><div class="value"><strong>__CURRENT_PRICE__</strong></div></div>
            <div class="metrics-item"><div class="label">MARKET CAP</div><div class="value"><strong>__MARKET_CAP__</strong></div></div>
            <div class="metrics-item"><div class="label">ENTERPRISE VALUE</div><div class="value"><strong>__ENTERPRISE_VALUE__</strong></div></div>
            <div class="metrics-item"><div class="label">52W RANGE</div><div class="value"><strong>__WEEK_52_RANGE__</strong></div></div>
            <div class="metrics-item"><div class="label">P/E (TTM/FWD)</div><div class="value"><strong>__PE_RATIO__</strong></div></div>
            <div class="metrics-item"><div class="label">EV/EBITDA (TTM)</div><div class="value"><strong>__EV_EBITDA__</strong></div></div>
            <div class="metrics-item"><div class="label">P/S (TTM)</div><div class="value"><strong>__PS_RATIO__</strong></div></div>
            <div class="metrics-item"><div class="label">P/B (MRQ)</div><div class="value"><strong>__PB_RATIO__</strong></div></div>
            <div class="metrics-item"><div class="label">PEG (TTM)</div><div class="value"><strong>__PEG_RATIO__</strong></div></div>
            <div class="metrics-item"><div class="label">MARGINS (G/O/N)</div><div class="value"><strong>__MARGINS__</strong></div></div>
            <div class="metrics-item"><div class="label">ROE (TTM)</div><div class="value"><strong>__ROE__</strong></div></div>
            <div class="metrics-item"><div class="label">ROA (TTM)</div><div class="value"><strong>__ROA__</strong></div></div>
            <div class="metrics-item"><div class="label">EBITDA MARGIN</div><div class="value"><strong>__EBITDA_MARGIN__</strong></div></div>
            <div class="metrics-item"><div class="label">TARGET RANGE</div><div class="value"><strong>__TARGET_RANGE__</strong></div></div>
            <div class="metrics-item"><div class="label">REV GROWTH (YoY)</div><div class="value"><strong>__REVENUE_GROWTH__</strong></div></div>
            <div class="metrics-item"><div class="label">EPS GROWTH (YoY)</div><div class="value"><strong>__EPS_GROWTH__</strong></div></div>
            <div class="metrics-item"><div class="label">BETA (5Y)</div><div class="value"><strong>__BETA__</strong></div></div>
            <div class="metrics-item"><div class="label">DEBT/EQUITY (MRQ)</div><div class="value"><strong>__DEBT_EQUITY__</strong></div></div>
            <div class="metrics-item"><div class="label">CURRENT RATIO</div><div class="value"><strong>__CURRENT_RATIO__</strong></div></div>
            <div class="metrics-item"><div class="label">FCF (TTM)</div><div class="value"><strong>__FREE_CASHFLOW__</strong></div></div>
            <div class="metrics-item"><div class="label">QUICK RATIO</div><div class="value"><strong>__QUICK_RATIO__</strong></div></div>
            <div class="metrics-item"><div class="label">DIV YIELD (TTM)</div><div class="value"><strong>__DIVIDEND_YIELD__</strong></div></div>
            <div class="metrics-item"><div class="label">PAYOUT RATIO</div><div class="value"><strong>__PAYOUT_RATIO__</strong></div></div>
            <div class="metrics-item"><div class="label">VOLUME (10D/3M)</div><div class="value"><strong>__VOLUME__</strong></div></div>
        </section>
        <div class="intro-and-chart-container">
            <div class="intro-text-block">
                <!-- EXECUTIVE SUMMARY - CONCISE & PRECISE (150 words MAX):

                YOUR CONTRARIAN THESIS (50 words): What's your differentiated view vs consensus? Be specific.
                KEY CATALYST (50 words): What upcoming development will prove your thesis? Include timing.
                PRICE TARGET (50 words): Specific target with probability and timeline.

                ⚡ CRITICAL: High info density - every word must add value. NO generic statements. -->
            </div>
            <div style="height: 420px; background: white; border: 1px solid #ccc; padding: 12px;">
                <h4 style="text-align: center; margin-bottom: 15px; font-size: 16px; color: #333; font-weight: bold;">5-Year Stock Price ({ticker}) - Current: {current_price}</h4>
                <svg viewBox="0 0 500 360" style="width: 100%; height: 380px;">
                    <!-- CHART DATA STATUS: Using PRIMARY system pre-processed data -->
                    <!-- PRIMARY: Use pre-processed chart if available, FALLBACK: Use raw data -->
                    <!-- Chart SVG and metrics pre-processed by PRIMARY system -->
                    
                    <!-- Y-AXIS (Price axis) - Use reasonable scale, not just min/max -->
                    <line x1="60" y1="40" x2="60" y2="320" stroke="#333" stroke-width="2"/>
                    <!-- Y-AXIS LABELS: Use pre-processed values if available -->
                    <text x="55" y="45" text-anchor="end" font-size="12" fill="#333" font-weight="bold">{y_high}</text>
                    <text x="55" y="105" text-anchor="end" font-size="12" fill="#333">{y_mid_high}</text>
                    <text x="55" y="180" text-anchor="end" font-size="12" fill="#333">{y_mid}</text>
                    <text x="55" y="255" text-anchor="end" font-size="12" fill="#333">{y_mid_low}</text>
                    <text x="55" y="315" text-anchor="end" font-size="12" fill="#333" font-weight="bold">{y_low}</text>
                    
                    <!-- Y-AXIS GRID LINES for better readability -->
                    <line x1="60" y1="40" x2="460" y2="40" stroke="#e0e0e0" stroke-width="1" stroke-dasharray="2,2"/>
                    <line x1="60" y1="105" x2="460" y2="105" stroke="#e0e0e0" stroke-width="1" stroke-dasharray="2,2"/>
                    <line x1="60" y1="180" x2="460" y2="180" stroke="#e0e0e0" stroke-width="1" stroke-dasharray="2,2"/>
                    <line x1="60" y1="255" x2="460" y2="255" stroke="#e0e0e0" stroke-width="1" stroke-dasharray="2,2"/>
                    <line x1="60" y1="320" x2="460" y2="320" stroke="#e0e0e0" stroke-width="1" stroke-dasharray="2,2"/>
                    
                    <!-- X-AXIS (Time axis) -->
                    <line x1="60" y1="320" x2="460" y2="320" stroke="#333" stroke-width="2"/>
                    <!-- X-AXIS LABELS: Use pre-processed date labels -->
                    <text x="60" y="340" text-anchor="start" font-size="12" fill="#333" font-weight="bold">{x_start}</text>
                    <text x="180" y="340" text-anchor="middle" font-size="12" fill="#333">{x_mid1}</text>
                    <text x="300" y="340" text-anchor="middle" font-size="12" fill="#333">{x_mid2}</text>
                    <text x="460" y="340" text-anchor="end" font-size="12" fill="#333" font-weight="bold">{x_end}</text>
                    
                    <!-- X-AXIS GRID LINES aligned with dynamic date labels -->
                    <line x1="60" y1="40" x2="60" y2="320" stroke="#e0e0e0" stroke-width="1" stroke-dasharray="2,2"/>
                    <line x1="180" y1="40" x2="180" y2="320" stroke="#e0e0e0" stroke-width="1" stroke-dasharray="2,2"/>
                    <line x1="300" y1="40" x2="300" y2="320" stroke="#e0e0e0" stroke-width="1" stroke-dasharray="2,2"/>
                    <line x1="460" y1="40" x2="460" y2="320" stroke="#e0e0e0" stroke-width="1" stroke-dasharray="2,2"/>
                    
                    <!-- STOCK PRICE LINE: Use pre-processed SVG if available, otherwise calculate -->
                    {chart_svg}
                    
                    <!-- CURRENT PRICE MARKER: Use pre-processed marker if available -->
                    {current_price_marker}
                    
                    <!-- CHART TITLE -->
                    <text x="260" y="25" text-anchor="middle" font-size="14" fill="#333" font-weight="bold">Price (in {currency_symbol})</text>

                </svg>
            </div>
        </div>
        <div class="analysis-sections">
            [CREATE 4 analysis-item blocks with these EXACT titles and sophisticated PM-level focus areas with high info density and concise and precise - ALL Google Search verified as of {datetime.now().strftime("%B %Y")}:]
            
            [ANALYSIS ITEM 1 - REASON TO ANALYZE: Write like a top PM explaining to a CIO why this is worth portfolio allocation. Focus on: market dislocation, timing catalyst, asymmetric risk/reward, differentiated insight that others miss. USE GOOGLE SEARCH to verify current market positioning, recent stock performance, and analyst sentiment. Show what consensus gets wrong with specific evidence. 150 words max.]
            
            [ANALYSIS ITEM 2 - LONG TERM OUTLOOK: Demonstrate advanced industry understanding and competitive dynamics. Quantify the TAM expansion, market share trajectory, and sustainable competitive advantages. Include specific 3-5 year targets with supporting thesis. USE GOOGLE SEARCH to verify industry growth forecasts, competitive landscape changes, and market size data. Connect strategy to future cash flows. 150 words max.]
            
            [ANALYSIS ITEM 3 - FUNDAMENTAL CONCLUSION: Show sophisticated financial analysis connecting current metrics to future value creation. Explain the investment thesis with DCF-level thinking, margin expansion catalysts, and capital allocation effectiveness. USE GOOGLE SEARCH to verify latest financial metrics, margin trends, and capital allocation announcements. Quantify the path to higher returns. 150 words max.]
            
            [ANALYSIS ITEM 4 - FIT WITH TOP-DOWN VIEW: Connect this stock pick to macro themes and sector allocation strategy. Show how this fits portfolio construction, correlation benefits, and thematic exposure. Demonstrate institutional-level portfolio thinking. USE GOOGLE SEARCH to verify current macro trends, sector performance, and thematic investment flows. Show asymmetric risk/reward profile. 150 words max.]
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
        <div class="slide-logo" style="top: 65px;">
            <img src="https://images.ctfassets.net/tl4x668xzide/7mygwms2vuSwirnfvaCSvL/72d2bbd858a69aecbf59fd3fb8954484/robeco-logo-color.png" alt="Robeco Logo" style="height: 2rem;">
        </div>
        <div class="header-blue-border">
            <div class="company-header">
                <!-- INSTRUCTION: Replace with actual company domain (e.g., apple.com, microsoft.com) -->
                <!-- INSTRUCTION: Replace with company's main domain for logo. Use https://logo.clearbit.com/[COMPANY-DOMAIN].com format
                Examples: apple.com, microsoft.com, tesla.com, frasersproperty.com, etc. 
                Research the actual company domain from stock_data['company_name'] and use appropriate domain -->
                <img src="https://logo.clearbit.com/[COMPANY-DOMAIN].com" onerror="this.onerror=null;this.src='https://placehold.co/20x20/005F90/ffffff?text={ticker}';" alt="Company Icon" class="icon" style="margin-top: -5px; width: 20px; height: 20px;">
                <h1 class="name"><!-- INSTRUCTION: Use the FULL OFFICIAL company name from stock_data['company_name'] NOT the user input. Example: "Daikin Industries, Ltd." not "DAKIN" --></h1>
                <!-- INSTRUCTION: Use CONSISTENT rating across ALL slides. Choose ONE: OVERWEIGHT (green #2E7D32), NEUTRAL (orange #FF8C00), or UNDERWEIGHT (red #C62828) -->
                <div class="rating" style="color: [RATING-COLOR];">[INVESTMENT-RATING]</div>
            </div>
        </div>
    </header>
    <main>
        <div class="analysis-sections">
            [CREATE 5 analysis-item blocks with these EXACT financial analysis categories and company-specific titles - ALL Google Search verified as of {datetime.now().strftime("%B %Y")}:] for {investment_focus}
            
            [VALUATION - CREATE SPECIFIC TITLE: Research {company_name}'s current valuation metrics (P/E, EV/EBITDA, P/B) vs peers and historical averages. Create specific title like "VALUATION - Compelling Entry Point at 17.55x FWD P/E" or "VALUATION - Trading at Premium but Justified by Growth Profile". USE GOOGLE SEARCH to verify latest analyst price targets, peer comparisons, and valuation multiples. Explain why current valuation presents opportunity or risk. Include specific price targets and timeline. 150 words max.]
            
            [RISKS - CREATE SPECIFIC TITLE: Identify key investment risks specific to {company_name}'s business model and market position. Create specific title like "RISKS - Geopolitical Instability & Supply Chain Volatility Mitigated by Integration" or "RISKS - Regulatory Changes Offset by Diversification Strategy". USE GOOGLE SEARCH to verify current risk factors, recent news, and management commentary. Quantify impact and mitigation strategies. 150 words max.]
            
            [QUANTITATIVE CONCLUSION - CREATE SPECIFIC TITLE: Present quantitative analysis using {company_name}'s financial metrics to support investment thesis. Create specific title like "QUANTITATIVE - 15% ROE and 25% EBITDA Growth Drive Alpha Generation" or "QUANTITATIVE - Strong FCF Conversion Supports 12% IRR Target". USE GOOGLE SEARCH to verify latest financial metrics and trends. Connect numbers to investment conclusion. 150 words max.]
            
            [SHORT TERM OUTLOOK - CREATE SPECIFIC TITLE: Analyze near-term catalysts and drivers for {company_name}. Create specific title like "SHORT TERM - U.S. Applied Business Driving Q2 FY2026 Beat" or "SHORT TERM - New Product Launch Expected to Drive Q4 Revenue Acceleration". USE GOOGLE SEARCH to verify upcoming earnings, product launches, and management guidance. Include specific timeframes and expected impact. 150 words max.]
            
            [EARNINGS REVISIONS - CREATE SPECIFIC TITLE: Analyze earnings revision trends and expectations for {company_name}. Create specific title like "EARNINGS REVISIONS - Consensus Estimates 15% Below Our Target on Cost Synergies" or "EARNINGS REVISIONS - Upgrade Cycle Supports Above-Consensus Growth". USE GOOGLE SEARCH to verify latest analyst revisions, consensus estimates, and earnings surprise history. Explain revision drivers and implications. 150 words max.]
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
    <header class="report-header-container">
        <div class="slide-logo" style="top: 65px;">
            <img src="https://images.ctfassets.net/tl4x668xzide/7mygwms2vuSwirnfvaCSvL/72d2bbd858a69aecbf59fd3fb8954484/robeco-logo-color.png" alt="Robeco Logo" style="height: 2rem;">
        </div>
        <div class="header-blue-border">
            <div class="company-header">
                <!-- INSTRUCTION: Replace with actual company domain (e.g., apple.com, microsoft.com) -->
                <!-- INSTRUCTION: Replace with company's main domain for logo. Use https://logo.clearbit.com/[COMPANY-DOMAIN].com format
                Examples: apple.com, microsoft.com, tesla.com, frasersproperty.com, etc. 
                Research the actual company domain from stock_data['company_name'] and use appropriate domain -->
                <img src="https://logo.clearbit.com/[COMPANY-DOMAIN].com" onerror="this.onerror=null;this.src='https://placehold.co/20x20/005F90/ffffff?text={ticker}';" alt="Company Icon" class="icon" style="margin-top: -5px; width: 20px; height: 20px;">
                <h1 class="name"><!-- INSTRUCTION: Use the FULL OFFICIAL company name from stock_data['company_name'] NOT the user input. Example: "Daikin Industries, Ltd." not "DAKIN" --></h1>
                <!-- INSTRUCTION: Use CONSISTENT rating across ALL slides. Choose ONE: OVERWEIGHT (green #2E7D32), NEUTRAL (orange #FF8C00), or UNDERWEIGHT (red #C62828) -->
                <div class="rating" style="color: [RATING-COLOR];">[INVESTMENT-RATING]</div>
            </div>
        </div>
    </header>
    <main class="report-prose">
        <h3>[Write a specific, insightful title that captures {company_name}'s unique investment highlights - what makes them a superior investment vs all alternatives? Focus on quantifiable competitive advantages that drive superior returns. Example: "TESLA'S VERTICAL INTEGRATION & BATTERY TECHNOLOGY MOAT" or "NVIDIA'S AI CHIP ARCHITECTURE DOMINANCE" - avoid generic titles]</h3>
        
        <h4>[Identify the #1 investment strength and write a subsection title that shows HOW this creates economic value. Think like a PM: what specific mechanism drives superior margins/growth/returns? Example: "Ecosystem Lock-in Strategy: 95% Customer Retention Drives 40% Gross Margins" or "Platform Network Effects: 70% Market Share Expansion"]</h4>
        <p>[Write 400-500 words with ELITE-LEVEL ANALYTICAL DEPTH that demonstrates differentiated insights. NATURAL ANALYSIS FLOW: 1) CORE INVESTMENT STRENGTH: Lead with your key analytical insight about this competitive advantage (e.g., "Network effects are accelerating adoption curves exponentially rather than linearly") 2) SUPPORTING EVIDENCE: Present specific data and metrics supporting your view (e.g., "NPS tracking shows 85% customer satisfaction vs 60% industry average, indicating expanding pricing power") 3) HISTORICAL PERFORMANCE: Explain how this strength drove past results (e.g., "This moat enabled 300bps margin expansion during 2022-23 downturn while peers contracted") 4) QUANTIFIED IMPACT: Use specific metrics and peer comparisons (e.g., "Management guidance suggests this will drive $2.5B incremental revenue by 2025") 5) FORWARD CATALYSTS: Identify specific events proving your thesis (e.g., "Q3 product launch will demonstrate 40% faster implementation vs legacy solutions") 6) INVESTMENT IMPLICATION: Impact on valuation and timeline (e.g., "This justifies 25x multiple vs 18x peer average, driving $15/share upside by year-end"). Present YOUR analytical conclusions first, reference market views only when directly relevant. Show sophisticated understanding of business model economics and competitive dynamics.]</p>
        
        <h4>[Second major investment strength with focus on financial impact and differentiation from peers]</h4>
        <p>[400-500 words of sophisticated analysis connecting this strength to valuation expansion and alpha generation]</p>
        
        <h4>[Third investment strength focusing on growth drivers and scalability]</h4>
        <p>[400-500 words demonstrating deep understanding of business model economics and expansion potential]</p>
        
        <h4>[Fourth investment strength emphasizing risk-adjusted returns and portfolio benefits]</h4>
        <p>[400-500 words showing institutional-level thinking about correlation, volatility, and portfolio construction]</p>
    </main>
    <footer class="report-footer"><p>Robeco Investment Research</p><p>Page 3 / 15</p></footer>
</div>

<div class="slide report-prose" id="catalyst-page">
    <header class="report-header-container">
        <div class="slide-logo" style="top: 65px;">
            <img src="https://images.ctfassets.net/tl4x668xzide/7mygwms2vuSwirnfvaCSvL/72d2bbd858a69aecbf59fd3fb8954484/robeco-logo-color.png" alt="Robeco Logo" style="height: 2rem;">
        </div>
        <div class="header-blue-border">
            <div class="company-header">
                <!-- INSTRUCTION: Replace with actual company domain (e.g., apple.com, microsoft.com) -->
                <!-- INSTRUCTION: Replace with company's main domain for logo. Use https://logo.clearbit.com/[COMPANY-DOMAIN].com format
                Examples: apple.com, microsoft.com, tesla.com, frasersproperty.com, etc. 
                Research the actual company domain from stock_data['company_name'] and use appropriate domain -->
                <img src="https://logo.clearbit.com/[COMPANY-DOMAIN].com" onerror="this.onerror=null;this.src='https://placehold.co/20x20/005F90/ffffff?text={ticker}';" alt="Company Icon" class="icon" style="margin-top: -5px; width: 20px; height: 20px;">
                <h1 class="name"><!-- INSTRUCTION: Use the FULL OFFICIAL company name from stock_data['company_name'] NOT the user input. Example: "Daikin Industries, Ltd." not "DAKIN" --></h1>
                <!-- INSTRUCTION: Use CONSISTENT rating across ALL slides. Choose ONE: OVERWEIGHT (green #2E7D32), NEUTRAL (orange #FF8C00), or UNDERWEIGHT (red #C62828) -->
                <div class="rating" style="color: [RATING-COLOR];">[INVESTMENT-RATING]</div>
            </div>
        </div>
    </header>
    <main class="report-prose">
        <h3>[ANALYZE {company_name}'S ACTUAL BUSINESS - Write title showing THE SPECIFIC CATALYST STORYLINE for THIS company. Study what drove {company_name}'s stock historically, what's changing NOW, and future implications. Example based on REAL analysis: "FLCT'S LOGISTICS RENTAL REVERSIONS: FROM 2023 DPU PRESSURE TO 2026 RECOVERY" or "APPLE'S SERVICES INFLECTION: BREAKING THE HARDWARE DEPENDENCE CYCLE"]</h3>
        
        **🎯 MANDATORY CATALYST ANALYSIS APPROACH:**
        
        **Step 1: STUDY {company_name}'S HISTORICAL STOCK DRIVERS**
        - What fundamental changes moved {company_name}'s stock price in past 3 years? (important to understand the company's business model and how it has changed over time)
        - Which earnings releases, business developments, or industry events drove major moves?
        - What valuation multiples does {company_name} trade at during good/bad times?
        
        **Step 2: IDENTIFY {company_name}'S CURRENT CATALYST DEVELOPMENTS**  
        - What business developments are happening NOW that mirror past stock drivers?
        - Which upcoming earnings, product launches, or strategic moves matter for {company_name}?
        - What's priced in vs what market is missing about {company_name}?
        
        **Step 3: CREATE COMPANY-SPECIFIC CATALYST SECTIONS**
        - Write 3-4 catalyst subsections based on {company_name}'s ACTUAL business model
        - Connect {company_name}'s past stock performance to current developments
        - Show forward-looking view of {company_name}'s specific triggers
        
        [CREATE 3-4 CATALYST SECTIONS SPECIFIC TO {company_name}'S BUSINESS - NOT GENERIC TEMPLATES. Each 150 words showing: HISTORICAL PATTERN for this company → CURRENT DEVELOPMENT for this company → FUTURE STOCK IMPACT for this company. Base everything on {company_name}'s actual fundamentals, stock history, and business model.]
    </main>
    <footer class="report-footer"><p>Robeco Investment Research</p><p>Page 4 / 15</p></footer>
</div>

<div class="slide report-prose" id="company-analysis-page">
    <header class="report-header-container">
        <div class="slide-logo" style="top: 65px;">
            <img src="https://images.ctfassets.net/tl4x668xzide/7mygwms2vuSwirnfvaCSvL/72d2bbd858a69aecbf59fd3fb8954484/robeco-logo-color.png" alt="Robeco Logo" style="height: 2rem;">
        </div>
        <div class="header-blue-border">
            <div class="company-header">
                <!-- INSTRUCTION: Replace with actual company domain (e.g., apple.com, microsoft.com) -->
                <!-- INSTRUCTION: Replace with company's main domain for logo. Use https://logo.clearbit.com/[COMPANY-DOMAIN].com format
                Examples: apple.com, microsoft.com, tesla.com, frasersproperty.com, etc. 
                Research the actual company domain from stock_data['company_name'] and use appropriate domain -->
                <img src="https://logo.clearbit.com/[COMPANY-DOMAIN].com" onerror="this.onerror=null;this.src='https://placehold.co/20x20/005F90/ffffff?text={ticker}';" alt="Company Icon" class="icon" style="margin-top: -5px; width: 20px; height: 20px;">
                <h1 class="name"><!-- INSTRUCTION: Use the FULL OFFICIAL company name from stock_data['company_name'] NOT the user input. Example: "Daikin Industries, Ltd." not "DAKIN" --></h1>
                <!-- INSTRUCTION: Use CONSISTENT rating across ALL slides. Choose ONE: OVERWEIGHT (green #2E7D32), NEUTRAL (orange #FF8C00), or UNDERWEIGHT (red #C62828) -->
                <div class="rating" style="color: [RATING-COLOR];">[INVESTMENT-RATING]</div>
            </div>
        </div>
    </header>
    <main class="report-prose">
        <h3>[Create company-specific investment thesis title that captures the unique alpha opportunity for {company_name} as of {datetime.now().strftime("%B %Y")}. Examples: "NVIDIA'S AI INFRASTRUCTURE MONOPOLY: $400B TAM WITH 80% MARKET DOMINANCE" or "TESLA'S MANUFACTURING REVOLUTION: $25K MODEL UNLOCKING 50M UNIT TAM" - Use actual company name, specific metrics, and the core alpha driver that makes this stock outperform]</h3>
        
        [INSTRUCTION: Identify 3-4 MOST CRITICAL ALPHA-GENERATING THEMES specific to {company_name}'s situation. DO NOT use fixed sections. Choose from company-specific opportunities like:]
        
        [- Business Model Innovation (e.g., subscription transformation, platform economics)]
        [- Technology Leadership (e.g., AI advantage, patent moat, R&D superiority)]  
        [- Market Disruption (e.g., new category creation, legacy player displacement)]
        [- Geographic Expansion (e.g., China penetration, India opportunity, Europe growth)]
        [- Competitive Moat Expansion (e.g., ecosystem lock-in, network effects, scale economics)]
        [- Regulatory Advantage (e.g., policy beneficiary, compliance moat, licensing barriers)]
        [- ESG Transformation (e.g., sustainability leadership, carbon advantage, social impact)]
        [- Capital Allocation Mastery (e.g., buyback strategy, dividend growth, M&A execution)]
        [- Management Transition (e.g., new CEO catalyst, strategic pivot, operational excellence)]
        [- Cyclical Recovery (e.g., downturn bottom, capacity utilization, pricing power return)]
        [- Activist Catalyst (e.g., shareholder pressure, strategic review, asset optimization)]
        [- Spin-off Value (e.g., conglomerate discount, pure-play premium, asset unlock)]
        
        <h4>[ALPHA THEME 1 - CHOOSE MOST CRITICAL]: [Create insight-rich title specific to {company_name}. Example: "NVIDIA's CUDA Software Moat: $50B Ecosystem with 95% Developer Mind Share" or "Tesla's 4680 Battery Breakthrough: 50% Cost Reduction Enabling $25K Model"]</h4>
        <p>[Write 750-800 words proving why this theme creates alpha for {company_name}. FRAMEWORK: 1) OPPORTUNITY QUANTIFICATION: Size the specific opportunity with TAM, growth rates, margin impact 2){company_name} ADVANTAGE: Explain unique positioning vs competitors with specific metrics 3) MARKET MISUNDERSTANDING: What consensus gets wrong about this opportunity 4) CATALYST TIMING: When this theme will drive stock performance with specific timeline 5) FINANCIAL IMPACT: Connect to earnings growth, margin expansion, multiple re-rating with numbers. Use Google-verified current data and forward-looking insights.]</p>
        
        <h4>[ALPHA THEME 2 - CHOOSE SECOND MOST CRITICAL]: [Create insight-rich title specific to {company_name}. Example: "Apple's India Manufacturing: $25B Smartphone Market with 15% Price Reduction" or "Amazon's AI Infrastructure: Bedrock $10B Revenue Potential vs Google/Azure"]</h4>
        <p>[Write 750-800 words proving alpha generation. Same framework as Theme 1 - focus on what makes {company_name} unique in this specific opportunity area.]</p>
        
        <h4>[ALPHA THEME 3 - CHOOSE THIRD MOST CRITICAL]: [Create insight-rich title specific to {company_name}. Example: "Microsoft's Enterprise AI Stack: Teams/Office Integration Creating $50B TAM" or "Meta's Metaverse Recovery: Reality Labs Break-even by 2026"]</h4>
        <p>[Write 750-800 words proving alpha generation. Same framework - connect theme to specific stock outperformance catalyst.]</p>
        
        <h4>[ALPHA THEME 4 - OPTIONAL FOURTH THEME IF CRITICAL]: [Create insight-rich title if there's a fourth major alpha driver specific to {company_name}]</h4>
        <p>[Write 750-800 words if needed for complete investment story. Focus on timing and quantified impact.]</p>
    </main>
    <footer class="report-footer"><p>Robeco Investment Research</p><p>Page 5 / 15</p></footer>
</div>

<div class="slide report-prose" id="slide-industry-analysis">
    <header class="report-header-container">
        <div class="slide-logo" style="top: 65px;">
            <img src="https://images.ctfassets.net/tl4x668xzide/7mygwms2vuSwirnfvaCSvL/72d2bbd858a69aecbf59fd3fb8954484/robeco-logo-color.png" alt="Robeco Logo" style="height: 2rem;">
        </div>
        <div class="header-blue-border">
            <div class="company-header">
                <!-- INSTRUCTION: Replace with actual company domain (e.g., apple.com, microsoft.com) -->
                <!-- INSTRUCTION: Replace with company's main domain for logo. Use https://logo.clearbit.com/[COMPANY-DOMAIN].com format
                Examples: apple.com, microsoft.com, tesla.com, frasersproperty.com, etc. 
                Research the actual company domain from stock_data['company_name'] and use appropriate domain -->
                <img src="https://logo.clearbit.com/[COMPANY-DOMAIN].com" onerror="this.onerror=null;this.src='https://placehold.co/20x20/005F90/ffffff?text={ticker}';" alt="Company Icon" class="icon" style="margin-top: -5px; width: 20px; height: 20px;">
                <h1 class="name"><!-- INSTRUCTION: Use the FULL OFFICIAL company name from stock_data['company_name'] NOT the user input. Example: "Daikin Industries, Ltd." not "DAKIN" --></h1>
                <!-- INSTRUCTION: Use CONSISTENT rating across ALL slides. Choose ONE: OVERWEIGHT (green #2E7D32), NEUTRAL (orange #FF8C00), or UNDERWEIGHT (red #C62828) -->
                <div class="rating" style="color: [RATING-COLOR];">[INVESTMENT-RATING]</div>
            </div>
        </div>
    </header>
    <main>
        <h3>[Create contrarian sector insight specific to {company_name}'s industry situation that drives investment outperformance. Examples: "SEMICONDUCTOR AI GOLD RUSH: NVIDIA CAPTURES 80% OF $400B INFRASTRUCTURE BUILD" or "CLOUD WARS ENDGAME: ENTERPRISE AI MIGRATION CREATING WINNER-TAKE-ALL" - Focus on sector dynamics that specifically benefit {company_name} vs peers]</h3>
        
        [INSTRUCTION: Identify 2-3 MOST CRITICAL SECTOR THEMES that directly impact {company_name}'s investment case. Choose themes based on current industry situation:]
        
        [SECTOR THEME OPTIONS: Market Transformation, Technology Cycle, Regulatory Disruption, Competitive Consolidation, Supply Chain Shifts, ESG Requirements, Geopolitical Impact, Capital Cycle, Customer Behavior Change, Pricing Power Inflection, etc.]
        
        <h4>[SECTOR THEME 1 - MOST CRITICAL FOR {company_name}]: [Create sector-insight title. Example: "AI Infrastructure Capex Supercycle: $150B→$400B TAM Favoring NVIDIA's 80% Market Share" or "Enterprise AI Adoption: $200B Cloud Migration Benefiting AWS 32% Market Position"]</h4>
        <p>[Write 800-900 words proving how this sector trend specifically benefits {company_name}. FRAMEWORK: 1) SECTOR TREND QUANTIFICATION: Size the trend with Google-verified TAM, growth rates, timeline 2) {company_name} POSITIONING: Exact market share, competitive advantage in this trend vs peers 3) MARKET MISUNDERSTANDING: What consensus gets wrong about sector dynamics 4) CATALYST TIMING: When sector trend accelerates with impact on {company_name} 5) FINANCIAL IMPLICATIONS: Connect to {company_name}'s earnings/margin/multiple expansion. Use current industry data and forward projections.]</p>
        
        <h4>[SECTOR THEME 2 - SECOND MOST CRITICAL]: [Create sector-insight title specific to {company_name}'s opportunity. Example: "Geopolitical Supply Chain Reshoring: $50B Domestic Chip Investment Benefiting Intel Manufacturing" or "SaaS Margin Expansion Cycle: Enterprise Software Pricing Power Favoring Microsoft/Salesforce"]</h4>
        <p>[Write 800-900 words proving sector advantage for {company_name}. Same framework - focus on what gives {company_name} specific edge in this sector dynamic.]</p>
        
        <h4>[SECTOR THEME 3 - OPTIONAL THIRD THEME IF CRITICAL]: [Create sector-insight title if there's a third major sector dynamic affecting {company_name}]</h4>
        <p>[Write 800-900 words if needed for complete sector story. Connect to stock outperformance catalyst.]</p>
    </main>
    <footer class="report-footer"><p>Robeco Investment Research</p><p>Page 6 / 15</p></footer>
</div>

<div class="slide report-prose" id="slide-competitive-advantage">
    <header class="report-header-container">
        <div class="slide-logo" style="top: 65px;">
            <img src="https://images.ctfassets.net/tl4x668xzide/7mygwms2vuSwirnfvaCSvL/72d2bbd858a69aecbf59fd3fb8954484/robeco-logo-color.png" alt="Robeco Logo" style="height: 2rem;">
        </div>
        <div class="header-blue-border">
            <div class="company-header">
                <!-- INSTRUCTION: Replace with actual company domain (e.g., apple.com, microsoft.com) -->
                <!-- INSTRUCTION: Replace with company's main domain for logo. Use https://logo.clearbit.com/[COMPANY-DOMAIN].com format
                Examples: apple.com, microsoft.com, tesla.com, frasersproperty.com, etc. 
                Research the actual company domain from stock_data['company_name'] and use appropriate domain -->
                <img src="https://logo.clearbit.com/[COMPANY-DOMAIN].com" onerror="this.onerror=null;this.src='https://placehold.co/20x20/005F90/ffffff?text={ticker}';" alt="Company Icon" class="icon" style="margin-top: -5px; width: 20px; height: 20px;">
                <h1 class="name"><!-- INSTRUCTION: Use the FULL OFFICIAL company name from stock_data['company_name'] NOT the user input. Example: "Daikin Industries, Ltd." not "DAKIN" --></h1>
                <!-- INSTRUCTION: Use CONSISTENT rating across ALL slides. Choose ONE: OVERWEIGHT (green #2E7D32), NEUTRAL (orange #FF8C00), or UNDERWEIGHT (red #C62828) -->
                <div class="rating" style="color: [RATING-COLOR];">[INVESTMENT-RATING]</div>
            </div>
        </div>
    </header>
    <main>
        <h3>[Create quantified competitive advantage thesis specific to {company_name}'s moat that drives alpha generation as of {datetime.now().strftime("%B %Y")}. Examples: "NVIDIA'S AI SOFTWARE ECOSYSTEM: $50B CUDA MOAT WITH 95% DEVELOPER MIND SHARE" or "TESLA'S MANUFACTURING MACHINE: 50% COST ADVANTAGE ENABLING $25K MODEL" - Focus on {company_name}'s strongest, most defensible competitive advantages]</h3>
        
        [INSTRUCTION: Identify 2-3 STRONGEST COMPETITIVE ADVANTAGES that create sustainable alpha for {company_name}. Choose moats based on what's most defensible:]
        
        [MOAT OPTIONS: Technology Leadership, Scale Economics, Network Effects, Brand Premium, Switching Costs, Regulatory Barriers, Geographic Advantages, Vertical Integration, IP Portfolio, Management Execution, Capital Access, Data Advantages, Platform Control, etc.]
        
        <h4>[COMPETITIVE MOAT 1 - STRONGEST FOR {company_name}]: [Create quantified-moat title. Example: "CUDA Software Ecosystem: $50B Platform with 95% AI Developer Mind Share" or "iPhone Ecosystem Lock-In: 1.4B Devices Creating $80B Annual Services Revenue"]</h4>
        <p>[Write 800-900 words proving sustainable competitive advantage for {company_name}. FRAMEWORK: 1) MOAT QUANTIFICATION: Measure advantage with specific financial metrics, market share, switching costs 2) SUSTAINABILITY PROOF: Why advantage is expanding not contracting vs historical periods 3) COMPETITOR FAILURE ANALYSIS: Why peers cannot replicate advantage in next 2-3 years with specific examples 4) PRICING POWER CONNECTION: How moat enables premium pricing, margin expansion, market share gains 5) ALPHA GENERATION: Connect moat strength to specific stock outperformance catalyst with timing. Use Google-verified competitive intelligence.]</p>
        
        <h4>[COMPETITIVE MOAT 2 - SECOND STRONGEST]: [Create quantified-moat title specific to {company_name}. Example: "Manufacturing Cost Leadership: 50% Lower Production Costs vs Legacy Automakers" or "Enterprise Software Stickiness: 95% Renewal Rates with 120% Net Revenue Retention"]</h4>
        <p>[Write 800-900 words proving second competitive advantage. Same framework - show why this moat creates alpha vs peers.]</p>
        
        <h4>[COMPETITIVE MOAT 3 - OPTIONAL THIRD MOAT IF CRITICAL]: [Create quantified-moat title if there's a third major competitive advantage for {company_name}]</h4>
        <p>[Write 800-900 words if needed for complete competitive story. Focus on moat expansion trajectory.]</p>
    </main>
    <footer class="report-footer"><p>Robeco Investment Research</p><p>Page 7 / 15</p></footer>
</div>
```

**INSTRUCTIONS FOR HTML STRUCTURE:**
- Replace "Apple" examples with actual company being analyzed
- Use company-specific Clearbit URL: `https://logo.clearbit.com/[company-domain].com`
- Create insightful, company-specific titles that show unique investment insights
- Keep exact HTML structure but customize content for each company

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
- **Analysis Items**: EXACTLY 5 sections with SPECIFIC titles and content focus:
  1. **VALUATION** - Compelling Entry Point at [X]x FWD P/E: Current valuation metrics, DCF analysis, peer comparison, intrinsic value calculation
  2. **RISKS** - [Primary Risk Category] & [Secondary Risk Category]: Key downside risks with specific impact quantification
  3. **QUANTITATIVE CONCLUSION** - Strong [Key Metric] Generation & [Financial Strength]: ROE, ROIC, cash flow analysis, balance sheet strength
  4. **SHORT TERM OUTLOOK** - [Specific Timeline] Earnings & [Key Catalyst]: Near-term catalysts, earnings expectations, management guidance
  5. **EARNINGS REVISIONS** - Consensus [Under/Over]estimates [Key Theme] Momentum: Analyst expectations, revision trends, surprise potential
- **Format**: Each analysis-item has `item-title` with **bold title** and `content-item` with 200-300 word analysis

**SLIDES 3-7 REQUIREMENTS:**

**SLIDE 3 - COMPANY ANALYSIS (3 FLEXIBLE SECTIONS):**
- **H3 Title**: Create compelling title specific to {company_name}'s unique investment proposition as of {datetime.now().strftime("%B %Y")}

**TITLE CONSTRUCTION FORMULA**: "3. {company_name}: [CORE INVESTMENT THEME] AMID [CURRENT MARKET/INDUSTRY CONTEXT]"

**TITLE CONSTRUCTION PRINCIPLES:**
- **Company Name**: Always start with {company_name}
- **Investment Theme**: Capture the 2-3 word core thesis (what drives value creation)
- **Current Context**: Reference the current environment this company operates in
- **Specificity**: Avoid generic terms - be specific to this company's situation

**FLEXIBLE TITLE STRUCTURE TEMPLATES:**
- "3. {company_name}: [BUSINESS TRANSFORMATION] AMID [MARKET CONDITIONS]"
- "3. {company_name}: [COMPETITIVE ADVANTAGE] & [GROWTH DRIVER] AMID [INDUSTRY DYNAMICS]"  
- "3. {company_name}: [STRATEGIC POSITIONING] AMID [ECONOMIC/REGULATORY ENVIRONMENT]"

**TITLE PRINCIPLES:**
- Include {company_name} at the beginning
- Capture the PRIMARY investment thesis in 3-6 words
- Reference current industry/macro environment context
- Make it immediately clear what drives this company's value creation as of {datetime.now().strftime("%B %Y")}

**🎯 HEDGE FUND ANALYST TO PM ANALYSIS - ULTRA-HIGH DENSITY:**
Generate EXACTLY 3 sections tailored to this specific company's fundamental drivers. Each section should provide differentiated insights that an experienced PM needs to make portfolio allocation decisions.

**MULTI-DIMENSIONAL ANALYSIS FRAMEWORK:**
Choose the 3 most critical analytical areas for THIS specific company, incorporating competitive intelligence and differentiated positioning. Consider multiple analytical dimensions:

**CORE ANALYTICAL DIMENSIONS (Select 3 Most Critical):**
- **Competitive Positioning Evolution**: How has {company_name}'s competitive position shifted vs key rivals? What are competitors doing that impacts {company_name}?
- **Business Model Differentiation**: What unique economic drivers separate {company_name} from competitors? How sustainable are these advantages?
- **Market Share Dynamics**: Where is {company_name} gaining/losing ground? What competitive moves are reshaping market structure?
- **Operational Excellence vs Peers**: How do {company_name}'s operational metrics compare to best-in-class competitors?
- **Strategic Response Analysis**: How is {company_name} responding to competitive threats? What strategic initiatives differentiate from peer approaches?
- **Technology/Innovation Gap**: Where does {company_name} lead or lag technologically vs competitors? What are the investment implications?
- **Financial Performance Divergence**: Why do {company_name}'s financial metrics differ from peers? What explains relative valuation gaps?
- **Management Execution vs Peers**: How does {company_name}'s management track record compare to competitive alternatives?

**COMPETITIVE INTELLIGENCE REQUIREMENTS:**
- **Peer Performance Analysis**: Compare {company_name} to 3-5 closest competitors with specific metrics
- **Strategic Moves Tracking**: Reference recent competitor actions and their impact on {company_name}
- **Market Position Shifts**: Quantify how competitive landscape changes affect {company_name}'s prospects
- **Differentiated Investment Case**: Explain why {company_name} is better/worse positioned than alternatives

**SECTION CONSTRUCTION REQUIREMENTS:**

**SECTION TITLES - MUST BE COMPANY-SPECIFIC & INSIGHTFUL:**
Each of the 3 sections must have H4 titles that immediately convey the analytical insight for {company_name} as of {datetime.now().strftime("%B %Y")}

**SECTION TITLE FORMULA**: "[SPECIFIC BUSINESS DRIVER] + [QUANTIFIED IMPACT] + [TIMELINE/DIRECTION]"

**SECTION TITLE CONSTRUCTION PRINCIPLES:**
- **Business-Specific**: Focus on the actual drivers unique to this company's business model
- **Quantified Impact**: Include specific numbers, percentages, or financial metrics
- **Time-Bound**: Provide timeline for when the impact will be realized
- **Directional**: Make clear if this is positive, negative, or mixed for the investment case

**TITLE STRUCTURE EXAMPLES (ADAPT TO ANY COMPANY/INDUSTRY):**
- "[BUSINESS CHANGE]: [X% FINANCIAL IMPACT] OVER [TIMEFRAME] FROM [ROOT CAUSE]"
- "[STRATEGIC INITIATIVE]: [QUANTIFIED BENEFIT] DRIVING [SPECIFIC OUTCOME] BY [DATE]"
- "[MARKET DYNAMIC]: [MEASURED EFFECT] ON [KEY METRIC] THROUGH [PERIOD]"

**ANALYTICAL REQUIREMENTS:**
- **Competitive Context Integration**: Each section must compare {company_name} to 2-3 specific competitors with quantified metrics
- **Historical Evolution Analysis**: Reference 3-5 year performance trends for both {company_name} and key competitors
- **Fundamental Drivers Analysis**: Connect {company_name}'s business drivers to financial metrics, explaining divergence from peer performance
- **Competitive Intelligence**: Reference specific competitor actions, strategies, or announcements that impact {company_name}
- **Differentiated Investment Thesis**: Explain why {company_name} is positioned better/worse than alternatives with specific evidence
- **Forward-Looking Competitive Dynamics**: Predict how competitive landscape will evolve and impact {company_name} over 12-24 months
- **Quantified Comparative Analysis**: Include 8-12 specific metrics showing {company_name} vs peer performance per section
- **PM-Level Competitive Sophistication**: Focus on non-obvious competitive advantages/disadvantages and second-order market effects

**ULTRA-HIGH INFORMATION DENSITY STANDARDS:**
- Each section: 600-800 words with MINIMUM 15 quantified data points
- Every paragraph must contain 3-4 specific metrics, dates, or comparative benchmarks
- **Competitive Data Density**: Include 5-8 peer comparison metrics per section
- **Historical Benchmarking**: Reference 3-5 specific competitor moves/events with quantified impacts
- **Forward-Looking Competitive Intelligence**: Predict competitor responses with probability assessments
- **Multi-Dimensional Comparison**: Compare across financial performance, operational metrics, strategic positioning, and market share
- Connect micro-level company dynamics to macro industry/economic trends and competitive landscape shifts

**COMPETITIVE ANALYSIS DEPTH REQUIREMENTS:**
- **Peer Identification**: Name 2-3 specific closest competitors in each section
- **Quantified Positioning**: Show exact metrics where {company_name} leads/lags (market share %, margins, growth rates, etc.)
- **Strategic Differentiation**: Explain specific strategic choices that differentiate {company_name} from each major competitor
- **Competitive Response Prediction**: Forecast how competitors will react to {company_name}'s moves and vice versa

**SLIDE 4 - CATALYSTS & DEVELOPMENTS (3 FLEXIBLE SECTIONS):**
- **H3 Title**: Create compelling title specific to {company_name}'s most important catalysts as of {datetime.now().strftime("%B %Y")}

**TITLE CONSTRUCTION FORMULA**: "4. {company_name}: [PRIMARY CATALYST THEME] & [SECONDARY DRIVER] CATALYSTS"

**FLEXIBLE TITLE STRUCTURE TEMPLATES:**
- "4. {company_name}: [STRATEGIC INITIATIVE] & [MARKET OPPORTUNITY] CATALYSTS"
- "4. {company_name}: [PRODUCT CYCLE] & [COMPETITIVE ADVANTAGE] CATALYSTS"  
- "4. {company_name}: [OPERATIONAL TRANSFORMATION] & [FINANCIAL INFLECTION] CATALYSTS"

**🎯 CATALYST SELECTION FRAMEWORK:**
Generate EXACTLY 3 catalyst sections tailored to {company_name}'s most critical value drivers. Choose from multiple catalyst dimensions based on what's most relevant:

**CATALYST DIMENSIONS (Select 3 Most Critical):**
- **Product/Innovation Catalysts**: New launches, R&D breakthroughs, technology advantages
- **Strategic/Operational Catalysts**: Management initiatives, operational improvements, strategic pivots
- **Market/Competitive Catalysts**: Market share gains, competitive positioning shifts, industry disruption
- **Financial/Capital Allocation Catalysts**: Margin expansion, capital efficiency, dividend/buyback programs
- **Regulatory/Policy Catalysts**: Regulatory approvals, policy changes, compliance advantages
- **Geographic/Market Expansion Catalysts**: New market entry, geographic expansion, customer acquisition
- **Cyclical/Economic Catalysts**: Economic recovery, commodity cycles, interest rate sensitivity
- **ESG/Sustainability Catalysts**: ESG improvements, sustainability initiatives, carbon transition

**COMPETITIVE CATALYST INTELLIGENCE:**
- **Catalyst Timing vs Peers**: How do {company_name}'s catalysts compare to competitor timelines?
- **Competitive Response Analysis**: How will competitors react to {company_name}'s catalyst execution?
- **First-Mover Advantages**: Where does {company_name} have timing advantages vs peers?
- **Catalyst Risk Assessment**: What could derail catalyst execution and how does this compare to peer risks?

**SECTION CONSTRUCTION REQUIREMENTS:**
- **Catalyst-Specific Titles**: Each section must have H4 title that specifies the exact catalyst with quantified impact and timeline
- **Competitive Context**: Compare catalyst strength/timing to 2-3 key competitors
- **Historical Context**: Reference past catalyst execution by {company_name} and lessons learned
- **Quantified Impact Analysis**: Include specific financial/operational impact predictions with timelines
- **Probability Assessment**: Assign execution probability and timeline confidence levels
- **Market Recognition Analysis**: Predict when and how market will recognize catalyst value

**ULTRA-HIGH CATALYST DENSITY STANDARDS:**
- Each section: 600-700 words with MINIMUM 12 quantified catalyst metrics
- **Competitive Benchmarking**: Include 4-6 peer catalyst comparisons per section
- **Timeline Specificity**: Provide exact dates, quarters, or timeframes for catalyst realization
- **Impact Quantification**: Include specific revenue, margin, or earnings impact predictions
- **Catalyst Chain Analysis**: Show how catalysts connect and compound over time

**SLIDE 5 - BUSINESS MODEL ANALYSIS (3 FLEXIBLE SECTIONS):**
- **H3 Title**: Create compelling title specific to {company_name}'s unique business model strengths as of {datetime.now().strftime("%B %Y")}

**TITLE CONSTRUCTION FORMULA**: "5. {company_name}: [CORE BUSINESS MODEL ADVANTAGE] & [DIFFERENTIATED VALUE CREATION]"

**FLEXIBLE TITLE STRUCTURE TEMPLATES:**
- "5. {company_name}: [ECONOMIC MOAT] & [SCALABILITY ADVANTAGE] ANALYSIS"
- "5. {company_name}: [OPERATIONAL EXCELLENCE] & [FINANCIAL EFFICIENCY] DRIVERS"
- "5. {company_name}: [STRATEGIC POSITIONING] & [VALUE CREATION] MECHANISMS"

**🎯 BUSINESS MODEL ANALYSIS FRAMEWORK:**
Generate EXACTLY 3 sections tailored to {company_name}'s most critical business model drivers. Choose the most relevant analytical areas based on what creates sustainable competitive advantage:

**BUSINESS MODEL DIMENSIONS (Select 3 Most Critical):**
- **Economic Moat Analysis**: Network effects, switching costs, scale advantages, regulatory barriers
- **Revenue Model Optimization**: Recurring vs transactional, pricing power, customer lifetime value
- **Operational Leverage Dynamics**: Fixed cost absorption, margin expansion potential, scalability factors
- **Capital Efficiency Metrics**: Asset turnover, working capital management, capital allocation effectiveness
- **Technology/Innovation Moats**: R&D productivity, patent protection, technological differentiation
- **Customer/Market Positioning**: Brand strength, customer loyalty, market positioning power
- **Supply Chain/Distribution Advantages**: Vertical integration, supplier relationships, distribution control
- **Management Execution Excellence**: Strategic vision, operational execution, capital allocation track record

**COMPETITIVE BUSINESS MODEL INTELLIGENCE:**
- **Business Model Comparison**: How does {company_name}'s model differ from 2-3 key competitors?
- **Sustainability Analysis**: Which competitive advantages are most defensible long-term?
- **Evolution Tracking**: How has {company_name}'s business model evolved vs peers over 3-5 years?
- **Disruption Vulnerability**: Where is the business model most/least vulnerable to disruption?

**SECTION CONSTRUCTION REQUIREMENTS:**
- **Business-Specific Titles**: Each section must have H4 title that captures the specific business model insight with quantified advantage
- **Competitive Differentiation**: Explain exactly how {company_name}'s approach differs from competitors with specific evidence
- **Historical Performance**: Reference 3-5 year track record demonstrating business model strength
- **Quantified Advantages**: Include specific metrics showing business model superiority (margins, returns, growth rates)
- **Future Evolution**: Predict how business model will adapt/strengthen over 12-24 months
- **Valuation Implications**: Connect business model strengths to justified valuation premium/discount

**ULTRA-HIGH BUSINESS MODEL DENSITY STANDARDS:**
- Each section: 700-800 words with MINIMUM 15 quantified business metrics
- **Competitive Benchmarking**: Include 5-7 peer business model comparisons per section
- **Historical Trend Analysis**: Show 3-5 year evolution of key business model metrics
- **Economic Value Quantification**: Include specific ROI, ROIC, or value creation measurements
- **Predictive Analysis**: Forecast business model performance with probability assessments

**SLIDE 6 - SECTOR INSIGHT (FLEXIBLE MARKET-SPECIFIC ANALYSIS):**
- **H3 Title**: Create contrarian sector insight specific to {company_name}'s industry situation as of {datetime.now().strftime("%B %Y")} (e.g., "6. SEMICONDUCTOR AI GOLD RUSH: NVIDIA CAPTURES 80% OF $400B INFRASTRUCTURE BUILD", "6. CLOUD WARS ENDGAME: ENTERPRISE AI MIGRATION CREATING WINNER-TAKE-ALL")
- **FLEXIBLE SECTOR APPROACH - TAILOR TO INDUSTRY'S CURRENT DYNAMICS:**
  - **IDENTIFY 2-3 MOST CRITICAL SECTOR THEMES** that directly impact {company_name}'s investment case
  - **NO FIXED SECTIONS** - Choose based on sector situation: Market Transformation, Regulatory Disruption, Technology Cycle, Competitive Consolidation, Supply Chain Shifts, ESG Requirements, Geopolitical Impact, Capital Cycle, etc.
  - **EXAMPLES OF SECTOR-SPECIFIC THEMES:**
    - **SEMICONDUCTORS**: "AI Infrastructure Capex Supercycle", "Geopolitical Supply Chain Reshoring", "Advanced Node Oligopoly Formation"
    - **CLOUD SOFTWARE**: "Enterprise AI Adoption Acceleration", "Hyperscaler Infrastructure Spending", "SaaS Margin Expansion Cycle"
    - **AUTOMOTIVE**: "EV Transition Inflection Point", "Autonomous Driving Technology Race", "Battery Supply Chain Consolidation"
    - **ENERGY**: "Renewable Energy Scaling Economics", "Grid Modernization Investment", "Carbon Pricing Policy Impact"
- **CRITICAL SECTOR ALPHA PRINCIPLES**:
  - Focus on sector trends that SPECIFICALLY benefit {company_name} vs peers
  - Identify what market MISUNDERSTANDS about industry dynamics
  - Use GOOGLE-VERIFIED current industry data and forward projections
  - Connect sector trends to {company_name}'s SPECIFIC earnings/margin/multiple catalysts
  - Show why sector dynamics create 12-24 month outperformance opportunity for {company_name}
- **Format**: Each section starts with sector-insight H4 title and 800-900 words proving how sector dynamics specifically benefit {company_name}

**SLIDE 7 - COMPETITIVE ADVANTAGE (FLEXIBLE MOAT-SPECIFIC ANALYSIS):**
- **H3 Title**: Create quantified competitive advantage thesis specific to {company_name}'s moat (e.g., "7. NVIDIA'S AI SOFTWARE ECOSYSTEM: $50B CUDA MOAT WITH 95% DEVELOPER MIND SHARE", "7. TESLA'S MANUFACTURING MACHINE: 50% COST ADVANTAGE ENABLING $25K MODEL")
- **FLEXIBLE COMPETITIVE APPROACH - TAILOR TO COMPANY'S SPECIFIC MOATS:**
  - **IDENTIFY 2-3 STRONGEST COMPETITIVE ADVANTAGES** that create sustainable alpha generation
  - **NO MANDATORY SECTIONS** - Choose from: Technology Leadership, Scale Economics, Network Effects, Brand Premium, Switching Costs, Regulatory Barriers, Geographic Advantages, Vertical Integration, IP Portfolio, Management Execution, Capital Access, etc.
  - **EXAMPLES OF COMPANY-SPECIFIC MOATS:**
    - **APPLE**: "Ecosystem Lock-In Economics", "Premium Brand Pricing Power", "Vertical Silicon Integration"
    - **AMAZON**: "Logistics Network Scale", "AWS Infrastructure Moat", "Prime Membership Flywheel"
    - **MICROSOFT**: "Enterprise Software Stickiness", "Cloud Platform Network Effects", "Developer Ecosystem Lock-In"
    - **GOOGLE**: "Search Data Advantage", "Android Platform Control", "AI/ML Technical Leadership"
- **CRITICAL COMPETITIVE ALPHA PRINCIPLES**:
  - QUANTIFY each competitive advantage with specific financial metrics
  - Prove advantage is EXPANDING not contracting vs historical periods
  - Show why competitors CANNOT replicate advantage in next 2-3 years for {company_name}
  - Connect moat strength to SPECIFIC pricing power, market share, margin expansion opportunities
  - Use GOOGLE-VERIFIED competitive intelligence and benchmark data
- **Format**: Each section starts with quantified-moat H4 title and 800-900 words proving sustainable competitive advantage with expansion trajectory

**CRITICAL TITLE GENERATION PRINCIPLES:**
- **NO GENERIC PLACEHOLDERS**: Never use "[COMPANY] INVESTMENT HIGHLIGHTS" - always create specific, insightful titles
- **CAPTURE THE INSIGHT**: Titles must immediately convey the unique investment thesis as of {datetime.now().strftime("%B %Y")} (e.g., "TESLA'S VERTICAL INTEGRATION: BATTERY-TO-SOFTWARE DOMINANCE")
- **USE QUANTIFICATION**: Include specific metrics when impactful (e.g., "APPLE'S $200B+ SERVICES TRANSFORMATION")
- **COMPELLING & SPECIFIC**: Make readers want to read more - show WHY this matters specifically for {company_name}
- **INDUSTRY-SPECIFIC**: Tailor to {company_name}'s sector and unique competitive position
- **ACTION-ORIENTED**: Convey what {company_name} is DOING that creates value (expansion, transformation, dominance, etc.)

**CRITICAL FORMATTING:**
- Use `report-prose` class with numbered headers (3., 4., 5., 6., 7.)
- Each slide must be complete with all subsections
- 500-600 word paragraphs with institutional sophistication
- Specific metrics and quantitative support throughout

### ELITE PM ANALYTICAL APPROACH FOR CALL 1:

**PROPRIETARY INSIGHT GENERATION (What Others Miss):**
- **Hidden Inflection Points**: Identify business model changes, competitive shifts, or technology adoptions occurring beneath surface that will drive 12-18 month performance starting from {datetime.now().strftime("%B %Y")}
- **Management Behavior Decoding**: Analyze subtle changes in capital allocation, strategic messaging, or operational focus that signal future direction before consensus recognizes
- **Competitive Intelligence Advantage**: Understand market share dynamics, pricing power evolution, and competitive response functions that aren't captured in public data
- **Second-Order Technology Effects**: Predict how emerging technologies will create/destroy value in ways that aren't immediately obvious

**NON-CONSENSUS POSITIONING FRAMEWORKS:**
- **Consensus Deconstruction as of {datetime.now().strftime("%B %Y")}**: Systematically identify why current analyst estimates, valuation metrics, or market sentiment are systematically wrong
- **Complexity Arbitrage**: Exploit situations where business model complexity, accounting complexity, or industry evolution create analytical barriers for consensus
- **Time Horizon Arbitrage**: Identify long-term value creation stories temporarily obscured by short-term noise or cyclical headwinds
- **Behavioral Finance Exploitation**: Leverage recency bias, anchoring effects, or sector rotation patterns that create temporary mispricings

**⚡ PREDICTIVE ANALYTICS MASTERY:**
- **Leading Indicator Development**: Identify forward-looking metrics (KPIs, competitive data, technology adoption) that predict earnings inflection points 2-3 quarters ahead
- **Pattern Recognition Application**: Apply historical parallels from similar companies, industries, or market cycles to predict likely future trajectories
- **Catalyst Probability Weighting**: Assess likelihood and timing of specific catalysts using base rates, management track records, and industry precedents
- **Inflection Point Timing**: Predict when current trends will accelerate, plateau, or reverse based on fundamental analysis

** FUTURE STATE VISUALIZATION:**
- **Business Model Evolution**: Predict how {company_name}'s business model will evolve over 3-5 years starting from {datetime.now().strftime("%B %Y")} based on current strategic initiatives and industry trends
- **Competitive Positioning Forecast**: Anticipate how competitive dynamics will shift and where {company_name} will be positioned
- **Technology Disruption Assessment**: Evaluate whether emerging technologies represent threats or opportunities for long-term competitive positioning
- **Capital Allocation Optimization**: Predict how management will allocate capital and the returns on that allocation based on historical patterns and current priorities

** SOPHISTICATED THESIS ARCHITECTURE:**
- **Multi-Layer Value Creation**: Identify 3-4 {company_name} independent value drivers operating on different time horizons that compound to create asymmetric returns
- **Option Value Recognition**: Quantify hidden optionality in business model flexibility, strategic assets, or expansion opportunities
- **Moat Evolution Analysis**: Predict how competitive advantages will strengthen/weaken over time and what management is doing to reinforce them
- **Quality of Growth Assessment**: Distinguish between revenue growth and profitable, sustainable, capital-efficient growth that creates long-term value

{user_context}

{financial_context}

{analyst_insights}

**STOCK PRICE DATA FOR CHART CREATION and the analysis of the stock price and its fundementals:**
{str(complete_stock_data)}

**ULTRA-SOPHISTICATED EXECUTION MANDATE as of {datetime.now().strftime("%B %Y")}**: 
Create ALL 7 slides that demonstrate **differentiated insights, non-consensus positioning, and second-order thinking** that generates sustainable alpha. Each slide must answer: **\"What do I know about {company_name}'s future that the market doesn't yet understand?\"**

**CRITICAL ANALYTICAL REQUIREMENTS:**
- **EXPLICIT DATE CONTEXT**: All analysis must explicitly reference current date {datetime.now().strftime("%B %Y")} to ensure updated information
- **MANDATORY GOOGLE SEARCH GROUNDING**: ALL information must be grounded with Google Search tool - no generic statements allowed
- **DIFFERENTIATED VIEW MANDATE**: Show what previous fundamentals reveal about stock price implications and future implications based on recent company strategy and themes
- **FORWARD-LOOKING FOCUS**: Provide concrete, precise analysis that demonstrates deep company understanding and insight into how strategy affects stock price and future performance
- **PM CONVICTION STANDARD**: Write concise, precise analysis that convinces PM you are different, have your own view, know company very well, and understand how company strategy will affect stock price and future - NO bullshit, be concrete and precise

**ADVANCED WRITING TECHNIQUES FOR MAXIMUM PM IMPACT:**
- **QUANTIFIED SPECIFICITY**: Use exact numbers, not ranges. "23.4% margin expansion" not "strong margins"
- **HISTORICAL PATTERN RECOGNITION**: Reference specific past events. "Similar to 2019 automation rollout that drove 400bps margin gains"
- **MANAGEMENT BEHAVIOR DECODING**: Read between lines. "CFO's emphasis on 'capital discipline' signals dividend increase vs buybacks"
- **SECOND-ORDER IMPLICATIONS**: Show cascade effects. "Pricing power in segment A enables cross-subsidization of segment B expansion"
- **COMPETITIVE INTELLIGENCE**: Demonstrate market knowledge. "While peers struggle with supply chain, {company_name}'s vertical integration provides 18-month cost advantage"
- **UNIT ECONOMICS MASTERY**: Show business model understanding. "Each new customer generates $2.3K annual recurring revenue at 67% gross margin"
- **CATALYST SEQUENCING**: Predict event timing. "Q1 earnings will show margin inflection, followed by guidance raise in Q2, driving re-rating by Q3"
- **CONTRARIAN EVIDENCE ACKNOWLEDGMENT**: Address bear case. "Despite cyclical headwinds, structural demand shift to premium segment sustains pricing"
- **INSIDER-LEVEL INSIGHTS**: Write like you know the company intimately. "Management's R&D reallocation toward AI indicates 2026 product cycle acceleration"
- **PROBABILISTIC THINKING**: Assign outcome probabilities. "75% chance of beating guidance by 5%+ given leading indicator trends"

**MAXIMUM INFORMATION DENSITY REQUIREMENTS:**
- **SYNTHESIS MASTERY**: Connect 3+ data points per insight. "Capex +40%, R&D +25%, and patent filings +60% signal product cycle acceleration beginning Q3 2025"
- **LAYERED ANALYSIS**: Multiple analytical lenses per paragraph. "Margin expansion (financial), market share gains (competitive), and customer satisfaction scores (operational) all confirm pricing power sustainability"
- **FORWARD-LOOKING SYNTHESIS**: Predict specific outcomes. "Current inventory build (+23% QoQ) + supplier contract renegotiations + automation phase 2 completion = 35% gross margin by Q2 2025"
- **BENCHMARKING SOPHISTICATION**: Multi-dimensional comparisons. "Trading at 0.8x vs historical 1.2x multiple, 0.7x vs peer average, but 1.1x vs growth-adjusted fair value"
- **RESOURCE ALLOCATION INTELLIGENCE**: Capital efficiency insights. "$500M capex generates $2.1B revenue capacity at 28% incremental margins = 84% IRR vs 15% cost of capital"
- **COMPRESSED INSIGHT DELIVERY**: Maximum insights per sentence. "Q3 beat (+8% vs consensus) driven by pricing (+5%), volume (+2%), and mix (+1%) validates our 3-factor expansion thesis"

**NON-CONSENSUS INSIGHT REQUIREMENTS:**
- **Slide 1**: Identify the primary market mispricing and why consensus is systematically wrong as of {datetime.now().strftime("%B %Y")}
- **Slide 2**: Highlight 5 specific insights that demonstrate superior analytical depth vs. sell-side research
- **Slide 3**: Reveal competitive advantages or market opportunities that others miss or underestimate
- **Slide 4**: Predict specific catalysts and their timing that consensus hasn't properly analyzed
- **Slide 5**: Demonstrate understanding of business model evolution that exceeds public company guidance
- **Slide 6**: Identify industry dynamics and second-order effects that create hidden value
- **Slide 7**: Quantify sustainable competitive advantages that others treat as commoditized as of {datetime.now().strftime("%B %Y")}

**🎯 MANDATORY KEY TAKEAWAYS SECTION (SLIDES 3-7 ONLY):**
Starting from Slide 3, each slide MUST end with a "Key Takeaways" section containing 2-5 bullet points (flexible based on content richness) that capture the most important insights from that specific slide's analysis.

**Key Takeaways Format:**
```html
<div class="key-takeaways-section">
    <h4 class="takeaways-header">Key Investment Takeaways</h4>
    <ul class="takeaways-list">
        <li class="takeaway-item">[Extract most critical insight from your analysis - company-specific with quantified data]</li>
        <li class="takeaway-item">[Second most important conclusion from your detailed analysis above]</li>
        <!-- Add more bullets ONLY if your analysis contains additional significant insights -->
    </ul>
</div>
```

**FLEXIBLE CONTENT-DRIVEN TAKEAWAY RULES:**
- **Content-Determined Quantity**: Generate 2-5 bullets based on how many significant insights your slide analysis actually contains
- **Quality over Quantity**: Better to have 2 powerful insights than 5 weak ones
- **Slide-Specific Focus**: Takeaways should only reflect what you analyzed in THIS specific slide
- **No Padding**: Don't add generic bullets just to reach a number
- **Analysis-Extraction**: Each bullet must summarize a specific conclusion from your detailed content above

**Bullet Point Requirements:**
- Each bullet point: 15-25 words maximum
- Must be analytical and quantified (include specific numbers/percentages where possible)
- NO GENERIC STATEMENTS: Avoid phrases like "strong fundamentals" or "competitive advantages"
- COMPANY-SPECIFIC ONLY: Must reference actual company name, specific business metrics, real financial data
- CONTENT-DERIVED: Extract insights directly from the detailed analysis you just wrote
- DIFFERENTIATED VIEW: Show how your analysis differs from consensus with specific evidence

**CRITICAL: ORGANIC CONTENT-BASED TAKEAWAYS**
- **Slide 3 might have**: 2 bullets (if focused on one major competitive advantage) or 4 bullets (if analyzing multiple strategic strengths)
- **Slide 8 might have**: 3 bullets (if income statement reveals key insights) or 2 bullets (if analysis is straightforward)
- **Quality First**: A slide with 2 powerful, specific insights is better than 5 generic statements
- **Content Determines Count**: Let your actual analysis drive the number of takeaways, not a fixed template
- **Industry-Specific**: Apple takeaways will be completely different from REIT or Tesla takeaways based on business fundamentals

**DIFFERENTIATION STANDARDS:**
- Every insight must be **differentiated** - something that institutional investors paying $50K+ annually would find valuable
- Demonstrate **pattern recognition** from historical analysis that others haven't applied
- Show **predictive analytics** that forecast inflection points 12-18 months ahead
- Reveal **complexity arbitrage** opportunities where business model sophistication creates analytical barriers

**MANDATORY SLIDE COMPLETION REQUIREMENTS:**
- MUST generate EXACTLY 7 slides: slides 1, 2, 3, 4, 5, 6, AND 7
- SLIDE 6 MUST be complete with full industry analysis content
- SLIDE 7 MUST be complete with full competitive advantage analysis  
- Each slide MUST have complete content - NO truncation allowed
- Final slide MUST end with "Page 7 / 15" footer

**CRITICAL OUTPUT FORMAT REQUIREMENTS:**
- Output PURE HTML ONLY - NO markdown code blocks, NO **bold** markdown
- NO ```html tags, NO explanatory text, NO comments
- ALL emphasis must use <strong>text</strong> HTML tags, NEVER **text** markdown
- Start directly with <div class="slide" id="portrait-page-1">
- End with slide 7's closing </div> tag (Page 7 / 15)
- Use exact CSS classes and structure shown in examples above
- GENERATE ALL 7 SLIDES COMPLETELY - DO NOT STOP EARLY

**⚠️ CRITICAL: FOLLOW EXACT HTML STRUCTURE - NO DEVIATIONS ALLOWED:**
- MUST use `<header class="report-header-container">` with `<div class="slide-logo">` inside
- MUST use `<section class="metrics-grid">` with simple `<div class="metrics-item">` structure 
- MUST use exact same header structure for ALL slides 1-7
- ⚠️ **MANDATORY**: COPY the metrics grid HTML EXACTLY as shown - DO NOT generate your own metrics
- ⚠️ **DO NOT REPLACE** placeholders like __MARKET_CAP__ - these will be automatically replaced with real data
- DO NOT create custom layouts or change the structure - follow template EXACTLY

**CONCISE & PRECISE WRITING REQUIREMENTS:**
- Each analysis section: MAX 150-200 words (not 300+ words)
- Each subsection paragraph: MAX 400-500 words (not 600+ words)
- Use <strong>key metrics</strong> and <strong>critical insights</strong> for emphasis
- Be punchy, direct, and impactful - eliminate unnecessary words
- Every sentence must add specific value or data points
"""
        
        # Use metrics from comprehensive system (or extract as fallback)
        if complete_stock_data.get('metrics_ready'):
            # PRIMARY: Use pre-calculated metrics - map to template placeholders
            metrics = complete_stock_data.get('metrics', {})
            metrics_data = {
                'ticker_exchange': f"{ticker}",
                'current_price': metrics.get('SHARE_PRICE', 'N/A'),
                'market_cap': metrics.get('MARKET_CAP', 'N/A'),
                'enterprise_value': metrics.get('ENTERPRISE_VALUE', 'N/A'),
                'week_52_range': metrics.get('52W_RANGE', 'N/A'),
                'pe_ratio': metrics.get('PE_RATIO', 'N/A'),
                'ev_ebitda': metrics.get('EV_EBITDA', 'N/A'),
                'ps_ratio': metrics.get('PS_RATIO', 'N/A'),
                'pb_ratio': metrics.get('PB_RATIO', 'N/A'),
                'peg_ratio': metrics.get('PEG_RATIO', 'N/A'),
                'margins': metrics.get('MARGINS', 'N/A'),
                'roe': metrics.get('ROE', 'N/A'),
                'roa': metrics.get('ROA', 'N/A'),
                'ebitda_margin': metrics.get('EBITDA_MARGIN', 'N/A'),
                'target_range': metrics.get('TARGET_RANGE', 'N/A'),
                'revenue_growth': metrics.get('REV_GROWTH', 'N/A'),
                'eps_growth': metrics.get('EPS_GROWTH', 'N/A'),
                'beta': metrics.get('BETA', 'N/A'),
                'debt_equity': metrics.get('DEBT_EQUITY', 'N/A'),
                'current_ratio': metrics.get('CURRENT_RATIO', 'N/A'),
                'free_cashflow': metrics.get('FCF', 'N/A'),
                'quick_ratio': metrics.get('QUICK_RATIO', 'N/A'),
                'dividend_yield': metrics.get('DIV_YIELD', 'N/A'),
                'payout_ratio': metrics.get('PAYOUT_RATIO', 'N/A'),
                'volume': metrics.get('VOLUME', 'N/A')
            }
            logger.info(f"✅ Using pre-calculated metrics: {len(metrics_data)} variables")
        else:
            # FALLBACK: Extract metrics using legacy method
            try:
                metrics_data = self._extract_metrics_data_for_template(ticker, financial_data)
                logger.info(f"⚠️ FALLBACK: Extracted metrics data: {len(metrics_data)} variables")
            except Exception as e:
                logger.warning(f"⚠️ Could not extract metrics data: {e}")
                metrics_data = {}
        
        # Stock price data is now provided directly in the prompt for AI to create simple chart
        
        # Replace metrics variables with actual data in the prompt
        call1_specific_with_metrics = call1_specific
        
        # Combine base prompt with Call 1 specifics (chart data already included)
        complete_call1_prompt = base_prompt + call1_specific_with_metrics
        
        # FIRST: Replace __METRICS_PLACEHOLDERS__ with actual values (do this before any formatting)
        replacements = {
            '__TICKER_EXCHANGE__': metrics_data.get('ticker_exchange', 'N/A'),
            '__CURRENT_PRICE__': metrics_data.get('current_price', 'N/A'),
            '__MARKET_CAP__': metrics_data.get('market_cap', 'N/A'),
            '__ENTERPRISE_VALUE__': metrics_data.get('enterprise_value', 'N/A'),
            '__WEEK_52_RANGE__': metrics_data.get('week_52_range', 'N/A'),
            '__PE_RATIO__': metrics_data.get('pe_ratio', 'N/A'),
            '__EV_EBITDA__': metrics_data.get('ev_ebitda', 'N/A'),
            '__PS_RATIO__': metrics_data.get('ps_ratio', 'N/A'),
            '__PB_RATIO__': metrics_data.get('pb_ratio', 'N/A'),
            '__PEG_RATIO__': metrics_data.get('peg_ratio', 'N/A'),
            '__MARGINS__': metrics_data.get('margins', 'N/A'),
            '__ROE__': metrics_data.get('roe', 'N/A'),
            '__ROA__': metrics_data.get('roa', 'N/A'),
            '__EBITDA_MARGIN__': metrics_data.get('ebitda_margin', 'N/A'),
            '__TARGET_RANGE__': metrics_data.get('target_range', 'N/A'),
            '__REVENUE_GROWTH__': metrics_data.get('revenue_growth', 'N/A'),
            '__EPS_GROWTH__': metrics_data.get('eps_growth', 'N/A'),
            '__BETA__': metrics_data.get('beta', 'N/A'),
            '__DEBT_EQUITY__': metrics_data.get('debt_equity', 'N/A'),
            '__CURRENT_RATIO__': metrics_data.get('current_ratio', 'N/A'),
            '__FREE_CASHFLOW__': metrics_data.get('free_cashflow', 'N/A'),
            '__QUICK_RATIO__': metrics_data.get('quick_ratio', 'N/A'),
            '__DIVIDEND_YIELD__': metrics_data.get('dividend_yield', 'N/A'),
            '__PAYOUT_RATIO__': metrics_data.get('payout_ratio', 'N/A'),
            '__VOLUME__': metrics_data.get('volume', 'N/A')
        }
        
        # Apply all metric replacements FIRST
        complete_call1_prompt_with_metrics = complete_call1_prompt
        for placeholder, value in replacements.items():
            complete_call1_prompt_with_metrics = complete_call1_prompt_with_metrics.replace(placeholder, str(value))
        
        logger.info(f"✅ Metrics placeholders replaced: {len([p for p in replacements.keys() if p not in complete_call1_prompt_with_metrics])} substituted")
        
        # THEN: Format the prompt with company name and context variables
        try:
            # Escape any problematic characters in company name for string formatting
            safe_company_name = str(company_name).replace('{', '{{').replace('}', '}}') if '{' in str(company_name) or '}' in str(company_name) else company_name
            
            logger.info(f"🔍 DEBUG: Formatting Call 1 prompt with:")
            logger.info(f"  - company_name: '{safe_company_name}'")
            logger.info(f"  - user_context: {len(user_context)} chars")
            logger.info(f"  - financial_context: {len(financial_context)} chars") 
            logger.info(f"  - analyst_insights: {len(analyst_insights)} chars")
            
            # Replace all template variables in the prompt that already has metrics replaced
            formatted_final = complete_call1_prompt_with_metrics.format(
                company_name=safe_company_name,
                user_context=user_context,
                financial_context=financial_context,
                analyst_insights=analyst_insights
            )
            
            logger.info(f"✅ Call 1 prompt built: {len(formatted_final):,} characters with real metrics and context")
            logger.info(f"🔍 DEBUG: User context in final prompt: {'user_context' not in formatted_final}")
            return formatted_final
            
        except KeyError as e:
            logger.error(f"❌ Formatting error in Call 1 prompt: {e}")
            logger.error(f"🔍 Looking for malformed placeholder: {e}")
            # Return version with metrics replaced (even if company name formatting failed)
            logger.info(f"✅ Call 1 prompt built (metrics replaced): {len(complete_call1_prompt_with_metrics):,} characters")
            return complete_call1_prompt_with_metrics

    # REMOVED: _build_real_metrics_grid() - replaced by comprehensive system
    
    def _extract_metrics_data_for_template(self, ticker: str, financial_data: Dict) -> Dict[str, str]:
        """
        Extract metrics data from yfinance and format as template variables
        """
        try:
            # Use the financial_data already fetched by the server to ensure data consistency
            if financial_data and 'info' in financial_data:
                info = financial_data['info']
                logger.info(f"📊 Using pre-fetched yfinance data for {ticker}")
            else:
                # Fallback: Import yfinance to get fresh info data  
                import yfinance as yf
                stock = yf.Ticker(ticker)
                info = stock.info
                logger.warning(f"⚠️ No pre-fetched data available, making fresh yfinance call for {ticker}")
            
            # Get current price and basic info
            current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
            currency = info.get('currency', 'USD')
            exchange = info.get('exchange', 'Unknown')
            
            # Format currency symbol
            if currency == 'SGD':
                curr_symbol = 'S$'
            elif currency == 'USD':
                curr_symbol = '$'
            elif currency == 'EUR':
                curr_symbol = '€'
            elif currency == 'GBP':
                curr_symbol = '£'
            elif currency == 'JPY':
                curr_symbol = '¥'
            else:
                curr_symbol = currency + ' '
            
            # Helper function to format large numbers
            def format_number(value, is_currency=False):
                if value is None or value == 0:
                    return "N/A"
                try:
                    value = float(value)
                    prefix = curr_symbol if is_currency else ""
                    if abs(value) >= 1e12:
                        return f"{prefix}{value/1e12:.2f}T"
                    elif abs(value) >= 1e9:
                        return f"{prefix}{value/1e9:.2f}B"
                    elif abs(value) >= 1e6:
                        return f"{prefix}{value/1e6:.1f}M"
                    elif abs(value) >= 1000:
                        return f"{prefix}{value/1000:.1f}K"
                    else:
                        return f"{prefix}{value:.2f}"
                except:
                    return "N/A"
            
            # Helper function to format percentages
            def format_percent(value, decimals=1):
                if value is None:
                    return "N/A"
                try:
                    return f"{float(value)*100:.{decimals}f}%" if value < 1 else f"{float(value):.{decimals}f}%"
                except:
                    return "N/A"
            
            # Helper function to format ratios
            def format_ratio(value, decimals=2):
                if value is None:
                    return "N/A"
                try:
                    return f"{float(value):.{decimals}f}x"
                except:
                    return "N/A"
                    
            # Helper function to format price range
            def format_range(low, high):
                if low is None or high is None:
                    return "N/A"
                try:
                    return f"{curr_symbol}{float(low):.2f} - {curr_symbol}{float(high):.2f}"
                except:
                    return "N/A"
            
            # Return structured data for template formatting
            return {
                'ticker_exchange': f"{ticker} / {exchange}",
                'current_price': f"{curr_symbol}{current_price:.3f}",
                'market_cap': format_number(info.get('marketCap'), True),
                'enterprise_value': format_number(info.get('enterpriseValue'), True),
                'week_52_range': format_range(info.get('fiftyTwoWeekLow'), info.get('fiftyTwoWeekHigh')),
                'pe_ratio': f"{format_ratio(info.get('trailingPE'))} / {format_ratio(info.get('forwardPE'))}",
                'ev_ebitda': format_ratio(info.get('enterpriseToEbitda')),
                'ps_ratio': format_ratio(info.get('priceToSalesTrailing12Months')),
                'pb_ratio': format_ratio(info.get('priceToBook')),
                'peg_ratio': format_ratio(info.get('pegRatio')),
                'margins': f"{format_percent(info.get('grossMargins'))} / {format_percent(info.get('operatingMargins'))} / {format_percent(info.get('profitMargins'))}",
                'roe': format_percent(info.get('returnOnEquity')),
                'roa': format_percent(info.get('returnOnAssets')),
                'ebitda_margin': format_percent(info.get('ebitdaMargins')),
                'target_range': format_range(info.get('targetLowPrice'), info.get('targetHighPrice')),
                'revenue_growth': format_percent(info.get('revenueGrowth')),
                'eps_growth': format_percent(info.get('earningsGrowth')),
                'beta': format_ratio(info.get('beta'), 2),
                'debt_equity': format_percent(info.get('debtToEquity')),
                'current_ratio': format_ratio(info.get('currentRatio')),
                'free_cashflow': format_number(info.get('freeCashflow'), True),
                'quick_ratio': format_ratio(info.get('quickRatio')),
                'dividend_yield': format_percent(info.get('dividendYield')),
                'payout_ratio': format_ratio(info.get('payoutRatio')),
                'volume': f"{format_number(info.get('averageVolume10days', 0)/1000000, False)}M / {format_number(info.get('averageVolume3months', 0)/1000000, False)}M"
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to extract metrics data for template: {e}")
            # Return empty variables to prevent formatting errors
            return {
                'ticker_exchange': 'N/A',
                'current_price': 'N/A',
                'market_cap': 'N/A',
                'enterprise_value': 'N/A',
                'week_52_range': 'N/A',
                'pe_ratio': 'N/A',
                'ev_ebitda': 'N/A',
                'ps_ratio': 'N/A',
                'pb_ratio': 'N/A',
                'peg_ratio': 'N/A',
                'margins': 'N/A',
                'roe': 'N/A',
                'roa': 'N/A',
                'ebitda_margin': 'N/A',
                'target_range': 'N/A',
                'revenue_growth': 'N/A',
                'eps_growth': 'N/A',
                'beta': 'N/A',
                'debt_equity': 'N/A',
                'current_ratio': 'N/A',
                'free_cashflow': 'N/A',
                'quick_ratio': 'N/A',
                'dividend_yield': 'N/A',
                'payout_ratio': 'N/A',
                'volume': 'N/A'
            }
    
    async def _build_call2_prompt(
        self,
        company_name: str,
        ticker: str,
        analyses_data: Dict[str, Any],
        financial_data: Dict = None,
        call1_context: Dict = None,
        investment_objective: str = None,
        data_sources: Dict = None
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
### CSS STYLING FOR CALL 2:

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
        
        # Get user context using helper method
        user_context = self._build_user_context(data_sources)
        
        # Get Call 1 context summary using helper method
        call1_summary = self._build_call1_context_summary(call1_context)
        
        # Build Call 2 specific requirements with precise HTML structure
        investment_focus = investment_objective or "comprehensive investment analysis"
        call2_specific = f"""
## ALPHA GENERATION PHASE 2: QUANTITATIVE VALIDATION & SOPHISTICATED VALUATION (SLIDES 8-15)

### YOUR ELITE PM MANDATE FOR CALL 2:
As an elite Portfolio Manager writing in {datetime.now().strftime("%B %Y")}, your **second phase objective** is to provide rigorous quantitative validation of the Phase 1 investment thesis through sophisticated financial analysis and multi-methodology valuation. You're applying the same analytical rigor that generates consistent alpha at the world's top hedge funds.

**INVESTMENT OBJECTIVE FOCUS**: {investment_focus} - Ensure all financial analysis and valuation work supports this specific investment objective and connects quantitative insights to this goal.

**Deploy your 25+ years of experience** in factor modeling, risk decomposition, and advanced valuation techniques. Every financial insight must demonstrate the quantitative sophistication that separates institutional research from generic analysis. **Critical**: Use the most current financial data available as of {datetime.now().strftime("%B %Y")}, including latest quarterly reports, recent market developments, and current economic conditions. **Google Search Grounding**: Use Google Search extensively to verify all financial statements data, recent earnings results, analyst estimates, competitor performance, and industry benchmarks mentioned in your analysis.

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
<!-- 🚨 ADVANCED ANALYTICAL REQUIREMENTS for Slides 8-15 as of {datetime.now().strftime("%B %Y")}:

1. FINANCIAL DEEP DIVE: Show mastery of financial statement analysis with forward-looking insights
2. VALUATION SOPHISTICATION: Demonstrate multiple valuation methodologies with probability weightings  
3. SCENARIO ANALYSIS: Present bull/base/bear cases with specific assumptions and outcomes
4. RISK ASSESSMENT: Identify second-order risks that consensus misses
5. RATING CONSISTENCY: Use IDENTICAL rating from Call 1 across ALL slides
6. GOOGLE SEARCH MANDATE: Every financial metric, competitive comparison, and market assumption must be Google Search verified

WRITING STANDARDS:
- Avoid generic statements like "strong fundamentals" - be specific: "25.3% ROIC vs 18% sector average"
- Connect strategy to numbers: "AI investment of $2B drives 400bps margin expansion by 2026"
- Show differentiated insights: "Unlike consensus focus on top-line, we see margin inflection as key catalyst"
- Quantify everything: "40% probability of $100 target vs 30% probability of $85 downside scenario"

CRITICAL: BOLD FORMATTING FOR IMPORTANT ANALYSIS:
- **USE <strong></strong> tags** for all KEY FINANCIAL INSIGHTS, IMPORTANT METRICS, and CRITICAL VALUATION POINTS
- **Bold all specific numbers**: <strong>25.3% ROIC</strong>, <strong>$2B revenue</strong>, <strong>400bps margin expansion</strong>
- **Bold financial conclusions**: <strong>Free cash flow generation supports...</strong>
- **Bold valuation metrics**: <strong>Trading at 15.2x NTM EV/EBITDA</strong>, <strong>20% FCF yield</strong>
- **Bold competitive positioning**: <strong>Market-leading margins of 35%</strong>
- **Bold investment thesis**: <strong>Undervalued at current multiples</strong>
- **Bold risk factors**: <strong>Key downside risk is...</strong>

HEADER INSTRUCTIONS:
- Always use the exact Robeco logo URL: https://images.ctfassets.net/tl4x668xzide/7mygwms2vuSwirnfvaCSvL/72d2bbd858a69aecbf59fd3fb8954484/robeco-logo-color.png
- For company icons, use Clearbit format: https://logo.clearbit.com/[company-domain].com
- Examples: https://logo.clearbit.com/apple.com, https://logo.clearbit.com/microsoft.com, https://logo.clearbit.com/tesla.com
- Fallback for any company: https://placehold.co/20x20/005F90/ffffff?text=[TICKER]
- Use actual company name (not placeholder) and determine rating based on your analysis
-->
<div class="slide report-prose" id="slide-financial-income-statement">
    <div class="slide-logo" style="top: 65px;">
        <img src="https://images.ctfassets.net/tl4x668xzide/7mygwms2vuSwirnfvaCSvL/72d2bbd858a69aecbf59fd3fb8954484/robeco-logo-color.png" alt="Robeco Logo" style="height: 2rem;">
    </div>
    <header class="report-header-container">
        <div class="header-blue-border">
            <div class="company-header">
                <!-- INSTRUCTION: Replace with actual company domain (e.g., apple.com, microsoft.com) -->
                <!-- INSTRUCTION: Replace with company's main domain for logo. Use https://logo.clearbit.com/[COMPANY-DOMAIN].com format
                Examples: apple.com, microsoft.com, tesla.com, frasersproperty.com, etc. 
                Research the actual company domain from stock_data['company_name'] and use appropriate domain -->
                <img src="https://logo.clearbit.com/[COMPANY-DOMAIN].com" onerror="this.onerror=null;this.src='https://placehold.co/20x20/005F90/ffffff?text={ticker}';" alt="Company Icon" class="icon" style="margin-top: -5px; width: 20px; height: 20px;">
                <h1 class="name"><!-- INSTRUCTION: Use the FULL OFFICIAL company name from stock_data['company_name'] NOT the user input. Example: "Daikin Industries, Ltd." not "DAKIN" --></h1>
                <!-- INSTRUCTION: Use CONSISTENT rating across ALL slides. Choose ONE: OVERWEIGHT (green #2E7D32), NEUTRAL (orange #FF8C00), or UNDERWEIGHT (red #C62828) -->
                <div class="rating" style="color: [RATING-COLOR];">[INVESTMENT-RATING]</div>
            </div>
        </div>
    </header>
    <main>
        <h3>[Create a specific title that captures the key income statement insight that drives your investment thesis. Think like a PM presenting to the investment committee - what financial story does the P&L tell? Examples: "REVENUE ACCELERATION & MARGIN EXPANSION DRIVE EARNINGS MOMENTUM" or "SUBSCRIPTION MODEL TRANSFORMATION: 70% RECURRING REVENUE GROWTH" or "COST DISCIPLINE AMID GROWTH: OPERATING LEVERAGE DRIVES PROFITABILITY"]</h3>
        
        [COPY THE COMPLETE INCOME STATEMENT TABLE FROM ABOVE - DON'T GENERATE NEW TABLES]
        
        <p><strong>[Write a section header that identifies the key revenue growth drivers and profitability trends visible in the data]</strong></p>
        <p>[Write 400-500 words with DEEP FINANCIAL FORENSICS that reveals insights consensus misses. MANDATORY ANALYTICAL FRAMEWORK: 1) CONSENSUS ERROR IDENTIFICATION: Identify what street gets wrong about revenue/margin trends with specific evidence (e.g., "Consensus models 5% revenue growth but ignores $500M contract backlog disclosed in last earnings call") 2) HISTORICAL PRICE ATTRIBUTION: Connect income statement changes to past stock moves (e.g., "Q2 margin miss drove 15% stock decline, but one-time costs masked 200bps underlying improvement") 3) DIFFERENTIATED EARNINGS VIEW: Present your contrarian position on earnings quality/trajectory with research support (e.g., "While bears focus on headline revenue deceleration, we see 25% acceleration in high-margin subscription revenue") 4) COMPETITIVE INTELLIGENCE: Reference specific peer comparisons and industry data (e.g., "Unlike competitor margin compression, this company's 300bps expansion reflects superior operational execution") 5) FORWARD EARNINGS CATALYST: Identify specific upcoming events that will drive earnings inflection (e.g., "New product launch in Q1 should deliver $150M incremental high-margin revenue based on pilot program results") 6) INVESTMENT IMPLICATION: Quantify exact impact on valuation and timing (e.g., "Earnings revision cycle supports 20% multiple expansion to 25x vs current 21x"). Reference specific numbers from financial table, cite recent management commentary, and include forward EPS estimates with supporting assumptions. Every statement must connect to stock price implications.]</p>
        
        <p><strong>[Write a section header focusing on operational efficiency and margin expansion opportunities]</strong></p>
        <p>[Write 400-500 words demonstrating advanced understanding of operational leverage, cost structure optimization, and margin expansion catalysts. Connect the financial data to business model advantages and competitive positioning.]</p>
    </main>
    <footer class="report-footer"><p>Robeco Investment Research</p><p>Page 8 / 15</p></footer>
</div>

<div class="slide report-prose" id="slide-financial-balance-sheet">
    <div class="slide-logo" style="top: 65px;">
        <img src="https://images.ctfassets.net/tl4x668xzide/7mygwms2vuSwirnfvaCSvL/72d2bbd858a69aecbf59fd3fb8954484/robeco-logo-color.png" alt="Robeco Logo" style="height: 2rem;">
    </div>
    <header class="report-header-container">
        <div class="header-blue-border">
            <div class="company-header">
                <!-- INSTRUCTION: Replace with actual company domain (e.g., apple.com, microsoft.com) -->
                <!-- INSTRUCTION: Replace with company's main domain for logo. Use https://logo.clearbit.com/[COMPANY-DOMAIN].com format
                Examples: apple.com, microsoft.com, tesla.com, frasersproperty.com, etc. 
                Research the actual company domain from stock_data['company_name'] and use appropriate domain -->
                <img src="https://logo.clearbit.com/[COMPANY-DOMAIN].com" onerror="this.onerror=null;this.src='https://placehold.co/20x20/005F90/ffffff?text={ticker}';" alt="Company Icon" class="icon" style="margin-top: -5px; width: 20px; height: 20px;">
                <h1 class="name"><!-- INSTRUCTION: Use the FULL OFFICIAL company name from stock_data['company_name'] NOT the user input. Example: "Daikin Industries, Ltd." not "DAKIN" --></h1>
                <!-- INSTRUCTION: Use CONSISTENT rating across ALL slides. Choose ONE: OVERWEIGHT (green #2E7D32), NEUTRAL (orange #FF8C00), or UNDERWEIGHT (red #C62828) -->
                <div class="rating" style="color: [RATING-COLOR];">[INVESTMENT-RATING]</div>
            </div>
        </div>
    </header>
    <main>
        <h3>[Create a title that demonstrates sophisticated balance sheet analysis and shows what this means for investment returns. Think like a PM assessing financial strength and capital allocation. Examples: "FORTRESS BALANCE SHEET: $200B CASH ENABLES STRATEGIC FLEXIBILITY" or "DEBT OPTIMIZATION: REFINANCING LOWERS COST OF CAPITAL 150bps" or "ASSET-LIGHT MODEL: HIGH ROIC FROM WORKING CAPITAL EFFICIENCY"]</h3>
        
        [COPY THE COMPLETE BALANCE SHEET TABLE FROM ABOVE - DON'T GENERATE NEW TABLES]
        
        <p><strong>[Write a section header that identifies the key balance sheet strengths and what they enable strategically]</strong></p>
        <p>[Write 400-500 words like a PM assessing balance sheet quality for investment risk/return profile. Focus on: 1) Capital structure optimization - debt levels, cost of capital, refinancing opportunities, credit quality 2) Asset quality and efficiency - working capital management, asset turnover, return on assets, hidden assets/liabilities 3) Financial flexibility assessment - cash position, borrowing capacity, covenant headroom, acquisition capability 4) Risk assessment - leverage ratios, liquidity position, maturity profile, off-balance sheet items 5) Investment implications - how balance sheet strength supports growth investments, shareholder returns, defensive characteristics. Reference specific metrics from the table and compare to industry standards. Show understanding of how balance sheet positioning creates or destroys shareholder value.]</p>
        
        <p><strong>[Write a section header on capital allocation effectiveness and return on invested capital]</strong></p>
        <p>[Write 400-500 words demonstrating sophisticated understanding of how management uses the balance sheet to create shareholder value through strategic investments, acquisitions, and capital returns.]</p>
    </main>
    <footer class="report-footer"><p>Robeco Investment Research</p><p>Page 9 / 15</p></footer>
</div>

<div class="slide report-prose" id="slide-financial-cash-flow-statement">
    <div class="slide-logo" style="top: 65px;">
        <img src="https://images.ctfassets.net/tl4x668xzide/7mygwms2vuSwirnfvaCSvL/72d2bbd858a69aecbf59fd3fb8954484/robeco-logo-color.png" alt="Robeco Logo" style="height: 2rem;">
    </div>
    <header class="report-header-container">
        <div class="header-blue-border">
            <div class="company-header">
                <!-- INSTRUCTION: Replace with actual for {company_name} domain (e.g., apple.com, microsoft.com) -->
                <!-- INSTRUCTION: Replace with company's main domain for logo. Use https://logo.clearbit.com/[COMPANY-DOMAIN].com format
                Examples: apple.com, microsoft.com, tesla.com, frasersproperty.com, etc. 
                Research the actual company domain from stock_data['company_name'] and use appropriate domain -->
                <img src="https://logo.clearbit.com/[COMPANY-DOMAIN].com" onerror="this.onerror=null;this.src='https://placehold.co/20x20/005F90/ffffff?text={ticker}';" alt="Company Icon" class="icon" style="margin-top: -5px; width: 20px; height: 20px;">
                <h1 class="name"><!-- INSTRUCTION: Use the FULL OFFICIAL company name from stock_data['company_name'] NOT the user input. Example: "Daikin Industries, Ltd." not "DAKIN" --></h1>
                <!-- INSTRUCTION: Use CONSISTENT rating across ALL slides. Choose ONE: OVERWEIGHT (green #2E7D32), NEUTRAL (orange #FF8C00), or UNDERWEIGHT (red #C62828) -->
                <div class="rating" style="color: [RATING-COLOR];">[INVESTMENT-RATING]</div>
            </div>
        </div>
    </header>
    <main>
        <h3>[Create a title highlighting the key cash flow insight that validates your investment thesis for {company_name} as of {datetime.now().strftime("%B %Y")}. Think like a PM focused on cash generation quality and sustainability. Examples: "EXCEPTIONAL FCF CONVERSION: 95% OF NET INCOME TO FREE CASH FLOW" or "CAPEX EFFICIENCY: GROWTH WITH MINIMAL CAPITAL INTENSITY" or "CASH GENERATION ACCELERATION: WORKING CAPITAL IMPROVEMENTS"]</h3>
        
        [COPY THE COMPLETE CASH FLOW TABLE FROM ABOVE - DON'T GENERATE NEW TABLES]
        
        <p><strong>[Write a section header that identifies the quality and sustainability of operating cash flow generation]</strong></p>
        <p>[Write 600-800 words like a top-tier PM evaluating cash flow quality for investment decision-making that incrope the for {company_name}' specifc business model and fundemntal and link to the financial statements result. Focus on: 1) Operating cash flow quality - cash vs non-cash earnings, working capital impacts, seasonality patterns, collection efficiency 2) Free cash flow analysis - capex requirements, maintenance vs growth capex, asset intensity, cash conversion cycles 3) Cash flow sustainability - predictability, cyclicality, margin of safety, through-cycle analysis 4) Capital allocation analysis - reinvestment needs, dividend coverage, buyback capacity, acquisition funding 5) Investment implications - how cash generation supports valuation models, dividend growth, balance sheet strength. Reference specific numbers from the table and analyze cash flow trends vs peers. Show understanding of what separates high-quality cash generators from earnings manipulators.]</p>
        
        <p><strong>[Write a section header on capital efficiency and free cash flow yield analysi for {company_name}]</strong></p>
        <p>[Write 400-500 words demonstrating advanced understanding of cash flow-based valuation, capital intensity analysis, and how cash generation patterns support your investment thesis, must link to the financial statements result and the company fundmental and specifc events/news that happened that related to the cash flow and the investment thesis]</p>
    </main>
    <footer class="report-footer"><p>Robeco Investment Research</p><p>Page 10 / 15</p></footer>
</div>

<div class="slide report-prose" id="slide-financial-ratios">
    <div class="slide-logo" style="top: 65px;">
        <img src="https://images.ctfassets.net/tl4x668xzide/7mygwms2vuSwirnfvaCSvL/72d2bbd858a69aecbf59fd3fb8954484/robeco-logo-color.png" alt="Robeco Logo" style="height: 2rem;">
    </div>
    <header class="report-header-container">
        <div class="header-blue-border">
            <div class="company-header">
                <!-- INSTRUCTION: Replace with actual for {company_name} domain (e.g., apple.com, microsoft.com) -->
                <!-- INSTRUCTION: Replace with company's main domain for logo. Use https://logo.clearbit.com/[COMPANY-DOMAIN].com format
                Examples: apple.com, microsoft.com, tesla.com, frasersproperty.com, etc. 
                Research the actual company domain from stock_data['company_name'] and use appropriate domain -->
                <img src="https://logo.clearbit.com/[COMPANY-DOMAIN].com" onerror="this.onerror=null;this.src='https://placehold.co/20x20/005F90/ffffff?text={ticker}';" alt="Company Icon" class="icon" style="margin-top: -5px; width: 20px; height: 20px;">
                <h1 class="name"><!-- INSTRUCTION: Use the FULL OFFICIAL company name from stock_data['company_name'] NOT the user input. Example: "Daikin Industries, Ltd." not "DAKIN" --></h1>
                <!-- INSTRUCTION: Use CONSISTENT rating across ALL slides. Choose ONE: OVERWEIGHT (green #2E7D32), NEUTRAL (orange #FF8C00), or UNDERWEIGHT (red #C62828) -->
                <div class="rating" style="color: [RATING-COLOR];">[INVESTMENT-RATING]</div>
            </div>
        </div>
    </header>
    <main>
        <h3>[Create a title that shows sophisticated ratio analysis and competitive benchmarking for {company_name} as of {datetime.now().strftime("%B %Y")}. Think like a PM demonstrating superior analytical insight. Examples: "SUPERIOR CAPITAL EFFICIENCY: 25% ROE VS INDUSTRY 12% AVERAGE" or "MARGIN EXPANSION OPPORTUNITY: PATH TO INDUSTRY-LEADING PROFITABILITY" or "ASSET TURNOVER LEADERSHIP: OPERATIONAL EFFICIENCY DRIVES RETURNS"]</h3>
        
        <p><strong>[Write a section header focusing on profitability ratios and peer comparison analysis for {company_name}]</strong></p>
        <p>[Write 400-500 words like a PM conducting sophisticated ratio analysis for portfolio construction. Focus on: 1) Profitability analysis - ROE decomposition (margin x turnover x leverage), ROI trends, ROIC vs WACC analysis, peer benchmarking 2) Quality metrics - gross margin stability, EBITDA margin expansion, operating leverage measurement 3) Efficiency ratios - asset turnover, working capital management, inventory turnover, receivables quality 4) Trend analysis - 3-5 year ratio evolution, cyclical adjustments, normalized earnings power 5) Investment implications - how ratio analysis supports valuation premium/discount, identifies operational improvements, predicts mean reversion. Use industry-specific ratios and benchmarks. Show understanding of what ratios matter most for this business model and industry.]</p>
        
        <p><strong>[Write a section header on capital allocation efficiency and shareholder return metrics]</strong></p>
        <p>[Write 400-500 words demonstrating advanced understanding of capital efficiency metrics, management effectiveness in deploying capital, and how this translates to superior shareholder returns vs alternatives.]</p>
    </main>
    <footer class="report-footer"><p>Robeco Investment Research</p><p>Page 11 / 15</p></footer>
</div>

<div class="slide report-prose" id="slide-valuation">
    <div class="slide-logo" style="top: 65px;">
        <img src="https://images.ctfassets.net/tl4x668xzide/7mygwms2vuSwirnfvaCSvL/72d2bbd858a69aecbf59fd3fb8954484/robeco-logo-color.png" alt="Robeco Logo" style="height: 2rem;">
    </div>
    <header class="report-header-container">
        <div class="header-blue-border">
            <div class="company-header">
                <!-- INSTRUCTION: Replace with actual for {company_name} domain (e.g., apple.com, microsoft.com) -->
                <!-- INSTRUCTION: Replace with company's main domain for logo. Use https://logo.clearbit.com/[COMPANY-DOMAIN].com format
                Examples: apple.com, microsoft.com, tesla.com, frasersproperty.com, etc. 
                Research the actual company domain from stock_data['company_name'] and use appropriate domain -->
                <img src="https://logo.clearbit.com/[COMPANY-DOMAIN].com" onerror="this.onerror=null;this.src='https://placehold.co/20x20/005F90/ffffff?text={ticker}';" alt="Company Icon" class="icon" style="margin-top: -5px; width: 20px; height: 20px;">
                <h1 class="name"><!-- INSTRUCTION: Use the FULL OFFICIAL company name from stock_data['company_name'] NOT the user input. Example: "Daikin Industries, Ltd." not "DAKIN" --></h1>
                <!-- INSTRUCTION: Use CONSISTENT rating across ALL slides. Choose ONE: OVERWEIGHT (green #2E7D32), NEUTRAL (orange #FF8C00), or UNDERWEIGHT (red #C62828) -->
                <div class="rating" style="color: [RATING-COLOR];">[INVESTMENT-RATING]</div>
            </div>
        </div>
    </header>
    <main>
        <h3>[Create a title that demonstrates sophisticated valuation analysis and shows specific upside potential for {company_name} as of {datetime.now().strftime("%B %Y")}. Think like a PM presenting a compelling valuation case. Examples: "SIGNIFICANT UNDERVALUATION: DCF SHOWS 40% UPSIDE TO FAIR VALUE" or "GROWTH AT REASONABLE PRICE: 1.2 PEG RATIO SUPPORTS PREMIUM" or "SUM-OF-PARTS ANALYSIS: HIDDEN VALUE IN UNDERVALUED SEGMENTS"]</h3>
        
        <p><strong>[Write a section header on DCF analysis and intrinsic value calculation]</strong></p>
        <p>[Write 700-800 words with DEEP DCF LINE-ITEM ANALYSIS that demonstrates sophisticated bottom-up modeling. ⚠️ GOOGLE SEARCH REQUIREMENT: Use Google Search extensively to verify all financial data, recent earnings results, segment performance, industry forecasts, and competitive dynamics mentioned. 

MANDATORY DCF STRUCTURE - ANALYZE EACH COMPONENT:

**REVENUE BREAKDOWN & FORECASTING (200-250 words):**
1) SEGMENT-LEVEL ANALYSIS: Break down revenue by business segments/geographies with specific growth drivers. Search for latest segment reporting, management guidance, and end-market dynamics
2) UNIT ECONOMICS: Analyze revenue per customer, pricing trends, volume growth, market share progression. Search for unit metrics, customer growth rates, and pricing announcements
3) CYCLICAL vs STRUCTURAL GROWTH: Distinguish temporary vs sustainable revenue drivers. Search for industry growth rates, competitive positioning, and secular trends
4) TOP-LINE CATALYSTS: Quantify impact of new products, market expansion, price increases. Search for product launch timelines, addressable market size, and penetration rates

**OPERATING MARGIN PROGRESSION (200-250 words):**
1) MARGIN BRIDGE ANALYSIS: Decompose operating leverage, cost inflation, mix effects, efficiency gains. Search for recent cost pressures, automation initiatives, and margin guidance
2) SCALABILITY ASSESSMENT: Fixed vs variable cost structure, incremental margin potential. Search for operating leverage history and management commentary on scalability
3) COMPETITIVE DYNAMICS: Margin sustainability vs pricing pressure, moat strength. Search for competitor margin trends and pricing actions
4) INVESTMENT PHASE IMPACT: R&D, capex, SG&A investments and their margin implications. Search for investment cycles and expected returns

**FREE CASH FLOW MODELING (200-250 words):**
1) CAPEX REQUIREMENTS: Maintenance vs growth capex, asset intensity, automation investments. Search for recent capex guidance and industry reinvestment needs
2) WORKING CAPITAL DYNAMICS: Cash conversion cycles, seasonality, growth impact on working capital. Search for working capital trends and management efficiency initiatives
3) CASH CONVERSION QUALITY: Percentage of earnings converted to free cash flow, sustainability. Search for cash flow quality metrics and historical conversion rates
4) TAX OPTIMIZATION: Effective tax rate progression, geographic optimization, tax reform impact. Search for recent tax strategies and jurisdictional changes

Each analysis must connect to current fundamentals using specific public information sources and predict future performance based on verifiable trends and management actions.

**🔥 SLIDE 12 ULTRA-HIGH DENSITY REQUIREMENTS:**
PACK MAXIMUM ANALYTICAL VALUE - This section must be dense with quantified insights:
- Include 15+ specific financial metrics (growth rates, margins, ratios, multiples)
- Reference 6+ peer companies with exact valuation multiples  
- Present 3+ valuation methodologies with specific price targets
- Provide 8+ DCF assumptions with justification and sensitivity analysis
- Include 4+ scenario outcomes with probability weightings
- Reference 10+ recent data points (earnings, guidance, industry reports)
- Every sentence must contain 2-3 quantified data points - NO filler content]</p>
        
        <p><strong>[Write a section header on multiple-based valuation and peer comparison]</strong></p>
        <p>[Write 600-700 words demonstrating SOPHISTICATED RELATIVE VALUATION with quality-adjusted peer analysis. ⚠️ GOOGLE SEARCH REQUIREMENT: Search extensively for current peer multiples, financial metrics, growth rates, and recent trading patterns.

MANDATORY MULTIPLES ANALYSIS STRUCTURE:

**PEER SELECTION & ADJUSTMENT (150-200 words):**
1) PURE-PLAY IDENTIFICATION: Select 4-6 closest operational comparables with justification. Search for companies with similar business models, end markets, and scale
2) FINANCIAL QUALITY ADJUSTMENTS: Normalize for differences in profitability, growth, balance sheet strength. Search for peer ROE, ROIC, debt levels, and cash generation metrics
3) BUSINESS MODEL PREMIUMS/DISCOUNTS: Quantify valuation impact of subscription vs transactional, asset-light vs asset-heavy, recurring vs cyclical. Search for business model valuations and investor preferences
4) MARKET POSITIONING: Adjust for competitive positioning, market share, and moat strength. Search for market share data and competitive analysis

**FORWARD-LOOKING MULTIPLE ANALYSIS (200-250 words):**
1) EV/SALES PROGRESSION: Analyze revenue quality, growth sustainability, conversion to profits. Search for revenue visibility, contract duration, and organic vs inorganic growth
2) EV/EBITDA vs EBIT SPREAD: Assess D&A intensity, capex requirements, asset productivity. Search for peer capital intensity and depreciation policies
3) P/E vs PEG ANALYSIS: Growth-adjusted valuation, earnings quality, cyclical adjustments. Search for earnings growth forecasts and quality metrics
4) PRICE/BOOK PREMIUM: Asset intensity, intangible value, return on equity justification. Search for peer asset turns and intangible asset ratios

**CATALYST-DRIVEN MULTIPLE EXPANSION (200-250 words):**
1) HISTORICAL RE-RATING ANALYSIS: When and why multiples expanded/contracted historically. Search for past multiple ranges and fundamental drivers
2) PEER MULTIPLE MIGRATION: Track how comparable companies achieved premium valuations. Search for successful transformation stories and multiple progression
3) SECTOR ROTATION IMPACT: Position within investment themes and sector allocation flows. Search for sector performance trends and institutional flows
4) TIMING CATALYSTS: Specific events that drive multiple re-rating (earnings, approvals, announcements). Search for upcoming catalysts and historical precedents

Connect each multiple to fundamental performance and show specific path to valuation convergence/divergence with peers based on differentiated business performance.]</p>
    </main>
    <footer class="report-footer"><p>Robeco Investment Research</p><p>Page 12 / 15</p></footer>
</div>
```

**SLIDES 13-15 - COMPREHENSIVE ANALYSIS & CONCLUSION:**
```html
<div class="slide report-prose" id="slide-bull-bear-analysis">
    <div class="slide-logo" style="top: 65px;">
        <img src="https://images.ctfassets.net/tl4x668xzide/7mygwms2vuSwirnfvaCSvL/72d2bbd858a69aecbf59fd3fb8954484/robeco-logo-color.png" alt="Robeco Logo" style="height: 2rem;">
    </div>
    <header class="report-header-container">
        <div class="header-blue-border">
            <div class="company-header">
                <!-- INSTRUCTION: Replace with actual company domain (e.g., apple.com, microsoft.com) -->
                <!-- INSTRUCTION: Replace with company's main domain for logo. Use https://logo.clearbit.com/[COMPANY-DOMAIN].com format
                Examples: apple.com, microsoft.com, tesla.com, frasersproperty.com, etc. 
                Research the actual company domain from stock_data['company_name'] and use appropriate domain -->
                <img src="https://logo.clearbit.com/[COMPANY-DOMAIN].com" onerror="this.onerror=null;this.src='https://placehold.co/20x20/005F90/ffffff?text={ticker}';" alt="Company Icon" class="icon" style="margin-top: -5px; width: 20px; height: 20px;">
                <h1 class="name"><!-- INSTRUCTION: Use the FULL OFFICIAL company name from stock_data['company_name'] NOT the user input. Example: "Daikin Industries, Ltd." not "DAKIN" --></h1>
                <!-- INSTRUCTION: Use CONSISTENT rating across ALL slides. Choose ONE: OVERWEIGHT (green #2E7D32), NEUTRAL (orange #FF8C00), or UNDERWEIGHT (red #C62828) -->
                <div class="rating" style="color: [RATING-COLOR];">[INVESTMENT-RATING]</div>
            </div>
        </div>
    </header>
    <main>
        <h3>[Create a title that demonstrates sophisticated risk assessment and asymmetric return analysis for {company_name} as of {datetime.now().strftime("%B %Y")}. Think like a PM presenting risk/reward to investment committee. Examples: "AI LEADERSHIP VS COMPETITION THREAT: ASYMMETRIC RISK/REWARD" or "MARKET EXPANSION VS REGULATORY RISK: PROBABILITY-WEIGHTED OUTCOMES" or "MARGIN EXPANSION VS CYCLICAL HEADWINDS: DEFENSIVE GROWTH PROFILE"]</h3>
        
        <h4>[Write a bull case section title that identifies the primary upside driver with quantified potential. Example: "Bull Case: AI Platform Dominance Drives 40% Revenue CAGR"]</h4>
        <p>[Write 500-600 words like a PM building the bull case for investment committee approval. Focus on: 1) Primary upside catalyst with specific timeline and probability assessment 2) Quantified financial impact - revenue growth, margin expansion, market share gains with supporting analysis 3) Market opportunity size and company's ability to capture value with competitive advantages 4) Multiple expansion potential and valuation re-rating catalysts 5) Risk mitigation factors that protect downside even if bull case doesn't fully materialize. Use specific data, industry research, and competitive intelligence. Show sophisticated understanding of what could drive exceptional returns and why this outcome is achievable.]</p>
        
        <h4>[Write a bear case section title that identifies the primary downside risk with specific threat. Example: "Bear Case: Regulatory Headwinds + Competition Pressure Margin Compression"]</h4> 
        <p>[Write 500-600 words like a PM conducting rigorous risk analysis for downside protection. Focus on: 1) Primary downside risk with timeline and probability assessment 2) Quantified negative impact - revenue headwinds, margin compression, market share loss with supporting analysis 3) Competitive threats, regulatory risks, or macro headwinds that could derail thesis 4) Valuation compression scenarios and multiple contraction risks 5) Risk mitigation strategies, hedging opportunities, and downside protection measures. Show understanding of base rates, historical precedents, and what has gone wrong in similar situations. Demonstrate sophisticated risk management thinking.]</p>
        
        <h4>Risk-Adjusted Return Assessment & Expected Value Calculation for {company_name} as of {datetime.now().strftime("%B %Y")}</h4>
        <p>[Write 400-500 words like a PM conducting rigorous expected value analysis for portfolio construction. Include probability-weighted scenario analysis, Sharpe ratio calculations, maximum drawdown assessment, and correlation analysis vs portfolio holdings. Show sophisticated risk-adjusted return thinking that goes beyond simple upside/downside scenarios.]</p>
    </main>
    <footer class="report-footer"><p>Robeco Investment Research</p><p>Page 13 / 15</p></footer>
</div>

<div class="slide report-prose" id="slide-scenario-analysis">
    <div class="slide-logo" style="top: 65px;">
        <img src="https://images.ctfassets.net/tl4x668xzide/7mygwms2vuSwirnfvaCSvL/72d2bbd858a69aecbf59fd3fb8954484/robeco-logo-color.png" alt="Robeco Logo" style="height: 2rem;">
    </div>
    <header class="report-header-container">
        <div class="header-blue-border">
            <div class="company-header">
                <!-- INSTRUCTION: Replace with actual company domain (e.g., apple.com, microsoft.com) -->
                <!-- INSTRUCTION: Replace with company's main domain for logo. Use https://logo.clearbit.com/[COMPANY-DOMAIN].com format
                Examples: apple.com, microsoft.com, tesla.com, frasersproperty.com, etc. 
                Research the actual company domain from stock_data['company_name'] and use appropriate domain -->
                <img src="https://logo.clearbit.com/[COMPANY-DOMAIN].com" onerror="this.onerror=null;this.src='https://placehold.co/20x20/005F90/ffffff?text={ticker}';" alt="Company Icon" class="icon" style="margin-top: -5px; width: 20px; height: 20px;">
                <h1 class="name"><!-- INSTRUCTION: Use the FULL OFFICIAL company name from stock_data['company_name'] NOT the user input. Example: "Daikin Industries, Ltd." not "DAKIN" --></h1>
                <!-- INSTRUCTION: Use CONSISTENT rating across ALL slides. Choose ONE: OVERWEIGHT (green #2E7D32), NEUTRAL (orange #FF8C00), or UNDERWEIGHT (red #C62828) -->
                <div class="rating" style="color: [RATING-COLOR];">[INVESTMENT-RATING]</div>
            </div>
        </div>
    </header>
    <main>
        <h3>[Create a title that demonstrates sophisticated scenario analysis and quantified probability assessment. Think like a PM using Monte Carlo analysis. Examples: "THREE SCENARIOS: BASE CASE 25% RETURNS DRIVE OVERWEIGHT RATING" or "MONTE CARLO ANALYSIS: 70% PROBABILITY OF OUTPERFORMANCE" or "RISK-ADJUSTED RETURNS: 2.1 SHARPE RATIO IN ALL SCENARIOS"]</h3>
        
        <p><strong>[Write section header for base case with specific probability and return expectation]</strong></p>
        <p>[Write 400-500 words like a PM modeling the most likely scenario for investment committee. Focus on: 1) Base case assumptions with supporting rationale and historical precedents 2) Key financial drivers and their expected evolution with specific timeline 3) Catalyst realization timeline with realistic execution assessment 4) Expected return calculation with proper risk adjustment 5) Key signposts and metrics to monitor base case progression. Use industry benchmarks, management guidance analysis, and competitive positioning assessment. Show this is the most probable outcome with supporting evidence.]</p>
        
        <p><strong>[Write section header for bull case with specific probability and upside potential]</strong></p>
        <p>[Write 400-500 words demonstrating sophisticated understanding of what drives exceptional investment outcomes. Include analysis of catalyst acceleration, market expansion scenarios, and multiple re-rating potential with quantified upside targets and timeline.]</p>
        
        <p><strong>[Write section header for bear case with specific probability and downside protection]</strong></p>
        <p>[Write 400-500 words showing advanced risk analysis of what could go wrong, with specific downside scenarios, risk mitigation strategies, and portfolio protection measures.]</p>
        
        <p><strong>Expected Value Analysis & Target Price Derivation</strong></p>
        <p>[Write 300-400 words like a PM calculating probability-weighted target prices for position sizing decisions. Include expected value calculations, risk-adjusted returns, and specific entry/exit price targets with supporting methodology.]</p>
    </main>
    <footer class="report-footer"><p>Robeco Investment Research</p><p>Page 14 / 15</p></footer>
</div>

<div class="slide report-prose" id="slide-investment-conclusion">
    <div class="slide-logo" style="top: 65px;">
        <img src="https://images.ctfassets.net/tl4x668xzide/7mygwms2vuSwirnfvaCSvL/72d2bbd858a69aecbf59fd3fb8954484/robeco-logo-color.png" alt="Robeco Logo" style="height: 2rem;">
    </div>
    <header class="report-header-container">
        <div class="header-blue-border">
            <div class="company-header">
                <!-- INSTRUCTION: Replace with actual company {company_name} domain (e.g., apple.com, microsoft.com) -->
                <!-- INSTRUCTION: Replace with company's main domain for logo. Use https://logo.clearbit.com/[COMPANY-DOMAIN].com format
                Examples: apple.com, microsoft.com, tesla.com, frasersproperty.com, etc. 
                Research the actual company domain from stock_data['company_name'] and use appropriate domain -->
                <img src="https://logo.clearbit.com/[COMPANY-DOMAIN].com" onerror="this.onerror=null;this.src='https://placehold.co/20x20/005F90/ffffff?text={ticker}';" alt="Company Icon" class="icon" style="margin-top: -5px; width: 20px; height: 20px;">
                <h1 class="name"><!-- INSTRUCTION: Use the FULL OFFICIAL company name from stock_data['company_name'] NOT the user input. Example: "Daikin Industries, Ltd." not "DAKIN" --></h1>
                <!-- INSTRUCTION: Use CONSISTENT rating across ALL slides. Choose ONE: OVERWEIGHT (green #2E7D32), NEUTRAL (orange #FF8C00), or UNDERWEIGHT (red #C62828) -->
                <div class="rating" style="color: [RATING-COLOR];">[INVESTMENT-RATING]</div>
            </div>
        </div>
    </header>
    <main>
        <h3>[Create a title that delivers your SPECIFIC rating with quantified thesis and timeline as of {datetime.now().strftime("%B %Y")}. Google Search: recent guidance, analyst estimates, valuation metrics. Examples: "OVERWEIGHT: 35% UPSIDE FROM AI AUTOMATION BY Q4 2025" or "NEUTRAL: FAIR VALUE AT 18X P/E AMID MARGIN HEADWINDS" or "UNDERWEIGHT: 25% DOWNSIDE RISK FROM CYCLICAL PEAK"]</h3>
        
        <p><strong>[Write section header focusing on the core alpha generation thesis and specific return expectations]</strong></p>
        <p>[Write 400-500 words like a PM delivering the final investment recommendation to the investment committee. Focus on: 1) Core investment thesis with specific return target and timeline 2) Key alpha drivers that differentiate this opportunity from alternatives 3) Catalyst timeline with specific milestones and expected market reaction 4) Risk-adjusted return profile and why this merits portfolio allocation 5) Conviction level and position sizing recommendation based on opportunity size and risk assessment. Synthesize all prior analysis into compelling investment case that demonstrates superior risk-adjusted returns vs alternatives.]</p>
        
        <p><strong>[Write section header on portfolio construction and institutional considerations]</strong></p>
        <p>[Write 300-400 words demonstrating institutional-level portfolio thinking including position sizing, correlation benefits, sector allocation impact, liquidity considerations, and how this investment fits overall portfolio construction strategy.]</p>
        
        <p><strong>[Write section header on monitoring framework and performance tracking]</strong></p>
        <p>[Write 300-400 words like a PM setting up systematic monitoring of investment thesis progression. Include specific KPIs, financial metrics, industry benchmarks, and signposts to track thesis validation or deterioration with actionable triggers for position adjustments.]</p>
        
        <p><strong>[Write section header on catalyst timeline and exit strategy]</strong></p>
        <p>[Write 300-400 words showing sophisticated understanding of catalyst timing, price target realization, exit strategy planning, and specific dates/milestones that will drive investment performance. Include risk management protocols and position adjustment triggers.]</p>
    </main>
    <footer class="report-footer"><p>Robeco Investment Research</p><p>Page 15 / 15</p></footer>
</div>
```

### CRITICAL: NO TABLE GENERATION REQUIRED!

**SLIDES 8-10 - FINANCIAL STATEMENTS ANALYSIS WITH HIGH-DENSITY FRAMEWORK:**

**SLIDE 8 - INCOME STATEMENT ANALYSIS:**
- **H3 Title**: Create compelling title specific to {company_name}'s earnings quality as of {datetime.now().strftime("%B %Y")}

**TITLE CONSTRUCTION FORMULA**: "8. {company_name}: [EARNINGS INSIGHT] & [MARGIN ANALYSIS] AMID [CURRENT ENVIRONMENT]"

**🎯 ADAPTIVE INCOME STATEMENT ANALYSIS FOR {company_name}:**
Generate 2-4 sections (flexible based on {company_name}'s specific financial characteristics) analyzing the most critical income statement insights for THIS company.

**COMPANY-ADAPTIVE ANALYTICAL APPROACH:**
Choose the most relevant analytical angles based on {company_name}'s business model, industry dynamics, and current financial position. Consider these potential dimensions but select only those most critical for {company_name}:

**POTENTIAL INCOME STATEMENT FOCUS AREAS (Select Most Relevant):**
- **Revenue Model Analysis**: For subscription/SaaS companies - recurring vs one-time revenue analysis
- **Seasonality & Cyclicality**: For retail/consumer companies - seasonal pattern analysis and normalization
- **Geographic Revenue Mix**: For multinational companies - regional performance and currency impact analysis
- **Product/Segment Profitability**: For diversified companies - segment margin analysis and resource allocation
- **Operating Leverage Dynamics**: For high fixed-cost companies - incremental margin analysis and scale benefits
- **Pricing Power Assessment**: For branded/premium companies - price realization and volume trade-offs
- **Cost Structure Evolution**: For transforming companies - fixed vs variable cost analysis and efficiency gains
- **Regulatory Impact Analysis**: For regulated industries - regulatory cost impact and compliance analysis

**SLIDE 9 - BALANCE SHEET ANALYSIS:**
- **H3 Title**: Create compelling title specific to {company_name}'s financial strength as of {datetime.now().strftime("%B %Y")}

**TITLE CONSTRUCTION FORMULA**: "9. {company_name}: [BALANCE SHEET STRENGTH] & [CAPITAL STRUCTURE] POSITIONING"

**🎯 ADAPTIVE BALANCE SHEET ANALYSIS FOR {company_name}:**
Generate 2-4 sections (flexible based on {company_name}'s capital structure and business model) analyzing the most critical balance sheet insights for THIS company.

**COMPANY-ADAPTIVE ANALYTICAL APPROACH:**
Choose the most relevant balance sheet angles based on {company_name}'s industry, capital intensity, and financial strategy. Select only the most critical areas for {company_name}:

**POTENTIAL BALANCE SHEET FOCUS AREAS (Select Most Relevant):**
- **Capital Intensity Analysis**: For manufacturing/infrastructure companies - asset turnover and capital efficiency
- **Working Capital Dynamics**: For retail/manufacturing companies - inventory, receivables, and cash conversion cycle
- **Debt Structure Optimization**: For leveraged companies - maturity profile, covenant analysis, and refinancing risks
- **Asset Quality Assessment**: For financial institutions - loan quality, provisions, and risk-weighted assets
- **Intangible Asset Valuation**: For tech/pharma companies - R&D capitalization, IP value, and goodwill analysis
- **Real Estate Portfolio Value**: For REITs/retail companies - property valuation and location analysis
- **Cash Management Strategy**: For cash-rich companies - cash deployment strategy and capital allocation priorities
- **Off-Balance Sheet Analysis**: For complex companies - operating leases, JVs, and contingent liabilities

**SLIDE 10 - CASH FLOW ANALYSIS:**
- **H3 Title**: Create compelling title specific to {company_name}'s cash generation as of {datetime.now().strftime("%B %Y")}

**TITLE CONSTRUCTION FORMULA**: "10. {company_name}: [CASH FLOW INSIGHT] & [CAPITAL ALLOCATION] EFFECTIVENESS"

**🎯 ADAPTIVE CASH FLOW ANALYSIS FOR {company_name}:**
Generate 2-4 sections (flexible based on {company_name}'s cash flow characteristics and business model) analyzing the most critical cash flow insights for THIS company.

**COMPANY-ADAPTIVE ANALYTICAL APPROACH:**
Choose the most relevant cash flow angles based on {company_name}'s business model, capital requirements, and cash flow patterns. Select only the most critical areas for {company_name}:

**POTENTIAL CASH FLOW FOCUS AREAS (Select Most Relevant):**
- **Free Cash Flow Conversion**: For high-growth companies - conversion from earnings to free cash flow and sustainability
- **Capital Allocation Efficiency**: For mature companies - dividend policy, buybacks, and M&A cash deployment
- **Working Capital Seasonality**: For seasonal businesses - cash flow timing and financing requirements
- **Capex Investment Cycles**: For capital-intensive companies - maintenance vs growth capex and ROI analysis
- **Cash Flow Predictability**: For subscription companies - recurring cash flow visibility and customer churn impact
- **Financing Cash Flow Analysis**: For high-growth companies - funding requirements and capital raising patterns
- **Operating Cash Flow Quality**: For complex companies - cash vs non-cash components and sustainability
- **International Cash Flow**: For multinational companies - repatriation policies and geographic cash distribution

**IMPLEMENTATION REQUIREMENTS:**
- **Tables**: Copy the ready-made HTML tables provided above - NEVER create from scratch
- **Analysis**: Write detailed analysis paragraphs referencing specific numbers from the tables
- **Competitive Context**: Compare {company_name} to 2-3 specific competitors in each section

### SIMPLIFIED CALL 2 CONTENT SPECIFICATIONS:

**SLIDES 11-12 (RATIOS & VALUATION) - ULTRA-HIGH DENSITY ANALYSIS:**

**SLIDE 11 - FINANCIAL RATIOS ANALYSIS:**
- **H3 Title**: Create compelling title specific to {{company_name}}'s financial performance as of {datetime.now().strftime("%B %Y")}

**TITLE CONSTRUCTION FORMULA**: "8. {{company_name}}: [KEY FINANCIAL INSIGHT] & [COMPETITIVE POSITIONING] AS OF {datetime.now().strftime("%B %Y")}"

**TITLE CONSTRUCTION PRINCIPLES:**
- **Company Name**: Always start with {{company_name}}
- **Financial Insight**: Capture the 2-3 word core financial strength/weakness
- **Competitive Context**: Reference how {{company_name}} compares to industry/peers
- **Specificity**: Include specific metrics or performance indicators

**🎯 ADAPTIVE FINANCIAL RATIOS ANALYSIS FOR {company_name}:**
Generate 2-4 sections (flexible based on {company_name}'s most critical ratio performance areas) analyzing the key financial metrics that drive investment decisions for THIS company.

**COMPANY-ADAPTIVE ANALYTICAL APPROACH:**
Choose the most relevant ratio categories based on {company_name}'s business model, industry dynamics, and key performance drivers. Select only the most critical ratio areas for {company_name}:

**POTENTIAL FINANCIAL RATIO FOCUS AREAS (Select Most Relevant):**
- **Profitability & Returns Analysis**: For capital-intensive companies - ROE, ROIC, ROA trends and peer comparison
- **Efficiency & Productivity Metrics**: For asset-heavy companies - asset turnover, inventory turns, receivables efficiency
- **Leverage & Coverage Ratios**: For debt-heavy companies - debt/equity, interest coverage, debt service capability
- **Liquidity & Financial Flexibility**: For cyclical companies - current ratio, quick ratio, cash conversion cycle
- **Growth & Investment Ratios**: For high-growth companies - reinvestment rates, growth sustainability metrics
- **Valuation Ratios Analysis**: For value/growth companies - P/E, EV/EBITDA, PEG ratio peer comparison
- **Quality & Sustainability Metrics**: For dividend companies - payout ratios, dividend coverage, earnings quality
- **Sector-Specific Ratios**: For specialized industries - same-store sales (retail), loan-to-deposit (banks), occupancy (REITs)

**SLIDE 12 - VALUATION METHODOLOGY ANALYSIS:**
- **H3 Title**: Create compelling title specific to {{company_name}}'s valuation opportunity as of {datetime.now().strftime("%B %Y")}

**TITLE CONSTRUCTION FORMULA**: "9. {{company_name}}: [VALUATION THESIS] AMID [MARKET MISPRICING/OPPORTUNITY] AS OF {datetime.now().strftime("%B %Y")}"

**🎯 ADAPTIVE VALUATION ANALYSIS FOR {company_name}:**
Generate 2-4 sections (flexible based on {company_name}'s most appropriate valuation methodologies) covering the most relevant valuation approaches for THIS company's business model and industry.

**COMPANY-ADAPTIVE VALUATION APPROACH:**
Choose the most suitable valuation methodologies based on {company_name}'s business characteristics, cash flow patterns, and industry standards. Select only the most relevant approaches for {company_name}:

**POTENTIAL VALUATION METHODOLOGY FOCUS AREAS (Select Most Relevant):**
- **DCF Valuation Analysis**: For stable cash flow companies - detailed DCF with sensitivity analysis and terminal value assessment
- **Comparable Company Analysis**: For industry-standard companies - trading multiples vs peers with premium/discount analysis
- **Sum-of-the-Parts Valuation**: For diversified companies - segment-by-segment valuation and conglomerate discount analysis
- **Asset-Based Valuation**: For asset-heavy companies - book value, replacement cost, and liquidation value analysis
- **Revenue Multiple Analysis**: For high-growth companies - P/S, EV/Sales analysis with growth-adjusted metrics
- **Option Valuation Models**: For development-stage companies - real options valuation for growth opportunities
- **Dividend Discount Model**: For dividend-focused companies - DDM with growth rate and payout ratio analysis
- **Industry-Specific Metrics**: For specialized sectors - price per subscriber (telecom), price per barrel (oil), NAV (REITs)

### CRITICAL SIMPLIFICATION MANDATE:
- **80% complexity reduction** - Remove all nested inline styles
- **Focus on content quality** over visual complexity
- **Use ONLY basic HTML** - `<p>`, `<ul>`, `<li>`, `<strong>`, `<table class="financial-table">`
- **This prevents AI cognitive overload** that caused slide 9-10 failures

### CRITICAL TITLE GENERATION PRINCIPLES FOR CALL 2:
- **FINANCIAL INSIGHT FOCUS**: Every title must capture the key financial insight (e.g., "EXCEPTIONAL FCF CONVERSION: 95% OF NET INCOME TO FREE CASH FLOW")
- **QUANTIFY THE STORY**: Include specific metrics that show financial strength/weakness (e.g., "25% ROE VS INDUSTRY 12% AVERAGE")
- **COMPARATIVE ADVANTAGE**: Show how {company_name}'s financials compare to peers/industry (e.g., "SUPERIOR CAPITAL EFFICIENCY")
- **VALUE DRIVER IDENTIFICATION**: Highlight what drives financial performance (e.g., "SUBSCRIPTION MODEL TRANSFORMATION")
- **INVESTMENT IMPLICATION**: Make clear why this financial insight matters for investment returns
- **NO GENERIC FINANCIAL TITLES**: Avoid "Income Statement Analysis" - use "REVENUE ACCELERATION & MARGIN EXPANSION"
rd valuation with DCF and multiples (no complex tables)
- **Format**: Simple paragraph structure with clear section headers
- **Focus**: Quality over complexity - concise but comprehensive analysis

**SLIDES 13-15 (RISK & CONCLUSION) - INSTITUTIONAL-GRADE ANALYSIS:**

**SLIDE 13 - COMPREHENSIVE RISK ASSESSMENT:**
- **H3 Title**: Create compelling title specific to {company_name}'s risk profile as of {datetime.now().strftime("%B %Y")}

**TITLE CONSTRUCTION FORMULA**: "10. {company_name}: [PRIMARY RISK THEME] & [MITIGATION STRATEGY] IN {datetime.now().strftime("%B %Y")} ENVIRONMENT"

**🎯 ADAPTIVE RISK ANALYSIS FOR {company_name}:**
Generate 2-4 sections (flexible based on {company_name}'s most material risk factors) covering the key risks that could significantly impact investment returns for THIS company.

**COMPANY-ADAPTIVE RISK APPROACH:**
Choose the most material risk categories based on {company_name}'s business model, industry position, and current environment. Select only the most critical risk areas for {company_name}:

**POTENTIAL RISK FOCUS AREAS (Select Most Relevant):**
- **Cyclical & Economic Risks**: For economically sensitive companies - recession impact, interest rate sensitivity, commodity exposure
- **Competitive & Market Share Risks**: For market leaders - disruption threats, new entrants, competitive response risks
- **Regulatory & Political Risks**: For regulated industries - policy changes, compliance costs, political stability
- **Technology & Disruption Risks**: For traditional companies - digital transformation, automation, obsolescence threats
- **Financial & Leverage Risks**: For debt-heavy companies - refinancing, covenant breaches, credit rating risks
- **Operational & Execution Risks**: For complex operations - supply chain, manufacturing, project execution risks
- **ESG & Sustainability Risks**: For resource companies - environmental liabilities, social license, governance issues
- **Geographic & Currency Risks**: For international companies - country risks, currency volatility, trade tensions

**SLIDE 14 - SCENARIO ANALYSIS & BULL/BEAR CASES:**
- **H3 Title**: Create compelling title specific to {company_name}'s scenario outcomes as of {datetime.now().strftime("%B %Y")}

**TITLE CONSTRUCTION FORMULA**: "11. {company_name}: [SCENARIO THEME] WITH [PROBABILITY RANGE] OUTCOMES BY {datetime.now().strftime("%B %Y")}"

**🎯 ADAPTIVE SCENARIO ANALYSIS FOR {company_name}:**
Generate 2-4 sections (flexible based on {company_name}'s key scenario drivers) covering the most probable outcome scenarios that drive investment decision-making for THIS company.

**COMPANY-ADAPTIVE SCENARIO APPROACH:**
Choose the most relevant scenario frameworks based on {company_name}'s key value drivers, risk factors, and catalyst timeline. Select the scenario structure most appropriate for {company_name}:

**POTENTIAL SCENARIO FRAMEWORK OPTIONS (Select Most Relevant):**
- **Traditional Bull/Base/Bear**: For stable companies - probability-weighted outcomes with price targets
- **Catalyst-Driven Scenarios**: For event-driven companies - regulatory approval, merger, product launch outcomes
- **Cycle-Based Scenarios**: For cyclical companies - upcycle, downcycle, recovery scenarios with timing analysis
- **Execution Scenarios**: For turnaround companies - successful transformation vs execution failure scenarios
- **Market Environment Scenarios**: For macro-sensitive companies - rate environment, economic growth scenarios
- **Competitive Response Scenarios**: For market leaders - competitive dynamics and market share scenarios
- **Technology Adoption Scenarios**: For disruptive companies - adoption rate scenarios and market penetration
- **Geographic Expansion Scenarios**: For growth companies - expansion success vs market entry challenges

**SLIDE 15 - INVESTMENT CONCLUSION & RECOMMENDATION:**
- **H3 Title**: Create compelling title specific to {company_name}'s investment conclusion as of {datetime.now().strftime("%B %Y")}

**TITLE CONSTRUCTION FORMULA**: "12. {company_name}: [INVESTMENT RATING] - [KEY CATALYST] DRIVES [EXPECTED RETURN] BY {datetime.now().strftime("%B %Y")}"

**🎯 ADAPTIVE INVESTMENT CONCLUSION FOR {company_name}:**
Generate 3-5 sections (flexible based on {company_name}'s investment complexity and decision factors) synthesizing the complete analysis into actionable portfolio recommendations for THIS company.

**COMPANY-ADAPTIVE CONCLUSION APPROACH:**
Choose the most relevant conclusion framework based on {company_name}'s investment characteristics, risk profile, and portfolio fit. Select the conclusion structure most appropriate for {company_name}:

**POTENTIAL CONCLUSION FOCUS AREAS (Select Most Relevant):**
- **Core Investment Thesis Summary**: For all companies - fundamental value proposition and differentiated positioning
- **Valuation & Price Target Analysis**: For value opportunities - target price methodology and expected returns timeline
- **Risk-Adjusted Return Profile**: For complex positions - risk/reward analysis and portfolio impact assessment
- **Position Sizing & Timing Guidance**: For tactical positions - recommended allocation and entry/exit strategy
- **Catalyst Timeline & Milestones**: For catalyst-driven positions - key events and milestone tracking framework
- **Portfolio Construction Impact**: For core holdings - correlation analysis and diversification benefits
- **ESG & Sustainability Factors**: For ESG-focused strategies - sustainability profile and long-term viability
- **Competitive Moat Assessment**: For quality companies - sustainable advantage analysis and durability assessment

**🎯 ADAPTIVE FRAMEWORK IMPLEMENTATION:**
- **Company-Specific Selection**: For each slide, select only the 2-4 most relevant analytical areas for {company_name}
- **Business Model Driven**: Let {company_name}'s specific characteristics (industry, size, growth stage, capital structure) determine the analytical focus
- **Quality Over Quantity**: Better to have 2 deep, company-specific sections than 4 generic ones
- **Industry Adaptation**: Tech companies get different analysis than REITs, banks get different analysis than retail companies

**ULTRA-HIGH INFORMATION DENSITY STANDARDS FOR ALL CALL 2 SLIDES:**
- Each section: 600-800 words with MINIMUM 15 quantified data points
- Every paragraph must contain 3-4 specific metrics, dates, or comparative benchmarks
- **Financial Data Density**: Include 8-12 financial metrics per section with peer comparisons
- **Historical Benchmarking**: Reference 3-5 year financial trends with specific competitor comparisons
- **Forward-Looking Financial Intelligence**: Predict financial performance with probability assessments
- **Multi-Dimensional Financial Comparison**: Compare across profitability, efficiency, leverage, and growth metrics
- Connect financial analysis to macro economic trends and competitive landscape shifts

**COMPETITIVE FINANCIAL ANALYSIS DEPTH REQUIREMENTS:**
- **Peer Financial Benchmarking**: Compare {company_name} to 2-3 closest competitors with exact financial ratios
- **Quantified Financial Positioning**: Show specific metrics where {company_name} leads/lags (ROE, margins, debt ratios, etc.)
- **Financial Strategy Differentiation**: Explain capital allocation choices that differentiate {company_name} from competitors
- **Financial Performance Prediction**: Forecast how {company_name}'s financial metrics will evolve vs peer group
### CRITICAL SIMPLIFICATION MANDATE FOR CALL 2:
- **80% complexity reduction** - Remove all nested inline styles that cause AI cognitive overload
- **Focus on analytical content quality** over visual complexity  
- **Use ONLY basic HTML** - `<p>`, `<ul>`, `<li>`, `<strong>`, `<h3>`, `<h4>`, `<table class="financial-table">`
- **This prevents AI cognitive overload** that historically caused slide 9-10 generation failures

### 🎯 CRITICAL TITLE GENERATION FOR CALL 2:
- **FINANCIAL INSIGHT FOCUS**: Every title must capture the key financial insight (e.g., "EXCEPTIONAL FCF CONVERSION: 95% OF NET INCOME TO FREE CASH FLOW")
- **QUANTIFY THE STORY**: Include specific metrics showing strength/weakness (e.g., "25% ROE VS INDUSTRY 12% AVERAGE")  
- **COMPARATIVE ADVANTAGE**: Show {company_name}'s financials vs peers (e.g., "SUPERIOR CAPITAL EFFICIENCY: 25% ROIC VS PEER 15%")
- **VALUE DRIVER IDENTIFICATION**: Highlight what drives performance (e.g., "SUBSCRIPTION MODEL: 70% GROSS MARGINS")
- **INVESTMENT IMPLICATION**: Connect financial insight to stock price impact and investment returns
- **NO GENERIC TITLES**: Avoid "Income Statement Analysis" - use "REVENUE ACCELERATION & MARGIN EXPANSION CYCLE"

### ELITE PM FINANCIAL ANALYSIS FRAMEWORK for {company_name} as of {datetime.now().strftime("%B %Y")}:

** FINANCIAL FORENSICS & QUALITY ANALYSIS:**
- **Earnings Quality Dissection**: Separate recurring vs. non-recurring, cash vs. non-cash components; assess sustainability of reported margins; identify accounting choices that enhance/mask true performance specific to {company_name} as of {datetime.now().strftime("%B %Y")}
- **Capital Allocation Mastery**: Assess ROIC trends by segment, incremental returns on new investments, M&A track record, and value creation vs. destruction patterns
- **Hidden Value Discovery**: Identify understated assets, off-balance sheet value, real estate/IP portfolios, and embedded optionality not reflected in current valuation

**⚡ FORWARD-LOOKING FINANCIAL INSIGHTS:**
- **Leading Indicator Analysis**: Identify metrics that predict earnings 2-3 quarters ahead (deferred revenue growth, customer acquisition trends, inventory patterns)
- **Margin Inflection Prediction**: Analyze when margin expansion/compression accelerates; assess pricing power sustainability and cost structure evolution
- **Cash Flow Predictability**: Evaluate free cash flow conversion consistency, working capital seasonality, and cash generation through cycles
- **Capital Efficiency Evolution**: Predict future ROIC/ROE trajectory based on investment patterns, competitive positioning, and industry dynamics

**🎯 NON-CONSENSUS INSIGHTS & ALPHA GENERATION:**
- **Segment Profitability Deep Dive**: Uncover hidden value in segments consensus treats as commoditized; identify cross-subsidization and standalone opportunities
- **Competitive Financial Edge**: Predict how {company_name}'s unit economics and cost advantages evolve vs peers; assess pricing power sustainability
- **Capital Cycle Positioning**: Determine where company sits in investment/harvest cycle; predict future cash generation vs. capital needs
- **Quality of Growth Assessment**: Distinguish growth that creates vs. destroys value using incremental returns and customer economics analysis

**PRACTICAL VALUATION & RISK ASSESSMENT:**
- **Multiple Valuation Methods**: DCF with realistic assumptions, sum-of-parts analysis, peer comparisons with quality adjustments
- **Scenario Analysis**: Bull/base/bear cases with specific assumptions and probability assessments based on fundamentals
- **Through-Cycle Normalization**: Adjust for cyclical factors to assess sustainable earning power and appropriate multiples
- **Risk Factor Identification**: Company-specific, sector, and macro risks with impact quantification and mitigation assessment

{user_context}

{financial_context}

{analyst_insights}

**ULTRA-SOPHISTICATED EXECUTION MANDATE as of {datetime.now().strftime("%B %Y")}**: 
Generate ALL 8 slides that demonstrate **differentiated financial insights, predictive analytics, and quantitative edge** that validates your investment thesis through analysis that others systematically miss. Each slide must answer: **"What do the financials reveal about {company_name}'s future that consensus analysis overlooks?"**

**CRITICAL ANALYTICAL REQUIREMENTS:**
- **EXPLICIT DATE CONTEXT**: All analysis must explicitly reference current date {datetime.now().strftime("%B %Y")} to ensure updated information
- **MANDATORY GOOGLE SEARCH GROUNDING**: ALL information must be grounded with Google Search tool - no generic statements allowed
- **DIFFERENTIATED VIEW MANDATE**: Show what previous fundamentals reveal about stock price implications and future implications based on recent company strategy and themes
- **FORWARD-LOOKING FOCUS**: Provide concrete, precise analysis that demonstrates deep company understanding and insight into how strategy affects stock price and future performance
- **PM CONVICTION STANDARD**: Write concise, precise analysis that convinces PM you are different, have your own view, know company very well, and understand how company strategy will affect stock price and future - NO bullshit, be concrete and precise

**ADVANCED WRITING TECHNIQUES FOR MAXIMUM PM IMPACT:**
- **QUANTIFIED SPECIFICITY**: Use exact numbers, not ranges. "23.4% margin expansion" not "strong margins"
- **HISTORICAL PATTERN RECOGNITION**: Reference specific past events. "Similar to 2019 automation rollout that drove 400bps margin gains"
- **MANAGEMENT BEHAVIOR DECODING**: Read between lines. "CFO's emphasis on 'capital discipline' signals dividend increase vs buybacks"
- **SECOND-ORDER IMPLICATIONS**: Show cascade effects. "Pricing power in segment A enables cross-subsidization of segment B expansion"
- **COMPETITIVE INTELLIGENCE**: Demonstrate market knowledge. "While peers struggle with supply chain, {company_name}'s vertical integration provides 18-month cost advantage"
- **UNIT ECONOMICS MASTERY**: Show business model understanding. "Each new customer generates $2.3K annual recurring revenue at 67% gross margin"
- **CATALYST SEQUENCING**: Predict event timing. "Q1 earnings will show margin inflection, followed by guidance raise in Q2, driving re-rating by Q3"
- **CONTRARIAN EVIDENCE ACKNOWLEDGMENT**: Address bear case. "Despite cyclical headwinds, structural demand shift to premium segment sustains pricing"
- **INSIDER-LEVEL INSIGHTS**: Write like you know the company intimately. "Management's R&D reallocation toward AI indicates 2026 product cycle acceleration"
- **PROBABILISTIC THINKING**: Assign outcome probabilities. "75% chance of beating guidance by 5%+ given leading indicator trends"

**MAXIMUM INFORMATION DENSITY REQUIREMENTS:**
- **SYNTHESIS MASTERY**: Connect 3+ data points per insight. "Capex +40%, R&D +25%, and patent filings +60% signal product cycle acceleration beginning Q3 2025"
- **LAYERED ANALYSIS**: Multiple analytical lenses per paragraph. "Margin expansion (financial), market share gains (competitive), and customer satisfaction scores (operational) all confirm pricing power sustainability"
- **FORWARD-LOOKING SYNTHESIS**: Predict specific outcomes. "Current inventory build (+23% QoQ) + supplier contract renegotiations + automation phase 2 completion = 35% gross margin by Q2 2025"
- **BENCHMARKING SOPHISTICATION**: Multi-dimensional comparisons. "Trading at 0.8x vs historical 1.2x multiple, 0.7x vs peer average, but 1.1x vs growth-adjusted fair value"
- **RESOURCE ALLOCATION INTELLIGENCE**: Capital efficiency insights. "$500M capex generates $2.1B revenue capacity at 28% incremental margins = 84% IRR vs 15% cost of capital"
- **COMPRESSED INSIGHT DELIVERY**: Maximum insights per sentence. "Q3 beat (+8% vs consensus) driven by pricing (+5%), volume (+2%), and mix (+1%) validates our 3-factor expansion thesis"

**FINANCIAL INSIGHT REQUIREMENTS for {company_name} as of {datetime.now().strftime("%B %Y")}:
- **Slide 8**: Identify hidden earnings quality issues or sustainable competitive advantages buried in income statement
- **Slide 9**: Reveal balance sheet strengths/weaknesses that create option value or hidden risks consensus misses
- **Slide 10**: Uncover cash flow generation patterns that predict future capital allocation effectiveness
- **Slide 11**: Demonstrate superior ratio analysis that identifies competitive positioning trends before consensus
- **Slide 12**: Generate valuation insights using sophisticated methodologies that exploit market mispricing
- **Slide 13**: Assess risks using probability-weighted analysis that accounts for second-order effects
- **Slide 14**: Model scenarios that incorporate competitive responses and industry dynamics consensus ignores
- **Slide 15**: Synthesize financial analysis into actionable investment conclusion with specific alpha generation pathway

**🎯 MANDATORY KEY TAKEAWAYS SECTION (ALL SLIDES 8-15):**
Each slide from 8-15 MUST end with a "Key Takeaways" section containing 2-4 bullet points (flexible based on analysis depth) that distill the most important financial insights from that specific slide's content.

**Financial Key Takeaways Format:**
```html
<div class="key-takeaways-section">
    <h4 class="takeaways-header">Key Investment Takeaways</h4>
    <ul class="takeaways-list">
        <li class="takeaway-item">[Most important financial discovery from your analysis - include specific metrics and ratios]</li>
        <li class="takeaway-item">[Key competitive financial positioning insight - quantified vs peers with actual numbers]</li>
        <!-- Add more bullets ONLY if your analysis contains additional critical financial insights -->
    </ul>
</div>
```

**FLEXIBLE FINANCIAL TAKEAWAY GENERATION RULES:**
- **Analysis-Driven Quantity**: Generate 2-4 bullets based on the actual financial insights discovered in THIS slide
- **Slide-Specific Content**: Takeaways should only reflect the financial analysis performed on this particular slide
- **Metric-Rich**: Each bullet must include specific financial data, ratios, or percentages from your analysis
- **No Generic Fillers**: Don't add standard financial bullets just to reach a count
- **Investment-Focused**: Each takeaway should have clear implications for investment decisions

**Financial Bullet Point Requirements:**
- Each bullet point: 15-25 words maximum  
- MUST include specific financial metrics, ratios, or percentages from your analysis
- NO GENERIC FINANCIAL STATEMENTS: Avoid "strong balance sheet" or "healthy cash flow"
- COMPANY-SPECIFIC METRICS: Reference actual ROE, debt-to-equity, free cash flow margins, etc.
- ANALYSIS-DERIVED: Extract insights directly from the financial tables and analysis you wrote
- PEER-COMPARATIVE: Show how financial metrics compare to specific competitors with numbers

**EXAMPLES OF GOOD vs BAD TAKEAWAYS:**
❌ BAD: "Strong cash flow generation supports dividend growth"
✅ GOOD: "Frasers Logistics generates 95% cash-to-earnings conversion vs peer average of 78%, supporting 4% DPU growth"

❌ BAD: "Attractive valuation metrics indicate upside potential"  
✅ GOOD: "DCF fair value of $1.15 vs current $0.95 suggests 21% upside, driven by NOI recovery"

❌ BAD: "Solid balance sheet provides financial flexibility"
✅ GOOD: "Debt-to-assets ratio of 35% vs sector average 42% provides $800M additional borrowing capacity"

**QUANTITATIVE DIFFERENTIATION STANDARDS:**
- **Financial Forensics**: Uncover insights in financial statements that require deep analytical sophistication
- **Predictive Modeling**: Use financial trends to predict inflection points 2-3 quarters ahead of consensus
- **Quality Assessment**: Distinguish between accounting performance and true economic value creation
- **Complexity Premium**: Exploit valuation gaps created by financial statement complexity or business model sophistication

**MANDATORY SLIDE COMPLETION REQUIREMENTS:**
- MUST generate EXACTLY 8 slides: slides 8, 9, 10, 11, 12, 13, 14, AND 15
- Each slide MUST have complete financial analysis content
- SLIDE 15 MUST be complete with investment conclusion
- Each slide MUST have complete content - NO truncation allowed  
- Final slide MUST end with "Page 15 / 15" footer

**CRITICAL OUTPUT FORMAT REQUIREMENTS:**
- Output PURE HTML ONLY - NO markdown code blocks, NO **bold** markdown
- NO ```html tags, NO explanatory text, NO comments
- ALL emphasis must use <strong>text</strong> HTML tags, NEVER **text** markdown
- Start directly with <div class="slide report-prose" id="slide-financial-income-statement">
- End with slide 15's closing </div> tag (Page 15 / 15)
- Use exact CSS classes and structure shown in examples above
- GENERATE ALL 8 SLIDES COMPLETELY - DO NOT STOP EARLY

**🚨 CRITICAL: USE EXACT RATING "{{call1_rating}}" ON ALL SLIDES 8-15**
- Call 1 established the investment rating: **{{call1_rating}}**
- YOU MUST use "{{call1_rating}}" on EVERY single slide (8, 9, 10, 11, 12, 13, 14, 15)
- All financial analysis must SUPPORT the "{{call1_rating}}" investment conclusion
- ABSOLUTELY NO contradictory ratings - use "{{call1_rating}}" only

**🔥 ULTRA-HIGH INFORMATION DENSITY REQUIREMENTS:**

**SLIDES 12-14 CRITICAL ANALYTICAL CORE - MAXIMUM DENSITY:**
- **Slide 12 (DCF & Multiples)**: HIGHEST density - pack 3-4 valuation insights per paragraph, include 8-12 specific metrics, reference 4-6 peer comparisons with exact multiples
- **Slide 13 (Risk Analysis)**: Ultra-compressed risk assessment - 4-6 quantified risks with probability estimates, 3-4 scenario outcomes with specific price impacts  
- **Slide 14 (Bull/Bear Cases)**: Maximum scenario density - 6-8 bull factors, 6-8 bear factors, each with quantified earnings/price impact and probability weighting

**INFORMATION DENSITY STANDARDS:**
- **Slide 12**: Minimum 15 financial metrics per section, 6+ peer comparisons, 3+ valuation methodologies with specific price targets
- **Slide 13**: Minimum 8 quantified risk factors, 4+ scenario probabilities, 6+ specific impact measurements (earnings, cash flow, valuation)
- **Slide 14**: Minimum 12 bull/bear factors total, each with specific % impact on earnings/price, timeline for catalyst realization

**WRITING REQUIREMENTS - MAXIMUM EFFICIENCY:**
- Each analysis section: MAX 150-200 words but MINIMUM 8-10 specific data points per section
- Each subsection paragraph: MAX 400-500 words but MINIMUM 12-15 quantified insights per paragraph  
- Use <strong>key metrics</strong> and <strong>critical insights</strong> for emphasis
- Be punchy, direct, and impactful - eliminate unnecessary words
- Every sentence must add 2-3 specific value/data points minimum
- NO filler words, NO generic statements - pure analytical content only

**CRITICAL COMPLETION ENFORCEMENT:**
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
        
        
        # Format the prompt with actual company name and context variables
        try:
            # Escape any problematic characters in company name for string formatting
            safe_company_name = str(company_name).replace('{', '{{').replace('}', '}}') if '{' in str(company_name) or '}' in str(company_name) else company_name
            
            logger.info(f"🔍 DEBUG: Formatting Call 2 prompt with:")
            logger.info(f"  - company_name: '{safe_company_name}'")
            logger.info(f"  - user_context: {len(user_context)} chars")
            logger.info(f"  - financial_context: {len(financial_context)} chars")
            logger.info(f"  - analyst_insights: {len(analyst_insights)} chars")
            logger.info(f"  - call1_summary: {len(call1_summary)} chars")
            
            formatted_call2_prompt = complete_call2_prompt.format(
                company_name=safe_company_name,
                user_context=user_context,
                financial_context=financial_context,
                analyst_insights=analyst_insights,
                call1_summary=call1_summary,
                call1_rating=call1_context.get('investment_rating', 'NEUTRAL')
            )
            
            logger.info(f"✅ Call 2 prompt built: {len(formatted_call2_prompt):,} characters with pre-built HTML tables and context")
            logger.info(f"🔍 DEBUG: User context in Call 2 final prompt: {'user_context' not in formatted_call2_prompt}")
            return formatted_call2_prompt
        except KeyError as e:
            logger.error(f"❌ Formatting error in Call 2 prompt: {e}")
            logger.error(f"🔍 Looking for malformed placeholder: {e}")
            # Return unformatted prompt for debugging
            logger.info(f"✅ Call 2 prompt built (unformatted): {len(complete_call2_prompt):,} characters")
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
        
        # Get current date for dynamic prompts
        current_date = datetime.now().strftime("%B %d, %Y")
        current_month_year = datetime.now().strftime("%B %Y")
        
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
                
                # Configure for maximum comprehensive content generation with Google Search grounding
                generate_config = types.GenerateContentConfig(
                    temperature=1.2,  # Slightly higher for more detailed analysis
                    top_p=0.9,  # Good for comprehensive content generation
                    max_output_tokens=800000,  # ULTRA-MAXIMIZED for complete 15-slide template structure
                    response_mime_type="text/plain",
                    tools=[Tool(google_search=GoogleSearch())],  # Enable Google Search grounding
                    system_instruction=f"""You are a Managing Director at Robeco writing institutional-grade investment research as of {current_date}. 

🎯 DIFFERENTIATED ANALYSIS MANDATE: 
- Write PROPRIETARY insights that distinguish you from sell-side research
- Show DEEP company understanding that demonstrates superior analytical work
- Connect company STRATEGY directly to stock price implications
- Provide FORWARD-LOOKING fundamental analysis, not backward-looking summaries
- Demonstrate what you know that the market DOESN'T yet understand

📊 GOOGLE SEARCH REQUIREMENT - MANDATORY FOR ALL CLAIMS:
- EVERY financial metric must be Google Search verified as of {current_date}
- EVERY strategic development must be grounded with recent search data
- EVERY forward-looking statement must reference recent company guidance/earnings calls
- EVERY competitive analysis must use current market data via Google Search
- NO generic statements - ALL insights must be backed by real-time search verification

🔍 PM-LEVEL ANALYTICAL STANDARDS:
- Show how RECENT strategic initiatives will impact future cash flows
- Explain why current valuation is WRONG (mispriced) with specific evidence
- Identify second-order effects that consensus analysts miss
- Quantify probability-weighted scenarios with specific timelines
- Connect macro themes to company-specific competitive advantages
- Demonstrate pattern recognition from historical precedents

⚡ CONCRETE INSIGHTS REQUIRED:
- 'Company X's Q3 2024 margin expansion to 23.5% (vs consensus 21.8%) signals...'
- 'Based on management's Nov 2024 guidance, we forecast...'  
- 'Unlike consensus, we believe the new factory capacity will...'
- 'Historical analysis shows similar strategic pivots delivered...'

Determine CONSISTENT investment rating (OVERWEIGHT/NEUTRAL/UNDERWEIGHT) based on YOUR differentiated analysis and use SAME rating across ALL slides.

⚠️ CRITICAL FORMATTING RULES: 
- Use <strong>text</strong> for ALL emphasis - NEVER **text** markdown. Output PURE HTML ONLY.
- ALWAYS bold important numbers: <strong>+43.3%</strong>, <strong>S$1.18</strong>, <strong>96.7%</strong>
- ALWAYS bold key financial terms: <strong>DPU</strong>, <strong>EBITDA</strong>, <strong>P/B ratio</strong>
- ALWAYS bold company names, ratings, and crucial metrics for PM attention

🚨 FORBIDDEN FORMATTING:
- **bold text** (markdown) ❌
- `code blocks` (markdown) ❌  
- # Headers (markdown) ❌
- *italic text* (markdown) ❌

✅ REQUIRED FORMATTING:
- <strong>bold text</strong> (HTML) ✅
- <em>italic text</em> (HTML) ✅
- Proper HTML structure only ✅"""
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
                                        
                                # Check for incomplete slide 10 (more flexible detection)
                                if last_detected_slide == 10 and chunk_count > 200 and not any(pattern in accumulated_response for pattern in ["Page 11", "slide-financial-ratios", "11."]):
                                    logger.error(f"🚨 SLIDE 10 STUCK: No progress to slide 11 after {chunk_count} chunks!")
                            
                            # Send real-time streaming updates to frontend with DEBUG info
                            if websocket and connection_id:
                                try:
                                    progress = min(30 + (chunk_count * 2), 95)  # Cap at 95% until complete
                                    if contains_html_end:
                                        progress = 95  # Near completion when HTML end detected
                                    
                                    # Create message data first
                                    message_data = {
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
                                    }
                                    
                                    # Send the message using safe WebSocket method
                                    await self._send_websocket_safe(websocket, message_data)
                                    
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
                        # Note: API key management handled by external system
                        
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
                    
                    # Convert any leaked markdown formatting to proper HTML
                    cleaned_response = self._convert_markdown_to_html(accumulated_response)
                    
                    return cleaned_response
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
                
                # Send retry notification to frontend via WebSocket
                if websocket and connection_id:
                    try:
                        retry_message = {
                            "type": "report_generation_progress",
                            "data": {
                                "status": "retrying",
                                "message": f"⏳ API overloaded, retrying with different key (attempt {attempt+2}/{max_retries})...",
                                "retry_attempt": attempt + 2,
                                "max_retries": max_retries,
                                "connection_id": connection_id,
                                "timestamp": datetime.now().isoformat()
                            }
                        }
                        await self._send_websocket_safe(websocket, retry_message)
                        logger.info(f"📤 Sent retry notification to frontend: attempt {attempt+2}")
                    except Exception as ws_error:
                        logger.warning(f"⚠️ Could not send retry notification: {ws_error}")
                
                # Add a small delay before retry to avoid immediate rate limiting
                import asyncio
                await asyncio.sleep(2)
        
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
        Save the complete HTML report to Example Output directory
        
        Args:
            html_content: Complete HTML report content
            company_name: Company name for filename
            ticker: Stock ticker
            
        Returns:
            Path to saved file in src/robeco/Example Output/ directory
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
            
            # Save to the Example Output directory
            report_dir = Path(__file__).parent.parent / "Example Output"
            
            # Ensure the Example Output directory exists
            report_dir.mkdir(parents=True, exist_ok=True)
            
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
    
    def _build_complete_stock_data_with_chart(self, ticker: str, financial_data: Dict) -> Dict:
        """
        Pre-process ALL stock data, metrics, and chart components with final ready-to-use values.
        No more AI calculation needed - everything is pre-computed and formatted.
        """
        try:
            logger.info(f"🏗️ Pre-processing complete stock data for {ticker}")
            
            # Use consistent financial_data from server
            if financial_data and 'info' in financial_data:
                info = financial_data['info']
                logger.info(f"📊 Using pre-fetched yfinance data for complete processing")
            else:
                # Fallback: Fresh yfinance call
                import yfinance as yf
                stock = yf.Ticker(ticker)
                info = stock.info
                logger.warning(f"⚠️ Making fresh yfinance call for complete processing")
            
            # Get historical price data
            from datetime import datetime, timedelta
            import yfinance as yf
            stock = yf.Ticker(ticker)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=5*365)  # 5 years
            hist = stock.history(start=start_date, end=end_date, interval="1mo")
            
            if hist.empty:
                return {"error": "No historical data available", "chart_ready": False, "metrics_ready": False}
            
            # Extract price and date data
            prices = [round(float(row['Close']), 2) for _, row in hist.iterrows()]
            dates = [date.strftime('%Y-%m') for date, _ in hist.iterrows()]
            
            # Get basic info
            current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
            currency = info.get('currency', 'USD')
            exchange = info.get('exchange', 'Unknown')
            company_name = info.get('longName', ticker)
            
            # Format currency symbol
            if currency == 'SGD':
                curr_symbol = 'S$'
            elif currency == 'USD':
                curr_symbol = '$'
            elif currency == 'EUR':
                curr_symbol = '€'
            elif currency == 'GBP':
                curr_symbol = '£'
            elif currency == 'JPY':
                curr_symbol = '¥'
            else:
                curr_symbol = currency + ' '
            
            # Pre-calculate ALL 25 metrics with final formatting
            metrics = self._pre_calculate_all_metrics(info, curr_symbol, ticker, exchange)
            
            # Pre-calculate chart coordinates and SVG elements
            chart_elements = self._pre_calculate_chart_svg(prices, dates, curr_symbol, current_price)
            
            # Pre-calculate axis labels
            axis_labels = self._pre_calculate_axis_labels(prices, dates, curr_symbol)
            
            # Return everything pre-processed and ready
            complete_data = {
                # Status flags
                "chart_ready": True,
                "metrics_ready": True,
                "data_points": len(prices),
                
                # Basic info
                "company_name": company_name,
                "ticker": ticker,
                "currency": curr_symbol,
                "current_price": f"{curr_symbol}{current_price:.2f}",
                
                # Pre-calculated metrics (ready for direct substitution)
                "metrics": metrics,
                
                # Pre-calculated chart elements (ready SVG)
                "chart_svg": chart_elements["svg_content"],
                "chart_coordinates": chart_elements["coordinates"],
                "current_price_marker": chart_elements["price_marker"],
                
                # Pre-calculated axis labels
                "axis_labels": axis_labels,
                
                # Raw data for debugging
                "monthly_prices": prices,
                "dates": dates,
                "price_range": f"{curr_symbol}{min(prices):.2f} - {curr_symbol}{max(prices):.2f}",
                "total_return": f"{((current_price - prices[0]) / prices[0] * 100):+.1f}%" if prices else "0.0%"
            }
            
            logger.info(f"✅ Complete stock data pre-processed: {len(metrics)} metrics, {len(prices)} price points")
            return complete_data
            
        except Exception as e:
            logger.error(f"❌ Error pre-processing complete stock data: {e}")
            return {"error": str(e), "chart_ready": False, "metrics_ready": False}
    
    def _pre_calculate_all_metrics(self, info: Dict, curr_symbol: str, ticker: str, exchange: str) -> Dict[str, str]:
        """Pre-calculate all 25 metrics with final formatting - ready for direct use"""
        
        # Helper functions
        def format_number(value, is_currency=False):
            if value is None or value == 0:
                return "N/A"
            try:
                value = float(value)
                prefix = curr_symbol if is_currency else ""
                if abs(value) >= 1e12:
                    return f"{prefix}{value/1e12:.2f}T"
                elif abs(value) >= 1e9:
                    return f"{prefix}{value/1e9:.2f}B"
                elif abs(value) >= 1e6:
                    return f"{prefix}{value/1e6:.1f}M"
                elif abs(value) >= 1000:
                    return f"{prefix}{value/1000:.1f}K"
                else:
                    return f"{prefix}{value:.2f}"
            except:
                return "N/A"
        
        def format_percent(value, decimals=1):
            if value is None:
                return "N/A"
            try:
                return f"{float(value)*100:.{decimals}f}%" if value < 1 else f"{float(value):.{decimals}f}%"
            except:
                return "N/A"
        
        def format_ratio(value, decimals=2):
            if value is None:
                return "N/A"
            try:
                return f"{float(value):.{decimals}f}x"
            except:
                return "N/A"
        
        def format_range(low, high):
            if low is None or high is None:
                return "N/A"
            try:
                return f"{curr_symbol}{float(low):.2f} - {curr_symbol}{float(high):.2f}"
            except:
                return "N/A"
        
        # Pre-calculate all metrics
        current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
        
        return {
            # Row 1
            "MAIN_LISTING": f"{ticker}",
            "SHARE_PRICE": f"{curr_symbol}{current_price:.2f}",
            "MARKET_CAP": format_number(info.get('marketCap'), True),
            "ENTERPRISE_VALUE": format_number(info.get('enterpriseValue'), True),
            "52W_RANGE": format_range(info.get('fiftyTwoWeekLow'), info.get('fiftyTwoWeekHigh')),
            
            # Row 2
            "PE_RATIO": f"{format_ratio(info.get('trailingPE'))} / {format_ratio(info.get('forwardPE'))}",
            "EV_EBITDA": format_ratio(info.get('enterpriseToEbitda')),
            "PS_RATIO": format_ratio(info.get('priceToSalesTrailing12Months')),
            "PB_RATIO": format_ratio(info.get('priceToBook')),
            "PEG_RATIO": format_ratio(info.get('pegRatio')),
            
            # Row 3
            "MARGINS": f"{format_percent(info.get('grossMargins'))}/{format_percent(info.get('operatingMargins'))}/{format_percent(info.get('profitMargins'))}",
            "ROE": format_percent(info.get('returnOnEquity')),
            "ROA": format_percent(info.get('returnOnAssets')),
            "EBITDA_MARGIN": format_percent(info.get('ebitdaMargins')),
            "TARGET_RANGE": format_range(info.get('targetLowPrice'), info.get('targetHighPrice')),
            
            # Row 4
            "REV_GROWTH": format_percent(info.get('revenueGrowth')),
            "EPS_GROWTH": format_percent(info.get('earningsGrowth')),
            "BETA": format_ratio(info.get('beta'), 2),
            "DEBT_EQUITY": format_percent(info.get('debtToEquity')),
            "CURRENT_RATIO": format_ratio(info.get('currentRatio')),
            
            # Row 5
            "FCF": format_number(info.get('freeCashflow'), True),
            "QUICK_RATIO": format_ratio(info.get('quickRatio')),
            "DIV_YIELD": format_percent(info.get('dividendYield')),
            "PAYOUT_RATIO": format_ratio(info.get('payoutRatio')),
            "VOLUME": f"{format_number(info.get('averageVolume10days', 0)/1000000, False)}M / {format_number(info.get('averageVolume3months', 0)/1000000, False)}M"
        }
    
    def _pre_calculate_chart_svg(self, prices: list, dates: list, curr_symbol: str, current_price: float) -> Dict[str, str]:
        """Pre-calculate complete SVG chart with coordinates - ready for direct insertion"""
        
        if not prices or len(prices) < 2:
            return {
                "svg_content": "<text x='260' y='180' text-anchor='middle' fill='#666'>No price data available</text>",
                "coordinates": "",
                "price_marker": ""
            }
        
        # Calculate scaling with 10% padding
        min_price = min(prices)
        max_price = max(prices)
        y_min = min_price * 0.9
        y_max = max_price * 1.1
        
        # Calculate all coordinates
        coordinates = []
        for i, price in enumerate(prices):
            x = 60 + (i * 400 / len(prices))
            y = 320 - ((price - y_min) / (y_max - y_min) * 280)
            coordinates.append(f"{x:.1f},{y:.1f}")
        
        # Calculate current price marker position (last point)
        last_x = 60 + ((len(prices) - 1) * 400 / len(prices))
        last_y = 320 - ((current_price - y_min) / (y_max - y_min) * 280)
        
        return {
            "svg_content": f'<polyline points="{" ".join(coordinates)}" fill="none" stroke="#1976d2" stroke-width="3"/>',
            "coordinates": " ".join(coordinates),
            "price_marker": f'<circle cx="{last_x:.1f}" cy="{last_y:.1f}" r="5" fill="#E63946"/><text x="{last_x:.1f}" y="{last_y-15:.1f}" text-anchor="middle" font-size="12" fill="#E63946" font-weight="bold">{curr_symbol}{current_price:.2f}</text>'
        }
    
    def _pre_calculate_axis_labels(self, prices: list, dates: list, curr_symbol: str) -> Dict[str, str]:
        """Pre-calculate axis labels with actual values"""
        
        if not prices or not dates:
            return {
                "y_high": "N/A", "y_mid_high": "N/A", "y_mid": "N/A", "y_mid_low": "N/A", "y_low": "N/A",
                "x_start": "Start", "x_mid1": "Mid1", "x_mid2": "Mid2", "x_end": "End"
            }
        
        # Y-axis labels with 10% padding
        min_price = min(prices)
        max_price = max(prices)
        y_max = max_price * 1.1
        y_min = min_price * 0.9
        
        # X-axis labels based on actual dates
        x_start = dates[0][:4] if dates else "Start"
        x_mid1 = dates[len(dates)//3][:4] if len(dates) > 10 else "Mid1"
        x_mid2 = dates[len(dates)*2//3][:4] if len(dates) > 20 else "Mid2"
        x_end = dates[-1][:4] if dates else "End"
        
        return {
            "y_high": f"{curr_symbol}{y_max:.0f}",
            "y_mid_high": f"{curr_symbol}{max_price * 1.05:.0f}",
            "y_mid": f"{curr_symbol}{(max_price + min_price) / 2:.0f}",
            "y_mid_low": f"{curr_symbol}{min_price * 0.95:.0f}",
            "y_low": f"{curr_symbol}{y_min:.0f}",
            "x_start": x_start,
            "x_mid1": x_mid1,
            "x_mid2": x_mid2,
            "x_end": x_end
        }
    
    def _convert_markdown_to_html(self, content: str) -> str:
        """Convert leaked markdown formatting to proper HTML tags"""
        try:
            import re
            
            conversions_made = 0
            
            # Convert ***bold italic*** to <strong><em>bold italic</em></strong> (do this first)
            before_count = content.count('***')
            content = re.sub(r'\*\*\*(.*?)\*\*\*', r'<strong><em>\1</em></strong>', content)
            conversions_made += (before_count - content.count('***')) // 2
            
            # Convert **bold** to <strong>bold</strong>
            before_count = content.count('**')
            content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', content)
            conversions_made += (before_count - content.count('**')) // 2
            
            # Convert *italic* to <em>italic</em> (but avoid conflict with remaining asterisks)
            before_count = content.count('*')
            content = re.sub(r'(?<!\*)\*([^*\n]+?)\*(?!\*)', r'<em>\1</em>', content)
            italic_conversions = (before_count - content.count('*')) // 2
            conversions_made += italic_conversions
            
            # Convert # headers to h4 (if any leak through)
            header_matches = re.findall(r'^#{1,6}\s+(.+)$', content, re.MULTILINE)
            if header_matches:
                content = re.sub(r'^#{1,6}\s+(.+)$', r'<h4>\1</h4>', content, flags=re.MULTILINE)
                conversions_made += len(header_matches)
            
            # Convert - bullet points to proper list items (if any leak through)
            bullet_matches = re.findall(r'^\s*-\s+(.+)$', content, re.MULTILINE)
            if bullet_matches:
                content = re.sub(r'^\s*-\s+(.+)$', r'<li>\1</li>', content, flags=re.MULTILINE)
                # Wrap consecutive li items in ul tags
                content = re.sub(r'(<li>.*?</li>(?:\s*<li>.*?</li>)*)', r'<ul>\1</ul>', content, flags=re.DOTALL)
                conversions_made += len(bullet_matches)
            
            # Log if any conversions were made
            if conversions_made > 0:
                logger.info(f"🔧 Converted {conversions_made} markdown formatting patterns to HTML tags")
            
            return content
            
        except Exception as e:
            logger.warning(f"⚠️ Error converting markdown to HTML: {e}")
            return content  # Return original content if conversion fails


# Global instance
template_report_generator = RobecoTemplateReportGenerator()