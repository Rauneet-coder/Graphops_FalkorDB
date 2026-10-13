import logging

from app.core.config import settings

logger = logging.getLogger("graphops.falkordb")

try:
    from falkordb import FalkorDB
    from redis.exceptions import RedisError
except ImportError:
    FalkorDB = None  # type: ignore
    RedisError = Exception  # type: ignore


class FalkorDBClient:
    def __init__(self):
        self._driver: object | None = None

    def get_client(self):
        if FalkorDB is None:
            raise RuntimeError(
                "falkordb package is not installed. Install with 'pip install falkordb'."
            )
        if self._driver is None:
            self._driver = FalkorDB(
                host=settings.FALKORDB_HOST,
                port=settings.FALKORDB_PORT,
            )
        return self._driver

    def get_graph(self, graph_name: str | None = None):
        client = self.get_client()
        target_graph = graph_name or settings.FALKORDB_GRAPH
        return client.select_graph(target_graph)

    def ping(self) -> bool:
        if FalkorDB is None:
            return False
        try:
            client = self.get_client()
            if hasattr(client, "connection"):
                return bool(client.connection.ping())
            return True
        except (RedisError, ConnectionError, TimeoutError, OSError, RuntimeError) as exc:
            logger.debug("FalkorDB ping failed: %s", exc)
            # Reset driver so next call retries connection fresh
            self._driver = None
            return False


falkordb_client = FalkorDBClient()
