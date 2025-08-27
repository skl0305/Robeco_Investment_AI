#!/usr/bin/env python3
"""
Robeco Professional Streaming Server
Ultra-sophisticated real-time streaming server for investment analysis
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Set
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from typing import List
import uvicorn
import sys
import os
from pathlib import Path
import yfinance as yf
import pandas as pd

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from robeco.backend.ultra_sophisticated_multi_agent_engine import (
    ultra_sophisticated_engine,
    AnalysisContext,
    AnalysisPhase
)

# Import bulk file processor
from robeco.backend.bulk_file_processor import bulk_processor, BulkAnalysisSession

# Import for chat functionality
try:
    from google import genai
    from google.genai import types
except ImportError:
    pass  # Will warn later when logger is available

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Robeco Ultra-Sophisticated Professional Streaming Server",
    description="Sequential Intelligence Multi-Agent Architecture with cross-agent synthesis",
    version="2.0.0"
)

# Mount static files
static_path = Path(__file__).parent.parent / "frontend" / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
    logger.info(f"✅ Static files mounted from {static_path}")

# Active WebSocket connections and chat sessions
active_connections: Set[WebSocket] = set()
connection_counter = 0
chat_sessions = {}  # Store chat history per connection and analyst

@app.get("/favicon.ico")
async def get_favicon():
    """Return a simple favicon"""
    return HTMLResponse("", status_code=204)

@app.get("/", response_class=HTMLResponse)
async def serve_workbench():
    """Serve the enhanced professional workbench interface"""
    try:
        # Try enhanced template first
        enhanced_template_path = Path(__file__).parent.parent / "frontend" / "templates" / "robeco_professional_workbench_enhanced.html"
        logger.info(f"DEBUG: Looking for template at: {enhanced_template_path}")
        
        if enhanced_template_path.exists():
            logger.info("DEBUG: Enhanced template file exists, reading content...")
            with open(enhanced_template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            # Silent syntax validation (only show errors)
            main_script_pattern = content.find('<script>\n        // DEBUG: Script started loading')
            main_script_end = content.rfind('</script>')
            
            if main_script_pattern != -1 and main_script_end != -1:
                js_content = content[main_script_pattern:main_script_end]
                
                # Quick syntax validation
                unmatched_braces = js_content.count('{') - js_content.count('}')
                unmatched_parens = js_content.count('(') - js_content.count(')')
                unmatched_brackets = js_content.count('[') - js_content.count(']')
                
                # Check for template literal issues (ignore regex patterns)
                import re
                js_content_no_regex = re.sub(r'\.replace\([^)]*`[^`]*`[^)]*\)', '', js_content)
                backtick_count = js_content_no_regex.count('`')
                
                # Only log errors, not debug info
                if unmatched_braces != 0:
                    logger.error(f"❌ SYNTAX ERROR: Unmatched braces detected: {unmatched_braces}")
                if unmatched_parens != 0:
                    logger.error(f"❌ SYNTAX ERROR: Unmatched parentheses detected: {unmatched_parens}")
                if unmatched_brackets != 0:
                    logger.error(f"❌ SYNTAX ERROR: Unmatched brackets detected: {unmatched_brackets}")
                if backtick_count > 0:
                    logger.error(f"❌ SYNTAX ERROR: Template literals still present: {backtick_count}")
            
            logger.info("✅ Served enhanced professional workbench interface")
            return HTMLResponse(content)
        
        # Fallback to MVP template
        template_path = Path(__file__).parent.parent / "frontend" / "templates" / "robeco_investment_workbench_mvp.html"
        
        if template_path.exists():
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            logger.info("✅ Served MVP workbench interface")
            return HTMLResponse(content)
        
        logger.error(f"No templates found")
        return HTMLResponse("""
            <h1>Robeco Professional Platform</h1>
            <p>Template not found. Please ensure the frontend files are properly configured.</p>
        """, status_code=404)
        
    except Exception as e:
        logger.error(f"Error serving workbench: {e}")
        return HTMLResponse(f"<h1>Error</h1><p>{str(e)}</p>", status_code=500)

@app.websocket("/ws/professional")
async def websocket_endpoint(websocket: WebSocket):
    """Professional WebSocket endpoint for real-time analysis streaming"""
    global connection_counter
    connection_counter += 1
    connection_id = f"robeco_client_{connection_counter}"
    
    await websocket.accept()
    active_connections.add(websocket)
    
    logger.info(f"🔗 New professional connection: {connection_id}")
    
    # Send initial connection confirmation
    await websocket.send_text(json.dumps({
        "type": "connection_established",
        "data": {
            "connection_id": connection_id,
            "server": "Robeco Professional Streaming Server",
            "capabilities": [
                "real_time_analysis",
                "professional_reports", 
                "institutional_sources",
                "streaming_content"
            ],
            "timestamp": datetime.now().isoformat()
        }
    }))
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            message_type = message.get('type', 'unknown')
            
            logger.info(f"📨 Message from {connection_id}: {message_type}")
            
            if message_type == 'start_analysis':
                # Handle real-time analysis request
                await handle_streaming_analysis(websocket, connection_id, message)
            
            elif message_type == 'chat_message':
                # Handle post-analysis chat with AI analyst
                await handle_chat_message(websocket, connection_id, message)
            
            elif message_type == 'get_chat_history':
                # Get chat history for specific analyst
                await handle_get_chat_history(websocket, connection_id, message)
            
            elif message_type == 'clear_chat_history':
                # Clear chat history for specific analyst
                await handle_clear_chat_history(websocket, connection_id, message)
            
            elif message_type == 'start_bulk_analysis':
                # Handle bulk file analysis with real-time streaming
                await handle_bulk_analysis_streaming(websocket, connection_id, message)
            
            elif message_type == 'ping':
                # Handle ping for connection health
                await websocket.send_text(json.dumps({
                    "type": "pong",
                    "data": {"timestamp": datetime.now().isoformat()}
                }))
            
            else:
                logger.warning(f"⚠️ Unhandled message type: {message_type}")
                
    except WebSocketDisconnect:
        active_connections.discard(websocket)
        # Clean up chat sessions for this connection
        keys_to_remove = [key for key in chat_sessions.keys() if key.startswith(connection_id)]
        for key in keys_to_remove:
            del chat_sessions[key]
        logger.info(f"❌ Connection closed: {connection_id} (cleaned up {len(keys_to_remove)} chat sessions)")
        
    except Exception as e:
        logger.error(f"❌ WebSocket error for {connection_id}: {e}")
        active_connections.discard(websocket)

async def fetch_stock_data_internal(ticker: str) -> Dict:
    """Internal function to fetch stock data for agent analysis"""
    try:
        # This reuses the same logic as the API endpoint but returns the data directly
        import yfinance as yf
        import pandas as pd
        
        logger.info(f"🔍 Fetching stock data for: {ticker}")
        
        # Clean and format ticker symbol for different exchanges
        original_ticker = ticker
        ticker_formats = [ticker.upper()]
        
        # Try different exchange suffixes for international markets
        if '.' not in ticker:
            ticker_formats.extend([
                f"{ticker}.SI",  # Singapore Exchange  
                f"{ticker}.HK",  # Hong Kong Exchange
                f"{ticker}.TO",  # Toronto Stock Exchange
                f"{ticker}.L",   # London Stock Exchange
            ])
        
        logger.info(f"📊 Trying ticker formats: {ticker_formats}")
        
        stock = None
        working_ticker = None
        
        # Try each ticker format until one works
        for ticker_format in ticker_formats:
            try:
                logger.info(f"🎯 Testing ticker format: {ticker_format}")
                test_stock = yf.Ticker(ticker_format)
                test_info = test_stock.info
                
                # Check if we got valid data
                if test_info and len(test_info) > 10 and 'regularMarketPrice' in test_info:
                    stock = test_stock
                    working_ticker = ticker_format
                    logger.info(f"✅ Success with ticker format: {working_ticker}")
                    break
                else:
                    logger.info(f"⚠️ No data for format: {ticker_format}")
                    
            except Exception as e:
                logger.info(f"❌ Failed format {ticker_format}: {str(e)[:100]}")
                continue
        
        if not stock or not working_ticker:
            return {
                "success": False, 
                "message": f"No valid data found for ticker {original_ticker} across all exchange formats",
                "ticker": original_ticker
            }
        
        # Get comprehensive stock information
        info = stock.info
        
        # Prepare comprehensive data structure (same as API endpoint)
        # [Include the same data structure as the existing API endpoint]
        stock_data = {
            # Basic Info
            "ticker": working_ticker,
            "company_name": info.get("longName", info.get("shortName", "")),
            "currency": info.get("currency", "USD"),
            "exchange": info.get("exchange", ""),
            "sector": info.get("sector", ""),
            "industry": info.get("industry", ""),
            "country": info.get("country", ""),
            "website": info.get("website", ""),
            "business_summary": info.get("longBusinessSummary", ""),
            
            # Current Price Data
            "current_price": info.get("regularMarketPrice", info.get("currentPrice")),
            "previous_close": info.get("regularMarketPreviousClose", info.get("previousClose")),
            "price_change": None,  # Will calculate below
            "price_change_pct": None,  # Will calculate below
            "day_range": None,  # Will format below
            
            # Market Data
            "market_cap": info.get("marketCap"),
            "enterprise_value": info.get("enterpriseValue"),
            "shares_outstanding": info.get("sharesOutstanding"),
            "float_shares": info.get("floatShares"),
            "volume": info.get("regularMarketVolume", info.get("volume")),
            "average_volume": info.get("averageVolume"),
            "average_volume_10days": info.get("averageVolume10days"),
            
            # Valuation Metrics
            "pe_ratio": info.get("trailingPE"),
            "forward_pe": info.get("forwardPE"),
            "peg_ratio": info.get("pegRatio"),
            "price_to_book": info.get("priceToBook"),
            "price_to_sales": info.get("priceToSalesTrailing12Months"),
            "enterprise_to_revenue": info.get("enterpriseToRevenue"),
            "enterprise_to_ebitda": info.get("enterpriseToEbitda"),
            
            # Profitability Metrics
            "profit_margin": info.get("profitMargins"),
            "operating_margin": info.get("operatingMargins"),
            "return_on_equity": info.get("returnOnEquity"),
            "return_on_assets": info.get("returnOnAssets"),
            "revenue_growth": info.get("revenueGrowth"),
            "earnings_growth": info.get("earningsGrowth"),
            "earnings_quarterly_growth": info.get("earningsQuarterlyGrowth"),
            
            # Financial Health
            "total_cash": info.get("totalCash"),
            "total_debt": info.get("totalDebt"),
            "current_ratio": info.get("currentRatio"),
            "debt_to_equity": info.get("debtToEquity"),
            "quick_ratio": info.get("quickRatio"),
            "gross_margins": info.get("grossMargins"),
            
            # All other yfinance fields (unfiltered)
            "raw_data": info  # Complete raw data for agents
        }
        
        return {"success": True, "data": stock_data}
        
    except Exception as e:
        logger.error(f"❌ Internal stock fetch error: {e}")
        return {"success": False, "message": str(e), "ticker": ticker}

async def handle_streaming_analysis(websocket: WebSocket, connection_id: str, message: Dict):
    """Handle real-time streaming analysis request"""
    
    try:
        # Extract analysis parameters
        analyst_type = message.get('analyst', 'fundamentals')
        company = message.get('company', 'Unknown Company')
        ticker = message.get('ticker', 'N/A')
        user_query = message.get('user_query', '')
        
        logger.info(f"🧠 Starting ultra-sophisticated sequential multi-agent analysis for {company} ({ticker})")
        
        # Fetch comprehensive stock data to feed to agents
        stock_data = None
        try:
            logger.info(f"📊 Fetching comprehensive stock data for agents: {ticker}")
            stock_response = await fetch_stock_data_internal(ticker)
            if stock_response.get('success', False):
                stock_data = stock_response.get('data', {})
                logger.info(f"✅ Stock data loaded for agents: {len(stock_data)} fields available")
            else:
                logger.warning(f"⚠️ Failed to fetch stock data: {stock_response.get('message', 'Unknown error')}")
        except Exception as e:
            logger.error(f"❌ Error fetching stock data for agents: {e}")
        
        # Send analysis started confirmation
        await websocket.send_text(json.dumps({
            "type": "streaming_analysis_started",
            "data": {
                "analyst_type": analyst_type,
                "company": company,
                "ticker": ticker,
                "connection_id": connection_id,
                "timestamp": datetime.now().isoformat()
            }
        }))
        
        # Create analysis context for ultra-sophisticated sequential deployment
        context = AnalysisContext(
            company_name=company,
            ticker=ticker,
            user_query=user_query,
            session_id=f"{connection_id}_{int(datetime.now().timestamp())}",
            start_time=datetime.now(),
            stock_data=stock_data  # Feed complete yfinance data to all agents
        )
        
        # Stream single specialist analysis in real-time with Google Search
        async for update in ultra_sophisticated_engine.generate_single_agent_analysis(analyst_type, context):
            
            # Format update for frontend
            if update['type'] == 'status_update':
                await websocket.send_text(json.dumps({
                    "type": "streaming_status_update",
                    "data": {
                        "progress": update['data']['progress'],
                        "message": update['data']['message'],
                        "phase": update['data']['phase'],
                        "timestamp": update['data']['timestamp']
                    }
                }))
                
            elif update['type'] == 'research_source':
                await websocket.send_text(json.dumps({
                    "type": "streaming_research_source", 
                    "data": update['data']
                }))
                
            elif update['type'] == 'streaming_ai_content':
                # Add safety checks for streaming content
                try:
                    content_data = update['data']
                    chunk_content = content_data.get('content_chunk', '')
                    
                    # Ensure content is safe for JSON serialization
                    if chunk_content:
                        # Clean any potentially problematic characters
                        safe_chunk = chunk_content.replace('\x00', '').replace('\ufffd', '')
                        
                        # Limit chunk size to prevent WebSocket issues
                        if len(safe_chunk) > 50000:  # 50KB limit per chunk
                            logger.warning(f"📨 Large chunk detected ({len(safe_chunk)} chars), splitting...")
                            # Split large chunks
                            for i in range(0, len(safe_chunk), 50000):
                                sub_chunk = safe_chunk[i:i+50000]
                                await websocket.send_text(json.dumps({
                                    "type": "streaming_ai_content",
                                    "data": {"content_chunk": sub_chunk}
                                }))
                        else:
                            await websocket.send_text(json.dumps({
                                "type": "streaming_ai_content",
                                "data": {"content_chunk": safe_chunk}
                            }))
                    else:
                        # Send empty chunk to maintain flow
                        await websocket.send_text(json.dumps({
                            "type": "streaming_ai_content", 
                            "data": content_data
                        }))
                except Exception as stream_error:
                    logger.warning(f"📨 Error processing streaming content: {stream_error}")
                    # Continue without failing the entire stream
                    continue
            
            elif update['type'] == 'streaming_chunk':
                # Handle real-time streaming chunks from engine
                try:
                    chunk_content = update['data'].get('chunk', '')
                    
                    # Ensure content is safe for JSON serialization
                    if chunk_content:
                        # Clean any potentially problematic characters
                        safe_chunk = chunk_content.replace('\x00', '').replace('\ufffd', '')
                        
                        await websocket.send_text(json.dumps({
                            "type": "streaming_ai_content",
                            "data": {"content_chunk": safe_chunk}
                        }))
                    
                except Exception as chunk_error:
                    logger.warning(f"📨 Error processing streaming chunk: {chunk_error}")
                    continue
            
            elif update['type'] == 'streaming_ai_content_final':
                # Handle final content with all citations integrated
                logger.info(f"🎯 WEBSOCKET: Received streaming_ai_content_final from engine")
                logger.info(f"   📄 Content length: {len(update['data'].get('content_complete', ''))}")
                logger.info(f"   📚 Citations: {update['data'].get('citations_count', 0)}")
                
                try:
                    logger.info(f"🚀 WEBSOCKET: Preparing final content message...")
                    
                    # Clean content for JSON serialization
                    content_complete = update['data'].get('content_complete', '')
                    safe_content = content_complete.replace('\x00', '').replace('\ufffd', '')
                    
                    # Check message size before sending
                    safe_message = {
                        "type": "streaming_ai_content_final",
                        "data": {
                            **update['data'],
                            "content_complete": safe_content
                        }
                    }
                    
                    # Test JSON serialization first
                    json_string = json.dumps(safe_message)
                    message_size = len(json_string)
                    logger.info(f"📏 WEBSOCKET: Message size: {message_size} bytes")
                    
                    # WebSocket limit handling with chunked delivery for large content
                    if message_size > 200000:  # 200KB limit - more conservative
                        logger.warning(f"⚠️ WEBSOCKET: Large message ({message_size} bytes), using chunked delivery...")
                        
                        # Send content in chunks with final assembly message
                        chunk_size = 150000  # 150KB per chunk
                        content_chunks = []
                        
                        for i in range(0, len(safe_content), chunk_size):
                            chunk = safe_content[i:i + chunk_size]
                            content_chunks.append(chunk)
                        
                        logger.info(f"📦 WEBSOCKET: Splitting into {len(content_chunks)} chunks")
                        
                        # Send chunk header
                        chunk_header = {
                            "type": "streaming_ai_content_chunked_start",
                            "data": {
                                "total_chunks": len(content_chunks),
                                "citations_count": safe_message['data']['citations_count'],
                                "chunk_id": f"citations_{int(datetime.now().timestamp())}"
                            }
                        }
                        await websocket.send_text(json.dumps(chunk_header))
                        
                        # Send each chunk
                        for chunk_idx, chunk in enumerate(content_chunks):
                            chunk_message = {
                                "type": "streaming_ai_content_chunk",
                                "data": {
                                    "chunk_index": chunk_idx,
                                    "chunk_content": chunk,
                                    "is_final_chunk": chunk_idx == len(content_chunks) - 1,
                                    "chunk_id": chunk_header['data']['chunk_id']
                                }
                            }
                            await websocket.send_text(json.dumps(chunk_message))
                            logger.info(f"📦 WEBSOCKET: Sent chunk {chunk_idx + 1}/{len(content_chunks)}")
                            
                            # Small delay between chunks to prevent overwhelming
                            await asyncio.sleep(0.01)
                        
                        # Send final assembly message
                        final_assembly = {
                            "type": "streaming_ai_content_final",
                            "data": {
                                "content_complete": "CHUNKED_CONTENT",  # Special marker
                                "citations_count": safe_message['data']['citations_count'],
                                "replace_content": True,
                                "chunk_id": chunk_header['data']['chunk_id'],
                                "assembly_mode": "chunked"
                            }
                        }
                        await websocket.send_text(json.dumps(final_assembly))
                        logger.info(f"✅ WEBSOCKET: Chunked delivery completed ({len(content_chunks)} chunks, {message_size} total bytes)")
                        
                    else:
                        # Standard single message delivery for smaller content
                        logger.info(f"🚀 WEBSOCKET: Sending standard message ({message_size} bytes)...")
                        await websocket.send_text(json_string)
                        logger.info(f"✅ WEBSOCKET: streaming_ai_content_final message sent successfully ({len(json_string)} bytes)")
                    
                except Exception as final_error:
                    logger.error(f"❌ WEBSOCKET ERROR: Failed to send streaming_ai_content_final: {final_error}")
                    logger.error(f"   Content length: {len(update['data'].get('content_complete', ''))}")
                    logger.error(f"   Error type: {type(final_error).__name__}")
                    import traceback
                    logger.error(f"   Stack trace: {traceback.format_exc()}")
                    
                    # Try sending a minimal error message instead
                    try:
                        error_message = {
                            "type": "streaming_ai_content_final",
                            "data": {
                                "content_complete": "Error: Content too large for WebSocket transmission",
                                "citations_count": 0,
                                "replace_content": True
                            }
                        }
                        await websocket.send_text(json.dumps(error_message))
                        logger.info("📤 WEBSOCKET: Sent error fallback message")
                    except Exception as fallback_error:
                        logger.error(f"❌ WEBSOCKET: Even fallback message failed: {fallback_error}")
                
            elif update['type'] == 'streaming_analysis_completed':
                await websocket.send_text(json.dumps({
                    "type": "streaming_analysis_completed",
                    "data": update['data']
                }))
                
            elif update['type'] == 'analysis_error':
                await websocket.send_text(json.dumps({
                    "type": "streaming_analysis_error",
                    "data": update['data']
                }))
                
            elif update['type'] == 'agent_deployed':
                await websocket.send_text(json.dumps({
                    "type": "agent_deployed",
                    "data": update['data']
                }))
                
            elif update['type'] == 'agent_completed':
                await websocket.send_text(json.dumps({
                    "type": "agent_completed", 
                    "data": update['data']
                }))
                
            # Small delay to ensure proper streaming experience
            await asyncio.sleep(0.01)
        
        logger.info(f"✅ Analysis completed for {connection_id}: {analyst_type} - {ticker}")
        
    except Exception as e:
        logger.error(f"❌ Analysis error for {connection_id}: {e}")
        logger.error(f"❌ Exception type: {type(e).__name__}")
        import traceback
        logger.error(f"❌ Full traceback: {traceback.format_exc()}")
        
        # Determine error type and send clear message
        error_message = str(e)
        if "API key" in error_message or "suspended" in error_message or "403" in error_message:
            error_type = "api_suspended"
            user_message = "All API keys suspended! Please provide working GEMINI_API_KEY environment variable."
        else:
            error_type = "analysis_failed"
            user_message = f"Analysis failed: {error_message}"
        
        # Send clear error message to client - but only if WebSocket is still open
        try:
            await websocket.send_text(json.dumps({
                "type": "streaming_analysis_error",
                "data": {
                    "error": user_message,
                    "error_type": error_type,
                    "timestamp": datetime.now().isoformat()
                }
            }))
        except Exception as ws_error:
            logger.error(f"❌ Could not send error message to {connection_id} - WebSocket closed: {ws_error}")

async def handle_chat_message(websocket: WebSocket, connection_id: str, message: Dict):
    """Handle post-analysis chat with AI analyst - with conversation history"""
    
    try:
        analyst_type = message.get('analyst', 'fundamentals')
        user_message = message.get('message', '')
        company = message.get('company', 'Unknown Company')
        ticker = message.get('ticker', 'N/A')
        analysis_content = message.get('analysis_content', '')  # Pass the analysis results for context
        
        logger.info(f"💬 Chat message from {connection_id}: {user_message[:50]}... (analyst: {analyst_type})")
        
        # Initialize sophisticated chat session with memory integration if not exists
        chat_key = f"{connection_id}_{analyst_type}"
        if chat_key not in chat_sessions:
            chat_sessions[chat_key] = {
                'messages': [],
                'analyst': analyst_type,
                'company': company,
                'ticker': ticker,
                'analysis_content': analysis_content,
                'created': datetime.now().isoformat(),
                'key_insights_discussed': [],
                'pm_concerns_raised': [],
                'contrarian_views_shared': [],
                'follow_up_items': [],
                'conversation_depth': 'institutional_portfolio_manager_level'
            }
        
        # Update analysis content if provided (for continuity across conversations)
        if analysis_content:
            chat_sessions[chat_key]['analysis_content'] = analysis_content
        
        # Add user message to history
        chat_sessions[chat_key]['messages'].append({
            'role': 'user',
            'content': user_message,
            'timestamp': datetime.now().isoformat()
        })
        
        # Build sophisticated conversation context with full history and memory integration
        conversation_history = ""
        recent_messages = chat_sessions[chat_key]['messages'][-15:]  # Last 15 messages for deeper context
        
        if recent_messages:
            conversation_history += "**Recent Discussion Context**:\n"
            for msg in recent_messages:
                role_label = "Portfolio Manager" if msg['role'] == 'user' else f"{analyst_type.title()} Analyst"
                timestamp = msg.get('timestamp', '')[:10]  # Date only
                conversation_history += f"{role_label} ({timestamp}): {msg['content']}\n\n"
        
        # Add conversation memory elements
        session = chat_sessions[chat_key]
        memory_context = ""
        if session.get('key_insights_discussed'):
            memory_context += f"**Previously Discussed Insights**: {', '.join(session['key_insights_discussed'])}\n"
        if session.get('pm_concerns_raised'):
            memory_context += f"**PM Concerns Previously Raised**: {', '.join(session['pm_concerns_raised'])}\n"
        if session.get('contrarian_views_shared'):
            memory_context += f"**Contrarian Views Already Shared**: {', '.join(session['contrarian_views_shared'])}\n"
        
        conversation_history = memory_context + conversation_history
        
        # Enhanced chat context with analysis results and conversation history
        chat_context = f"""
You are a Senior {analyst_type.title()} Analyst at Robeco engaged in sophisticated portfolio management discussion about {company} ({ticker}) with an experienced Portfolio Manager. This is institutional-level dialogue requiring exceptional insight and directness.

**Your Completed Analysis Context**: 
{analysis_content[:2000] if analysis_content else 'Comprehensive multi-agent analysis recently completed with detailed sector, fundamental, technical, risk, ESG and valuation assessment'}

**Conversation Memory & History**:
{conversation_history}

**Current Portfolio Manager Inquiry**: {user_message}

**Discussion Requirements**:
- Be exceptionally insightful and direct - challenge assumptions and provide contrarian perspectives
- Reference specific quantitative findings, metrics, and data points from your analysis
- Provide sophisticated institutional-level insights that experienced PMs expect
- Build upon previous conversation points and maintain analytical continuity
- Focus on actionable investment implications and portfolio construction considerations
- Use investment banking terminology naturally (bps, YoY, QoQ, ROIC, multiple expansion, etc.)
- Challenge conventional thinking with data-driven alternative viewpoints
- Provide specific catalyst timelines and risk/reward asymmetry analysis

**Your Analytical Persona**: You are the specialist who conducted rigorous institutional research. Be confident, direct, and insightful. Avoid generic responses - provide specific, sophisticated insights that demonstrate deep analytical capabilities and challenge the PM's thinking where appropriate.

**Response Style**: Professional, direct, sophisticated - as if discussing with a seasoned institutional investor who expects exceptional insights beyond conventional analysis.

Respond with institutional-level sophistication:"""
        
        # Try to get a working API key and generate response
        try:
            from .api_key.gemini_api_key import get_intelligent_api_key, suspended_keys
            
            api_key, key_info = get_intelligent_api_key(agent_type=analyst_type)
            if not api_key:
                raise Exception("No API key available")
            
            client = genai.Client(api_key=api_key)
            
            # Generate sophisticated portfolio manager discussion response
            generate_config = types.GenerateContentConfig(
                temperature=0.15,  # Lower for more focused, consistent institutional dialogue
                top_p=0.85,
                max_output_tokens=32000,  # Enhanced for comprehensive follow-up discussions
                response_mime_type="text/plain",
                system_instruction=chat_context
            )
            
            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=user_message)],
                ),
            ]
            
            # Generate response
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=contents,
                config=generate_config,
            )
            
            if response and response.text:
                # Add AI response to chat history
                chat_sessions[chat_key]['messages'].append({
                    'role': 'assistant',
                    'content': response.text,
                    'timestamp': datetime.now().isoformat()
                })
                
                # Send chat response
                await websocket.send_text(json.dumps({
                    "type": "chat_response",
                    "data": {
                        "response": response.text,
                        "analyst": analyst_type,
                        "timestamp": datetime.now().isoformat(),
                        "conversation_id": chat_key
                    }
                }))
                
                logger.info(f"✅ Chat response sent for {analyst_type} analyst (history: {len(chat_sessions[chat_key]['messages'])} messages)")
            else:
                raise Exception("No response generated")
                
        except Exception as api_error:
            # No fallback - require working API
            logger.error(f"❌ Chat API failed: {api_error}")
            
            await websocket.send_text(json.dumps({
                "type": "chat_error",
                "data": {
                    "error": f"Chat requires working API key. Please set GEMINI_API_KEY environment variable.",
                    "analyst": analyst_type,
                    "timestamp": datetime.now().isoformat()
                }
            }))
        
    except Exception as e:
        logger.error(f"❌ Chat handling error for {connection_id}: {e}")
        
        # Send error message
        await websocket.send_text(json.dumps({
            "type": "chat_error",
            "data": {
                "error": f"Chat failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
        }))

async def handle_get_chat_history(websocket: WebSocket, connection_id: str, message: Dict):
    """Get chat history for specific analyst"""
    try:
        analyst_type = message.get('analyst', 'fundamentals')
        chat_key = f"{connection_id}_{analyst_type}"
        
        if chat_key in chat_sessions:
            chat_history = chat_sessions[chat_key]['messages']
            logger.info(f"📜 Sending chat history for {analyst_type}: {len(chat_history)} messages")
        else:
            chat_history = []
            logger.info(f"📜 No chat history found for {analyst_type}")
        
        await websocket.send_text(json.dumps({
            "type": "chat_history",
            "data": {
                "analyst": analyst_type,
                "messages": chat_history,
                "conversation_id": chat_key
            }
        }))
        
    except Exception as e:
        logger.error(f"❌ Error getting chat history: {e}")
        await websocket.send_text(json.dumps({
            "type": "chat_error",
            "data": {
                "error": f"Failed to get chat history: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
        }))

async def handle_clear_chat_history(websocket: WebSocket, connection_id: str, message: Dict):
    """Clear chat history for specific analyst"""
    try:
        analyst_type = message.get('analyst', 'fundamentals')
        chat_key = f"{connection_id}_{analyst_type}"
        
        if chat_key in chat_sessions:
            message_count = len(chat_sessions[chat_key]['messages'])
            chat_sessions[chat_key]['messages'] = []
            logger.info(f"🗑️ Cleared {message_count} messages for {analyst_type}")
        else:
            logger.info(f"🗑️ No chat history to clear for {analyst_type}")
        
        await websocket.send_text(json.dumps({
            "type": "chat_history_cleared",
            "data": {
                "analyst": analyst_type,
                "timestamp": datetime.now().isoformat()
            }
        }))
        
    except Exception as e:
        logger.error(f"❌ Error clearing chat history: {e}")
        await websocket.send_text(json.dumps({
            "type": "chat_error",
            "data": {
                "error": f"Failed to clear chat history: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
        }))

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": "Robeco Professional Streaming Server",
        "active_connections": len(active_connections),
        "timestamp": datetime.now().isoformat(),
        "capabilities": [
            "real_time_streaming",
            "professional_analysis",
            "institutional_reports",
            "websocket_support"
        ]
    }

@app.get("/api/status")
async def api_status():
    """API status information"""
    return {
        "server_info": {
            "name": "Robeco Professional Streaming Server",
            "version": "1.0.0",
            "uptime": "Active",
            "environment": "Production"
        },
        "connections": {
            "active": len(active_connections),
            "total_served": connection_counter
        },
        "capabilities": {
            "analysis_types": [
                "fundamentals",
                "industry", 
                "technical",
                "risk",
                "esg",
                "valuation",
                "bull",
                "bear", 
                "catalysts",
                "drivers",
                "consensus",
                "anti_consensus"
            ],
            "streaming": True,
            "real_time": True,
            "professional_grade": True
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/stock/{ticker}")
async def get_stock_data(ticker: str):
    """Get real-time stock data from yfinance with chart data"""
    try:
        # Clean and format ticker symbol for different exchanges
        original_ticker = ticker
        ticker = ticker.upper().strip()
        
        # Handle different ticker formats
        formatted_tickers = [ticker]
        
        # Singapore Exchange (SGX) formatting
        if "SGX:" in ticker:
            sgx_ticker = ticker.replace("SGX:", "").strip()
            formatted_tickers = [
                f"{sgx_ticker}.SI",  # Singapore format
                sgx_ticker,
                f"{sgx_ticker}.SG"
            ]
        # Hong Kong Exchange (HKG) formatting  
        elif "HKG:" in ticker:
            hkg_ticker = ticker.replace("HKG:", "").strip()
            formatted_tickers = [
                f"{hkg_ticker}.HK",  # Hong Kong format
                f"0{hkg_ticker}.HK" if len(hkg_ticker) < 4 else f"{hkg_ticker}.HK",
                hkg_ticker
            ]
        # Other exchange formats
        elif ":" in ticker:
            exchange, symbol = ticker.split(":", 1)
            symbol = symbol.strip()
            if exchange == "NYSE" or exchange == "NASDAQ":
                formatted_tickers = [symbol]
            else:
                formatted_tickers = [f"{symbol}.{exchange}", symbol]
        
        logger.info(f"🔍 Fetching stock data for: {original_ticker}")
        logger.info(f"📊 Trying ticker formats: {formatted_tickers}")
        
        stock = None
        info = {}
        hist_5d = None
        hist_5y = None
        
        # Try different ticker formats
        for test_ticker in formatted_tickers:
            try:
                logger.info(f"🎯 Testing ticker format: {test_ticker}")
                test_stock = yf.Ticker(test_ticker)
                test_info = test_stock.info
                test_hist = test_stock.history(period="5d")
                
                if not test_hist.empty and test_info and test_info.get('regularMarketPrice') is not None:
                    logger.info(f"✅ Success with ticker format: {test_ticker}")
                    stock = test_stock
                    info = test_info
                    hist_5d = test_hist
                    ticker = test_ticker  # Update to working format
                    break
                    
            except Exception as e:
                logger.warning(f"⚠️ Failed ticker format {test_ticker}: {e}")
                continue
        
        if stock is None or hist_5d is None or hist_5d.empty:
            return {
                "success": False,
                "error": f"No data found for ticker {original_ticker}. Tried formats: {formatted_tickers}",
                "ticker": original_ticker
            }
        
        # Get 5-year history for chart
        try:
            hist_5y = stock.history(period="5y")
            logger.info(f"📈 Retrieved 5-year history: {len(hist_5y)} data points")
        except Exception as e:
            logger.warning(f"⚠️ Could not get 5-year data: {e}")
            hist_5y = hist_5d
        
        # Get current price (last close)
        current_price = round(float(hist_5d['Close'].iloc[-1]), 4)
        prev_close = round(float(hist_5d['Close'].iloc[-2]) if len(hist_5d) > 1 else current_price, 4)
        
        # Calculate change
        price_change = round(current_price - prev_close, 4)
        price_change_pct = round((price_change / prev_close) * 100, 2) if prev_close != 0 else 0
        
        # Prepare 5-year chart data (monthly samples)
        chart_data = []
        if hist_5y is not None and not hist_5y.empty:
            # Resample to monthly data to reduce size
            monthly_data = hist_5y.resample('M').agg({
                'Open': 'first',
                'High': 'max', 
                'Low': 'min',
                'Close': 'last',
                'Volume': 'sum'
            }).dropna()
            
            for date, row in monthly_data.iterrows():
                chart_data.append({
                    "date": date.strftime('%Y-%m-%d'),
                    "open": round(float(row['Open']), 4),
                    "high": round(float(row['High']), 4),
                    "low": round(float(row['Low']), 4),
                    "close": round(float(row['Close']), 4),
                    "volume": int(row['Volume']) if not pd.isna(row['Volume']) else 0
                })
        
        # Extract comprehensive information
        stock_data = {
            "success": True,
            "ticker": ticker,
            "original_ticker": original_ticker,
            "company_name": info.get("longName", info.get("shortName", ticker)),
            "current_price": current_price,
            "previous_close": prev_close,
            "price_change": price_change,
            "price_change_pct": price_change_pct,
            "currency": info.get("currency", "USD"),
            
            # Market Data
            "market_cap": info.get("marketCap"),
            "enterprise_value": info.get("enterpriseValue"),
            "volume": int(hist_5d['Volume'].iloc[-1]) if not hist_5d['Volume'].empty else None,
            "avg_volume": info.get("averageVolume"),
            "day_high": info.get("dayHigh"),
            "day_low": info.get("dayLow"),
            "day_range": info.get("regularMarketDayRange"),
            
            # Valuation Metrics
            "pe_ratio": info.get("trailingPE"),
            "forward_pe": info.get("forwardPE"),
            "peg_ratio": info.get("trailingPegRatio"),
            "price_to_book": info.get("priceToBook"),
            "price_to_sales": info.get("priceToSalesTrailing12Months"),
            "enterprise_to_ebitda": info.get("enterpriseToEbitda"),
            "enterprise_to_revenue": info.get("enterpriseToRevenue"),
            
            # Financial Health
            "debt_to_equity": info.get("debtToEquity"),
            "current_ratio": info.get("currentRatio"),
            "quick_ratio": info.get("quickRatio"),
            "return_on_equity": info.get("returnOnEquity"),
            "return_on_assets": info.get("returnOnAssets"),
            "profit_margins": info.get("profitMargins"),
            "operating_margins": info.get("operatingMargins"),
            "gross_margins": info.get("grossMargins"),
            
            # Dividends
            "dividend_yield": info.get("dividendYield"),
            "dividend_rate": info.get("dividendRate"),
            "trailing_annual_dividend_yield": info.get("trailingAnnualDividendYield"),
            "trailing_annual_dividend_rate": info.get("trailingAnnualDividendRate"),
            "payout_ratio": info.get("payoutRatio"),
            "five_year_avg_dividend_yield": info.get("fiveYearAvgDividendYield"),
            "ex_dividend_date": info.get("exDividendDate"),
            "last_dividend_value": info.get("lastDividendValue"),
            
            # Growth & Performance
            "revenue_growth": info.get("revenueGrowth"),
            "earnings_growth": info.get("earningsGrowth"),
            "earnings_quarterly_growth": info.get("earningsQuarterlyGrowth"),
            "week_52_change": info.get("52WeekChange"),
            "week_52_high": info.get("fiftyTwoWeekHigh"),
            "week_52_low": info.get("fiftyTwoWeekLow"),
            "week_52_range": info.get("fiftyTwoWeekRange"),
            
            # Moving Averages
            "fifty_day_average": info.get("fiftyDayAverage"),
            "two_hundred_day_average": info.get("twoHundredDayAverage"),
            "fifty_day_change": info.get("fiftyDayAverageChange"),
            "two_hundred_day_change": info.get("twoHundredDayAverageChange"),
            
            # Analyst Data
            "recommendation_mean": info.get("recommendationMean"),
            "recommendation_key": info.get("recommendationKey"),
            "number_of_analyst_opinions": info.get("numberOfAnalystOpinions"),
            "target_high_price": info.get("targetHighPrice"),
            "target_low_price": info.get("targetLowPrice"),
            "target_mean_price": info.get("targetMeanPrice"),
            "target_median_price": info.get("targetMedianPrice"),
            
            # Company Info
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "exchange": info.get("exchange"),
            "country": info.get("country"),
            "website": info.get("website"),
            "business_summary": info.get("longBusinessSummary"),
            "full_time_employees": info.get("fullTimeEmployees"),
            
            # Financial Fundamentals
            "total_revenue": info.get("totalRevenue"),
            "total_cash": info.get("totalCash"),
            "total_debt": info.get("totalDebt"),
            "total_cash_per_share": info.get("totalCashPerShare"),
            "book_value": info.get("bookValue"),
            "shares_outstanding": info.get("sharesOutstanding"),
            "float_shares": info.get("floatShares"),
            "held_percent_institutions": info.get("heldPercentInstitutions"),
            "held_percent_insiders": info.get("heldPercentInsiders"),
            
            # Risk Metrics
            "beta": info.get("beta"),
            "implied_shares_outstanding": info.get("impliedSharesOutstanding"),
            
            # Technical Data
            "chart_data": chart_data,
            "chart_data_points": len(chart_data),
            "last_updated": datetime.now().isoformat()
        }
        
        logger.info(f"✅ Successfully fetched data for {ticker}: ${current_price}")
        return stock_data
        
    except Exception as e:
        logger.error(f"❌ Error fetching stock data for {ticker}: {e}")
        return {
            "success": False,
            "error": str(e),
            "ticker": ticker
        }

@app.post("/api/upload/bulk")
async def upload_bulk_files(
    files: List[UploadFile] = File(...),
    company_ticker: str = Form(...)
):
    """
    Upload multiple files for bulk analysis using Google Gemini API
    """
    try:
        logger.info(f"📂 Bulk file upload initiated for {company_ticker}: {len(files)} files")
        
        # Validate bulk processor is ready
        if not bulk_processor.model:
            raise HTTPException(status_code=500, detail="Bulk analysis system not properly initialized")
        
        # Start bulk analysis process
        session_id = await bulk_processor.start_bulk_analysis(files, company_ticker)
        
        return {
            "success": True,
            "session_id": session_id,
            "message": f"Bulk analysis started for {len(files)} files",
            "company_ticker": company_ticker,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Bulk upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/upload/status/{session_id}")
async def get_upload_status(session_id: str):
    """
    Get the status of a bulk file analysis session
    """
    try:
        session = await bulk_processor.get_session_status(session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {
            "success": True,
            "session_id": session_id,
            "status": session.status,
            "company_ticker": session.company_ticker,
            "total_files": session.total_files,
            "processed_files": session.processed_files,
            "error_message": session.error_message,
            "timestamp": session.upload_timestamp.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Status check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/upload/results/{session_id}")
async def get_upload_results(session_id: str):
    """
    Get the analysis results from a completed bulk file analysis session
    """
    try:
        session = await bulk_processor.get_session_status(session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if session.status != "completed":
            return {
                "success": False,
                "message": f"Analysis not completed. Status: {session.status}",
                "session_id": session_id
            }
        
        # Get formatted summary for analysts
        analyst_summary = bulk_processor.get_file_summary_for_analysts(session_id)
        
        return {
            "success": True,
            "session_id": session_id,
            "company_ticker": session.company_ticker,
            "analysis_results": {
                "consolidated_summary": session.consolidated_summary,
                "file_results": [
                    {
                        "filename": result.filename,
                        "file_type": result.file_type,
                        "analysis_summary": result.analysis_summary,
                        "key_insights": result.key_insights,
                        "financial_metrics": result.financial_metrics,
                        "risk_factors": result.risk_factors,
                        "confidence_score": result.confidence_score
                    }
                    for result in session.file_results
                ],
                "analyst_formatted_summary": analyst_summary
            },
            "timestamp": session.upload_timestamp.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Results retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/upload/session/{session_id}")
async def cleanup_upload_session(session_id: str):
    """
    Clean up a bulk file analysis session and associated files
    """
    try:
        session = await bulk_processor.get_session_status(session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Cleanup session files
        await bulk_processor.cleanup_session_files(session_id)
        
        # Remove from active sessions
        if session_id in bulk_processor.active_sessions:
            del bulk_processor.active_sessions[session_id]
        
        return {
            "success": True,
            "message": f"Session {session_id} cleaned up successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Session cleanup failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def handle_bulk_analysis_streaming(websocket: WebSocket, connection_id: str, message: Dict):
    """Handle bulk file analysis with real-time streaming"""
    
    try:
        files_data = message.get('files_data', [])
        company_ticker = message.get('company_ticker', '')
        
        if not files_data or not company_ticker:
            await websocket.send_text(json.dumps({
                "type": "bulk_analysis_error",
                "data": {"error": "Missing files or company ticker"}
            }))
            return
        
        logger.info(f"🗂️ Starting bulk analysis streaming for {connection_id}: {len(files_data)} files")
        
        # Note: API key validation now handled by intelligent key system in bulk processor
        
        # Send initial confirmation
        await websocket.send_text(json.dumps({
            "type": "bulk_analysis_initiated",
            "data": {
                "connection_id": connection_id,
                "company_ticker": company_ticker,
                "file_count": len(files_data),
                "message": "Bulk analysis started with real-time streaming"
            }
        }))
        
        # Convert file data to UploadFile objects for processing
        from fastapi import UploadFile
        import io
        import base64
        
        upload_files = []
        for file_data in files_data:
            file_content = base64.b64decode(file_data['content'])
            file_obj = UploadFile(
                filename=file_data['filename'],
                file=io.BytesIO(file_content)
            )
            upload_files.append(file_obj)
        
        # Start streaming analysis
        session_id = await bulk_processor.start_bulk_analysis(
            upload_files, 
            company_ticker, 
            websocket=websocket
        )
        
        # Check if analysis actually succeeded
        session = await bulk_processor.get_session_status(session_id)
        if session and session.status == "failed":
            # Analysis failed, send error instead of completion
            await websocket.send_text(json.dumps({
                "type": "bulk_analysis_error",
                "data": {
                    "error": session.error_message or "Analysis failed with unknown error",
                    "error_type": "analysis_failed",
                    "session_id": session_id
                }
            }))
        else:
            # Send completion
            await websocket.send_text(json.dumps({
                "type": "bulk_analysis_completed",
                "data": {
                    "session_id": session_id,
                    "message": "Bulk analysis completed successfully",
                    "timestamp": datetime.now().isoformat()
                }
            }))
        
    except Exception as e:
        logger.error(f"❌ Bulk analysis streaming error for {connection_id}: {e}")
        await websocket.send_text(json.dumps({
            "type": "bulk_analysis_error",
            "data": {
                "error": f"Bulk analysis failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
        }))

def find_available_port(preferred_port=8005, max_attempts=10):
    """Find an available port starting from preferred_port"""
    import socket
    
    for port in range(preferred_port, preferred_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                return port
        except OSError:
            continue
    
    raise Exception(f"No available ports found in range {preferred_port}-{preferred_port + max_attempts - 1}")

def main():
    """Main application entry point"""
    logger.info("🚀 Starting Robeco Ultra-Sophisticated Professional Streaming Server")
    logger.info("🧠 Sequential Intelligence Multi-Agent Architecture")
    logger.info("🔧 Cross-agent synthesis with maximum AI utilization")
    logger.info("📊 Professional-grade streaming reports with Google Search grounding")
    
    # Find available port, preferring 8005
    try:
        port = find_available_port(8005)
        logger.info(f"🌐 Server will be available at: http://127.0.0.1:{port}")
        
        if port != 8005:
            logger.info(f"💡 Port 8005 was busy, using port {port} instead")
        
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=port,
            log_level="info",
            access_log=True,
            ws_ping_interval=30,
            ws_ping_timeout=10
        )
    except Exception as e:
        logger.error(f"❌ Server startup failed: {e}")
        raise

if __name__ == "__main__":
    main()