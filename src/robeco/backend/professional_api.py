"""
Professional Investment Research Workbench API

Unlimited AI-powered investment analysis platform with maximum research capacity.
No artificial constraints - full AI capabilities enabled for institutional-grade analysis.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List
import json

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from pydantic import BaseModel

from ..core.memory import EnhancedSharedMemory, APIKeyManager
from ..core.models import AnalysisContext, WebSocketMessage
from ..agents.streaming_professional_analyst import StreamingInvestmentAnalystTeam
from ..backend.websocket_manager import WebSocketManager
from ..backend.word_report_generator import RobecoWordReportGenerator
from ..backend.pdf_report_generator import RobecoPdfReportGenerator

logger = logging.getLogger(__name__)

# Request models for unlimited AI analysis
class AnalysisRequest(BaseModel):
    ticker: str
    company_name: str
    analyst_type: str  # chief, fundamentals, industry, technical, risk, esg
    user_query: str = "Perform unlimited capacity professional investment analysis"

class ReportRequest(BaseModel):
    ticker: str 
    company_name: str
    report_type: str = "unlimited"  # unlimited AI capacity analysis

class DocumentConversionRequest(BaseModel):
    html_content: str
    company_name: str
    ticker: str
    format: str  # "word" or "pdf"


class ProfessionalInvestmentAPI:
    """Professional Investment Analysis API - Unlimited AI Capacity"""
    
    def __init__(self):
        from ..core.config import Settings
        settings = Settings()
        self.memory = EnhancedSharedMemory()
        self.api_manager = APIKeyManager(settings.GEMINI_API_KEYS)
        self.analyst_team = StreamingInvestmentAnalystTeam(self.memory, self.api_manager)
        self.websocket_manager = WebSocketManager(self.memory)
        self.word_generator = RobecoWordReportGenerator()
        self.pdf_generator = RobecoPdfReportGenerator()
        
        # Template configuration for unlimited AI interface
        self.templates = Jinja2Templates(directory="src/robeco/frontend/templates")
        
    def setup_routes(self, app: FastAPI):
        """Setup unlimited AI analysis API routes"""
        
        @app.get("/workbench", response_class=HTMLResponse)
        async def professional_workbench(request: Request):
            """Professional investment research workbench MVP"""
            return self.templates.TemplateResponse(
                "robeco_investment_workbench_mvp.html", 
                {"request": request}
            )
        
        @app.get("/", response_class=HTMLResponse)
        async def root_workbench(request: Request):
            """Serve MVP workbench at root"""
            return self.templates.TemplateResponse(
                "robeco_investment_workbench_mvp.html", 
                {"request": request}
            )
        
        @app.websocket("/ws/professional")
        async def professional_websocket(websocket: WebSocket):
            """Unlimited AI professional investment workbench WebSocket"""
            # Don't accept here - let websocket_manager handle it
            client_id = f"unlimited_ai_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            
            logger.info(f"🔗 Professional WebSocket connecting: {client_id}")
            
            try:
                # Accept the connection directly (don't use websocket_manager for connection handling)
                await websocket.accept()
                logger.info(f"✅ Professional WebSocket connected successfully: {client_id}")
                
                # Send connection established message
                connection_msg = {
                    "type": "connection_established",
                    "data": {
                        "client_id": client_id,
                        "message": "Connected to Robeco AI System",
                        "system_status": "ready"
                    },
                    "timestamp": datetime.now().isoformat(),
                    "client_id": client_id
                }
                await websocket.send_text(json.dumps(connection_msg))
                logger.info(f"📤 Sent connection established message to {client_id}")

                # Store websocket reference for direct messaging
                self.active_websockets = getattr(self, 'active_websockets', {})
                self.active_websockets[client_id] = websocket
                
                # Send client connected broadcast (manual)
                broadcast_msg = {
                    "type": "client_connected",
                    "timestamp": datetime.now().timestamp(),
                    "client_id": client_id,
                    "total_connections": 1
                }
                await websocket.send_text(json.dumps(broadcast_msg))
                logger.info(f"📤 Sent client connected message to {client_id}")

                while True:
                    # Receive unlimited AI analysis requests
                    logger.info(f"📡 Waiting for message from client: {client_id}")
                    try:
                        data = await websocket.receive_text()
                        logger.info(f"📨 Raw data received from {client_id}: {data}")
                        
                        message = json.loads(data)
                        logger.info(f"🔥 Professional WebSocket received from {client_id}: {message}")
                        logger.info(f"📋 Message type: {message.get('type')}")
                        logger.info(f"📋 Message analyst: {message.get('analyst')}")
                        logger.info(f"📋 Message ticker: {message.get('ticker')}")
                        logger.info(f"📋 Message company: {message.get('company')}")
                        
                        # Handle the message with websocket reference
                        await self._handle_professional_message(message, client_id, websocket)
                        logger.info(f"✅ Message processed successfully for {client_id}")
                        
                    except WebSocketDisconnect:
                        logger.info(f"📤 Client {client_id} disconnected normally")
                        break
                    except json.JSONDecodeError as e:
                        logger.error(f"❌ JSON decode error for {client_id}: {e}, Raw data: {data}")
                        try:
                            await websocket.send_text(json.dumps({
                                "type": "error",
                                "data": {"error": f"Invalid JSON: {str(e)}"}
                            }))
                        except Exception:
                            logger.error(f"Failed to send error message to {client_id}")
                            break
                    except Exception as e:
                        logger.error(f"❌ Message processing error for {client_id}: {e}")
                        try:
                            await websocket.send_text(json.dumps({
                                "type": "analysis_error", 
                                "data": {"error": str(e)}
                            }))
                        except Exception:
                            logger.error(f"Failed to send error message to {client_id}")
                            break
                        
            except WebSocketDisconnect:
                logger.info(f"📤 Professional WebSocket disconnected: {client_id}")
            except Exception as e:
                logger.error(f"❌ Professional WebSocket error for {client_id}: {e}")
            finally:
                # Clean up
                if hasattr(self, 'active_websockets') and client_id in self.active_websockets:
                    del self.active_websockets[client_id]
                logger.info(f"🧹 Cleaned up connection for {client_id}")
        
        @app.post("/api/professional/analyze")
        async def start_professional_analysis(request: AnalysisRequest):
            """Start unlimited AI professional investment analysis"""
            try:
                # Create unlimited AI analysis context
                context = AnalysisContext(
                    company_name=request.company_name,
                    ticker=request.ticker,
                    user_query=request.user_query,
                    analysis_focus=[request.analyst_type]
                )
                
                # Execute unlimited AI analysis
                result = await self.analyst_team.conduct_analysis(request.analyst_type, context)
                
                return {
                    "status": "success",
                    "analyst_type": request.analyst_type,
                    "analysis_id": result.agent_id,
                    "processing_time": result.processing_time,
                    "quality_score": result.quality_score,
                    "unlimited_capacity": True
                }
                
            except Exception as e:
                logger.error(f"Unlimited AI analysis startup failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.post("/api/professional/report")
        async def generate_comprehensive_report(request: ReportRequest):
            """Generate unlimited AI comprehensive investment report"""
            try:
                context = AnalysisContext(
                    company_name=request.company_name,
                    ticker=request.ticker,
                    user_query="Generate unlimited capacity comprehensive investment report",
                    analysis_focus=["unlimited_comprehensive_report"]
                )
                
                # Generate unlimited AI comprehensive report
                report = await self.analyst_team.generate_comprehensive_report(context)
                
                return {
                    "status": "success",
                    "report_type": request.report_type,
                    "report_data": report,
                    "generation_time": datetime.now().isoformat(),
                    "unlimited_capacity": True
                }
                
            except Exception as e:
                logger.error(f"Unlimited AI report generation failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.post("/api/professional/convert")
        async def convert_html_to_document(request: DocumentConversionRequest):
            """Convert HTML report to Word document or PDF"""
            try:
                logger.info(f"🔄 Converting HTML to {request.format.upper()}: {request.ticker}")
                
                if request.format.lower() == "word":
                    # Convert to Word document
                    output_path = await self.word_generator.convert_html_to_word(
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
                    # Convert to PDF document
                    output_path = await self.pdf_generator.convert_html_to_pdf(
                        html_content=request.html_content,
                        company_name=request.company_name,
                        ticker=request.ticker
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
        
        @app.get("/api/professional/analysts")
        async def get_analyst_team_status():
            """Get unlimited AI analyst team status"""
            return {
                "status": "success",
                "unlimited_capacity": True,
                "analysts": [
                    {
                        "id": "chief",
                        "name": "Chief Investment Officer",
                        "specialty": "Strategic Investment Decision-Making & Portfolio Management",
                        "status": "unlimited_ai_ready"
                    },
                    {
                        "id": "fundamentals", 
                        "name": "Senior Fundamental Analyst",
                        "specialty": "Financial Analysis & Valuation Modeling",
                        "status": "unlimited_ai_ready"
                    },
                    {
                        "id": "industry",
                        "name": "Industry Research Analyst", 
                        "specialty": "Sector Analysis & Competitive Intelligence",
                        "status": "unlimited_ai_ready"
                    },
                    {
                        "id": "technical",
                        "name": "Technical Research Analyst",
                        "specialty": "Technical Analysis & Market Timing", 
                        "status": "unlimited_ai_ready"
                    },
                    {
                        "id": "risk",
                        "name": "Risk Management Analyst",
                        "specialty": "Risk Assessment & Scenario Analysis",
                        "status": "unlimited_ai_ready"
                    },
                    {
                        "id": "esg",
                        "name": "ESG Research Analyst",
                        "specialty": "Environmental, Social & Governance Analysis",
                        "status": "unlimited_ai_ready"
                    },
                    {
                        "id": "research",
                        "name": "Senior Third-Party Research Analyst",
                        "specialty": "Elite Research Synthesis & Consensus Analysis",
                        "status": "unlimited_ai_ready"
                    },
                    {
                        "id": "sentiment",
                        "name": "Senior News & Sentiment Analyst",
                        "specialty": "Elite Market Sentiment & News Analysis",
                        "status": "unlimited_ai_ready"
                    },
                    {
                        "id": "management",
                        "name": "Senior Management & Governance Analyst",
                        "specialty": "Elite Management Assessment & Corporate Governance",
                        "status": "unlimited_ai_ready"
                    },
                    {
                        "id": "business",
                        "name": "Senior Business Model Analyst",
                        "specialty": "Elite Business Model & Economic Moat Analysis",
                        "status": "unlimited_ai_ready"
                    },
                    {
                        "id": "valuation",
                        "name": "Senior Valuation & Modeling Analyst",
                        "specialty": "Elite Valuation Modeling & Quantitative Analysis",
                        "status": "unlimited_ai_ready"
                    },
                    {
                        "id": "macro",
                        "name": "Senior Macro & Cyclical Analyst",
                        "specialty": "Elite Macroeconomic & Cyclical Analysis",
                        "status": "unlimited_ai_ready"
                    }
                ]
            }
    
    async def _handle_professional_message(self, message: Dict[str, Any], client_id: str, websocket: WebSocket):
        """Handle unlimited AI professional workbench messages"""
        logger.info(f"🔄 Processing professional message for {client_id}")
        message_type = message.get("type")
        logger.info(f"📋 Message type: {message_type}")
        
        if message_type == "start_analysis":
            logger.info(f"🚀 Starting analysis request for {client_id}")
            await self._handle_analysis_request(message, client_id, websocket)
        elif message_type == "generate_report":
            logger.info(f"📊 Starting report generation for {client_id}")
            await self._handle_report_request(message, client_id, websocket)
        elif message_type == "analyst_chat":
            logger.info(f"💬 Starting analyst chat for {client_id}")
            await self._handle_analyst_chat(message, client_id, websocket)
        else:
            logger.warning(f"❌ Unknown unlimited AI message type: {message_type} from {client_id}")
    
    async def _handle_analysis_request(self, message: Dict[str, Any], client_id: str, websocket: WebSocket):
        """Handle real-time AI analysis request"""
        try:
            analyst_type = message.get("analyst", "chief")
            ticker = message.get("ticker", "")
            company = message.get("company", "")
            
            logger.info(f"🚀 Starting real AI analysis: {analyst_type} for {company} ({ticker})")
            
            # Send analysis start message directly to requesting client
            start_message = WebSocketMessage(
                type="analysis_started",
                data={
                    "analyst": analyst_type,
                    "ticker": ticker,
                    "company": company,
                    "status": f"AI {analyst_type} analyst is performing real-time analysis..."
                }
            )
            try:
                await websocket.send_text(json.dumps(start_message.to_json()))
                logger.info(f"📤 Sent analysis start notification to client {client_id}")
            except Exception as e:
                logger.error(f"❌ Failed to send start message to {client_id}: {e}")
                return
            
            # Create analysis context for real AI processing
            context = AnalysisContext(
                company_name=company,
                ticker=ticker,
                user_query=f"Perform comprehensive {analyst_type} investment analysis using real financial data",
                analysis_focus=[analyst_type]
            )
            
            # Execute STREAMING AI analysis (real-time)
            logger.info(f"📊 Executing streaming AI analysis with real-time updates...")
            result = await self.analyst_team.conduct_streaming_analysis(analyst_type, context)
            
            # Handle streaming analysis results
            if result.data.get('streaming_analysis'):
                # Final summary message
                complete_report_message = WebSocketMessage(
                    type="complete_investment_report",
                    data={
                        "analyst_id": result.agent_id,
                        "analyst_name": result.data.get('analyst_name', f"{analyst_type.capitalize()} Investment Analyst"),
                        "ticker": ticker,
                        "company": company,
                        "report_content": result.data['streaming_analysis'],
                        "streaming_complete": True,
                        "timestamp": datetime.now().isoformat()
                    }
                )
                # Send final report to client
                try:
                    await websocket.send_text(json.dumps(complete_report_message.to_json()))
                    logger.info(f"📤 Sent streaming analysis completion to client {client_id}")
                except Exception as e:
                    logger.error(f"❌ Failed to send streaming completion to {client_id}: {e}")
            
            # Streaming analysis completion notification
            try:
                complete_message = WebSocketMessage(
                    type="streaming_analysis_completed",
                    data={
                        "analyst": analyst_type,
                        "ticker": ticker,
                        "quality_score": result.quality_score,
                        "processing_time": result.processing_time,
                        "streaming_enabled": True,
                        "source_count": len(result.data_sources) if result.data_sources else 0
                    }
                )
                await websocket.send_text(json.dumps(complete_message.to_json()))
                logger.info(f"📤 Sent streaming analysis completion to client {client_id}")
            except Exception as e:
                logger.error(f"❌ Failed to send streaming completion message to {client_id}: {e}")
            
        except Exception as e:
            logger.error(f"❌ Real AI analysis failed: {e}")
            
            error_message = WebSocketMessage(
                type="analysis_error",
                data={
                    "error": f"AI Analysis Error: {str(e)}",
                    "analyst": message.get("analyst", "unknown")
                }
            )
            try:
                await websocket.send_text(json.dumps(error_message.to_json()))
                logger.info(f"📤 Sent error message to client {client_id}")
            except Exception as e:
                logger.error(f"❌ Failed to send error message to {client_id}: {e}")
    
    async def _handle_report_request(self, message: Dict[str, Any], client_id: str, websocket: WebSocket):
        """Handle comprehensive AI investment report generation"""
        try:
            ticker = message.get("ticker", "")
            company = message.get("company", "")
            
            logger.info(f"📊 Generating comprehensive AI investment report for {company} ({ticker})")
            
            # Broadcast report generation start
            start_message = WebSocketMessage(
                type="report_generation_started",
                data={
                    "ticker": ticker,
                    "company": company,
                    "status": "AI is generating comprehensive investment report..."
                }
            )
            await self.websocket_manager.broadcast_message(start_message.to_dict())
            
            # Create context for comprehensive AI report
            context = AnalysisContext(
                company_name=company,
                ticker=ticker,
                user_query="Generate comprehensive professional investment analysis report",
                analysis_focus=["comprehensive_report"]
            )
            
            # Generate comprehensive AI report
            report = await self.analyst_team.generate_comprehensive_report(context)
            
            # Report completion notification with real AI content
            complete_message = WebSocketMessage(
                type="complete_investment_report",
                data={
                    "ticker": ticker,
                    "company": company,
                    "report_content": report.get('consolidated_analysis', 'AI report generation in progress...'),
                    "analyst_name": "AI Investment Team",
                    "timestamp": datetime.now().isoformat()
                }
            )
            await self.websocket_manager.broadcast_message(complete_message.to_dict())
            
        except Exception as e:
            logger.error(f"❌ AI report generation failed: {e}")
            
            error_message = WebSocketMessage(
                type="analysis_error",
                data={
                    "error": f"AI Report Generation Error: {str(e)}",
                    "analyst": "report_generator"
                }
            )
            await self.websocket_manager.broadcast_message(error_message.to_dict())
    
    async def _handle_analyst_chat(self, message: Dict[str, Any], client_id: str, websocket: WebSocket):
        """Handle unlimited AI analyst interactive dialogue"""
        # Implement unlimited AI analyst interactive capabilities
        # No restrictions on conversation depth or analytical capacity
        pass


# Create unlimited AI global instance
professional_api = ProfessionalInvestmentAPI()


def setup_professional_routes(app: FastAPI):
    """Setup unlimited AI professional investment research API routes"""
    professional_api.setup_routes(app)