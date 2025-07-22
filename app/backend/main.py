from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.backend.api.router import api_router
from app.backend.core.logging_config import setup_logging


# --- Logging Setup ---
setup_logging()
logger = logging.getLogger(name="main")
logger.info("Starting FastAPI App...")


# --- Lifespan Event Handler ---
@asynccontextmanager
async def lifespan(app:FastAPI):
    logger.info("Startup: initializing resources...")
    yield
    logger.info("Shutdown: cleaning up resources...")


# --- FastAPI App Setup ---
app = FastAPI(
    title="Movies You Didn't Watch",
    description="A Conversational movie recommender chatbot",
    version="1.0.0",
    docs_url="/docs",
    redoc_url=None,
    lifespan=lifespan
)

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Include Routers ---
app.include_router(api_router)


# --- Health Check ---
@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}
