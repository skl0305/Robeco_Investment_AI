"""
Enhanced memory system for Robeco AI agents

Provides shared memory, real-time streaming, and agent collaboration capabilities.
"""

import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
import numpy as np
from .models import AnalysisContext, WebSocketMessage

logger = logging.getLogger(__name__)


class EnhancedSharedMemory:
    """Advanced memory system with real-time streaming and agent collaboration"""
    
    def __init__(self):
        self.data: Dict[str, Any] = {}
        self.agent_contributions: Dict[str, List[str]] = {}
        self.streaming_updates: Dict[str, Any] = {}
        self.agent_dependencies: Dict[str, List[str]] = {}
        self.data_quality_scores: Dict[str, float] = {}
        self.update_timestamps: Dict[str, datetime] = {}
        self.websocket_connections: Set[Any] = set()
        
    async def store_with_streaming(
        self, 
        key: str, 
        value: Any, 
        agent_id: str, 
        quality_score: float = 1.0, 
        stream: bool = True
    ) -> None:
        """Store data with real-time streaming to connected clients"""
        self.data[key] = value
        self.data_quality_scores[key] = quality_score
        self.update_timestamps[key] = datetime.now()
        
        if agent_id not in self.agent_contributions:
            self.agent_contributions[agent_id] = []
        self.agent_contributions[agent_id].append(key)
        
        # Stream update to all connected clients
        if stream and self.websocket_connections:
            try:
                update_message = WebSocketMessage(
                    type="agent_update",
                    data={
                        "agent_id": agent_id,
                        "key": key,
                        "timestamp": self.update_timestamps[key].isoformat(),
                        "quality_score": quality_score,
                        "data_preview": self._create_data_preview(value)
                    }
                )
                await self._broadcast_update(update_message.to_json())
            except Exception as e:
                logger.warning(f"WebSocket streaming failed: {e}")
                # Continue without streaming to avoid blocking analysis
        
        logger.info(f"Agent {agent_id} stored {key} with quality score {quality_score}")
    
    def _create_data_preview(self, value: Any) -> str:
        """Create a preview of the data for streaming"""
        str_value = str(value)
        if len(str_value) > 200:
            return str_value[:200] + "..."
        return str_value
    
    async def _broadcast_update(self, message: Dict[str, Any]) -> None:
        """Broadcast update to all WebSocket connections"""
        logger.info(f"🔀 Broadcasting to {len(self.websocket_connections)} WebSocket connections")
        
        if not self.websocket_connections:
            logger.warning("⚠️ No WebSocket connections available for broadcasting")
            return
            
        disconnected = set()
        for websocket in self.websocket_connections:
            try:
                # Ensure message is properly formatted as JSON string
                if isinstance(message, dict):
                    # The message is already a dict, convert directly to JSON string
                    message_str = json.dumps(message, default=str)
                    logger.debug(f"📤 Sending message: {message_str[:200]}...")
                else:
                    message_str = str(message)
                
                # Send the JSON string to WebSocket
                await websocket.send_text(message_str)
                logger.debug(f"✅ Message sent successfully to WebSocket connection {id(websocket)}")
                
            except Exception as e:
                logger.warning(f"❌ Failed to send update to websocket {id(websocket)}: {e}")
                disconnected.add(websocket)
        
        # Clean up disconnected websockets
        if disconnected:
            logger.info(f"🧹 Cleaning up {len(disconnected)} disconnected WebSocket connections")
            self.websocket_connections -= disconnected
    
    def get_enriched_context(self, requesting_agent: str, context: AnalysisContext) -> Dict[str, Any]:
        """Get comprehensive context enriched by all other agents"""
        enriched_data = {
            "base_context": {
                "company_name": context.company_name,
                "ticker": context.ticker,
                "user_query": context.user_query,
                "analysis_focus": context.analysis_focus,
                "timestamp": context.timestamp.isoformat(),
                "session_id": context.session_id
            },
            "shared_insights": {},
            "data_quality_map": {},
            "agent_dependencies": self.agent_dependencies.get(requesting_agent, []),
            "available_data_keys": list(self.data.keys())
        }
        
        # Add all available insights from other agents
        for key, value in self.data.items():
            enriched_data["shared_insights"][key] = {
                "data": value,
                "quality_score": self.data_quality_scores.get(key, 1.0),
                "timestamp": self.update_timestamps.get(key, datetime.now()).isoformat()
            }
        
        return enriched_data
    
    def get_all_insights(self) -> Dict[str, Any]:
        """Get all stored insights with quality scores"""
        return {
            'data': self.data,
            'quality_scores': self.data_quality_scores,
            'update_timestamps': {
                k: v.isoformat() for k, v in self.update_timestamps.items()
            }
        }
    
    async def add_websocket_connection(self, websocket: Any) -> None:
        """Add a WebSocket connection for streaming"""
        self.websocket_connections.add(websocket)
        logger.info(f"✅ WebSocket connection added. Total connections: {len(self.websocket_connections)}")
        logger.info(f"📍 Connection object: {type(websocket)} - {id(websocket)}")
        
    async def remove_websocket_connection(self, websocket: Any) -> None:
        """Remove a WebSocket connection"""
        self.websocket_connections.discard(websocket)
        logger.info(f"❌ WebSocket connection removed. Total connections: {len(self.websocket_connections)}")
        logger.info(f"📍 Removed connection: {type(websocket)} - {id(websocket)}")
    
    def get_agent_contributions(self, agent_id: str) -> List[str]:
        """Get all data keys contributed by a specific agent"""
        return self.agent_contributions.get(agent_id, [])
    
    def get_data_quality_score(self, key: str) -> float:
        """Get quality score for specific data"""
        return self.data_quality_scores.get(key, 0.0)
    
    def get_latest_data(self, limit: int = 10) -> Dict[str, Any]:
        """Get most recently updated data"""
        sorted_keys = sorted(
            self.update_timestamps.keys(),
            key=lambda k: self.update_timestamps[k],
            reverse=True
        )[:limit]
        
        return {
            key: {
                "data": self.data[key],
                "quality_score": self.data_quality_scores.get(key, 1.0),
                "timestamp": self.update_timestamps[key].isoformat()
            }
            for key in sorted_keys
        }
    
    def clear_agent_data(self, agent_id: str) -> None:
        """Clear all data from a specific agent"""
        if agent_id in self.agent_contributions:
            for key in self.agent_contributions[agent_id]:
                self.data.pop(key, None)
                self.data_quality_scores.pop(key, None)
                self.update_timestamps.pop(key, None)
            self.agent_contributions.pop(agent_id, None)
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory system statistics"""
        return {
            "total_data_items": len(self.data),
            "total_agents": len(self.agent_contributions),
            "active_connections": len(self.websocket_connections),
            "average_quality_score": np.mean(list(self.data_quality_scores.values())) if self.data_quality_scores else 0.0,
            "latest_update": max(self.update_timestamps.values()).isoformat() if self.update_timestamps else None,
            "agent_contributions": {
                agent: len(contributions) 
                for agent, contributions in self.agent_contributions.items()
            }
        }


class APIKeyManager:
    """Enhanced API key management with performance tracking"""
    
    def __init__(self, api_keys: Optional[List[str]] = None):
        self.api_keys = api_keys or []
        self.current_index = 0
        self.usage_count: Dict[str, int] = {}
        self.error_count: Dict[str, int] = {}
        self.response_times: Dict[str, List[float]] = {}
        self.rate_limits: Dict[str, datetime] = {}
        
        for key in self.api_keys:
            self.usage_count[key] = 0
            self.error_count[key] = 0
            self.response_times[key] = []
            self.rate_limits[key] = datetime.now()
    
    def get_optimal_key(self) -> str:
        """Get the best performing available API key"""
        if not self.api_keys:
            raise ValueError("No API keys configured. Please check config.py GEMINI_API_KEYS.")
            
        available_keys = []
        current_time = datetime.now()
        
        for i, key in enumerate(self.api_keys):
            # Check if key is rate limited
            if current_time > self.rate_limits[key]:
                error_rate = self.error_count[key] / max(1, self.usage_count[key])
                avg_response_time = (
                    np.mean(self.response_times[key][-10:]) 
                    if self.response_times[key] else 1.0
                )
                
                # Score based on error rate and response time
                score = 1.0 - (error_rate * 0.7 + avg_response_time * 0.3 / 10.0)
                available_keys.append((key, score, i))
        
        if available_keys:
            # Select best key
            best_key, _, index = max(available_keys, key=lambda x: x[1])
            self.current_index = index
            self.usage_count[best_key] += 1
            return best_key
        else:
            # Fallback to round-robin - ensure we have keys
            if not self.api_keys:
                raise ValueError("No API keys available for fallback.")
            key = self.api_keys[self.current_index % len(self.api_keys)]
            self.usage_count[key] += 1
            self.current_index = (self.current_index + 1) % len(self.api_keys)
            return key
    
    def record_performance(self, key: str, response_time: float, success: bool) -> None:
        """Record API key performance metrics"""
        self.response_times[key].append(response_time)
        if not success:
            self.error_count[key] += 1
            # Rate limit for 30 seconds if too many errors
            if self.error_count[key] / max(1, self.usage_count[key]) > 0.5:
                self.rate_limits[key] = datetime.now() + timedelta(seconds=30)
                logger.warning(f"API key rate limited due to high error rate: {key[:8]}...")
    
    def get_key_stats(self) -> Dict[str, Any]:
        """Get statistics for all API keys"""
        stats = {}
        for key in self.api_keys:
            error_rate = self.error_count[key] / max(1, self.usage_count[key])
            avg_response_time = (
                np.mean(self.response_times[key][-10:]) 
                if self.response_times[key] else 0.0
            )
            
            stats[key[:8] + "..."] = {
                "usage_count": self.usage_count[key],
                "error_count": self.error_count[key],
                "error_rate": error_rate,
                "avg_response_time": avg_response_time,
                "is_rate_limited": datetime.now() < self.rate_limits[key]
            }
        
        return stats
    
    def reset_key_stats(self, key: Optional[str] = None) -> None:
        """Reset statistics for a specific key or all keys"""
        keys_to_reset = [key] if key else self.api_keys
        
        for api_key in keys_to_reset:
            if api_key in self.usage_count:
                self.usage_count[api_key] = 0
                self.error_count[api_key] = 0
                self.response_times[api_key] = []
                self.rate_limits[api_key] = datetime.now()