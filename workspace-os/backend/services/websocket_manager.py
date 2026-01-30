"""
WebSocket connection manager for real-time updates
"""
from typing import List
from fastapi import WebSocket
import json

class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_personal(self, message: dict, websocket: WebSocket):
        await websocket.send_text(json.dumps(message))

    async def broadcast(self, message: dict):
        """Send message to all connected clients"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except:
                disconnected.append(connection)

        # Clean up disconnected
        for conn in disconnected:
            self.disconnect(conn)

    async def broadcast_file_event(self, event_type: str, path: str, details: dict = None):
        """Broadcast a file system event"""
        await self.broadcast({
            "type": "file_event",
            "event": event_type,
            "path": path,
            "details": details or {}
        })

    async def broadcast_activity(self, activity: dict):
        """Broadcast a new activity"""
        await self.broadcast({
            "type": "activity",
            "data": activity
        })

    @property
    def connection_count(self):
        return len(self.active_connections)
