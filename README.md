# Netflix Detection Engineering - Quick Start

A **security detection engine** that runs rules over logs and generates alerts. Define rules in YAML, implement detection logic in Python, get alerts in JSON.

**Tech Stack:** Python 3.11 • PostgreSQL • SQLAlchemy • FastAPI (UI) • pytest

---

## 🚀 Quick Start (2 min)

```bash
# 1. Start infrastructure
make up

# 2. Initialize database
make initdb

# 3. Load sample data
make seed

# 4. Run detections
make run

# 5. View results
cat alerts/alerts.jsonl  # Detection alerts (JSONL format)
make ui                  # Optional: Web interface at localhost:8000
```

---

## 📋 How It Works

```
YAML Rules → Python Logic → SQL Queries → PostgreSQL → JSON Alerts
```

1. **Rules** (`detections/rules/*.yml`) - Define what to detect
2. **Logic** (`detections/logic/*.py`) - Implement detection queries
3. **Database** - Auth logs + CloudTrail logs in PostgreSQL
4. **Alerts** - Generated as JSONL file + stored in DB

### Example Rule Flow

```yaml
# Rule: DET-001 Impossible Travel
datasource: auth_logs
logic_module: det_001_impossible_travel
```

```python
# Logic: Run SQL, return alerts
def run(engine, rule):
    rows = conn.execute("SELECT user_id, country, ts FROM auth_logs")
    # Detect: Same user in different countries within 30 minutes
    return [Alert(...), ...]
```

---

## 📁 Project Structure

```
detect/              # Core engine
  ├── cli.py         # Commands: initdb, run
  ├── db.py          # Database + schema
  ├── runner.py      # Execute rules
  └── config.py      # Environment settings

detections/
  ├── rules/         # Rule definitions (YAML)
  └── logic/         # Detection implementations (Python)

ui/                  # Web interface
tests/               # Unit tests
```

---

## 🛠️ Common Tasks

| Task | Command |
|------|---------|
| Run tests | `make test` |
| Run detections | `make run` |
| Watch logs | `make run 2>&1 \| grep -i alert` |
| Reset DB | `make initdb` |
| Start UI | `make ui` |

---

## ✅ Built-In Detections

| ID | Name | Detects |
|----|------|---------|
| DET-001 | Impossible Travel | Same user in different countries within 30 min |
| DET-002 | Suspicious Access Key | CreateAccessKey events outside business hours |
| DET-003 | Brute Force + Success | 5+ failed logins followed by success |

---

## 🔧 Add a New Detection (5 min)

### 1. Create rule (`detections/rules/det_004_example.yml`)
```yaml
id: DET-004
name: My Detection
datasource: auth_logs
logic_module: det_004_example
severity: MEDIUM
risk_score: 60
```

### 2. Implement logic (`detections/logic/det_004_example.py`)
```python
from detect.models import Alert

def run(engine, rule):
    with engine.begin() as conn:
        rows = conn.execute(text("""
            SELECT * FROM auth_logs WHERE ts > now() - '1 day'::interval
        """)).mappings().all()
    
    alerts = []
    for row in rows:
        if some_condition(row):
            alerts.append(Alert(
                id=f"{rule.id}-{row['user_id']}",
                rule_id=rule.id,
                # ... other fields
            ))
    return alerts
```

### 3. Run
```bash
make run  # Your detection runs automatically!
```

---

## 📊 Configuration

Edit `.env` for environment-specific settings:
```
DB_HOST=localhost
DB_PORT=5432
DB_USER=detect
LOG_LEVEL=INFO
```

---

## 🐛 Debugging

```bash
# View logs with timestamps
make run 2>&1

# Test single rule
python -c "from detections.logic.det_001_impossible_travel import run; ..."

# Check database
psql -U detect -h localhost -d detectlab
```

---

## 📈 Production Notes

- ✅ Logging enabled for all operations
- ✅ Error handling prevents cascading failures
- ✅ Database connection pooling configured
- ✅ Query indices optimized
- 📖 See [AUDIT_REPORT.md](AUDIT_REPORT.md) for production checklist

---

## 🧪 Testing

```bash
make test      # Run all tests
pytest tests/test_det_001_impossible_travel.py -v  # Single test
```

---

## 📚 Learn More

- [FIXES_SUMMARY.md](FIXES_SUMMARY.md) - Recent improvements
- [CONTRIBUTING.md](CONTRIBUTING.md) - Development guidelines
