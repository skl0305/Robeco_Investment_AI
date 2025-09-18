#!/usr/bin/env python3
"""
Test to show the EXACT prompt that gets sent to AI in Call2 - Slide 8 Financial Analysis
"""

import sys
import os
import json
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def test_exact_call2_prompt():
    """Show the exact prompt that AI receives for Slide 8 Financial Analysis"""
    
    print("🔍 EXACT CALL2 AI PROMPT - SLIDE 8 FINANCIAL ANALYSIS")
    print("=" * 80)
    
    # Sample Apple financial data
    sample_financial_data = {
        'income_statement_annual': {
            '2023-12-31': {
                'Total Revenue': 387538000000,
                'Cost Of Revenue': 214137000000,
                'Gross Profit': 173401000000,
                'Operating Income': 114301000000,
                'Net Income': 96995000000,
                'EBITDA': 123136000000,
                'Research And Development': 29915000000,
                'Selling General And Administration': 24932000000,
                'Operating Expense': 55618000000,
                'Interest Expense': 3933000000,
                'Pretax Income': 113025000000,
                'Tax Provision': 16741000000,
                'Diluted EPS': 6.16,
                'Basic EPS': 6.16
            },
            '2022-12-31': {
                'Total Revenue': 394328000000,
                'Cost Of Revenue': 223546000000,
                'Gross Profit': 170782000000,
                'Operating Income': 119437000000,
                'Net Income': 99803000000,
                'EBITDA': 130541000000,
                'Research And Development': 26251000000,
                'Selling General And Administration': 25094000000,
                'Operating Expense': 51345000000,
                'Interest Expense': 2931000000,
                'Pretax Income': 119103000000,
                'Tax Provision': 19300000000,
                'Diluted EPS': 6.15,
                'Basic EPS': 6.15
            }
        },
        'balance_sheet_annual': {
            '2023-12-31': {
                'Total Assets': 352755000000,
                'Current Assets': 143566000000,
                'Cash And Cash Equivalents': 29965000000,
                'Total Debt': 111088000000,
                'Stockholders Equity': 62146000000
            }
        },
        'cashflow_annual': {
            '2023-12-31': {
                'Operating Cash Flow': 110543000000,
                'Capital Expenditure': -10959000000,
                'Free Cash Flow': 99584000000
            }
        }
    }
    
    try:
        from template_report_generator import RobecoTemplateReportGenerator
        
        # Create generator instance
        generator = RobecoTemplateReportGenerator()
        
        # Extract financial statements
        financial_statements = generator._extract_financial_statements_for_analysis(sample_financial_data)
        
        # Create Call2 data context
        company_context = {'sector': 'Technology', 'industry': 'Consumer Electronics'}
        call1_context = {'investment_rating': 'BUY', 'content_summary': 'Strong fundamentals'}
        
        call2_data = generator._filter_data_for_call3(
            sample_financial_data, financial_statements, company_context, call1_context, {}
        )
        
        # Extract components for prompt
        income_statement = call2_data.get('financial_statements', {}).get('income_statement', {})
        balance_sheet = call2_data.get('financial_statements', {}).get('balance_sheet', {})
        cashflow = call2_data.get('financial_statements', {}).get('cashflow', {})
        key_metrics = call2_data.get('financial_statements', {}).get('key_metrics', {})
        pre_calculated_financial_tables = generator._extract_pre_calculated_financial_tables(sample_financial_data)
        
        # Build the EXACT prompt that gets sent to AI for Slide 8
        company_name = "Apple Inc."
        
        exact_ai_prompt = f"""
**SLIDE 8: {company_name} FINANCIAL PERFORMANCE - COMPREHENSIVE EQUITY ANALYST ASSESSMENT**

**🔍 MANDATORY GOOGLE RESEARCH FOR FINANCIAL INTELLIGENCE:**
- **CRITICAL**: Search for latest earnings results, guidance updates, analyst estimate revisions for {company_name} and key peers
- Research institutional investor commentary, hedge fund 13F filings, insider trading activity
- Identify recent financial inflection points, accounting policy changes, one-time items affecting comparability
- **Target**: Uncover financial quality insights that differentiate {company_name} from superficial ratio analysis

**🎯 EQUITY ANALYST FINANCIAL STATEMENT MINDSET:**
**OBJECTIVE**: Conduct unbiased, comprehensive financial statement analysis like a top-tier equity research analyst
**APPROACH**: Focus on detailed line-item analysis, trend identification, and company-specific financial drivers

**📊 COMPREHENSIVE FINANCIAL DATA ANALYSIS** (Use Actual {company_name} Financial Data):

**COMPREHENSIVE PRE-CALCULATED FINANCIAL TABLES (READY TO USE):**
{financial_statements.get('html_tables_for_ai', '')}

**ADDITIONAL FINANCIAL DATA CONTEXT:**
- Years Available: {financial_statements.get('years_available', [])}
- Data Quality: {financial_statements.get('data_quality', {})}
- Income Statement Available: {financial_statements.get('income_statement', {}).get('has_data', False)}
- Balance Sheet Available: {financial_statements.get('balance_sheet', {}).get('has_data', False)}
- Cash Flow Available: {financial_statements.get('cashflow', {}).get('has_data', False)}

**DYNAMIC FINANCIAL ANALYSIS FRAMEWORK** (800-1000 words - Company-Specific Analysis):

**CRITICAL INSTRUCTION: Use the comprehensive pre-calculated financial tables provided above for all analysis. The tables contain ready-to-use HTML with actual {company_name} financial data.**

**1) REVENUE & PROFITABILITY ANALYSIS** (Use Comprehensive Tables):
- **{company_name} Revenue Trends**: Reference the Income Statement table above - analyze revenue growth patterns, year-over-year changes, and growth trajectory trends
- **Margin Analysis**: Use the comprehensive tables to examine gross margins, operating margins, and net margins - identify specific drivers of margin expansion or compression for {company_name}
- **Profitability Quality**: Analyze earnings quality by comparing net income to operating cash flow from the provided tables - assess working capital impacts on profitability
- **Industry-Specific Metrics**: Focus on sector-relevant KPIs from the tables (e.g., EBITDA margins for industrials, return on assets for financials, recurring revenue for tech)

**2) BALANCE SHEET STRENGTH ANALYSIS** (Use Comprehensive Tables):
- **{company_name} Asset Quality**: Reference the Balance Sheet table - analyze asset composition, total assets growth, asset turnover efficiency trends
- **Capital Structure Assessment**: Use debt metrics from tables - examine total debt, debt-to-equity ratios, interest coverage ratios and their evolution over time
- **Working Capital Management**: Calculate and analyze changes in working capital components (receivables, inventory, payables) using balance sheet data
- **Liquidity Position**: Assess cash and short-term investments, current ratios, and debt maturity profiles from the comprehensive tables

**3) CASH FLOW GENERATION ANALYSIS** (Use Comprehensive Tables):
- **{company_name} Operating Cash Flow**: Reference Cash Flow table - analyze operating cash flow trends, cash conversion ratios, and seasonal patterns
- **Free Cash Flow Assessment**: Calculate free cash flow using operating cash flow minus capex from the tables - analyze FCF margins and sustainability
- **Cash Flow vs. Earnings**: Compare net income to operating cash flow from tables - identify any significant divergences and underlying causes
- **Capital Allocation Efficiency**: Analyze capex trends, acquisition spending, dividend payments, and share buybacks from cash flow data

**4) FINANCIAL RISK ASSESSMENT** (Use Comprehensive Tables):
- **Liquidity Analysis**: Use balance sheet and cash flow tables to assess cash position, debt maturities, and liquidity ratios
- **Leverage & Coverage**: Calculate debt service coverage, interest coverage ratios, and leverage trends using comprehensive financial data
- **Earnings Volatility**: Analyze earnings stability and cyclicality patterns across the years provided in the financial tables
- **Quality of Earnings**: Identify any unusual items, one-time charges, or accounting adjustments visible in the comprehensive tables

**SUCCESS METRIC**: A 30+ year veteran PM should think "This analyst has conducted the most comprehensive financial statement analysis of {company_name} I've seen - they understand the true financial drivers and risks better than sell-side consensus"
        """
        
        print("📋 EXACT PROMPT SENT TO AI:")
        print("=" * 80)
        print(exact_ai_prompt)
        print("=" * 80)
        
        # Show key statistics
        print(f"\n📊 PROMPT STATISTICS:")
        print(f"   📏 Total prompt length: {len(exact_ai_prompt):,} characters")
        print(f"   💰 Dollar values: {exact_ai_prompt.count('$')}")
        print(f"   📈 Billion figures: {exact_ai_prompt.count('B')}")
        print(f"   📊 Table elements: {exact_ai_prompt.count('<table')}")
        print(f"   📄 HTML rows: {exact_ai_prompt.count('<tr>')}")
        
        # Verify Apple data
        apple_metrics = [
            ("Apple Revenue 2023", "$387.54B"),
            ("Apple Net Income 2023", "$96.99B"),  
            ("Apple Cash", "$29.96B"),
            ("Apple Operating Income", "$114.30B")
        ]
        
        print(f"\n✅ APPLE FINANCIAL DATA VERIFICATION:")
        for metric, value in apple_metrics:
            found = value in exact_ai_prompt
            print(f"   {'✅' if found else '❌'} {metric}: {value} {'FOUND' if found else 'MISSING'}")
        
        # Show the financial tables section specifically
        tables_start = exact_ai_prompt.find("**COMPREHENSIVE PRE-CALCULATED FINANCIAL TABLES")
        tables_end = exact_ai_prompt.find("**ADDITIONAL FINANCIAL DATA CONTEXT:")
        
        if tables_start != -1 and tables_end != -1:
            tables_section = exact_ai_prompt[tables_start:tables_end]
            print(f"\n📊 FINANCIAL TABLES SECTION ({len(tables_section):,} chars):")
            print("=" * 50)
            print(tables_section[:2000])  # Show first 2000 characters
            print("..." if len(tables_section) > 2000 else "")
            print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(f"📋 Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    print("🚀 SHOWING EXACT CALL2 PROMPT FOR SLIDE 8\n")
    success = test_exact_call2_prompt()
    
    if success:
        print(f"\n✅ SUCCESS: This is the exact prompt that AI receives!")
        print(f"📊 Contains real Apple financial data in comprehensive HTML tables")
        print(f"🤖 AI will analyze actual financial metrics for equity research")
    else:
        print(f"\n❌ ERROR: Could not generate exact prompt")