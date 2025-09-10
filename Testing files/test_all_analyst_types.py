#!/usr/bin/env python3
"""
Test ALL analyst types work with comprehensive industry-specific system
"""

import sys
sys.path.append('/Users/skl/Desktop/Robeco Reporting/src')

from robeco.prompts.comprehensive_industry_prompts import get_comprehensive_industry_prompt

def test_all_analyst_types():
    """Test that all 12+ analyst types work with industry enhancement"""
    
    # All available analyst types from professional_investment_analyst.py
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
        "macro"           # Senior Macro & Cyclical Analyst
    ]
    
    # Test with REIT Industrial example
    test_data = {
        'info': {
            'sector': 'Real Estate',
            'industry': 'REIT - Industrial', 
            'longName': 'Prologis Inc'
        }
    }
    
    print("=== ALL ANALYST TYPES INDUSTRY INTEGRATION TEST ===")
    print(f"Testing {len(analyst_types)} analyst types with Industrial REIT example")
    
    results = {}
    
    for analyst_type in analyst_types:
        try:
            # Generate industry-enhanced prompt
            enhanced_prompt = get_comprehensive_industry_prompt(
                analyst_type=analyst_type,
                company='Prologis Inc',
                ticker='PLD',
                financial_data=test_data,
                user_query=f'{analyst_type.title()} analysis of Industrial REIT'
            )
            
            # Check for industry-specific content
            industry_checks = [
                'Industrial & Logistics REITs' in enhanced_prompt,
                'FFO per Share' in enhanced_prompt,
                'AFFO per Share' in enhanced_prompt,
                'warehouse' in enhanced_prompt.lower(),
                analyst_type.upper() in enhanced_prompt.upper()
            ]
            
            passed_checks = sum(industry_checks)
            results[analyst_type] = {
                'status': '✅ PASS' if passed_checks >= 4 else '❌ FAIL',
                'checks_passed': f'{passed_checks}/5',
                'prompt_length': len(enhanced_prompt)
            }
            
            print(f"\n{analyst_type.title()} Analyst:")
            print(f"  Industry Enhancement: {results[analyst_type]['checks_passed']} checks {results[analyst_type]['status']}")
            print(f"  Prompt Length: {results[analyst_type]['prompt_length']:,} characters")
            
            # Show sample analyst-specific content
            lines = enhanced_prompt.split('\n')
            analyst_lines = [line for line in lines if analyst_type.upper() in line.upper()][:2]
            if analyst_lines:
                print(f"  Sample Content: {analyst_lines[0].strip()[:80]}...")
            
        except Exception as e:
            results[analyst_type] = {
                'status': '❌ ERROR',
                'checks_passed': '0/5',
                'error': str(e)
            }
            print(f"\n{analyst_type.title()} Analyst: ❌ ERROR - {e}")
    
    # Summary
    passed_count = sum(1 for r in results.values() if r['status'] == '✅ PASS')
    total_count = len(analyst_types)
    
    print(f"\n=== SUMMARY ===")
    print(f"Analyst Types Tested: {total_count}")
    print(f"Successfully Enhanced: {passed_count}")
    print(f"Success Rate: {passed_count/total_count*100:.1f}%")
    
    return passed_count == total_count

def test_consensus_anti_consensus_analysts():
    """Test if we need to add consensus/anti-consensus analyst types"""
    
    print("\n=== CONSENSUS & ANTI-CONSENSUS ANALYST TEST ===")
    
    # Check if consensus analysis is mentioned in current system
    try:
        consensus_prompt = get_comprehensive_industry_prompt(
            analyst_type='research',  # This handles consensus analysis
            company='Apple Inc',
            ticker='AAPL',
            financial_data={'info': {'sector': 'Technology', 'industry': 'Consumer Electronics'}},
            user_query='Consensus analysis vs contrarian view'
        )
        
        consensus_keywords = [
            'consensus' in consensus_prompt.lower(),
            'contrarian' in consensus_prompt.lower(),
            'third-party research' in consensus_prompt.lower(),
            'analyst consensus' in consensus_prompt.lower(),
            'research synthesis' in consensus_prompt.lower()
        ]
        
        consensus_score = sum(consensus_keywords)
        
        print(f"Current 'research' analyst handles consensus: {consensus_score}/5 keywords found")
        
        if consensus_score >= 3:
            print("✅ Consensus analysis already covered by 'research' analyst type")
        else:
            print("⚠️ May need dedicated consensus/anti-consensus analyst types")
        
    except Exception as e:
        print(f"❌ Error testing consensus analysis: {e}")

def test_different_industries_same_analyst():
    """Test that same analyst type works across different industries"""
    
    print("\n=== CROSS-INDUSTRY ANALYST TEST ===")
    
    industries_test = [
        {'name': 'Industrial REIT', 'sector': 'Real Estate', 'industry': 'REIT - Industrial', 'key_metric': 'FFO'},
        {'name': 'Large Bank', 'sector': 'Financial Services', 'industry': 'Banks - Diversified', 'key_metric': 'NIM'},
        {'name': 'SaaS Company', 'sector': 'Technology', 'industry': 'Software - Application', 'key_metric': 'ARR'},
        {'name': 'Biotech', 'sector': 'Healthcare', 'industry': 'Biotechnology', 'key_metric': 'Clinical Trial'}
    ]
    
    analyst_type = 'fundamentals'  # Test one analyst across industries
    
    print(f"Testing '{analyst_type}' analyst across {len(industries_test)} different industries:")
    
    for industry_test in industries_test:
        test_data = {'info': {'sector': industry_test['sector'], 'industry': industry_test['industry']}}
        
        try:
            enhanced_prompt = get_comprehensive_industry_prompt(
                analyst_type=analyst_type,
                company=f"Test {industry_test['name']} Company",
                ticker='TEST',
                financial_data=test_data,
                user_query=f'{industry_test["name"]} analysis'
            )
            
            # Check for industry-specific metric
            has_metric = industry_test['key_metric'] in enhanced_prompt
            status = '✅ PASS' if has_metric else '❌ FAIL'
            
            print(f"  {industry_test['name']}: {status} ({'Found' if has_metric else 'Missing'} '{industry_test['key_metric']}')")
            
        except Exception as e:
            print(f"  {industry_test['name']}: ❌ ERROR - {e}")

if __name__ == "__main__":
    print("🧪 COMPREHENSIVE ANALYST TYPES INTEGRATION TEST")
    print("=" * 60)
    
    # Test all analyst types
    all_types_work = test_all_analyst_types()
    
    # Test consensus analysis
    test_consensus_anti_consensus_analysts()
    
    # Test cross-industry capability
    test_different_industries_same_analyst()
    
    print("\n" + "=" * 60)
    if all_types_work:
        print("🎉 ALL ANALYST TYPES WORK WITH INDUSTRY SYSTEM!")
        print("✅ Ready for production use across all 12 analyst types")
    else:
        print("⚠️  Some analyst types need investigation")