#!/usr/bin/env python3
"""Test syntax of template_report_generator.py"""

import sys
sys.path.append('/Users/skl/Desktop/Robeco Reporting')

try:
    print("Testing import...")
    from src.robeco.backend.template_report_generator import RobecoTemplateReportGenerator
    print("✅ Import successful!")
    
    print("Testing API key stats...")
    from src.robeco.backend.api_key.gemini_api_key import get_api_key_stats
    stats = get_api_key_stats()
    print(f"✅ API Key Stats: {stats}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()