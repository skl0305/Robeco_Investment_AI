#!/usr/bin/env python3
"""
Robeco Template-Based Report Generator
Collects analysis from all agents and generates formatted reports following Robeco template
"""

import logging
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from google.genai import Client, types
from .api_key.gemini_api_key import get_intelligent_api_key

logger = logging.getLogger(__name__)

class RobecoTemplateReportGenerator:
    """Generate comprehensive investment reports following Robeco template structure"""
    
    def __init__(self):
        self.template_path = "/Users/skl/Desktop/Robeco Reporting/Robeco_InvestmentCase_Template.txt"
        logger.info("🏗️ Robeco Template Report Generator initialized")
    
    async def generate_report_from_analyses(
        self, 
        company_name: str,
        ticker: str, 
        analyses_data: Dict[str, Any],
        report_focus: str = "comprehensive"
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
            # Prepare comprehensive analysis prompt (AI generates slides only)
            analysis_prompt = await self._build_report_generation_prompt(
                company_name, ticker, analyses_data
            )
            
            # Generate slides content using AI (no CSS)
            slides_content = await self._generate_ai_report(analysis_prompt)
            
            if not slides_content:
                raise Exception("Failed to generate slides content")
            
            # Combine fixed CSS with generated slides content
            final_report_html = self._combine_css_with_slides(company_name, ticker, slides_content)
            
            logger.info("✅ Robeco template report generated and combined successfully")
            return final_report_html
            
        except Exception as e:
            logger.error(f"❌ Report generation failed: {e}")
            raise e
    
    async def _build_report_generation_prompt(
        self, 
        company_name: str, 
        ticker: str, 
        analyses_data: Dict[str, Any]
    ) -> str:
        """Build comprehensive prompt for AI report generation (slides only)"""
        
        # Extract analysis content from each agent
        agent_analyses = []
        for agent_type, analysis in analyses_data.items():
            if analysis and analysis.get('content'):
                agent_analyses.append({
                    'agent_type': agent_type,
                    'content': analysis['content'],
                    'sources': analysis.get('sources', []),
                    'timestamp': analysis.get('timestamp', '')
                })
        
        prompt = f"""
# ROBECO INVESTMENT SLIDES GENERATION TASK

You are generating ONLY the slide content for a professional investment report for **{company_name} ({ticker})**. 

IMPORTANT: Generate ONLY the HTML slide content - do NOT include any CSS, HTML headers, or styling. Just generate the slides content starting with:

<div class="presentation-container">

And ending with:

</div>

## SOURCE ANALYSES AVAILABLE

You have access to the following specialist analyses:

"""
        
        # Add each agent analysis
        for i, analysis in enumerate(agent_analyses, 1):
            prompt += f"""
### {i}. {analysis['agent_type'].upper()} AGENT ANALYSIS:
```
{analysis['content'][:8000]}...
```

Sources: {len(analysis['sources'])} citations available
Generated: {analysis['timestamp']}

"""
        
        prompt += f"""

## SLIDE STRUCTURE REQUIREMENTS

Generate slides following this exact structure:

```html
<div class="presentation-container">
    <!-- Slide 1: Cover Page -->
    <div class="slide">
        <div class="slide-logo">
            <img src="https://images.ctfassets.net/tl4x668xzide/7mygwms2vuSwirnfvaCSvL/72d2bbd858a69aecbf59fd3fb8954484/robeco-logo-color.png" alt="Robeco">
        </div>
        <div class="slide-content">
            <h1 class="report-title">{company_name}</h1>
            <p class="report-subtitle">Investment Analysis | {ticker}</p>
            <!-- Add cover content based on analyses -->
        </div>
        <div class="report-footer">
            <p>Robeco Investment Analysis</p>
            <p>Page 1</p>
        </div>
    </div>
    
    <!-- Generate 15-20 additional slides based on available agent analyses -->
    <!-- Use the analysis data provided to populate each slide with real insights -->
</div>
```

Generate ONLY this slide content - no CSS, no HTML headers. The system will automatically wrap it with the proper CSS header and footer.

## REPORT GENERATION REQUIREMENTS

1. **SLIDE CONTENT ONLY**: Generate only the presentation-container div with slides inside
2. **CONTENT INTEGRATION**: Synthesize ALL agent analyses into cohesive slide sections:
   - **Fundamentals Agent** → Financial Performance, Operational Analysis slides
   - **Industry Agent** → Market Analysis, Competitive Positioning slides  
   - **Technical Agent** → Price Analysis, Technical Indicators slides
   - **Risk Agent** → Risk Assessment, Mitigation Strategies slides
   - **ESG Agent** → ESG Performance, Sustainability Analysis slides
   - **Valuation Agent** → DCF Analysis, Valuation Metrics slides

3. **PROFESSIONAL QUALITY**: 
   - Institutional-grade analysis with specific metrics and data points
   - Use proper CSS classes: .slide, .slide-content, .section-title, .analysis-item, .metrics-grid
   - Professional investment terminology and insights

4. **SLIDE ORGANIZATION**:
   - Cover slide with company overview
   - Executive summary slide
   - Financial performance slides (from fundamentals analysis)
   - Market/industry slides (from industry analysis)
   - Technical analysis slides
   - Risk assessment slides
   - ESG slides (if available)
   - Valuation and recommendation slides

Focus on creating cohesive, professional slides that synthesize all available agent insights using the proper CSS classes for formatting.
"""
        
        return prompt
    
    async def _generate_ai_report(self, prompt: str) -> str:
        """Generate slides content using AI with automatic retry logic"""
        
        max_retries = 3
        for attempt in range(max_retries):
            # Get API key
            key_result = get_intelligent_api_key(agent_type="report_generator")
            if not key_result:
                raise Exception("No API key available for report generation")
            
            api_key, key_info = key_result
            logger.info(f"📝 Report generation attempt {attempt+1} using API key: {api_key[:8]}...{api_key[-4:]}")
            
            try:
                client = Client(api_key=api_key)
                
                # Configure for comprehensive report generation
                generate_config = types.GenerateContentConfig(
                    temperature=0.1,  # Low for consistent, professional output
                    top_p=0.85,
                    max_output_tokens=65536,  # Maximum tokens for complete analysis without truncation
                    response_mime_type="text/plain",
                    system_instruction="You are a senior institutional investment analyst generating professional investment slides for Robeco. Generate ONLY slide HTML content without CSS headers. Focus on institutional-quality analysis with specific metrics and professional investment terminology."
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
                
                # Use streaming to get real content as it generates
                try:
                    for chunk in client.models.generate_content_stream(
                        model='gemini-2.0-flash-exp',
                        contents=contents,
                        config=generate_config,
                    ):
                        if chunk.text:
                            chunk_count += 1
                            accumulated_response += chunk.text
                            
                            # Log first chunk content to see what AI is generating
                            if chunk_count == 1:
                                logger.info(f"📝 FIRST CHUNK: {chunk.text[:200]}...")
                            
                            # Log milestone chunks to track progress
                            if chunk_count in [50, 100, 200]:
                                logger.info(f"📊 Progress: {chunk_count} chunks, {len(accumulated_response)} chars")
                                
                except Exception as stream_error:
                    logger.error(f"❌ STREAMING ERROR: {stream_error}")
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
    
    def _combine_css_with_slides(self, company_name: str, ticker: str, slides_content: str) -> str:
        """Combine fixed CSS header with AI-generated slides content"""
        
        # Fixed CSS header - consistent every time (no f-string issues)
        css_header = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Robeco - ''' + company_name + ''' Investment Analysis</title>
    <link href="https://fonts.googleapis.com/css2?family=Arial:wght@400;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" crossorigin="anonymous" referrerpolicy="no-referrer" />
    <script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>
    <style>
        :root {
            --robeco-blue: #005F90;
            --robeco-blue-darker: #003D5A;
            --robeco-brown-black: #3B312A;
            --robeco-orange: #FF8C00;
            --text-dark: #000000;
            --text-secondary: #333333;
            --bg-light: #FFFFFF;
            --border-color: var(--robeco-blue);
            --accent-green: #2E7D32;
            --accent-red: #C62828;
            --accent-yellow: #FBC02D;
            --takeaway-bg: radial-gradient(circle at top left, rgba(0, 95, 144, 0.05), rgba(0, 61, 90, 0.0) 50%);
            --primary-blue: #005F90;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; border-radius: 0; }
        html { background-color: #DDE2E7; }
        body { font-family: 'Arial', 'Helvetica Neue', sans-serif; color: var(--text-dark); line-height: 1.5; font-size: 18px; }
        h1, h2, h3, h4, h5, h6 { font-weight: 700; color: var(--robeco-brown-black); margin-bottom: 0.3rem; }
        .presentation-container { width: 1620px; margin: 0; display: flex; flex-direction: column; box-shadow: 0 6px 12px rgba(0,0,0,0.1); }
        .slide {
            width: 1620px; height: 2291px; background-color: var(--bg-light); position: relative; overflow: hidden;
            display: flex; flex-direction: column; border-bottom: 5px solid var(--robeco-blue); padding: 105px 98px; box-sizing: border-box;
        }
        .slide:last-child { border-bottom: none; }
        .slide-logo { position: absolute; top: 30px; right: 98px; width: 120px; height: auto; z-index: 100; }
        .slide-logo img { width: 100%; height: auto; }
        .slide-content { flex-grow: 1; padding: 0; display: flex; flex-direction: column; gap: 15px; overflow-y: auto; }
        .report-footer {
            position: absolute; bottom: 45px; left: 98px; right: 98px; padding-top: 12px;
            border-top: 5px solid var(--robeco-blue); display: flex; justify-content: space-between;
            align-items: center; font-size: 16.5pt; color: var(--text-secondary); z-index: 1000;
        }
        .report-title { font-size: 57px; font-weight: 700; line-height: 1.0; margin-bottom: 0; }
        .report-subtitle { font-size: 27px; font-weight: 400; color: var(--text-dark); margin-bottom: 22.5px; }
        .section-title { font-size: 25.5px; font-weight: 700; padding-bottom: 7.5px; border-bottom: 5px solid var(--robeco-blue); margin-bottom: 18px; color: var(--robeco-blue-darker); }
        .metrics-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1px 2px; padding: 5px 0; margin-bottom: 10px; border-top: 5px solid var(--robeco-blue); border-bottom: 5px solid var(--robeco-blue); }
        .metrics-item { text-align: left; padding: 2px 0; }
        .metrics-item .label { font-size: 10pt; font-weight: 700; color: var(--text-secondary); }
        .metrics-item .value { font-size: 14pt; font-weight: 400; color: var(--text-dark); }
        .analysis-item { display: flex; padding-top: 9px; padding-bottom: 9px; border-bottom: 3.5px solid var(--robeco-blue); margin-bottom: 10px; overflow: hidden; }
        .analysis-item .item-title { flex: 0 0 16%; font-weight: 500; font-size: 16px; color: var(--robeco-blue); padding-right: 15px; }
        .analysis-item .content-item { flex: 1; font-size: 18px; color: var(--text-dark); }
        .bullet-list-square li { position: relative; padding-left: 27px; margin-bottom: 5px; font-size: 18px; color: var(--text-dark); }
        .bullet-list-square li::before { content: ''; position: absolute; left: 0; top: 7px; width: 5.25px; height: 5.25px; background-color: var(--robeco-blue); }
        .compact-table { width: 100%; border-collapse: collapse; font-size: 18px; }
        .compact-table th { background-color: #f2f2f2; font-weight: 700; padding: 6px 12px; }
        .compact-table td { color: var(--text-secondary); padding: 6px 12px; }
    </style>
</head>
<body>'''
        
        # Clean slides content (remove any HTML headers if AI includes them)
        clean_slides = slides_content.strip()
        if clean_slides.startswith('<!DOCTYPE'):
            # AI included full HTML - extract just the slides content
            start_marker = '<div class="presentation-container">'
            if start_marker in clean_slides:
                start_idx = clean_slides.find(start_marker)
                # Find the matching closing div
                div_count = 0
                end_idx = -1
                for i in range(start_idx, len(clean_slides)):
                    if clean_slides[i:i+5] == '<div ':
                        div_count += 1
                    elif clean_slides[i:i+6] == '</div>':
                        div_count -= 1
                        if div_count == 0:
                            end_idx = i + 6
                            break
                if end_idx > 0:
                    clean_slides = clean_slides[start_idx:end_idx]
        
        # Combine CSS header with clean slides content
        combined_html = css_header + '\n' + clean_slides + '\n</body>\n</html>'
        
        logger.info(f"✅ Combined CSS header with {len(clean_slides)} characters of slides content")
        return combined_html
    
    async def _build_report_generation_prompt(
        self, 
        company_name: str, 
        ticker: str, 
        analyses_data: Dict[str, Any]
    ) -> str:
        """Build comprehensive prompt for AI report generation (slides only)"""
        
        # Extract analysis content from each agent
        agent_analyses = []
        for agent_type, analysis in analyses_data.items():
            if analysis and analysis.get('content'):
                agent_analyses.append({
                    'agent_type': agent_type,
                    'content': analysis['content'],
                    'sources': analysis.get('sources', []),
                    'timestamp': analysis.get('timestamp', '')
                })
        
        prompt = f"""
# ROBECO INVESTMENT SLIDES GENERATION TASK

You are generating ONLY the slide content for a professional investment report for **{company_name} ({ticker})**. 

IMPORTANT: Generate ONLY the HTML slide content - do NOT include any CSS, HTML headers, or styling. Just generate the slides content starting with:

<div class="presentation-container">

And ending with:

</div>

## SOURCE ANALYSES AVAILABLE

You have access to the following specialist analyses:

"""
        
        # Add each agent analysis
        for i, analysis in enumerate(agent_analyses, 1):
            prompt += f"""
### {i}. {analysis['agent_type'].upper()} AGENT ANALYSIS:
```
{analysis['content'][:8000]}...
```

Sources: {len(analysis['sources'])} citations available
Generated: {analysis['timestamp']}

"""
        
        prompt += f"""

## SLIDE STRUCTURE REQUIREMENTS

Generate slides following this exact structure:

```html
<div class="presentation-container">
    <!-- Slide 1: Cover Page -->
    <div class="slide">
        <div class="slide-logo">
            <img src="https://images.ctfassets.net/tl4x668xzide/7mygwms2vuSwirnfvaCSvL/72d2bbd858a69aecbf59fd3fb8954484/robeco-logo-color.png" alt="Robeco">
        </div>
        <div class="slide-content">
            <h1 class="report-title">{company_name}</h1>
            <p class="report-subtitle">Investment Analysis | {ticker}</p>
            <!-- Add cover content based on analyses -->
        </div>
        <div class="report-footer">
            <p>Robeco Investment Analysis</p>
            <p>Page 1</p>
        </div>
    </div>
    
    <!-- Generate 15-20 additional slides based on available agent analyses -->
    <!-- Use the analysis data provided to populate each slide with real insights -->
</div>
```

Generate ONLY this slide content - no CSS, no HTML headers. The system will automatically wrap it with the proper CSS header and footer.

## REPORT GENERATION REQUIREMENTS

1. **SLIDE CONTENT ONLY**: Generate only the presentation-container div with slides inside
2. **CONTENT INTEGRATION**: Synthesize ALL agent analyses into cohesive slide sections:
   - **Fundamentals Agent** → Financial Performance, Operational Analysis slides
   - **Industry Agent** → Market Analysis, Competitive Positioning slides  
   - **Technical Agent** → Price Analysis, Technical Indicators slides
   - **Risk Agent** → Risk Assessment, Mitigation Strategies slides
   - **ESG Agent** → ESG Performance, Sustainability Analysis slides
   - **Valuation Agent** → DCF Analysis, Valuation Metrics slides

3. **PROFESSIONAL QUALITY**: 
   - Institutional-grade analysis with specific metrics and data points
   - Use proper CSS classes: .slide, .slide-content, .section-title, .analysis-item, .metrics-grid
   - Professional investment terminology and insights

4. **SLIDE ORGANIZATION**:
   - Cover slide with company overview
   - Executive summary slide
   - Financial performance slides (from fundamentals analysis)
   - Market/industry slides (from industry analysis)
   - Technical analysis slides
   - Risk assessment slides
   - ESG slides (if available)
   - Valuation and recommendation slides

Focus on creating cohesive, professional slides that synthesize all available agent insights using the proper CSS classes for formatting.
"""
        
        return prompt
    
    async def _generate_ai_report(self, prompt: str) -> str:
        """Generate slides content using AI with automatic retry logic"""
        
        max_retries = 3
        for attempt in range(max_retries):
            # Get API key
            key_result = get_intelligent_api_key(agent_type="report_generator")
            if not key_result:
                raise Exception("No API key available for report generation")
            
            api_key, key_info = key_result
            logger.info(f"📝 Report generation attempt {attempt+1} using API key: {api_key[:8]}...{api_key[-4:]}")
            
            try:
                client = Client(api_key=api_key)
                
                # Configure for comprehensive report generation
                generate_config = types.GenerateContentConfig(
                    temperature=0.1,  # Low for consistent, professional output
                    top_p=0.85,
                    max_output_tokens=65536,  # Maximum tokens for complete analysis without truncation
                    response_mime_type="text/plain",
                    system_instruction="You are a senior institutional investment analyst generating professional investment slides for Robeco. Generate ONLY slide HTML content without CSS headers. Focus on institutional-quality analysis with specific metrics and professional investment terminology."
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
                
                # Use streaming to get real content as it generates
                try:
                    for chunk in client.models.generate_content_stream(
                        model='gemini-2.0-flash-exp',
                        contents=contents,
                        config=generate_config,
                    ):
                        if chunk.text:
                            chunk_count += 1
                            accumulated_response += chunk.text
                            
                            # Log first chunk content to see what AI is generating
                            if chunk_count == 1:
                                logger.info(f"📝 FIRST CHUNK: {chunk.text[:200]}...")
                            
                            # Log milestone chunks to track progress
                            if chunk_count in [50, 100, 200]:
                                logger.info(f"📊 Progress: {chunk_count} chunks, {len(accumulated_response)} chars")
                                
                except Exception as stream_error:
                    logger.error(f"❌ STREAMING ERROR: {stream_error}")
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