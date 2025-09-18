#!/usr/bin/env python3
"""
Test script to verify Google Search grounding functionality
"""

import sys
import os
sys.path.append('src')

from robeco.backend.api_key.gemini_api_key import get_intelligent_api_key
import google.generativeai as genai
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_google_search():
    """Test if Google Search grounding is working with our API keys"""
    
    # Get API key
    key_result = get_intelligent_api_key(agent_type="test")
    if not key_result:
        logger.error("❌ No API key available for testing")
        return False
    
    api_key, metadata = key_result
    logger.info(f"🔑 Testing with API key: {api_key[:8]}...{api_key[-4:]}")
    
    try:
        # Configure Gemini client
        genai.configure(api_key=api_key)
        
        # Test Google Search with simple query using proper SDK
        test_prompt = """
        Please search Google for recent information about Apple Inc (AAPL) stock performance and provide 2-3 key facts with sources.
        Use Google Search to find the most current information about Apple's stock price and recent news.
        """
        
        logger.info("🔍 Sending test request with Google Search...")
        
        # Use the newer SDK method
        model = genai.GenerativeModel(
            "gemini-2.5-flash",
            tools=[{"google_search": {}}]
        )
        
        # Generate response
        response = model.generate_content(
            test_prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.1,
                max_output_tokens=1000,
            )
        )
        
        logger.info(f"✅ Response received: {len(response.text)} characters")
        logger.info(f"📄 Response preview: {response.text[:200]}...")
        
        # Check for grounding metadata
        has_grounding = False
        if hasattr(response, 'candidates') and response.candidates:
            for candidate in response.candidates:
                if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
                    has_grounding = True
                    logger.info("✅ GROUNDING METADATA FOUND!")
                    
                    # Check for grounding chunks
                    if hasattr(candidate.grounding_metadata, 'grounding_chunks'):
                        chunks = candidate.grounding_metadata.grounding_chunks
                        logger.info(f"📚 Found {len(chunks)} grounding chunks")
                        
                        for i, chunk in enumerate(chunks[:3]):  # Show first 3 chunks
                            if hasattr(chunk, 'web') and chunk.web:
                                logger.info(f"   🌐 Chunk {i+1}: {chunk.web.title} - {chunk.web.uri}")
                    
                    # Check for search queries
                    if hasattr(candidate.grounding_metadata, 'search_entry_point'):
                        logger.info("🔍 Search entry point found")
                    
                    break
        
        if not has_grounding:
            logger.warning("⚠️ NO GROUNDING METADATA FOUND")
            logger.warning("🚨 This indicates Google Search is NOT working with this API key")
            logger.warning("💡 Possible causes:")
            logger.warning("   1. API key doesn't have Google Search grounding enabled")
            logger.warning("   2. Google Search quota exceeded")
            logger.warning("   3. API key region restrictions")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Google Search test failed: {e}")
        logger.error(f"   Error type: {type(e).__name__}")
        return False

def test_multiple_keys():
    """Test multiple API keys to find working ones"""
    from robeco.backend.api_key.gemini_api_key import api_keys
    
    working_keys = []
    
    for i, key in enumerate(api_keys[:5]):  # Test first 5 keys
        logger.info(f"\n🧪 Testing API key {i+1}/5: {key[:8]}...{key[-4:]}")
        
        # Temporarily override the key selection
        original_func = get_intelligent_api_key
        
        def temp_get_key(*args, **kwargs):
            return key, {"source": "test"}
        
        # Monkey patch for this test
        import robeco.backend.api_key.gemini_api_key
        robeco.backend.api_key.gemini_api_key.get_intelligent_api_key = temp_get_key
        
        try:
            if test_google_search():
                working_keys.append(key)
                logger.info(f"✅ Key {i+1} WORKS with Google Search!")
            else:
                logger.warning(f"❌ Key {i+1} does NOT work with Google Search")
        except:
            logger.error(f"❌ Key {i+1} failed completely")
        
        # Restore original function
        robeco.backend.api_key.gemini_api_key.get_intelligent_api_key = original_func
    
    logger.info(f"\n📊 SUMMARY: {len(working_keys)}/{len(api_keys[:5])} keys work with Google Search")
    
    if working_keys:
        logger.info("✅ Working keys:")
        for key in working_keys:
            logger.info(f"   🔑 {key[:8]}...{key[-4:]}")
    else:
        logger.error("🚨 NO API keys have Google Search grounding enabled!")
        logger.error("💡 You need to:")
        logger.error("   1. Get API keys with Google Search grounding permissions")
        logger.error("   2. Enable grounding in Google AI Studio")
        logger.error("   3. Check if your region supports Google Search grounding")
    
    return working_keys

if __name__ == "__main__":
    logger.info("🧪 Testing Google Search grounding functionality...")
    logger.info("=" * 60)
    
    # Test current key selection
    logger.info("\n1️⃣ Testing current API key selection...")
    current_works = test_google_search()
    
    # Test multiple keys
    logger.info("\n2️⃣ Testing multiple API keys...")
    working_keys = test_multiple_keys()
    
    logger.info("\n" + "=" * 60)
    logger.info("🎯 CONCLUSION:")
    
    if working_keys:
        logger.info(f"✅ Found {len(working_keys)} working API keys with Google Search")
        logger.info("✅ Google Search should work - issue might be elsewhere")
    else:
        logger.error("❌ NO API keys have Google Search grounding enabled")
        logger.error("🔧 ACTION REQUIRED: Get API keys with proper permissions")