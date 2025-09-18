#!/usr/bin/env python3
"""
Check yfinance data for BUOU.SI (Frasers Logistics & Commercial Trust)
and compare with the report template values
"""

import yfinance as yf
import pandas as pd
from datetime import datetime

def check_buou_data():
    """Check real yfinance data for BUOU.SI"""
    
    print("🔍 Fetching real yfinance data for BUOU.SI (Frasers Logistics & Commercial Trust)...")
    
    try:
        # Fetch the stock data
        stock = yf.Ticker("BUOU.SI")
        info = stock.info
        
        print(f"\n✅ Successfully fetched data for: {info.get('longName', 'BUOU.SI')}")
        print(f"📊 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Template values (what's currently in the report)
        template_values = {
            "MAIN LISTING": "SES",
            "SHARE PRICE": "S$1.08", 
            "TARGET PRICE": "S$1.05",
            "UPSIDE/DOWNSIDE": "-2.8%",
            "MARKET CAP": "S$3.57bn",
            "P/E (TTM)": "28.5x",
            "P/E (NTM)": "27.0x", 
            "EV/EBITDA (TTM)": "22.0x",
            "EV/EBITDA (NTM)": "21.5x",
            "P/B RATIO": "0.86x",
            "ROE (TTM)": "5.5%",
            "ROA (TTM)": "3.2%",
            "GROSS MARGINS (TTM)": "75.0%",
            "OPERATING MARGINS (TTM)": "60.0%", 
            "NET MARGINS (TTM)": "25.0%",
            "CURRENT RATIO": "0.9x",
            "DEBT/EQUITY": "0.85x",
            "NET DEBT/EBITDA": "9.5x", 
            "INTEREST COVERAGE": "3.0x",
            "CASH POSITION": "S$150m",
            "REVENUE GROWTH (TTM)": "3.5%",
            "EARNINGS GROWTH (TTM)": "-5.0%",
            "FCF GROWTH (TTM)": "-8.0%",
            "DIVIDEND YIELD": "6.8%",
            "FCF YIELD": "4.5%"
        }
        
        # Extract real yfinance values
        real_values = {}
        
        # Basic info
        real_values["MAIN LISTING"] = "SGX" if ".SI" in stock.ticker else "Unknown"
        real_values["SHARE PRICE"] = f"S${info.get('currentPrice', 'N/A')}"
        real_values["MARKET CAP"] = f"S${info.get('marketCap', 0) / 1e9:.2f}bn" if info.get('marketCap') else "N/A"
        
        # Valuation ratios
        real_values["P/E (TTM)"] = f"{info.get('trailingPE', 'N/A'):.1f}x" if info.get('trailingPE') else "N/A"
        real_values["P/E (NTM)"] = f"{info.get('forwardPE', 'N/A'):.1f}x" if info.get('forwardPE') else "N/A"
        real_values["EV/EBITDA (TTM)"] = f"{info.get('enterpriseToEbitda', 'N/A'):.1f}x" if info.get('enterpriseToEbitda') else "N/A"
        real_values["P/B RATIO"] = f"{info.get('priceToBook', 'N/A'):.2f}x" if info.get('priceToBook') else "N/A"
        
        # Profitability ratios
        real_values["ROE (TTM)"] = f"{info.get('returnOnEquity', 0) * 100:.1f}%" if info.get('returnOnEquity') else "N/A"
        real_values["ROA (TTM)"] = f"{info.get('returnOnAssets', 0) * 100:.1f}%" if info.get('returnOnAssets') else "N/A"
        real_values["GROSS MARGINS (TTM)"] = f"{info.get('grossMargins', 0) * 100:.1f}%" if info.get('grossMargins') else "N/A"
        real_values["OPERATING MARGINS (TTM)"] = f"{info.get('operatingMargins', 0) * 100:.1f}%" if info.get('operatingMargins') else "N/A"
        real_values["NET MARGINS (TTM)"] = f"{info.get('profitMargins', 0) * 100:.1f}%" if info.get('profitMargins') else "N/A"
        
        # Financial health
        real_values["CURRENT RATIO"] = f"{info.get('currentRatio', 'N/A'):.1f}x" if info.get('currentRatio') else "N/A"
        real_values["DEBT/EQUITY"] = f"{info.get('debtToEquity', 0) / 100:.2f}x" if info.get('debtToEquity') else "N/A"
        real_values["CASH POSITION"] = f"S${info.get('totalCash', 0) / 1e6:.0f}m" if info.get('totalCash') else "N/A"
        
        # Growth rates
        real_values["REVENUE GROWTH (TTM)"] = f"{info.get('revenueGrowth', 0) * 100:.1f}%" if info.get('revenueGrowth') else "N/A"
        real_values["EARNINGS GROWTH (TTM)"] = f"{info.get('earningsGrowth', 0) * 100:.1f}%" if info.get('earningsGrowth') else "N/A"
        
        # Yield metrics  
        real_values["DIVIDEND YIELD"] = f"{info.get('dividendYield', 0) * 100:.1f}%" if info.get('dividendYield') else "N/A"
        
        # Print comparison
        print("\n" + "="*80)
        print("📊 COMPARISON: TEMPLATE vs REAL YFINANCE DATA")
        print("="*80)
        print(f"{'METRIC':<25} {'TEMPLATE VALUE':<15} {'REAL YFINANCE':<15} {'MATCH':<10}")
        print("-"*80)
        
        matches = 0
        total_comparable = 0
        
        for metric in template_values.keys():
            template_val = template_values[metric]
            real_val = real_values.get(metric, "N/A")
            
            if real_val != "N/A":
                total_comparable += 1
                is_match = "✅" if template_val == real_val else "❌"
                if template_val == real_val:
                    matches += 1
            else:
                is_match = "N/A"
                
            print(f"{metric:<25} {template_val:<15} {real_val:<15} {is_match:<10}")
        
        print("-"*80)
        if total_comparable > 0:
            accuracy = (matches / total_comparable) * 100
            print(f"📈 ACCURACY: {matches}/{total_comparable} metrics match ({accuracy:.1f}%)")
        else:
            print("⚠️  No comparable metrics found")
            
        print("\n🔍 KEY OBSERVATIONS:")
        print("- Template values appear to be ESTIMATED/PLACEHOLDER values")
        print("- Real yfinance data shows different metrics")
        print("- Some metrics (like EV/EBITDA NTM, Interest Coverage) not available in yfinance")
        print("- For REITs, focus on: NAV, DPU, Gearing Ratio, WALE")
        
        # Print all available yfinance keys for reference
        print(f"\n📋 Available yfinance info keys ({len(info)} total):")
        for i, key in enumerate(sorted(info.keys())):
            if i % 4 == 0:
                print()
            print(f"{key:<25}", end="")
        print("\n")
        
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return False
    
    return True

if __name__ == "__main__":
    check_buou_data()