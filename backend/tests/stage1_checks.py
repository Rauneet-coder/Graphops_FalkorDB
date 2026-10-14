"""Live process/persistence checks driven by scripts/verify-stage1.sh."""

import json
import sys
import time
from uuid import uuid4
from pathlib import Path

import httpx
from app.core.config import Settings
from app.core.falkordb import FalkorDBClient

PROBE_GRAPH = 'graphops_test_persistence'


def health(expected: int, initialization: bool | None = None) -> None:
    deadline = time.monotonic() + 25
    with httpx.Client(timeout=3, trust_env=False) as http:
        while True:
            response = http.get('http://127.0.0.1:8000/health/ready')
            if response.status_code == expected:
                break
            if time.monotonic() >= deadline:
                raise AssertionError(f'Expected readiness {expected}, got {response.status_code}')
            time.sleep(0.2)
        data = response.json()
        if initialization is not None:
            assert data['initialization']['completed'] is initialization, data
        assert data['initialization']['demo_data_loaded'] is False
        assert http.get('http://127.0.0.1:8000/health').status_code == expected
        assert http.get('http://127.0.0.1:8000/health/live').status_code == 200
    print(json.dumps(data, sort_keys=True))


def persistence(action: str, token: str | None = None) -> None:
    # This test helper never selects the demo graph or deletes any graph/volume.
    assert PROBE_GRAPH.startswith('graphops_test_')
    client = FalkorDBClient(Settings(FALKORDB_GRAPH=PROBE_GRAPH))
    try:
        if action == 'write':
            assert client.initialize(), 'Cannot initialize test-only probe graph'
            token = uuid4().hex
            client.get_graph().query(
                'CREATE (:InfrastructureProbe {id: $token})',
                params={'token': token}, timeout=500,
            )
            print(token)
        else:
            # Read first, before any initialization could recreate the graph.
            assert token is not None
            result = client.get_graph().ro_query(
                'MATCH (n:InfrastructureProbe {id: $token}) RETURN n.id',
                params={'token': token}, timeout=500,
            )
            assert result.result_set == [[token]], 'Non-fixture persistence probe lost'
            values = client.get_client().connection.config_get('dir', 'appendonly', 'appendfsync')
            assert values == {
                'dir': '/var/lib/falkordb/data',
                'appendonly': 'yes', 'appendfsync': 'everysec',
            }, values
            print('Non-fixture probe survived; effective persistence configuration:', values)
    finally:
        client.close()


if __name__ == '__main__':
    phase = sys.argv[1]
    if phase == 'ready':
        health(200, True)
    elif phase == 'outage':
        health(503)
    elif phase == 'uninitialized':
        health(503, False)
    elif phase == 'write-probe':
        persistence('write')
    elif phase == 'read-probe':
        persistence('read', sys.argv[2])
    elif phase == 'frontend':
        assert Path('/app/graph/seeds/sample_graph.json').is_file(), 'Graph assets missing from image'
        with httpx.Client(timeout=3, trust_env=False) as http:
            assert http.get('http://frontend:3000/health').json() == {'status': 'alive'}
            page = http.get('http://frontend:3000/')
            assert page.status_code == 200 and 'GraphOps' in page.text
            assert 'FalkorDB Engine Ready' not in page.text
        print('Production frontend health/page: 200')
    else:
        raise ValueError('Unknown verification phase')
