#!/usr/bin/env python3
"""
Test script to see all available yfinance financial statement metrics
"""
import yfinance as yf

def test_yfinance_metrics():
    """Test to see all available financial metrics from yfinance"""
    print("🔍 Testing yfinance financial statement metrics...")
    
    # Test with Apple data
    ticker = "AAPL"
    stock = yf.Ticker(ticker)
    
    print(f"\n📊 Fetching financial data for {ticker}...")
    
    # Get financial statements
    try:
        financials = stock.financials
        balance_sheet = stock.balance_sheet
        cashflow = stock.cashflow
        
        print(f"\n💰 INCOME STATEMENT METRICS:")
        if financials is not None and not financials.empty:
            print("Available metrics:")
            for metric in financials.index:
                latest_value = financials.iloc[0, 0] if not financials.empty else "N/A"
                print(f"  - {metric}: {latest_value}")
        
        print(f"\n🏦 BALANCE SHEET METRICS:")
        if balance_sheet is not None and not balance_sheet.empty:
            print("Available metrics:")
            for metric in balance_sheet.index:
                latest_value = balance_sheet.iloc[0, 0] if not balance_sheet.empty else "N/A"
                print(f"  - {metric}: {latest_value}")
        
        print(f"\n💸 CASH FLOW METRICS:")
        if cashflow is not None and not cashflow.empty:
            print("Available metrics:")
            for metric in cashflow.index:
                latest_value = cashflow.iloc[0, 0] if not cashflow.empty else "N/A"
                print(f"  - {metric}: {latest_value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing yfinance metrics: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_yfinance_metrics()