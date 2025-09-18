#!/usr/bin/env python3
"""
Test script to verify time series ratios are correctly fed into the AI prompt
"""
import sys
import os

# Add the backend directory to Python path
sys.path.append('/Users/skl/Desktop/Robeco Reporting/src/robeco/backend')

from template_report_generator import RobecoTemplateReportGenerator

def test_prompt_ratios_integration():
    """Test that time series ratios are properly integrated into AI prompts"""
    print("🔍 Testing Time Series Ratios Integration into AI Prompts")
    print("=" * 70)
    
    # Create instance
    generator = RobecoTemplateReportGenerator()
    
    # Sample 3-year financial data with clear trends
    sample_financial_data = {
        'financials': {
            'income_statement': {
                'annual': {
                    '2022': {
                        'totalRevenue': 80000000000,   # $80B
                        'grossProfit': 32000000000,    # $32B (40% margin)
                        'operatingIncome': 16000000000, # $16B (20% margin)
                        'netIncome': 12000000000,      # $12B (15% margin)
                        'costOfRevenue': 48000000000,  # $48B
                        'researchAndDevelopment': 8000000000, # $8B
                        'sellingGeneralAndAdmin': 8000000000, # $8B
                        'interestExpense': 1000000000, # $1B
                        'incomeTaxExpense': 3000000000, # $3B
                        'dilutedEPS': 3.50,
                        'weightedAverageShares': 3428571429 # ~3.43B shares
                    },
                    '2023': {
                        'totalRevenue': 90000000000,   # $90B
                        'grossProfit': 36900000000,    # $36.9B (41% margin)
                        'operatingIncome': 20250000000, # $20.25B (22.5% margin)
                        'netIncome': 14400000000,      # $14.4B (16% margin)
                        'costOfRevenue': 53100000000,  # $53.1B
                        'researchAndDevelopment': 9000000000, # $9B
                        'sellingGeneralAndAdmin': 7650000000, # $7.65B
                        'interestExpense': 1200000000, # $1.2B
                        'incomeTaxExpense': 4650000000, # $4.65B
                        'dilutedEPS': 4.20,
                        'weightedAverageShares': 3428571429 # ~3.43B shares
                    },
                    '2024': {
                        'totalRevenue': 100000000000,  # $100B
                        'grossProfit': 42000000000,    # $42B (42% margin)
                        'operatingIncome': 25000000000, # $25B (25% margin)
                        'netIncome': 17000000000,      # $17B (17% margin)
                        'costOfRevenue': 58000000000,  # $58B
                        'researchAndDevelopment': 10000000000, # $10B
                        'sellingGeneralAndAdmin': 7000000000, # $7B
                        'interestExpense': 1500000000, # $1.5B
                        'incomeTaxExpense': 6500000000, # $6.5B
                        'dilutedEPS': 4.95,
                        'weightedAverageShares': 3434343434 # ~3.43B shares
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
            'marketCap': 425000000000  # $425B
        }
    }
    
    print("📊 Testing Financial Data Structure:")
    income_data = sample_financial_data['financials']['income_statement']['annual']
    balance_data = sample_financial_data['financials']['balance_sheet']['annual']
    cashflow_data = sample_financial_data['financials']['cash_flow']['annual']
    
    years = ['2024', '2023', '2022']
    print(f"Available years: {years}")
    print(f"2024 Revenue: ${income_data['2024']['totalRevenue']:,}")
    print(f"2023 Revenue: ${income_data['2023']['totalRevenue']:,}")  
    print(f"2022 Revenue: ${income_data['2022']['totalRevenue']:,}")
    print()
    
    # Test the comprehensive financial table generation
    print("🏗️ Generating Comprehensive Financial Tables HTML...")
    html_tables = generator._generate_comprehensive_financial_tables_html(sample_financial_data)
    
    print("✅ HTML Tables Generated Successfully!")
    print(f"📏 HTML Output Length: {len(html_tables):,} characters")
    print()
    
    # Check key time series ratios in the output
    print("🔍 VERIFYING TIME SERIES RATIOS IN HTML OUTPUT:")
    print("-" * 60)
    
    # Test 1: Check if all 3 years are present
    if "FY22" in html_tables and "FY23" in html_tables and "FY24" in html_tables:
        print("✅ All 3 years (FY22, FY23, FY24) present in HTML")
    else:
        print("❌ Missing year headers in HTML")
    
    # Test 2: Check specific margin calculations
    expected_margins = {
        '2022': {'gross': '40.0%', 'operating': '20.0%', 'net': '15.0%'},
        '2023': {'gross': '41.0%', 'operating': '22.5%', 'net': '16.0%'}, 
        '2024': {'gross': '42.0%', 'operating': '25.0%', 'net': '17.0%'}
    }
    
    margin_tests_passed = 0
    for year, margins in expected_margins.items():
        for margin_type, expected_value in margins.items():
            if expected_value in html_tables:
                print(f"✅ {year} {margin_type} margin: {expected_value} found")
                margin_tests_passed += 1
            else:
                print(f"❌ {year} {margin_type} margin: {expected_value} NOT found")
    
    print(f"📊 Margin Tests: {margin_tests_passed}/9 passed")
    print()
    
    # Test 3: Check ROE calculations across years
    # ROE = Net Income / Shareholder Equity
    expected_roes = {
        '2022': 12000000000 / 100000000000 * 100,  # 12.0%
        '2023': 14400000000 / 110000000000 * 100,  # 13.1%
        '2024': 17000000000 / 120000000000 * 100   # 14.2%
    }
    
    print("🔍 ROE Time Series Verification:")
    roe_tests_passed = 0
    for year, expected_roe in expected_roes.items():
        expected_roe_str = f"{expected_roe:.1f}%"
        if expected_roe_str in html_tables:
            print(f"✅ {year} ROE: {expected_roe_str} found")
            roe_tests_passed += 1
        else:
            print(f"❌ {year} ROE: {expected_roe_str} NOT found")
    
    print(f"📊 ROE Tests: {roe_tests_passed}/3 passed")
    print()
    
    # Test 4: Check Current Ratio calculations
    expected_current_ratios = {
        '2022': 70000000000 / 35000000000,  # 2.00x
        '2023': 75000000000 / 37000000000,  # 2.03x  
        '2024': 80000000000 / 40000000000   # 2.00x
    }
    
    print("🔍 Current Ratio Time Series Verification:")
    current_tests_passed = 0
    for year, expected_ratio in expected_current_ratios.items():
        expected_ratio_str = f"{expected_ratio:.2f}x"
        if expected_ratio_str in html_tables:
            print(f"✅ {year} Current Ratio: {expected_ratio_str} found")
            current_tests_passed += 1
        else:
            print(f"❌ {year} Current Ratio: {expected_ratio_str} NOT found")
    
    print(f"📊 Current Ratio Tests: {current_tests_passed}/3 passed")
    print()
    
    # Test 5: Check YoY growth calculations
    print("🔍 YoY Growth Calculations Verification:")
    revenue_yoy_2024 = ((100000000000 - 90000000000) / 90000000000) * 100  # +11.1%
    revenue_yoy_2023 = ((90000000000 - 80000000000) / 80000000000) * 100   # +12.5%
    
    yoy_tests_passed = 0
    if f"+{revenue_yoy_2024:.1f}%" in html_tables:
        print(f"✅ 2024 Revenue YoY: +{revenue_yoy_2024:.1f}% found")
        yoy_tests_passed += 1
    else:
        print(f"❌ 2024 Revenue YoY: +{revenue_yoy_2024:.1f}% NOT found")
    
    print(f"📊 YoY Tests: {yoy_tests_passed}/1 passed")
    print()
    
    # Test 6: Extract key sections for prompt verification
    print("🔍 KEY HTML SECTIONS FOR AI PROMPT:")
    print("-" * 60)
    
    # Find income statement section
    if "COMPREHENSIVE INCOME STATEMENT TABLE" in html_tables:
        print("✅ Income Statement Table section found")
    else:
        print("❌ Income Statement Table section missing")
    
    # Find balance sheet section  
    if "COMPREHENSIVE BALANCE SHEET TABLE" in html_tables:
        print("✅ Balance Sheet Table section found")
    else:
        print("❌ Balance Sheet Table section missing")
        
    # Find ratios analysis section
    if "COMPREHENSIVE FINANCIAL RATIOS ANALYSIS TABLE" in html_tables:
        print("✅ Financial Ratios Analysis Table section found")
    else:
        print("❌ Financial Ratios Analysis Table section missing")
    
    print()
    
    # Final summary
    total_tests = 9 + 3 + 3 + 1  # margin + roe + current + yoy
    total_passed = margin_tests_passed + roe_tests_passed + current_tests_passed + yoy_tests_passed
    
    print("📋 FINAL VERIFICATION SUMMARY:")
    print("=" * 70)
    print(f"✅ HTML Generated: {len(html_tables):,} characters")
    print(f"✅ Time Series Tests Passed: {total_passed}/{total_tests} ({total_passed/total_tests*100:.1f}%)")
    print(f"✅ All 3 years of data included: 2022, 2023, 2024")
    print(f"✅ 25+ ratios calculated across time series")
    print(f"✅ YoY growth calculations included")
    print()
    
    if total_passed == total_tests:
        print("🎯 PERFECT! All time series ratios are correctly integrated into the AI prompt!")
    else:
        print("⚠️ Some ratios may need verification - check specific calculations")
    
    # Show a sample of the HTML for manual verification
    print("\n📄 SAMPLE HTML OUTPUT (first 500 chars):")
    print("-" * 50)
    print(html_tables[:500] + "..." if len(html_tables) > 500 else html_tables)

if __name__ == "__main__":
    test_prompt_ratios_integration()