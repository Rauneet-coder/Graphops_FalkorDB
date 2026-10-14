# Ingestion scope

This directory is reserved documentation, not an implemented ingestion framework.
The MVP has one planned validated idempotent fixture loader in
`backend/app/graph/loader.py`, with one CLI entry point at `graph/seed.py`.

A `Pipeline` graph node represents a concrete build/deployment run and is distinct
from this directory. See [the target relationship contract](../../docs/GRAPH_SCHEMA.md).
External extractors, telemetry ingestion, streaming, and vector embeddings are
deferred until the primary graph-backed investigation works.
