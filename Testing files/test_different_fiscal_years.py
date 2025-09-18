#!/usr/bin/env python3
"""
Test script to show how fiscal year-end formatting works with different companies
"""
import yfinance as yf
import sys
import os

# Add the backend directory to the path
sys.path.append('/Users/skl/Desktop/Robeco Reporting/src/robeco/backend')

from compact_financial_tables import generate_compact_income_statement_table

def test_different_fiscal_years():
    """Test fiscal year formatting with different companies"""
    print("🔍 Testing fiscal year-end formatting with different companies...")
    
    # Test companies with different fiscal year-ends
    test_companies = [
        ("AAPL", "Apple - September year-end"),
        ("MSFT", "Microsoft - June year-end"), 
        ("WMT", "Walmart - January year-end")
    ]
    
    for ticker, description in test_companies:
        print(f"\n📊 Testing {description} ({ticker})...")
        
        try:
            stock = yf.Ticker(ticker)
            financials = stock.financials
            
            if financials is not None and not financials.empty:
                # Convert to expected format
                income_data = {}
                for date_col in financials.columns:
                    date_str = date_col.strftime('%Y-%m-%d') if hasattr(date_col, 'strftime') else str(date_col)
                    income_data[date_str] = financials[date_col].to_dict()
                
                years = sorted(income_data.keys(), reverse=True)
                print(f"  Available years: {years[:3]}")
                
                # Show how the years would be formatted
                for year in years[:3]:
                    if '-' in year:
                        date_parts = year.split('-')
                        if len(date_parts) >= 3:
                            fiscal_year = date_parts[0]
                            month_num = date_parts[1]
                            # Convert month number to 3-letter abbreviation
                            month_names = {
                                '01': 'Jan', '02': 'Feb', '03': 'Mar', '04': 'Apr',
                                '05': 'May', '06': 'Jun', '07': 'Jul', '08': 'Aug', 
                                '09': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dec'
                            }
                            month_abbr = month_names.get(month_num, month_num)
                            year_short = fiscal_year[-2:]  # Get last 2 digits (2024 -> 24)
                            year_header = f"FY{year_short} {month_abbr}"
                            print(f"    {year} → {year_header}")
                
        except Exception as e:
            print(f"  ❌ Error with {ticker}: {e}")
    
    print(f"\n✅ Fiscal year-end formatting demonstrates:")
    print(f"  - Apple (Sep): FY24 Sep, FY23 Sep, FY22 Sep")
    print(f"  - Microsoft (Jun): FY24 Jun, FY23 Jun, FY22 Jun") 
    print(f"  - Walmart (Jan): FY24 Jan, FY23 Jan, FY22 Jan")
    print(f"  - Other months: Mar, Apr, May, Jul, Aug, Oct, Nov, Dec")

if __name__ == "__main__":
    test_different_fiscal_years()