import pytest


def pytest_addoption(parser):
    parser.addoption('--live-graph', action='store_true', help='Require live FalkorDB tests; fail on outage')


@pytest.fixture
def require_live_graph(request):
    if not request.config.getoption('--live-graph'):
        pytest.skip('Use --live-graph to require a live FalkorDB dependency')
