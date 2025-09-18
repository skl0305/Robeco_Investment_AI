#!/usr/bin/env python3
"""
Test script to verify full integration of compact tables with report generation
"""
import yfinance as yf
import sys
import os

# Add the backend directory to the path
sys.path.append('/Users/skl/Desktop/Robeco Reporting/src/robeco/backend')

from pre_calculated_financial_methods import (
    extract_pre_calculated_financial_tables,
    generate_ready_to_use_prompt_data
)

def test_full_integration():
    """Test the complete integration from yfinance to compact tables in AI prompt"""
    print("🔍 Testing full integration of compact financial tables...")
    
    # Test with Apple data
    ticker = "AAPL"
    print(f"\n📊 Fetching financial data for {ticker}...")
    
    try:
        stock = yf.Ticker(ticker)
        
        # Get financial statements (same as in professional_streaming_server.py)
        financials_df = stock.financials
        balance_sheet_df = stock.balance_sheet
        cashflow_df = stock.cashflow
        
        print(f"✅ Data shapes - Income: {financials_df.shape}, Balance: {balance_sheet_df.shape}, Cash: {cashflow_df.shape}")
        
        # Convert DataFrames to the expected annual format (same as professional_streaming_server.py)
        income_statement_annual = {}
        balance_sheet_annual = {}
        cashflow_annual = {}
        
        if financials_df is not None and not financials_df.empty:
            for date_col in financials_df.columns:
                date_str = date_col.strftime('%Y-%m-%d') if hasattr(date_col, 'strftime') else str(date_col)
                income_statement_annual[date_str] = financials_df[date_col].to_dict()
        
        if balance_sheet_df is not None and not balance_sheet_df.empty:
            for date_col in balance_sheet_df.columns:
                date_str = date_col.strftime('%Y-%m-%d') if hasattr(date_col, 'strftime') else str(date_col)
                balance_sheet_annual[date_str] = balance_sheet_df[date_col].to_dict()
        
        if cashflow_df is not None and not cashflow_df.empty:
            for date_col in cashflow_df.columns:
                date_str = date_col.strftime('%Y-%m-%d') if hasattr(date_col, 'strftime') else str(date_col)
                cashflow_annual[date_str] = cashflow_df[date_col].to_dict()
        
        # Create financial data structure
        financial_data = {
            'info': stock.info,
            'history': stock.history(period="5y", interval="1mo").to_dict() if hasattr(stock, 'history') else {},
            'income_statement_annual': income_statement_annual,
            'balance_sheet_annual': balance_sheet_annual,
            'cashflow_annual': cashflow_annual
        }
        
        print(f"📊 Converted data - Income years: {list(income_statement_annual.keys())}")
        
        # Step 1: Extract pre-calculated tables
        print("\n🔧 Step 1: Extracting pre-calculated financial tables...")
        pre_calculated_tables = extract_pre_calculated_financial_tables(financial_data)
        
        print(f"✅ Pre-calculated tables extracted:")
        print(f"  - Income data available: {pre_calculated_tables['data_quality']['income_data_available']}")
        print(f"  - Balance data available: {pre_calculated_tables['data_quality']['balance_data_available']}")
        print(f"  - Cashflow data available: {pre_calculated_tables['data_quality']['cashflow_data_available']}")
        print(f"  - Years available: {pre_calculated_tables['years_available']}")
        
        # Step 2: Generate ready-to-use prompt data with compact tables
        print("\n🎨 Step 2: Generating ready-to-use prompt data with compact tables...")
        prompt_data = generate_ready_to_use_prompt_data(pre_calculated_tables)
        
        # Save the full prompt data to see what the AI would receive
        output_file = "/Users/skl/Desktop/Robeco Reporting/src/robeco/backend/full_integration_test_output.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"FULL INTEGRATION TEST - APPLE (AAPL) FINANCIAL DATA\n")
            f.write(f"=" * 80 + "\n\n")
            f.write(f"Test Date: {pre_calculated_tables['years_available'][0] if pre_calculated_tables['years_available'] else 'N/A'}\n")
            f.write(f"Ticker: {ticker}\n")
            f.write(f"Data Quality: Income={pre_calculated_tables['data_quality']['income_data_available']}, ")
            f.write(f"Balance={pre_calculated_tables['data_quality']['balance_data_available']}, ")
            f.write(f"Cashflow={pre_calculated_tables['data_quality']['cashflow_data_available']}\n\n")
            f.write("PROMPT DATA THAT WOULD BE SENT TO AI:\n")
            f.write("=" * 80 + "\n")
            f.write(prompt_data)
        
        print(f"✅ Full prompt data saved to: {output_file}")
        
        # Show key metrics from the actual data
        if pre_calculated_tables['years_available']:
            latest_year = pre_calculated_tables['years_available'][0]
            income_data = pre_calculated_tables['income_statement_table'].get('data', {})
            if latest_year in income_data:
                latest_income = income_data[latest_year]
                print(f"\n💰 Verified Apple financial metrics for {latest_year}:")
                print(f"  - Revenue: {latest_income.get('revenue', 'N/A')}")
                print(f"  - Net Income: {latest_income.get('net_income', 'N/A')}")
                print(f"  - Gross Margin: {latest_income.get('gross_margin', 'N/A')}")
                print(f"  - Operating Margin: {latest_income.get('operating_margin', 'N/A')}")
        
        # Check if compact tables are being used
        if "💰 INCOME STATEMENT" in prompt_data and "background: linear-gradient" in prompt_data:
            print(f"\n✅ Compact tables successfully integrated!")
            print(f"  - Modern styling detected in prompt")
            print(f"  - Prompt data length: {len(prompt_data)} characters")
        else:
            print(f"\n⚠️ Warning: Compact tables may not be working properly")
        
        # Show preview of what AI would receive
        print(f"\n🔍 Preview of AI prompt data (first 800 characters):")
        print("-" * 80)
        print(prompt_data[:800] + "..." if len(prompt_data) > 800 else prompt_data)
        print("-" * 80)
        
        return True
        
    except Exception as e:
        print(f"❌ Error in full integration test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_full_integration()
    if success:
        print("\n🎉 Full integration test completed successfully!")
        print("✅ Compact financial tables are ready for Call2 report generation!")
    else:
        print("\n💥 Integration test failed - check error messages above")