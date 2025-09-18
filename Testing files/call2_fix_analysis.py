#!/usr/bin/env python3
"""
Call 2 Premature Termination - Root Cause Analysis & Fix

From conversation summary:
- Call 1: 69,625 chars, 5 complete slides ✅
- Call 2: 2,337 chars, incomplete slide 6, cuts off mid-sentence ❌
- Content ends with: "...while some markets like India, Australia, and Japan are expected to accelerate, Greater9% expansion for 2024..."

LIKELY ROOT CAUSES:
1. Content Safety Filtering - AI response blocked by safety filters
2. Prompt Structure Issues - Malformed prompt causing early termination  
3. Token Limits - Generation hitting model token limits
4. API Connection Issues - Streaming connection drops

SOLUTION STRATEGY:
1. Add safety filter detection in streaming error handling ✅ (implemented)
2. Reduce prompt complexity for Call 2 to avoid triggering filters
3. Add explicit completion requirements to prevent early termination
4. Implement retry logic with different prompts if safety filtering occurs
"""

# Key fixes needed in template_report_generator.py:

FIX_1_SAFETY_DETECTION = """
# Enhanced error handling with safety filter detection (already implemented):
except Exception as stream_error:
    error_str = str(stream_error).lower()
    if any(indicator in error_str for indicator in ['safety', 'blocked', 'filtered', 'inappropriate', 'policy']):
        logger.error(f"🚫 CONTENT FILTERING DETECTED: AI response was blocked by safety filters")
        # Try with simplified prompt or different approach
"""

FIX_2_PROMPT_STRUCTURE = """
# Simplified Call 2 prompt structure to avoid safety triggers:
- Remove investment banking jargon that might trigger filters
- Use more neutral financial language
- Avoid aggressive language like "beat", "crush", "destroy"
- Focus on factual analysis rather than persuasive language
"""

FIX_3_COMPLETION_ENFORCEMENT = """
# Add explicit completion requirements:
system_instruction += '''
CRITICAL COMPLETION REQUIREMENT: You MUST generate complete content for ALL 10 slides (6-15).
Never stop generation prematurely. Always complete the full analysis through slide 15.
If you encounter any issues, continue generating until slide 15 is complete.
'''
"""

FIX_4_RETRY_LOGIC = """
# Implement retry with different prompts if Call 2 fails:
if len(call2_content) < 5000 or not call2_complete:
    logger.warning("Call 2 incomplete, retrying with simplified prompt...")
    # Retry with safer, more neutral prompt
"""

print("🔍 Call 2 Analysis Complete")
print("📋 Key Issue: Content safety filtering likely causing premature termination")
print("🛠️ Solution: Implement safety detection + prompt simplification + retry logic")
print("✅ Enhanced debugging already added to detect exact failure point")