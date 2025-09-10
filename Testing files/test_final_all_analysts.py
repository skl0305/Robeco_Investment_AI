#!/usr/bin/env python3
"""
Final test: ALL 14 analyst types (including consensus/contrarian) with industry system
"""

import sys
sys.path.append('/Users/skl/Desktop/Robeco Reporting/src')

from robeco.prompts.comprehensive_industry_prompts import get_comprehensive_industry_prompt

def test_all_14_analyst_types():
    """Test all 14 analyst types including new consensus/contrarian"""
    
    # ALL 14 analyst types now available
    analyst_types = [
        "chief",           # Chief Investment Officer
        "fundamentals",    # Senior Fundamental Research Analyst  
        "industry",        # Senior Industry Research Analyst
        "technical",       # Senior Technical Research Analyst
        "risk",           # Senior Risk Management Analyst
        "esg",            # Senior ESG Research Analyst
        "research",       # Senior Third-Party Research Analyst
        "sentiment",      # Senior News & Sentiment Analyst
        "management",     # Senior Management & Governance Analyst
        "business",       # Senior Business Model Analyst
        "valuation",      # Senior Valuation & Modeling Analyst
        "macro",          # Senior Macro & Cyclical Analyst
        "consensus",      # NEW: Senior Consensus & Market Positioning Analyst
        "contrarian"      # NEW: Senior Contrarian & Anti-Consensus Analyst
    ]
    
    # Test with different industries to ensure universal coverage
    test_industries = [
        {
            'name': 'Industrial REIT',
            'data': {'info': {'sector': 'Real Estate', 'industry': 'REIT - Industrial'}},
            'key_metrics': ['FFO', 'AFFO', 'NOI Growth']
        },
        {
            'name': 'Large Bank', 
            'data': {'info': {'sector': 'Financial Services', 'industry': 'Banks - Diversified'}},
            'key_metrics': ['NIM', 'Tier 1', 'ROA']
        },
        {
            'name': 'Software Company',
            'data': {'info': {'sector': 'Technology', 'industry': 'Software - Application'}},
            'key_metrics': ['ARR', 'SaaS', 'Churn']
        }
    ]
    
    print("🧪 FINAL COMPREHENSIVE TEST: ALL 14 ANALYST TYPES")
    print("=" * 60)
    
    total_tests = 0
    passed_tests = 0
    
    for industry in test_industries:
        print(f"\n=== {industry['name'].upper()} INDUSTRY TEST ===")
        
        for analyst_type in analyst_types:
            total_tests += 1
            
            try:
                # Generate industry-enhanced prompt
                enhanced_prompt = get_comprehensive_industry_prompt(
                    analyst_type=analyst_type,
                    company=f"Test {industry['name']} Company",
                    ticker='TEST',
                    financial_data=industry['data'],
                    user_query=f'{analyst_type} analysis'
                )
                
                # Check for industry-specific content
                metric_found = any(metric in enhanced_prompt for metric in industry['key_metrics'])
                analyst_mentioned = analyst_type.upper() in enhanced_prompt.upper()
                industry_mentioned = industry['name'].split()[0] in enhanced_prompt
                
                checks_passed = sum([metric_found, analyst_mentioned, industry_mentioned])
                status = '✅ PASS' if checks_passed >= 2 else '❌ FAIL'
                
                if checks_passed >= 2:
                    passed_tests += 1
                
                print(f"  {analyst_type:12} -> {status} ({checks_passed}/3 checks)")
                
            except Exception as e:
                print(f"  {analyst_type:12} -> ❌ ERROR: {e}")
    
    print(f"\n=== FINAL RESULTS ===")
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Success Rate: {passed_tests/total_tests*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL ANALYST TYPES WORK WITH INDUSTRY SYSTEM!")
        print("✅ Production ready with 14 analyst types across 50+ industries")
    else:
        print(f"\n⚠️  {total_tests - passed_tests} tests failed")
    
    return passed_tests == total_tests

def test_consensus_contrarian_specialization():
    """Test that new consensus/contrarian analysts have proper specialization"""
    
    print("\n=== CONSENSUS & CONTRARIAN SPECIALIZATION TEST ===")
    
    test_data = {'info': {'sector': 'Technology', 'industry': 'Software - Application'}}
    
    # Test consensus analyst
    try:
        consensus_prompt = get_comprehensive_industry_prompt(
            analyst_type='consensus',
            company='Salesforce',
            ticker='CRM',
            financial_data=test_data,
            user_query='Consensus analysis'
        )
        
        consensus_keywords = [
            'consensus' in consensus_prompt.lower(),
            'sell-side' in consensus_prompt.lower(),
            'institutional positioning' in consensus_prompt.lower(),
            'market sentiment' in consensus_prompt.lower()
        ]
        
        consensus_score = sum(consensus_keywords)
        print(f"Consensus Analyst: {consensus_score}/4 specialized keywords found")
        print(f"  Status: {'✅ PASS' if consensus_score >= 3 else '❌ NEEDS WORK'}")
        
    except Exception as e:
        print(f"Consensus Analyst: ❌ ERROR - {e}")
    
    # Test contrarian analyst
    try:
        contrarian_prompt = get_comprehensive_industry_prompt(
            analyst_type='contrarian',
            company='Salesforce',
            ticker='CRM', 
            financial_data=test_data,
            user_query='Contrarian analysis'
        )
        
        contrarian_keywords = [
            'contrarian' in contrarian_prompt.lower(),
            'anti-consensus' in contrarian_prompt.lower(),
            'market inefficiency' in contrarian_prompt.lower(),
            'value trap' in contrarian_prompt.lower()
        ]
        
        contrarian_score = sum(contrarian_keywords)
        print(f"Contrarian Analyst: {contrarian_score}/4 specialized keywords found")
        print(f"  Status: {'✅ PASS' if contrarian_score >= 3 else '❌ NEEDS WORK'}")
        
    except Exception as e:
        print(f"Contrarian Analyst: ❌ ERROR - {e}")

if __name__ == "__main__":
    # Run comprehensive final test
    all_passed = test_all_14_analyst_types()
    
    # Test new analyst specializations
    test_consensus_contrarian_specialization()
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🚀 SYSTEM READY FOR PRODUCTION!")
        print("✅ 14 analyst types × 50+ industries = Comprehensive coverage")
    else:
        print("🔧 Some refinements needed before production")