#!/usr/bin/env python3
"""
Check which of the 25 metrics from the 5x5 grid are available from yfinance
and provide the exact yfinance mapping for BUOU.SI
"""

import yfinance as yf
from datetime import datetime

def check_5x5_metrics_availability():
    """Check availability of all 25 metrics from the 5x5 grid"""
    
    print("🔍 Checking 5x5 Metrics Grid Availability for BUOU.SI")
    print("=" * 80)
    
    # The exact 25 metrics from the prompt
    required_metrics = [
        # Row 1: Basic Info
        "MAIN LISTING", "SHARE PRICE", "TARGET PRICE", "UPSIDE/DOWNSIDE", "MARKET CAP",
        # Row 2: Valuation Ratios  
        "P/E (TTM)", "P/E (NTM)", "EV/EBITDA (TTM)", "EV/EBITDA (NTM)", "P/B RATIO",
        # Row 3: Profitability
        "ROE (TTM)", "ROA (TTM)", "GROSS MARGINS (TTM)", "OPERATING MARGINS (TTM)", "NET MARGINS (TTM)",
        # Row 4: Financial Health
        "CURRENT RATIO", "DEBT/EQUITY", "NET DEBT/EBITDA", "INTEREST COVERAGE", "CASH POSITION",
        # Row 5: Growth
        "REVENUE GROWTH (TTM)", "EARNINGS GROWTH (TTM)", "FCF GROWTH (TTM)", "DIVIDEND YIELD", "FCF YIELD"
    ]
    
    try:
        stock = yf.Ticker("BUOU.SI")
        info = stock.info
        print(f"✅ Fetched data for: {info.get('longName', 'BUOU.SI')}")
        
        # Map to yfinance fields
        yfinance_mapping = {}
        
        # Row 1: Basic Info
        yfinance_mapping["MAIN LISTING"] = ("MANUAL", "SGX")  # Always SGX for .SI
        yfinance_mapping["SHARE PRICE"] = ("currentPrice", info.get('currentPrice'))
        yfinance_mapping["TARGET PRICE"] = ("targetMeanPrice", info.get('targetMeanPrice'))  
        yfinance_mapping["UPSIDE/DOWNSIDE"] = ("CALCULATED", "currentPrice vs targetMeanPrice")
        yfinance_mapping["MARKET CAP"] = ("marketCap", info.get('marketCap'))
        
        # Row 2: Valuation Ratios
        yfinance_mapping["P/E (TTM)"] = ("trailingPE", info.get('trailingPE'))
        yfinance_mapping["P/E (NTM)"] = ("forwardPE", info.get('forwardPE'))
        yfinance_mapping["EV/EBITDA (TTM)"] = ("enterpriseToEbitda", info.get('enterpriseToEbitda'))
        yfinance_mapping["EV/EBITDA (NTM)"] = ("NOT_AVAILABLE", None)
        yfinance_mapping["P/B RATIO"] = ("priceToBook", info.get('priceToBook'))
        
        # Row 3: Profitability 
        yfinance_mapping["ROE (TTM)"] = ("returnOnEquity", info.get('returnOnEquity'))
        yfinance_mapping["ROA (TTM)"] = ("returnOnAssets", info.get('returnOnAssets'))
        yfinance_mapping["GROSS MARGINS (TTM)"] = ("grossMargins", info.get('grossMargins'))
        yfinance_mapping["OPERATING MARGINS (TTM)"] = ("operatingMargins", info.get('operatingMargins'))
        yfinance_mapping["NET MARGINS (TTM)"] = ("profitMargins", info.get('profitMargins'))
        
        # Row 4: Financial Health
        yfinance_mapping["CURRENT RATIO"] = ("currentRatio", info.get('currentRatio'))
        yfinance_mapping["DEBT/EQUITY"] = ("debtToEquity", info.get('debtToEquity'))
        yfinance_mapping["NET DEBT/EBITDA"] = ("NOT_AVAILABLE", None)  # Need to calculate
        yfinance_mapping["INTEREST COVERAGE"] = ("NOT_AVAILABLE", None)  # Need financial statements
        yfinance_mapping["CASH POSITION"] = ("totalCash", info.get('totalCash'))
        
        # Row 5: Growth
        yfinance_mapping["REVENUE GROWTH (TTM)"] = ("revenueGrowth", info.get('revenueGrowth'))
        yfinance_mapping["EARNINGS GROWTH (TTM)"] = ("earningsGrowth", info.get('earningsGrowth'))
        yfinance_mapping["FCF GROWTH (TTM)"] = ("NOT_AVAILABLE", None)  # Need historical FCF
        yfinance_mapping["DIVIDEND YIELD"] = ("dividendYield", info.get('dividendYield'))
        yfinance_mapping["FCF YIELD"] = ("CALCULATED", "freeCashflow / marketCap")
        
        # Print availability table
        print(f"\n{'METRIC':<25} {'YFINANCE FIELD':<20} {'VALUE':<15} {'STATUS':<10}")
        print("-" * 80)
        
        available_count = 0
        total_count = len(required_metrics)
        
        for metric in required_metrics:
            yf_field, value = yfinance_mapping[metric]
            
            if yf_field == "NOT_AVAILABLE":
                status = "❌"
                formatted_value = "N/A"
            elif yf_field == "MANUAL":
                status = "✅"
                formatted_value = str(value)
                available_count += 1
            elif yf_field == "CALCULATED":
                status = "🔧"
                formatted_value = "Calc"
                available_count += 1
            elif value is not None:
                status = "✅"
                if metric in ["MARKET CAP", "CASH POSITION"]:
                    formatted_value = f"${value/1e9:.2f}B" if value > 1e9 else f"${value/1e6:.0f}M"
                elif "%" in metric or "GROWTH" in metric or "YIELD" in metric or "MARGIN" in metric:
                    formatted_value = f"{value*100:.1f}%" if isinstance(value, float) and value < 1 else f"{value:.1f}%"
                elif "RATIO" in metric or "P/E" in metric or "EV/" in metric:
                    formatted_value = f"{value:.1f}x"
                else:
                    formatted_value = f"{value:.2f}"
                available_count += 1
            else:
                status = "❌"
                formatted_value = "None"
                
            print(f"{metric:<25} {yf_field:<20} {formatted_value:<15} {status:<10}")
        
        print("-" * 80)
        print(f"📊 AVAILABILITY SUMMARY: {available_count}/{total_count} metrics available ({available_count/total_count*100:.1f}%)")
        
        # Show what needs calculation or manual input
        print(f"\n🔧 METRICS NEEDING CALCULATION:")
        calc_metrics = [k for k, (field, _) in yfinance_mapping.items() if field == "CALCULATED"]
        for metric in calc_metrics:
            print(f"   • {metric}: {yfinance_mapping[metric][1]}")
        
        print(f"\n❌ METRICS NOT AVAILABLE IN YFINANCE:")
        missing_metrics = [k for k, (field, _) in yfinance_mapping.items() if field == "NOT_AVAILABLE"]
        for metric in missing_metrics:
            print(f"   • {metric}: Need alternative data source or estimation")
        
        # Generate the proper grid structure
        print(f"\n📋 SUGGESTED 5x5 GRID WITH REAL DATA:")
        print("=" * 80)
        
        for row in range(5):
            start_idx = row * 5
            end_idx = start_idx + 5
            row_metrics = required_metrics[start_idx:end_idx]
            
            print(f"Row {row+1}:")
            for metric in row_metrics:
                yf_field, value = yfinance_mapping[metric]
                availability = "✅" if yf_field != "NOT_AVAILABLE" and (value is not None or yf_field in ["MANUAL", "CALCULATED"]) else "❌"
                print(f"   {availability} {metric}")
            print()
            
    except Exception as e:
        print(f"❌ Error: {e}")
        
if __name__ == "__main__":
    check_5x5_metrics_availability()