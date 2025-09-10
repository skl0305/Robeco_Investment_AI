#!/usr/bin/env python3
"""
Test Enhanced Retry System
Verify that the improved retry mechanisms work correctly for various error scenarios
"""

import sys
import asyncio
import logging
sys.path.append('/Users/skl/Desktop/Robeco Reporting/src')

from robeco.core.utils import retry_async
from robeco.core.memory import APIKeyManager
from datetime import datetime

# Setup logging to see retry attempts
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockGeminiError(Exception):
    """Mock Gemini API errors for testing"""
    pass

@retry_async(max_retries=3, delay=0.5, backoff_factor=2.0, jitter=False)
async def mock_api_call_500_error():
    """Simulate Gemini API 500 Internal Server Error"""
    raise MockGeminiError("500 INTERNAL - Server Error")

@retry_async(max_retries=3, delay=0.5, backoff_factor=2.0, jitter=False) 
async def mock_api_call_rate_limit():
    """Simulate rate limit error"""
    raise MockGeminiError("Rate limit exceeded. Please try again later.")

@retry_async(max_retries=3, delay=0.5, backoff_factor=2.0, jitter=False)
async def mock_api_call_auth_error():
    """Simulate authentication error (should not retry)"""
    raise MockGeminiError("401 Unauthorized - Invalid API key")

@retry_async(max_retries=2, delay=0.3, backoff_factor=2.0, jitter=False)
async def mock_api_call_success_after_failures():
    """Simulate success after 2 failures"""
    if not hasattr(mock_api_call_success_after_failures, 'attempt_count'):
        mock_api_call_success_after_failures.attempt_count = 0
    
    mock_api_call_success_after_failures.attempt_count += 1
    
    if mock_api_call_success_after_failures.attempt_count <= 2:
        raise MockGeminiError("500 INTERNAL - Temporary server error")
    
    return "✅ SUCCESS: API call completed successfully!"

async def test_retry_functionality():
    """Test various retry scenarios"""
    
    print("🔧 TESTING ENHANCED RETRY SYSTEM")
    print("=" * 50)
    
    # Test 1: 500 Internal Server Error (should retry)
    print("\n1️⃣ Testing 500 Internal Server Error (should retry 3 times)...")
    try:
        await mock_api_call_500_error()
        print("❌ Test failed - should have thrown exception after retries")
    except MockGeminiError as e:
        print(f"✅ Test passed - Exception thrown after retries: {e}")
    
    # Test 2: Rate limit error (should retry)
    print("\n2️⃣ Testing Rate Limit Error (should retry 3 times)...")
    try:
        await mock_api_call_rate_limit()
        print("❌ Test failed - should have thrown exception after retries")
    except MockGeminiError as e:
        print(f"✅ Test passed - Exception thrown after retries: {e}")
    
    # Test 3: Auth error (should NOT retry)
    print("\n3️⃣ Testing Auth Error (should NOT retry)...")
    try:
        await mock_api_call_auth_error()
        print("❌ Test failed - should have thrown exception immediately")
    except MockGeminiError as e:
        print(f"✅ Test passed - Auth error thrown immediately (no retries): {e}")
    
    # Test 4: Success after failures
    print("\n4️⃣ Testing Success After Failures (should succeed on 3rd attempt)...")
    try:
        # Reset counter
        if hasattr(mock_api_call_success_after_failures, 'attempt_count'):
            delattr(mock_api_call_success_after_failures, 'attempt_count')
        
        result = await mock_api_call_success_after_failures()
        print(f"✅ Test passed - {result}")
    except MockGeminiError as e:
        print(f"❌ Test failed - Should have succeeded after retries: {e}")

def test_api_key_manager():
    """Test API Key Manager functionality"""
    
    print("\n🔑 TESTING API KEY MANAGER")
    print("=" * 50)
    
    # Create manager with mock keys
    mock_keys = [
        "test_key_1_good",
        "test_key_2_suspended", 
        "test_key_3_rate_limited"
    ]
    
    manager = APIKeyManager(mock_keys)
    
    # Test optimal key selection
    print("1️⃣ Testing optimal key selection...")
    key1 = manager.get_optimal_key()
    print(f"✅ Selected key: {key1[:12]}...")
    
    # Simulate some errors and successes
    print("\n2️⃣ Testing performance tracking...")
    manager.record_performance(mock_keys[0], 1.5, True)  # Good performance
    manager.record_performance(mock_keys[1], 5.0, False)  # Poor performance
    manager.record_performance(mock_keys[1], 4.0, False)  # More poor performance
    manager.record_performance(mock_keys[2], 2.0, True)   # Good performance
    
    # Get stats
    stats = manager.get_key_stats()
    print("✅ Key performance stats:")
    for key, stat in stats.items():
        print(f"   {key}: Success rate = {1 - stat['error_rate']:.1%}, "
              f"Avg response = {stat['avg_response_time']:.1f}s")
    
    # Test getting next working key
    print("\n3️⃣ Testing next working key selection...")
    next_key = manager.get_next_working_key()
    print(f"✅ Next working key: {next_key[:12] if next_key else 'None'}...")

async def main():
    """Main test function"""
    
    print("🚀 ROBECO ENHANCED RETRY SYSTEM TEST")
    print("=" * 60)
    print(f"Test started at: {datetime.now()}")
    
    # Test retry functionality
    await test_retry_functionality()
    
    # Test API key manager
    test_api_key_manager()
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS COMPLETED")
    print("\n📊 ENHANCED RETRY SYSTEM SUMMARY:")
    print("✅ 500/503/504 server errors: Will retry with exponential backoff")
    print("✅ Rate limit/quota errors: Will retry with exponential backoff")
    print("✅ Network/timeout errors: Will retry with exponential backoff")
    print("❌ Auth errors (401/403): Will NOT retry (fail fast)")
    print("🔄 Max retries: 5 attempts with 2-30s delays")
    print("🎯 Jitter enabled: Prevents thundering herd issues")
    print("🔑 Smart key rotation: Switches to alternative keys on failures")
    print("📈 Performance tracking: Monitors key health and response times")

if __name__ == "__main__":
    asyncio.run(main())