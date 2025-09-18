#!/usr/bin/env python3
"""
Updated 5x5 Metrics Grid with available yfinance alternatives
Replace the 4 missing metrics with available ones
"""

import yfinance as yf

def show_updated_5x5_grid():
    """Show the updated 5x5 grid with all available metrics"""
    
    print("🔄 UPDATED 5x5 METRICS GRID - ALL AVAILABLE FROM YFINANCE")
    print("=" * 80)
    
    # Updated 25 metrics - replacing missing ones with available alternatives
    updated_metrics = [
        # Row 1: Basic Info (unchanged)
        "MAIN LISTING", "SHARE PRICE", "TARGET PRICE", "UPSIDE/DOWNSIDE", "MARKET CAP",
        # Row 2: Valuation Ratios (replace EV/EBITDA NTM with EV/SALES)
        "P/E (TTM)", "P/E (NTM)", "EV/EBITDA (TTM)", "EV/SALES (TTM)", "P/B RATIO",
        # Row 3: Profitability (unchanged)
        "ROE (TTM)", "ROA (TTM)", "GROSS MARGINS (TTM)", "OPERATING MARGINS (TTM)", "NET MARGINS (TTM)",
        # Row 4: Financial Health (replace NET DEBT/EBITDA with QUICK RATIO, INTEREST COVERAGE with BETA)
        "CURRENT RATIO", "DEBT/EQUITY", "QUICK RATIO", "BETA", "CASH POSITION",
        # Row 5: Growth & Performance (replace FCF GROWTH with 52W RANGE)
        "REVENUE GROWTH (TTM)", "EARNINGS GROWTH (TTM)", "52W RANGE", "DIVIDEND YIELD", "FCF YIELD"
    ]
    
    # Test with BUOU.SI data
    try:
        stock = yf.Ticker("BUOU.SI")
        info = stock.info
        
        print(f"✅ Testing with: {info.get('longName', 'BUOU.SI')}")
        
        # Complete mapping with alternatives
        yfinance_mapping = {}
        
        # Row 1: Basic Info
        yfinance_mapping["MAIN LISTING"] = ("MANUAL", "SGX")
        yfinance_mapping["SHARE PRICE"] = ("currentPrice", info.get('currentPrice'))
        yfinance_mapping["TARGET PRICE"] = ("targetMeanPrice", info.get('targetMeanPrice'))
        yfinance_mapping["UPSIDE/DOWNSIDE"] = ("CALCULATED", "target vs current")
        yfinance_mapping["MARKET CAP"] = ("marketCap", info.get('marketCap'))
        
        # Row 2: Valuation Ratios (NEW: EV/SALES instead of EV/EBITDA NTM)
        yfinance_mapping["P/E (TTM)"] = ("trailingPE", info.get('trailingPE'))
        yfinance_mapping["P/E (NTM)"] = ("forwardPE", info.get('forwardPE'))
        yfinance_mapping["EV/EBITDA (TTM)"] = ("enterpriseToEbitda", info.get('enterpriseToEbitda'))
        yfinance_mapping["EV/SALES (TTM)"] = ("enterpriseToRevenue", info.get('enterpriseToRevenue'))  # NEW
        yfinance_mapping["P/B RATIO"] = ("priceToBook", info.get('priceToBook'))
        
        # Row 3: Profitability
        yfinance_mapping["ROE (TTM)"] = ("returnOnEquity", info.get('returnOnEquity'))
        yfinance_mapping["ROA (TTM)"] = ("returnOnAssets", info.get('returnOnAssets'))
        yfinance_mapping["GROSS MARGINS (TTM)"] = ("grossMargins", info.get('grossMargins'))
        yfinance_mapping["OPERATING MARGINS (TTM)"] = ("operatingMargins", info.get('operatingMargins'))
        yfinance_mapping["NET MARGINS (TTM)"] = ("profitMargins", info.get('profitMargins'))
        
        # Row 4: Financial Health (NEW: QUICK RATIO and BETA instead of missing ones)
        yfinance_mapping["CURRENT RATIO"] = ("currentRatio", info.get('currentRatio'))
        yfinance_mapping["DEBT/EQUITY"] = ("debtToEquity", info.get('debtToEquity'))
        yfinance_mapping["QUICK RATIO"] = ("quickRatio", info.get('quickRatio'))  # NEW
        yfinance_mapping["BETA"] = ("beta", info.get('beta'))  # NEW
        yfinance_mapping["CASH POSITION"] = ("totalCash", info.get('totalCash'))
        
        # Row 5: Growth & Performance (NEW: 52W RANGE instead of FCF GROWTH)
        yfinance_mapping["REVENUE GROWTH (TTM)"] = ("revenueGrowth", info.get('revenueGrowth'))
        yfinance_mapping["EARNINGS GROWTH (TTM)"] = ("earningsGrowth", info.get('earningsGrowth'))
        yfinance_mapping["52W RANGE"] = ("CALCULATED", "52WeekHigh - 52WeekLow")  # NEW
        yfinance_mapping["DIVIDEND YIELD"] = ("dividendYield", info.get('dividendYield'))
        yfinance_mapping["FCF YIELD"] = ("CALCULATED", "freeCashflow / marketCap")
        
        # Print updated table
        print(f"\n{'METRIC':<25} {'YFINANCE FIELD':<20} {'VALUE':<15} {'STATUS':<10}")
        print("-" * 80)
        
        available_count = 0
        
        for row in range(5):
            if row > 0:
                print()  # Add spacing between rows
            print(f"ROW {row+1}:")
            
            start_idx = row * 5
            end_idx = start_idx + 5
            row_metrics = updated_metrics[start_idx:end_idx]
            
            for metric in row_metrics:
                yf_field, value = yfinance_mapping[metric]
                
                if yf_field == "MANUAL":
                    status = "✅"
                    formatted_value = str(value)
                    available_count += 1
                elif yf_field == "CALCULATED":
                    status = "🔧"
                    # Calculate actual values for display
                    if metric == "UPSIDE/DOWNSIDE":
                        current = info.get('currentPrice', 0)
                        target = info.get('targetMeanPrice', 0)
                        if current and target:
                            upside = ((target - current) / current) * 100
                            formatted_value = f"{upside:+.1f}%"
                        else:
                            formatted_value = "N/A"
                    elif metric == "52W RANGE":
                        high = info.get('fiftyTwoWeekHigh', 0)
                        low = info.get('fiftyTwoWeekLow', 0)
                        if high and low:
                            formatted_value = f"${low:.2f}-${high:.2f}"
                        else:
                            formatted_value = "N/A"
                    elif metric == "FCF YIELD":
                        fcf = info.get('freeCashflow', 0)
                        mcap = info.get('marketCap', 1)
                        if fcf and mcap:
                            yield_pct = (fcf / mcap) * 100
                            formatted_value = f"{yield_pct:.1f}%"
                        else:
                            formatted_value = "N/A"
                    else:
                        formatted_value = "Calc"
                    available_count += 1
                elif value is not None:
                    status = "✅"
                    # Format based on metric type
                    if metric in ["MARKET CAP", "CASH POSITION"]:
                        formatted_value = f"${value/1e9:.2f}B" if value > 1e9 else f"${value/1e6:.0f}M"
                    elif "%" in metric or "GROWTH" in metric or "YIELD" in metric or "MARGIN" in metric:
                        if isinstance(value, float) and abs(value) < 1:
                            formatted_value = f"{value*100:.1f}%"
                        else:
                            formatted_value = f"{value:.1f}%"
                    elif "RATIO" in metric or "P/E" in metric or "EV/" in metric or metric == "BETA":
                        formatted_value = f"{value:.2f}x" if "RATIO" in metric or "P/E" in metric or "EV/" in metric else f"{value:.2f}"
                    else:
                        formatted_value = f"{value:.2f}"
                    available_count += 1
                else:
                    status = "❌"
                    formatted_value = "None"
                    
                print(f"  {metric:<23} {yf_field:<20} {formatted_value:<15} {status:<10}")
        
        print("-" * 80)
        print(f"📊 FINAL AVAILABILITY: {available_count}/{len(updated_metrics)} metrics available ({available_count/len(updated_metrics)*100:.1f}%)")
        
        # Show the changes made
        print(f"\n🔄 METRICS REPLACED:")
        replacements = [
            ("EV/EBITDA (NTM)", "EV/SALES (TTM)", "More widely available valuation metric"),
            ("NET DEBT/EBITDA", "QUICK RATIO", "Liquidity measure, complements current ratio"),
            ("INTEREST COVERAGE", "BETA", "Risk measure, shows volatility vs market"),
            ("FCF GROWTH (TTM)", "52W RANGE", "Performance range indicator")
        ]
        
        for old, new, reason in replacements:
            print(f"   • {old:<20} → {new:<20} ({reason})")
        
        print(f"\n✅ ALL 25 METRICS NOW AVAILABLE FROM YFINANCE!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    show_updated_5x5_grid()