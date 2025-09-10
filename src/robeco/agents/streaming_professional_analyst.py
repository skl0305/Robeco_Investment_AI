"""
Streaming Professional Investment Analyst AI System

Real-time streaming analysis with token-by-token response delivery,
live Google research integration, and progressive result display.
"""

import asyncio
import logging
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional, List, AsyncGenerator
import aiohttp

from .base_agent import BaseAgent
from ..core.models import AnalysisContext, AnalysisResult, AgentType, WebSocketMessage
from ..core.memory import EnhancedSharedMemory, APIKeyManager
from ..data.yfinance_fetcher import YFinanceFetcher

# Optional import for AI functionality
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    genai = None

logger = logging.getLogger(__name__)


class StreamingProfessionalAnalyst(BaseAgent):
    """Streaming Professional Investment Analyst with Real-time Capabilities
    
    Delivers institutional-grade investment analysis with:
    - Token-by-token streaming AI responses
    - Real-time Google research integration
    - Live progress indicators and status updates
    - Progressive result building and display
    """
    
    def __init__(self, memory: EnhancedSharedMemory, api_manager: APIKeyManager, analyst_type: str = "chief"):
        super().__init__(memory, api_manager, f"streaming_{analyst_type}_analyst", AgentType.FINANCIAL_ANALYSIS)
        self.analyst_type = analyst_type
        self.yfinance_fetcher = YFinanceFetcher()
        
        # Streaming configuration
        self.streaming_enabled = True
        self.chunk_size = 50  # Characters per streaming chunk
        self.research_batch_size = 3  # Google search results per batch
        
        # Enhanced sector-specific analysis
        self.use_sector_enhancement = True
        
        # Elite analyst configurations
        self.analyst_config = {
            "chief": {
                "name": "Chief Investment Officer",
                "specialty": "Strategic Investment Decision-Making & Multi-Asset Portfolio Management",
                "focus_areas": ["Macro-Strategic Asset Allocation", "Alpha Generation", "Risk-Adjusted Returns", "Multi-Factor Portfolio Construction"],
                "streaming_priority": "executive_summary"
            },
            "fundamentals": {
                "name": "Senior Fundamental Research Analyst", 
                "specialty": "Elite Financial Analysis & Advanced Valuation Modeling",
                "focus_areas": ["Advanced DCF Modeling", "Earnings Quality", "Capital Allocation", "Competitive Moats"],
                "streaming_priority": "financial_metrics"
            },
            "industry": {
                "name": "Senior Industry Research Analyst",
                "specialty": "Elite Sector Intelligence & Competitive Dynamics", 
                "focus_areas": ["Industry Disruption", "Competitive Advantage", "Market Structure", "Regulatory Impact"],
                "streaming_priority": "competitive_analysis"
            },
            "technical": {
                "name": "Senior Technical Research Analyst",
                "specialty": "Elite Technical Analysis & Systematic Trading Strategies",
                "focus_areas": ["Chart Patterns", "Multi-Timeframe Analysis", "Options Flow", "Market Microstructure"],
                "streaming_priority": "technical_signals"
            },
            "risk": {
                "name": "Senior Risk Management Analyst", 
                "specialty": "Elite Risk Assessment & Advanced Scenario Modeling",
                "focus_areas": ["Value-at-Risk", "Stress Testing", "Tail Risk", "Correlation Breakdown"],
                "streaming_priority": "risk_assessment"
            },
            "esg": {
                "name": "Senior ESG Research Analyst",
                "specialty": "Elite ESG Analysis & Sustainable Investment Strategy",
                "focus_areas": ["ESG Scoring", "Climate Risk", "Governance Quality", "Stakeholder Capitalism"],
                "streaming_priority": "esg_metrics"
            },
            "research": {
                "name": "Senior Third-Party Research Analyst",
                "specialty": "Elite Research Synthesis & Consensus Analysis",
                "focus_areas": ["Sell-Side Synthesis", "Analyst Consensus", "Institutional Positioning", "Contrarian Analysis"],
                "streaming_priority": "consensus_data"
            },
            "sentiment": {
                "name": "Senior News & Sentiment Analyst", 
                "specialty": "Elite Market Sentiment & News Analysis",
                "focus_areas": ["News Flow", "Market Sentiment", "Social Media", "Management Communication"],
                "streaming_priority": "sentiment_indicators"
            },
            "management": {
                "name": "Senior Management & Governance Analyst",
                "specialty": "Elite Management Assessment & Corporate Governance",
                "focus_areas": ["Management Evaluation", "Governance Structure", "Capital Allocation", "Strategic Execution"],
                "streaming_priority": "management_assessment"
            },
            "business": {
                "name": "Senior Business Model Analyst",
                "specialty": "Elite Business Model & Economic Moat Analysis", 
                "focus_areas": ["Business Model", "Economic Moats", "Competitive Advantage", "Customer Value"],
                "streaming_priority": "business_model"
            },
            "valuation": {
                "name": "Senior Valuation & Modeling Analyst",
                "specialty": "Elite Valuation Modeling & Quantitative Analysis",
                "focus_areas": ["DCF Construction", "Relative Valuation", "Sum-of-Parts", "Sensitivity Analysis"],
                "streaming_priority": "valuation_models"
            },
            "macro": {
                "name": "Senior Macro & Cyclical Analyst",
                "specialty": "Elite Macroeconomic & Cyclical Analysis",
                "focus_areas": ["Macro Environment", "Industry Cyclical", "Policy Impact", "Currency Sensitivity"],
                "streaming_priority": "macro_analysis"
            }
        }
    
    async def analyze(self, context: AnalysisContext) -> AnalysisResult:
        """Execute streaming comprehensive professional investment analysis"""
        start_time = datetime.now()
        
        try:
            # Initialize streaming analysis
            await self.broadcast_streaming_start(context)
            
            # Phase 1: Real-time data gathering with live updates
            await self.stream_status_update("🔍 Gathering real-time financial data...", "data_collection", 0.1)
            comprehensive_data = await self.yfinance_fetcher.fetch_comprehensive_data(context.ticker)
            await self.stream_status_update("✅ Financial data collected", "data_collection", 0.2)
            
            # Phase 2: Live Google research integration
            await self.stream_status_update("🌐 Conducting live Google research...", "research_collection", 0.3)
            research_results = await self.stream_google_research(context)
            await self.stream_status_update("✅ Research data integrated", "research_collection", 0.4)
            
            # Phase 3: Build streaming analysis prompt
            analysis_prompt = self._build_streaming_prompt(context, comprehensive_data, research_results)
            
            # Phase 4: Execute streaming AI analysis
            await self.stream_status_update("🧠 AI analyst generating insights...", "ai_analysis", 0.5)
            streaming_analysis = await self.execute_streaming_ai_analysis(analysis_prompt, context)
            await self.stream_status_update("✅ AI analysis completed", "ai_analysis", 1.0)
            
            # Build final result
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return AnalysisResult(
                agent_id=self.agent_id,
                agent_type=self.agent_type,
                data={
                    'analyst_type': self.analyst_type,
                    'analyst_name': self.get_analyst_name(),
                    'streaming_analysis': streaming_analysis,
                    'financial_data': comprehensive_data,
                    'research_data': research_results,
                    'analysis_timestamp': datetime.now().isoformat(),
                    'streaming_enabled': True
                },
                quality_score=0.95,
                processing_time=processing_time,
                data_sources=research_results.get('sources', [])
            )
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Streaming analysis failed: {e}")
            await self.stream_error_update(f"Analysis error: {str(e)}")
            
            return AnalysisResult(
                agent_id=self.agent_id,
                agent_type=self.agent_type,
                data={"error": str(e)},
                quality_score=0.0,
                processing_time=processing_time,
                error_message=str(e)
            )
    
    async def execute_streaming_ai_analysis(self, prompt: str, context: AnalysisContext) -> str:
        """Execute AI analysis with real-time token-by-token streaming"""
        if not GENAI_AVAILABLE:
            raise ImportError("google-generativeai package not available")
        
        api_key = self.api_manager.get_optimal_key()
        
        try:
            # Configure Gemini for streaming
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # Start streaming generation
            await self.stream_ai_start_message(context)
            
            # Generate streaming response
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=32000,
                    temperature=0.1
                ),
                stream=True  # Enable streaming
            )
            
            # Stream response token by token
            full_response = ""
            chunk_buffer = ""
            
            for chunk in response:
                if chunk.text:
                    chunk_buffer += chunk.text
                    full_response += chunk.text
                    
                    # Stream in manageable chunks
                    if len(chunk_buffer) >= self.chunk_size:
                        await self.stream_ai_content_chunk(chunk_buffer, context)
                        chunk_buffer = ""
                        await asyncio.sleep(0.1)  # Smooth streaming pace
            
            # Send remaining buffer
            if chunk_buffer:
                await self.stream_ai_content_chunk(chunk_buffer, context)
            
            # Send completion signal
            await self.stream_ai_complete_message(context, full_response)
            
            return full_response
            
        except Exception as e:
            logger.error(f"Streaming AI analysis failed: {e}")
            raise ValueError(f"AI Analysis unavailable - API Error: {str(e)}")
    
    async def stream_google_research(self, context: AnalysisContext) -> Dict[str, Any]:
        """Stream real-time Google research results"""
        research_queries = [
            f"{context.company_name} {context.ticker} latest earnings financial results 2024",
            f"{context.company_name} analyst ratings upgrades downgrades recent",
            f"{context.company_name} competitive analysis market share industry",
            f"{context.company_name} management guidance outlook forecast 2024 2025",
            f"{context.company_name} risk factors challenges regulatory issues"
        ]
        
        research_results = {
            'timestamp': datetime.now().isoformat(),
            'queries_executed': len(research_queries),
            'sources': [],
            'search_results': []
        }
        
        for i, query in enumerate(research_queries):
            try:
                # Stream search progress
                progress = (i + 1) / len(research_queries)
                await self.stream_research_progress(f"Searching: {query[:50]}...", progress)
                
                # Execute Google search with Gemini grounding
                search_result = await self._perform_streaming_google_search(query, context)
                research_results['search_results'].append(search_result)
                
                # Extract and stream sources
                if 'sources' in search_result:
                    for source in search_result['sources']:
                        research_results['sources'].append(source)
                        await self.stream_research_source(source, context)
                
                await asyncio.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                logger.warning(f"Search failed for query '{query}': {e}")
                await self.stream_research_error(f"Search failed: {query[:30]}...")
        
        await self.stream_research_complete(len(research_results['sources']))
        return research_results
    
    async def _perform_streaming_google_search(self, query: str, context: AnalysisContext) -> Dict[str, Any]:
        """Perform Google search using Gemini grounding with streaming results"""
        try:
            search_prompt = f"""
            Research the following investment-related query using Google Search: "{query}"
            
            Focus on finding current, credible information about {context.company_name} ({context.ticker}).
            Priority sources: SEC filings, earnings reports, analyst reports, financial news from Bloomberg/Reuters/WSJ.
            
            Provide factual, data-driven insights based on search results with specific sources and URLs when available.
            """
            
            # Use Gemini's grounding capabilities with proper Google Search tool
            api_key = self.api_manager.get_optimal_key()
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # Configure with Google Search tool for proper grounding
            search_results = await asyncio.to_thread(
                model.generate_content,
                search_prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=32000,
                    temperature=0.1
                ),
                tools=[genai.types.Tool(google_search=genai.types.GoogleSearch())]
            )
            
            # Extract real sources from Gemini's Google Search response
            real_sources = []
            grounding_available = False
            
            # Check if Google Search grounding provided real sources
            if hasattr(search_results, 'candidates') and search_results.candidates:
                for candidate in search_results.candidates:
                    if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
                        grounding_available = True
                        for chunk in candidate.grounding_metadata.grounding_chunks:
                            if hasattr(chunk, 'web') and chunk.web:
                                domain = chunk.web.uri.lower()
                                credibility = self._calculate_source_credibility(domain)
                                
                                real_sources.append({
                                    "title": chunk.web.title or "Google Search Result",
                                    "url": chunk.web.uri,
                                    "source_type": "google_search_result",
                                    "credibility_score": credibility,
                                    "domain": domain
                                })
            
            # Parse and structure results
            return {
                "query": query,
                "search_results": search_results.text,
                "search_timestamp": datetime.now().isoformat(),
                "method": "gemini_google_grounding",
                "sources": real_sources,
                "grounding_available": grounding_available,
                "source_count": len(real_sources)
            }
            
        except Exception as e:
            logger.error(f"Streaming Google search failed: {e}")
            return {
                "query": query,
                "error": str(e),
                "search_timestamp": datetime.now().isoformat(),
                "sources": []
            }
    
    def _calculate_source_credibility(self, url: str) -> float:
        """Calculate credibility score based on actual domain reputation"""
        url_lower = url.lower()
        
        # Tier 1: Official/Regulatory sources
        if any(domain in url_lower for domain in ['sec.gov', 'edgar.sec.gov', 'investor.gov']):
            return 0.99
        
        # Tier 2: Major financial institutions  
        if any(domain in url_lower for domain in ['bloomberg.com', 'reuters.com', 'wsj.com', 'ft.com']):
            return 0.95
        
        # Tier 3: Financial data providers
        if any(domain in url_lower for domain in ['yahoo.com/finance', 'finance.yahoo.com', 'morningstar.com', 'marketwatch.com']):
            return 0.90
        
        # Tier 4: Company official sites
        if any(domain in url_lower for domain in ['investor.', '/investor/', '/ir/', 'investors.']):
            return 0.88
        
        # Tier 5: Major news outlets
        if any(domain in url_lower for domain in ['cnbc.com', 'cnn.com/business', 'bbc.com/business']):
            return 0.85
        
        # Tier 6: Financial analysis sites
        if any(domain in url_lower for domain in ['seekingalpha.com', 'fool.com', 'zacks.com']):
            return 0.75
        
        # Default for unknown sources
        return 0.70
    
    # Streaming WebSocket Message Methods
    async def broadcast_streaming_start(self, context: AnalysisContext):
        """Broadcast streaming analysis start"""
        message = WebSocketMessage(
            type="streaming_analysis_started",
            data={
                "analyst_id": self.agent_id,
                "analyst_name": self.get_analyst_name(),
                "ticker": context.ticker,
                "company": context.company_name,
                "streaming_enabled": True,
                "timestamp": datetime.now().isoformat()
            }
        )
        await self.memory._broadcast_update(message.to_json())
    
    async def stream_status_update(self, message: str, phase: str, progress: float):
        """Stream status updates during analysis"""
        status_message = WebSocketMessage(
            type="streaming_status_update",
            data={
                "analyst_id": self.agent_id,
                "analyst_name": self.get_analyst_name(),
                "message": message,
                "phase": phase,
                "progress": progress,
                "timestamp": datetime.now().isoformat()
            }
        )
        await self.memory._broadcast_update(status_message.to_json())
    
    async def stream_research_progress(self, query: str, progress: float):
        """Stream Google research progress"""
        research_message = WebSocketMessage(
            type="streaming_research_progress",
            data={
                "analyst_id": self.agent_id,
                "query": query,
                "progress": progress,
                "timestamp": datetime.now().isoformat()
            }
        )
        await self.memory._broadcast_update(research_message.to_json())
    
    async def stream_research_source(self, source: Dict[str, Any], context: AnalysisContext):
        """Stream individual research sources as found"""
        source_message = WebSocketMessage(
            type="streaming_research_source",
            data={
                "analyst_id": self.agent_id,
                "ticker": context.ticker,
                "source": source,
                "timestamp": datetime.now().isoformat()
            }
        )
        await self.memory._broadcast_update(source_message.to_json())
    
    async def stream_ai_start_message(self, context: AnalysisContext):
        """Signal start of AI content generation"""
        ai_message = WebSocketMessage(
            type="streaming_ai_start",
            data={
                "analyst_id": self.agent_id,
                "analyst_name": self.get_analyst_name(),
                "ticker": context.ticker,
                "company": context.company_name,
                "timestamp": datetime.now().isoformat()
            }
        )
        await self.memory._broadcast_update(ai_message.to_json())
    
    async def stream_ai_content_chunk(self, chunk: str, context: AnalysisContext):
        """Stream AI content token by token"""
        chunk_message = WebSocketMessage(
            type="streaming_ai_content",
            data={
                "analyst_id": self.agent_id,
                "ticker": context.ticker,
                "content_chunk": chunk,
                "timestamp": datetime.now().isoformat()
            }
        )
        await self.memory._broadcast_update(chunk_message.to_json())
    
    async def stream_ai_complete_message(self, context: AnalysisContext, full_content: str):
        """Signal completion of AI content generation"""
        complete_message = WebSocketMessage(
            type="streaming_ai_complete",
            data={
                "analyst_id": self.agent_id,
                "analyst_name": self.get_analyst_name(),
                "ticker": context.ticker,
                "company": context.company_name,
                "full_content": full_content,
                "timestamp": datetime.now().isoformat()
            }
        )
        await self.memory._broadcast_update(complete_message.to_json())
    
    async def stream_research_complete(self, source_count: int):
        """Signal research collection completion"""
        complete_message = WebSocketMessage(
            type="streaming_research_complete",
            data={
                "analyst_id": self.agent_id,
                "source_count": source_count,
                "timestamp": datetime.now().isoformat()
            }
        )
        await self.memory._broadcast_update(complete_message.to_json())
    
    async def stream_research_error(self, error_message: str):
        """Stream research errors"""
        error_msg = WebSocketMessage(
            type="streaming_research_error",
            data={
                "analyst_id": self.agent_id,
                "error": error_message,
                "timestamp": datetime.now().isoformat()
            }
        )
        await self.memory._broadcast_update(error_msg.to_json())
    
    async def stream_error_update(self, error_message: str):
        """Stream analysis errors"""
        error_msg = WebSocketMessage(
            type="streaming_analysis_error",
            data={
                "analyst_id": self.agent_id,
                "error": error_message,
                "timestamp": datetime.now().isoformat()
            }
        )
        await self.memory._broadcast_update(error_msg.to_json())
    
    def _build_streaming_prompt(self, context: AnalysisContext, comprehensive_data: Dict[str, Any], research_data: Dict[str, Any] = None) -> str:
        """Build optimized prompt for streaming analysis"""
        config = self.analyst_config.get(self.analyst_type, self.analyst_config["chief"])
        
        # Extract comprehensive data components
        info = comprehensive_data.get("info", {})
        
        # Enhanced company information
        market_cap = info.get('marketCap', 0) or 0
        employees = info.get('fullTimeEmployees', 'N/A')
        market_cap_str = f"${market_cap:,}" if market_cap > 0 else "N/A"
        
        company_info = f"""
        **COMPANY PROFILE:**
        Company: {context.company_name} ({context.ticker})
        Industry: {info.get('industry', 'Unknown')} | Sector: {info.get('sector', 'Unknown')}
        Market Cap: {market_cap_str}
        Business: {info.get('longBusinessSummary', 'Not available')[:300]}...
        """
        
        # Current date for context
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        # Streaming-optimized prompt
        streaming_prompt = f"""You are an elite {config['name']} at a top-tier institutional investment firm.

**STREAMING ANALYSIS MANDATE:**
Generate a comprehensive investment analysis for {context.company_name} ({context.ticker}) that will be streamed in real-time to professional investors.

**ANALYSIS FRAMEWORK:**
{config['specialty']}

**KEY FOCUS AREAS:**
{', '.join(config['focus_areas'])}

**COMPANY DATA:**
{company_info}

**RESEARCH CONTEXT:**
- Analysis Date: {current_date}
- Research Integration: {len(research_data.get('sources', []))} live sources
- Data Quality: Comprehensive real-time financial data available

**STREAMING ANALYSIS REQUIREMENTS:**
1. **Executive Summary** - Clear investment recommendation with conviction level
2. **Key Investment Thesis** - 3-5 primary investment reasons
3. **Financial Analysis** - Core metrics and trends analysis
4. **Risk Assessment** - Primary risks and mitigation factors
5. **Price Target & Timeline** - 12-month target with confidence level
6. **Investment Recommendation** - BUY/HOLD/SELL with position sizing guidance

**OUTPUT FORMAT:**
Structure your analysis for optimal streaming delivery:
- Use clear section headers with ## formatting
- Provide quantitative data points and specific metrics
- Include actionable insights and precise recommendations
- Maintain professional institutional-grade language
- Focus on investment decision-making utility

**CONTEXT:** This analysis will stream live to portfolio managers making multi-million dollar investment decisions.

Begin comprehensive streaming analysis now:"""
        
        return streaming_prompt
    
    def get_analyst_name(self) -> str:
        """Get analyst name"""
        return self.analyst_config.get(self.analyst_type, {}).get("name", "Professional Analyst")
    
    def get_prompt_template(self) -> str:
        """Get streaming prompt template"""
        return "Streaming professional investment analyst with real-time capabilities"


# Streaming Investment Analyst Team Manager
class StreamingInvestmentAnalystTeam:
    """Streaming Investment Analyst Team Manager"""
    
    def __init__(self, memory: EnhancedSharedMemory, api_manager: APIKeyManager):
        self.memory = memory
        self.api_manager = api_manager
        
        # Initialize streaming analysts
        self.streaming_analysts = {
            "chief": StreamingProfessionalAnalyst(memory, api_manager, "chief"),
            "fundamentals": StreamingProfessionalAnalyst(memory, api_manager, "fundamentals"),
            "industry": StreamingProfessionalAnalyst(memory, api_manager, "industry"), 
            "technical": StreamingProfessionalAnalyst(memory, api_manager, "technical"),
            "risk": StreamingProfessionalAnalyst(memory, api_manager, "risk"),
            "esg": StreamingProfessionalAnalyst(memory, api_manager, "esg"),
            "research": StreamingProfessionalAnalyst(memory, api_manager, "research"),
            "sentiment": StreamingProfessionalAnalyst(memory, api_manager, "sentiment"),
            "management": StreamingProfessionalAnalyst(memory, api_manager, "management"),
            "business": StreamingProfessionalAnalyst(memory, api_manager, "business"),
            "valuation": StreamingProfessionalAnalyst(memory, api_manager, "valuation"),
            "macro": StreamingProfessionalAnalyst(memory, api_manager, "macro")
        }
    
    async def conduct_streaming_analysis(self, analyst_type: str, context: AnalysisContext) -> AnalysisResult:
        """Execute streaming analysis with specified analyst"""
        if analyst_type in self.streaming_analysts:
            return await self.streaming_analysts[analyst_type].analyze(context)
        else:
            raise ValueError(f"Unknown streaming analyst type: {analyst_type}")