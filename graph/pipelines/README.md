# Graph Ingestion & Transformation Pipelines

This directory contains pipeline definitions for extracting, transforming, and ingesting graph data into FalkorDB.

## Pipeline Structure
- `extractors/`: Ingest raw data from CSV, JSON, telemetry, or external APIs.
- `transformers/`: Map source schemas into the target SRE ontology defined in `../schema/ontology.json`.
- `loaders/`: Batch write operations into FalkorDB using Cypher transactions and unwound parameters.
- `embedders/`: Vector embedding generation for hybrid vector + graph search in FalkorDB.
