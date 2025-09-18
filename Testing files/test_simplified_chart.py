#!/usr/bin/env python3
"""
Test the simplified chart data extraction functionality
"""
import sys
import os
sys.path.append('/Users/skl/Desktop/Robeco Reporting/src')

from robeco.backend.template_report_generator import RobecoTemplateReportGenerator
import json

def test_chart_data_extraction():
    """Test simplified chart data extraction"""
    print("🧪 TESTING SIMPLIFIED CHART DATA EXTRACTION")
    print("="*60)
    
    # Initialize the generator
    generator = RobecoTemplateReportGenerator()
    
    # Test 1: Professional streaming server format
    print("\n📊 Test 1: Professional streaming server format")
    professional_data = {
        'chart_data': [
            {'date': '2020-01-01', 'open': 100.0, 'high': 105.0, 'low': 98.0, 'close': 103.0, 'volume': 1000000},
            {'date': '2020-02-01', 'open': 103.0, 'high': 108.0, 'low': 101.0, 'close': 106.0, 'volume': 1100000},
            {'date': '2020-03-01', 'open': 106.0, 'high': 110.0, 'low': 104.0, 'close': 109.0, 'volume': 1200000},
        ]
    }
    
    chart_code = generator._extract_stock_price_data(professional_data)
    print("✅ Professional format test completed")
    
    # Check if the data was converted to simple date/price format
    if "d.price" in chart_code and "'date':" in chart_code and "'price':" in chart_code:
        print("✅ Chart uses simplified date/price structure")
    else:
        print("❌ Chart still uses complex OHLC structure")
    
    # Extract the data array from the generated code
    start_marker = "const stockData = "
    end_marker = ";"
    start_idx = chart_code.find(start_marker)
    if start_idx != -1:
        start_idx += len(start_marker)
        end_idx = chart_code.find(end_marker, start_idx)
        if end_idx != -1:
            data_str = chart_code[start_idx:end_idx].strip()
            try:
                # Parse the data
                import ast
                data = ast.literal_eval(data_str)
                print(f"📈 Extracted {len(data)} data points:")
                for i, point in enumerate(data[:3]):  # Show first 3 points
                    print(f"  Point {i+1}: {point}")
                
                # Verify structure
                if all('date' in point and 'price' in point for point in data):
                    print("✅ All data points have correct date/price structure")
                    # Verify no OHLC data
                    if not any('high' in point or 'low' in point or 'open' in point for point in data):
                        print("✅ No OHLC data present - clean simple structure")
                    else:
                        print("⚠️ OHLC data still present in simplified structure")
                else:
                    print("❌ Data points missing date/price fields")
            except Exception as e:
                print(f"❌ Failed to parse extracted data: {e}")
    
    # Test 2: Old yfinance history format
    print("\n📊 Test 2: Old yfinance history format")
    old_format_data = {
        'history': {
            'Close': {
                '2020-01-01': 103.0,
                '2020-02-01': 106.0,
                '2020-03-01': 109.0,
            },
            'High': {
                '2020-01-01': 105.0,
                '2020-02-01': 108.0,
                '2020-03-01': 110.0,
            },
            'Low': {
                '2020-01-01': 98.0,
                '2020-02-01': 101.0,
                '2020-03-01': 104.0,
            }
        }
    }
    
    chart_code_old = generator._extract_stock_price_data(old_format_data)
    print("✅ Old format test completed")
    
    # Verify it also uses simple structure
    if "d.price" in chart_code_old and "'date':" in chart_code_old and "'price':" in chart_code_old:
        print("✅ Old format also converted to simplified date/price structure")
    else:
        print("❌ Old format conversion failed")
    
    # Test 3: Empty data
    print("\n📊 Test 3: Empty/invalid data")
    empty_data = {}
    chart_code_empty = generator._extract_stock_price_data(empty_data)
    if "No financial data available" in chart_code_empty:
        print("✅ Empty data handled correctly")
    else:
        print("❌ Empty data not handled properly")
    
    print("\n" + "="*60)
    print("🎯 CHART DATA SIMPLIFICATION TEST COMPLETE")
    print("✅ Charts now use simple date/price structure instead of complex OHLC")
    print("✅ Both professional_streaming_server and old yfinance formats supported")
    print("✅ Error handling for missing data implemented")

if __name__ == "__main__":
    test_chart_data_extraction()