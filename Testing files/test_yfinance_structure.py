#!/usr/bin/env python3
"""
Test script to understand yfinance data structure for different companies
"""
import yfinance as yf
import json
from pprint import pprint

def test_company_data(symbol):
    """Test yfinance data structure for a company"""
    print(f"\n{'='*80}")
    print(f"TESTING {symbol}")
    print(f"{'='*80}")
    
    try:
        # Get ticker
        ticker = yf.Ticker(symbol)
        
        # Get basic info
        print(f"\n📊 BASIC INFO for {symbol}:")
        info = ticker.info
        print(f"Company Name: {info.get('longName', 'N/A')}")
        print(f"Sector: {info.get('sector', 'N/A')}")
        print(f"Market Cap: {info.get('marketCap', 'N/A')}")
        print(f"Current Price: {info.get('currentPrice', 'N/A')}")
        
        # Test financial statements
        print(f"\n📈 FINANCIAL STATEMENTS for {symbol}:")
        
        # Income Statement
        income_stmt = ticker.financials
        print(f"Income Statement Shape: {income_stmt.shape if income_stmt is not None and not income_stmt.empty else 'No data'}")
        if income_stmt is not None and not income_stmt.empty:
            print("Income Statement Columns (first 5):")
            print(list(income_stmt.columns[:5]))
            print("Income Statement Index (first 10):")
            print(list(income_stmt.index[:10]))
        
        # Balance Sheet
        balance_sheet = ticker.balance_sheet
        print(f"Balance Sheet Shape: {balance_sheet.shape if balance_sheet is not None and not balance_sheet.empty else 'No data'}")
        if balance_sheet is not None and not balance_sheet.empty:
            print("Balance Sheet Index (first 10):")
            print(list(balance_sheet.index[:10]))
        
        # Cash Flow
        cashflow = ticker.cashflow
        print(f"Cash Flow Shape: {cashflow.shape if cashflow is not None and not cashflow.empty else 'No data'}")
        if cashflow is not None and not cashflow.empty:
            print("Cash Flow Index (first 10):")
            print(list(cashflow.index[:10]))
        
        # Test historical data
        print(f"\n📊 HISTORICAL PRICE DATA for {symbol}:")
        hist = ticker.history(period="5y", interval="1mo")
        print(f"History Shape: {hist.shape if hist is not None and not hist.empty else 'No data'}")
        if hist is not None and not hist.empty:
            print("History Columns:")
            print(list(hist.columns))
            print("Sample data (last 3 months):")
            print(hist.tail(3))
        
        # Test specific key metrics from info
        print(f"\n🔍 KEY METRICS for {symbol}:")
        key_metrics = [
            'trailingPE', 'forwardPE', 'priceToBook', 'priceToSalesTrailing12Months',
            'returnOnEquity', 'returnOnAssets', 'grossMargins', 'operatingMargins',
            'dividendYield', 'payoutRatio', 'currentRatio', 'debtToEquity',
            'revenueGrowth', 'earningsGrowth', 'freeCashflow', 'beta'
        ]
        
        available_metrics = {}
        for metric in key_metrics:
            value = info.get(metric)
            if value is not None:
                available_metrics[metric] = value
        
        print(f"Available key metrics: {len(available_metrics)}/{len(key_metrics)}")
        for metric, value in list(available_metrics.items())[:8]:  # Show first 8
            print(f"  {metric}: {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing {symbol}: {e}")
        return False

def main():
    """Test multiple companies to understand data patterns"""
    print("🔍 YFINANCE DATA STRUCTURE ANALYSIS")
    print("Testing different company types to understand data availability")
    
    # Test different types of companies
    test_companies = [
        "AAPL",  # Large tech company
        "MSFT",  # Another large tech
        "JNJ",   # Healthcare/Pharma
        "JPM",   # Financial services
        "XOM",   # Energy
        "TSLA",  # Growth stock
        "KO",    # Consumer staples
        "ASML",  # European tech (ADR)
    ]
    
    successful_tests = 0
    for symbol in test_companies:
        success = test_company_data(symbol)
        if success:
            successful_tests += 1
    
    print(f"\n{'='*80}")
    print(f"SUMMARY: {successful_tests}/{len(test_companies)} companies tested successfully")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()