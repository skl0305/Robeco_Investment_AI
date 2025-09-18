#!/usr/bin/env python3
"""
Test script to debug Call 2 premature termination issue
"""

import asyncio
import sys
import os
import logging

# Add project root to path
sys.path.append('/Users/skl/Desktop/Robeco Reporting')

from src.robeco.backend.template_report_generator import TemplateReportGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_call2_generation():
    """Test Call 2 generation with enhanced debugging"""
    print("🔍 Starting Call 2 debugging test...")
    
    generator = TemplateReportGenerator()
    
    # Test data
    company_name = "Apple Inc."
    ticker = "AAPL"
    investment_objective = "Growth"
    user_query = "Generate comprehensive investment analysis"
    
    try:
        print("📊 Starting report generation...")
        result = await generator.generate_report(
            company_name=company_name,
            ticker=ticker,
            investment_objective=investment_objective,
            user_query=user_query,
            websocket=None,
            connection_id="debug_test"
        )
        
        print(f"✅ Report generation completed!")
        print(f"📏 Call 1 length: {len(result.get('call1_content', '')):,} chars")
        print(f"📏 Call 2 length: {len(result.get('call2_content', '')):,} chars")
        print(f"📊 Call 1 complete: {result.get('call1_complete', False)}")
        print(f"📊 Call 2 complete: {result.get('call2_complete', False)}")
        
        # Check for premature termination indicators
        call2_content = result.get('call2_content', '')
        if call2_content:
            print(f"📄 Call 2 ending: ...{call2_content[-200:]}")
            if len(call2_content) < 5000:
                print("🚨 POTENTIAL ISSUE: Call 2 content is suspiciously short!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_call2_generation())