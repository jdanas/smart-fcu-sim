from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
import json
import asyncio

router = APIRouter(tags=["websocket"])


class ConnectionManager:
    """Manages WebSocket connections."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        """Send message to all connected clients."""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)

        # Clean up disconnected clients
        for conn in disconnected:
            self.disconnect(conn)

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send message to specific client."""
        try:
            await websocket.send_json(message)
        except Exception:
            self.disconnect(websocket)


# Global connection manager
manager = ConnectionManager()


@router.websocket("/ws/sensors")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time sensor data.

    Message types received from server:
    - reading: New sensor reading
    - prediction: Updated prediction
    - device_discovered: New device detected
    - device_status: Device status change
    """
    await manager.connect(websocket)

    try:
        while True:
            # Keep connection alive and handle any client messages
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=60.0)
                # Handle ping/pong or other client messages
                if data == "ping":
                    await websocket.send_text("pong")
            except asyncio.TimeoutError:
                # Send keepalive
                try:
                    await websocket.send_json({"type": "keepalive"})
                except Exception:
                    break
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)


async def broadcast_sensor_reading(data: dict):
    """Broadcast a sensor reading to all connected clients."""
    await manager.broadcast(data)


async def broadcast_device_event(data: dict):
    """Broadcast a device discovery/status event to all clients."""
    await manager.broadcast(data)


async def broadcast_prediction(data: dict):
    """Broadcast a prediction update to all clients."""
    await manager.broadcast(data)
