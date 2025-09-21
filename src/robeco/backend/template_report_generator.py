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

- **Information Asymmetry Hunter**: Expert at finding insights hiding in plain sight that others overlook due to cognitive biases, complexity, or time horizons
- **Second-Order Thinking Master**: Understanding consequences of consequences - how today's trends create tomorrow's opportunities and risks that markets haven't priced
- **Pattern Recognition Virtuoso**: Identifying historical parallels, cycle analysis, and inflection points before they become obvious to consensus
- **Contrarian Positioning Expert**: Systematic frameworks for understanding why consensus is wrong and when contrarian positions offer asymmetric returns
- **Predictive Analytics Pioneer**: Building forward-looking models using leading indicators, management behavior analysis, and competitive intelligence
- **Capital Cycle Detective**: Understanding where companies are in their investment cycles and predicting capital allocation effectiveness
- **Technological Disruption Analyst**: Identifying second and third-order effects of emerging technologies on business models and competitive dynamics

**Your reputation**: Wall Street's most prescient mind, known for calling major inflection points 12-18 months before consensus, with a track record of generating 300+ basis points of annual alpha through differentiated insights.

🎯 **TARGET AUDIENCE - CIO WITH 30 YEARS STREET EXPERIENCE:**
Your analysis targets a Chief Investment Officer with 30 years on the Street who:
- **Understands everything** - needs NO basic explanations or obvious insights
- **Has NO TIME for fluff** - every sentence must deliver actionable intelligence  
- **Demands high info density** - more insights per word than any analyst they've read
- **Values only UNIQUE perspectives** - will instantly recognize recycled consensus thinking
- **Expects forward-looking analysis** - wants to know what happens NEXT, not what already happened
- **Requires conviction** - needs specific price targets, timeframes, and conviction levels

🚨 **ZERO TOLERANCE POLICY:**
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

**🔬 DEEP FUNDAMENTAL FORENSICS:**
- **Management Behavior Analysis**: Read between lines of management actions, capital allocation, and strategic messaging
- **Competitive Intelligence**: Understand competitive dynamics, market share shifts, and industry evolution better than consensus
- **Technology Impact Assessment**: Predict how emerging technologies will reshape business models and competitive moats
- **Regulatory Anticipation**: Forecast policy changes and their second/third-order effects on industry structure

**⚡ TIMING & CATALYST PRECISION:**
- **Earnings Inflection Points**: Predict when financial performance will surprise consensus based on leading indicators
- **Multiple Expansion/Compression**: Identify when valuation re-rating will occur and what will trigger it
- **Capital Cycle Positioning**: Understand where company and industry are in investment cycles for optimal entry/exit timing
- **Sentiment Reversal Timing**: Predict when negative/positive sentiment will reverse based on fundamental improvements

**Your analysis must answer: \"What do I know about {company_name}'s future that the market doesn't yet understand?\"**

### MANDATORY ANALYTICAL REQUIREMENTS:

**1. NON-CONSENSUS THESIS DEVELOPMENT:**
- **Contrarian Positioning**: Systematically identify why consensus view is fundamentally flawed or incomplete
- **Information Asymmetry Exploitation**: Leverage complexity, behavioral biases, or time horizon mismatches that create mispricings
- **Multi-Dimensional Alpha Sources**: Build thesis on 3-4 independent, uncorrelated value drivers that markets underestimate
- **Differentiated Insight**: Demonstrate differentiated understanding of business model, competitive dynamics, or industry evolution

**2. PREDICTIVE ANALYTICS FRAMEWORK:**
- **Leading Indicator Analysis**: Identify forward-looking metrics that predict earnings/multiple inflection points 6-12 months ahead
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

### 🔥 CRITICAL: DATA-DRIVEN ANALYTICAL MANDATES

**🔍 RESEARCH-BACKED ANALYSIS REQUIREMENTS:**
Every analysis point MUST be supported by:
- **Latest Company Research**: Reference recent analyst reports, management guidance, and industry research
- **Google Search Integration**: Use current news, earnings transcripts, industry reports, regulatory filings
- **Specific Data Points**: Cite exact numbers, percentages, dates, and quantified metrics
- **Source Attribution**: Reference where insights come from (earnings calls, research reports, industry data)
- **Comparative Analysis**: Compare to industry benchmarks, peer companies, and historical norms

**📈 STOCK PRICE MOVEMENT ATTRIBUTION (MANDATORY):**
For every major analytical point, you MUST address:
- **Historical Price Context**: Why did the stock move up/down in the past 12-24 months?
- **Fundamental Attribution**: What specific fundamental changes drove those price movements?
- **Market Reaction Analysis**: Why did the market react that way to specific events/earnings?
- **Mispricing Identification**: Where did the market overreact or underreact to fundamental changes?
- **Forward Price Implications**: How will future fundamental changes impact stock price trajectory?

**💡 DIFFERENTIATED VIEW REQUIREMENTS:**
Every section must demonstrate:
- **Consensus View Summary**: What does the street currently believe and why?
- **Your Contrarian Position**: How does your view differ from consensus and why?
- **Evidence for Differentiation**: What specific evidence supports your different view?
- **Timing Advantage**: Why will your view be proven right before consensus catches up?
- **Quantified Impact**: What specific financial/stock price impact will your differentiated view create?

**🎯 IMPLICATIONS-DRIVEN ANALYSIS:**
After every analytical statement, you MUST provide:
- **"So What?" Analysis**: What does this mean for future earnings, margins, competitive position?
- **Investment Implications**: How does this impact your investment thesis and price target?
- **Risk Assessment**: What could go wrong with this analysis and how do you mitigate it?
- **Timeline Specificity**: When will these implications become apparent to the market?
- **Portfolio Impact**: How does this affect position sizing and risk management?

**🔮 FORWARD-LOOKING MANDATE:**
Every analysis must include:
- **12-Month Outlook**: Specific predictions for the next 4 quarters with supporting logic
- **Catalyst Timeline**: Exact dates/events that will validate or invalidate your thesis
- **Scenario Planning**: Base/Bull/Bear cases with specific probability weightings
- **Market Recognition**: When and how will the market recognize your insights?
- **Exit Strategy**: Specific triggers for taking profits or cutting losses

**5. MULTI-DIMENSIONAL VALUATION:**
- **Dynamic DCF Modeling**: Incorporate optionality, competitive response functions, and non-linear growth trajectories
- **Sum-of-the-Parts with Synergies**: Value business segments independently while modeling cross-segment synergies
- **Real Options Valuation**: Quantify strategic flexibility, expansion options, and abandonment values
- **Through-the-Cycle Analysis**: Normalize for cyclical factors to assess sustainable earning power

**6. RISK-ADJUSTED IMPLEMENTATION:**
- **Position Sizing Optimization**: Use Kelly Criterion and risk parity concepts for optimal capital allocation
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
            <img src="[COMPANY_LOGO]" alt="Company Icon" class="icon">
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
        call1_specific = f"""
## ALPHA GENERATION PHASE 1: INVESTMENT FOUNDATION & MARKET INEFFICIENCY IDENTIFICATION (SLIDES 1-7)

### YOUR ELITE PM MANDATE FOR CALL 1:
As a top-tier hedge fund Portfolio Manager, your **first phase objective** is to establish the fundamental investment case that demonstrates **why this opportunity exists** and **why consensus is wrong**. You're not writing generic research—you're identifying specific market inefficiencies and mispricings that create asymmetric risk/reward profiles for sophisticated capital allocation.

**Your analytical depth must rival the best Renaissance Technologies or Bridgewater research.** Every insight should demonstrate the pattern recognition and multi-layered thinking that separates elite PMs from sell-side analysts.

### HTML STRUCTURE REQUIREMENTS - FOLLOW THESE PATTERNS:

**SLIDE 1 - EXECUTIVE SUMMARY & METRICS (analysis-item format):**

**Header Instructions:**
- Always use the exact Robeco logo URL: `https://images.ctfassets.net/tl4x668xzide/7mygwms2vuSwirnfvaCSvL/72d2bbd858a69aecbf59fd3fb8954484/robeco-logo-color.png`
- For company icons, use Clearbit format: `https://logo.clearbit.com/[company-domain].com` 
- Examples: `https://logo.clearbit.com/apple.com`, `https://logo.clearbit.com/microsoft.com`, `https://logo.clearbit.com/tesla.com`
- Fallback for any company: `https://placehold.co/30x30/005F90/ffffff?text=[TICKER]`
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
<!-- 🚨 CRITICAL INSTRUCTIONS:
1. Do NOT generate <style> tags - CSS is provided in template
2. ALL analysis must be company-specific and based on current fundamentals
3. INVESTMENT RATING must be determined by YOUR analysis - NOT hardcoded
4. Use Google Search to verify latest company data, earnings, analyst reports
5. Replace ALL placeholders with actual company-specific information
6. Rating must be CONSISTENT across ALL slides: OVERWEIGHT (green #2E7D32), NEUTRAL (orange #FF8C00), UNDERWEIGHT (red #C62828)
-->
<div class="slide" id="portrait-page-1">
    <header class="report-header-container">
        <div class="slide-logo" style="top: 85px;">
            <img src="https://images.ctfassets.net/tl4x668xzide/7mygwms2vuSwirnfvaCSvL/72d2bbd858a69aecbf59fd3fb8954484/robeco-logo-color.png" alt="Robeco Logo" style="height: 1.5rem;">
        </div>
        <div class="header-blue-border">
            <div class="company-header">
                <!-- INSTRUCTION: Replace with actual company domain (e.g., apple.com, microsoft.com) -->
                <!-- INSTRUCTION: Replace with company's main domain for logo. Use https://logo.clearbit.com/[COMPANY-DOMAIN].com format
                Examples: apple.com, microsoft.com, tesla.com, frasersproperty.com, etc. 
                Research the actual company domain from stock_data['company_name'] and use appropriate domain -->
                <img src="https://logo.clearbit.com/[COMPANY-DOMAIN].com" onerror="this.onerror=null;this.src='https://placehold.co/30x30/005F90/ffffff?text={ticker}';" alt="Company Icon" class="icon">
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
            [CREATE 4 analysis-item blocks with these EXACT titles and sophisticated PM-level focus areas - ALL Google Search verified as of {datetime.now().strftime("%B %Y")}:]
            
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
        <div class="slide-logo" style="top: 85px;">
            <img src="https://images.ctfassets.net/tl4x668xzide/7mygwms2vuSwirnfvaCSvL/72d2bbd858a69aecbf59fd3fb8954484/robeco-logo-color.png" alt="Robeco Logo" style="height: 1.5rem;">
        </div>
        <div class="header-blue-border">
            <div class="company-header">
                <!-- INSTRUCTION: Replace with actual company domain (e.g., apple.com, microsoft.com) -->
                <!-- INSTRUCTION: Replace with company's main domain for logo. Use https://logo.clearbit.com/[COMPANY-DOMAIN].com format
                Examples: apple.com, microsoft.com, tesla.com, frasersproperty.com, etc. 
                Research the actual company domain from stock_data['company_name'] and use appropriate domain -->
                <img src="https://logo.clearbit.com/[COMPANY-DOMAIN].com" onerror="this.onerror=null;this.src='https://placehold.co/30x30/005F90/ffffff?text={ticker}';" alt="Company Icon" class="icon">
                <h1 class="name"><!-- INSTRUCTION: Use the FULL OFFICIAL company name from stock_data['company_name'] NOT the user input. Example: "Daikin Industries, Ltd." not "DAKIN" --></h1>
                <!-- INSTRUCTION: Use CONSISTENT rating across ALL slides. Choose ONE: OVERWEIGHT (green #2E7D32), NEUTRAL (orange #FF8C00), or UNDERWEIGHT (red #C62828) -->
                <div class="rating" style="color: [RATING-COLOR];">[INVESTMENT-RATING]</div>
            </div>
        </div>
    </header>
    <main>
        <div class="analysis-sections">
            [CREATE 5 analysis-item blocks with these EXACT financial analysis categories and company-specific titles - ALL Google Search verified as of {datetime.now().strftime("%B %Y")}:]
            
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
        <div class="slide-logo" style="top: 85px;">
            <img src="https://images.ctfassets.net/tl4x668xzide/7mygwms2vuSwirnfvaCSvL/72d2bbd858a69aecbf59fd3fb8954484/robeco-logo-color.png" alt="Robeco Logo" style="height: 1.5rem;">
        </div>
        <div class="header-blue-border">
            <div class="company-header">
                <!-- INSTRUCTION: Replace with actual company domain (e.g., apple.com, microsoft.com) -->
                <!-- INSTRUCTION: Replace with company's main domain for logo. Use https://logo.clearbit.com/[COMPANY-DOMAIN].com format
                Examples: apple.com, microsoft.com, tesla.com, frasersproperty.com, etc. 
                Research the actual company domain from stock_data['company_name'] and use appropriate domain -->
                <img src="https://logo.clearbit.com/[COMPANY-DOMAIN].com" onerror="this.onerror=null;this.src='https://placehold.co/30x30/005F90/ffffff?text={ticker}';" alt="Company Icon" class="icon">
                <h1 class="name"><!-- INSTRUCTION: Use the FULL OFFICIAL company name from stock_data['company_name'] NOT the user input. Example: "Daikin Industries, Ltd." not "DAKIN" --></h1>
                <!-- INSTRUCTION: Use CONSISTENT rating across ALL slides. Choose ONE: OVERWEIGHT (green #2E7D32), NEUTRAL (orange #FF8C00), or UNDERWEIGHT (red #C62828) -->
                <div class="rating" style="color: [RATING-COLOR];">[INVESTMENT-RATING]</div>
            </div>
        </div>
    </header>
    <main class="report-prose">
        <h3>[Write a specific, insightful title that captures {company_name}'s unique investment highlights - what makes them a superior investment vs all alternatives? Focus on quantifiable competitive advantages that drive superior returns. Example: "TESLA'S VERTICAL INTEGRATION & BATTERY TECHNOLOGY MOAT" or "NVIDIA'S AI CHIP ARCHITECTURE DOMINANCE" - avoid generic titles]</h3>
        
        <h4>[Identify the #1 investment strength and write a subsection title that shows HOW this creates economic value. Think like a PM: what specific mechanism drives superior margins/growth/returns? Example: "Ecosystem Lock-in Strategy: 95% Customer Retention Drives 40% Gross Margins" or "Platform Network Effects: 70% Market Share Expansion"]</h4>
        <p>[Write 400-500 words with ELITE-LEVEL ANALYTICAL DEPTH that demonstrates differentiated insights. MANDATORY STRUCTURE: 1) CONSENSUS MISTAKE: Start by identifying what consensus gets wrong about this strength (e.g., "Street underestimates network effects, modeling linear growth when data shows exponential adoption curves") 2) YOUR DIFFERENTIATED VIEW: Present your contrarian position with specific evidence (e.g., "Our differentiated NPS tracking shows 85% customer satisfaction vs 60% industry average, indicating pricing power expansion") 3) HISTORICAL ATTRIBUTION: Explain how this strength drove past stock performance (e.g., "This moat enabled 300bps margin expansion during 2022-23 downturn while peers contracted") 4) QUANTIFIED IMPACT: Use specific metrics and peer comparisons with sources (e.g., "Based on latest earnings call, management guidance suggests this will drive $2.5B incremental revenue by 2025") 5) FORWARD CATALYSTS: Identify specific events in next 12 months that will prove your thesis (e.g., "Q3 product launch will demonstrate 40% faster implementation vs legacy solutions") 6) INVESTMENT IMPLICATION: Exact impact on price target and timeline (e.g., "This justifies 25x multiple vs 18x peer average, driving $15/share upside by year-end"). Each paragraph must include research citations and answer "So what for stock price?" Show sophisticated understanding of business model economics and competitive dynamics.]</p>
        
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
        <div class="slide-logo" style="top: 85px;">
            <img src="https://images.ctfassets.net/tl4x668xzide/7mygwms2vuSwirnfvaCSvL/72d2bbd858a69aecbf59fd3fb8954484/robeco-logo-color.png" alt="Robeco Logo" style="height: 1.5rem;">
        </div>
        <div class="header-blue-border">
            <div class="company-header">
                <!-- INSTRUCTION: Replace with actual company domain (e.g., apple.com, microsoft.com) -->
                <!-- INSTRUCTION: Replace with company's main domain for logo. Use https://logo.clearbit.com/[COMPANY-DOMAIN].com format
                Examples: apple.com, microsoft.com, tesla.com, frasersproperty.com, etc. 
                Research the actual company domain from stock_data['company_name'] and use appropriate domain -->
                <img src="https://logo.clearbit.com/[COMPANY-DOMAIN].com" onerror="this.onerror=null;this.src='https://placehold.co/30x30/005F90/ffffff?text={ticker}';" alt="Company Icon" class="icon">
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
        - What fundamental changes moved {company_name}'s stock +/- 20% in past 3 years?
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
    <header class="report-header-container">[Same header structure as slide 1 - copy exactly]</header>
    <main class="report-prose">
        <h3>[Create a title that demonstrates deep understanding of {company_name}'s business model and what drives its competitive advantage. Focus on the core economic engine. Example: "APPLE'S HARDWARE-SOFTWARE INTEGRATION ADVANTAGE" or "AMAZON'S LOGISTICS & DATA FLYWHEEL DOMINANCE"]</h3>
        
        <h4>[Business model analysis focused on economic moats and value creation mechanisms]</h4>
        <p>[Write 400-500 words like a sophisticated investor who understands business model economics. Focus on: 1) Core value proposition and how it creates customer stickiness 2) Unit economics and scalability factors 3) Network effects, switching costs, or scale advantages 4) Capital efficiency and return on invested capital drivers 5) Business model evolution and expansion opportunities. Use specific metrics like customer lifetime value, acquisition costs, churn rates, market share data. Show you understand what makes this business model superior to alternatives and how it translates to sustainable competitive advantage.]</p>
        
        <h4>[Operational excellence and execution capabilities]</h4>
        <p>[400-500 words analyzing management quality, operational efficiency, and execution track record]</p>
        
        <h4>[Financial model durability and cash generation profile]</h4>
        <p>[400-500 words demonstrating sophisticated understanding of cash flow dynamics and capital allocation]</p>
        
        <h4>[Strategic positioning and market opportunity expansion]</h4>
        <p>[400-500 words showing advanced analysis of addressable markets and growth vectors]</p>
    </main>
    <footer class="report-footer"><p>Robeco Investment Research</p><p>Page 5 / 15</p></footer>
</div>

<div class="slide report-prose" id="slide-industry-analysis">
    <header class="report-header-container">[Same header structure as slide 1 - copy exactly]</header>
    <main>
        <h3>[Create an industry-focused title that shows deep sector expertise and identifies key themes driving sector performance. Example: "CONSUMER ELECTRONICS: AI-DRIVEN UPGRADE SUPERCYCLE" or "CLOUD SOFTWARE: ENTERPRISE AI TRANSFORMATION ACCELERATING"]</h3>
        
        <p><strong>[Write a section header that identifies the key market transformation theme]</strong></p>
        <p>[Write 500-600 words like a sector specialist PM who understands industry dynamics better than generalists. Focus on: 1) Market size evolution and growth drivers with specific TAM data 2) Industry structural changes and disruption patterns 3) Key technology/regulatory/demographic trends reshaping the industry 4) Margin and profitability trends across the value chain 5) Capital allocation patterns and consolidation dynamics. Use industry-specific metrics, market research data, and forward-looking analysis. Show you understand where the industry is in its cycle and what drives outperformance.]</p>
        
        <p><strong>[Write a section header focusing on competitive landscape and market structure]</strong></p>
        <p>[Write 500-600 words demonstrating sophisticated understanding of competitive dynamics, market share trends, barriers to entry, and pricing power evolution. Include analysis of key players, competitive positioning, and how market structure is evolving.]</p>
        
        <p><strong>[Write a section header on industry investment implications and sector allocation]</strong></p>
        <p>[Write 500-600 words connecting industry analysis to investment strategy, showing how sector themes drive stock selection and portfolio positioning.]</p>
    </main>
    <footer class="report-footer"><p>Robeco Investment Research</p><p>Page 6 / 15</p></footer>
</div>

<div class="slide report-prose" id="slide-competitive-advantage">
    <header class="report-header-container">[Same header structure as slide 1 - copy exactly]</header>
    <main>
        <h3>[Create a title focused on sustainable competitive advantages and economic moats. Show what makes {company_name} defensible long-term. Example: "ECOSYSTEM MOAT & PREMIUM PRICING POWER" or "SCALE ADVANTAGES & TECHNOLOGICAL DIFFERENTIATION"]</h3>
        
        <h4 style="font-size: 22.5px; color: var(--robeco-blue-darker);">[Write a subsection title that quantifies market position and competitive standing with specific metrics. Example: "Market Leadership: 55% Global Premium Smartphone Share" or "Technology Moat: 3-Year R&D Lead vs Competitors"]</h4>
        <p>[Write 500-600 words like a PM who understands what creates sustainable competitive advantage. Focus on: 1) Quantified market position with specific share, customer, and financial metrics vs peers 2) Competitive dynamics and how they're evolving 3) Barriers to entry and switching costs 4) Scale/network effects that strengthen over time 5) Innovation capabilities and R&D effectiveness. Use competitive intelligence, patent analysis, customer survey data, market research. Show you understand Porter's Five Forces and how {company_name} wins structurally.]</p>
        
        <h4 style="font-size: 22.5px; color: var(--robeco-blue-darker);">[Write a subsection title focused on sustainable business model advantages and economic moats]</h4>
        <p>[Write 500-600 words demonstrating deep understanding of what makes competitive advantages sustainable vs temporary, including analysis of moat durability, competitive responses, and long-term defensibility.]</p>
        
        <h4 style="font-size: 22.5px; color: var(--robeco-blue-darker);">[Write a subsection title on competitive threats and defensive strategies]</h4>
        <p>[Write 500-600 words showing sophisticated analysis of competitive risks and how {company_name} maintains its advantages over time.]</p>
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

**SLIDE 3 - INVESTMENT HIGHLIGHTS (4 subsections):**
- **H3 Title**: Create compelling title like "3. {company_name} INVESTMENT HIGHLIGHTS" but make it specific to {company_name}'s unique strengths
- **Subsection Titles - MAKE THEM INSIGHTFUL & SPECIFIC:**
  - **Subsection 1**: Identify {company_name}'s PRIMARY competitive moat and create a title that captures it specifically (e.g., "Tesla's Vertical Integration & Battery Technology Moat", "Apple's Ecosystem Lock-in & Premium Brand Power")
  - **Subsection 2**: Identify {company_name}'s BIGGEST market opportunity and create a specific title (e.g., "Amazon's Cloud Dominance in $500B+ Market", "NVIDIA's AI Chip Leadership in Trillion-Dollar Transformation")
  - **Subsection 3**: Identify {company_name}'s STRONGEST operational advantage and create a specific title (e.g., "Costco's Membership Model & Supply Chain Efficiency", "Microsoft's Subscription Revenue & Margin Expansion")
  - **Subsection 4**: Identify {company_name}'s FUTURE value creation potential and create a specific title (e.g., "Google's AI Leadership & Search Evolution", "Berkshire's Capital Allocation & Insurance Float")
- **TITLE PRINCIPLES**: Titles must immediately convey the specific insight, use quantifiable elements when possible, and make readers want to read more
- **Format**: Each subsection starts with insightful H4 title and 500-600 word analysis paragraph

**SLIDE 4 - CATALYSTS AND RECENT DEVELOPMENTS (4 subsections):**
- **H3 Title**: Create specific title focusing on {company_name}'s KEY catalysts (e.g., "4. TESLA'S AUTONOMOUS DRIVING & CHINA EXPANSION CATALYSTS", "4. APPLE'S AI INTEGRATION & SERVICES MOMENTUM")
- **Subsection Titles - IDENTIFY SPECIFIC CATALYSTS:**
  - **Subsection 1**: Near-term catalyst with SPECIFIC event and timeline (e.g., "Q4 2024 Model 3 Highland Launch in Europe", "iPhone 16 AI Features Driving Upgrade Cycle")
  - **Subsection 2**: Product/pipeline catalyst with SPECIFIC innovation (e.g., "ChatGPT-5 Launch & Enterprise Adoption", "AWS Graviton Chips & AI Infrastructure")
  - **Subsection 3**: Management/strategic catalyst with SPECIFIC initiative (e.g., "Elon's $44B Twitter Integration Strategy", "Cook's Services Revenue Target of $100B")
  - **Subsection 4**: Market expansion catalyst with SPECIFIC geography/segment (e.g., "India Manufacturing & $25K Model Target", "Vision Pro Enterprise Market Penetration")
- **CATALYST PRINCIPLES**: Each title must specify the exact catalyst, include timing/quantification, and convey why it matters
- **Format**: Each subsection starts with specific H4 title and 500-600 word analysis paragraph

**SLIDE 5 - COMPANY ANALYSIS (6 subsections):**
- **H3 Title**: Create business model-focused title (e.g., "5. APPLE'S ECOSYSTEM FLYWHEEL & SERVICES TRANSFORMATION", "5. AMAZON'S THREE-PILLAR DOMINANCE MODEL")
- **Subsection Titles - ANALYZE SPECIFIC BUSINESS FUNDAMENTALS:**
  - **Subsection 1**: Core business analysis with SPECIFIC revenue mix (e.g., "iPhone Hardware: 52% Revenue Driving Services Adoption", "AWS: 70% Operating Income from 16% Revenue")
  - **Subsection 2**: Revenue diversification with SPECIFIC geographic/segment data (e.g., "China 19% Revenue Despite Regulatory Headwinds", "International: 60% Revenue Growth Acceleration")
  - **Subsection 3**: Operational excellence with SPECIFIC metrics (e.g., "38% Gross Margins vs 22% Industry Average", "Free Cash Flow Conversion: 95% vs Industry 60%")
  - **Subsection 4**: Management track record with SPECIFIC achievements (e.g., "Cook's 10-Year $2.9T Value Creation Record", "Bezos-to-Jassy Transition Success")
  - **Subsection 5**: Competitive position with SPECIFIC market data (e.g., "15% Global Smartphone Share, 50% Profit Share", "40% Cloud Infrastructure Market Leadership")
  - **Subsection 6**: Strategic outlook with SPECIFIC initiatives (e.g., "Vision Pro: $10B+ Spatial Computing Opportunity", "AI Integration Across Product Suite")
- **ANALYSIS PRINCIPLES**: Use actual company data, specific market positioning, and quantified competitive advantages
- **Format**: Each subsection starts with data-driven H4 title and 500-600 word analysis paragraph

**SLIDE 6 - SECTOR ANALYSIS:**
- **H3 Title**: Create industry-specific insight title (e.g., "6. SEMICONDUCTOR CAPITAL INTENSITY: AI CHIP SHORTAGE DRIVES PRICING POWER", "6. CLOUD INFRASTRUCTURE: ENTERPRISE MIGRATION ACCELERATING POST-COVID")
- **Content Sections - IDENTIFY KEY INDUSTRY DYNAMICS:**
  - **Section 1**: Market size and growth with specific data (e.g., "Global Cloud Market: $500B by 2025, 15% CAGR")
  - **Section 2**: Competitive landscape with specific player analysis (e.g., "Big 3 Cloud Players Control 65% Market Share")
  - **Section 3**: Regulatory/technology trends affecting the industry (e.g., "AI Regulation Timeline & Data Privacy Impact")
  - **Section 4**: Industry value chain and profit pools (e.g., "Where Margins Are Highest: Software vs Hardware")
- **SECTOR PRINCIPLES**: Use specific market data, identify unique industry dynamics, and explain how they benefit/threaten {company_name}
- **Format**: Multiple paragraphs with **bold section headers** and 600-word detailed analysis

**SLIDE 7 - COMPETITIVE ADVANTAGE:**
- **H3 Title**: Create moat-specific title (e.g., "7. APPLE'S ECOSYSTEM LOCK-IN: $2T SWITCHING COST BARRIER", "7. AMAZON'S SCALE ECONOMICS: FULFILLMENT NETWORK MOAT")
- **Content Sections - ANALYZE SPECIFIC COMPETITIVE MOATS:**
  - **Section 1**: Primary competitive advantage with quantification (e.g., "Brand Premium: 40% Higher ASPs vs Android")
  - **Section 2**: Barriers to entry analysis (e.g., "R&D Spending: $30B vs Competitor Average $5B")
  - **Section 3**: Network effects or scale advantages (e.g., "App Store: 1.8B Users Create Developer Flywheel")
  - **Section 4**: Sustainability of advantage (e.g., "Patent Portfolio & Manufacturing Partnerships")
- **MOAT PRINCIPLES**: Quantify the competitive advantage, explain sustainability, and show why competitors can't replicate
- **Format**: Multiple H4 subsections with 600-word analysis each

**CRITICAL TITLE GENERATION PRINCIPLES:**
- **NO GENERIC PLACEHOLDERS**: Never use "[COMPANY] INVESTMENT HIGHLIGHTS" - always create specific, insightful titles
- **CAPTURE THE INSIGHT**: Titles must immediately convey the unique investment thesis (e.g., "TESLA'S VERTICAL INTEGRATION: BATTERY-TO-SOFTWARE DOMINANCE")
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

**🔍 PROPRIETARY INSIGHT GENERATION (What Others Miss):**
- **Hidden Inflection Points**: Identify business model changes, competitive shifts, or technology adoptions occurring beneath surface that will drive 12-18 month performance
- **Management Behavior Decoding**: Analyze subtle changes in capital allocation, strategic messaging, or operational focus that signal future direction before consensus recognizes
- **Competitive Intelligence Advantage**: Understand market share dynamics, pricing power evolution, and competitive response functions that aren't captured in public data
- **Second-Order Technology Effects**: Predict how emerging technologies will create/destroy value in ways that aren't immediately obvious

**🎯 NON-CONSENSUS POSITIONING FRAMEWORKS:**
- **Consensus Deconstruction**: Systematically identify why current analyst estimates, valuation metrics, or market sentiment are systematically wrong
- **Complexity Arbitrage**: Exploit situations where business model complexity, accounting complexity, or industry evolution create analytical barriers for consensus
- **Time Horizon Arbitrage**: Identify long-term value creation stories temporarily obscured by short-term noise or cyclical headwinds
- **Behavioral Finance Exploitation**: Leverage recency bias, anchoring effects, or sector rotation patterns that create temporary mispricings

**⚡ PREDICTIVE ANALYTICS MASTERY:**
- **Leading Indicator Development**: Identify forward-looking metrics (KPIs, competitive data, technology adoption) that predict earnings inflection points 2-3 quarters ahead
- **Pattern Recognition Application**: Apply historical parallels from similar companies, industries, or market cycles to predict likely future trajectories
- **Catalyst Probability Weighting**: Assess likelihood and timing of specific catalysts using base rates, management track records, and industry precedents
- **Inflection Point Timing**: Predict when current trends will accelerate, plateau, or reverse based on fundamental analysis

**🚀 FUTURE STATE VISUALIZATION:**
- **Business Model Evolution**: Predict how {company_name}'s business model will evolve over 3-5 years based on current strategic initiatives and industry trends
- **Competitive Positioning Forecast**: Anticipate how competitive dynamics will shift and where {company_name} will be positioned
- **Technology Disruption Assessment**: Evaluate whether emerging technologies represent threats or opportunities for long-term competitive positioning
- **Capital Allocation Optimization**: Predict how management will allocate capital and the returns on that allocation based on historical patterns and current priorities

**🧠 SOPHISTICATED THESIS ARCHITECTURE:**
- **Multi-Layer Value Creation**: Identify 3-4 independent value drivers operating on different time horizons that compound to create asymmetric returns
- **Option Value Recognition**: Quantify hidden optionality in business model flexibility, strategic assets, or expansion opportunities
- **Moat Evolution Analysis**: Predict how competitive advantages will strengthen/weaken over time and what management is doing to reinforce them
- **Quality of Growth Assessment**: Distinguish between revenue growth and profitable, sustainable, capital-efficient growth that creates long-term value

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
- **Slide 1**: Identify the primary market mispricing and why consensus is systematically wrong
- **Slide 2**: Highlight 5 specific insights that demonstrate superior analytical depth vs. sell-side research
- **Slide 3**: Reveal competitive advantages or market opportunities that others miss or underestimate
- **Slide 4**: Predict specific catalysts and their timing that consensus hasn't properly analyzed
- **Slide 5**: Demonstrate understanding of business model evolution that exceeds public company guidance
- **Slide 6**: Identify industry dynamics and second-order effects that create hidden value
- **Slide 7**: Quantify sustainable competitive advantages that others treat as commoditized

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
        
        # THEN: Format the prompt with company name
        try:
            # Escape any problematic characters in company name for string formatting
            safe_company_name = str(company_name).replace('{', '{{').replace('}', '}}') if '{' in str(company_name) or '}' in str(company_name) else company_name
            # Replace {company_name} in the prompt that already has metrics replaced
            formatted_final = complete_call1_prompt_with_metrics.format(company_name=safe_company_name)
            
            logger.info(f"✅ Call 1 prompt built: {len(formatted_final):,} characters with real metrics")
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
As an elite Portfolio Manager writing in {datetime.now().strftime("%B %Y")}, your **second phase objective** is to provide rigorous quantitative validation of the Phase 1 investment thesis through sophisticated financial analysis and multi-methodology valuation. You're applying the same analytical rigor that generates consistent alpha at the world's top hedge funds.

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

🏢 HEADER INSTRUCTIONS:
- Always use the exact Robeco logo URL: https://images.ctfassets.net/tl4x668xzide/7mygwms2vuSwirnfvaCSvL/72d2bbd858a69aecbf59fd3fb8954484/robeco-logo-color.png
- For company icons, use Clearbit format: https://logo.clearbit.com/[company-domain].com
- Examples: https://logo.clearbit.com/apple.com, https://logo.clearbit.com/microsoft.com, https://logo.clearbit.com/tesla.com
- Fallback for any company: https://placehold.co/30x30/005F90/ffffff?text=[TICKER]
- Use actual company name (not placeholder) and determine rating based on your analysis
-->
<div class="slide report-prose" id="slide-financial-income-statement">
    <div class="slide-logo" style="top: 85px;">
        <img src="https://images.ctfassets.net/tl4x668xzide/7mygwms2vuSwirnfvaCSvL/72d2bbd858a69aecbf59fd3fb8954484/robeco-logo-color.png" alt="Robeco Logo" style="height: 1.5rem;">
    </div>
    <header class="report-header-container">
        <div class="header-blue-border">
            <div class="company-header">
                <!-- INSTRUCTION: Replace with actual company domain (e.g., apple.com, microsoft.com) -->
                <!-- INSTRUCTION: Replace with company's main domain for logo. Use https://logo.clearbit.com/[COMPANY-DOMAIN].com format
                Examples: apple.com, microsoft.com, tesla.com, frasersproperty.com, etc. 
                Research the actual company domain from stock_data['company_name'] and use appropriate domain -->
                <img src="https://logo.clearbit.com/[COMPANY-DOMAIN].com" onerror="this.onerror=null;this.src='https://placehold.co/30x30/005F90/ffffff?text={ticker}';" alt="Company Icon" class="icon">
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
    <div class="slide-logo" style="top: 85px;">
        <img src="https://images.ctfassets.net/tl4x668xzide/7mygwms2vuSwirnfvaCSvL/72d2bbd858a69aecbf59fd3fb8954484/robeco-logo-color.png" alt="Robeco Logo" style="height: 1.5rem;">
    </div>
    <header class="report-header-container">
        <div class="header-blue-border">
            <div class="company-header">
                <!-- INSTRUCTION: Replace with actual company domain (e.g., apple.com, microsoft.com) -->
                <!-- INSTRUCTION: Replace with company's main domain for logo. Use https://logo.clearbit.com/[COMPANY-DOMAIN].com format
                Examples: apple.com, microsoft.com, tesla.com, frasersproperty.com, etc. 
                Research the actual company domain from stock_data['company_name'] and use appropriate domain -->
                <img src="https://logo.clearbit.com/[COMPANY-DOMAIN].com" onerror="this.onerror=null;this.src='https://placehold.co/30x30/005F90/ffffff?text={ticker}';" alt="Company Icon" class="icon">
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
    <div class="slide-logo" style="top: 85px;">
        <img src="https://images.ctfassets.net/tl4x668xzide/7mygwms2vuSwirnfvaCSvL/72d2bbd858a69aecbf59fd3fb8954484/robeco-logo-color.png" alt="Robeco Logo" style="height: 1.5rem;">
    </div>
    <header class="report-header-container">
        <div class="header-blue-border">
            <div class="company-header">
                <!-- INSTRUCTION: Replace with actual company domain (e.g., apple.com, microsoft.com) -->
                <!-- INSTRUCTION: Replace with company's main domain for logo. Use https://logo.clearbit.com/[COMPANY-DOMAIN].com format
                Examples: apple.com, microsoft.com, tesla.com, frasersproperty.com, etc. 
                Research the actual company domain from stock_data['company_name'] and use appropriate domain -->
                <img src="https://logo.clearbit.com/[COMPANY-DOMAIN].com" onerror="this.onerror=null;this.src='https://placehold.co/30x30/005F90/ffffff?text={ticker}';" alt="Company Icon" class="icon">
                <h1 class="name"><!-- INSTRUCTION: Use the FULL OFFICIAL company name from stock_data['company_name'] NOT the user input. Example: "Daikin Industries, Ltd." not "DAKIN" --></h1>
                <!-- INSTRUCTION: Use CONSISTENT rating across ALL slides. Choose ONE: OVERWEIGHT (green #2E7D32), NEUTRAL (orange #FF8C00), or UNDERWEIGHT (red #C62828) -->
                <div class="rating" style="color: [RATING-COLOR];">[INVESTMENT-RATING]</div>
            </div>
        </div>
    </header>
    <main>
        <h3>[Create a title highlighting the key cash flow insight that validates your investment thesis. Think like a PM focused on cash generation quality and sustainability. Examples: "EXCEPTIONAL FCF CONVERSION: 95% OF NET INCOME TO FREE CASH FLOW" or "CAPEX EFFICIENCY: GROWTH WITH MINIMAL CAPITAL INTENSITY" or "CASH GENERATION ACCELERATION: WORKING CAPITAL IMPROVEMENTS"]</h3>
        
        [COPY THE COMPLETE CASH FLOW TABLE FROM ABOVE - DON'T GENERATE NEW TABLES]
        
        <p><strong>[Write a section header that identifies the quality and sustainability of operating cash flow generation]</strong></p>
        <p>[Write 400-500 words like a PM evaluating cash flow quality for investment decision-making. Focus on: 1) Operating cash flow quality - cash vs non-cash earnings, working capital impacts, seasonality patterns, collection efficiency 2) Free cash flow analysis - capex requirements, maintenance vs growth capex, asset intensity, cash conversion cycles 3) Cash flow sustainability - predictability, cyclicality, margin of safety, through-cycle analysis 4) Capital allocation analysis - reinvestment needs, dividend coverage, buyback capacity, acquisition funding 5) Investment implications - how cash generation supports valuation models, dividend growth, balance sheet strength. Reference specific numbers from the table and analyze cash flow trends vs peers. Show understanding of what separates high-quality cash generators from earnings manipulators.]</p>
        
        <p><strong>[Write a section header on capital efficiency and free cash flow yield analysis]</strong></p>
        <p>[Write 400-500 words demonstrating advanced understanding of cash flow-based valuation, capital intensity analysis, and how cash generation patterns support your investment thesis.]</p>
    </main>
    <footer class="report-footer"><p>Robeco Investment Research</p><p>Page 10 / 15</p></footer>
</div>

<div class="slide report-prose" id="slide-financial-ratios">
    <div class="slide-logo" style="top: 85px;">
        <img src="https://images.ctfassets.net/tl4x668xzide/7mygwms2vuSwirnfvaCSvL/72d2bbd858a69aecbf59fd3fb8954484/robeco-logo-color.png" alt="Robeco Logo" style="height: 1.5rem;">
    </div>
    <header class="report-header-container">
        <div class="header-blue-border">
            <div class="company-header">
                <!-- INSTRUCTION: Replace with actual company domain (e.g., apple.com, microsoft.com) -->
                <!-- INSTRUCTION: Replace with company's main domain for logo. Use https://logo.clearbit.com/[COMPANY-DOMAIN].com format
                Examples: apple.com, microsoft.com, tesla.com, frasersproperty.com, etc. 
                Research the actual company domain from stock_data['company_name'] and use appropriate domain -->
                <img src="https://logo.clearbit.com/[COMPANY-DOMAIN].com" onerror="this.onerror=null;this.src='https://placehold.co/30x30/005F90/ffffff?text={ticker}';" alt="Company Icon" class="icon">
                <h1 class="name"><!-- INSTRUCTION: Use the FULL OFFICIAL company name from stock_data['company_name'] NOT the user input. Example: "Daikin Industries, Ltd." not "DAKIN" --></h1>
                <!-- INSTRUCTION: Use CONSISTENT rating across ALL slides. Choose ONE: OVERWEIGHT (green #2E7D32), NEUTRAL (orange #FF8C00), or UNDERWEIGHT (red #C62828) -->
                <div class="rating" style="color: [RATING-COLOR];">[INVESTMENT-RATING]</div>
            </div>
        </div>
    </header>
    <main>
        <h3>[Create a title that shows sophisticated ratio analysis and competitive benchmarking. Think like a PM demonstrating superior analytical insight. Examples: "SUPERIOR CAPITAL EFFICIENCY: 25% ROE VS INDUSTRY 12% AVERAGE" or "MARGIN EXPANSION OPPORTUNITY: PATH TO INDUSTRY-LEADING PROFITABILITY" or "ASSET TURNOVER LEADERSHIP: OPERATIONAL EFFICIENCY DRIVES RETURNS"]</h3>
        
        <p><strong>[Write a section header focusing on profitability ratios and peer comparison analysis]</strong></p>
        <p>[Write 400-500 words like a PM conducting sophisticated ratio analysis for portfolio construction. Focus on: 1) Profitability analysis - ROE decomposition (margin x turnover x leverage), ROI trends, ROIC vs WACC analysis, peer benchmarking 2) Quality metrics - gross margin stability, EBITDA margin expansion, operating leverage measurement 3) Efficiency ratios - asset turnover, working capital management, inventory turnover, receivables quality 4) Trend analysis - 3-5 year ratio evolution, cyclical adjustments, normalized earnings power 5) Investment implications - how ratio analysis supports valuation premium/discount, identifies operational improvements, predicts mean reversion. Use industry-specific ratios and benchmarks. Show understanding of what ratios matter most for this business model and industry.]</p>
        
        <p><strong>[Write a section header on capital allocation efficiency and shareholder return metrics]</strong></p>
        <p>[Write 400-500 words demonstrating advanced understanding of capital efficiency metrics, management effectiveness in deploying capital, and how this translates to superior shareholder returns vs alternatives.]</p>
    </main>
    <footer class="report-footer"><p>Robeco Investment Research</p><p>Page 11 / 15</p></footer>
</div>

<div class="slide report-prose" id="slide-valuation">
    <div class="slide-logo" style="top: 85px;">
        <img src="https://images.ctfassets.net/tl4x668xzide/7mygwms2vuSwirnfvaCSvL/72d2bbd858a69aecbf59fd3fb8954484/robeco-logo-color.png" alt="Robeco Logo" style="height: 1.5rem;">
    </div>
    <header class="report-header-container">
        <div class="header-blue-border">
            <div class="company-header">
                <!-- INSTRUCTION: Replace with actual company domain (e.g., apple.com, microsoft.com) -->
                <!-- INSTRUCTION: Replace with company's main domain for logo. Use https://logo.clearbit.com/[COMPANY-DOMAIN].com format
                Examples: apple.com, microsoft.com, tesla.com, frasersproperty.com, etc. 
                Research the actual company domain from stock_data['company_name'] and use appropriate domain -->
                <img src="https://logo.clearbit.com/[COMPANY-DOMAIN].com" onerror="this.onerror=null;this.src='https://placehold.co/30x30/005F90/ffffff?text={ticker}';" alt="Company Icon" class="icon">
                <h1 class="name"><!-- INSTRUCTION: Use the FULL OFFICIAL company name from stock_data['company_name'] NOT the user input. Example: "Daikin Industries, Ltd." not "DAKIN" --></h1>
                <!-- INSTRUCTION: Use CONSISTENT rating across ALL slides. Choose ONE: OVERWEIGHT (green #2E7D32), NEUTRAL (orange #FF8C00), or UNDERWEIGHT (red #C62828) -->
                <div class="rating" style="color: [RATING-COLOR];">[INVESTMENT-RATING]</div>
            </div>
        </div>
    </header>
    <main>
        <h3>[Create a title that demonstrates sophisticated valuation analysis and shows specific upside potential. Think like a PM presenting a compelling valuation case. Examples: "SIGNIFICANT UNDERVALUATION: DCF SHOWS 40% UPSIDE TO FAIR VALUE" or "GROWTH AT REASONABLE PRICE: 1.2 PEG RATIO SUPPORTS PREMIUM" or "SUM-OF-PARTS ANALYSIS: HIDDEN VALUE IN UNDERVALUED SEGMENTS"]</h3>
        
        <p><strong>[Write a section header on DCF analysis and intrinsic value calculation]</strong></p>
        <p>[Write 500-600 words with PROPRIETARY VALUATION INSIGHTS that demonstrate sophisticated modeling. ⚠️ GOOGLE SEARCH REQUIREMENT: Use Google Search to verify all consensus estimates, peer multiples, recent transactions, and industry benchmarks mentioned. MANDATORY ANALYTICAL STRUCTURE: 1) CONSENSUS VALUATION ERROR: Identify specific flaws in street models with evidence (search for latest analyst reports and consensus estimates) 2) YOUR DIFFERENTIATED MODEL: Present contrarian DCF assumptions with research backing (search for company guidance, industry reports, and management commentary) 3) HISTORICAL VALUATION CONTEXT: Connect current multiple to past trading ranges with fundamental attribution (search for historical valuation data and peer comparisons) 4) PEER VALUATION ARBITRAGE: Identify specific mispricing vs comparables with adjustment factors (search for current peer multiples and financial metrics) 5) CATALYST-DRIVEN RERATING: Map specific events to valuation inflection points (search for upcoming catalysts, regulatory approvals, product launches) 6) SCENARIO-WEIGHTED TARGET: Present probability-weighted price targets with specific triggers (search for recent price target updates and analyst methodology). Include DCF sensitivity tables, reference recent comparable transactions, cite specific research reports, and connect every assumption to business fundamentals. Each valuation component must include investment implications and timing catalysts.]</p>
        
        <p><strong>[Write a section header on multiple-based valuation and peer comparison]</strong></p>
        <p>[Write 500-600 words demonstrating advanced relative valuation analysis, including P/E, EV/EBITDA, P/S comparisons with proper adjustments for growth, profitability, and risk differences. Show why {company_name} deserves premium/discount vs peers and identify valuation catalysts.]</p>
    </main>
    <footer class="report-footer"><p>Robeco Investment Research</p><p>Page 12 / 15</p></footer>
</div>
```

**SLIDES 13-15 - COMPREHENSIVE ANALYSIS & CONCLUSION:**
```html
<div class="slide report-prose" id="slide-bull-bear-analysis">
    <div class="slide-logo" style="top: 85px;">
        <img src="https://images.ctfassets.net/tl4x668xzide/7mygwms2vuSwirnfvaCSvL/72d2bbd858a69aecbf59fd3fb8954484/robeco-logo-color.png" alt="Robeco Logo" style="height: 1.5rem;">
    </div>
    <header class="report-header-container">
        <div class="header-blue-border">
            <div class="company-header">
                <!-- INSTRUCTION: Replace with actual company domain (e.g., apple.com, microsoft.com) -->
                <!-- INSTRUCTION: Replace with company's main domain for logo. Use https://logo.clearbit.com/[COMPANY-DOMAIN].com format
                Examples: apple.com, microsoft.com, tesla.com, frasersproperty.com, etc. 
                Research the actual company domain from stock_data['company_name'] and use appropriate domain -->
                <img src="https://logo.clearbit.com/[COMPANY-DOMAIN].com" onerror="this.onerror=null;this.src='https://placehold.co/30x30/005F90/ffffff?text={ticker}';" alt="Company Icon" class="icon">
                <h1 class="name"><!-- INSTRUCTION: Use the FULL OFFICIAL company name from stock_data['company_name'] NOT the user input. Example: "Daikin Industries, Ltd." not "DAKIN" --></h1>
                <!-- INSTRUCTION: Use CONSISTENT rating across ALL slides. Choose ONE: OVERWEIGHT (green #2E7D32), NEUTRAL (orange #FF8C00), or UNDERWEIGHT (red #C62828) -->
                <div class="rating" style="color: [RATING-COLOR];">[INVESTMENT-RATING]</div>
            </div>
        </div>
    </header>
    <main>
        <h3>[Create a title that demonstrates sophisticated risk assessment and asymmetric return analysis. Think like a PM presenting risk/reward to investment committee. Examples: "AI LEADERSHIP VS COMPETITION THREAT: ASYMMETRIC RISK/REWARD" or "MARKET EXPANSION VS REGULATORY RISK: PROBABILITY-WEIGHTED OUTCOMES" or "MARGIN EXPANSION VS CYCLICAL HEADWINDS: DEFENSIVE GROWTH PROFILE"]</h3>
        
        <h4>[Write a bull case section title that identifies the primary upside driver with quantified potential. Example: "Bull Case: AI Platform Dominance Drives 40% Revenue CAGR"]</h4>
        <p>[Write 500-600 words like a PM building the bull case for investment committee approval. Focus on: 1) Primary upside catalyst with specific timeline and probability assessment 2) Quantified financial impact - revenue growth, margin expansion, market share gains with supporting analysis 3) Market opportunity size and company's ability to capture value with competitive advantages 4) Multiple expansion potential and valuation re-rating catalysts 5) Risk mitigation factors that protect downside even if bull case doesn't fully materialize. Use specific data, industry research, and competitive intelligence. Show sophisticated understanding of what could drive exceptional returns and why this outcome is achievable.]</p>
        
        <h4>[Write a bear case section title that identifies the primary downside risk with specific threat. Example: "Bear Case: Regulatory Headwinds + Competition Pressure Margin Compression"]</h4> 
        <p>[Write 500-600 words like a PM conducting rigorous risk analysis for downside protection. Focus on: 1) Primary downside risk with timeline and probability assessment 2) Quantified negative impact - revenue headwinds, margin compression, market share loss with supporting analysis 3) Competitive threats, regulatory risks, or macro headwinds that could derail thesis 4) Valuation compression scenarios and multiple contraction risks 5) Risk mitigation strategies, hedging opportunities, and downside protection measures. Show understanding of base rates, historical precedents, and what has gone wrong in similar situations. Demonstrate sophisticated risk management thinking.]</p>
        
        <h4>Risk-Adjusted Return Assessment & Expected Value Calculation</h4>
        <p>[Write 400-500 words like a PM conducting rigorous expected value analysis for portfolio construction. Include probability-weighted scenario analysis, Sharpe ratio calculations, maximum drawdown assessment, and correlation analysis vs portfolio holdings. Show sophisticated risk-adjusted return thinking that goes beyond simple upside/downside scenarios.]</p>
    </main>
    <footer class="report-footer"><p>Robeco Investment Research</p><p>Page 13 / 15</p></footer>
</div>

<div class="slide report-prose" id="slide-scenario-analysis">
    <div class="slide-logo" style="top: 85px;">
        <img src="https://images.ctfassets.net/tl4x668xzide/7mygwms2vuSwirnfvaCSvL/72d2bbd858a69aecbf59fd3fb8954484/robeco-logo-color.png" alt="Robeco Logo" style="height: 1.5rem;">
    </div>
    <header class="report-header-container">
        <div class="header-blue-border">
            <div class="company-header">
                <!-- INSTRUCTION: Replace with actual company domain (e.g., apple.com, microsoft.com) -->
                <!-- INSTRUCTION: Replace with company's main domain for logo. Use https://logo.clearbit.com/[COMPANY-DOMAIN].com format
                Examples: apple.com, microsoft.com, tesla.com, frasersproperty.com, etc. 
                Research the actual company domain from stock_data['company_name'] and use appropriate domain -->
                <img src="https://logo.clearbit.com/[COMPANY-DOMAIN].com" onerror="this.onerror=null;this.src='https://placehold.co/30x30/005F90/ffffff?text={ticker}';" alt="Company Icon" class="icon">
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
    <div class="slide-logo" style="top: 85px;">
        <img src="https://images.ctfassets.net/tl4x668xzide/7mygwms2vuSwirnfvaCSvL/72d2bbd858a69aecbf59fd3fb8954484/robeco-logo-color.png" alt="Robeco Logo" style="height: 1.5rem;">
    </div>
    <header class="report-header-container">
        <div class="header-blue-border">
            <div class="company-header">
                <!-- INSTRUCTION: Replace with actual company domain (e.g., apple.com, microsoft.com) -->
                <!-- INSTRUCTION: Replace with company's main domain for logo. Use https://logo.clearbit.com/[COMPANY-DOMAIN].com format
                Examples: apple.com, microsoft.com, tesla.com, frasersproperty.com, etc. 
                Research the actual company domain from stock_data['company_name'] and use appropriate domain -->
                <img src="https://logo.clearbit.com/[COMPANY-DOMAIN].com" onerror="this.onerror=null;this.src='https://placehold.co/30x30/005F90/ffffff?text={ticker}';" alt="Company Icon" class="icon">
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

### 🎯 CRITICAL TITLE GENERATION PRINCIPLES FOR CALL 2:
- **FINANCIAL INSIGHT FOCUS**: Every title must capture the key financial insight (e.g., "EXCEPTIONAL FCF CONVERSION: 95% OF NET INCOME TO FREE CASH FLOW")
- **QUANTIFY THE STORY**: Include specific metrics that show financial strength/weakness (e.g., "25% ROE VS INDUSTRY 12% AVERAGE")
- **COMPARATIVE ADVANTAGE**: Show how {company_name}'s financials compare to peers/industry (e.g., "SUPERIOR CAPITAL EFFICIENCY")
- **VALUE DRIVER IDENTIFICATION**: Highlight what drives financial performance (e.g., "SUBSCRIPTION MODEL TRANSFORMATION")
- **INVESTMENT IMPLICATION**: Make clear why this financial insight matters for investment returns
- **NO GENERIC FINANCIAL TITLES**: Avoid "Income Statement Analysis" - use "REVENUE ACCELERATION & MARGIN EXPANSION"

### ELITE PM QUANTITATIVE FRAMEWORK FOR CALL 2:

**🔬 FINANCIAL FORENSICS & QUALITY ANALYSIS:**
- **Earnings Quality Decomposition**: Separate recurring vs. non-recurring, cash vs. non-cash components to assess sustainability of reported performance
- **Working Capital Forensics**: Analyze changes in DSO, DIO, DPO to uncover management efficiency, competitive pressure, or accounting manipulation
- **Capital Allocation Effectiveness**: Assess ROIC trends, incremental returns on invested capital, and management's track record of value creation
- **Hidden Value Discovery**: Identify understated assets, off-balance sheet value, or optionality not reflected in current valuation

**⚡ PREDICTIVE FINANCIAL MODELING:**
- **Leading Indicator Analysis**: Identify financial metrics that predict future performance 2-3 quarters ahead (e.g., deferred revenue growth, R&D productivity, customer acquisition trends)
- **Inflection Point Detection**: Use ratio analysis and trend decomposition to predict when margin expansion/compression, revenue acceleration/deceleration will occur
- **Cash Flow Predictability**: Assess quality and sustainability of free cash flow generation through cycle analysis and working capital management
- **Capital Efficiency Trajectory**: Predict future ROIC, ROE evolution based on current investment patterns and competitive positioning

**🎯 NON-CONSENSUS FINANCIAL INSIGHTS:**
- **Segment Profitability Analysis**: Uncover hidden value in business segments that consensus treats as commoditized or declining
- **Competitive Margin Analysis**: Predict how pricing power, cost structure advantages will evolve relative to peers
- **Capital Cycle Positioning**: Determine where company is in investment cycle and predict future cash generation vs. capital needs
- **Quality of Growth Assessment**: Distinguish between growth that destroys vs. creates value based on incremental returns and capital requirements

**📊 SOPHISTICATED VALUATION FRAMEWORKS:**
- **Dynamic DCF with Optionality**: Model non-linear growth trajectories, competitive response functions, and real options value
- **Sum-of-Parts with Synergies**: Value business segments independently while capturing cross-segment value creation
- **Through-the-Cycle Normalization**: Adjust for cyclical factors to assess sustainable earning power and appropriate valuation multiples
- **Behavioral Finance Valuation**: Exploit sentiment-driven valuation gaps by comparing fundamental value to market perceptions

**🧮 QUANTITATIVE RISK ASSESSMENT:**
- **Scenario Probability Weighting**: Use Bayesian inference and base rates to assign probabilities to bull/base/bear outcomes
- **Factor Decomposition**: Understand style, sector, quality, and company-specific drivers of returns for portfolio construction
- **Stress Testing**: Model performance under various macro scenarios, competitive threats, and operational challenges
- **Correlation Analysis**: Assess how returns correlate with market factors, sector peers, and macroeconomic variables

**💡 ALPHA SOURCE IDENTIFICATION:**
- **Information Asymmetry Quantification**: Measure how much the market understands vs. misses about financial trajectory
- **Complexity Premium Assessment**: Quantify valuation discount due to business model complexity or accounting complexity
- **Time Horizon Arbitrage**: Identify when short-term volatility creates opportunities in long-term value creation stories
- **Management Quality Premium**: Assess whether market properly values management's capital allocation and operational excellence

{financial_context}

{analyst_insights}

**🚀 ULTRA-SOPHISTICATED EXECUTION MANDATE as of {datetime.now().strftime("%B %Y")}**: 
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

**FINANCIAL INSIGHT REQUIREMENTS:**
- **Slide 8**: Identify hidden earnings quality issues or sustainable competitive advantages buried in income statement
- **Slide 9**: Reveal balance sheet strengths/weaknesses that create option value or hidden risks consensus misses
- **Slide 10**: Uncover cash flow generation patterns that predict future capital allocation effectiveness
- **Slide 11**: Demonstrate superior ratio analysis that identifies competitive positioning trends before consensus
- **Slide 12**: Generate valuation insights using sophisticated methodologies that exploit market mispricing
- **Slide 13**: Assess risks using probability-weighted analysis that accounts for second-order effects
- **Slide 14**: Model scenarios that incorporate competitive responses and industry dynamics consensus ignores
- **Slide 15**: Synthesize financial analysis into actionable investment conclusion with specific alpha generation pathway

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

**CONCISE & PRECISE WRITING REQUIREMENTS:**
- Each analysis section: MAX 150-200 words (not 300+ words)
- Each subsection paragraph: MAX 400-500 words (not 600+ words)
- Use <strong>key metrics</strong> and <strong>critical insights</strong> for emphasis
- Be punchy, direct, and impactful - eliminate unnecessary words
- Every sentence must add specific value or data points

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
        
        
        # Format the prompt with actual company name
        try:
            # Escape any problematic characters in company name for string formatting
            safe_company_name = str(company_name).replace('{', '{{').replace('}', '}}') if '{' in str(company_name) or '}' in str(company_name) else company_name
            formatted_call2_prompt = complete_call2_prompt.format(company_name=safe_company_name)
            logger.info(f"✅ Call 2 prompt built: {len(formatted_call2_prompt):,} characters with pre-built HTML tables")
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