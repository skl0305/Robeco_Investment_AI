#!/usr/bin/env python3
"""
Test script to verify financial ratio calculations are correct
"""
import sys
import os

# Add the backend directory to Python path
sys.path.append('/Users/skl/Desktop/Robeco Reporting/src/robeco/backend')

from template_report_generator import RobecoTemplateReportGenerator

def test_financial_ratio_calculations():
    """Test financial ratio calculations with sample data"""
    print("🧮 Testing Financial Ratio Calculations")
    print("=" * 50)
    
    # Create instance
    generator = RobecoTemplateReportGenerator()
    
    # Sample financial data (similar to real financial data structure)
    sample_income_data = {
        '2024': {
            'totalRevenue': 100000000000,  # $100B
            'grossProfit': 40000000000,    # $40B
            'operatingIncome': 25000000000, # $25B
            'netIncome': 15000000000,      # $15B
        },
        '2023': {
            'totalRevenue': 90000000000,   # $90B
            'grossProfit': 36000000000,    # $36B
            'operatingIncome': 22500000000, # $22.5B
            'netIncome': 13500000000,      # $13.5B
        }
    }
    
    sample_balance_data = {
        '2024': {
            'totalAssets': 200000000000,      # $200B
            'totalCurrentAssets': 80000000000, # $80B
            'inventory': 10000000000,         # $10B
            'totalCurrentLiabilities': 40000000000, # $40B
            'longTermDebt': 30000000000,      # $30B
            'shortLongTermDebt': 5000000000,  # $5B
            'totalShareholderEquity': 120000000000, # $120B
        },
        '2023': {
            'totalAssets': 180000000000,      # $180B
            'totalCurrentAssets': 75000000000, # $75B
            'inventory': 9000000000,          # $9B
            'totalCurrentLiabilities': 35000000000, # $35B
            'longTermDebt': 28000000000,      # $28B
            'shortLongTermDebt': 4000000000,  # $4B
            'totalShareholderEquity': 108000000000, # $108B
        }
    }
    
    sample_cashflow_data = {
        '2024': {
            'totalCashFromOperatingActivities': 30000000000, # $30B
            'capitalExpenditures': -8000000000,              # -$8B
        },
        '2023': {
            'totalCashFromOperatingActivities': 27000000000, # $27B
            'capitalExpenditures': -7200000000,              # -$7.2B
        }
    }
    
    print("Sample Data:")
    print(f"2024 Revenue: ${sample_income_data['2024']['totalRevenue']:,}")
    print(f"2024 Net Income: ${sample_income_data['2024']['netIncome']:,}")
    print(f"2024 Total Assets: ${sample_balance_data['2024']['totalAssets']:,}")
    print(f"2024 Shareholder Equity: ${sample_balance_data['2024']['totalShareholderEquity']:,}")
    print(f"2024 Operating Cash Flow: ${sample_cashflow_data['2024']['totalCashFromOperatingActivities']:,}")
    print()
    
    # Test calculations for 2024
    year = '2024'
    
    # 1. Test Margin Calculations
    print("📊 MARGIN RATIO TESTS:")
    
    # Gross Margin = Gross Profit / Revenue
    gross_margin = generator._calculate_margin_ratio(sample_income_data, year, 'grossProfit', 'totalRevenue')
    expected_gross = (40000000000 / 100000000000) * 100  # Should be 40.0%
    print(f"Gross Margin: {gross_margin} (Expected: {expected_gross:.1f}%)")
    
    # Operating Margin = Operating Income / Revenue  
    operating_margin = generator._calculate_margin_ratio(sample_income_data, year, 'operatingIncome', 'totalRevenue')
    expected_operating = (25000000000 / 100000000000) * 100  # Should be 25.0%
    print(f"Operating Margin: {operating_margin} (Expected: {expected_operating:.1f}%)")
    
    # Net Margin = Net Income / Revenue
    net_margin = generator._calculate_margin_ratio(sample_income_data, year, 'netIncome', 'totalRevenue')
    expected_net = (15000000000 / 100000000000) * 100  # Should be 15.0%
    print(f"Net Margin: {net_margin} (Expected: {expected_net:.1f}%)")
    print()
    
    # 2. Test Return Ratios
    print("📈 RETURN RATIO TESTS:")
    
    # ROE = Net Income / Shareholder Equity
    roe = generator._calculate_roe_ratio(sample_income_data, sample_balance_data, year)
    expected_roe = (15000000000 / 120000000000) * 100  # Should be 12.5%
    print(f"ROE: {roe} (Expected: {expected_roe:.1f}%)")
    
    # ROA = Net Income / Total Assets
    roa = generator._calculate_roa_ratio(sample_income_data, sample_balance_data, year)
    expected_roa = (15000000000 / 200000000000) * 100  # Should be 7.5%
    print(f"ROA: {roa} (Expected: {expected_roa:.1f}%)")
    print()
    
    # 3. Test Liquidity Ratios
    print("💧 LIQUIDITY RATIO TESTS:")
    
    # Current Ratio = Current Assets / Current Liabilities
    current_ratio = generator._calculate_current_ratio(sample_balance_data, year)
    expected_current = 80000000000 / 40000000000  # Should be 2.00x
    print(f"Current Ratio: {current_ratio} (Expected: {expected_current:.2f}x)")
    
    # Quick Ratio = (Current Assets - Inventory) / Current Liabilities
    quick_ratio = generator._calculate_quick_ratio(sample_balance_data, year)
    expected_quick = (80000000000 - 10000000000) / 40000000000  # Should be 1.75x
    print(f"Quick Ratio: {quick_ratio} (Expected: {expected_quick:.2f}x)")
    print()
    
    # 4. Test Leverage Ratios
    print("⚖️ LEVERAGE RATIO TESTS:")
    
    # Debt-to-Equity = Total Debt / Shareholder Equity
    debt_equity = generator._calculate_debt_equity_ratio(sample_balance_data, year)
    expected_de = (30000000000 + 5000000000) / 120000000000  # Should be 0.29x
    print(f"Debt-to-Equity: {debt_equity} (Expected: {expected_de:.2f}x)")
    print()
    
    # 5. Test Cash Flow Calculations
    print("💰 CASH FLOW TESTS:")
    
    # Free Cash Flow = Operating Cash Flow - CapEx
    fcf = generator._calculate_free_cash_flow(sample_cashflow_data, year)
    expected_fcf = 30000000000 + (-8000000000)  # $22B (capex is negative)
    print(f"Free Cash Flow: {fcf} (Expected: ${expected_fcf/1000000000:.1f}B)")
    print()
    
    # 6. Test Edge Cases
    print("🔍 EDGE CASE TESTS:")
    
    # Test division by zero
    zero_data = {'2024': {'totalRevenue': 0, 'grossProfit': 1000}}
    zero_margin = generator._calculate_margin_ratio(zero_data, '2024', 'grossProfit', 'totalRevenue')
    print(f"Zero denominator test: {zero_margin} (Expected: N/A)")
    
    # Test missing data
    empty_data = {}
    missing_roe = generator._calculate_roe_ratio(empty_data, empty_data, '2024')
    print(f"Missing data test: {missing_roe} (Expected: N/A)")
    
    # Test None values
    none_data = {'2024': {'netIncome': None, 'totalRevenue': 1000}}
    none_margin = generator._calculate_margin_ratio(none_data, '2024', 'netIncome', 'totalRevenue')
    print(f"None value test: {none_margin} (Expected: N/A)")
    print()
    
    print("✅ All ratio calculation tests completed!")
    print("Check the output above to verify calculations match expected values.")
    print()
    
    # Summary of key ratios that should be correct
    print("📋 RATIO SUMMARY (2024):")
    print(f"• Gross Margin: {gross_margin}")
    print(f"• Operating Margin: {operating_margin}")  
    print(f"• Net Margin: {net_margin}")
    print(f"• ROE: {roe}")
    print(f"• ROA: {roa}")
    print(f"• Current Ratio: {current_ratio}")
    print(f"• Quick Ratio: {quick_ratio}")
    print(f"• Debt-to-Equity: {debt_equity}")
    print(f"• Free Cash Flow: {fcf}")

if __name__ == "__main__":
    test_financial_ratio_calculations()