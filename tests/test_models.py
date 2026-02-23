from datetime import datetime, timezone

from detect.models import Alert


def test_alert_serialization():
    alert = Alert(
        id="DET-001-1",
        rule_id="DET-001",
        rule_name="Impossible Travel",
        severity="HIGH",
        risk_score=90,
        created_at=datetime.now(timezone.utc),
        details={"user_id": "alice", "from_country": "US", "to_country": "GB"},
    )
    assert alert.rule_id == "DET-001"
    data = alert.model_dump()
    assert data["details"]["user_id"] == "alice"
