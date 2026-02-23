from datetime import datetime, timezone

from detections.logic.det_001_impossible_travel import run
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

    def __exit__(self, _exc_type, _exc, _tb):
        return False


class _FakeEngine:
    def __init__(self, rows):
        self._rows = rows

    def begin(self):
        return _FakeBegin(self._rows)


def _rule() -> RuleSpec:
    return RuleSpec(
        id="DET-001",
        name="Impossible Travel Login",
        description="Detect logins from distant countries in a short time window.",
        enabled=True,
        severity="HIGH",
        risk_score=90,
        type="python",
        datasource="auth_logs",
        logic_module="det_001_impossible_travel",
        tags=["auth", "anomaly"],
    )


def _alert_map(alerts):
    mapped = {}
    for alert in alerts:
        key = (
            alert.details["user_id"],
            alert.details["from_country"],
            alert.details["to_country"],
            alert.details["from_ts"],
            alert.details["to_ts"],
        )
        mapped[key] = alert.id
    return mapped


def test_det_001_generates_stable_ids_independent_of_result_order():
    row_a = {
        "user_id": "alice",
        "country": "GB",
        "ts": datetime(2025, 2, 1, 10, 20, tzinfo=timezone.utc),
        "prev_country": "US",
        "prev_ts": datetime(2025, 2, 1, 10, 0, tzinfo=timezone.utc),
    }
    row_b = {
        "user_id": "bob",
        "country": "JP",
        "ts": datetime(2025, 2, 1, 11, 10, tzinfo=timezone.utc),
        "prev_country": "CA",
        "prev_ts": datetime(2025, 2, 1, 10, 50, tzinfo=timezone.utc),
    }

    first = run(_FakeEngine([row_a, row_b]), _rule())
    second = run(_FakeEngine([row_b, row_a]), _rule())

    assert _alert_map(first) == _alert_map(second)
