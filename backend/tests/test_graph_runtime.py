import os
from uuid import uuid4

import pytest
from app.core.config import Settings
from app.core.falkordb import FalkorDBClient
from redis.exceptions import ResponseError


@pytest.fixture
def live_graph(require_live_graph):
    graph_id = 'graphops_test_stage1_' + uuid4().hex
    client = FalkorDBClient(Settings(_env_file=None, FALKORDB_GRAPH=graph_id))
    try:
        assert client.initialize(), 'Required live FalkorDB initialization failed'
        yield client
    finally:
        # Never use configured/default demo graph for integration cleanup.
        assert graph_id.startswith('graphops_test_stage1_') and graph_id != 'graphops'
        try:
            if client.initialized:
                # DEL is idempotent even for a graph without durable writes.
                # GRAPH.DELETE of that empty key errors during AOF replay on
                # server 6.0.2. This targets only the generated test graph key.
                client.get_client().connection.delete(graph_id)
        finally:
            client.close()


def test_live_cypher_repeatable_initialization_preserves_data(live_graph):
    graph = live_graph.get_graph()
    assert graph.ro_query('MATCH (n) RETURN count(n)', timeout=500).result_set == [[0]]
    graph.query('CREATE (:InfrastructureProbe {id: $id})', params={'id': 'preserve-me'}, timeout=500)
    # Simulate a new process initializing the same persisted graph.
    restarted = FalkorDBClient(live_graph.settings)
    try:
        assert restarted.initialize()
        assert restarted.is_ready()
        assert restarted.get_graph().ro_query(
            'MATCH (n:InfrastructureProbe) RETURN n.id', timeout=500,
        ).result_set == [['preserve-me']]
    finally:
        restarted.close()


def test_live_probe_and_read_only_enforcement(live_graph):
    assert live_graph.is_ready()
    with pytest.raises(ResponseError):
        live_graph.get_graph().ro_query('CREATE (:MustNotExist)', timeout=500)
    assert live_graph.get_graph().ro_query('MATCH (n) RETURN count(n)', timeout=500).result_set == [[0]]


def test_ordinary_redis_cannot_become_ready(require_live_graph):
    redis_host = os.environ.get('PLAIN_REDIS_HOST')
    assert redis_host, '--live-graph requires PLAIN_REDIS_HOST for the non-graph negative control'
    client = FalkorDBClient(Settings(_env_file=None, FALKORDB_HOST=redis_host))
    try:
        assert client.get_client().connection.ping() is True
        assert client.initialize() is False
        assert client.is_ready() is False
    finally:
        client.close()
