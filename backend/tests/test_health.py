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
