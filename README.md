# Netflix Detection Engineering

A small detection-engine framework that runs security rules over log data (auth and CloudTrail), evaluates them with Python logic modules, and writes alerts to a JSONL file. Built for lab or pipeline use with PostgreSQL and optional MinIO.

## Features

- **Rule-driven detections**: Define rules in YAML; each rule points to a Python logic module that runs over a datasource.
- **PostgreSQL-backed**: Auth and CloudTrail logs live in Postgres; rules query via SQLAlchemy.
- **Pluggable logic**: Each detection is a module that implements `run(engine, rule) -> List[Alert]`.
- **CLI + Makefile**: Initialize DB, load sample data, run all enabled rules, and run tests via `make` or the `detect.cli` module.

## Architecture

```
detections/rules/*.yml     →  rule_loader  →  RuleSpec
                                                    ↓
PostgreSQL (auth_logs,      ←  runner  ←  detections/logic/<logic_module>.run(engine, rule)
cloudtrail_logs)                                              ↓
                                                    Alert (rule_id, severity, details)
                                                    ↓
                                            alerts/alerts.jsonl
```

1. **Rules** are YAML files in `detections/rules/`. Each has an `id`, `name`, `datasource`, and `logic_module`.
2. **Runner** loads rules, skips disabled ones, and for each enabled rule imports `detections.logic.<logic_module>` and calls `run(engine, rule)`.
3. **Logic modules** run SQL (or other logic) against the engine and return a list of `Alert` objects.
4. **Alerts** are written as one JSON object per line to the path you pass (default `alerts/alerts.jsonl`).

## Project structure

```
.
├── detect/                 # Core app
│   ├── cli.py              # Click CLI: initdb, run
│   ├── config.py           # Pydantic settings from .env
│   ├── db.py               # Postgres engine + schema (auth_logs, cloudtrail_logs)
│   ├── models.py           # Alert model
│   ├── rule_loader.py      # Load RuleSpec from YAML
│   ├── runner.py           # Run all enabled rules, write alerts
│   ├── alerts.py           # Write alerts to JSONL
│   └── load_sample_data.py # Load data/sample/auth_logs.jsonl into auth_logs
├── detections/
│   ├── rules/              # Rule definitions (*.yml)
│   │   ├── det_001_impossible_travel.yml
│   │   ├── det_002_suspicious_api_keys.yml
│   │   └── det_003_bruteforce_login.yml
│   └── logic/              # Detection logic (one module per rule)
│       ├── det_001_impossible_travel.py
│       ├── det_002_suspicious_api_keys.py
│       └── det_003_bruteforce_login.py
├── data/sample/            # Sample JSONL for seeding
├── alerts/                  # Output directory for alerts.jsonl
├── tests/
├── docker-compose.yml      # Postgres + MinIO
├── Makefile
└── .env                    # DB and MinIO config (not in git)
```

## Prerequisites

- Python 3.11+
- Docker and Docker Compose (for Postgres and MinIO)
- Git

## Setup

### 1. Clone and virtual environment

```bash
git clone git@github.com:Make-It-More-Secure/netflix_detection_engineering.git
cd netflix_detection_engineering
python3 -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
```

### 2. Install dependencies

```bash
pip install "psycopg[binary]" sqlalchemy pydantic pydantic-settings click pyyaml pytest
```

### 3. Environment

Create a `.env` in the project root (see **Configuration** below). Minimum for running detections:

```env
# Postgres (must match docker-compose)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=detectlab
DB_USER=detect
DB_PASSWORD=detect
```

### 4. Start Postgres and initialize schema

```bash
make up      # start Postgres (and MinIO) in the background
make initdb  # create auth_logs and cloudtrail_logs tables
```

### 5. (Optional) Load sample auth data

```bash
make seed    # loads data/sample/auth_logs.jsonl into auth_logs
```

Sample file format (one JSON object per line):

```json
{"user_id": "alice", "ip": "1.1.1.1", "country": "US", "user_agent": "Chrome", "ts": "2025-02-01T10:00:00Z"}
```

## Usage

### Make targets

| Command     | Description |
|------------|-------------|
| `make up`  | Start Docker services (Postgres on 5432, MinIO on 9000/9001). |
| `make initdb` | Create database tables. |
| `make seed` | Load sample auth logs from `data/sample/auth_logs.jsonl`. |
| `make run` | Run all enabled rules; write alerts to `alerts/alerts.jsonl`. |
| `make test` | Run pytest. |

The Makefile uses `.venv/bin/python`, so you don’t need to activate the venv for `make`.

### CLI

You can also call the CLI directly (with venv active or using `.venv/bin/python`):

```bash
python -m detect.cli initdb
python -m detect.cli run [--rule-dir detections/rules] [--out alerts/alerts.jsonl]
```

## Data model

### Database tables

- **auth_logs**: `id`, `user_id`, `ip`, `country`, `user_agent`, `ts` (timestamptz), `raw` (jsonb).
- **cloudtrail_logs**: `id`, `event_name`, `user_identity`, `source_ip`, `aws_region`, `ts`, `raw` (jsonb).

### Alert model

Each alert has: `id`, `rule_id`, `rule_name`, `severity`, `risk_score`, `created_at`, `details` (dict). Written as one JSON line per alert.

## Rules

Rules live in `detections/rules/*.yml`. Each file must be a single YAML object with:

| Field          | Required | Description |
|----------------|----------|-------------|
| `id`           | Yes      | Unique rule ID (e.g. `DET-001`). |
| `name`         | Yes      | Short name. |
| `description`  | Yes      | What the rule detects. |
| `enabled`      | No       | Default `true`. Set to `false` to skip. |
| `severity`     | Yes      | e.g. `HIGH`, `MEDIUM`. |
| `risk_score`   | Yes      | Numeric score. |
| `type`         | Yes      | e.g. `python`. |
| `datasource`   | Yes      | `auth_logs` or `cloudtrail_logs`. |
| `logic_module` | Yes      | Python module name under `detections.logic` (e.g. `det_001_impossible_travel`). |
| `tags`         | No       | List of tags. |

Example:

```yaml
id: DET-001
name: Impossible Travel Login
description: Detect logins from distant countries in a short time window.
enabled: true
severity: HIGH
risk_score: 90
type: python
datasource: auth_logs
logic_module: det_001_impossible_travel
tags:
  - auth
  - anomaly
```

Empty or invalid YAML rule files will cause a clear error when loading rules.

## Logic modules

Each rule’s `logic_module` must be a Python module under `detections/logic/` that defines:

```python
def run(engine: Engine, rule: RuleSpec) -> List[Alert]:
    ...
    return alerts
```

- **engine**: SQLAlchemy engine (Postgres).
- **rule**: The rule’s `RuleSpec` (id, name, severity, etc.).
- **return**: List of `Alert` instances from `detect.models`.

Example (conceptually): **DET-001 Impossible Travel** uses a 30-minute window: same user, two logins from different countries within 30 minutes → one alert per user. The implementation uses a SQL window to get previous country/ts and filters by `country <> prev_country` and `ts - prev_ts <= 30 minutes`.

DET-002 and DET-003 are stubs (they return `[]`) until you implement them.

## Configuration

`detect/config.py` loads from `.env` via Pydantic. Defaults:

| Variable           | Default       | Description |
|--------------------|---------------|-------------|
| `DB_HOST`          | `localhost`   | Postgres host. |
| `DB_PORT`          | `5432`        | Postgres port. |
| `DB_NAME`          | `detectlab`   | Database name. |
| `DB_USER`          | `detect`      | Database user. |
| `DB_PASSWORD`      | `detect`      | Database password. |
| `MINIO_*`          | (see config)  | MinIO endpoint and credentials (for future use). |

Do not commit `.env`; it is listed in `.gitignore`.

## Tests

```bash
make test
# or
.venv/bin/python -m pytest tests/ -q
```

Tests cover rule loading (valid YAML and empty-file error) and the Alert model. Add more under `tests/` as you extend the project.

## License

Use and modify as needed for your environment.
