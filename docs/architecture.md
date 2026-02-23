# Architecture

## Goal
Provide a lightweight detection engineering platform that supports:
- detection-as-code (rules in version control)
- modular detection logic (Python)
- repeatable execution (CLI + containers)
- testable detections (fixtures + regression tests)
- portable storage backends (dev DB → scalable query engine)

## High-level flow
1. Ingest logs (JSON / JSONL) into a storage backend (dev: Postgres, scale: Trino/Iceberg).
2. Normalize into a consistent event schema where possible while preserving raw payloads.
3. Load detection rules from `rules/*.yml`.
4. Execute detection logic modules referenced by rules.
5. Emit alerts with consistent schema (id, rule_name, severity, risk_score, entities, evidence).
6. Persist alerts (DB table and/or JSONL) and export to downstream systems.

## Components
- `detect/cli.py`: entry point; runs detections and orchestrates I/O.
- `detect/rule_loader.py`: loads/validates YAML rule definitions into Python objects.
- `detect/runner.py`: executes detections, handles scheduling/time windows, collects results.
- `detect/db.py` / models: storage abstraction (SQLAlchemy) for events and alerts.
- `detect/alerts.py`: alert schema + serialization.
- `rules/*.yml`: detection-as-code definitions (metadata + logic mapping).
- `detections/*.py`: detection logic modules (SQL-based or event-stream based).

## Storage strategy
### Dev: Postgres
- Fast local iteration
- JSONB columns for semi-structured logs
- Easy unit tests + deterministic fixtures

### Scale: Trino + Iceberg on S3-compatible storage (MinIO)
- Partitioned log lake (e.g., by day/hour/account/region)
- SQL detections executed on distributed engine
- Mirrors Hive/Presto-style workloads used in large environments

## Testing strategy
- Each detection has test fixtures:
  - positive events -> must alert
  - negative events -> must not alert
  - expected output -> must match schema and key fields
- CI gates merges on:
  - lint/type checks
  - unit tests
  - detection regression tests
  - (optional) performance sanity checks

## Operational considerations
- Observability: structured logs + OpenTelemetry metrics
- Noise reduction: allowlists, suppression keys, threshold tuning
- Ownership: rule metadata includes owner/team and triage runbook links