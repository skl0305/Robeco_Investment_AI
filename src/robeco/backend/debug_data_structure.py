#!/usr/bin/env python3
"""
Debug script to understand the exact data structure being passed to compact tables
"""
import yfinance as yf
import sys
import os
import json

# Add the backend directory to the path
sys.path.append('/Users/skl/Desktop/Robeco Reporting/src/robeco/backend')

from pre_calculated_financial_methods import extract_pre_calculated_financial_tables

def debug_data_structure():
    """Debug the data structure passed to compact tables"""
    print("🔍 Debugging data structure for compact financial tables...")
    
    # Get Apple data
    ticker = "AAPL"
    stock = yf.Ticker(ticker)
    
    # Convert to expected format
    financials_df = stock.financials
    balance_sheet_df = stock.balance_sheet
    cashflow_df = stock.cashflow
    
    income_statement_annual = {}
    if financials_df is not None and not financials_df.empty:
        for date_col in financials_df.columns:
            date_str = date_col.strftime('%Y-%m-%d') if hasattr(date_col, 'strftime') else str(date_col)
            income_statement_annual[date_str] = financials_df[date_col].to_dict()
    
    financial_data = {
        'income_statement_annual': income_statement_annual,
        'balance_sheet_annual': {},  # Keep simple for debugging
        'cashflow_annual': {}
    }
    
    # Extract pre-calculated tables
    pre_calculated = extract_pre_calculated_financial_tables(financial_data)
    
    print(f"\n📊 Pre-calculated structure:")
    print(f"Years: {pre_calculated.get('years_available', [])}")
    
    income_table = pre_calculated.get('income_statement_table', {})
    print(f"\n💰 Income table structure:")
    print(f"  - has_data: {income_table.get('has_data')}")
    print(f"  - years: {income_table.get('years', [])}")
    
    # Show the actual data structure
    income_data = income_table.get('data', {})
    if income_data:
        latest_year = list(income_data.keys())[0] if income_data else None
        print(f"\n📋 Sample data for {latest_year}:")
        if latest_year and latest_year in income_data:
            sample_data = income_data[latest_year]
            print(f"  Keys: {list(sample_data.keys())[:10]}")
            print(f"  Revenue: {sample_data.get('revenue', 'Not found')}")
            print(f"  Net Income: {sample_data.get('net_income', 'Not found')}")
    
    # Now show what raw yfinance data looks like
    print(f"\n🔍 Raw yfinance data structure:")
    if income_statement_annual:
        raw_year = list(income_statement_annual.keys())[0]
        print(f"Raw data for {raw_year}:")
        raw_data = income_statement_annual[raw_year]
        print(f"  Keys: {list(raw_data.keys())[:10]}")
        print(f"  Total Revenue: {raw_data.get('Total Revenue', 'Not found')}")
        print(f"  Net Income: {raw_data.get('Net Income', 'Not found')}")
    
    # Save debug output
    debug_output = {
        'pre_calculated_structure': {
            'years_available': pre_calculated.get('years_available', []),
            'income_has_data': income_table.get('has_data'),
            'income_years': income_table.get('years', []),
            'income_data_keys': list(income_data.keys()) if income_data else []
        },
        'sample_processed_data': income_data,
        'sample_raw_data': income_statement_annual
    }
    
    with open('/Users/skl/Desktop/Robeco Reporting/src/robeco/backend/debug_structure.json', 'w') as f:
        json.dump(debug_output, f, indent=2, default=str)
    
    print(f"\n✅ Debug data saved to debug_structure.json")
    return income_data, pre_calculated.get('years_available', [])

if __name__ == "__main__":
    debug_data_structure()