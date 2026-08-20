# app/main.py
import logging
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.actions.router import router as actions_router
from app.auth.router import router as auth_router
from app.config import get_settings
from app.database import init_db
from app.library.router import router as library_router
from app.playlists.router import router as playlists_router
from app.users.router import router as users_router

settings = get_settings()

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.ENVIRONMENT == "production" else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Meu Spotify API...")
    await init_db()
    logger.info("Database initialized")
    yield
    # Shutdown
    logger.info("Shutting down Meu Spotify API...")


app = FastAPI(
    title="Meu Spotify API",
    description="Backend para painel pessoal do Spotify - Organize, analise e gerencie sua biblioteca",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
    openapi_url="/openapi.json" if settings.ENVIRONMENT != "production" else None,
)

# Request ID middleware for tracing
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4())[:8])
    start_time = time.time()

    # Add request_id to request state for logging
    request.state.request_id = request_id

    response = await call_next(request)

    process_time = time.time() - start_time
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{process_time:.4f}"

    logger.info(
        f"req_id={request_id} method={request.method} path={request.url.path} "
        f"status={response.status_code} duration={process_time:.4f}s"
    )

    return response


# Global exception handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    request_id = getattr(request.state, "request_id", "unknown")
    logger.warning(f"req_id={request_id} HTTP {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "request_id": request_id},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    request_id = getattr(request.state, "request_id", "unknown")
    logger.warning(f"req_id={request_id} Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Erro de validação",
            "errors": exc.errors(),
            "request_id": request_id,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", "unknown")
    logger.exception(f"req_id={request_id} Unhandled error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Erro interno do servidor" if settings.ENVIRONMENT == "production" else str(exc),
            "request_id": request_id,
        },
    )


# CORS - configured for credentials (cookies)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,  # Critical for cookies
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Process-Time"],
)

# Gzip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Routers
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(playlists_router, prefix="/playlists", tags=["playlists"])
app.include_router(library_router, prefix="/library", tags=["library"])
app.include_router(actions_router, prefix="/actions", tags=["actions"])


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint for load balancers / monitoring."""
    return {
        "status": "ok",
        "service": "meu-spotify-api",
        "version": "0.1.0",
        "environment": settings.ENVIRONMENT,
    }


@app.get("/health/ready", tags=["health"])
async def readiness_check():
    """Readiness check - verifies DB and Redis connectivity."""
    import redis.asyncio as redis

    from app.database import engine

    checks = {}

    # Check PostgreSQL
    try:
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        checks["database"] = "ok"
    except Exception as e:
        checks["database"] = f"error: {e}"

    # Check Redis
    try:
        r = redis.from_url(settings.REDIS_URL)
        await r.ping()
        await r.close()
        checks["redis"] = "ok"
    except Exception as e:
        checks["redis"] = f"error: {e}"

    all_healthy = all(v == "ok" for v in checks.values())

    return JSONResponse(
        status_code=status.HTTP_200_OK if all_healthy else status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "status": "ready" if all_healthy else "not_ready",
            "checks": checks,
        },
    )


@app.get("/", tags=["root"])
async def root():
    return {
        "message": "Meu Spotify API",
        "description": "Backend para painel pessoal do Spotify - Seu Spotify, do seu jeito",
        "docs": "/docs",
        "version": "0.1.0",
        "health": "/health",
    }
