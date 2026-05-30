import json
import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import List

from dotenv import load_dotenv
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

START_TIME = datetime.utcnow()

active_websockets: List[WebSocket] = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("=" * 60)
    logger.info("ShieldNet AI Platform - Starting up...")
    logger.info("=" * 60)

    from models.database import init_db
    try:
        init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.warning(f"Database init skipped (SQLite fallback): {e}")

    from scripts.seed_data import seed_database
    try:
        seed_database()
        logger.info("Seed data loaded")
    except Exception as e:
        logger.warning(f"Seed data loading issue: {e}")

    from ml.threat_detection import threat_detection_ml
    from ml.risk_scoring import risk_scoring_ml
    from ml.fraud_detection import fraud_detection_ml
    from ml.nlp_threat_intel import nlp_threat_intel

    try:
        logger.info("Training ML models...")
        threat_detection_ml.train()
        risk_scoring_ml.train()
        fraud_detection_ml.train()
        nlp_threat_intel.train()
        logger.info("All ML models trained successfully")
    except Exception as e:
        logger.error(f"ML model training failed: {e}")

    logger.info("ShieldNet API is ready")
    yield

    logger.info("ShieldNet shutting down...")
    for ws in active_websockets:
        try:
            await ws.close()
        except Exception:
            pass
    active_websockets.clear()


app = FastAPI(
    title="ShieldNet API",
    description="AI-Powered Decentralized Cybersecurity & Fintech Intelligence Platform",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "path": request.url.path,
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "detail": "Not found",
            "path": request.url.path,
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


from api.routes import router as api_router
app.include_router(api_router)


@app.get("/")
async def root():
    uptime = (datetime.utcnow() - START_TIME).total_seconds()
    return {
        "name": "ShieldNet API",
        "version": "1.0.0",
        "description": "AI-Powered Decentralized Cybersecurity & Fintech Intelligence Platform",
        "status": "operational",
        "uptime_seconds": int(uptime),
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "health": "GET /api/v1/health",
            "threats": "GET /api/v1/threats",
            "dashboard": "GET /api/v1/dashboard/stats",
            "network": "GET /api/v1/network/status",
            "auth": "POST /api/v1/auth/login",
            "websocket": "WS /ws",
        },
    }


@app.get("/health")
async def root_health():
    return {
        "status": "healthy",
        "service": "ShieldNet",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_websockets.append(websocket)
    logger.info(f"WebSocket client connected. Total: {len(active_websockets)}")

    try:
        await websocket.send_json({
            "type": "connection_established",
            "data": {
                "message": "Connected to ShieldNet real-time feed",
                "timestamp": datetime.utcnow().isoformat(),
            },
        })

        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                msg_type = message.get("type", "ping")

                if msg_type == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "data": {"timestamp": datetime.utcnow().isoformat()},
                    })
                elif msg_type == "subscribe":
                    channels = message.get("channels", ["all"])
                    await websocket.send_json({
                        "type": "subscribed",
                        "data": {"channels": channels, "status": "active"},
                    })
                elif msg_type == "get_status":
                    from services.blockchain_service import blockchain_service
                    await websocket.send_json({
                        "type": "status_update",
                        "data": {
                            "gas_prices": blockchain_service.get_gas_prices(),
                            "timestamp": datetime.utcnow().isoformat(),
                        },
                    })
                else:
                    await websocket.send_json({
                        "type": "echo",
                        "data": message,
                    })
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "data": {"message": "Invalid JSON format"},
                })

    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        if websocket in active_websockets:
            active_websockets.remove(websocket)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=os.getenv("ENV", "development") == "development",
        log_level="info",
    )
