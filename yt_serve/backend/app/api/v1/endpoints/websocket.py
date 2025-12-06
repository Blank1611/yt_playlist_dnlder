"""
WebSocket endpoints for real-time updates
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set
import json
import asyncio

router = APIRouter()

# Active WebSocket connections
active_connections: Dict[int, Set[WebSocket]] = {}

class ConnectionManager:
    """Manage WebSocket connections"""
    
    def __init__(self):
        self.active_connections: Dict[int, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, job_id: int):
        """Connect a WebSocket for a specific job"""
        await websocket.accept()
        if job_id not in self.active_connections:
            self.active_connections[job_id] = set()
        self.active_connections[job_id].add(websocket)
    
    def disconnect(self, websocket: WebSocket, job_id: int):
        """Disconnect a WebSocket"""
        if job_id in self.active_connections:
            self.active_connections[job_id].discard(websocket)
            if not self.active_connections[job_id]:
                del self.active_connections[job_id]
    
    async def send_message(self, message: dict, job_id: int):
        """Send message to all connections for a job"""
        if job_id in self.active_connections:
            disconnected = set()
            for connection in self.active_connections[job_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    disconnected.add(connection)
            
            # Remove disconnected connections
            for conn in disconnected:
                self.disconnect(conn, job_id)
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connections"""
        for job_id in list(self.active_connections.keys()):
            await self.send_message(message, job_id)

manager = ConnectionManager()

@router.websocket("/logs/{job_id}")
async def websocket_logs(websocket: WebSocket, job_id: int):
    """WebSocket endpoint for real-time job logs"""
    await manager.connect(websocket, job_id)
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            # Echo back for ping/pong
            await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        manager.disconnect(websocket, job_id)

@router.websocket("/progress/{job_id}")
async def websocket_progress(websocket: WebSocket, job_id: int):
    """WebSocket endpoint for real-time progress updates"""
    await manager.connect(websocket, job_id)
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        manager.disconnect(websocket, job_id)

# Helper function to send updates (called from background tasks)
async def send_log_update(job_id: int, log_message: str):
    """Send log update to connected clients"""
    await manager.send_message({
        "type": "log",
        "message": log_message
    }, job_id)

async def send_progress_update(job_id: int, progress: float, completed: int, total: int):
    """Send progress update to connected clients"""
    await manager.send_message({
        "type": "progress",
        "progress": progress,
        "completed": completed,
        "total": total
    }, job_id)
