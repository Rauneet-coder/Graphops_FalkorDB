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
                    max_connections=self.settings.GRAPH_WORKERS,
                    retry=Retry(NoBackoff(), 0),
                )
            return self._driver

    def get_graph(self):
        return self.get_client().select_graph(self.settings.FALKORDB_GRAPH)

    def initialize(self) -> bool:
        """Create an empty graph if necessary, without loading domain data."""
        with self._lock:
            if self._initialized:
                return True
            try:
                initialize_graph(self.get_graph(), self.settings.FALKORDB_QUERY_TIMEOUT_MS)
            except (RedisError, OSError, RuntimeError, AttributeError) as exc:
                logger.warning("Graph initialization unavailable: %s", type(exc).__name__)
                return False
            self._initialized = True
            return True

    def is_ready(self) -> bool:
        """Readiness never creates graphs and never substitutes Redis PING."""
        if not self._initialized:
            return False
        try:
            probe_graph(self.get_graph(), self.settings.FALKORDB_QUERY_TIMEOUT_MS)
        except (RedisError, OSError, RuntimeError, AttributeError) as exc:
            logger.warning("Graph capability unavailable: %s", type(exc).__name__)
            # Empty graph initialization has no durable write to replay in AOF.
            # After replacement the lifespan worker must initialize again.
            # Readiness itself remains read-only and reports this failure as 503.
            self._initialized = False
            return False
        return True

    def close(self) -> None:
        with self._lock:
            if self._driver is not None:
                self._driver.connection.close()
                self._driver.connection.connection_pool.disconnect()
                self._driver = None
            self._initialized = False
