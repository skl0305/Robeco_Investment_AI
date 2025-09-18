#!/usr/bin/env python3
"""
Test script to verify compact financial tables with Apple data
"""
import yfinance as yf
import sys
import os

# Add the backend directory to the path
sys.path.append('/Users/skl/Desktop/Robeco Reporting/src/robeco/backend')

from compact_financial_tables import (
    generate_compact_income_statement_table,
    generate_compact_balance_sheet_table,
    generate_compact_cashflow_table,
    format_financial_value
)

def test_with_apple():
    """Test compact tables with actual Apple data"""
    print("🔍 Testing compact financial tables with Apple (AAPL) data...")
    
    # Fetch Apple data
    ticker = "AAPL"
    stock = yf.Ticker(ticker)
    
    print(f"\n📊 Fetching financial data for {ticker}...")
    
    # Get financial statements
    try:
        financials = stock.financials
        balance_sheet = stock.balance_sheet  
        cashflow = stock.cashflow
        
        print(f"✅ Income Statement: {financials.shape if financials is not None else 'None'}")
        print(f"✅ Balance Sheet: {balance_sheet.shape if balance_sheet is not None else 'None'}")
        print(f"✅ Cash Flow: {cashflow.shape if cashflow is not None else 'None'}")
        
        # Show available data fields
        if financials is not None and not financials.empty:
            print(f"\n📋 Available income statement fields: {list(financials.index)[:10]}...")
            print(f"📋 Available date columns: {list(financials.columns)}")
        
        # Convert to the format expected by compact tables
        def convert_dataframe_to_dict(df):
            if df is None or df.empty:
                return {}
            
            result = {}
            for date_col in df.columns:
                date_str = date_col.strftime('%Y-%m-%d') if hasattr(date_col, 'strftime') else str(date_col)
                result[date_str] = df[date_col].to_dict()
            return result
        
        # Convert data
        income_data = convert_dataframe_to_dict(financials)
        balance_data = convert_dataframe_to_dict(balance_sheet)
        cashflow_data = convert_dataframe_to_dict(cashflow)
        
        # Get available years
        years = sorted(income_data.keys(), reverse=True) if income_data else []
        print(f"\n📅 Available years: {years}")
        
        # Show some actual data values to verify accuracy
        if years and income_data:
            latest_year = years[0]
            print(f"\n💰 Sample Apple financial data for {latest_year}:")
            latest_income = income_data[latest_year]
            
            # Show available keys for debugging
            print(f"📋 Available keys in latest income data: {list(latest_income.keys())[:10]}...")
            
            revenue = latest_income.get('Total Revenue')
            net_income = latest_income.get('Net Income')
            print(f"  - Total Revenue: {format_financial_value(revenue)} (raw: {revenue})")
            print(f"  - Net Income: {format_financial_value(net_income)} (raw: {net_income})")
            
            if balance_data and latest_year in balance_data:
                latest_balance = balance_data[latest_year]
                total_assets = latest_balance.get('Total Assets')
                print(f"  - Total Assets: {format_financial_value(total_assets)} (raw: {total_assets})")
        
        # Test compact table generation
        print("\n🎨 Generating compact income statement table...")
        compact_income_html = generate_compact_income_statement_table(income_data, years)
        
        print("\n🎨 Generating compact balance sheet table...")
        compact_balance_html = generate_compact_balance_sheet_table(balance_data, years)
        
        print("\n🎨 Generating compact cash flow table...")
        compact_cashflow_html = generate_compact_cashflow_table(cashflow_data, years)
        
        # Save test output
        test_output = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Apple Compact Financial Tables Test</title>
    <meta charset="utf-8">
</head>
<body style="margin: 20px; font-family: Arial, sans-serif;">
    <h1>🍎 Apple Inc. (AAPL) - Compact Financial Tables Test</h1>
    <p><strong>Test Date:</strong> {years[0] if years else 'N/A'}</p>
    <p><strong>Years Available:</strong> {', '.join(years[:3]) if years else 'None'}</p>
    
    <h2>📊 Income Statement</h2>
    {compact_income_html}
    
    <h2>🏦 Balance Sheet</h2>
    {compact_balance_html}
    
    <h2>💸 Cash Flow Statement</h2>
    {compact_cashflow_html}
    
    <div style="margin-top: 40px; padding: 20px; background: #f8f9fa; border-radius: 8px;">
        <h3>✅ Test Results</h3>
        <ul>
            <li>Income Statement HTML: {len(compact_income_html)} characters</li>
            <li>Balance Sheet HTML: {len(compact_balance_html)} characters</li>
            <li>Cash Flow HTML: {len(compact_cashflow_html)} characters</li>
            <li>Data Source: yfinance API</li>
            <li>Ticker: {ticker}</li>
        </ul>
    </div>
</body>
</html>
"""
        
        # Save the test file
        output_file = "/Users/skl/Desktop/Robeco Reporting/src/robeco/backend/apple_compact_tables_test.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(test_output)
        
        print(f"\n✅ Test complete! Results saved to: {output_file}")
        print(f"📝 Open the file in a browser to see the compact tables with actual Apple data")
        
        # Show a preview of the income statement table
        print(f"\n🔍 Income Statement Table Preview (first 500 characters):")
        print(compact_income_html[:500] + "..." if len(compact_income_html) > 500 else compact_income_html)
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing compact tables: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_with_apple()
    if success:
        print("\n🎉 Compact financial tables test completed successfully!")
    else:
        print("\n💥 Test failed - check error messages above")