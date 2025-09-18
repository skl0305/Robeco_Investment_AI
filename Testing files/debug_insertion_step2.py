#!/usr/bin/env python3
"""
Debug the specific second insertion step where Call 3 is inserted into accumulated Call 2
"""

import sys
import os
from pathlib import Path

# Add src to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from robeco.backend.template_report_generator import RobecoTemplateReportGenerator

def test_second_insertion_step():
    """Test the specific step where Call 3 is inserted into (Call 1 + Call 2)"""
    print("🔧 Testing Second Insertion Step: (Call1+Call2) + Call3")
    print("=" * 70)
    
    # Create generator instance
    generator = RobecoTemplateReportGenerator()
    
    # Simulate accumulated_call2 (Call 1 + Call 2 result) - slides 1-2-3-4-5
    accumulated_call2 = '''<div class="slide" id="portrait-page-1">
    <div class="slide-content">
        <h2>Executive Summary - Slide 1</h2>
        <p>This is slide 1 content.</p>
    </div>
</div>

<div class="slide" id="portrait-page-1A">
    <div class="slide-content">
        <h2>Investment Summary - Slide 2</h2>
        <p>This is slide 2 content.</p>
    </div>
</div>

<div class="slide report-prose" id="investment-highlights-pitchbook-page">
    <div class="slide-content">
        <h2>Investment Highlights - Slide 3</h2>
        <p>This is slide 3 content.</p>
    </div>
</div>

<div class="slide report-prose" id="catalyst-page">
    <div class="slide-content">
        <h2>Catalysts - Slide 4</h2>
        <p>This is slide 4 content.</p>
    </div>
</div>

<div class="slide report-prose" id="company-analysis-page">
    <div class="slide-content">
        <h2>Company Analysis - Slide 5</h2>
        <p>This is slide 5 content.</p>
    </div>
</div>'''
    
    # Simulate clean_call3 content - slides 6-16
    clean_call3 = '''<div class="slide report-prose" id="slide-industry-analysis-part1">
    <div class="slide-content">
        <h2>Industry Analysis 1 - Slide 6</h2>
        <p>This is slide 6 content.</p>
    </div>
</div>

<div class="slide report-prose" id="slide-industry-analysis-part2">
    <div class="slide-content">
        <h2>Industry Analysis 2 - Slide 7</h2>
        <p>This is slide 7 content.</p>
    </div>
</div>

<div class="slide report-prose" id="dcf-analysis-page">
    <div class="slide-content">
        <h2>DCF Analysis - Slide 15</h2>
        <p>This is slide 15 content.</p>
    </div>
</div>

<div class="slide" id="bull-bear-analysis-comprehensive">
    <div class="slide-content">
        <h2>Bull/Bear Analysis - Slide 16</h2>
        <p>This is slide 16 content.</p>
    </div>
</div>'''
    
    print("🔧 Step 2 Input Analysis:")
    print(f"   📄 accumulated_call2 slides: {accumulated_call2.count('<div class=\"slide\"')}")
    print(f"   📄 clean_call3 slides: {clean_call3.count('<div class=\"slide\"')}")
    
    # Check what slides are in accumulated_call2
    slide1_count = accumulated_call2.count('id="portrait-page-1"')
    slide2_count = accumulated_call2.count('id="portrait-page-1A"')
    slide3_count = accumulated_call2.count('id="investment-highlights-pitchbook-page"')
    slide4_count = accumulated_call2.count('id="catalyst-page"')
    slide5_count = accumulated_call2.count('id="company-analysis-page"')
    
    print(f"   ✅ accumulated_call2 contains:")
    print(f"      Slide 1: {slide1_count} occurrences")
    print(f"      Slide 2: {slide2_count} occurrences") 
    print(f"      Slide 3: {slide3_count} occurrences")
    print(f"      Slide 4: {slide4_count} occurrences")
    print(f"      Slide 5: {slide5_count} occurrences")
    
    # Check what slides are in clean_call3
    slide6_count = clean_call3.count('id="slide-industry-analysis-part1"')
    slide15_count = clean_call3.count('id="dcf-analysis-page"')
    slide16_count = clean_call3.count('id="bull-bear-analysis-comprehensive"')
    
    print(f"   ✅ clean_call3 contains:")
    print(f"      Slide 6: {slide6_count} occurrences")
    print(f"      Slide 15: {slide15_count} occurrences")
    print(f"      Slide 16: {slide16_count} occurrences")
    
    print(f"\n🔧 Calling _insert_slides_into_html(accumulated_call2, clean_call3)")
    
    # ADD DEBUGGING: Check slide detection logic manually
    print(f"\n🔍 DEBUGGING SLIDE DETECTION:")
    slide_positions = []
    search_pos = 0
    while True:
        slide_start = accumulated_call2.find('<div class="slide"', search_pos)
        if slide_start == -1:
            break
        # Find slide ID for this position
        id_start = accumulated_call2.find('id="', slide_start)
        if id_start != -1:
            id_end = accumulated_call2.find('"', id_start + 4)
            slide_id = accumulated_call2[id_start + 4:id_end] if id_end != -1 else "unknown"
        else:
            slide_id = "no-id"
        
        slide_positions.append((slide_start, slide_id))
        search_pos = slide_start + 1
    
    print(f"   📄 Found {len(slide_positions)} slide positions in accumulated_call2:")
    for i, (pos, slide_id) in enumerate(slide_positions):
        print(f"      Position {i+1}: {slide_id} at char {pos}")
    
    if slide_positions:
        last_slide_start, last_slide_id = slide_positions[-1]
        print(f"   🎯 Last slide detected: {last_slide_id} at position {last_slide_start}")
        print(f"   ❗ This should be 'company-analysis-page' (slide 5), not slide 2!")
    
    # Perform the problematic insertion
    result = generator._insert_slides_into_html(accumulated_call2, clean_call3)
    
    print(f"\n🔧 Step 2 Result Analysis:")
    print(f"   📏 Final result length: {len(result):,} chars")
    print(f"   📄 Final slide count: {result.count('<div class=\"slide\"')}")
    
    # Check final slide order
    import re
    slide_ids = []
    for match in re.finditer(r'id="([^"]+)"', result):
        slide_id = match.group(1)
        if 'slide' in slide_id.lower() or 'page' in slide_id.lower() or 'analysis' in slide_id.lower():
            slide_ids.append(slide_id)
    
    print(f"\n📋 FINAL SLIDE ORDER:")
    slide_mappings = {
        'portrait-page-1': 'Slide 1',
        'portrait-page-1A': 'Slide 2', 
        'investment-highlights-pitchbook-page': 'Slide 3',
        'catalyst-page': 'Slide 4',
        'company-analysis-page': 'Slide 5',
        'slide-industry-analysis-part1': 'Slide 6',
        'slide-industry-analysis-part2': 'Slide 7',
        'dcf-analysis-page': 'Slide 15',
        'bull-bear-analysis-comprehensive': 'Slide 16'
    }
    
    for i, slide_id in enumerate(slide_ids, 1):
        slide_desc = slide_mappings.get(slide_id, f"Unknown: {slide_id}")
        print(f"   Position {i:2d}: {slide_desc} ({slide_id})")
    
    # Check if the order is correct
    expected_order = ['portrait-page-1', 'portrait-page-1A', 'investment-highlights-pitchbook-page', 
                     'catalyst-page', 'company-analysis-page', 'slide-industry-analysis-part1', 
                     'slide-industry-analysis-part2', 'dcf-analysis-page', 'bull-bear-analysis-comprehensive']
    
    order_correct = slide_ids == expected_order[:len(slide_ids)]
    
    print(f"\n🎯 RESULT:")
    if order_correct:
        print("   ✅ SUCCESS: Slides are in correct order after second insertion!")
    else:
        print("   ❌ FAILURE: Slides are STILL in wrong order after second insertion!")
        print(f"   🔍 Expected: {[slide_mappings.get(s, s) for s in expected_order[:len(slide_ids)]]}")
        print(f"   🔍 Actual:   {[slide_mappings.get(s, s) for s in slide_ids]}")
        
        # Find where the problem occurs
        for i, (actual, expected) in enumerate(zip(slide_ids, expected_order)):
            if actual != expected:
                print(f"   ❌ First mismatch at position {i+1}: got '{slide_mappings.get(actual, actual)}' expected '{slide_mappings.get(expected, expected)}'")
                break
    
    # Save result for inspection
    output_file = project_root / "debug_insertion_step2_result.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(result)
    print(f"\n💾 Result saved to: {output_file}")
    
    return order_correct

if __name__ == "__main__":
    success = test_second_insertion_step()
    exit_code = 0 if success else 1
    print(f"\n🏁 Debug completed with exit code: {exit_code}")
    sys.exit(exit_code)