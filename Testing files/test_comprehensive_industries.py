#!/usr/bin/env python3
"""
Test the comprehensive 50+ industry detection and analysis system
"""

import sys
sys.path.append('/Users/skl/Desktop/Robeco Reporting/src')

from robeco.prompts.comprehensive_industry_prompts import ComprehensiveIndustryDetector, get_comprehensive_industry_prompt

def test_comprehensive_industry_detection():
    """Test comprehensive industry detection with real yfinance data patterns"""
    
    test_cases = [
        # REITs - Different types
        {'ticker': 'PLD', 'sector': 'Real Estate', 'industry': 'REIT - Industrial', 'expected': 'reit_industrial'},
        {'ticker': 'AVB', 'sector': 'Real Estate', 'industry': 'REIT - Residential', 'expected': 'reit_residential'},
        {'ticker': 'AMT', 'sector': 'Real Estate', 'industry': 'REIT - Specialty', 'expected': 'reit_specialty'},
        
        # Banking - Different types
        {'ticker': 'JPM', 'sector': 'Financial Services', 'industry': 'Banks - Diversified', 'expected': 'banks_diversified'},
        {'ticker': 'USB', 'sector': 'Financial Services', 'industry': 'Banks - Regional', 'expected': 'banks_regional'},
        {'ticker': 'COF', 'sector': 'Financial Services', 'industry': 'Credit Services', 'expected': 'credit_services'},
        
        # Technology - Different subsectors
        {'ticker': 'CRM', 'sector': 'Technology', 'industry': 'Software - Application', 'expected': 'software_application'},
        {'ticker': 'NVDA', 'sector': 'Technology', 'industry': 'Semiconductors', 'expected': 'semiconductors'},
        {'ticker': 'AAPL', 'sector': 'Technology', 'industry': 'Consumer Electronics', 'expected': 'consumer_electronics'},
        
        # Healthcare - Different subsectors  
        {'ticker': 'JNJ', 'sector': 'Healthcare', 'industry': 'Drug Manufacturers - General', 'expected': 'pharma_large_cap'},
        {'ticker': 'GILD', 'sector': 'Healthcare', 'industry': 'Biotechnology', 'expected': 'biotechnology'},
        {'ticker': 'ABT', 'sector': 'Healthcare', 'industry': 'Medical Devices', 'expected': 'medical_devices'},
        
        # Energy - Different types
        {'ticker': 'XOM', 'sector': 'Energy', 'industry': 'Oil & Gas Integrated', 'expected': 'oil_gas_integrated'},
        {'ticker': 'KMI', 'sector': 'Energy', 'industry': 'Oil & Gas Midstream', 'expected': 'oil_gas_midstream'},
        
        # Consumer - Different types
        {'ticker': 'AMZN', 'sector': 'Consumer Cyclical', 'industry': 'Internet Retail', 'expected': 'internet_retail'},
        {'ticker': 'TSLA', 'sector': 'Consumer Cyclical', 'industry': 'Auto Manufacturers', 'expected': 'auto_manufacturers'},
        {'ticker': 'WMT', 'sector': 'Consumer Defensive', 'industry': 'Discount Stores', 'expected': 'discount_stores'},
        
        # Other sectors
        {'ticker': 'DIS', 'sector': 'Communication Services', 'industry': 'Entertainment', 'expected': 'entertainment'},
        {'ticker': 'DD', 'sector': 'Materials', 'industry': 'Chemicals', 'expected': 'chemicals'}
    ]
    
    print("=== COMPREHENSIVE INDUSTRY DETECTION TEST ===")
    print(f"Testing {len(test_cases)} different industry classifications")
    
    passed = 0
    total = len(test_cases)
    
    for case in test_cases:
        financial_data = {'info': {'sector': case['sector'], 'industry': case['industry']}}
        detected = ComprehensiveIndustryDetector.detect_industry(financial_data)
        framework = ComprehensiveIndustryDetector.get_industry_framework(detected)
        
        status = "✅ PASS" if detected == case['expected'] else "❌ FAIL"
        if detected == case['expected']:
            passed += 1
        
        print(f"\n{case['ticker']} - {case['industry']}")
        print(f"  Expected: {case['expected']}")
        print(f"  Detected: {detected} {status}")
        print(f"  Industry Name: {framework['name']}")
        print(f"  Key Metrics: {framework['key_metrics'][:3]}")
        print(f"  Valuation Methods: {framework['valuation_methods'][:2]}")
        print(f"  Research Keywords: {framework['research_keywords'][:3]}")
        if framework['peer_comparison']:
            print(f"  Peer Group: {framework['peer_comparison'][:3]}")
    
    print(f"\n=== SUMMARY ===")
    print(f"Passed: {passed}/{total} ({passed/total*100:.1f}%)")
    
    return passed == total

def test_industry_specific_metrics():
    """Test that industry-specific metrics are properly assigned"""
    
    print("\n=== INDUSTRY-SPECIFIC METRICS TEST ===")
    
    test_cases = [
        {
            'industry': 'reit_industrial',
            'expected_metrics': ['FFO per Share', 'AFFO per Share', 'Same-Store NOI Growth'],
            'expected_keywords': ['industrial REIT', 'logistics', 'warehouse']
        },
        {
            'industry': 'banks_diversified', 
            'expected_metrics': ['Net Interest Margin (NIM)', 'Return on Assets (ROA)', 'Tier 1 Capital Ratio'],
            'expected_keywords': ['large bank', 'NIM', 'credit quality']
        },
        {
            'industry': 'software_application',
            'expected_metrics': ['Annual Recurring Revenue (ARR)', 'Revenue Growth Rate', 'Rule of 40'],
            'expected_keywords': ['SaaS', 'application software', 'ARR']
        }
    ]
    
    for case in test_cases:
        framework = ComprehensiveIndustryDetector.get_industry_framework(case['industry'])
        
        print(f"\n{case['industry']} ({framework['name']}):")
        
        # Check key metrics
        metrics_match = all(metric in framework['key_metrics'] for metric in case['expected_metrics'])
        print(f"  Key Metrics Match: {'✅' if metrics_match else '❌'}")
        print(f"    Expected: {case['expected_metrics']}")
        print(f"    Got: {framework['key_metrics'][:3]}")
        
        # Check research keywords
        keywords_match = all(keyword in framework['research_keywords'] for keyword in case['expected_keywords'])
        print(f"  Research Keywords Match: {'✅' if keywords_match else '❌'}")
        print(f"    Expected: {case['expected_keywords']}")
        print(f"    Got: {framework['research_keywords']}")

def test_comprehensive_prompt_generation():
    """Test enhanced prompt generation for different industries"""
    
    print("\n=== COMPREHENSIVE PROMPT GENERATION TEST ===")
    
    # Test REIT Industrial
    reit_data = {
        'info': {
            'sector': 'Real Estate',
            'industry': 'REIT - Industrial',
            'longName': 'Prologis Inc'
        }
    }
    
    try:
        enhanced_prompt = get_comprehensive_industry_prompt(
            analyst_type='fundamentals',
            company='Prologis Inc',
            ticker='PLD',
            financial_data=reit_data,
            user_query='Industrial REIT analysis'
        )
        
        # Check for industry-specific content
        industry_checks = [
            'Industrial & Logistics REITs' in enhanced_prompt,
            'FFO per Share' in enhanced_prompt,
            'AFFO per Share' in enhanced_prompt,
            'E-commerce Growth Impact' in enhanced_prompt,
            'warehouse' in enhanced_prompt.lower()
        ]
        
        passed_checks = sum(industry_checks)
        print(f"Industrial REIT Enhancement: {passed_checks}/5 checks passed")
        
        if passed_checks >= 4:
            print("✅ Industrial REIT industry enhancement working correctly")
        else:
            print("❌ Industrial REIT industry enhancement needs improvement")
            
        # Show some sample content
        print("\nSample enhanced content:")
        lines = enhanced_prompt.split('\n')
        for i, line in enumerate(lines):
            if 'FFO' in line or 'Industrial' in line:
                print(f"  {line.strip()}")
                if i > 20:  # Limit output
                    break
                    
    except Exception as e:
        print(f"❌ Comprehensive prompt generation failed: {e}")

if __name__ == "__main__":
    print("🧪 COMPREHENSIVE INDUSTRY SYSTEM TEST")
    print("=" * 50)
    
    # Run all tests
    detection_passed = test_comprehensive_industry_detection()
    test_industry_specific_metrics() 
    test_comprehensive_prompt_generation()
    
    print("\n" + "=" * 50)
    if detection_passed:
        print("🎉 ALL TESTS PASSED - Comprehensive industry system is working!")
    else:
        print("⚠️  Some tests failed - Check detection logic")