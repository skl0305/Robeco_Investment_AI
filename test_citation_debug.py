#!/usr/bin/env python3
"""
Citation Debug Test - Isolate the exact point where citations are lost
"""

import json
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_backend_citation_generation():
    """Test if backend generates citations correctly"""
    logger.info("🧪 TEST 1: Backend Citation Generation")
    
    # Simulate the backend citation generation process
    mock_content = """# Investment Analysis Report

    Based on our comprehensive analysis, the company shows strong fundamentals with revenue growth of 15% year-over-year. The management team has demonstrated excellent capital allocation capabilities through strategic acquisitions and organic expansion initiatives.

    ## Financial Performance
    
    The company's EBITDA margins have expanded by 200 basis points to 18.5% in the latest quarter, significantly outpacing industry averages. This improvement reflects operational efficiency gains from recent automation investments and favorable product mix shifts.
    
    ## Valuation Assessment
    
    Current valuation multiples appear attractive relative to peer group, with the stock trading at 12.5x forward earnings compared to sector median of 15.2x. The discount appears unjustified given superior growth profile and margin expansion trajectory."""
    
    # Simulate backend citation placement
    enhanced_content = mock_content + " [1]" + " Based on latest quarterly earnings report [2]" + " and management guidance [3]"
    
    # Add sources section
    enhanced_content += "\n\n## 📚 Research Sources\n\n"
    enhanced_content += "**[1]** Company Quarterly Report<br/>\n"
    enhanced_content += "<a href='https://example.com/q1-report' target='_blank' style='color: #007b7b; text-decoration: underline;'>🔗 View Source</a>\n\n"
    enhanced_content += "**[2]** Bloomberg Financial Data<br/>\n"
    enhanced_content += "<a href='https://bloomberg.com/company-data' target='_blank' style='color: #007b7b; text-decoration: underline;'>🔗 View Source</a>\n\n"
    
    citations_count = enhanced_content.count('[1]') + enhanced_content.count('[2]') + enhanced_content.count('[3]')
    
    logger.info(f"✅ Backend generated content with {citations_count} citations")
    logger.info(f"📄 Content length: {len(enhanced_content)} chars")
    logger.info(f"🔍 Sample citations: {enhanced_content.count('[1]')} [1], {enhanced_content.count('[2]')} [2], {enhanced_content.count('[3]')} [3]")
    
    return enhanced_content, citations_count

def test_websocket_message_creation():
    """Test WebSocket message creation"""
    logger.info("\n🧪 TEST 2: WebSocket Message Creation")
    
    enhanced_content, citations_count = test_backend_citation_generation()
    
    # Simulate WebSocket server message creation (from professional_streaming_server.py lines 474-497)
    message = {
        "type": "streaming_ai_content_final",
        "data": {
            "content_complete": enhanced_content,
            "citations_count": citations_count,
            "replace_content": True
        }
    }
    
    # Test JSON serialization
    try:
        json_string = json.dumps(message)
        message_size = len(json_string)
        logger.info(f"✅ WebSocket message created successfully")
        logger.info(f"📏 Message size: {message_size} bytes")
        logger.info(f"📚 Citations in message: {message['data']['citations_count']}")
        
        # Verify content integrity
        content_in_message = message['data']['content_complete']
        citations_in_content = content_in_message.count('[1]') + content_in_message.count('[2]') + content_in_message.count('[3]')
        logger.info(f"🔍 Citations preserved in JSON: {citations_in_content}")
        
        return message, json_string
        
    except Exception as e:
        logger.error(f"❌ JSON serialization failed: {e}")
        return None, None

def test_frontend_message_handling():
    """Test frontend message handling simulation"""
    logger.info("\n🧪 TEST 3: Frontend Message Handling Simulation")
    
    message, json_string = test_websocket_message_creation()
    if not message:
        return False
    
    # Simulate frontend receiving and parsing message
    try:
        # Parse JSON (simulating WebSocket receive)
        parsed_message = json.loads(json_string)
        logger.info(f"✅ Frontend parsed WebSocket message successfully")
        
        # Simulate handleFinalContentWithCitations function
        data = parsed_message['data']
        content_complete = data.get('content_complete', '')
        citations_count = data.get('citations_count', 0)
        
        logger.info(f"📄 Content received by frontend: {len(content_complete)} chars")
        logger.info(f"📚 Citations count in data: {citations_count}")
        
        # Test citation pattern matching (from formatMarkdownContent)
        citation_patterns = [
            r'\[(\d+)\]',           # Standard [1] format
            r'\[\s*(\d+)\s*\]',     # With spaces [ 1 ] format  
            r'\(\s*(\d+)\s*\)'      # Parentheses (1) format
        ]
        
        import re
        total_citations_found = 0
        for pattern in citation_patterns:
            matches = re.findall(pattern, content_complete)
            total_citations_found += len(matches)
            logger.info(f"🔍 Pattern '{pattern}' found {len(matches)} matches: {matches}")
        
        logger.info(f"📊 Total citations found by frontend: {total_citations_found}")
        
        # Simulate HTML formatting
        processed_content = content_complete
        processed_content = re.sub(r'\[(\d+)\]', 
            r'<sup class="citation-marker" onclick="scrollToSource(\1)" style="background: var(--robeco-blue); color: white; padding: 2px 6px; border-radius: 4px; font-size: 11px; cursor: pointer; margin-left: 2px;">[\1]</sup>', 
            processed_content)
        
        html_citations = len(re.findall(r'<sup class="citation-marker"', processed_content))
        logger.info(f"✨ HTML citations created: {html_citations}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Frontend processing failed: {e}")
        return False

def test_large_content_handling():
    """Test handling of large content that might cause issues"""
    logger.info("\n🧪 TEST 4: Large Content Handling")
    
    # Create large content similar to what the backend generates
    large_content = """# Comprehensive Investment Analysis Report

## Executive Summary

""" + ("This is a detailed analysis paragraph with substantial content. " * 100) + """ [1]

## Industry Analysis

""" + ("Comprehensive industry research and competitive positioning analysis. " * 150) + """ [2]

## Financial Analysis

""" + ("Detailed financial metrics, ratios, and performance analysis. " * 200) + """ [3]

## Technical Analysis

""" + ("Chart patterns, momentum indicators, and technical signals. " * 100) + """ [4]

## Risk Assessment

""" + ("Comprehensive risk evaluation and scenario analysis. " * 150) + """ [5]

## ESG Analysis

""" + ("Environmental, social, and governance factor assessment. " * 100) + """ [6]

## Valuation

""" + ("DCF modeling, comparable company analysis, and price targets. " * 200) + """ [7]

## Research Sources

**[1]** Company 10-K Filing<br/>
<a href='https://sec.gov/filing1' target='_blank'>🔗 View Source</a>

**[2]** Industry Research Report<br/>  
<a href='https://research.com/report' target='_blank'>🔗 View Source</a>

**[3]** Financial Database<br/>
<a href='https://bloomberg.com/data' target='_blank'>🔗 View Source</a>

**[4]** Technical Analysis Platform<br/>
<a href='https://tradingview.com/chart' target='_blank'>🔗 View Source</a>

**[5]** Risk Management Report<br/>
<a href='https://risk.com/analysis' target='_blank'>🔗 View Source</a>

**[6]** ESG Rating Agency<br/>
<a href='https://msci.com/esg' target='_blank'>🔗 View Source</a>

**[7]** Valuation Model<br/>
<a href='https://valuation.com/model' target='_blank'>🔗 View Source</a>
"""
    
    content_size = len(large_content)
    citations_count = 7
    
    logger.info(f"📏 Large content size: {content_size} chars")
    logger.info(f"📚 Citations in large content: {citations_count}")
    
    # Test WebSocket message size limits
    message = {
        "type": "streaming_ai_content_final",
        "data": {
            "content_complete": large_content,
            "citations_count": citations_count,
            "replace_content": True
        }
    }
    
    try:
        json_string = json.dumps(message)
        message_size = len(json_string)
        logger.info(f"📏 Large message size: {message_size} bytes")
        
        # Check if message exceeds typical WebSocket limits
        if message_size > 500000:  # 500KB limit from server
            logger.warning(f"⚠️ Message exceeds 500KB limit - would be truncated by server")
            return False
        else:
            logger.info(f"✅ Large message within acceptable limits")
            return True
            
    except Exception as e:
        logger.error(f"❌ Large content handling failed: {e}")
        return False

def main():
    """Run all diagnostic tests"""
    logger.info("🔍 ROBECO CITATION SYSTEM DIAGNOSTIC TESTS")
    logger.info("=" * 60)
    
    # Run tests
    results = []
    
    try:
        # Test 1: Backend citation generation
        enhanced_content, citations_count = test_backend_citation_generation()
        results.append(("Backend Citation Generation", True))
    except Exception as e:
        logger.error(f"❌ Backend test failed: {e}")
        results.append(("Backend Citation Generation", False))
    
    try:
        # Test 2: WebSocket message creation
        success = test_websocket_message_creation()[0] is not None
        results.append(("WebSocket Message Creation", success))
    except Exception as e:
        logger.error(f"❌ WebSocket test failed: {e}")
        results.append(("WebSocket Message Creation", False))
    
    try:
        # Test 3: Frontend message handling
        success = test_frontend_message_handling()
        results.append(("Frontend Message Handling", success))
    except Exception as e:
        logger.error(f"❌ Frontend test failed: {e}")
        results.append(("Frontend Message Handling", False))
    
    try:
        # Test 4: Large content handling
        success = test_large_content_handling()
        results.append(("Large Content Handling", success))
    except Exception as e:
        logger.error(f"❌ Large content test failed: {e}")
        results.append(("Large Content Handling", False))
    
    # Summary
    logger.info("\n📊 DIAGNOSTIC TEST RESULTS")
    logger.info("=" * 40)
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} {test_name}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    logger.info(f"\n🎯 OVERALL: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("✅ All tests passed - citation system appears to be working correctly in isolation")
        logger.info("💡 The issue may be in the real-time integration or specific edge cases")
    else:
        logger.info("❌ Some tests failed - issues identified in citation pipeline")

if __name__ == "__main__":
    main()