#!/usr/bin/env python3

# Script to fix the template generator structure

import re

def fix_template_generator():
    """Fix the template generator to match RB.html structure exactly"""
    
    file_path = "/Users/skl/Desktop/Robeco Reporting/src/robeco/backend/template_report_generator.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Read the corrected slides content
    with open("/Users/skl/Desktop/Robeco Reporting/corrected_slides_template.txt", 'r', encoding='utf-8') as f:
        new_slides = f.read()
    
    # Find the pattern to replace - everything from SLIDE 3 to the end of SLIDE 18
    pattern = r'(<!-- SLIDE 3: Investment Highlights.*?)</div>\n"""'
    
    # Replace with new structure
    replacement = new_slides + '\n"""'
    
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # Also update other references
    new_content = new_content.replace('Page 3 / 18', 'Page 3 / 9')
    new_content = new_content.replace('18-slide structure', '9-slide structure')
    new_content = new_content.replace('Complete 18-slide', 'Complete 9-slide')
    new_content = new_content.replace('ALL 18 slides', 'EXACTLY 9 SLIDES')
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ Template generator fixed to match RB.html structure!")
    print("📊 Changed from 18 slides to 9 slides with correct embedded subsections")

if __name__ == "__main__":
    fix_template_generator()