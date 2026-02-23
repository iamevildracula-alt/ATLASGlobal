from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.core.event_bus import broadcaster
import asyncio
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.websocket("/live")
async def telemetry_websocket(websocket: WebSocket):
    await websocket.accept()
    queue = broadcaster.subscribe()
    
    try:
        while True:
            # Wait for data from the broadcaster
            data = await queue.get()
            await websocket.send_text(data)
    except WebSocketDisconnect:
        broadcaster.unsubscribe(queue)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        broadcaster.unsubscribe(queue)
    finally:
        # Avoid closing an already closed socket
        try:
            await websocket.close()
        except:
            pass
