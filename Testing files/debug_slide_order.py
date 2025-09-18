#!/usr/bin/env python3
"""
Debug script to understand why slides are appearing in wrong order
"""

# Sample content based on your actual HTML output
actual_html = '''<div class="slide" id="portrait-page-1">SLIDE 1</div>
<div class="slide" id="portrait-page-1A">SLIDE 2</div>
<div class="slide report-prose" id="slide-industry-analysis-part1">SLIDE 6</div>
<div class="slide report-prose" id="slide-industry-analysis-part2">SLIDE 7</div>
<div class="slide report-prose" id="slide-industry-analysis-part3">SLIDE 8</div>
<div class="slide report-prose" id="slide-industry-analysis-part4">SLIDE 9</div>
<div class="slide report-prose" id="slide-industry-analysis-part5">SLIDE 10</div>
<div class="slide report-prose" id="slide-financial-highlights-part1">SLIDE 11</div>
<div class="slide report-prose" id="slide-financial-income-statement">SLIDE 12</div>
<div class="slide report-prose" id="slide-financial-balance-sheet">SLIDE 13</div>
<div class="slide report-prose" id="slide-financial-cash-flow-statement">SLIDE 14</div>
<div class="slide report-prose" id="dcf-analysis-page">SLIDE 15</div>
<div class="slide" id="bull-bear-analysis-comprehensive">SLIDE 16</div>
<div class="slide report-prose" id="investment-highlights-pitchbook-page">SLIDE 3</div>
<div class="slide report-prose" id="catalyst-page">SLIDE 4</div>
<div class="slide report-prose" id="company-analysis-page">SLIDE 5</div>'''

# Extract slide positions
import re

def analyze_slide_order(html_content):
    """Analyze the order of slides in HTML content"""
    print("🔍 SLIDE ORDER ANALYSIS")
    print("=" * 50)
    
    # Expected slide mappings
    slide_mappings = {
        'portrait-page-1': 'Slide 1 (Executive Summary)',
        'portrait-page-1A': 'Slide 2 (Investment Summary)', 
        'investment-highlights-pitchbook-page': 'Slide 3 (Investment Highlights)',
        'catalyst-page': 'Slide 4 (Catalysts)',
        'company-analysis-page': 'Slide 5 (Company Analysis)',
        'slide-industry-analysis-part1': 'Slide 6 (Industry Analysis 1)',
        'slide-industry-analysis-part2': 'Slide 7 (Industry Analysis 2)',
        'slide-industry-analysis-part3': 'Slide 8 (Industry Analysis 3)',
        'slide-industry-analysis-part4': 'Slide 9 (Industry Analysis 4)',
        'slide-industry-analysis-part5': 'Slide 10 (Industry Analysis 5)',
        'slide-financial-highlights-part1': 'Slide 11 (Financial Highlights)',
        'slide-financial-income-statement': 'Slide 12 (Income Statement)',
        'slide-financial-balance-sheet': 'Slide 13 (Balance Sheet)',
        'slide-financial-cash-flow-statement': 'Slide 14 (Cash Flow)',
        'dcf-analysis-page': 'Slide 15 (DCF Analysis)',
        'bull-bear-analysis-comprehensive': 'Slide 16 (Bull/Bear Analysis)'
    }
    
    # Find all slide IDs in order of appearance
    slide_pattern = r'id="([^"]+)"'
    slide_ids_in_order = []
    
    for match in re.finditer(slide_pattern, html_content):
        slide_id = match.group(1)
        if slide_id in slide_mappings:
            slide_ids_in_order.append(slide_id)
    
    print(f"📄 Found {len(slide_ids_in_order)} slides in document")
    print("\n📋 ACTUAL ORDER (as they appear in HTML):")
    
    for i, slide_id in enumerate(slide_ids_in_order, 1):
        slide_description = slide_mappings.get(slide_id, f"Unknown: {slide_id}")
        print(f"   Position {i:2d}: {slide_description}")
    
    print("\n🎯 EXPECTED ORDER:")
    expected_order = [
        'portrait-page-1', 'portrait-page-1A',
        'investment-highlights-pitchbook-page', 'catalyst-page', 'company-analysis-page',
        'slide-industry-analysis-part1', 'slide-industry-analysis-part2', 'slide-industry-analysis-part3',
        'slide-industry-analysis-part4', 'slide-industry-analysis-part5', 'slide-financial-highlights-part1',
        'slide-financial-income-statement', 'slide-financial-balance-sheet', 'slide-financial-cash-flow-statement',
        'dcf-analysis-page', 'bull-bear-analysis-comprehensive'
    ]
    
    for i, slide_id in enumerate(expected_order, 1):
        slide_description = slide_mappings.get(slide_id, f"Unknown: {slide_id}")
        print(f"   Position {i:2d}: {slide_description}")
    
    print("\n⚖️ COMPARISON:")
    issues_found = False
    for i, (actual_id, expected_id) in enumerate(zip(slide_ids_in_order, expected_order), 1):
        if actual_id != expected_id:
            issues_found = True
            actual_desc = slide_mappings.get(actual_id, actual_id)
            expected_desc = slide_mappings.get(expected_id, expected_id)
            print(f"   ❌ Position {i:2d}: Found '{actual_desc}' but expected '{expected_desc}'")
        else:
            actual_desc = slide_mappings.get(actual_id, actual_id)
            print(f"   ✅ Position {i:2d}: Correct - '{actual_desc}'")
    
    if not issues_found:
        print("   🎉 All slides are in correct order!")
    else:
        print("\n🚨 SLIDE ORDER ISSUES DETECTED!")
        
        # Identify which slides are out of place
        print("\n🔀 MISPLACED SLIDES:")
        
        # Group by call
        call1_slides = ['portrait-page-1', 'portrait-page-1A']
        call2_slides = ['investment-highlights-pitchbook-page', 'catalyst-page', 'company-analysis-page']  
        call3_slides = [s for s in expected_order if s not in call1_slides + call2_slides]
        
        print(f"   📞 Call 1 slides (1-2): {[slide_mappings[s] for s in call1_slides if s in slide_ids_in_order]}")
        print(f"   📞 Call 2 slides (3-5): {[slide_mappings[s] for s in call2_slides if s in slide_ids_in_order]}")
        print(f"   📞 Call 3 slides (6-16): {[slide_mappings[s] for s in call3_slides if s in slide_ids_in_order]}")
        
        # Check where each call's slides appear
        call1_positions = [i+1 for i, s in enumerate(slide_ids_in_order) if s in call1_slides]
        call2_positions = [i+1 for i, s in enumerate(slide_ids_in_order) if s in call2_slides]
        call3_positions = [i+1 for i, s in enumerate(slide_ids_in_order) if s in call3_slides]
        
        print(f"\n📍 POSITIONS IN ACTUAL HTML:")
        print(f"   Call 1 slides appear at positions: {call1_positions}")
        print(f"   Call 2 slides appear at positions: {call2_positions}") 
        print(f"   Call 3 slides appear at positions: {call3_positions}")
        
        if call2_positions and call3_positions and min(call3_positions) < max(call2_positions):
            print(f"\n🎯 ROOT CAUSE IDENTIFIED:")
            print(f"   Call 3 slides (positions {min(call3_positions)}-{max(call3_positions)}) appear BEFORE Call 2 slides (positions {min(call2_positions)}-{max(call2_positions)})")
            print(f"   This indicates the slide insertion logic is inserting Call 3 before Call 2!")

if __name__ == "__main__":
    analyze_slide_order(actual_html)