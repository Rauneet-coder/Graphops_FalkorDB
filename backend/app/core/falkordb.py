"""Lifespan-owned, bounded synchronous client; call through the graph worker pool."""

import logging
from threading import RLock

from falkordb import FalkorDB
from redis.backoff import NoBackoff
from redis.exceptions import RedisError
from redis.retry import Retry

from app.core.config import Settings
from app.graph.runtime import initialize_graph, probe_graph

logger = logging.getLogger(__name__)


class FalkorDBClient:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._driver: FalkorDB | None = None
        self._initialized = False
        self._lock = RLock()

    @property
    def initialized(self) -> bool:
        return self._initialized

    def get_client(self) -> FalkorDB:
        with self._lock:
            if self._driver is None:
                self._driver = FalkorDB(
                    host=self.settings.FALKORDB_HOST,
                    port=self.settings.FALKORDB_PORT,
                    socket_connect_timeout=self.settings.FALKORDB_CONNECT_TIMEOUT_SECONDS,
                    socket_timeout=self.settings.FALKORDB_SOCKET_TIMEOUT_SECONDS,
