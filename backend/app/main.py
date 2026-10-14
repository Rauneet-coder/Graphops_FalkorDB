from collections.abc import Callable
from contextlib import asynccontextmanager

import anyio
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import Settings
from app.core.falkordb import FalkorDBClient


def create_app(
    settings: Settings | None = None,
    client_factory: Callable[[Settings], FalkorDBClient] = FalkorDBClient,
) -> FastAPI:
    config = settings if settings is not None else Settings()

    @asynccontextmanager
    async def lifespan(application: FastAPI):
        client = client_factory(config)
        limiter = anyio.CapacityLimiter(config.GRAPH_WORKERS)
        application.state.falkordb = client
        application.state.graph_limiter = limiter

        async def initialize_until_available() -> None:
            while not await anyio.to_thread.run_sync(client.initialize, limiter=limiter):
                await anyio.sleep(config.GRAPH_INIT_RETRY_SECONDS)

        try:
            async with anyio.create_task_group() as tasks:
                tasks.start_soon(initialize_until_available)
                try:
                    yield
                finally:
                    tasks.cancel_scope.cancel()
        finally:
            await anyio.to_thread.run_sync(client.close, limiter=limiter)

    application = FastAPI(
        title=config.PROJECT_NAME,
        version=config.VERSION,
        lifespan=lifespan,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=config.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )

    @application.get("/health/live", tags=["System"])
    async def liveness():
        return {"status": "alive", "service": config.PROJECT_NAME, "version": config.VERSION}

    @application.get("/health", tags=["System"])
    @application.get("/health/ready", tags=["System"])
    async def readiness(request: Request, response: Response):
        client = getattr(request.app.state, "falkordb", None)
        ready = False
        if client is not None:
            ready = await anyio.to_thread.run_sync(
                client.is_ready, limiter=request.app.state.graph_limiter
            )
        initialized = client is not None and client.initialized
        response.status_code = 200 if ready else 503
        return {
            "status": "ready" if ready else "not_ready",
            "service": config.PROJECT_NAME,
            "version": config.VERSION,
            "database": {"type": "FalkorDB", "graph_query_capable": ready},
            "initialization": {
                "scope": "infrastructure",
                "completed": initialized,
                "demo_data_loaded": False,
            },
        }

    @application.get("/", tags=["System"])
    async def root():
        return {
            "message": "Welcome to GraphOps API",
            "docs": "/docs",
            "liveness": "/health/live",
            "readiness": "/health/ready",
        }

    return application


app = create_app()
