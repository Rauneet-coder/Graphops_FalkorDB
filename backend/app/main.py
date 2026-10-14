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
