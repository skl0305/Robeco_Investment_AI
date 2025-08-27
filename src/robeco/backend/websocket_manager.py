"""
WebSocket connection manager for real-time communication

Handles WebSocket connections, broadcasting, and connection lifecycle.
"""

import json
import logging
from typing import Dict, Set
import asyncio

from fastapi import WebSocket, WebSocketDisconnect

from ..core.memory import EnhancedSharedMemory
from ..core.models import WebSocketMessage

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self, shared_memory: EnhancedSharedMemory):
        self.active_connections: Dict[str, WebSocket] = {}
        self.connection_metadata: Dict[str, Dict] = {}
        self.shared_memory = shared_memory
        
    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept and manage a WebSocket connection"""
        await websocket.accept()
        
        self.active_connections[client_id] = websocket
        self.connection_metadata[client_id] = {
            "connected_at": asyncio.get_event_loop().time(),
            "messages_sent": 0,
            "last_activity": asyncio.get_event_loop().time()
        }
        
        # Add to shared memory
        await self.shared_memory.add_websocket_connection(websocket)
        
        logger.info(f"WebSocket connected: {client_id}")
        
        # Send welcome message
        welcome_message = WebSocketMessage(
            type="connection_established",
            data={
                "client_id": client_id,
                "message": "Connected to Robeco AI System",
                "system_status": "ready"
            },
            client_id=client_id
        )
        
        await self.send_personal_message(welcome_message.to_json(), client_id)
        
        # Broadcast connection update
        await self.broadcast_system_message({
            "type": "client_connected",
            "client_id": client_id,
            "total_connections": len(self.active_connections)
        })
        
        try:
            # Keep connection alive and handle messages
            await self._handle_connection(websocket, client_id)
        except WebSocketDisconnect:
            await self.disconnect(client_id)
        except Exception as e:
            logger.error(f"WebSocket error for {client_id}: {e}")
            await self.disconnect(client_id)
    
    async def _handle_connection(self, websocket: WebSocket, client_id: str):
        """Handle incoming WebSocket messages"""
        while True:
            try:
                # Wait for message from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Update activity timestamp
                self.connection_metadata[client_id]["last_activity"] = asyncio.get_event_loop().time()
                
                # Handle different message types
                await self._process_client_message(message, client_id)
                
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON from {client_id}")
            except Exception as e:
                logger.error(f"Error handling message from {client_id}: {e}")
                break
    
    async def _process_client_message(self, message: Dict, client_id: str):
        """Process incoming client messages"""
        message_type = message.get("type", "unknown")
        
        if message_type == "ping":
            # Respond to ping
            await self.send_personal_message({
                "type": "pong",
                "timestamp": asyncio.get_event_loop().time()
            }, client_id)
        
        elif message_type == "get_status":
            # Send system status
            await self.send_personal_message({
                "type": "system_status",
                "data": {
                    "active_connections": len(self.active_connections),
                    "memory_stats": self.shared_memory.get_memory_stats(),
                    "uptime": asyncio.get_event_loop().time() - self.connection_metadata[client_id]["connected_at"]
                }
            }, client_id)
        
        elif message_type == "subscribe":
            # Handle subscription to specific data types
            subscription_types = message.get("data", {}).get("types", [])
            logger.info(f"Client {client_id} subscribed to: {subscription_types}")
        
        else:
            logger.debug(f"Unknown message type from {client_id}: {message_type}")
    
    async def disconnect(self, client_id: str):
        """Disconnect a WebSocket client"""
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]
            
            # Remove from shared memory
            await self.shared_memory.remove_websocket_connection(websocket)
            
            # Clean up
            del self.active_connections[client_id]
            del self.connection_metadata[client_id]
            
            logger.info(f"WebSocket disconnected: {client_id}")
            
            # Broadcast disconnection
            await self.broadcast_system_message({
                "type": "client_disconnected", 
                "client_id": client_id,
                "total_connections": len(self.active_connections)
            })
    
    async def send_personal_message(self, message: Dict, client_id: str):
        """Send message to a specific client"""
        if client_id in self.active_connections:
            try:
                websocket = self.active_connections[client_id]
                await websocket.send_text(json.dumps(message))
                
                # Update metrics
                self.connection_metadata[client_id]["messages_sent"] += 1
                self.connection_metadata[client_id]["last_activity"] = asyncio.get_event_loop().time()
                
            except Exception as e:
                logger.error(f"Error sending message to {client_id}: {e}")
                await self.disconnect(client_id)
    
    async def broadcast_message(self, message: Dict, exclude_client: str = None):
        """Broadcast message to all connected clients"""
        disconnected_clients = []
        
        for client_id, websocket in self.active_connections.items():
            if exclude_client and client_id == exclude_client:
                continue
            
            try:
                await websocket.send_text(json.dumps(message))
                self.connection_metadata[client_id]["messages_sent"] += 1
                
            except Exception as e:
                logger.error(f"Error broadcasting to {client_id}: {e}")
                disconnected_clients.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected_clients:
            await self.disconnect(client_id)
    
    async def broadcast_system_message(self, message: Dict):
        """Broadcast system-level message"""
        system_message = {
            "type": "system_message",
            "timestamp": asyncio.get_event_loop().time(),
            **message
        }
        await self.broadcast_message(system_message)
    
    async def broadcast_agent_update(self, agent_id: str, update_data: Dict):
        """Broadcast agent-specific update"""
        agent_message = {
            "type": "agent_update",
            "agent_id": agent_id,
            "timestamp": asyncio.get_event_loop().time(),
            "data": update_data
        }
        await self.broadcast_message(agent_message)
    
    async def broadcast_progress_update(self, progress_data: Dict):
        """Broadcast progress update"""
        progress_message = {
            "type": "progress_update",
            "timestamp": asyncio.get_event_loop().time(),
            **progress_data
        }
        await self.broadcast_message(progress_message)
    
    async def disconnect_all(self):
        """Disconnect all clients (for shutdown)"""
        for client_id in list(self.active_connections.keys()):
            await self.disconnect(client_id)
    
    def get_connection_stats(self) -> Dict:
        """Get connection statistics"""
        current_time = asyncio.get_event_loop().time()
        
        return {
            "total_connections": len(self.active_connections),
            "active_clients": list(self.active_connections.keys()),
            "connection_details": {
                client_id: {
                    "connected_duration": current_time - meta["connected_at"],
                    "messages_sent": meta["messages_sent"],
                    "last_activity": current_time - meta["last_activity"]
                }
                for client_id, meta in self.connection_metadata.items()
            }
        }
    
    async def send_heartbeat(self):
        """Send heartbeat to all connections"""
        heartbeat_message = {
            "type": "heartbeat",
            "timestamp": asyncio.get_event_loop().time(),
            "server_status": "healthy"
        }
        await self.broadcast_message(heartbeat_message)