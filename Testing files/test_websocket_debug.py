#!/usr/bin/env python3
"""
Test WebSocket connection to verify Google Search tool debugging
"""
import asyncio
import websockets
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_analysis():
    uri = "ws://localhost:8001/ws/professional"
    
    try:
        async with websockets.connect(uri) as websocket:
            logger.info("🔗 Connected to WebSocket")
            
            # Listen for connection message
            response = await websocket.recv()
            logger.info(f"📨 Connection response: {response}")
            
            # Send analysis request
            test_message = {
                "type": "start_analysis",
                "analyst": "fundamentals", 
                "ticker": "AAPL",
                "company": "Apple Inc"
            }
            
            logger.info(f"📤 Sending test message: {test_message}")
            await websocket.send(json.dumps(test_message))
            
            # Listen for responses (for 30 seconds)
            timeout_counter = 0
            while timeout_counter < 30:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    logger.info(f"📨 Analysis response: {response}")
                    
                    # Parse response to check for completion
                    try:
                        resp_data = json.loads(response)
                        if resp_data.get("type") in ["complete_investment_report", "streaming_analysis_completed"]:
                            logger.info("✅ Analysis completed!")
                            break
                    except:
                        pass
                        
                except asyncio.TimeoutError:
                    timeout_counter += 1
                    if timeout_counter % 5 == 0:
                        logger.info(f"⏳ Waiting for response... ({timeout_counter}s)")
                    continue
                    
    except Exception as e:
        logger.error(f"❌ WebSocket test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_analysis())