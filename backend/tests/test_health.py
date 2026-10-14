import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from app.core.config import Settings
from app.core.falkordb import FalkorDBClient
from app.main import create_app
from fastapi.testclient import TestClient
from pydantic import ValidationError
from redis.exceptions import ResponseError


def config(**overrides):
    return Settings(_env_file=None, GRAPH_INIT_RETRY_SECONDS=0.05, **overrides)


class FakeClient:
    def __init__(self):
        self.initialized = False
        self.available = True
        self.initialization_available = True
        self.closed = False
        self.probe_gate = None
        self.probe_entered = threading.Event()

    def initialize(self):
        self.initialized = self.initialization_available
        return self.initialized

    def is_ready(self):
        self.probe_entered.set()
        if self.probe_gate is not None:
            assert self.probe_gate.wait(timeout=2)
        return self.initialized and self.available

    def close(self):
        self.closed = True


def wait_ready(http):
    for _ in range(100):
        response = http.get('/health/ready')
        if response.status_code == 200:
            return response
        time.sleep(0.01)
    pytest.fail('Readiness did not recover')


def test_liveness_and_readiness_before_lifespan():
    http = TestClient(create_app(config()))
    assert http.get('/health/live').json()['status'] == 'alive'
    assert http.get('/health/ready').status_code == 503
    assert http.get('/health').status_code == 503
    assert http.get('/').json()['readiness'] == '/health/ready'


def test_failure_recovery_and_shutdown():
    fake = FakeClient()
    with TestClient(create_app(config(), lambda _: fake)) as http:
        assert wait_ready(http).json()['initialization'] == {
            'scope': 'infrastructure', 'completed': True, 'demo_data_loaded': False,
        }
        fake.available = False
        for path in ('/health', '/health/ready'):
            response = http.get(path)
            assert response.status_code == 503
            assert response.json()['database']['graph_query_capable'] is False
        assert http.get('/health/live').status_code == 200
        fake.available = True
        wait_ready(http)
    assert fake.closed


def test_initialization_retries_without_false_readiness():
    fake = FakeClient()
    fake.initialization_available = False
    with TestClient(create_app(config(), lambda _: fake)) as http:
        assert http.get('/health/ready').status_code == 503
        assert http.get('/health/ready').json()['initialization']['completed'] is False
        fake.initialization_available = True
        wait_ready(http)


def test_database_probe_does_not_block_event_loop():
    fake = FakeClient()
    with TestClient(create_app(config(), lambda _: fake)) as http:
        wait_ready(http)
        fake.probe_entered.clear()
        fake.probe_gate = threading.Event()
        with ThreadPoolExecutor(max_workers=1) as workers:
            pending = workers.submit(http.get, '/health/ready')
            try:
                assert fake.probe_entered.wait(timeout=1)
                assert http.get('/health/live').status_code == 200
            finally:
                fake.probe_gate.set()
            assert pending.result(timeout=2).status_code == 200


@pytest.mark.parametrize('value', [
    '[invalid', '[3]', '[]', '', '*', 'http://x/path', 'https://user:pass@x',
    'https://x:999999', '{"origin":"http://x"}', 'http://a,', ['http://x', 3],
])
def test_invalid_cors(value):
    with pytest.raises(ValidationError):
        config(CORS_ORIGINS=value)


def test_cors_from_environment(monkeypatch):
    monkeypatch.setenv('CORS_ORIGINS', '["https://example.com","http://localhost:3000"]')
    assert config().CORS_ORIGINS == ['https://example.com', 'http://localhost:3000']
    monkeypatch.setenv('CORS_ORIGINS', '[invalid')
    with pytest.raises(ValidationError):
        config()


def test_csv_cors():
    assert config(CORS_ORIGINS='https://a.example, http://localhost:3000').CORS_ORIGINS == [
        'https://a.example', 'http://localhost:3000',
    ]


def test_invalid_timeout_order():
    with pytest.raises(ValidationError):
        config(FALKORDB_SOCKET_TIMEOUT_SECONDS=0.1)


def test_client_uses_graph_capability_bounded_timeouts_and_closes(monkeypatch):
    driver = MagicMock()
    graph = driver.select_graph.return_value
    graph.query.return_value.result_set = [[1]]
    graph.ro_query.return_value.result_set = [[1]]
    factory = MagicMock(return_value=driver)
    monkeypatch.setattr('app.core.falkordb.FalkorDB', factory)
    client = FalkorDBClient(config())
    assert client.is_ready() is False
    assert client.initialize() is True
    assert client.is_ready() is True
    assert factory.call_args.kwargs['socket_connect_timeout'] == 1
    assert factory.call_args.kwargs['socket_timeout'] == 2
    assert factory.call_args.kwargs['max_connections'] == 4
    assert graph.ro_query.call_args.kwargs['timeout'] == 500
    driver.connection.ping.assert_not_called()
    graph.ro_query.side_effect = ResponseError('unknown command GRAPH.RO_QUERY')
    assert client.is_ready() is False
    graph.ro_query.side_effect = None
    assert client.is_ready() is True
    client.close()
    driver.connection.close.assert_called_once()
    driver.connection.connection_pool.disconnect.assert_called_once()
    assert client.initialized is False


def test_missing_expected_interface_is_not_success(monkeypatch):
    driver = MagicMock(spec=['connection'])
    monkeypatch.setattr('app.core.falkordb.FalkorDB', lambda **_: driver)
    client = FalkorDBClient(config())
    assert client.initialize() is False
    assert client.is_ready() is False
    client.close()


def test_invalid_graph_result_is_not_ready(monkeypatch):
    driver = MagicMock()
    driver.select_graph.return_value.query.return_value.result_set = []
    monkeypatch.setattr('app.core.falkordb.FalkorDB', lambda **_: driver)
    client = FalkorDBClient(config())
    assert client.initialize() is False
    assert client.is_ready() is False
    client.close()


def test_missing_required_graph_package_fails_import():
    result = subprocess.run(
        [sys.executable, '-c', "import sys; sys.modules['falkordb'] = None; import app.main"],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
        timeout=5,
        check=False,
    )
    assert result.returncode != 0
    assert 'ModuleNotFoundError' in result.stderr
