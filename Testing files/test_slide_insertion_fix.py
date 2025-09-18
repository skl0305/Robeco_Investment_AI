#!/usr/bin/env python3
"""
Test script for the fixed _insert_slides_into_html method
Validates that slides are inserted in proper sequential order (1→2→3→4→5→6→7→8→9→10→11→12→13)
"""

import sys
import os
from pathlib import Path

# Add src to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from robeco.backend.template_report_generator import RobecoTemplateReportGenerator

def test_slide_insertion_logic():
    """Test the fixed slide insertion method with sample data"""
    print("🔧 Testing Fixed Slide Insertion Logic")
    print("=" * 60)
    
    # Create generator instance (constructor takes no parameters)
    generator = RobecoTemplateReportGenerator()
    
    # Test 1: Simulate Call 1 content (slides 1-2)
    call1_content = '''<div class="slide" id="portrait-page-1">
    <div class="slide-content">
        <h2>Executive Summary - Slide 1</h2>
        <p>This is slide 1 content with metrics grid and stock chart.</p>
    </div>
</div>

<div class="slide" id="portrait-page-1A">
    <div class="slide-content">
        <h2>Investment Summary Continued - Slide 2</h2>
        <p>This is slide 2 content with continued analysis.</p>
    </div>
</div>'''
    
    # Test 2: Simulate Call 2 content (slides 3-5) 
    call2_content = '''<div class="slide" id="investment-highlights-pitchbook-page">
    <div class="slide-content">
        <h2>Investment Highlights - Slide 3</h2>
        <p>This is slide 3 content.</p>
    </div>
</div>

<div class="slide" id="equity-story-catalysts-page">
    <div class="slide-content">
        <h2>Equity Story & Catalysts - Slide 4</h2>
        <p>This is slide 4 content.</p>
    </div>
</div>

<div class="slide" id="company-analysis-positioning-page">
    <div class="slide-content">
        <h2>Company Analysis - Slide 5</h2>
        <p>This is slide 5 content.</p>
    </div>
</div>'''
    
    # Test 3: Simulate Call 3 content (slides 6-13)
    call3_content = '''<div class="slide" id="slide-industry-analysis">
    <div class="slide-content">
        <h2>Industry Analysis - Slide 6</h2>
        <p>This is slide 6 content.</p>
    </div>
</div>

<div class="slide" id="slide-global-market-dynamics-part2">
    <div class="slide-content">
        <h2>Global Market Dynamics - Slide 7</h2>
        <p>This is slide 7 content.</p>
    </div>
</div>

<div class="slide" id="slide-financial-highlights-part1">
    <div class="slide-content">
        <h2>Financial Highlights - Slide 8</h2>
        <p>This is slide 8 content.</p>
    </div>
</div>

<div class="slide" id="dcf-analysis-page">
    <div class="slide-content">
        <h2>DCF Analysis - Slide 13</h2>
        <p>This is slide 13 content (final slide).</p>
    </div>
</div>'''
    
    print("🔧 Step 1: Testing Call 1 → Call 2 insertion")
    print("   📄 Call 1: 2 slides (1-2)")
    print("   📄 Call 2: 3 slides (3-5)")
    
    # Test Call 1 + Call 2 insertion
    accumulated_call2 = generator._insert_slides_into_html(call1_content, call2_content)
    
    # Validate Call 1 + Call 2 result
    slide1_count = accumulated_call2.count('id="portrait-page-1"')
    slide2_count = accumulated_call2.count('id="portrait-page-1A"') 
    slide3_count = accumulated_call2.count('id="investment-highlights-pitchbook-page"')
    slide4_count = accumulated_call2.count('id="equity-story-catalysts-page"')
    slide5_count = accumulated_call2.count('id="company-analysis-positioning-page"')
    
    print(f"   ✅ Slide 1: {slide1_count} occurrences")
    print(f"   ✅ Slide 2: {slide2_count} occurrences")
    print(f"   ✅ Slide 3: {slide3_count} occurrences")
    print(f"   ✅ Slide 4: {slide4_count} occurrences")
    print(f"   ✅ Slide 5: {slide5_count} occurrences")
    print(f"   📏 Combined length: {len(accumulated_call2):,} chars")
    print(f"   📄 Total slides: {accumulated_call2.count('<div class=\"slide\"')} divs")
    
    print("\n🔧 Step 2: Testing Accumulated → Call 3 insertion")
    print("   📄 Accumulated: 5 slides (1-5)")
    print("   📄 Call 3: 4 slides (6, 7, 8, 13)")
    
    # Test Accumulated + Call 3 insertion  
    final_result = generator._insert_slides_into_html(accumulated_call2, call3_content)
    
    # Validate final result
    final_slide1 = final_result.count('id="portrait-page-1"')
    final_slide2 = final_result.count('id="portrait-page-1A"')
    final_slide3 = final_result.count('id="investment-highlights-pitchbook-page"')
    final_slide4 = final_result.count('id="equity-story-catalysts-page"')
    final_slide5 = final_result.count('id="company-analysis-positioning-page"')
    final_slide6 = final_result.count('id="slide-industry-analysis"')
    final_slide7 = final_result.count('id="slide-global-market-dynamics-part2"')
    final_slide8 = final_result.count('id="slide-financial-highlights-part1"')
    final_slide13 = final_result.count('id="dcf-analysis-page"')
    
    print(f"   ✅ Final Slide 1: {final_slide1} occurrences")
    print(f"   ✅ Final Slide 2: {final_slide2} occurrences") 
    print(f"   ✅ Final Slide 3: {final_slide3} occurrences")
    print(f"   ✅ Final Slide 4: {final_slide4} occurrences")
    print(f"   ✅ Final Slide 5: {final_slide5} occurrences")
    print(f"   ✅ Final Slide 6: {final_slide6} occurrences")
    print(f"   ✅ Final Slide 7: {final_slide7} occurrences")
    print(f"   ✅ Final Slide 8: {final_slide8} occurrences")
    print(f"   ✅ Final Slide 13: {final_slide13} occurrences")
    print(f"   📏 Final length: {len(final_result):,} chars")
    print(f"   📄 Total slides: {final_result.count('<div class=\"slide\"')} divs")
    
    print("\n🔍 Step 3: Testing Slide Order Validation")
    
    # Check slide order by finding positions of each slide ID
    slide_positions = []
    slide_ids = [
        'id="portrait-page-1"',
        'id="portrait-page-1A"', 
        'id="investment-highlights-pitchbook-page"',
        'id="equity-story-catalysts-page"',
        'id="company-analysis-positioning-page"',
        'id="slide-industry-analysis"',
        'id="slide-global-market-dynamics-part2"',
        'id="slide-financial-highlights-part1"',
        'id="dcf-analysis-page"'
    ]
    
    for i, slide_id in enumerate(slide_ids, 1):
        pos = final_result.find(slide_id)
        if pos != -1:
            slide_positions.append((i, slide_id.replace('id="', '').replace('"', ''), pos))
        else:
            slide_positions.append((i, slide_id.replace('id="', '').replace('"', ''), -1))
    
    # Sort by position to check order
    found_slides = [(num, name, pos) for num, name, pos in slide_positions if pos != -1]
    found_slides.sort(key=lambda x: x[2])  # Sort by position
    
    print("   📋 Slide Order in Final HTML (by position):")
    order_correct = True
    for i, (slide_num, slide_name, pos) in enumerate(found_slides):
        expected_order = i + 1
        actual_order = slide_num
        status = "✅" if expected_order == actual_order else "❌"
        if expected_order != actual_order:
            order_correct = False
        print(f"      {status} Position {i+1}: Slide {slide_num} ({slide_name[:30]}...)")
    
    print(f"\n🎯 FINAL RESULT:")
    if order_correct:
        print("   ✅ SUCCESS: All slides appear in correct sequential order!")
        print("   ✅ Fixed slide insertion logic is working properly")
        print("   ✅ The slide ordering issue has been resolved")
    else:
        print("   ❌ FAILURE: Slides are still not in correct order")
        print("   ❌ Additional debugging may be needed")
    
    # Save test output for inspection
    output_file = project_root / "test_slide_insertion_output.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(final_result)
    print(f"\n💾 Test output saved to: {output_file}")
    
    return order_correct

if __name__ == "__main__":
    success = test_slide_insertion_logic()
    exit_code = 0 if success else 1
    print(f"\n🏁 Test completed with exit code: {exit_code}")
    sys.exit(exit_code)