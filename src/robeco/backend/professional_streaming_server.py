#!/usr/bin/env python3
"""
Robeco Professional Streaming Server
Ultra-sophisticated real-time streaming server for investment analysis
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Set, Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from typing import List
import uvicorn
import sys
import os
from pathlib import Path
import yfinance as yf
import pandas as pd

# Add project root to path and set working directory
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
os.chdir(str(project_root))

from robeco.backend.ultra_sophisticated_multi_agent_engine import (
    ultra_sophisticated_engine,
    AnalysisContext,
    AnalysisPhase
)

# Import bulk file processor
from robeco.backend.bulk_file_processor import bulk_processor, BulkAnalysisSession

# Import template report generator
from robeco.backend.template_report_generator import template_report_generator

# Import Word report generator
from robeco.backend.word_report_generator import word_report_generator
# Import Enhanced PDF service
from robeco.backend.enhanced_pdf_service import EnhancedPdfService

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

# Session-isolated WebSocket connections and data
active_connections: Dict[str, WebSocket] = {}  # session_id -> websocket
session_data: Dict[str, Dict] = {}  # session_id -> {connection_id, start_time, client_info, etc}
connection_counter = 0
chat_sessions: Dict[str, Dict] = {}  # session_id -> {analyst -> chat_history}
session_projects: Dict[str, Dict] = {}  # session_id -> project_data
session_analyses: Dict[str, Dict] = {}  # session_id -> {analysis_id -> analysis_data}

# Document conversion request model
class DocumentConversionRequest(BaseModel):
    html_content: str
    company_name: str
    ticker: str
    format: str  # "word" or "pdf"

# Enhanced PDF service - no lazy loading needed (static methods)
def get_pdf_generator():
    """Return the EnhancedPdfService for PDF generation"""
    try:
        # EnhancedPdfService uses static methods, so just return the class
        logger.info("✅ PDF generator initialized successfully")
        logger.info("📍 Using PDF engine: Enhanced Puppeteer Service")
        return EnhancedPdfService
    except Exception as e:
        logger.error(f"❌ PDF generator initialization failed: {e}")
        raise RuntimeError(f"PDF generation unavailable: {e}")

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
    """Professional WebSocket endpoint for real-time analysis streaming with session isolation"""
    global connection_counter
    connection_counter += 1
    temp_connection_id = f"robeco_client_{connection_counter}"
    
    await websocket.accept()
    
    # Wait for session initialization message
    session_id = None
    connection_id = None
    
    logger.info(f"🔗 New professional connection: {temp_connection_id} (waiting for session init)")
    
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
            
            # Handle session initialization first
            if message_type == 'session_init' and session_id is None:
                session_id = message.get('data', {}).get('session_id')
                connection_id = message.get('data', {}).get('connection_id', temp_connection_id)
                
                if session_id:
                    # Register session-isolated connection
                    active_connections[session_id] = websocket
                    session_data[session_id] = {
                        'connection_id': connection_id,
                        'start_time': message.get('data', {}).get('start_time'),
                        'client_info': message.get('data', {}).get('client_info', {}),
                        'temp_connection_id': temp_connection_id
                    }
                    
                    # Initialize session-specific data stores
                    if session_id not in chat_sessions:
                        chat_sessions[session_id] = {}
                    if session_id not in session_projects:
                        session_projects[session_id] = {}
                    if session_id not in session_analyses:
                        session_analyses[session_id] = {}
                    
                    logger.info(f"🆔 Session {session_id} initialized for connection {connection_id}")
                    
                    # Send confirmation
                    await websocket.send_text(json.dumps({
                        "type": "session_confirmed",
                        "data": {
                            "session_id": session_id,
                            "connection_id": connection_id,
                            "message": "Session isolation activated"
                        }
                    }))
                continue
            
            # Skip processing if session not initialized
            if session_id is None:
                logger.warning(f"⚠️ Message {message_type} received before session initialization")
                continue
                
            logger.info(f"📨 Message from session {session_id}: {message_type}")
            
            # IMPORTANT: Log the EXACT message structure for debugging
            logger.info(f"🔍 EXACT MESSAGE DEBUG: {json.dumps(message, indent=2, default=str)[:500]}...")
            
            # IMMEDIATE ACKNOWLEDGMENT for generate_report
            if message_type == 'generate_report':
                logger.info(f"🎯 GENERATE_REPORT MESSAGE RECEIVED! Sending immediate acknowledgment...")
                await websocket.send_text(json.dumps({
                    "type": "generate_report_acknowledged", 
                    "data": {
                        "message": "📝 Report generation request received and processing...",
                        "connection_id": connection_id,
                        "timestamp": datetime.now().isoformat()
                    }
                }))
            
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
            
            elif message_type == 'generate_report':
                # Handle report generation request
                await handle_report_generation(websocket, connection_id, message)
            
            elif message_type == 'generate_word_report':
                # Handle Word document generation request
                await handle_word_report_generation(websocket, connection_id, message)
            
            elif message_type == 'ping':
                # Handle ping for connection health
                await websocket.send_text(json.dumps({
                    "type": "pong",
                    "data": {"timestamp": datetime.now().isoformat()}
                }))
            
            else:
                logger.warning(f"⚠️ Unhandled message type: {message_type}")
                
    except WebSocketDisconnect:
        # Clean up session-based data
        if session_id:
            active_connections.pop(session_id, None)
            session_data.pop(session_id, None)
            session_projects.pop(session_id, None)
            session_analyses.pop(session_id, None)
            chat_sessions.pop(session_id, None)
            logger.info(f"❌ Session {session_id} disconnected and cleaned up")
        else:
            logger.info(f"❌ Connection {temp_connection_id} closed (no session)")
        
    except Exception as e:
        logger.error(f"❌ WebSocket error for session {session_id or temp_connection_id}: {e}")
        if session_id:
            active_connections.pop(session_id, None)

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
        
        # Fetch complete 3-statements for comprehensive analysis
        try:
            logger.info(f"📊 Fetching complete 3-statements for {working_ticker}")
            
            # Income Statement (annual and quarterly)
            try:
                income_stmt_annual = stock.financials  # Annual income statement
                income_stmt_quarterly = stock.quarterly_financials  # Quarterly income statement
                
                if not income_stmt_annual.empty:
                    # Convert Timestamp columns to strings for JSON serialization
                    income_annual_dict = income_stmt_annual.to_dict()
                    income_annual_clean = {}
                    for date_key, values in income_annual_dict.items():
                        date_str = date_key.strftime('%Y-%m-%d') if hasattr(date_key, 'strftime') else str(date_key)
                        income_annual_clean[date_str] = values
                    stock_data["income_statement_annual"] = income_annual_clean
                    logger.info(f"✅ Annual Income Statement: {len(income_stmt_annual.columns)} periods, {len(income_stmt_annual.index)} line items")
                
                if not income_stmt_quarterly.empty:
                    # Convert Timestamp columns to strings for JSON serialization
                    income_quarterly_dict = income_stmt_quarterly.to_dict()
                    income_quarterly_clean = {}
                    for date_key, values in income_quarterly_dict.items():
                        date_str = date_key.strftime('%Y-%m-%d') if hasattr(date_key, 'strftime') else str(date_key)
                        income_quarterly_clean[date_str] = values
                    stock_data["income_statement_quarterly"] = income_quarterly_clean
                    logger.info(f"✅ Quarterly Income Statement: {len(income_stmt_quarterly.columns)} periods, {len(income_stmt_quarterly.index)} line items")
                    
            except Exception as e:
                logger.warning(f"⚠️ Income Statement fetch failed: {e}")
            
            # Balance Sheet (annual and quarterly)
            try:
                balance_sheet_annual = stock.balance_sheet  # Annual balance sheet
                balance_sheet_quarterly = stock.quarterly_balance_sheet  # Quarterly balance sheet
                
                if not balance_sheet_annual.empty:
                    # Convert Timestamp columns to strings for JSON serialization
                    balance_annual_dict = balance_sheet_annual.to_dict()
                    balance_annual_clean = {}
                    for date_key, values in balance_annual_dict.items():
                        date_str = date_key.strftime('%Y-%m-%d') if hasattr(date_key, 'strftime') else str(date_key)
                        balance_annual_clean[date_str] = values
                    stock_data["balance_sheet_annual"] = balance_annual_clean
                    logger.info(f"✅ Annual Balance Sheet: {len(balance_sheet_annual.columns)} periods, {len(balance_sheet_annual.index)} line items")
                
                if not balance_sheet_quarterly.empty:
                    # Convert Timestamp columns to strings for JSON serialization
                    balance_quarterly_dict = balance_sheet_quarterly.to_dict()
                    balance_quarterly_clean = {}
                    for date_key, values in balance_quarterly_dict.items():
                        date_str = date_key.strftime('%Y-%m-%d') if hasattr(date_key, 'strftime') else str(date_key)
                        balance_quarterly_clean[date_str] = values
                    stock_data["balance_sheet_quarterly"] = balance_quarterly_clean
                    logger.info(f"✅ Quarterly Balance Sheet: {len(balance_sheet_quarterly.columns)} periods, {len(balance_sheet_quarterly.index)} line items")
                    
            except Exception as e:
                logger.warning(f"⚠️ Balance Sheet fetch failed: {e}")
            
            # Cash Flow Statement (annual and quarterly)
            try:
                cashflow_annual = stock.cashflow  # Annual cash flow statement
                cashflow_quarterly = stock.quarterly_cashflow  # Quarterly cash flow statement
                
                if not cashflow_annual.empty:
                    # Convert Timestamp columns to strings for JSON serialization
                    cashflow_annual_dict = cashflow_annual.to_dict()
                    cashflow_annual_clean = {}
                    for date_key, values in cashflow_annual_dict.items():
                        date_str = date_key.strftime('%Y-%m-%d') if hasattr(date_key, 'strftime') else str(date_key)
                        cashflow_annual_clean[date_str] = values
                    stock_data["cashflow_annual"] = cashflow_annual_clean
                    logger.info(f"✅ Annual Cash Flow: {len(cashflow_annual.columns)} periods, {len(cashflow_annual.index)} line items")
                
                if not cashflow_quarterly.empty:
                    # Convert Timestamp columns to strings for JSON serialization
                    cashflow_quarterly_dict = cashflow_quarterly.to_dict()
                    cashflow_quarterly_clean = {}
                    for date_key, values in cashflow_quarterly_dict.items():
                        date_str = date_key.strftime('%Y-%m-%d') if hasattr(date_key, 'strftime') else str(date_key)
                        cashflow_quarterly_clean[date_str] = values
                    stock_data["cashflow_quarterly"] = cashflow_quarterly_clean
                    logger.info(f"✅ Quarterly Cash Flow: {len(cashflow_quarterly.columns)} periods, {len(cashflow_quarterly.index)} line items")
                    
            except Exception as e:
                logger.warning(f"⚠️ Cash Flow Statement fetch failed: {e}")
            
            # Additional financial metrics - handle deprecation warnings
            try:
                # Revenue and earnings from income statement (more reliable)
                if "income_statement_annual" in stock_data:
                    logger.info(f"✅ Earnings data available from Income Statement")
                else:
                    logger.warning(f"⚠️ Using fallback earnings data method")
                    
            except Exception as e:
                logger.warning(f"⚠️ Earnings data processing failed: {e}")
            
            # Additional key financial ratios and metrics
            try:
                # Key financial metrics that may not be in basic info
                additional_metrics = {
                    "beta": info.get("beta"),
                    "dividend_yield": info.get("dividendYield"),
                    "payout_ratio": info.get("payoutRatio"),
                    "book_value": info.get("bookValue"),
                    "price_to_book": info.get("priceToBook"),
                    "trailing_eps": info.get("trailingEps"),
                    "forward_eps": info.get("forwardEps"),
                    "revenue_per_share": info.get("revenuePerShare"),
                    "free_cashflow": info.get("freeCashflow"),
                    "operating_cashflow": info.get("operatingCashflow"),
                    "revenue_growth": info.get("revenueGrowth"),
                    "earnings_growth": info.get("earningsGrowth")
                }
                
                # Add non-null additional metrics
                for key, value in additional_metrics.items():
                    if value is not None:
                        stock_data[f"additional_{key}"] = value
                        
                logger.info(f"✅ Additional financial metrics: {len([v for v in additional_metrics.values() if v is not None])} metrics")
                    
            except Exception as e:
                logger.warning(f"⚠️ Additional metrics fetch failed: {e}")
            
            # Historical price data for comprehensive analysis
            try:
                # 5-year historical data
                hist_5y = stock.history(period="5y")
                if not hist_5y.empty:
                    # Convert Timestamp index to strings for JSON serialization
                    hist_5y_dict = hist_5y.to_dict()
                    hist_5y_clean = {}
                    for column, values in hist_5y_dict.items():
                        clean_values = {}
                        for date_key, value in values.items():
                            date_str = date_key.strftime('%Y-%m-%d') if hasattr(date_key, 'strftime') else str(date_key)
                            clean_values[date_str] = value
                        hist_5y_clean[column] = clean_values
                    stock_data["price_history_5y"] = hist_5y_clean
                    logger.info(f"✅ 5-Year Price History: {len(hist_5y)} trading days")
                    
            except Exception as e:
                logger.warning(f"⚠️ Price history fetch failed: {e}")
                
            logger.info(f"🎯 Complete financial dataset prepared: {len(stock_data)} total fields including 3-statements")
            
        except Exception as e:
            logger.error(f"❌ Error fetching 3-statements: {e}")
        
        # Clean NaN values before JSON serialization
        def clean_nan_values(obj):
            """Recursively clean NaN/inf values from nested dictionaries and lists"""
            import math
            if isinstance(obj, dict):
                return {k: clean_nan_values(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [clean_nan_values(item) for item in obj]
            elif isinstance(obj, float):
                if math.isnan(obj) or math.isinf(obj):
                    return None
                return obj
            else:
                return obj
        
        clean_stock_data = clean_nan_values(stock_data)
        return {"success": True, "data": clean_stock_data}
        
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
        data_sources = message.get('data_sources', {})
        
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
            stock_data=stock_data,  # Feed complete yfinance data to all agents
            data_sources=data_sources  # Pass user context data to all agents
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
                
                # COMPREHENSIVE WEBSOCKET STREAMING DEBUG TRACE
                logger.info(f"🔍 *** WEBSOCKET STREAMING SERVER DEBUG TRACE START ***")
                logger.info(f"   📨 Update received at: {datetime.now().isoformat()}")
                logger.info(f"   📊 Update keys: {list(update.keys())}")
                logger.info(f"   📊 Update data keys: {list(update.get('data', {}).keys())}")
                
                # Check content before any processing
                raw_content = update['data'].get('content_complete', '')
                raw_citations_count = update['data'].get('citations_count', 0)
                
                import re
                citations_in_raw = re.findall(r'\[(\d+)\]', raw_content)
                logger.info(f"   📚 Citations in raw content from agent: {len(citations_in_raw)} patterns: {citations_in_raw[:10]}")
                logger.info(f"   📄 Raw content preview (first 300): {raw_content[:300]}")
                logger.info(f"   📄 Raw content preview (last 300): {raw_content[-300:]}")
                
                if len(citations_in_raw) == 0 and raw_citations_count > 0:
                    logger.error(f"   ❌ CRITICAL: Agent claims {raw_citations_count} citations but content has NONE!")
                elif len(citations_in_raw) != raw_citations_count:
                    logger.warning(f"   ⚠️ Citation count mismatch: found {len(citations_in_raw)}, expected {raw_citations_count}")
                
                # Sample content at different positions to verify citation distribution
                content_samples = []
                for pos in [0, len(raw_content)//4, len(raw_content)//2, 3*len(raw_content)//4, max(0, len(raw_content)-500)]:
                    if pos < len(raw_content):
                        sample = raw_content[pos:pos+100].replace('\n', '\\n')
                        sample_citations = len(re.findall(r'\[(\d+)\]', sample))
                        if sample_citations > 0:
                            content_samples.append(f"pos {pos}: {sample_citations} citations in '{sample[:50]}...'")
                logger.info(f"   📍 Content distribution samples: {content_samples}")
                
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
                    
                    # VERIFY CITATIONS IN SAFE MESSAGE
                    citations_in_safe = re.findall(r'\[(\d+)\]', safe_message['data']['content_complete'])
                    logger.info(f"   🔧 Citations in safe_message: {len(citations_in_safe)} patterns: {citations_in_safe[:10]}")
                    
                    if len(citations_in_safe) != len(citations_in_raw):
                        logger.error(f"   ❌ CITATIONS LOST IN SAFE MESSAGE CREATION: {len(citations_in_raw)} → {len(citations_in_safe)}")
                    elif len(citations_in_safe) == 0:
                        logger.warning(f"   🔍 Safe message has NO citations - checking content cleaning...")
                        logger.info(f"   📄 Original length: {len(content_complete)}, Safe length: {len(safe_content)}")
                        logger.info(f"   📄 Content cleaning removed: {len(content_complete) - len(safe_content)} chars")
                    
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
                        
                        # DEBUG CHUNKED CITATIONS
                        total_chunked_citations = 0
                        for i, chunk in enumerate(content_chunks):
                            chunk_citations = len(re.findall(r'\[(\d+)\]', chunk))
                            total_chunked_citations += chunk_citations
                            if chunk_citations > 0:
                                logger.info(f"   📦 Chunk {i+1} has {chunk_citations} citations")
                        
                        logger.info(f"   📚 Total citations across all chunks: {total_chunked_citations}")
                        if total_chunked_citations != len(citations_in_safe):
                            logger.error(f"   ❌ CITATIONS LOST IN CHUNKING: {len(citations_in_safe)} → {total_chunked_citations}")
                        
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
                        logger.info(f"   📚 Chunked delivery sent {total_chunked_citations} citations to frontend")
                        logger.info(f"🔍 *** WEBSOCKET STREAMING SERVER DEBUG TRACE END (CHUNKED) ***")
                        
                    else:
                        # Standard single message delivery for smaller content
                        logger.info(f"🚀 WEBSOCKET: Sending standard message ({message_size} bytes)...")
                        
                        # FINAL WEBSOCKET SEND DEBUG
                        final_send_citations = re.findall(r'\[(\d+)\]', json_string)
                        logger.info(f"   📤 About to send WebSocket with {len(final_send_citations)} citations")
                        logger.info(f"   📄 JSON string preview: {json_string[:200]}...{json_string[-200:]}")
                        
                        await websocket.send_text(json_string)
                        
                        logger.info(f"✅ WEBSOCKET: streaming_ai_content_final message sent successfully ({len(json_string)} bytes)")
                        logger.info(f"   📚 WebSocket delivered {len(final_send_citations)} citations to frontend")
                        logger.info(f"🔍 *** WEBSOCKET STREAMING SERVER DEBUG TRACE END ***")
                    
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
                
            elif update['type'] == 'error_notification':
                # Handle retry and error notifications for frontend popup
                await websocket.send_text(json.dumps({
                    "type": "error_notification",
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
        
        # Try to get a working API key and generate response with retry logic
        try:
            logger.info(f"🔍 CHAT [{analyst_type}]: Starting chat API key system")
            
            # Send debug to frontend that we're starting
            await websocket.send_text(json.dumps({
                "type": "chat_debug",
                "data": {
                    "message": f"🔍 Starting chat system for {analyst_type}...",
                    "analyst": analyst_type,
                    "timestamp": datetime.now().isoformat()
                }
            }))
            
            from robeco.backend.api_key.gemini_api_key import get_intelligent_api_key
            logger.info(f"✅ CHAT [{analyst_type}]: Successfully imported API key system")
            
            # Send debug to frontend about successful import
            await websocket.send_text(json.dumps({
                "type": "chat_debug",
                "data": {
                    "message": f"✅ API key system imported successfully",
                    "analyst": analyst_type,
                    "timestamp": datetime.now().isoformat()
                }
            }))
            
            # Retry logic for API key (same as main analysis system - keep trying until successful)
            client = None
            api_key = None
            
            logger.info(f"🔑 CHAT [{analyst_type}]: Creating client (will retry until successful)")
            
            attempt = 0
            max_attempts = 100  # Reasonable limit to prevent infinite loop
            
            logger.info(f"🔄 CHAT [{analyst_type}]: Starting retry loop with max {max_attempts} attempts")
            
            # Send debug to frontend that retry loop is starting
            await websocket.send_text(json.dumps({
                "type": "chat_debug",
                "data": {
                    "message": f"🔄 Starting API key retry loop (max {max_attempts} attempts)",
                    "analyst": analyst_type,
                    "timestamp": datetime.now().isoformat()
                }
            }))
            
            while attempt < max_attempts:
                attempt += 1
                try:
                    api_key, key_info = get_intelligent_api_key(agent_type=analyst_type, attempt=attempt-1)
                    if not api_key:
                        logger.error(f"❌ CHAT No API key available on attempt {attempt}")
                        continue
                    
                    logger.info(f"🔑 CHAT [{analyst_type}]: Got API key {api_key[:8]}...{api_key[-4:]} | Key info: {key_info}")
                    
                    # Send debug info to frontend user
                    await websocket.send_text(json.dumps({
                        "type": "chat_debug",
                        "data": {
                            "message": f"🔑 Using API key {api_key[:8]}...{api_key[-4:]} (attempt {attempt})",
                            "analyst": analyst_type,
                            "key_info": key_info,
                            "timestamp": datetime.now().isoformat()
                        }
                    }))
                    
                    # Try to create client
                    client = genai.Client(api_key=api_key)
                    logger.info(f"✅ CHAT [{analyst_type}]: Client created successfully with API key {api_key[:8]}...{api_key[-4:]}")
                    
                    # Send success debug to frontend
                    await websocket.send_text(json.dumps({
                        "type": "chat_debug",
                        "data": {
                            "message": f"✅ Client created successfully with {key_info.get('source', 'unknown')} key",
                            "analyst": analyst_type,
                            "timestamp": datetime.now().isoformat()
                        }
                    }))
                    break
                    
                except Exception as client_error:
                    error_msg = str(client_error)
                    logger.warning(f"🔄 CHAT Key failed (attempt {attempt}), trying next: {error_msg[:100]}...")
                    
                    # Send API key failure debug to frontend user
                    await websocket.send_text(json.dumps({
                        "type": "chat_debug",
                        "data": {
                            "message": f"🔄 API key failed (attempt {attempt}): {error_msg[:50]}... Trying next key...",
                            "analyst": analyst_type,
                            "error": error_msg[:100],
                            "timestamp": datetime.now().isoformat()
                        }
                    }))
                    
                    continue  # Try next key
            
            # If we get here, all 100 attempts failed
            if not client:
                error_msg = f"🚨 ALL API KEYS EXHAUSTED: Tried {max_attempts} attempts across all available keys"
                logger.error(f"❌ {error_msg}")
                
                # Notify frontend user about API key problem
                await websocket.send_text(json.dumps({
                    "type": "chat_debug",
                    "data": {
                        "message": f"🚨 All {max_attempts} API keys failed! Please add working keys to primary_gemini_key.txt",
                        "analyst": analyst_type,
                        "severity": "critical",
                        "action_needed": "Add working API keys",
                        "timestamp": datetime.now().isoformat()
                    }
                }))
                
                raise Exception(error_msg)
            
            # Generate sophisticated portfolio manager discussion response
            generate_config = types.GenerateContentConfig(
                temperature=0.15,  # Lower for more focused, consistent institutional dialogue
                top_p=0.85,
                max_output_tokens=65536,  # Maximum tokens for complete analysis without truncation
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
                    "error": f"🚨 Chat API Key System Failure: All 100 retry attempts exhausted. Please check API key configuration and quota limits.",
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
        
        # Clean NaN values before returning
        def clean_nan_values(obj):
            """Recursively clean NaN/inf values from nested dictionaries and lists"""
            import math
            if isinstance(obj, dict):
                return {k: clean_nan_values(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [clean_nan_values(item) for item in obj]
            elif isinstance(obj, float):
                if math.isnan(obj) or math.isinf(obj):
                    return None
                return obj
            else:
                return obj
        
        clean_stock_data = clean_nan_values(stock_data)
        logger.info(f"✅ Successfully fetched data for {ticker}: ${current_price}")
        return clean_stock_data
        
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

@app.post("/api/professional/convert")
async def convert_html_to_document(request: DocumentConversionRequest):
    """Convert HTML report to Word document or PDF"""
    try:
        logger.info(f"🔄 Converting HTML to {request.format.upper()}: {request.ticker}")
        
        if request.format.lower() == "word":
            # Convert to Word document
            output_path = await word_report_generator.convert_html_to_word(
                html_content=request.html_content,
                company_name=request.company_name,
                ticker=request.ticker
            )
            
            return {
                "status": "success",
                "format": "word",
                "file_path": output_path,
                "message": f"Word document generated successfully for {request.ticker}",
                "download_available": True
            }
            
        elif request.format.lower() == "pdf":
            # Convert to PDF document using EnhancedPdfService
            try:
                pdf_gen = get_pdf_generator()  # Returns EnhancedPdfService class
                
                # Generate PDF using the EnhancedPdfService static method
                pdf_data = pdf_gen.generate_pdf_from_html(
                    html_content=request.html_content,
                    project_id=request.ticker,
                    settings=None
                )
                
                # Save PDF to temporary file for download
                import tempfile
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_ticker = request.ticker.replace('.', '_').replace(':', '_')
                filename = f"{safe_ticker}_Investment_Report_{timestamp}.pdf"
                output_path = os.path.join(tempfile.gettempdir(), filename)
                
                with open(output_path, 'wb') as f:
                    f.write(pdf_data)
                
            except RuntimeError as e:
                raise HTTPException(
                    status_code=503,
                    detail=str(e)
                )
            
            return {
                "status": "success", 
                "format": "pdf",
                "file_path": output_path,
                "message": f"PDF document generated successfully for {request.ticker}",
                "download_available": True
            }
        else:
            raise HTTPException(status_code=400, detail="Invalid format. Use 'word' or 'pdf'")
            
    except Exception as e:
        logger.error(f"Document conversion failed: {e}")
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")

@app.get("/api/download/word")
async def download_word_document(file_path: str):
    """
    Download generated Word document
    """
    try:
        import os
        from fastapi.responses import FileResponse
        from pathlib import Path
        
        # Validate file path and existence
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        if not file_path_obj.suffix.lower() == '.docx':
            raise HTTPException(status_code=400, detail="Invalid file type")
        
        # Security check - ensure file is in expected directory
        if not str(file_path_obj).startswith('/tmp/'):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Generate appropriate filename
        filename = file_path_obj.name
        
        logger.info(f"📥 Serving Word document download: {filename}")
        
        return FileResponse(
            path=str(file_path_obj),
            filename=filename,
            media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Word download failed: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Download failed: {e}"
        )

@app.get("/api/download/pdf")
async def download_pdf_document(file_path: str):
    """
    Download generated PDF document
    """
    try:
        import os
        import tempfile
        from fastapi.responses import FileResponse
        from pathlib import Path
        
        # Validate file path and existence
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        if not file_path_obj.suffix.lower() == '.pdf':
            raise HTTPException(status_code=400, detail="Invalid file type")
        
        # Security check - ensure file is in expected temporary directory
        temp_dirs = ['/tmp/', '/var/folders/', tempfile.gettempdir()]
        is_valid_temp = any(str(file_path_obj).startswith(temp_dir) for temp_dir in temp_dirs)
        if not is_valid_temp:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Generate appropriate filename
        filename = file_path_obj.name
        
        logger.info(f"📥 Serving PDF document download: {filename}")
        
        return FileResponse(
            path=str(file_path_obj),
            filename=filename,
            media_type='application/pdf'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ PDF download failed: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Download failed: {e}"
        )

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

async def _build_enhanced_report_prompt(
    company_name: str,
    ticker: str, 
    analyses_data: Dict[str, Any],
    template_content: str,
    report_focus: str = "comprehensive"
) -> str:
    """Build enhanced prompt with all analyst outputs and template example"""
    
    # Extract analysis content from each agent
    agent_analyses = []
    for agent_type, analysis in analyses_data.items():
        if analysis and analysis.get('content'):
            agent_analyses.append({
                'agent_type': agent_type,
                'content': analysis['content'],
                'timestamp': analysis.get('timestamp', '')
            })
    
    # Build comprehensive prompt with template example and all analyst outputs
    prompt = f"""
# ROBECO INVESTMENT REPORT CONTENT GENERATION

You are generating ONLY THE CONTENT PART of a professional investment report for **{company_name} ({ticker})**.

## CRITICAL: CSS IS 100% FIXED - NO STYLING ALLOWED

We already have 100% fixed CSS code at 'Report Example/CSScode.txt'. 
**ABSOLUTELY NO CSS, STYLING, OR INLINE STYLES ALLOWED.**
**GENERATE ONLY PURE HTML CONTENT WITH CLASS NAMES - NO STYLE ATTRIBUTES.**

**FORBIDDEN - DO NOT GENERATE:**
- NO `style="..."` attributes anywhere
- NO CSS styling code
- NO color definitions  
- NO inline styling
- NO `<style>` tags
- NO styling properties

**ALLOWED - ONLY GENERATE:**
- Pure HTML content with class names
- Text content and data
- HTML structure using existing classes

## ONE-SHOT TEMPLATE EXAMPLE

Here is the complete Robeco Investment Case Template showing the structure you should follow for content organization:

```html
{template_content}
```

**EXTRACT ONLY THE CONTENT STRUCTURE** from this template (ignore all CSS/styling) and generate similar content for {company_name}.

## ALL SPECIALIST ANALYST OUTPUTS

You have comprehensive analysis from {len(agent_analyses)} specialist analysts. Use ALL of these outputs to generate thorough, well-informed content:

"""
    
    # Add each agent analysis with full content
    for i, analysis in enumerate(agent_analyses, 1):
        prompt += f"""
### {i}. {analysis['agent_type'].upper()} SPECIALIST ANALYSIS:

**Generated:** {analysis['timestamp']}

**FULL ANALYSIS CONTENT:**
```
{analysis['content']}
```

---

"""
    
    prompt += f"""

## GENERATION REQUIREMENTS

**CRITICAL INSTRUCTIONS:**
1. **CONTENT ONLY:** Generate ONLY the HTML content (body content), NO CSS, NO HTML headers, NO styling
2. **Follow Content Structure:** Use the template's content organization and structure  
3. **Integrate ALL Analyst Outputs:** Synthesize insights from all {len(agent_analyses)} specialist analyses
4. **Professional Language:** Maintain Robeco's institutional investment research style
5. **Accurate Data:** Use only data and insights from the provided analyst outputs

**WHAT TO GENERATE:**
- Start with: `<div class="presentation-container">`
- Generate all slide content using template structure
- End with: `</div>`
- Include company metrics, analysis sections, charts, recommendations
- Use class names from template but DO NOT include any CSS

**WHAT NOT TO GENERATE:**
- NO CSS styling code
- NO `<html>`, `<head>`, `<style>` tags  
- NO styling definitions
- NO `<!DOCTYPE html>`

**EXAMPLE OUTPUT FORMAT:**
```html
<div class="presentation-container">
    <div class="slide">
        <div class="slide-content">
            <!-- Your generated content here -->
        </div>
    </div>
    <!-- More slides with content -->
</div>
```

Generate the complete investment report CONTENT now, incorporating all analyst insights and following the template content structure exactly. Remember: CONTENT ONLY, NO CSS!
"""
    
    return prompt


async def _generate_template_guided_content(prompt: str) -> str:
    """Generate ONLY content using AI with template guidance and all analyst outputs"""
    
    try:
        logger.info(f"🤖 Generating content-only with enhanced prompt ({len(prompt)} chars)")
        
        # Use the ultra sophisticated engine for content generation
        from robeco.backend.ultra_sophisticated_multi_agent_engine import ultra_sophisticated_engine
        
        # Create context for content generation
        context = AnalysisContext(
            company_name="Content Generation",
            ticker="CONTENT",
            user_query=prompt,
            session_id=f"content_gen_{int(datetime.now().timestamp())}",
            start_time=datetime.now()
        )
        
        # Generate content using the sophisticated AI system
        # Extract the final content
        content = ""
        async for update in ultra_sophisticated_engine.generate_single_agent_analysis('anti_consensus', context):
            if update.get('type') == 'streaming_ai_content_final':
                content = update.get('data', {}).get('content_complete', '')
                break
            elif update.get('type') == 'streaming_ai_content':
                # Accumulate streaming content
                current_content = update.get('data', {}).get('content', '')
                if current_content:
                    content += current_content
        
        if not content:
            raise Exception("No content generated by AI system")
            
        logger.info(f"✅ AI content generated: {len(content)} characters")
        return content
        
    except Exception as e:
        logger.error(f"❌ AI content generation failed: {e}")
        raise e

async def handle_report_generation(websocket: WebSocket, connection_id: str, message: Dict):
    """Handle comprehensive AI investment report generation with streaming"""
    
    logger.info(f"🎯 ENTERED handle_report_generation function for {connection_id}")
    logger.info(f"🎯 Message keys: {list(message.keys())}")
    
    try:
        # Extract report parameters - they should be in message.data
        data = message.get('data', {})
        ticker = data.get('ticker', data.get('company_ticker', ''))
        company = data.get('company_name', data.get('company', ''))
        report_focus = data.get('report_focus', 'comprehensive')
        analyses_data = data.get('analyses_data', {})
        investment_objective = data.get('investment_objective', '')
        user_query = data.get('user_query', '')
        data_sources = data.get('data_sources', {})
        
        logger.info(f"📊 Starting report generation for {company} ({ticker}) - Focus: {report_focus}")
        logger.info(f"📋 Received analyses data: {list(analyses_data.keys()) if analyses_data else 'NONE'}")
        logger.info(f"🎯 Investment Objective: '{investment_objective}' | User Query: '{user_query}'")
        logger.info(f"📋 Message keys: {list(message.keys())}")
        logger.info(f"📋 Full message data keys: {list(message.get('data', {}).keys()) if message.get('data') else 'NO DATA KEY'}")
        logger.info(f"🔍 DEBUG: Full message structure: {json.dumps(message, indent=2, default=str)[:1000]}...")
        logger.info(f"🔍 DEBUG: analyses_data type: {type(analyses_data)}, length: {len(analyses_data) if analyses_data else 0}")
        
        # Send report generation started message
        await websocket.send_text(json.dumps({
            "type": "report_generation_started",
            "data": {
                "ticker": ticker,
                "company": company,
                "connection_id": connection_id,
                "message": f"📊 Generating comprehensive AI investment report for {company}...",
                "timestamp": datetime.now().isoformat()
            }
        }))
        
        # Report generation using template and all analyst outputs with streaming
        
        # Generate the report using all analyst outputs and template structure with real-time updates
        if analyses_data:
            # Use existing analyses data to generate template-based report with enhanced prompt
            logger.info(f"📋 Using {len(analyses_data)} stored analyses for report generation")
            
            # Load the Robeco template as one-shot example
            template_content = ""
            try:
                # Use relative path from project root
                current_file = Path(__file__)
                project_root = current_file.parent.parent.parent.parent  # Go up from backend/src/robeco/ to root
                template_path = project_root / "Report Example" / "Robeco_InvestmentCase_Template.txt"
                with open(template_path, 'r', encoding='utf-8') as f:
                    template_content = f.read()
                logger.info(f"✅ Loaded Robeco template: {len(template_content)} characters")
            except Exception as e:
                logger.warning(f"⚠️ Could not load template file: {e}")
                template_content = "Template not available"
            
            # Build enhanced prompt with all analyst outputs and template example
            enhanced_prompt = await _build_enhanced_report_prompt(
                company_name=company,
                ticker=ticker,
                analyses_data=analyses_data,
                template_content=template_content,
                report_focus=report_focus
            )
            
            # Generate report using the template system with streaming updates
            report_content = await generate_report_with_streaming(
                websocket=websocket,
                connection_id=connection_id,
                company_name=company,
                ticker=ticker,
                analyses_data=analyses_data,
                report_focus=report_focus,
                investment_objective=investment_objective,
                user_query=user_query,
                data_sources=data_sources
            )
            
        else:
            # No stored analyses - generate comprehensive report using financial data only
            logger.info(f"🏗️ No stored analyses found - generating comprehensive investment report for {company} using financial data")
            
            # Send progress update
            await websocket.send_text(json.dumps({
                "type": "report_generation_progress",
                "data": {
                    "status": "ai_generating",
                    "message": f"Generating comprehensive investment report for {company} using available financial data",
                    "connection_id": connection_id,
                    "timestamp": datetime.now().isoformat()
                }
            }))
            
            # Load the Robeco template for comprehensive report structure
            template_content = ""
            try:
                current_file = Path(__file__)
                project_root = current_file.parent.parent.parent.parent
                template_path = project_root / "Report Example" / "Robeco_InvestmentCase_Template.txt"
                with open(template_path, 'r', encoding='utf-8') as f:
                    template_content = f.read()
                logger.info(f"✅ Loaded Robeco template for comprehensive report: {len(template_content)} characters")
            except Exception as e:
                logger.warning(f"⚠️ Could not load template file: {e}")
                template_content = "Template not available"
            
            # Generate report using the same system, just with empty analyses data
            report_content = await generate_report_with_streaming(
                websocket=websocket,
                connection_id=connection_id,
                company_name=company,
                ticker=ticker,
                analyses_data={},  # Empty analyses - AI will generate content directly
                report_focus=report_focus,
                investment_objective=investment_objective,
                user_query=user_query,
                data_sources=data_sources
            )
        
        # The template_report_generator already returns complete HTML with CSS
        final_report_html = report_content
        
        # Send final report completion message with proper type
        logger.info(f"🔍 DEBUG: About to send final report completion message")
        logger.info(f"🔍 DEBUG: report_content length: {len(report_content) if report_content else 'None'}")
        logger.info(f"🔍 DEBUG: final_report_html length: {len(final_report_html) if final_report_html else 'None'}")
        
        await websocket.send_text(json.dumps({
            "type": "report_generation_completed",
            "data": {
                "report_html": final_report_html,
                "raw_content": report_content,
                "ticker": ticker,
                "company_name": company,
                "template_used": "Robeco Professional Template",
                "analyses_count": len(analyses_data) if analyses_data else 0,
                "content_length": len(report_content) if report_content else 0,
                "final_length": len(final_report_html) if final_report_html else 0,
                "connection_id": connection_id,
                "timestamp": datetime.now().isoformat()
            }
        }))
        
        logger.info(f"✅ SUCCESS: Final report completion message sent to WebSocket")
        logger.info(f"✅ Report generation completed for {connection_id}: {len(report_content)} characters")
        
    except Exception as e:
        logger.error(f"❌ Report generation failed for {connection_id}: {e}")
        import traceback
        logger.error(f"❌ Full traceback: {traceback.format_exc()}")
        
        # Send error message
        await websocket.send_text(json.dumps({
            "type": "report_generation_error",
            "data": {
                "error": f"Report generation failed: {str(e)}",
                "connection_id": connection_id,
                "timestamp": datetime.now().isoformat()
            }
        }))

def kill_process_on_port(port):
    """Kill any process running on the specified port - Enhanced reliability"""
    import subprocess
    import signal
    import psutil
    
    killed_any = False
    
    # Method 1: Try psutil with proper connection handling
    try:
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                # Get connections separately to avoid attribute issues
                connections = proc.net_connections()
                for conn in connections:
                    if hasattr(conn, 'laddr') and conn.laddr.port == port:
                        logger.info(f"🔫 Killing process {proc.info['name']} (PID: {proc.info['pid']}) on port {port}")
                        proc.kill()
                        proc.wait(timeout=3)
                        killed_any = True
                        break
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, AttributeError):
                continue
            except Exception:
                continue
    except Exception as e:
        logger.debug(f"Method 1 (psutil) failed: {e}")
        
    # Method 2: Use lsof and kill (more reliable on macOS)
    try:
        result = subprocess.run(['lsof', '-ti', f':{port}'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0 and result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid.strip():
                    try:
                        logger.info(f"🔫 Killing process PID {pid.strip()} on port {port}")
                        subprocess.run(['kill', '-9', pid.strip()], timeout=3, check=True)
                        killed_any = True
                    except subprocess.CalledProcessError:
                        continue
    except Exception as e:
        logger.debug(f"Method 2 (lsof) failed: {e}")
    
    # Method 3: Try netstat approach
    try:
        result = subprocess.run(['netstat', '-tulpn'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            for line in lines:
                if f':{port}' in line and 'LISTEN' in line:
                    parts = line.split()
                    if len(parts) > 6:
                        pid_info = parts[6]
                        if '/' in pid_info:
                            pid = pid_info.split('/')[0]
                            try:
                                logger.info(f"🔫 Killing process PID {pid} on port {port} (netstat method)")
                                subprocess.run(['kill', '-9', pid], timeout=3, check=True)
                                killed_any = True
                            except subprocess.CalledProcessError:
                                continue
    except Exception as e:
        logger.debug(f"Method 3 (netstat) failed: {e}")
    
    return killed_any

def force_use_port_8005():
    """Kill any process on port 8005 and ensure it's available"""
    import socket
    import time
    import subprocess
    
    port = 8005
    logger.info(f"🎯 Forcing use of port {port}")
    
    # Check if port is in use
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('0.0.0.0', port))
            logger.info(f"✅ Port {port} is already available")
            return port
    except OSError:
        logger.info(f"🔍 Port {port} is occupied, attempting to free it...")
        
        # Try multiple attempts to kill processes
        for attempt in range(3):
            logger.info(f"🔄 Attempt {attempt + 1} to free port {port}")
            
            # Kill process on port
            killed = kill_process_on_port(port)
            
            # Wait a bit longer for the port to be freed
            time.sleep(3)
            
            # Verify port is now available
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('0.0.0.0', port))
                    logger.info(f"✅ Successfully freed port {port}")
                    return port
            except OSError:
                if attempt < 2:  # Not the last attempt
                    logger.warning(f"⚠️ Port {port} still occupied, trying again...")
                    continue
                else:
                    logger.error(f"❌ Port {port} still occupied after {attempt + 1} attempts")
                    logger.error(f"🚀 FORCE MODE: PROCEEDING WITH PORT {port} ANYWAY - NO ALTERNATIVES!")
                    # Force kill with stronger methods
                    subprocess.run(['sudo', 'lsof', '-ti', f':{port}', '|', 'xargs', 'sudo', 'kill', '-9'], 
                                 shell=True, capture_output=True)
                    time.sleep(2)
                    return port

# Removed find_available_port function - ONLY USE PORT 8005!

async def generate_report_with_streaming(
    websocket: WebSocket,
    connection_id: str,
    company_name: str,
    ticker: str,
    analyses_data: Dict[str, Any],
    report_focus: str = "comprehensive",
    investment_objective: str = None,
    user_query: str = None,
    data_sources: Dict = None
) -> str:
    """Generate report with real-time streaming updates to frontend"""
    
    from robeco.backend.template_report_generator import RobecoTemplateReportGenerator
    
    # Initialize streaming variables
    accumulated_content = ""
    total_chunks = 0
    
    # Send initial status
    await websocket.send_text(json.dumps({
        "type": "report_generation_progress",
        "data": {
            "status": "initializing",
            "message": "🏗️ Initializing report template...",
            "progress": 0,
            "connection_id": connection_id,
            "timestamp": datetime.now().isoformat()
        }
    }))
    
    try:
        # Create template generator
        generator = RobecoTemplateReportGenerator()
        
        # Send template loading status
        await websocket.send_text(json.dumps({
            "type": "report_generation_progress",
            "data": {
                "status": "template_loading",
                "message": "📋 Loading Robeco investment template...",
                "progress": 10,
                "connection_id": connection_id,
                "timestamp": datetime.now().isoformat()
            }
        }))
        
        # Fetch yfinance data for the company
        financial_data = {}
        try:
            await websocket.send_text(json.dumps({
                "type": "report_generation_progress",
                "data": {
                    "status": "fetching_data",
                    "message": f"📊 Fetching yfinance data for {ticker}...",
                    "progress": 15,
                    "connection_id": connection_id,
                    "timestamp": datetime.now().isoformat()
                }
            }))
            
            stock = yf.Ticker(ticker)
            
            # Get financial statements in the correct format for the template generator
            financials_df = stock.financials if hasattr(stock, 'financials') else None
            balance_sheet_df = stock.balance_sheet if hasattr(stock, 'balance_sheet') else None
            cashflow_df = stock.cashflow if hasattr(stock, 'cashflow') else None
            
            # Convert DataFrames to the expected annual format with proper date keys
            income_statement_annual = {}
            balance_sheet_annual = {}
            cashflow_annual = {}
            
            if financials_df is not None and not financials_df.empty:
                for date_col in financials_df.columns:
                    date_str = date_col.strftime('%Y-%m-%d') if hasattr(date_col, 'strftime') else str(date_col)
                    income_statement_annual[date_str] = financials_df[date_col].to_dict()
            
            if balance_sheet_df is not None and not balance_sheet_df.empty:
                for date_col in balance_sheet_df.columns:
                    date_str = date_col.strftime('%Y-%m-%d') if hasattr(date_col, 'strftime') else str(date_col)
                    balance_sheet_annual[date_str] = balance_sheet_df[date_col].to_dict()
                    
            if cashflow_df is not None and not cashflow_df.empty:
                for date_col in cashflow_df.columns:
                    date_str = date_col.strftime('%Y-%m-%d') if hasattr(date_col, 'strftime') else str(date_col)
                    cashflow_annual[date_str] = cashflow_df[date_col].to_dict()
            
            financial_data = {
                'info': stock.info,
                'history': stock.history(period="5y", interval="1mo").to_dict() if hasattr(stock, 'history') else {},
                'income_statement_annual': income_statement_annual,
                'balance_sheet_annual': balance_sheet_annual,
                'cashflow_annual': cashflow_annual
            }
            logger.info(f"✅ Fetched yfinance data for {ticker}: {len(str(financial_data)):,} characters")
        except Exception as e:
            logger.warning(f"⚠️ Could not fetch yfinance data for {ticker}: {e}")
            financial_data = {"error": f"Could not fetch data: {e}"}

        # Send AI generation start
        await websocket.send_text(json.dumps({
            "type": "report_generation_progress",
            "data": {
                "status": "ai_generating",
                "message": "🤖 AI generating professional investment report...",
                "progress": 20,
                "connection_id": connection_id,
                "timestamp": datetime.now().isoformat()
            }
        }))
        
        # Generate the report with real streaming from AI (uses 2-call architecture internally)
        logger.info(f"🔍 DEBUG: About to call generate_report_with_websocket_streaming")
        
        report_content = await generator.generate_report_with_websocket_streaming(
            company_name=company_name,
            ticker=ticker,
            analyses_data=analyses_data,
            report_focus=report_focus,
            websocket=websocket,
            connection_id=connection_id,
            financial_data=financial_data,
            investment_objective=investment_objective,
            user_query=user_query,
            data_sources=data_sources
        )
        
        logger.info(f"🔍 DEBUG: generate_report_with_websocket_streaming completed, content length: {len(report_content) if report_content else 'None'}")
        
        # Send final processing status
        await websocket.send_text(json.dumps({
            "type": "report_generation_progress",
            "data": {
                "status": "finalizing",
                "message": "✨ Finalizing report formatting...",
                "progress": 90,
                "connection_id": connection_id,
                "timestamp": datetime.now().isoformat()
            }
        }))
        
        logger.info(f"✅ Streaming report generation completed: {len(report_content):,} characters in {total_chunks} chunks")
        return report_content
        
    except Exception as e:
        logger.error(f"❌ Streaming report generation failed: {e}")
        
        # Send error status
        await websocket.send_text(json.dumps({
            "type": "report_generation_progress",
            "data": {
                "status": "error",
                "message": f"❌ Report generation failed: {str(e)[:100]}...",
                "progress": 0,
                "connection_id": connection_id,
                "timestamp": datetime.now().isoformat()
            }
        }))
        raise


async def handle_word_report_generation(websocket: WebSocket, connection_id: str, message: Dict):
    """Handle Word document generation from HTML report"""
    
    try:
        # Extract parameters
        data = message.get('data', {})
        html_content = data.get('html_content', '')
        company_name = data.get('company_name', '')
        ticker = data.get('ticker', '')
        
        logger.info(f"📄 Starting Word report generation for {company_name} ({ticker})")
        
        if not html_content:
            raise ValueError("No HTML content provided for Word conversion")
        
        # Send start notification
        await websocket.send_text(json.dumps({
            "type": "word_generation_started",
            "data": {
                "ticker": ticker,
                "company_name": company_name,
                "message": f"📄 Converting HTML report to Word document for {company_name}...",
                "timestamp": datetime.now().isoformat()
            }
        }))
        
        # Send progress update
        await websocket.send_text(json.dumps({
            "type": "word_generation_progress",
            "data": {
                "status": "parsing_html",
                "message": "🔍 Parsing HTML content and extracting structure...",
                "progress": 20,
                "timestamp": datetime.now().isoformat()
            }
        }))
        
        # Generate Word document
        output_path = await word_report_generator.convert_html_to_word(
            html_content=html_content,
            company_name=company_name,
            ticker=ticker
        )
        
        # Send progress update
        await websocket.send_text(json.dumps({
            "type": "word_generation_progress", 
            "data": {
                "status": "converting_styles",
                "message": "🎨 Converting CSS styles to Word formatting...",
                "progress": 60,
                "timestamp": datetime.now().isoformat()
            }
        }))
        
        # Send completion notification
        await websocket.send_text(json.dumps({
            "type": "word_generation_completed",
            "data": {
                "ticker": ticker,
                "company_name": company_name,
                "file_path": output_path,
                "message": f"✅ Word document generated successfully for {company_name}",
                "download_url": f"/api/download/word?file_path={output_path}",
                "timestamp": datetime.now().isoformat()
            }
        }))
        
        logger.info(f"✅ Word document generated: {output_path}")
        
    except Exception as e:
        logger.error(f"❌ Word generation failed: {e}")
        
        # Send error notification
        await websocket.send_text(json.dumps({
            "type": "word_generation_error",
            "data": {
                "error": str(e),
                "message": f"❌ Word generation failed: {str(e)[:100]}...",
                "timestamp": datetime.now().isoformat()
            }
        }))

def main():
    """Main application entry point"""
    logger.info("🚀 Starting Robeco Ultra-Sophisticated Professional Streaming Server")
    logger.info("🧠 Sequential Intelligence Multi-Agent Architecture")
    logger.info("🔧 Cross-agent synthesis with maximum AI utilization")
    logger.info("📊 Professional-grade streaming reports with Google Search grounding")
    
    # Force use of port 8005 (kill any existing process)
    try:
        port = force_use_port_8005()
        
        # Get IP addresses for display
        import requests
        import socket
        
        def get_public_ip_server():
            try:
                response = requests.get('https://ifconfig.me', timeout=5)
                return response.text.strip()
            except:
                try:
                    response = requests.get('https://api.ipify.org', timeout=5)
                    return response.text.strip()
                except:
                    return "Unable to detect"

        def get_local_ip_server():
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
                s.close()
                return local_ip
            except:
                return "127.0.0.1"
        
        public_ip = get_public_ip_server()
        local_ip = get_local_ip_server()
        
        logger.info(f"🌐 Server will be available at: http://0.0.0.0:{port}")
        logger.info(f"🎯 Successfully secured port {port}")
        logger.info("")
        logger.info("=" * 80)
        logger.info("🌍 INTERNET ACCESS URLS - SHARE WITH OUTSIDERS:")
        logger.info("=" * 80)
        logger.info(f"📍 Main App: http://{public_ip}:{port}/")
        logger.info(f"📍 Workbench: http://{public_ip}:{port}/workbench")
        logger.info(f"📍 Local Network: http://{local_ip}:{port}/")
        logger.info("=" * 80)
        logger.info("⚠️  ROUTER MUST FORWARD PORT 8005 FOR INTERNET ACCESS")
        logger.info("💡 Copy these URLs and share them worldwide!")
        logger.info("=" * 80)
        logger.info("")
        
        uvicorn.run(
            app,
            host="0.0.0.0",
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