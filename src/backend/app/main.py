# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from app.config import get_settings
from app.database import init_db
from app.auth.router import router as auth_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown (cleanup if needed)


app = FastAPI(
    title="Meu Spotify API",
    description="Backend para painel pessoal do Spotify",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gzip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Routers
app.include_router(auth_router)


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "meu-spotify-api"}


@app.get("/")
async def root():
    return {"message": "Meu Spotify API", "docs": "/docs", "version": "0.1.0"}