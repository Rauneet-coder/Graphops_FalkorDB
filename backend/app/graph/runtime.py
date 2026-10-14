"""Infrastructure probes only. Domain schema/seed initialization belongs to Stage 2."""

from falkordb.graph import Graph

PROBE_QUERY = "RETURN 1 AS graphops_ready"


def probe_graph(graph: Graph, timeout_ms: int) -> None:
    result = graph.ro_query(PROBE_QUERY, timeout=timeout_ms)
    if result.result_set != [[1]]:
        raise RuntimeError("Unexpected graph probe result")


def initialize_graph(graph: Graph, timeout_ms: int) -> None:
    # RO_QUERY cannot initialize a nonexistent graph. This creates only an empty
    # graph key, without indexes, fixture nodes/edges, or deleting existing data.
    result = graph.query(PROBE_QUERY, timeout=timeout_ms)
    if result.result_set != [[1]]:
        raise RuntimeError("Unexpected graph initialization result")
    probe_graph(graph, timeout_ms)
