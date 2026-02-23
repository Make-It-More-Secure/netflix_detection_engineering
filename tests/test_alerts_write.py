from datetime import datetime, timezone

from detect.alerts import write_alerts
from detect.models import Alert


class _FakeConn:
    def __init__(self):
        self.calls = []

    def execute(self, statement, params):
        self.calls.append((statement, params))


class _FakeBegin:
    def __init__(self, conn):
        self.conn = conn

    def __enter__(self):
        return self.conn

    def __exit__(self, _exc_type, _exc, _tb):
        return False


class _FakeEngine:
    def __init__(self, conn):
        self.conn = conn

    def begin(self):
        return _FakeBegin(self.conn)


def test_write_alerts_writes_jsonl_and_upserts(monkeypatch, tmp_path):
    conn = _FakeConn()
    monkeypatch.setattr("detect.alerts.get_engine", lambda: _FakeEngine(conn))

    alerts = [
        Alert(
            id="DET-001-a",
            rule_id="DET-001",
            rule_name="Impossible Travel Login",
            severity="HIGH",
            risk_score=90,
            created_at=datetime(2025, 2, 1, 10, 0, tzinfo=timezone.utc),
            details={"user_id": "alice"},
        ),
        Alert(
            id="DET-001-b",
            rule_id="DET-001",
            rule_name="Impossible Travel Login",
            severity="HIGH",
            risk_score=90,
            created_at=datetime(2025, 2, 1, 11, 0, tzinfo=timezone.utc),
            details={"user_id": "bob"},
        ),
    ]

    out = tmp_path / "alerts.jsonl"
    write_alerts(alerts, out)

    lines = out.read_text().splitlines()
    assert lines == [a.model_dump_json() for a in alerts]
    assert len(conn.calls) == 2
    assert conn.calls[0][1]["id"] == "DET-001-a"
    assert conn.calls[1][1]["id"] == "DET-001-b"
