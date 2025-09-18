#!/usr/bin/env python3
"""
Test script to verify complete prompt generation with time series ratios
"""
import sys
import os

# Add the backend directory to Python path
sys.path.append('/Users/skl/Desktop/Robeco Reporting/src/robeco/backend')

from template_report_generator import RobecoTemplateReportGenerator

def test_full_prompt_with_ratios():
    """Test complete prompt generation including time series ratios"""
    print("🔍 Testing Complete AI Prompt Generation with Time Series Ratios")
    print("=" * 70)
    
    # Create instance
    generator = RobecoTemplateReportGenerator()
    
    # Sample complete financial data structure
    sample_financial_data = {
        'financials': {
            'income_statement': {
                'annual': {
                    '2022': {
                        'totalRevenue': 80000000000,   
                        'grossProfit': 32000000000,    
                        'operatingIncome': 16000000000, 
                        'netIncome': 12000000000,      
                        'costOfRevenue': 48000000000,  
                        'researchAndDevelopment': 8000000000, 
                        'sellingGeneralAndAdmin': 8000000000, 
                        'interestExpense': 1000000000, 
                        'incomeTaxExpense': 3000000000, 
                        'dilutedEPS': 3.50,
                        'weightedAverageShares': 3428571429
                    },
                    '2023': {
                        'totalRevenue': 90000000000,   
                        'grossProfit': 36900000000,    
                        'operatingIncome': 20250000000, 
                        'netIncome': 14400000000,      
                        'costOfRevenue': 53100000000,  
                        'researchAndDevelopment': 9000000000, 
                        'sellingGeneralAndAdmin': 7650000000, 
                        'interestExpense': 1200000000, 
                        'incomeTaxExpense': 4650000000, 
                        'dilutedEPS': 4.20,
                        'weightedAverageShares': 3428571429
                    },
                    '2024': {
                        'totalRevenue': 100000000000,  
                        'grossProfit': 42000000000,    
                        'operatingIncome': 25000000000, 
                        'netIncome': 17000000000,      
                        'costOfRevenue': 58000000000,  
                        'researchAndDevelopment': 10000000000, 
                        'sellingGeneralAndAdmin': 7000000000, 
                        'interestExpense': 1500000000, 
                        'incomeTaxExpense': 6500000000, 
                        'dilutedEPS': 4.95,
                        'weightedAverageShares': 3434343434
                    }
                }
            },
            'balance_sheet': {
                'annual': {
                    '2022': {
                        'totalAssets': 180000000000,
                        'totalCurrentAssets': 70000000000,
                        'cashAndCashEquivalents': 25000000000,
                        'netReceivables': 15000000000,
                        'inventory': 8000000000,
                        'totalCurrentLiabilities': 35000000000,
                        'longTermDebt': 25000000000,
                        'shortLongTermDebt': 3000000000,
                        'totalShareholderEquity': 100000000000
                    },
                    '2023': {
                        'totalAssets': 190000000000,
                        'totalCurrentAssets': 75000000000,
                        'cashAndCashEquivalents': 28000000000,
                        'netReceivables': 16000000000,
                        'inventory': 9000000000,
                        'totalCurrentLiabilities': 37000000000,
                        'longTermDebt': 27000000000,
                        'shortLongTermDebt': 4000000000,
                        'totalShareholderEquity': 110000000000
                    },
                    '2024': {
                        'totalAssets': 200000000000,
                        'totalCurrentAssets': 80000000000,
                        'cashAndCashEquivalents': 30000000000,
                        'netReceivables': 18000000000,
                        'inventory': 10000000000,
                        'totalCurrentLiabilities': 40000000000,
                        'longTermDebt': 30000000000,
                        'shortLongTermDebt': 5000000000,
                        'totalShareholderEquity': 120000000000
                    }
                }
            },
            'cash_flow': {
                'annual': {
                    '2022': {
                        'totalCashFromOperatingActivities': 24000000000,
                        'capitalExpenditures': -6000000000
                    },
                    '2023': {
                        'totalCashFromOperatingActivities': 27000000000,
                        'capitalExpenditures': -7000000000
                    },
                    '2024': {
                        'totalCashFromOperatingActivities': 30000000000,
                        'capitalExpenditures': -8000000000
                    }
                }
            }
        },
        'key_stats': {
            'trailingPE': 25.5,
            'priceToBook': 3.2,
            'marketCap': 425000000000
        }
    }
    
    # Test the financial statements extraction process
    print("📊 Step 1: Testing Financial Statements Extraction...")
    financial_statements = generator._extract_financial_statements_for_analysis(sample_financial_data)
    
    print(f"✅ Financial statements extracted successfully")
    print(f"   📄 Income Statement: {financial_statements.get('income_statement', {}).get('has_data', False)}")
    print(f"   📄 Balance Sheet: {financial_statements.get('balance_sheet', {}).get('has_data', False)}")
    print(f"   📄 Cash Flow: {financial_statements.get('cashflow', {}).get('has_data', False)}")
    print(f"   📊 HTML Tables Available: {bool(financial_statements.get('html_tables_for_ai'))}")
    print()
    
    # Check if HTML tables contain time series data
    html_content = financial_statements.get('html_tables_for_ai', '')
    if html_content:
        print("📊 Step 2: Verifying HTML Tables Content...")
        print(f"   📏 HTML Length: {len(html_content):,} characters")
        
        # Check for key time series elements
        has_all_years = all(year in html_content for year in ['FY22', 'FY23', 'FY24'])
        has_ratios_table = 'COMPREHENSIVE FINANCIAL RATIOS ANALYSIS TABLE' in html_content
        has_income_table = 'COMPREHENSIVE INCOME STATEMENT TABLE' in html_content
        has_balance_table = 'COMPREHENSIVE BALANCE SHEET TABLE' in html_content
        
        print(f"   ✅ All 3 Years Present: {has_all_years}")
        print(f"   ✅ Ratios Analysis Table: {has_ratios_table}")
        print(f"   ✅ Income Statement Table: {has_income_table}")
        print(f"   ✅ Balance Sheet Table: {has_balance_table}")
        print()
        
        # Test specific ratio calculations
        print("📊 Step 3: Verifying Specific Time Series Ratios...")
        
        # Check margin progression: 40% -> 41% -> 42%
        margin_2022 = '40.0%' in html_content
        margin_2023 = '41.0%' in html_content  
        margin_2024 = '42.0%' in html_content
        print(f"   📈 Gross Margin Series: 2022({margin_2022}) -> 2023({margin_2023}) -> 2024({margin_2024})")
        
        # Check ROE progression: 12.0% -> 13.1% -> 14.2%
        roe_2022 = '12.0%' in html_content
        roe_2023 = '13.1%' in html_content
        roe_2024 = '14.2%' in html_content
        print(f"   📈 ROE Series: 2022({roe_2022}) -> 2023({roe_2023}) -> 2024({roe_2024})")
        
        # Check Current Ratio: ~2.0x consistently
        current_2022 = '2.00x' in html_content
        current_2023 = '2.03x' in html_content
        current_2024 = '2.00x' in html_content  
        print(f"   📊 Current Ratio Series: 2022({current_2022}) -> 2023({current_2023}) -> 2024({current_2024})")
        
        # Check YoY calculations
        has_yoy = any(pct in html_content for pct in ['+11.1%', '+12.5%', '+41.7%'])
        print(f"   📈 YoY Growth Calculations Present: {has_yoy}")
        print()
    
    # Now test the actual prompt generation
    print("📝 Step 4: Testing AI Prompt Generation...")
    
    # Simulate the data structure used in the financial section generation
    company_name = "Test Corp"
    ticker = "TEST"
    company_context = {'company_name': company_name}
    call1_context = {'extracted_info': 'Investment thesis data'}
    call2_context = {'extracted_info': 'Business analysis data'}
    
    # Filter data for call2 financial (this is what actually gets passed to prompt)
    call2_financial_data = generator._filter_data_for_call2_financial(
        sample_financial_data, 
        financial_statements, 
        company_context, 
        call1_context, 
        call2_context
    )
    
    print(f"✅ Call2 Financial Data Filtered")
    print(f"   📊 Data Keys: {list(call2_financial_data.keys())}")
    print(f"   📄 Financial Statements Available: {bool(call2_financial_data.get('financial_statements'))}")
    
    # Check if the filtered data contains the HTML tables
    filtered_html = call2_financial_data.get('financial_statements', {}).get('html_tables_for_ai', '')
    if filtered_html:
        print(f"   ✅ HTML Tables in Filtered Data: {len(filtered_html):,} characters")
        
        # Verify key ratios are still present in filtered data
        key_ratios_present = all(ratio in filtered_html for ratio in [
            '40.0%', '41.0%', '42.0%',  # Gross margins
            '12.0%', '13.1%', '14.2%',  # ROE series
            '2.00x', '2.03x'  # Current ratios
        ])
        print(f"   ✅ Key Time Series Ratios Present: {key_ratios_present}")
        
        # Test that the prompt would actually contain the data
        sample_prompt_section = f"""
**COMPREHENSIVE PRE-CALCULATED FINANCIAL TABLES (READY TO USE):**
{filtered_html[:1000]}...
"""
        
        print(f"   ✅ Sample Prompt Section Generated: {len(sample_prompt_section):,} characters")
        
        # Verify prompt section contains time series data
        prompt_has_ratios = all(check in sample_prompt_section for check in [
            'FY22', 'FY23', 'FY24',
            '40.0%', '41.0%'  # At least some margins
        ])
        print(f"   ✅ Prompt Section Contains Time Series: {prompt_has_ratios}")
    else:
        print("   ❌ HTML Tables NOT found in filtered data!")
    
    print()
    
    # Final verification
    print("🎯 FINAL VERIFICATION SUMMARY:")
    print("=" * 70)
    
    success_checks = [
        financial_statements.get('html_tables_for_ai') is not None,
        len(html_content) > 20000,  # Substantial content
        has_all_years,
        has_ratios_table,
        margin_2022 and margin_2023 and margin_2024,
        roe_2022 and roe_2023 and roe_2024,
        bool(filtered_html),
        key_ratios_present if filtered_html else False
    ]
    
    passed_checks = sum(success_checks)
    total_checks = len(success_checks)
    
    print(f"✅ Verification Checks Passed: {passed_checks}/{total_checks} ({passed_checks/total_checks*100:.1f}%)")
    
    if passed_checks == total_checks:
        print("🎯 SUCCESS! Time series ratios are correctly integrated into AI prompts!")
        print("📊 The AI will receive:")
        print("   • 25+ ratios calculated across 3 years (2022-2024)")
        print("   • Complete income statement, balance sheet, cash flow tables")
        print("   • YoY growth calculations and trend analysis")
        print("   • Professional HTML table formatting")
        print("   • Pre-calculated ratios ready for institutional analysis")
    else:
        print("⚠️ Some integration issues detected - review the failed checks above")
    
    return passed_checks == total_checks

if __name__ == "__main__":
    success = test_full_prompt_with_ratios()
    if success:
        print("\n🎉 ALL TESTS PASSED - Time series ratios are properly fed to AI prompts!")
    else:
        print("\n⚠️ Some tests failed - check the output above for issues")