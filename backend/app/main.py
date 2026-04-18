import asyncio
import redis.asyncio as aioredis
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from starlette.middleware.sessions import SessionMiddleware

from app.api.routes import api_router
from app.core.middleware import setup_cors
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AsyncPDF Backend API", version="1.0.0")

# Session management for OAuth state
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.secret_key,
    session_cookie="asyncdoc_session",
    same_site="lax",
    https_only=True if settings.frontend_url.startswith("https") else False
)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    r = await aioredis.from_url(settings.redis_url)
    pubsub = r.pubsub()
    await pubsub.psubscribe("task:*")

    async def listen_to_redis():
        try:
            async for message in pubsub.listen():
                if message["type"] == "pmessage":
                    data = message["data"].decode("utf-8")
                    await websocket.send_text(data)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print("Redis listen error:", e)

    task = asyncio.create_task(listen_to_redis())

    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming data if necessary
    except WebSocketDisconnect:
        print("Client disconnected")
    finally:
        task.cancel()
        try:
            await pubsub.unsubscribe("task:*")
            await pubsub.close()
            await r.aclose()
        except:
            pass


setup_cors(app)

app.include_router(api_router)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/debug/settings")
def debug_settings():
    return {
        "google_redirect_uri": settings.google_redirect_uri,
        "frontend_url": settings.frontend_url,
        "is_https": settings.frontend_url.startswith("https"),
        "client_id": settings.google_client_id[:10] + "..." if settings.google_client_id else None
    }