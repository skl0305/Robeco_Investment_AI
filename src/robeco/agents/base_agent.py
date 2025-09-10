"""
Base Agent class for Robeco AI System

Provides common functionality for all AI agents including memory access,
API management, and performance tracking.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

# Optional import for AI functionality
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    genai = None

from ..core.models import AnalysisContext, AnalysisResult, AgentType, AnalysisStatus
from ..core.memory import EnhancedSharedMemory, APIKeyManager
from ..core.utils import time_execution, retry_async, calculate_quality_score

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Abstract base class for all AI agents"""
    
    def __init__(
        self,
        memory: EnhancedSharedMemory,
        api_manager: APIKeyManager,
        agent_id: str,
        agent_type: AgentType
    ):
        self.memory = memory
        self.api_manager = api_manager
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.logger = logging.getLogger(f"robeco.agents.{agent_id}")
        
        # Performance tracking
        self.execution_count = 0
        self.total_execution_time = 0.0
        self.success_count = 0
        self.error_count = 0
        
    @abstractmethod
    async def analyze(self, context: AnalysisContext) -> AnalysisResult:
        """
        Perform analysis based on the given context
        
        Args:
            context: Analysis context containing company info and parameters
            
        Returns:
            AnalysisResult containing the agent's analysis
        """
        pass
    
    @abstractmethod
    def get_prompt_template(self) -> str:
        """
        Get the enhanced prompt template for this agent
        
        Returns:
            String template for the AI prompt
        """
        pass
    
    async def get_enriched_context(self, context: AnalysisContext) -> Dict[str, Any]:
        """
        Get comprehensive context enriched with ALL available data
        
        This provides maximum context for AI agents including:
        - Data from all other agents
        - Complete financial data
        - File context and user queries
        - Cross-agent insights and dependencies
        """
        enriched = self.memory.get_enriched_context(self.agent_id, context)
        
        # Add comprehensive context enhancement
        enriched["comprehensive_context"] = {
            "agent_collaboration": {
                "available_insights": list(enriched.get("shared_insights", {}).keys()),
                "data_quality_scores": {
                    key: data.get("quality_score", 0.0) 
                    for key, data in enriched.get("shared_insights", {}).items()
                },
                "agent_dependencies": enriched.get("agent_dependencies", []),
                "cross_agent_patterns": self._identify_cross_agent_patterns(enriched)
            },
            "context_depth": {
                "user_intent": context.user_query,
                "analysis_scope": context.analysis_focus,
                "session_context": context.session_id,
                "timestamp": context.timestamp.isoformat(),
                "priority_level": getattr(context, 'priority', 1)
            },
            "data_completeness": self._assess_data_completeness(enriched),
            "enhancement_opportunities": self._identify_enhancement_opportunities(enriched)
        }
        
        return enriched
    
    def _identify_cross_agent_patterns(self, enriched: Dict[str, Any]) -> Dict[str, Any]:
        """Identify patterns across agent insights"""
        patterns = {
            "convergent_insights": [],
            "conflicting_views": [],
            "data_gaps": [],
            "quality_trends": {}
        }
        
        # Analyze shared insights for patterns
        shared_insights = enriched.get("shared_insights", {})
        if len(shared_insights) > 1:
            # Look for convergent themes
            patterns["convergent_insights"] = ["Multi-agent analysis available"]
            
            # Quality assessment across agents
            quality_scores = [
                data.get("quality_score", 0.0) 
                for data in shared_insights.values()
            ]
            if quality_scores:
                patterns["quality_trends"] = {
                    "average_quality": sum(quality_scores) / len(quality_scores),
                    "quality_range": f"{min(quality_scores):.2f} - {max(quality_scores):.2f}",
                    "high_quality_agents": len([q for q in quality_scores if q > 0.8])
                }
        
        return patterns
    
    def _assess_data_completeness(self, enriched: Dict[str, Any]) -> Dict[str, Any]:
        """Assess completeness of available data"""
        return {
            "shared_insights_count": len(enriched.get("shared_insights", {})),
            "data_sources_available": len(enriched.get("available_data_keys", [])),
            "agent_collaboration_level": "high" if len(enriched.get("shared_insights", {})) > 3 else "medium",
            "context_richness": "comprehensive" if enriched.get("shared_insights") else "building"
        }
    
    def _identify_enhancement_opportunities(self, enriched: Dict[str, Any]) -> List[str]:
        """Identify opportunities to enhance analysis"""
        opportunities = []
        
        shared_insights = enriched.get("shared_insights", {})
        
        if not shared_insights:
            opportunities.append("First agent - establishing baseline analysis")
        elif len(shared_insights) < 3:
            opportunities.append("Early stage - leverage existing insights for enhanced analysis")
        else:
            opportunities.append("Rich context - synthesize multi-agent insights for comprehensive analysis")
        
        return opportunities
    
    @time_execution
    @retry_async(max_retries=5, delay=2.0, backoff_factor=2.0, jitter=True)
    async def call_gemini_api(
        self, 
        prompt: str, 
        max_tokens: int = 8000,
        temperature: float = 0.7
    ) -> str:
        """
        Call Gemini API with retry logic and performance tracking
        
        Args:
            prompt: The prompt to send to Gemini
            max_tokens: Maximum tokens in response
            temperature: Response creativity (0-1)
            
        Returns:
            Generated response from Gemini
        """
        if not GENAI_AVAILABLE:
            raise ImportError("google-generativeai package not installed. Run: pip install google-generativeai")
        
        start_time = datetime.now()
        api_key = self.api_manager.get_optimal_key()
        
        try:
            # Configure Gemini
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # Generate response
            response = await asyncio.to_thread(
                model.generate_content,
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=temperature
                )
            )
            
            response_time = (datetime.now() - start_time).total_seconds()
            self.api_manager.record_performance(api_key, response_time, True)
            
            # Validate response
            if not hasattr(response, 'text') or not response.text:
                raise ValueError("Empty or invalid response from Gemini API")
            
            return response.text
            
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds()
            self.api_manager.record_performance(api_key, response_time, False)
            
            error_msg = str(e).lower()
            
            # Enhanced error logging with specific error types
            if '500 internal' in error_msg:
                self.logger.warning(f"Gemini API 500 Internal Server Error in {self.agent_id}: {e}")
            elif 'rate limit' in error_msg or 'quota' in error_msg:
                self.logger.warning(f"Gemini API rate limit/quota error in {self.agent_id}: {e}")
            elif 'timeout' in error_msg:
                self.logger.warning(f"Gemini API timeout in {self.agent_id}: {e}")
            elif any(auth_error in error_msg for auth_error in ['401', '403', 'unauthorized', 'forbidden']):
                self.logger.error(f"Gemini API authentication error in {self.agent_id}: {e}")
            else:
                self.logger.error(f"Gemini API error in {self.agent_id}: {e}")
            
            # Try to get next working key for certain error types
            if any(retry_worthy in error_msg for retry_worthy in [
                '500 internal', 'service unavailable', 'timeout', 'rate limit', 'quota'
            ]):
                next_key = self.api_manager.get_next_working_key()
                if next_key and next_key != api_key:
                    self.logger.info(f"Switching to alternative API key for retry: {next_key[:8]}...")
            
            raise
    
    async def store_result(
        self, 
        key: str, 
        data: Any, 
        quality_score: float = None
    ) -> None:
        """
        Store analysis result in shared memory with streaming
        
        Args:
            key: Storage key for the data
            data: Analysis data to store
            quality_score: Optional quality score (calculated if not provided)
        """
        if quality_score is None:
            if isinstance(data, dict):
                quality_score = calculate_quality_score(data)
            else:
                quality_score = 0.8  # Default for non-dict data
        
        await self.memory.store_with_streaming(
            key=key,
            value=data,
            agent_id=self.agent_id,
            quality_score=quality_score,
            stream=True
        )
    
    async def broadcast_status(self, status: str, message: str) -> None:
        """
        Broadcast status update via WebSocket
        
        Args:
            status: Status type (e.g., 'started', 'progress', 'completed')
            message: Status message
        """
        logger.info(f"🎯 Agent {self.agent_id} broadcasting status: {status} - {message}")
        from ..core.models import WebSocketMessage
        status_message = WebSocketMessage(
            type="agent_status", 
            data={
                "agent_id": self.agent_id,
                "status": status,
                "message": message,
                "timestamp": datetime.now().isoformat()
            }
        )
        logger.info(f"📢 Broadcasting agent status message: type={status_message.type}, agent={self.agent_id}")
        await self.memory._broadcast_update(status_message.to_json())
    
    async def stream_output(self, content: str, output_type: str = "analysis", quality_score: float = None):
        """
        Stream real-time output to frontend
        
        Args:
            content: Content to stream
            output_type: Type of output (analysis, progress, result)
            quality_score: Optional quality score for the output
        """
        logger.info(f"🔄 Agent {self.agent_id} streaming: {content[:100]}...")
        from ..core.models import WebSocketMessage
        output_message = WebSocketMessage(
            type="agent_output",
            data={
                "agent_id": self.agent_id,
                "content": content,
                "output_type": output_type,
                "quality_score": quality_score,
                "timestamp": datetime.now().isoformat()
            }
        )
        logger.info(f"📡 Broadcasting WebSocket message: type={output_message.type}, agent={self.agent_id}")
        await self.memory._broadcast_update(output_message.to_json())
    
    async def add_research_source(self, source: str, url: str, relevance: float = 0.0, summary: str = ""):
        """
        Add grounded research source with link
        
        Args:
            source: Name/title of the research source
            url: URL to the source
            relevance: Relevance score (0-100)
            summary: Brief summary of the source content
        """
        from ..core.models import WebSocketMessage
        source_message = WebSocketMessage(
            type="research_source",
            data={
                "agent_id": self.agent_id,
                "source": source,
                "url": url,
                "relevance": relevance,
                "summary": summary,
                "timestamp": datetime.now().isoformat()
            }
        )
        await self.memory._broadcast_update(source_message.to_json())
    
    def update_performance_metrics(self, execution_time: float, success: bool) -> None:
        """
        Update agent performance metrics
        
        Args:
            execution_time: Time taken for execution in seconds
            success: Whether the execution was successful
        """
        self.execution_count += 1
        self.total_execution_time += execution_time
        
        if success:
            self.success_count += 1
        else:
            self.error_count += 1
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get agent performance statistics"""
        if self.execution_count == 0:
            return {
                "agent_id": self.agent_id,
                "agent_type": self.agent_type.value,
                "execution_count": 0,
                "success_rate": 0.0,
                "average_execution_time": 0.0,
                "total_execution_time": 0.0
            }
        
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type.value,
            "execution_count": self.execution_count,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "success_rate": self.success_count / self.execution_count,
            "average_execution_time": self.total_execution_time / self.execution_count,
            "total_execution_time": self.total_execution_time
        }
    
    async def execute_analysis(self, context: AnalysisContext) -> AnalysisResult:
        """
        Execute the agent's analysis with full error handling and performance tracking
        
        Args:
            context: Analysis context
            
        Returns:
            AnalysisResult with the agent's findings
        """
        start_time = datetime.now()
        
        try:
            # Broadcast start status
            await self.broadcast_status(
                "started", 
                f"{self.agent_id.replace('_', ' ').title()} analysis started"
            )
            
            # Perform the analysis
            result = await self.analyze(context)
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            result.processing_time = execution_time
            
            # Update performance metrics
            self.update_performance_metrics(execution_time, True)
            
            # Broadcast completion status
            await self.broadcast_status(
                "completed",
                f"{self.agent_id.replace('_', ' ').title()} analysis completed"
            )
            
            self.logger.info(
                f"{self.agent_id} completed analysis for {context.ticker} "
                f"in {execution_time:.2f}s"
            )
            
            return result
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            self.update_performance_metrics(execution_time, False)
            
            # Broadcast error status
            await self.broadcast_status(
                "error",
                f"{self.agent_id.replace('_', ' ').title()} analysis failed: {str(e)}"
            )
            
            self.logger.error(f"{self.agent_id} analysis failed: {e}")
            
            return AnalysisResult(
                agent_id=self.agent_id,
                agent_type=self.agent_type,
                data={},
                quality_score=0.0,
                processing_time=execution_time,
                status=AnalysisStatus.FAILED,
                error_message=str(e)
            )
    
    def format_prompt(self, template: str, context: AnalysisContext, **kwargs) -> str:
        """
        Format prompt template with context data
        
        Args:
            template: Prompt template string
            context: Analysis context
            **kwargs: Additional template variables
            
        Returns:
            Formatted prompt string
        """
        return template.format(
            company_name=context.company_name,
            ticker=context.ticker,
            user_query=context.user_query,
            analysis_focus=", ".join(context.analysis_focus),
            timestamp=context.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            **kwargs
        )
    
    async def get_shared_data(self, key: str) -> Optional[Any]:
        """
        Get data from shared memory
        
        Args:
            key: Data key to retrieve
            
        Returns:
            Data value or None if not found
        """
        return self.memory.data.get(key)
    
    def validate_context(self, context: AnalysisContext) -> bool:
        """
        Validate analysis context
        
        Args:
            context: Analysis context to validate
            
        Returns:
            True if context is valid, False otherwise
        """
        if not context.company_name or not context.ticker:
            return False
        
        if not context.ticker.isalnum() and not any(c in context.ticker for c in '.-'):
            return False
        
        return True