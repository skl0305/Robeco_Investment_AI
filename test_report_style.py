#!/usr/bin/env python3
"""
Test Report Style Template Generator
Verify that the updated generator produces report-style paragraphs instead of bullet points
"""

import sys
import os
import asyncio
from datetime import datetime

# Add the project root to Python path
sys.path.append('src')

from robeco.backend.template_report_generator import RobecoTemplateReportGenerator

async def test_report_style():
    print('🧪 TESTING REPORT-STYLE TEMPLATE GENERATOR')
    print('=' * 60)
    
    # Initialize the generator
    generator = RobecoTemplateReportGenerator()
    
    # Test parameters
    test_params = {
        'company_name': 'Frasers Logistics & Commercial Trust',
        'ticker': 'BUOU.SI',
        'available_analyses': [],
        'financial_data': {
            'revenue': 'S$3.53B',
            'market_cap': 'S$3.53B',
            'dividend_yield': '6.76%'
        }
    }
    
    print(f"🎯 Testing: {test_params['company_name']} ({test_params['ticker']})")
    print(f"🔍 Focus: Report-style paragraphs vs bullet points")
    print()
    
    try:
        # Generate the report
        print("🚀 Generating report with report-style structure...")
        report_html = await generator.generate_report_from_analyses(
            company_name=test_params['company_name'],
            ticker=test_params['ticker'],
            analyses_data={},
            financial_data=test_params['financial_data']
        )
        
        if not report_html:
            print("❌ CRITICAL: No report generated!")
            return False
            
        print(f"✅ Report generated successfully!")
        print(f"📏 Report length: {len(report_html):,} characters")
        print()
        
        # Save test report
        output_file = f"/Users/skl/Desktop/Robeco Reporting/test_report_style_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report_html)
        print(f"💾 Test report saved: {output_file}")
        
        # Check for forbidden structures (actual HTML elements, not CSS)
        print("\n🔍 CHECKING STRUCTURE COMPLIANCE:")
        print("-" * 45)
        
        forbidden_checks = {
            'bullet-list-square divs': '<div class="bullet-list-square">' in report_html,
            'h4 subheadings': '<h4>' in report_html,
            'ul lists': '<ul>' in report_html,
            'li items': '<li>' in report_html,
        }
        
        required_checks = {
            'h3 section headers': '<h3>' in report_html,
            'paragraph content': '<p>' in report_html,
            'analysis-sections': 'analysis-sections' in report_html,
        }
        
        # Check forbidden structures
        violations = 0
        for check_name, found in forbidden_checks.items():
            status = "❌ FOUND" if found else "✅ CLEAN"
            print(f"  {status} {check_name}")
            if found:
                violations += 1
        
        # Check required structures  
        missing = 0
        for check_name, found in required_checks.items():
            status = "✅ FOUND" if found else "❌ MISSING"
            print(f"  {status} {check_name}")
            if not found:
                missing += 1
        
        print(f"\n📊 STRUCTURE COMPLIANCE:")
        print(f"   Violations (forbidden elements): {violations}")
        print(f"   Missing (required elements): {missing}")
        
        if violations == 0 and missing == 0:
            print("🎉 PERFECT: Report-style structure compliance!")
            result = "PASS"
        elif violations > 0:
            print("❌ FAIL: Contains forbidden bullet point structures")
            result = "FAIL"
        else:
            print("⚠️  PARTIAL: Missing some required elements")
            result = "PARTIAL"
        
        # Show content sample from slide 3+ (where report style should be used)
        import re
        slide_3_match = re.search(r'<h3>1\. INVESTMENT HIGHLIGHTS</h3>(.*?)</section>', report_html, re.DOTALL)
        if slide_3_match:
            slide_3_content = slide_3_match.group(1)
            print(f"\n📄 SLIDE 3 CONTENT SAMPLE (INVESTMENT HIGHLIGHTS):")
            print("-" * 45)
            # Clean HTML tags for display
            import re
            clean_content = re.sub(r'<[^>]+>', '', slide_3_content)
            print(f'"{clean_content[:300]}..."')
        
        return result == "PASS"
        
    except Exception as e:
        print(f"❌ ERROR during report generation: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    try:
        success = asyncio.run(test_report_style())
        if success:
            print("\n🎉 Report-style template test: PASSED!")
            print("✅ Template generator now produces report-style paragraphs")
        else:
            print("\n❌ Report-style template test: FAILED")
            print("🔧 Additional fixes needed")
    except Exception as e:
        print(f"\n💥 Test execution failed: {e}")