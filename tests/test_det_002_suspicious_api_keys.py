from datetime import datetime, timezone

from detections.logic.det_002_suspicious_access_key import run
from detect.rule_loader import RuleSpec


class _FakeResult:
    def __init__(self, rows):
        self._rows = rows

    def mappings(self):
        return self

    def all(self):
        return self._rows


class _FakeConn:
    def __init__(self, rows):
        self._rows = rows

    def execute(self, *_args, **_kwargs):
        return _FakeResult(self._rows)


class _FakeBegin:
    def __init__(self, rows):
        self._rows = rows

    def __enter__(self):
        return _FakeConn(self._rows)

    def __exit__(self, *_args):
        pass


class _FakeEngine:
    def __init__(self, rows):
        self._rows = rows

    def begin(self):
        return _FakeBegin(self._rows)


def test_det_002_stub_returns_empty_alerts():
    rule = RuleSpec(
        id="DET-002",
        name="Suspicious Access Key Creation",
        description="Detect CreateAccessKey events for human users outside business hours.",
        enabled=True,
        severity="high",
        risk_score=85,
        type="python",
        datasource="cloudtrail_logs",
        logic_module="det_002_suspicious_api_keys",
        tags=["aws", "iam"],
    )

    fake_engine = _FakeEngine([])
    assert run(engine=fake_engine, rule=rule) == []
