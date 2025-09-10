#!/usr/bin/env python3
"""
Test Corrected Template Generator
Verify that the updated prompt produces reports matching Robeco template structure
"""

import sys
import os
import asyncio
from datetime import datetime

# Add the project root to Python path
sys.path.append('src')

from robeco.backend.template_report_generator import RobecoTemplateReportGenerator

async def test_corrected_template():
    print('🧪 TESTING CORRECTED TEMPLATE GENERATOR')
    print('=' * 60)
    
    # Initialize the generator
    generator = RobecoTemplateReportGenerator()
    
    # Test parameters
    test_params = {
        'company_name': 'Apple Inc',
        'ticker': 'AAPL',
        'available_analyses': [],  # Test without specialist analyses first
        'financial_data': {
            'revenue': '$394.3B',
            'net_income': '$99.8B',
            'pe_ratio': '29.1x',
            'market_cap': '$3.0T'
        }
    }
    
    print(f"🎯 Testing company: {test_params['company_name']} ({test_params['ticker']})")
    print(f"📊 Using basic financial data only")
    print(f"🔬 Focus: Template structure validation")
    print()
    
    try:
        # Generate the report
        print("🚀 Generating report with corrected template...")
        report_html = await generator.generate_report_from_analyses(
            company_name=test_params['company_name'],
            ticker=test_params['ticker'],
            analyses_data={},  # Empty analyses data for template structure test
            financial_data=test_params['financial_data']
        )
        
        if not report_html:
            print("❌ CRITICAL: No report generated!")
            return False
            
        print(f"✅ Report generated successfully!")
        print(f"📏 Report length: {len(report_html):,} characters")
        print()
        
        # Check for exact Robeco template sections
        required_sections = [
            'REASON TO ANALYZE',
            'LONG TERM OUTLOOK', 
            'FUNDAMENTAL CONCLUSION',
            'FIT WITH TOP-DOWN VIEW',
            'VALUATION',
            'RISKS',
            'QUANTITATIVE CONCLUSION',
            'SHORT TERM OUTLOOK',
            'EARNINGS REVISIONS'
        ]
        
        print("🔍 CHECKING TEMPLATE STRUCTURE COMPLIANCE:")
        print("-" * 45)
        
        structure_check = {
            'sections_found': 0,
            'missing_sections': [],
            'has_robeco_logo': False,
            'has_company_header': False,
            'has_analysis_items': False,
            'professional_content': False
        }
        
        # Check each required section
        for section in required_sections:
            if f'<strong>{section}</strong>' in report_html or f'**{section}**' in report_html:
                structure_check['sections_found'] += 1
                print(f"  ✅ {section}: FOUND")
            else:
                structure_check['missing_sections'].append(section)
                print(f"  ❌ {section}: MISSING")
        
        # Check other structural elements
        structure_check['has_robeco_logo'] = 'robeco-logo-container' in report_html
        structure_check['has_company_header'] = 'company-header' in report_html  
        structure_check['has_analysis_items'] = 'analysis-item' in report_html
        
        # Check for professional investment language
        professional_terms = ['catalyst', 'tailwinds', 'headwinds', 'EBITDA', 'volatility', 'compelling', 'Our analysis']
        terms_found = sum(1 for term in professional_terms if term.lower() in report_html.lower())
        structure_check['professional_content'] = terms_found >= 3
        
        print()
        print("📊 STRUCTURE VALIDATION SUMMARY:")
        print("-" * 35)
        print(f"  Required sections found: {structure_check['sections_found']}/{len(required_sections)}")
        print(f"  Robeco logo container: {'✅' if structure_check['has_robeco_logo'] else '❌'}")
        print(f"  Company header structure: {'✅' if structure_check['has_company_header'] else '❌'}")
        print(f"  Analysis item divs: {'✅' if structure_check['has_analysis_items'] else '❌'}")
        print(f"  Professional investment language: {'✅' if structure_check['professional_content'] else '❌'} ({terms_found} terms)")
        
        # Overall compliance score
        compliance_score = (
            (structure_check['sections_found'] / len(required_sections)) * 0.6 +  # 60% weight for sections
            (1 if structure_check['has_analysis_items'] else 0) * 0.2 +  # 20% weight for structure
            (1 if structure_check['professional_content'] else 0) * 0.2   # 20% weight for content
        ) * 100
        
        print()
        print(f"🎯 OVERALL COMPLIANCE SCORE: {compliance_score:.1f}%")
        
        if compliance_score >= 90:
            print("🎉 EXCELLENT: Template structure fully compliant!")
            result = "PASS"
        elif compliance_score >= 70:
            print("⚠️  GOOD: Minor template structure issues")
            result = "PARTIAL_PASS"
        else:
            print("❌ FAIL: Major template structure problems")
            result = "FAIL"
        
        # Show missing sections
        if structure_check['missing_sections']:
            print()
            print("🚨 MISSING SECTIONS:")
            for section in structure_check['missing_sections']:
                print(f"   • {section}")
        
        # Save test report for inspection
        output_file = f"/Users/skl/Desktop/Robeco Reporting/test_corrected_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report_html)
        print(f"\n💾 Test report saved: {output_file}")
        
        # Show content sample
        print("\n📄 CONTENT SAMPLE (first 500 characters):")
        print("-" * 45)
        sample = report_html[:500].replace('<', '&lt;').replace('>', '&gt;')
        print(f'"{sample}..."')
        
        return result == "PASS"
        
    except Exception as e:
        print(f"❌ ERROR during report generation: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    try:
        success = asyncio.run(test_corrected_template())
        if success:
            print("\n🎉 Template correction test: PASSED!")
            print("✅ Report generator now produces Robeco-compliant structure")
        else:
            print("\n❌ Template correction test: FAILED")
            print("🔧 Additional fixes needed")
    except Exception as e:
        print(f"\n💥 Test execution failed: {e}")