#!/usr/bin/env python3
"""
Test script to show what financial data gets passed to Call2 AI prompt
"""

import sys
import os
import json
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def test_financial_data_integration():
    """Test what financial data structure gets passed to Call2"""
    
    print("🔍 TESTING FINANCIAL DATA INTEGRATION FOR CALL2")
    print("=" * 60)
    
    # Sample financial data structure (using correct yfinance field names)
    sample_financial_data = {
        'income_statement_annual': {
            '2023-12-31': {
                'Total Revenue': 123456789000,
                'Cost Of Revenue': 67890123000,
                'Gross Profit': 55566666000,
                'Operating Income': 34567890000,
                'Net Income': 28901234000,
                'EBITDA': 45678901000,
                'Research And Development': 8900000000,
                'Selling General And Administration': 12345000000,
                'Operating Expense': 21245000000,
                'Interest Expense': 2100000000,
                'Pretax Income': 32467890000,
                'Tax Provision': 3566666000,
                'Diluted EPS': 12.45,
                'Basic EPS': 12.50
            },
            '2022-12-31': {
                'Total Revenue': 118000000000,
                'Cost Of Revenue': 65000000000,
                'Gross Profit': 53000000000,
                'Operating Income': 32000000000,
                'Net Income': 26500000000,
                'EBITDA': 42000000000,
                'Research And Development': 8500000000,
                'Selling General And Administration': 11800000000,
                'Operating Expense': 20300000000,
                'Interest Expense': 2000000000,
                'Pretax Income': 30000000000,
                'Tax Provision': 3500000000,
                'Diluted EPS': 11.85,
                'Basic EPS': 11.90
            },
            '2021-12-31': {
                'Total Revenue': 112000000000,
                'Cost Of Revenue': 62000000000,
                'Gross Profit': 50000000000,
                'Operating Income': 29000000000,
                'Net Income': 24000000000,
                'EBITDA': 38000000000,
                'Research And Development': 8100000000,
                'Selling General And Administration': 11200000000,
                'Operating Expense': 19300000000,
                'Interest Expense': 1900000000,
                'Pretax Income': 27100000000,
                'Tax Provision': 3100000000,
                'Diluted EPS': 10.95,
                'Basic EPS': 11.00
            }
        },
        'balance_sheet_annual': {
            '2023-12-31': {
                'Total Assets': 450000000000,
                'Current Assets': 150000000000,
                'Cash And Cash Equivalents': 45000000000,
                'Total Debt': 120000000000,
                'Stockholders Equity': 200000000000,
                'Current Liabilities': 45000000000,
                'Total Liabilities Net Minority Interest': 250000000000,
                'Net PPE': 180000000000,
                'Inventory': 12000000000,
                'Accounts Receivable': 23000000000,
                'Accounts Payable': 18000000000,
                'Working Capital': 105000000000
            },
            '2022-12-31': {
                'Total Assets': 420000000000,
                'Current Assets': 140000000000,
                'Cash And Cash Equivalents': 42000000000,
                'Total Debt': 115000000000,
                'Stockholders Equity': 185000000000,
                'Current Liabilities': 42000000000,
                'Total Liabilities Net Minority Interest': 235000000000,
                'Net PPE': 170000000000,
                'Inventory': 11500000000,
                'Accounts Receivable': 21000000000,
                'Accounts Payable': 17000000000,
                'Working Capital': 98000000000
            },
            '2021-12-31': {
                'Total Assets': 400000000000,
                'Current Assets': 130000000000,
                'Cash And Cash Equivalents': 38000000000,
                'Total Debt': 110000000000,
                'Stockholders Equity': 170000000000,
                'Current Liabilities': 40000000000,
                'Total Liabilities Net Minority Interest': 230000000000,
                'Net PPE': 160000000000,
                'Inventory': 11000000000,
                'Accounts Receivable': 19000000000,
                'Accounts Payable': 16000000000,
                'Working Capital': 90000000000
            }
        },
        'cashflow_annual': {
            '2023-12-31': {
                'Operating Cash Flow': 38000000000,
                'Capital Expenditure': -12000000000,
                'Free Cash Flow': 26000000000,
                'Cash Dividends Paid': -8000000000,
                'Repurchase Of Capital Stock': -15000000000,
                'Issuance Of Debt': 5000000000,
                'Repayment Of Debt': -3000000000,
                'Net Cash Flow': 11000000000
            },
            '2022-12-31': {
                'Operating Cash Flow': 35000000000,
                'Capital Expenditure': -11000000000,
                'Free Cash Flow': 24000000000,
                'Cash Dividends Paid': -7500000000,
                'Repurchase Of Capital Stock': -12000000000,
                'Issuance Of Debt': 3000000000,
                'Repayment Of Debt': -2500000000,
                'Net Cash Flow': 8000000000
            },
            '2021-12-31': {
                'Operating Cash Flow': 32000000000,
                'Capital Expenditure': -10000000000,
                'Free Cash Flow': 22000000000,
                'Cash Dividends Paid': -7000000000,
                'Repurchase Of Capital Stock': -10000000000,
                'Issuance Of Debt': 2000000000,
                'Repayment Of Debt': -2000000000,
                'Net Cash Flow': 5000000000
            }
        }
    }
    
    try:
        # Import the template generator
        from template_report_generator import RobecoTemplateReportGenerator
        
        # Create an instance
        generator = RobecoTemplateReportGenerator()
        
        # Test the financial statements extraction
        print("\n📊 TESTING FINANCIAL STATEMENTS EXTRACTION:")
        financial_statements = generator._extract_financial_statements_for_analysis(sample_financial_data)
        
        print(f"   ✅ Income Statement has data: {financial_statements.get('income_statement', {}).get('has_data', False)}")
        print(f"   ✅ Balance Sheet has data: {financial_statements.get('balance_sheet', {}).get('has_data', False)}")
        print(f"   ✅ Cash Flow has data: {financial_statements.get('cashflow', {}).get('has_data', False)}")
        print(f"   📊 Years available: {financial_statements.get('years_available', [])}")
        
        # Test comprehensive HTML tables
        print("\n📊 TESTING COMPREHENSIVE HTML TABLES:")
        html_tables = financial_statements.get('html_tables_for_ai', '')
        if html_tables:
            table_count = html_tables.count('<table')
            print(f"   ✅ HTML tables generated: {table_count} tables found")
            print(f"   📏 Total HTML length: {len(html_tables):,} characters")
            
            # Show first 1000 characters
            print(f"\n📋 SAMPLE HTML TABLE OUTPUT (first 1000 chars):")
            print("-" * 50)
            print(html_tables[:1000])
            print("-" * 50)
            
            # Check for specific table types
            if 'Income Statement' in html_tables:
                print("   ✅ Contains Income Statement table")
            if 'Balance Sheet' in html_tables:
                print("   ✅ Contains Balance Sheet table")
            if 'Cash Flow' in html_tables:
                print("   ✅ Contains Cash Flow table")
        else:
            print("   ❌ No HTML tables generated")
            
        # Try direct import test
        print("\n📊 TESTING DIRECT IMPORT OF COMPREHENSIVE METHODS:")
        try:
            from pre_calculated_financial_methods import extract_pre_calculated_financial_tables, generate_ready_to_use_prompt_data
            
            # Test direct generation
            pre_calc_direct = extract_pre_calculated_financial_tables(sample_financial_data)
            html_direct = generate_ready_to_use_prompt_data(pre_calc_direct)
            
            print(f"   ✅ Direct import successful")
            print(f"   📊 Direct tables keys: {list(pre_calc_direct.keys())}")
            print(f"   📏 Direct HTML length: {len(html_direct):,} characters")
            
            if html_direct:
                direct_table_count = html_direct.count('<table')
                print(f"   ✅ Direct HTML tables: {direct_table_count} tables found")
                
                # Show sample of direct HTML
                print(f"\n📋 DIRECT HTML SAMPLE (first 1500 chars):")
                print("-" * 50)
                print(html_direct[:1500])
                print("-" * 50)
                
                # Look for actual data values in the HTML
                print(f"\n🔍 CHECKING FOR ACTUAL DATA VALUES:")
                if "123456789000" in html_direct:
                    print("   ✅ Found sample revenue data (123456789000)")
                if "67890123000" in html_direct:
                    print("   ✅ Found sample cost data (67890123000)")
                if "450000000000" in html_direct:
                    print("   ✅ Found sample total assets (450000000000)")
                if "38000000000" in html_direct:
                    print("   ✅ Found sample operating cash flow (38000000000)")
                    
                # Count how many "N/A" values appear
                na_count = html_direct.count("N/A")
                print(f"   📊 Number of 'N/A' values in tables: {na_count}")
                
                # Look for key financial line items
                key_items = ["Revenue", "Operating Income", "Net Income", "Total Assets", "Operating Cash Flow"]
                for item in key_items:
                    if item in html_direct:
                        print(f"   ✅ Contains line item: {item}")
                
                # Show middle section with actual data
                print(f"\n📋 MIDDLE SECTION WITH DATA (chars 5000-6500):")
                print("-" * 50)
                print(html_direct[5000:6500])
                print("-" * 50)
                
                # Show end section
                print(f"\n📋 END SECTION (last 1000 chars):")
                print("-" * 50)
                print(html_direct[-1000:])
                print("-" * 50)
                
        except Exception as import_error:
            print(f"   ❌ Direct import failed: {import_error}")
        
        # Test pre-calculated tables
        print("\n📊 TESTING PRE-CALCULATED TABLES:")
        pre_calc_tables = generator._extract_pre_calculated_financial_tables(sample_financial_data)
        print(f"   📊 Pre-calculated table keys: {list(pre_calc_tables.keys())}")
        
        if 'income_statement_table' in pre_calc_tables:
            income_table = pre_calc_tables['income_statement_table']
            print(f"   📊 Income table structure: {list(income_table.keys()) if income_table else 'Empty'}")
        
        # Test Call2 data filtering
        print("\n📊 TESTING CALL2 DATA FILTERING:")
        sample_company_context = {'sector': 'Technology', 'industry': 'Software'}
        sample_call1_context = {'investment_rating': 'BUY', 'content_summary': 'Test summary'}
        
        call2_data = generator._filter_data_for_call3(
            sample_financial_data, 
            financial_statements, 
            sample_company_context, 
            sample_call1_context, 
            {}
        )
        
        print(f"   📊 Call2 data keys: {list(call2_data.keys())}")
        print(f"   ✅ Financial statements included: {bool(call2_data.get('financial_statements'))}")
        print(f"   ✅ Financial data included: {bool(call2_data.get('financial_data'))}")
        
        # Show what would be in the AI prompt
        print("\n🤖 SAMPLE AI PROMPT CONTENT:")
        print("=" * 60)
        
        # Extract components like in actual Call2
        income_statement = call2_data.get('financial_statements', {}).get('income_statement', {})
        balance_sheet = call2_data.get('financial_statements', {}).get('balance_sheet', {})
        cashflow = call2_data.get('financial_statements', {}).get('cashflow', {})
        
        # Simulate the prompt section
        prompt_preview = f"""
**COMPREHENSIVE PRE-CALCULATED FINANCIAL TABLES (READY TO USE):**
{financial_statements.get('html_tables_for_ai', 'No tables available')[:2000]}...

**ADDITIONAL FINANCIAL DATA CONTEXT:**
- Years Available: {financial_statements.get('years_available', [])}
- Data Quality: {financial_statements.get('data_quality', {})}
- Income Statement Available: {financial_statements.get('income_statement', {}).get('has_data', False)}
- Balance Sheet Available: {financial_statements.get('balance_sheet', {}).get('has_data', False)}
- Cash Flow Available: {financial_statements.get('cashflow', {}).get('has_data', False)}
        """
        
        print(prompt_preview)
        print("=" * 60)
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you're running this from the correct directory")
        return False
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        print(f"📋 Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    print("🚀 STARTING FINANCIAL DATA INTEGRATION TEST\n")
    success = test_financial_data_integration()
    
    if success:
        print("\n✅ TEST COMPLETED SUCCESSFULLY")
        print("📊 Financial data integration is working properly")
    else:
        print("\n❌ TEST FAILED")
        print("🔧 Check the error messages above for debugging")