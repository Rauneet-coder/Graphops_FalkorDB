import sys
from pathlib import Path

# Ensure backend directory is in sys.path for direct module runs
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.falkordb import falkordb_client

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["System"])
async def health_check():
    falkor_ok = falkordb_client.ping()
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "database": {
            "type": "FalkorDB",
            "host": settings.FALKORDB_HOST,
            "port": settings.FALKORDB_PORT,
            "connected": falkor_ok,
        },
    }


@app.get("/", tags=["System"])
async def root():
    return {
        "message": "Welcome to GraphOps API",
        "docs": "/docs",
        "health": "/health",
    }
