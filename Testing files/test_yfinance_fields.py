#!/usr/bin/env python3
"""
Test actual yfinance financial statement field names
"""
import yfinance as yf

def analyze_financial_fields():
    """Analyze actual field names in yfinance financial statements"""
    print("🔍 ANALYZING YFINANCE FINANCIAL STATEMENT FIELDS")
    print("="*70)
    
    # Test with a reliable large cap stock
    ticker = yf.Ticker("AAPL")
    
    print("\n📊 INCOME STATEMENT FIELDS:")
    income_stmt = ticker.financials
    if income_stmt is not None and not income_stmt.empty:
        print("Available fields (index):")
        for i, field in enumerate(income_stmt.index):
            print(f"  {i+1:2d}. {field}")
        
        # Look for key income statement items
        key_income_fields = [
            'Total Revenue', 'Revenue', 'Operating Revenue',
            'Gross Profit', 'Operating Income', 'Operating Revenue',
            'Net Income', 'Net Income From Continuing Operations',
            'EBITDA', 'EBIT', 'Normalized EBITDA'
        ]
        
        print("\n🎯 KEY INCOME STATEMENT MAPPINGS:")
        for field in key_income_fields:
            if field in income_stmt.index:
                latest_value = income_stmt.loc[field].iloc[0] if not income_stmt.loc[field].empty else None
                print(f"  ✅ {field}: {latest_value}")
            else:
                print(f"  ❌ {field}: NOT FOUND")
    
    print("\n📊 BALANCE SHEET FIELDS:")
    balance_sheet = ticker.balance_sheet
    if balance_sheet is not None and not balance_sheet.empty:
        print("Available fields (first 20):")
        for i, field in enumerate(balance_sheet.index[:20]):
            print(f"  {i+1:2d}. {field}")
        
        # Look for key balance sheet items
        key_balance_fields = [
            'Total Assets', 'Current Assets', 'Total Debt',
            'Stockholder Equity', 'Total Equity', 'Common Stock Equity',
            'Current Liabilities', 'Working Capital', 'Cash And Cash Equivalents'
        ]
        
        print("\n🎯 KEY BALANCE SHEET MAPPINGS:")
        for field in key_balance_fields:
            if field in balance_sheet.index:
                latest_value = balance_sheet.loc[field].iloc[0] if not balance_sheet.loc[field].empty else None
                print(f"  ✅ {field}: {latest_value}")
            else:
                print(f"  ❌ {field}: NOT FOUND")
    
    print("\n📊 CASH FLOW FIELDS:")
    cashflow = ticker.cashflow
    if cashflow is not None and not cashflow.empty:
        print("Available fields (first 20):")
        for i, field in enumerate(cashflow.index[:20]):
            print(f"  {i+1:2d}. {field}")
        
        # Look for key cash flow items
        key_cashflow_fields = [
            'Operating Cash Flow', 'Free Cash Flow',
            'Capital Expenditure', 'Capital Expenditures',
            'Investing Cash Flow', 'Financing Cash Flow'
        ]
        
        print("\n🎯 KEY CASH FLOW MAPPINGS:")
        for field in key_cashflow_fields:
            if field in cashflow.index:
                latest_value = cashflow.loc[field].iloc[0] if not cashflow.loc[field].empty else None
                print(f"  ✅ {field}: {latest_value}")
            else:
                print(f"  ❌ {field}: NOT FOUND")

if __name__ == "__main__":
    analyze_financial_fields()