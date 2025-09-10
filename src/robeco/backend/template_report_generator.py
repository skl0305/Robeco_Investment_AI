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
        financial_data: Dict = None
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
            # Prepare comprehensive analysis prompt (AI generates complete report)
            analysis_prompt = await self._build_report_generation_prompt(
                company_name, ticker, analyses_data, financial_data
            )
            
            # Generate slides content using AI (no CSS) with optional websocket streaming
            slides_content = await self._generate_ai_report(analysis_prompt, websocket, connection_id)
            
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
        analyses_data: Dict[str, Any],
        financial_data: Dict = None
    ) -> str:
        """Build optimized prompt that prioritizes content generation over template embedding"""
        
        # Load essential template structure (extract key sections only, not full content)
        try:
            with open(self.template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            logger.info(f"✅ Loaded template: {len(template_content):,} characters")
            
            # Extract just the key structural elements and section titles (not full content)
            # This reduces prompt size while maintaining structure guidance
            template_structure = self._extract_key_template_structure(template_content)
            
        except Exception as e:
            logger.error(f"❌ Failed to load template: {e}")
            raise Exception(f"Could not load template file: {e}")
        
        # Include available analyst insights as supplementary data (not required)
        available_analyses = []
        for agent_type, analysis in analyses_data.items():
            if analysis and analysis.get('content'):
                available_analyses.append({
                    'agent_type': agent_type,
                    'content': analysis['content'][:6000],  # Moderate size for context
                    'sources': analysis.get('sources', []),
                })
        
        # Build comprehensive prompt for exact Robeco presentation-container structure
        prompt = f"""
# ROBECO INVESTMENT CASE - EXACT TEMPLATE REPLICATION

You are a Robeco Managing Director creating an investment case for **{company_name} ({ticker})**.

## CRITICAL: EXACT CSS STRUCTURE AND LAYOUT COMPLIANCE

### 1. EXACT HTML HIERARCHY REQUIREMENTS:

You must generate ONLY the content that goes inside <body></body> tags. 

**CRITICAL: NO EXTRA WRAPPERS OR CODE BLOCKS**
- ❌ DO NOT include DOCTYPE, HTML, HEAD, or BODY tags
- ❌ DO NOT include ```html code blocks or markdown formatting
- ❌ DO NOT include any wrapper divs like `<div class="container">`
- ❌ DO NOT include any CSS styles or script tags

**START IMMEDIATELY WITH EXACTLY THIS:**
Your response must begin with the first line being:
`<div class="presentation-container">`

**MANDATORY ROOT STRUCTURE:**

```html
<div class="presentation-container">
    <div class="slide" id="portrait-page-1">
        <header class="report-header-container">
            <div class="robeco-logo-container">
                <img src="https://www.theia.org/sites/default/files/2019-04/Robeco-UK.png" alt="Robeco Logo">
            </div>
            <div class="header-blue-border">
                <div class="company-header">
                    <img src="[COMPANY_LOGO]" alt="Company Icon" class="icon">
                    <h1 class="name">{company_name}</h1>
                    <div class="rating" style="color: #C62828;">RATING</div>
                </div>
            </div>
        </header>
        <main style="display: flex; flex-direction: column; flex-grow: 1;">
            <!-- CONTENT GOES HERE -->
        </main>
        <footer class="report-footer">
            <p>Source: Robeco Internal Analysis, Bloomberg</p>
            <p>Page 1 / 15</p>
        </footer>
    </div>
</div>
```

### 2. LAYOUT COMPLIANCE - EXACT DIMENSIONS:

**SLIDE SPECIFICATIONS:**
- Each slide MUST be exactly **1620px width × 2291px height**
- Padding: **105px top/bottom, 98px left/right** (already in CSS)
- Background: **#FFFFFF** (--bg-light)
- Border: **5px solid #005F90** (--robeco-blue) at bottom

**SPACING REQUIREMENTS:**
- Header height: **Variable based on content**
- Main content area: **flex-grow: 1** (fills remaining space)
- Footer position: **absolute, bottom: 45px**
- Footer border: **5px solid #005F90** at top

### 3. MANDATORY CSS CLASS HIERARCHY:

**ROOT CONTAINER:**
```html
<div class="presentation-container">  <!-- 1620px width, flex column -->
```

**SLIDE STRUCTURE:**
```html
<div class="slide" id="portrait-page-1">  <!-- 1620×2291px, padding 105px 98px -->
    <header class="report-header-container">
        <div class="robeco-logo-container">
            <img src="..." alt="Robeco Logo">
        </div>
        <div class="header-blue-border">
            <div class="company-header">
                <img src="..." alt="Company Icon" class="icon">
                <h1 class="name">COMPANY NAME</h1>
                <div class="rating" style="color: #COLOR;">RATING</div>
            </div>
        </div>
    </header>
    <main style="display: flex; flex-direction: column; flex-grow: 1;">
        <!-- MAIN CONTENT -->
    </main>
    <footer class="report-footer">
        <p>Source: Robeco Internal Analysis, Bloomberg</p>
        <p>Page X / 15</p>
    </footer>
</div>
```

**METRICS GRID (MANDATORY STRUCTURE):**
```html
<section class="metrics-grid">  <!-- 4-column grid, gap 1px 2px -->
    <div class="metrics-item">
        <div class="label">LABEL TEXT</div>    <!-- 10pt font, #333333 -->
        <div class="value">VALUE TEXT</div>    <!-- 14pt font, #000000 -->
    </div>
    <!-- Repeat for all metrics -->
</section>
```

**CONTENT STRUCTURE (MANDATORY):**
```html
<div class="content-grid grid-1-col">
    <div class="content-block">
        <div class="intro-and-chart-container">
            <div class="intro-text-block">
                <p><strong>COMPANY NAME</strong> introduction text...</p>
            </div>
            <div class="stock-chart-container" id="stock-price-line-chart">
                <!-- D3 Chart placeholder -->
            </div>
        </div>
        <div class="orange-separator"></div>
        <div class="investment-summary-table-section">
            <div class="analysis-item first-analysis-item">
                <div class="item-title"><strong>SECTION TITLE</strong></div>
                <div class="content-item">CONTENT</div>
            </div>
            <!-- More analysis items -->
        </div>
    </div>
</div>
```

### 4. CRITICAL: NO DEVIATIONS ALLOWED

**FORBIDDEN STRUCTURES:**
- ❌ `<div class="container">` (generic container)
- ❌ `<div class="item-title">` without parent `analysis-item`
- ❌ Any custom CSS classes not in original template
- ❌ Missing `presentation-container` wrapper
- ❌ Wrong slide dimensions or padding

**REQUIRED STRUCTURE VALIDATION:**
Every generated HTML must contain:
✅ `<div class="presentation-container">`
✅ `<div class="slide" id="portrait-page-1">`
✅ `<header class="report-header-container">`
✅ `<section class="metrics-grid">`
✅ `<div class="content-grid grid-1-col">`
✅ `<footer class="report-footer">`

3. **PROFESSIONAL INVESTMENT ANALYSIS TONE**: Write like a seasoned institutional investor with:
   - Specific financial metrics in bold: **¥1,690bn**, **24.6x P/E**, **15-20% downside**
   - Professional terminology: WACC, DCF, EBITDA, FCF, basis points, YoY, QoQ
   - Definitive investment conclusions and price targets
   - Risk-focused language highlighting concerns and challenges

## FINANCIAL DATA AVAILABLE:
{str(financial_data)[:6000] if financial_data else "Conduct fundamental analysis based on market knowledge"}

## EXACT ROBECO TEMPLATE STRUCTURE TO REPLICATE:

Generate exactly this structure with your analysis content:

```html
<div class="slide" id="portrait-page-1">
    <header class="report-header-container">
        <div class="robeco-logo-container">
            <img src="https://www.theia.org/sites/default/files/2019-04/Robeco-UK.png" alt="Robeco Logo">
        </div>
        <div class="header-blue-border">
            <div class="company-header">
                <img src="[COMPANY_LOGO]" alt="Company Icon" class="icon">
                <h1 class="name">{company_name}</h1>
                <div class="rating" style="color: #FF0000;">BUY/HOLD/SELL</div>
            </div>
        </div>
    </header>
    <main style="display: flex; flex-direction: column; flex-grow: 1;">
        <section class="metrics-grid">
            <div class="metrics-item">
                <div class="label">MAIN LISTING</div>
                <div class="value">{ticker}</div>
            </div>
            <div class="metrics-item">
                <div class="label">MARKET CAP</div>
                <div class="value">[CALCULATE]</div>
            </div>
            <div class="metrics-item">
                <div class="label">ENTERPRISE VALUE</div>
                <div class="value">[CALCULATE]</div>
            </div>
            <div class="metrics-item">
                <div class="label">CURRENT PRICE</div>
                <div class="value">[FROM DATA]</div>
            </div>
            <div class="metrics-item">
                <div class="label">TARGET PRICE</div>
                <div class="value">[DCF ANALYSIS]</div>
            </div>
            <div class="metrics-item">
                <div class="label">REVENUE GROWTH (FY24)</div>
                <div class="value">[CALCULATE]</div>
            </div>
            <div class="metrics-item">
                <div class="label">ESG RATING</div>
                <div class="value">[RESEARCH]</div>
            </div>
            <div class="metrics-item">
                <div class="label">FCF YIELD (FY24)</div>
                <div class="value">[CALCULATE]</div>
            </div>
            <div class="metrics-item">
                <div class="label">DIVIDEND YIELD</div>
                <div class="value">[CALCULATE]</div>
            </div>
            <div class="metrics-item">
                <div class="label">NET DEBT / EBITDA</div>
                <div class="value">[CALCULATE]</div>
            </div>
            <div class="metrics-item">
                <div class="label">DEBT/EQUITY</div>
                <div class="value">[CALCULATE]</div>
            </div>
            <div class="metrics-item">
                <div class="label">QR RANKING</div>
                <div class="value">[RESEARCH]</div>
            </div>
            <div class="metrics-item">
                <div class="label">ANALYSTS</div>
                <div class="value">[COUNT]</div>
            </div>
            <div class="metrics-item">
                <div class="label">P/E (FY1)</div>
                <div class="value">[CALCULATE]</div>
            </div>
            <div class="metrics-item">
                <div class="label">EV/EBITDA (FY+1)</div>
                <div class="value">[CALCULATE]</div>
            </div>
            <div class="metrics-item">
                <div class="label">AVG. ANALYST RATING</div>
                <div class="value">[RESEARCH]</div>
            </div>
        </section>
        <div class="content-grid grid-1-col">
            <div class="content-block">
                <div class="intro-and-chart-container">
                    <div class="intro-text-block">
                        <p><strong>{company_name}</strong> [Write comprehensive company introduction - 3-4 sentences about business model, market position, and strategic focus]</p>
                    </div>
                    <div class="stock-chart-container" id="stock-price-line-chart">
                        <!-- D3 Line Chart will be rendered here -->
                    </div>
                </div>

                <div class="orange-separator"></div>

                <div class="investment-summary-table-section">
                    <div class="analysis-item first-analysis-item">
                        <div class="item-title"><strong>REASON TO ANALYZE</strong></div>
                        <div class="content-item">
                            [Your comprehensive analysis - 2-3 detailed paragraphs with specific metrics and investment rationale]
                        </div>
                    </div>
                    <div class="analysis-item">
                        <div class="item-title"><strong>LONG TERM OUTLOOK</strong></div>
                        <div class="content-item">
                            [Your long-term analysis - 2-3 detailed paragraphs with growth projections and strategic outlook]
                        </div>
                    </div>
                    <div class="analysis-item">
                        <div class="item-title"><strong>FUNDAMENTAL CONCLUSION</strong></div>
                        <div class="content-item">
                            [Your fundamental analysis conclusion - 2-3 detailed paragraphs with financial analysis]
                        </div>
                    </div>
                    <div class="analysis-item" style="border-bottom: none; padding-bottom: 0; margin-bottom: 0;">
                        <div class="item-title"><strong>FIT WITH TOP-DOWN VIEW</strong></div>
                        <div class="content-item">
                            [Your top-down analysis - 2-3 detailed paragraphs with macro/thematic view]
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </main>
</div>

<div class="slide" id="portrait-page-1A">
    <header class="report-header-container">
        <div class="robeco-logo-container">
            <img src="https://www.theia.org/sites/default/files/2019-04/Robeco-UK.png" alt="Robeco Logo">
        </div>
        <div class="header-blue-border">
            <div class="company-header">
                <img src="[COMPANY_LOGO]" alt="Company Icon" class="icon">
                <h1 class="name">{company_name}</h1>
                <div class="rating" style="color: #FF0000;">BUY/HOLD/SELL</div>
            </div>
        </div>
    </header>
    <main style="display: flex; flex-direction: column; flex-grow: 1;">
        <div class="investment-summary-table-section">
            <div class="analysis-item first-analysis-item">
                <div class="item-title"><strong>VALUATION</strong></div>
                <div class="content-item">
                    [Your valuation analysis - DCF, multiples, target price with specific calculations]
                </div>
            </div>
            <div class="analysis-item">
                <div class="item-title"><strong>RISKS</strong></div>
                <div class="content-item">
                    [Your risk analysis - key risks with probability and impact assessment]
                </div>
            </div>
            <div class="analysis-item">
                <div class="item-title"><strong>QUANTITATIVE CONCLUSION</strong></div>
                <div class="content-item">
                    [Your quantitative analysis - metrics, ratios, and financial conclusions]
                </div>
            </div>
            <div class="analysis-item">
                <div class="item-title"><strong>SHORT TERM OUTLOOK</strong></div>
                <div class="content-item">
                    [Your short-term outlook - next 6-12 months with catalysts and projections]
                </div>
            </div>
            <div class="analysis-item" style="border-bottom: none; padding-bottom: 0; margin-bottom: 0;">
                <div class="item-title"><strong>EARNINGS REVISIONS</strong></div>
                <div class="content-item">
                    [Your earnings revision analysis - consensus vs your estimates with revision expectations]
                </div>
            </div>
        </div>
    </main>
</div>
```

## CRITICAL CONTENT REQUIREMENTS - INVESTMENT BANKING ANALYSIS STYLE:

1. **SOPHISTICATED INSTITUTIONAL TONE**: Write like a seasoned Robeco Managing Director with:
   - **Balanced, objective analysis** that weighs both opportunities and risks
   - **Data-driven conclusions** based on comprehensive financial and strategic assessment
   - **Professional analytical rigor** with nuanced market insights
   - **Unbiased perspective** that lets the facts determine the investment thesis

2. **COMPREHENSIVE ANALYTICAL FRAMEWORK**:
   - **Assess both strengths and weaknesses** objectively without predetermined bias
   - **Analyze competitive positioning** - where the company leads and where it lags
   - **Evaluate growth prospects** - realistic assessment of opportunities and constraints
   - **Financial health analysis** - balance sheet strength, cash generation, capital allocation efficiency

3. **BALANCED INVESTMENT ANALYSIS LANGUAGE**:
   - **Opportunity Assessment**: "compelling growth prospects", "strong competitive advantages", "robust financial position"
   - **Risk Evaluation**: "key risks to monitor", "potential headwinds", "execution challenges"
   - **Financial Analysis**: "sustainable cash generation", "efficient capital allocation", "margin expansion potential"
   - **Strategic Positioning**: "well-positioned for growth", "market leadership", "strategic initiatives driving value"

4. **SPECIFIC FINANCIAL METRICS IN BOLD**: **¥2.5 trillion backlog**, **6.4% operating margin**, **¥90bn R&D spend**

3. **COMPREHENSIVE ANALYSIS**: Each section must be 2-3 detailed paragraphs (150-300 words each) with specific financial analysis

4. **INVESTMENT RECOMMENDATION**: Provide clear BUY/HOLD/SELL recommendation with price target and timeline

5. **CRITICAL ANALYSIS DEPTH REQUIREMENTS**:
   - **Question management narratives**: Challenge official growth strategies and execution timelines
   - **Highlight structural weaknesses**: Focus on competitive vulnerabilities and market pressures  
   - **Analyze margin sustainability**: Question whether recent improvements are cyclical vs structural
   - **Assess capital allocation**: Scrutinize R&D spend, backlog quality, and return expectations
   - **Challenge growth assumptions**: Provide realistic growth projections vs management guidance

6. **SECTION-SPECIFIC BALANCED ANALYSIS**:
   - **REASON TO ANALYZE**: Objective assessment of investment merits - both opportunities and risks
   - **LONG TERM OUTLOOK**: Balanced view of growth prospects and potential challenges
   - **FUNDAMENTAL CONCLUSION**: Comprehensive financial health assessment with clear conclusion
   - **FIT WITH TOP-DOWN VIEW**: Alignment assessment with strategic themes and market outlook
   - **VALUATION**: Fair value analysis with multiple scenarios (base, bull, bear cases)
   - **RISKS**: Balanced risk assessment with mitigation factors and opportunities

7. **FINANCIAL ANALYSIS RIGOR**: Use real calculations from provided data, not generic placeholders

## AVAILABLE ANALYST INSIGHTS (SUPPLEMENTARY ONLY):
{f"Available analyses from {len(available_analyses)} specialists:" if available_analyses else "No specialist analyses available - conduct independent comprehensive analysis"}
"""
        
        # Add available analyses as context only
        if available_analyses:
            for analysis in available_analyses[:8]:  # Limit to prevent prompt bloat
                prompt += f"""
**{analysis['agent_type'].upper()}**: {analysis['content'][:3000]}...
"""
        else:
            prompt += """
**NOTE**: No specialist analyses available. Conduct comprehensive independent analysis using your investment banking expertise and the financial data provided.
"""
        
        prompt += f"""

## BALANCED ANALYTICAL LANGUAGE TO USE:
- **STRENGTHS**: "compelling competitive advantages", "robust financial position", "strong market leadership"
- **OPPORTUNITIES**: "significant growth potential", "expanding market opportunities", "strategic initiatives driving value"  
- **CHALLENGES**: "execution risks to monitor", "competitive pressures", "market headwinds"
- **RISKS**: "key risks include", "potential volatility", "regulatory uncertainties"
- **CONCLUSIONS**: "well-positioned for growth", "attractive risk-reward profile", "compelling investment case"
- **NEUTRAL TERMS**: "balanced portfolio exposure", "prudent capital allocation", "sustainable competitive position"

## EXACT TEMPLATE STRUCTURE TO FOLLOW:
{template_structure}

## CRITICAL: OBJECTIVE & COMPREHENSIVE ANALYSIS REQUIREMENTS

Your analysis must be UNBIASED and data-driven. Let the financial facts and market realities determine whether this is a BUY, HOLD, or SELL - not predetermined negativity.

**ANALYTICAL OBJECTIVITY PRINCIPLES:**
1. **Start with facts**: Present financial data and business fundamentals objectively
2. **Weigh pros and cons**: Every section should acknowledge both strengths and weaknesses  
3. **Evidence-based conclusions**: Let the data drive the investment recommendation
4. **Fair valuation**: Use realistic assumptions, not overly conservative or optimistic ones
5. **Balanced risk assessment**: Highlight risks but also discuss competitive advantages and opportunities

Each section requires:

**CONTENT LENGTH REQUIREMENTS:**
- Each `<p>` paragraph: 150-300 words minimum (not 1-2 sentences!)
- Each bullet point `<li>`: 80-150 words with detailed analysis
- Each section must have 3-5 detailed bullet points with sub-analysis
- Total content per slide: 500-800 words minimum

**INVESTMENT BANKING WRITING STYLE:**
- **Parenthetical Data Emphasis**: ALL metrics in parentheses: "(24.6x P/E)", "(¥1,690bn revenue)", "(15% ROIC)"
- **Professional Terminology**: tailwinds, headwinds, catalyst, volatility, bps, YoY, QoQ, risk-on/off, bullish/bearish
- **Definitive Assertions**: "Our analysis indicates...", "We project...", "This presents a compelling..."
- **Detailed Financial Analysis**: Include specific projections, margin analysis, growth rates, competitive positioning
- **Bold Emphasis**: Use **bold** for key metrics and important financial data points throughout

**ANALYSIS DEPTH REQUIREMENTS:**
- Provide specific financial projections and metrics
- Include detailed competitive analysis and market positioning  
- Analyze business segment performance with quantitative data
- Discuss management strategy execution with specific examples
- Include risk assessment with probability and impact analysis

**EXAMPLE OF REQUIRED DEPTH (from template):**
```
<div class="item-title">REASON TO ANALYZE</div>
<div class="content-item">
    <p>IHI's positioning at the confluence of global mega-trends, particularly <strong>decarbonization</strong> and <strong>aerospace recovery</strong>, presents more risk than opportunity. While these sectors offer long-term potential, our analysis suggests the company's execution capabilities and significant capital intensity in these nascent areas are questionable, making it a high-risk proposition for mandates focused on "Sustainable Energy" and "Future Transportation."</p>
    <ul>
        <li><strong>Strategic Misalignment:</strong> Despite extensive R&D efforts, IHI's core competencies remain heavily tied to traditional, cyclical heavy industries, making its transition to sustainable solutions slower and more capital-intensive than anticipated.</li>
        <li><strong>Unproven Leadership:</strong> While IHI is a player in ammonia co-firing, its "leadership" is in pilot stages, not commercial scale. The path to profitability for these technologies remains highly uncertain and capital-intensive, evidenced by pilot tests demonstrating <strong>99% combustion efficiency</strong>, which is not a metric for commercial viability.</li>
        <li><strong>Concentrated Exposure:</strong> The diversified portfolio offers limited true diversification; its key segments remain highly sensitive to global macroeconomic downturns and geopolitical shifts, a risk evidenced by past earnings volatility.</li>
    </ul>
</div>
```

**CRITICAL: REPORT-STYLE CONTENT STRUCTURE (NO BULLET POINTS)**

**FOR SLIDES 3+ USE REPORT-STYLE PARAGRAPHS ONLY:**
```html
<section class="analysis-sections" style="flex-grow: 1;">
    <h3>1. INVESTMENT HIGHLIGHTS</h3>
    <p>Comprehensive paragraph 1 of detailed analysis (150-200 words)...</p>
    <p>Comprehensive paragraph 2 continuing analysis (150-200 words)...</p>
    <p>Comprehensive paragraph 3 with conclusions (150-200 words)...</p>
    <!-- NO bullet-list-square, NO h4 subheadings, NO ul/li -->
</section>
```

**FORBIDDEN IN SLIDES 3+:**
- ❌ `<div class="bullet-list-square">`
- ❌ `<h4>CORE INVESTMENT THESIS:</h4>` or any h4 subheadings
- ❌ `<ul><li>` bullet point structures
- ❌ Any list formatting or bullet points

**REQUIRED IN SLIDES 3+:**
- ✅ Only `<p>` paragraphs with continuous narrative
- ✅ Comprehensive report-style analysis like RB.html
- ✅ Each paragraph 150-200 words of detailed analysis
- ✅ Professional investment banking prose with specific metrics in bold

**YOUR CONTENT MUST MATCH RB.HTML STYLE:** Detailed report paragraphs, specific metrics in bold, comprehensive narrative analysis, professional investment banking language.

## MANDATORY FINAL INSTRUCTION:

**FIRST LINE OF YOUR RESPONSE:**
Start your response with exactly this text (no spaces before it):
`<div class="presentation-container">`

**LAST LINE OF YOUR RESPONSE:**
End your response with exactly this text:
`</div>`

**NO OTHER TEXT OR FORMATTING** - just clean HTML following the exact structure specified above.

## MANDATORY REQUIREMENTS:

1. **EXACT STRUCTURE COMPLIANCE**: Follow the template structure exactly - same CSS classes, same section titles
2. **REPLACE ALL PLACEHOLDERS**: Replace [COMPANY_NAME], [TICKER], [MARKET_CAP], etc. with actual data
3. **GENERATE ALL 18 SLIDES**: Follow the complete template structure with all slides:
   - Slides 1-2: Investment summary with exact sections
   - Slides 3-4: Investment highlights and catalysts
   - Slides 5-7: Company, operational, and strategic analysis
   - Slides 8-10: Industry analysis (3 parts)
   - Slides 11-14: Financial analysis (performance, income, balance sheet, cash flow)
   - Slides 15-16: DCF and bull-bear analysis
   - Slides 17-18: ESG and corporate governance
4. **PROFESSIONAL ANALYSIS**: Generate comprehensive investment banking analysis for each section
5. **REAL DATA INTEGRATION**: Use actual financial metrics throughout with parenthetical emphasis

## COMPLETE 18-SLIDE STRUCTURE REQUIREMENTS:
Your output must include ALL 18 slides in this exact order:
1. `portrait-page-1` - Company info, metrics, investment summary
2. `portrait-page-1A` - Investment summary continued (valuation, risks, etc.)
3. `investment-highlights-pitchbook-page` - Investment highlights
4. `catalyst-page` - Catalysts and recent developments
5. `company-analysis-page` - Company and operational analysis
6. `operational-analysis-page` - Operational analysis
7. `strategic-initiative-page` - Key strategic initiatives
8. `industry-analysis-page-1` - Industry analysis part 1
9. `industry-analysis-page-2` - Industry analysis part 2 (global dynamics)
10. `industry-analysis-page-3` - Industry analysis part 3 (sector-specific)
11. `financial-performance-page` - Financial performance highlights
12. `income-statement-page` - Income statement analysis
13. `balance-sheet-page` - Balance sheet analysis
14. `cash-flow-page` - Cash flow analysis
15. `dcf-analysis-page` - DCF analysis
16. `bull-bear-analysis-page` - Bull-bear scenario analysis
17. `esg-analysis-page` - ESG analysis
18. `governance-page` - Corporate governance & shareholders

## FINAL CRITICAL INSTRUCTION:

**DO NOT GENERATE BRIEF SUMMARIES!** Your output must be comprehensive, detailed investment research with:
- Long paragraphs (150-300 words each)
- Detailed bullet points (80-150 words each)  
- Specific financial metrics and projections
- Professional investment banking analysis depth
- Total content per slide: 500-800 words minimum

**GENERATE COMPLETE 18-SLIDE COMPREHENSIVE INVESTMENT ANALYSIS NOW:**
"""
        
        logger.info(f"✅ Optimized prompt built: {len(prompt):,} characters (reduced from massive template)")
        return prompt
    
    def _extract_key_template_structure(self, template_content: str) -> str:
        """Extract the complete 18-slide template structure that AI must follow exactly"""
        
        # Complete 18-slide structure from the Robeco template
        structure_template = """
COMPLETE 18-SLIDE ROBECO TEMPLATE STRUCTURE:

You must generate ALL 18 slides following this EXACT structure:

<!-- SLIDE 1: Company Info, Metrics, Stock Chart, Investment Summary -->
<div class="slide" id="portrait-page-1">
    <header class="report-header-container">
        <div class="robeco-logo-container">
            <img src="https://www.theia.org/sites/default/files/2019-04/Robeco-UK.png" alt="Robeco Logo">
        </div>
        <div class="header-blue-border">
            <div class="company-header">
                <img src="[COMPANY_LOGO]" alt="Company Icon" class="icon">
                <h1 class="name">[COMPANY_NAME]</h1>
                <div class="rating" style="color: [RATING_COLOR];">[INVESTMENT_RATING]</div>
            </div>
        </div>
    </header>
    <main style="display: flex; flex-direction: column; flex-grow: 1;">
        <section class="metrics-grid">
            [8 metrics: MAIN LISTING, MARKET CAP, ENTERPRISE VALUE, CURRENT PRICE, TARGET PRICE, DIVIDEND YIELD, PRICE/BOOK, FORWARD P/E]
        </section>
        <div class="investment-summary-table-section">
            <div class="analysis-item first-analysis-item">
                <div class="item-title">REASON TO ANALYZE</div>
                <div class="content-item">[Content]</div>
            </div>
            <div class="analysis-item">
                <div class="item-title">LONG TERM OUTLOOK</div>
                <div class="content-item">[Content]</div>
            </div>
            <div class="analysis-item">
                <div class="item-title">FUNDAMENTAL CONCLUSION</div>
                <div class="content-item">[Content]</div>
            </div>
            <div class="analysis-item">
                <div class="item-title">FIT WITH TOP-DOWN VIEW</div>
                <div class="content-item">[Content]</div>
            </div>
        </div>
    </main>
</div>

<!-- SLIDE 2: Investment Summary (Continued) -->
<div class="slide" id="portrait-page-1A">
    <header class="report-header-container">[Same header structure]</header>
    <main style="display: flex; flex-direction: column; flex-grow: 1;">
        <div class="investment-summary-table-section">
            <div class="analysis-item first-analysis-item">
                <div class="item-title">VALUATION</div>
                <div class="content-item">[Content]</div>
            </div>
            <div class="analysis-item">
                <div class="item-title">RISKS</div>
                <div class="content-item">[Content]</div>
            </div>
            <div class="analysis-item">
                <div class="item-title">QUANTITATIVE CONCLUSION</div>
                <div class="content-item">[Content]</div>
            </div>
            <div class="analysis-item">
                <div class="item-title">SHORT TERM OUTLOOK</div>
                <div class="content-item">[Content]</div>
            </div>
            <div class="analysis-item">
                <div class="item-title">EARNINGS REVISIONS</div>
                <div class="content-item">[Content]</div>
            </div>
        </div>
    </main>
</div>

<!-- SLIDE 3: Investment Highlights (Pitchbook Style) -->
<div class="slide report-prose" id="investment-highlights-pitchbook-page">
    <header class="report-header-container">[Same header structure]</header>
    <main style="display: flex; flex-direction: column; flex-grow: 1;">
        <section class="analysis-sections" style="flex-grow: 1;">
            <h3>1. INVESTMENT HIGHLIGHTS</h3>
            <p>[Comprehensive paragraph 1 - 150-200 words of detailed investment analysis]</p>
            <p>[Comprehensive paragraph 2 - 150-200 words continuing analysis]</p>
            <p>[Comprehensive paragraph 3 - 150-200 words with conclusions]</p>
        </section>
    </main>
    <footer class="report-footer">
        <p>Source: Robeco Internal Analysis, Bloomberg</p>
        <p>Page 3 / 18</p>
    </footer>
</div>

<!-- SLIDE 4: Catalysts (New Page) -->
<div class="slide report-prose" id="catalyst-page">
    <header class="report-header-container">[Same header structure]</header>
    <main style="display: flex; flex-direction: column; flex-grow: 1;">
        <section class="analysis-sections" style="flex-grow: 1;">
            <h3>2. CATALYSTS AND RECENT DEVELOPMENTS</h3>
            <p>[Comprehensive paragraph 1 - 150-200 words analyzing key catalysts]</p>
            <p>[Comprehensive paragraph 2 - 150-200 words on recent developments]</p>
            <p>[Comprehensive paragraph 3 - 150-200 words on performance triggers]</p>
        </section>
    </main>
    <footer class="report-footer">
        <p>Source: Robeco Internal Analysis, Bloomberg</p>
        <p>Page 4 / 18</p>
    </footer>
</div>

<!-- SLIDE 5: Company Analysis -->
<div class="slide report-prose" id="company-analysis-page">
    <header class="report-header-container">[Same header structure]</header>
    <main style="display: flex; flex-direction: column; flex-grow: 1;">
        <section class="analysis-sections" style="flex-grow: 1;">
            <h3>3. COMPANY AND OPERATIONAL ANALYSIS</h3>
            <p>[Company analysis content]</p>
            <p>[Comprehensive paragraph 1 - 150-200 words on company operations]</p>
            <p>[Comprehensive paragraph 2 - 150-200 words on business segments]</p>
            <p>[Comprehensive paragraph 3 - 150-200 words on operational review]</p>
        </section>
    </main>
    <footer class="report-footer">
        <p>Source: Robeco Internal Analysis, Bloomberg</p>
        <p>Page 5 / 18</p>
    </footer>
</div>

<!-- SLIDE 6: Operational Analysis -->
<div class="slide report-prose" id="operational-analysis-page">
    <header class="report-header-container">[Same header structure]</header>
    <main style="display: flex; flex-direction: column; flex-grow: 1;">
        <section class="analysis-sections" style="flex-grow: 1;">
            <h3>4. OPERATIONAL ANALYSIS</h3>
            <p>[Operational metrics and performance]</p>
            <p>[Comprehensive paragraph 1 - 150-200 words of detailed analysis]</p>
            <p>[Comprehensive paragraph 2 - 150-200 words continuing analysis]</p>
            <p>[Comprehensive paragraph 3 - 150-200 words with conclusions]</p>
            <!-- REMOVED bullet-list-square structure, replaced with report-style paragraphs
                <h4>KEY OPERATIONAL METRICS:</h4>
                <!-- REMOVED ul structure: [Operational performance analysis] -->
        </section>
    </main>
    <footer class="report-footer">
        <p>Source: Robeco Internal Analysis, Bloomberg</p>
        <p>Page 6 / 18</p>
    </footer>
</div>

<!-- SLIDE 7: Key Strategic Initiative -->
<div class="slide report-prose" id="strategic-initiative-page">
    <header class="report-header-container">[Same header structure]</header>
    <main style="display: flex; flex-direction: column; flex-grow: 1;">
        <section class="analysis-sections" style="flex-grow: 1;">
            <h3>5. KEY STRATEGIC INITIATIVES</h3>
            <p>[Strategic initiative analysis]</p>
            <p>[Comprehensive paragraph 1 - 150-200 words of detailed analysis]</p>
            <p>[Comprehensive paragraph 2 - 150-200 words continuing analysis]</p>
            <p>[Comprehensive paragraph 3 - 150-200 words with conclusions]</p>
            <!-- REMOVED bullet-list-square structure, replaced with report-style paragraphs
                <h4>STRATEGIC FOCUS AREAS:</h4>
                <!-- REMOVED ul structure: [Strategic analysis with metrics] -->
        </section>
    </main>
    <footer class="report-footer">
        <p>Source: Robeco Internal Analysis, Bloomberg</p>
        <p>Page 7 / 18</p>
    </footer>
</div>

<!-- SLIDE 8: Industry Analysis (Part 1) -->
<div class="slide report-prose" id="industry-analysis-page-1">
    <header class="report-header-container">[Same header structure]</header>
    <main style="display: flex; flex-direction: column; flex-grow: 1;">
        <section class="analysis-sections" style="flex-grow: 1;">
            <h3>6. INDUSTRY ANALYSIS (PART 1)</h3>
            <p>[Industry dynamics and trends]</p>
            <p>[Comprehensive paragraph 1 - 150-200 words of detailed analysis]</p>
            <p>[Comprehensive paragraph 2 - 150-200 words continuing analysis]</p>
            <p>[Comprehensive paragraph 3 - 150-200 words with conclusions]</p>
            <!-- REMOVED bullet-list-square structure, replaced with report-style paragraphs
                <h4>INDUSTRY DYNAMICS:</h4>
                <!-- REMOVED ul structure: [Industry analysis with data points] -->
        </section>
    </main>
    <footer class="report-footer">
        <p>Source: Robeco Internal Analysis, Bloomberg</p>
        <p>Page 8 / 18</p>
    </footer>
</div>

<!-- SLIDE 9: Industry Analysis (Part 2) - Global Market Dynamics -->
<div class="slide report-prose" id="industry-analysis-page-2">
    <header class="report-header-container">[Same header structure]</header>
    <main style="display: flex; flex-direction: column; flex-grow: 1;">
        <section class="analysis-sections" style="flex-grow: 1;">
            <h3>7. INDUSTRY ANALYSIS (PART 2) - GLOBAL MARKET DYNAMICS</h3>
            <p>[Global market trends and competitive landscape]</p>
            <p>[Comprehensive paragraph 1 - 150-200 words of detailed analysis]</p>
            <p>[Comprehensive paragraph 2 - 150-200 words continuing analysis]</p>
            <p>[Comprehensive paragraph 3 - 150-200 words with conclusions]</p>
            <!-- REMOVED bullet-list-square structure, replaced with report-style paragraphs
                <h4>GLOBAL MARKET TRENDS:</h4>
                <!-- REMOVED ul structure: [Global market analysis] -->
        </section>
    </main>
    <footer class="report-footer">
        <p>Source: Robeco Internal Analysis, Bloomberg</p>
        <p>Page 9 / 18</p>
    </footer>
</div>

<!-- SLIDE 10: Industry Analysis (Part 3) - Sector-Specific Analysis -->
<div class="slide report-prose" id="industry-analysis-page-3">
    <header class="report-header-container">[Same header structure]</header>
    <main style="display: flex; flex-direction: column; flex-grow: 1;">
        <section class="analysis-sections" style="flex-grow: 1;">
            <h3>8. INDUSTRY ANALYSIS (PART 3) - SECTOR-SPECIFIC DYNAMICS</h3>
            <p>[Sector-specific trends and regulatory environment]</p>
            <p>[Comprehensive paragraph 1 - 150-200 words of detailed analysis]</p>
            <p>[Comprehensive paragraph 2 - 150-200 words continuing analysis]</p>
            <p>[Comprehensive paragraph 3 - 150-200 words with conclusions]</p>
            <!-- REMOVED bullet-list-square structure, replaced with report-style paragraphs
                <h4>SECTOR-SPECIFIC FACTORS:</h4>
                <!-- REMOVED ul structure: [Sector analysis with regulatory considerations] -->
        </section>
    </main>
    <footer class="report-footer">
        <p>Source: Robeco Internal Analysis, Bloomberg</p>
        <p>Page 10 / 18</p>
    </footer>
</div>

<!-- SLIDE 11: Financial Performance Highlights -->
<div class="slide report-prose" id="financial-performance-page">
    <header class="report-header-container">[Same header structure]</header>
    <main style="display: flex; flex-direction: column; flex-grow: 1;">
        <section class="analysis-sections" style="flex-grow: 1;">
            <h3>9. FINANCIAL PERFORMANCE HIGHLIGHTS</h3>
            <p>[Key financial metrics and performance trends]</p>
            <p>[Comprehensive paragraph 1 - 150-200 words of detailed analysis]</p>
            <p>[Comprehensive paragraph 2 - 150-200 words continuing analysis]</p>
            <p>[Comprehensive paragraph 3 - 150-200 words with conclusions]</p>
            <!-- REMOVED bullet-list-square structure, replaced with report-style paragraphs
                <h4>FINANCIAL HIGHLIGHTS:</h4>
                <!-- REMOVED ul structure: [Financial performance with specific metrics] -->
        </section>
    </main>
    <footer class="report-footer">
        <p>Source: Robeco Internal Analysis, Bloomberg</p>
        <p>Page 11 / 18</p>
    </footer>
</div>

<!-- SLIDE 12: Detailed Financial Statements - Income Statement -->
<div class="slide report-prose" id="income-statement-page">
    <header class="report-header-container">[Same header structure]</header>
    <main style="display: flex; flex-direction: column; flex-grow: 1;">
        <h3 class="section-title">5.1. DETAILED FINANCIAL STATEMENTS: INCOME STATEMENT - COMPREHENSIVE ANALYSIS</h3>
        
        <table class="compact-table">
            <thead>
                <tr>
                    <th style="font-family: Calibri, sans-serif;">METRIC</th>
                    <th style="text-align:right; font-family: Calibri, sans-serif;">FY22</th>
                    <th style="text-align:right; font-family: Calibri, sans-serif;">FY23</th>
                    <th style="text-align:right; font-family: Calibri, sans-serif;">FY24</th>
                    <th style="text-align:right; font-family: Calibri, sans-serif;">YoY Change</th>
                </tr>
            </thead>
            <tbody>
                <tr><td style="font-family: Calibri, sans-serif;">Revenue</td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="color: #228B22; font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td></tr>
                <tr><td style="font-family: Calibri, sans-serif;">Gross Profit</td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="color: #228B22; font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td></tr>
                <tr><td style="font-family: Calibri, sans-serif;">Gross Margin</td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="color: #228B22; font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td></tr>
                <tr><td style="font-family: Calibri, sans-serif;">Operating Income</td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="color: #228B22; font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td></tr>
                <tr><td style="font-family: Calibri, sans-serif;">Operating Margin</td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="color: #228B22; font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td></tr>
                <tr><td style="font-family: Calibri, sans-serif;">EBITDA</td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="color: #228B22; font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td></tr>
                <tr><td style="font-family: Calibri, sans-serif;">EBITDA Margin</td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="color: #228B22; font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td></tr>
                <tr><td style="font-family: Calibri, sans-serif;">Net Income</td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="color: #228B22; font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td></tr>
                <tr><td style="font-family: Calibri, sans-serif;">Net Margin</td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="color: #228B22; font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td></tr>
                <tr><td style="font-family: Calibri, sans-serif;">EPS</td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="color: #228B22; font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td></tr>
            </tbody>
        </table>
        <p style="margin-top: 4.5px; font-family: Calibri, sans-serif;">[Comprehensive income statement analysis paragraph 1 - 150-200 words analyzing revenue trends, growth drivers, and sustainability with specific metrics]</p>
        <p style="margin-top: 15px; font-family: Calibri, sans-serif;">[Comprehensive income statement analysis paragraph 2 - 150-200 words on profitability metrics, margin analysis, and operational leverage with detailed calculations]</p>
        <p style="margin-top: 15px; font-family: Calibri, sans-serif;">[Comprehensive income statement analysis paragraph 3 - 150-200 words on cost structure, efficiency, and competitive positioning with industry comparisons]</p>
        <p style="margin-top: 15px; font-family: Calibri, sans-serif;">[Comprehensive income statement analysis paragraph 4 - 150-200 words on outlook, risks, and earnings quality assessment with forward-looking projections]</p>
            <!-- REMOVED bullet-list-square structure, replaced with report-style paragraphs
                <h4>INCOME STATEMENT HIGHLIGHTS:</h4>
                <!-- REMOVED ul structure: [Revenue, profitability, and margin analysis] -->
        </section>
    </main>
    <footer class="report-footer">
        <p>Source: Robeco Internal Analysis, Bloomberg</p>
        <p>Page 12 / 18</p>
    </footer>
</div>

<!-- SLIDE 13: Detailed Financial Statements - Balance Sheet -->
<div class="slide report-prose" id="slide-financial-balance-sheet">
    <header class="report-header-container">[Same header structure]</header>
    <main style="display: flex; flex-direction: column; flex-grow: 1;">
        <h3 class="section-title">5.2. DETAILED FINANCIAL STATEMENTS: BALANCE SHEET - CAPITAL STRUCTURE ANALYSIS</h3>
        
        <table class="compact-table">
            <thead>
                <tr>
                    <th style="font-family: Calibri, sans-serif;">METRIC</th>
                    <th style="text-align:right; font-family: Calibri, sans-serif;">FY22</th>
                    <th style="text-align:right; font-family: Calibri, sans-serif;">FY23</th>
                    <th style="text-align:right; font-family: Calibri, sans-serif;">FY24</th>
                    <th style="text-align:right; font-family: Calibri, sans-serif;">YoY Change</th>
                </tr>
            </thead>
            <tbody>
                <tr><td style="font-family: Calibri, sans-serif;">Total Assets</td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="color: #228B22; font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td></tr>
                <tr><td style="font-family: Calibri, sans-serif;">Current Assets</td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="color: #228B22; font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td></tr>
                <tr><td style="font-family: Calibri, sans-serif;">Cash & Equivalents</td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="color: #228B22; font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td></tr>
                <tr><td style="font-family: Calibri, sans-serif;">Total Debt</td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="color: #DC143C; font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td></tr>
                <tr><td style="font-family: Calibri, sans-serif;">Net Debt</td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="color: #DC143C; font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td></tr>
                <tr><td style="font-family: Calibri, sans-serif;">Shareholders' Equity</td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="color: #228B22; font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td></tr>
                <tr><td style="font-family: Calibri, sans-serif;">Book Value per Share</td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="color: #228B22; font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td></tr>
                <tr><td style="font-family: Calibri, sans-serif;">Debt-to-Equity</td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="color: #DC143C; font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td></tr>
                <tr><td style="font-family: Calibri, sans-serif;">Current Ratio</td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="color: #228B22; font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td></tr>
                <tr><td style="font-family: Calibri, sans-serif;">Return on Equity</td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="color: #228B22; font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td></tr>
            </tbody>
        </table>
        <p style="margin-top: 4.5px; font-family: Calibri, sans-serif;">[Comprehensive balance sheet analysis paragraph 1 - 150-200 words analyzing asset composition, quality, and efficiency with specific metrics]</p>
        <p style="margin-top: 15px; font-family: Calibri, sans-serif;">[Comprehensive balance sheet analysis paragraph 2 - 150-200 words on capital structure, leverage analysis, and debt sustainability with detailed calculations]</p>
        <p style="margin-top: 15px; font-family: Calibri, sans-serif;">[Comprehensive balance sheet analysis paragraph 3 - 150-200 words on liquidity position, working capital management, and financial flexibility]</p>
        <p style="margin-top: 15px; font-family: Calibri, sans-serif;">[Comprehensive balance sheet analysis paragraph 4 - 150-200 words on equity valuation, book value trends, and capital efficiency metrics]</p>
            <!-- REMOVED bullet-list-square structure, replaced with report-style paragraphs
                <h4>BALANCE SHEET HIGHLIGHTS:</h4>
                <!-- REMOVED ul structure: [Asset quality, debt levels, and capital structure] -->
        </section>
    </main>
    <footer class="report-footer">
        <p>Source: Robeco Internal Analysis, Bloomberg</p>
        <p>Page 13 / 18</p>
    </footer>
</div>

<!-- SLIDE 14: Detailed Financial Statements - Cash Flow Statement -->
<div class="slide report-prose" id="cash-flow-page">
    <header class="report-header-container">[Same header structure]</header>
    <main style="display: flex; flex-direction: column; flex-grow: 1;">
        <h3 class="section-title">5.3. DETAILED FINANCIAL STATEMENTS: CASH FLOW - CAPITAL ALLOCATION ANALYSIS</h3>
        
        <table class="compact-table">
            <thead>
                <tr>
                    <th style="font-family: Calibri, sans-serif;">METRIC</th>
                    <th style="text-align:right; font-family: Calibri, sans-serif;">FY22</th>
                    <th style="text-align:right; font-family: Calibri, sans-serif;">FY23</th>
                    <th style="text-align:right; font-family: Calibri, sans-serif;">FY24</th>
                    <th style="text-align:right; font-family: Calibri, sans-serif;">YoY Change</th>
                </tr>
            </thead>
            <tbody>
                <tr><td style="font-family: Calibri, sans-serif;">Operating Cash Flow</td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="color: #228B22; font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td></tr>
                <tr><td style="font-family: Calibri, sans-serif;">Capital Expenditures</td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="color: #DC143C; font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td></tr>
                <tr><td style="font-family: Calibri, sans-serif;">Free Cash Flow</td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="color: #228B22; font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td></tr>
                <tr><td style="font-family: Calibri, sans-serif;">FCF Conversion Rate</td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="color: #228B22; font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td></tr>
                <tr><td style="font-family: Calibri, sans-serif;">Dividends Paid</td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="color: #DC143C; font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td></tr>
                <tr><td style="font-family: Calibri, sans-serif;">Share Repurchases</td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="color: #DC143C; font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td></tr>
                <tr><td style="font-family: Calibri, sans-serif;">Net Debt Issuance</td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="color: #DC143C; font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td></tr>
                <tr><td style="font-family: Calibri, sans-serif;">Working Capital Change</td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="color: #228B22; font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td></tr>
                <tr><td style="font-family: Calibri, sans-serif;">FCF Yield</td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="color: #228B22; font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td></tr>
                <tr><td style="font-family: Calibri, sans-serif;">Cash Conversion Cycle</td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td><td style="color: #228B22; font-family: Calibri, sans-serif;"><strong>[CALCULATE]</strong></td></tr>
            </tbody>
        </table>
        <p style="margin-top: 4.5px; font-family: Calibri, sans-serif;">[Comprehensive cash flow analysis paragraph 1 - 150-200 words analyzing operating cash flow generation, quality, and sustainability with specific metrics]</p>
        <p style="margin-top: 15px; font-family: Calibri, sans-serif;">[Comprehensive cash flow analysis paragraph 2 - 150-200 words on capital allocation strategy, investment returns, and capex efficiency]</p>
        <p style="margin-top: 15px; font-family: Calibri, sans-serif;">[Comprehensive cash flow analysis paragraph 3 - 150-200 words on shareholder returns, dividend policy, and free cash flow utilization]</p>
        <p style="margin-top: 15px; font-family: Calibri, sans-serif;">[Comprehensive cash flow analysis paragraph 4 - 150-200 words on working capital management, cash conversion cycle, and liquidity assessment]</p>
            <!-- REMOVED bullet-list-square structure, replaced with report-style paragraphs
                <h4>CASH FLOW HIGHLIGHTS:</h4>
                <!-- REMOVED ul structure: [Operating cash flow, capex, and free cash flow] -->
        </section>
    </main>
    <footer class="report-footer">
        <p>Source: Robeco Internal Analysis, Bloomberg</p>
        <p>Page 14 / 18</p>
    </footer>
</div>

<!-- SLIDE 15: DCF Analysis -->
<div class="slide report-prose" id="dcf-analysis-page">
    <header class="report-header-container">[Same header structure]</header>
    <main style="display: flex; flex-direction: column; flex-grow: 1;">
        <section class="analysis-sections" style="flex-grow: 1;">
            <h3>13. DCF ANALYSIS</h3>
            <p>[DCF model assumptions and valuation]</p>
            <p>[Comprehensive paragraph 1 - 150-200 words of detailed analysis]</p>
            <p>[Comprehensive paragraph 2 - 150-200 words continuing analysis]</p>
            <p>[Comprehensive paragraph 3 - 150-200 words with conclusions]</p>
            <!-- REMOVED bullet-list-square structure, replaced with report-style paragraphs
                <h4>DCF ASSUMPTIONS:</h4>
                <!-- REMOVED ul structure: [WACC, growth rates, and valuation multiples] -->
        </section>
    </main>
    <footer class="report-footer">
        <p>Source: Robeco Internal Analysis, Bloomberg</p>
        <p>Page 15 / 18</p>
    </footer>
</div>

<!-- SLIDE 16: Bull-Bear Analysis -->
<div class="slide report-prose" id="bull-bear-analysis-page">
    <header class="report-header-container">[Same header structure]</header>
    <main style="display: flex; flex-direction: column; flex-grow: 1;">
        <section class="analysis-sections" style="flex-grow: 1;">
            <h3>14. BULL-BEAR SCENARIO ANALYSIS</h3>
            <p>[Scenario analysis with upside and downside cases]</p>
            <p>[Comprehensive paragraph 1 - 150-200 words of detailed analysis]</p>
            <p>[Comprehensive paragraph 2 - 150-200 words continuing analysis]</p>
            <p>[Comprehensive paragraph 3 - 150-200 words with conclusions]</p>
            <!-- REMOVED bullet-list-square structure, replaced with report-style paragraphs
                <h4>SCENARIO ASSUMPTIONS:</h4>
                <!-- REMOVED ul structure: [Bull case, bear case, and base case analysis] -->
        </section>
    </main>
    <footer class="report-footer">
        <p>Source: Robeco Internal Analysis, Bloomberg</p>
        <p>Page 16 / 18</p>
    </footer>
</div>

<!-- SLIDE 17: ESG Analysis -->
<div class="slide report-prose" id="esg-analysis-page">
    <header class="report-header-container">[Same header structure]</header>
    <main style="display: flex; flex-direction: column; flex-grow: 1;">
        <section class="analysis-sections" style="flex-grow: 1;">
            <h3>15. ESG ANALYSIS</h3>
            <p>[Environmental, Social, and Governance assessment]</p>
            <p>[Comprehensive paragraph 1 - 150-200 words of detailed analysis]</p>
            <p>[Comprehensive paragraph 2 - 150-200 words continuing analysis]</p>
            <p>[Comprehensive paragraph 3 - 150-200 words with conclusions]</p>
            <!-- REMOVED bullet-list-square structure, replaced with report-style paragraphs
                <h4>ESG FACTORS:</h4>
                <!-- REMOVED ul structure: [ESG score, sustainability initiatives, governance quality] -->
        </section>
    </main>
    <footer class="report-footer">
        <p>Source: Robeco Internal Analysis, Bloomberg</p>
        <p>Page 17 / 18</p>
    </footer>
</div>

<!-- SLIDE 18: Corporate Governance & Shareholders -->
<div class="slide report-prose" id="governance-page">
    <header class="report-header-container">[Same header structure]</header>
    <main style="display: flex; flex-direction: column; flex-grow: 1;">
        <section class="analysis-sections" style="flex-grow: 1;">
            <h3>16. CORPORATE GOVERNANCE & SHAREHOLDERS</h3>
            <p>[Corporate governance structure and shareholder analysis]</p>
            <p>[Comprehensive paragraph 1 - 150-200 words of detailed analysis]</p>
            <p>[Comprehensive paragraph 2 - 150-200 words continuing analysis]</p>
            <p>[Comprehensive paragraph 3 - 150-200 words with conclusions]</p>
            <!-- REMOVED bullet-list-square structure, replaced with report-style paragraphs
                <h4>GOVERNANCE HIGHLIGHTS:</h4>
                <!-- REMOVED ul structure: [Board composition, management quality, shareholder structure] -->
        </section>
    </main>
    <footer class="report-footer">
        <p>Source: Robeco Internal Analysis, Bloomberg</p>
        <p>Page 18 / 18</p>
    </footer>
</div>
"""
        
        return structure_template
    
    async def _generate_ai_report(self, prompt: str, websocket=None, connection_id: str = None) -> str:
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
                    max_output_tokens=200000,  # MAXIMIZED for complete 18-slide template structure
                    response_mime_type="text/plain",
                    system_instruction="You are a Managing Director at Robeco writing institutional-grade investment research. CRITICAL: Generate comprehensive, detailed analysis - NOT brief summaries. Each paragraph must be 150-300 words, each bullet point 80-150 words with specific metrics and detailed analysis. Follow EXACT 18-slide template structure. Generate ALL 18 slides with deep, professional investment banking analysis matching the template's sophistication. Use exact CSS classes and section titles. Include specific financial projections, competitive analysis, and quantitative assessments with bold metrics throughout."
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
                
                # Use streaming to get real content as it generates with enhanced completion tracking
                try:
                    last_chunk_text = ""
                    for chunk in client.models.generate_content_stream(
                        model='gemini-2.0-flash-exp',
                        contents=contents,
                        config=generate_config,
                    ):
                        if chunk.text:
                            chunk_count += 1
                            accumulated_response += chunk.text
                            last_chunk_text = chunk.text
                            
                            # Log first chunk content to see what AI is generating
                            if chunk_count == 1:
                                logger.info(f"📝 FIRST CHUNK: {chunk.text[:300]}...")
                            
                            # Enhanced progress tracking with completion detection
                            contains_html_end = '</html>' in accumulated_response.lower()
                            contains_body_end = '</body>' in accumulated_response.lower()
                            
                            # Send real-time streaming updates to frontend if websocket available
                            if websocket and connection_id:
                                try:
                                    progress = min(30 + (chunk_count * 2), 95)  # Cap at 95% until complete
                                    if contains_html_end:
                                        progress = 95  # Near completion when HTML end detected
                                    
                                    await websocket.send_text(json.dumps({
                                        "type": "report_generation_streaming",
                                        "data": {
                                            "status": "streaming_html",
                                            "html_chunk": chunk.text,
                                            "accumulated_html": accumulated_response,
                                            "chunk_number": chunk_count,
                                            "progress": progress,
                                            "message": f"🤖 AI generating {'(COMPLETING)' if contains_html_end else 'content'}... ({chunk_count} chunks, {len(accumulated_response):,} chars)",
                                            "connection_id": connection_id,
                                            "timestamp": datetime.now().isoformat(),
                                            "completion_indicators": {
                                                "has_html_end": contains_html_end,
                                                "has_body_end": contains_body_end
                                            }
                                        }
                                    }))
                                except Exception as ws_error:
                                    logger.warning(f"WebSocket streaming failed: {ws_error}")
                                    # Continue without websocket streaming
                            
                            # Enhanced milestone logging with completion tracking
                            if chunk_count in [50, 100, 200, 500] or chunk_count % 100 == 0:
                                logger.info(f"📊 Progress: {chunk_count} chunks, {len(accumulated_response):,} chars, HTML_END: {contains_html_end}")
                                
                    # Log completion analysis
                    logger.info(f"📄 Final chunk text: {last_chunk_text[-100:] if last_chunk_text else 'N/A'}")
                    
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
            
            # Find the body section in CSS template and replace content
            if '<body>' in css_template and '</body>' in css_template:
                # Extract everything before <body> tag (including <body>)
                body_start = css_template.find('<body>')
                head_section = css_template[:body_start + 6]  # Include <body>
                
                # Create the complete HTML
                complete_html = head_section + '\n' + clean_slides + '\n</body>\n</html>'
                
                logger.info(f"✅ Successfully combined fixed CSS with AI slide content")
                logger.info(f"📊 Final HTML: {len(complete_html):,} characters")
                
                return complete_html
            else:
                # Fallback if CSS template structure is unexpected
                logger.warning("⚠️ CSS template doesn't have expected <body> structure, using fallback")
                
                fallback_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Robeco - {company_name} Investment Analysis</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .slide {{ padding: 30px; border-bottom: 1px solid #eee; }}
        h2 {{ color: #2c3e50; margin-bottom: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        {clean_slides}
    </div>
</body>
</html>'''
                return fallback_html
                
        except Exception as e:
            logger.error(f"❌ Failed to load CSS template: {e}")
            
            # Last resort fallback with basic styling
            fallback_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Robeco - {company_name} Investment Analysis</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
        .slide {{ margin-bottom: 40px; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }}
        h2 {{ color: #333; border-bottom: 2px solid #007acc; padding-bottom: 10px; }}
    </style>
</head>
<body>
    <h1>Investment Analysis: {company_name} ({ticker})</h1>
    {slides_content.strip()}
</body>
</html>'''
            logger.info(f"✅ Used last resort fallback HTML")
            return fallback_html
    
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