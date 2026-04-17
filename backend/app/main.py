import asyncio
import redis.asyncio as aioredis
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from starlette.middleware.sessions import SessionMiddleware

from app.api.routes import api_router
from app.core.middleware import setup_cors
from app.core.config import settings

app = FastAPI(title="AsyncPDF Backend API",version="1.0.0",)
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    r = await aioredis.from_url("redis://localhost:6379/0")
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