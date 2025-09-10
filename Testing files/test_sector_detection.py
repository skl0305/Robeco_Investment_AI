#!/usr/bin/env python3
"""
Test the enhanced sector detection system
"""

import sys
sys.path.append('/Users/skl/Desktop/Robeco Reporting/src')

from robeco.prompts.enhanced_sector_prompts import SectorDetector, get_enhanced_analyst_prompt

def test_sector_detection():
    """Test sector detection with sample data"""
    
    test_cases = [
        {
            'ticker': 'BUOU.SI',
            'company': 'Frasers Logistics & Commercial Trust',
            'info': {'sector': 'Real Estate', 'industry': 'REIT - Industrial'},
            'expected': 'reit'
        },
        {
            'ticker': 'AAPL', 
            'company': 'Apple Inc',
            'info': {'sector': 'Technology', 'industry': 'Consumer Electronics'},
            'expected': 'technology'
        },
        {
            'ticker': 'JPM',
            'company': 'JPMorgan Chase & Co',
            'info': {'sector': 'Financial Services', 'industry': 'Banks - Diversified'},
            'expected': 'banking'
        },
        {
            'ticker': 'JNJ',
            'company': 'Johnson & Johnson', 
            'info': {'sector': 'Healthcare', 'industry': 'Drug Manufacturers - General'},
            'expected': 'healthcare'
        }
    ]
    
    print("=== SECTOR DETECTION TEST ===")
    for case in test_cases:
        financial_data = {'info': case['info']}
        detected = SectorDetector.detect_sector(financial_data)
        sector_info = SectorDetector.get_sector_info(detected)
        
        status = "✅ PASS" if detected == case['expected'] else "❌ FAIL"
        
        print(f"\n{case['ticker']} - {case['company']}")
        print(f"  Expected: {case['expected']}")
        print(f"  Detected: {detected} {status}")
        print(f"  Sector Name: {sector_info['name']}")
        print(f"  Key Metrics: {sector_info['key_metrics'][:3]}")
        print(f"  Research Keywords: {sector_info['research_keywords'][:3]}")

def test_enhanced_prompts():
    """Test enhanced prompt generation"""
    
    # Test REIT analysis
    print("\n=== ENHANCED PROMPT TEST ===")
    
    reit_data = {
        'info': {
            'sector': 'Real Estate',
            'industry': 'REIT - Industrial',
            'longName': 'Frasers Logistics & Commercial Trust'
        }
    }
    
    try:
        enhanced_prompt = get_enhanced_analyst_prompt(
            analyst_type='fundamentals',
            company='Frasers Logistics & Commercial Trust',
            ticker='BUOU.SI',
            financial_data=reit_data,
            user_query='Comprehensive REIT analysis'
        )
        
        # Check if sector-specific content is included
        reit_checks = [
            'FFO' in enhanced_prompt,
            'AFFO' in enhanced_prompt, 
            'REIT' in enhanced_prompt,
            'Distribution' in enhanced_prompt,
            'Real Estate Investment Trust' in enhanced_prompt
        ]
        
        passed = sum(reit_checks)
        print(f"REIT Sector Enhancement: {passed}/5 checks passed")
        
        if passed >= 4:
            print("✅ REIT sector enhancement working correctly")
        else:
            print("❌ REIT sector enhancement needs improvement")
            print("Missing elements in prompt")
            
    except Exception as e:
        print(f"❌ Enhanced prompt generation failed: {e}")

if __name__ == "__main__":
    test_sector_detection()
    test_enhanced_prompts()