from __future__ import annotations

import logging
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from .api import router
from .db import engine
from .models import Base

logger = logging.getLogger("plantpulse")
logging.basicConfig(level=logging.INFO, format="%(message)s")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    Base.metadata.create_all(engine)
    yield


app = FastAPI(
    title="PlantPulse",
    version="1.0.0",
    description=(
        "S&OP exception desk for a contact-lens network. Ranks stockout, overtime, "
        "forecast bias, and scrap by dollar impact and returns the action a planner should take."
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3009",
        "http://127.0.0.1:3009",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router, prefix="/api")


@app.middleware("http")
async def access_log(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    started = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - started) * 1000
    logger.info(
        '{"event":"request","id":"%s","method":"%s","path":"%s","status":%d,"ms":%.1f}',
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    response.headers["X-Request-ID"] = request_id
    return response


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/ready")
def ready() -> dict:
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return {"status": "ready"}
