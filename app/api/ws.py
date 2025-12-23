from typing import Dict, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from json import dumps

ws_router = APIRouter()

class ConnectionManager:
    """Mantiene conexiones por session_id."""
    def __init__(self):
        self.active: Dict[str, Set[WebSocket]] = {}

    async def connect(self, session_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active.setdefault(session_id, set()).add(websocket)

    def disconnect(self, session_id: str, websocket: WebSocket):
        peers = self.active.get(session_id)
        if not peers:
            return
        peers.discard(websocket)
        if not peers:
            self.active.pop(session_id, None)

    async def broadcast(self, session_id: str, payload: dict):
        peers = self.active.get(session_id, set())
        if not peers:
            return
        text = dumps(payload, ensure_ascii=False)
        for ws in list(peers):
            try:
                await ws.send_text(text)
            except Exception:
                self.disconnect(session_id, ws)

manager = ConnectionManager()

@ws_router.websocket("/ws/messages/{session_id}")
async def ws_messages(websocket: WebSocket, session_id: str):
    await manager.connect(session_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(session_id, websocket)