#!/usr/bin/env python3
"""
Debug the FIRST insertion step where Call 2 is inserted into Call 1
This is where the real problem lies!
"""

import sys
import os
from pathlib import Path

# Add src to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from robeco.backend.template_report_generator import RobecoTemplateReportGenerator

def test_first_insertion_step():
    """Test the first step where Call 2 is inserted into Call 1"""
    print("🔧 Testing First Insertion Step: Call1 + Call2")
    print("=" * 60)
    
    # Create generator instance
    generator = RobecoTemplateReportGenerator()
    
    # Simulate clean_call1 content - slides 1-2
    clean_call1 = '''<div class="slide" id="portrait-page-1">
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
</div>'''
    
    # Simulate clean_call2 content - slides 3-5 (IN MARKDOWN FORMAT like in real system!)
    clean_call2 = '''```html
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
</div>
```'''
    
    print("🔧 Step 1 Input Analysis:")
    print(f"   📄 clean_call1 slides: {clean_call1.count('<div class=\"slide\"')}")
    print(f"   📄 clean_call2 slides: {clean_call2.count('<div class=\"slide\"')}")
    
    # Check what slides are in each call
    print(f"   ✅ clean_call1 contains:")
    print(f"      Slide 1: {clean_call1.count('id=\"portrait-page-1\"')} occurrences")
    print(f"      Slide 2: {clean_call1.count('id=\"portrait-page-1A\"')} occurrences")
    
    print(f"   ✅ clean_call2 contains:")
    print(f"      Slide 3: {clean_call2.count('id=\"investment-highlights-pitchbook-page\"')} occurrences")
    print(f"      Slide 4: {clean_call2.count('id=\"catalyst-page\"')} occurrences") 
    print(f"      Slide 5: {clean_call2.count('id=\"company-analysis-page\"')} occurrences")
    
    print(f"\n🔧 Calling _insert_slides_into_html(clean_call1, clean_call2)")
    
    # ADD DEBUGGING: Check slide detection logic manually for call1
    print(f"\n🔍 DEBUGGING SLIDE DETECTION IN CALL1:")
    slide_positions = []
    search_pos = 0
    while True:
        slide_start = clean_call1.find('<div class="slide"', search_pos)
        if slide_start == -1:
            break
        # Find slide ID for this position
        id_start = clean_call1.find('id="', slide_start)
        if id_start != -1:
            id_end = clean_call1.find('"', id_start + 4)
            slide_id = clean_call1[id_start + 4:id_end] if id_end != -1 else "unknown"
        else:
            slide_id = "no-id"
        
        slide_positions.append((slide_start, slide_id))
        search_pos = slide_start + 1
    
    print(f"   📄 Found {len(slide_positions)} slide positions in clean_call1:")
    for i, (pos, slide_id) in enumerate(slide_positions):
        print(f"      Position {i+1}: {slide_id} at char {pos}")
    
    if slide_positions:
        last_slide_start, last_slide_id = slide_positions[-1]
        print(f"   🎯 Last slide detected: {last_slide_id} at position {last_slide_start}")
        print(f"   ✅ This should be 'portrait-page-1A' (slide 2)")
    
    # Perform the first insertion
    accumulated_call2 = generator._insert_slides_into_html(clean_call1, clean_call2)
    
    print(f"\n🔧 Step 1 Result Analysis:")
    print(f"   📏 Final result length: {len(accumulated_call2):,} chars")
    print(f"   📄 Final slide count: {accumulated_call2.count('<div class=\"slide\"')}")
    print(f"   ✅ Should be 5 slides total (2 from call1 + 3 from call2)")
    
    # Check if all expected slides are present
    result_slide1 = accumulated_call2.count('id="portrait-page-1"')
    result_slide2 = accumulated_call2.count('id="portrait-page-1A"')
    result_slide3 = accumulated_call2.count('id="investment-highlights-pitchbook-page"')
    result_slide4 = accumulated_call2.count('id="catalyst-page"')
    result_slide5 = accumulated_call2.count('id="company-analysis-page"')
    
    print(f"\n📋 ACCUMULATED RESULT CONTAINS:")
    print(f"   Slide 1: {result_slide1} occurrences")
    print(f"   Slide 2: {result_slide2} occurrences")
    print(f"   Slide 3: {result_slide3} occurrences")
    print(f"   Slide 4: {result_slide4} occurrences")
    print(f"   Slide 5: {result_slide5} occurrences")
    
    # Check final slide order
    import re
    slide_ids = []
    for match in re.finditer(r'id="([^"]+)"', accumulated_call2):
        slide_id = match.group(1)
        if 'slide' in slide_id.lower() or 'page' in slide_id.lower() or 'analysis' in slide_id.lower():
            slide_ids.append(slide_id)
    
    print(f"\n📋 ACCUMULATED SLIDE ORDER:")
    slide_mappings = {
        'portrait-page-1': 'Slide 1',
        'portrait-page-1A': 'Slide 2', 
        'investment-highlights-pitchbook-page': 'Slide 3',
        'catalyst-page': 'Slide 4',
        'company-analysis-page': 'Slide 5'
    }
    
    for i, slide_id in enumerate(slide_ids, 1):
        slide_desc = slide_mappings.get(slide_id, f"Unknown: {slide_id}")
        print(f"   Position {i:2d}: {slide_desc} ({slide_id})")
    
    # Check if the order is correct
    expected_order = ['portrait-page-1', 'portrait-page-1A', 'investment-highlights-pitchbook-page', 
                     'catalyst-page', 'company-analysis-page']
    
    order_correct = slide_ids == expected_order
    
    print(f"\n🎯 FIRST INSERTION RESULT:")
    if order_correct:
        print("   ✅ SUCCESS: Call1 + Call2 insertion is working correctly!")
        print("   ✅ All 5 slides are present in correct order")
    else:
        print("   ❌ FAILURE: Call1 + Call2 insertion is BROKEN!")
        print(f"   🔍 Expected: {[slide_mappings.get(s, s) for s in expected_order]}")
        print(f"   🔍 Actual:   {[slide_mappings.get(s, s) for s in slide_ids]}")
        
        # Find where the problem occurs
        for i, (actual, expected) in enumerate(zip(slide_ids, expected_order)):
            if actual != expected:
                print(f"   ❌ First mismatch at position {i+1}: got '{slide_mappings.get(actual, actual)}' expected '{slide_mappings.get(expected, expected)}'")
                break
    
    # Save result for inspection
    output_file = project_root / "debug_insertion_step1_result.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(accumulated_call2)
    print(f"\n💾 Result saved to: {output_file}")
    
    return order_correct, accumulated_call2

if __name__ == "__main__":
    success, result = test_first_insertion_step()
    exit_code = 0 if success else 1
    print(f"\n🏁 Debug completed with exit code: {exit_code}")
    sys.exit(exit_code)