from detections.logic.det_002_suspicious_api_keys import run
from detect.rule_loader import RuleSpec


def test_det_002_stub_returns_empty_alerts():
    rule = RuleSpec(
        id="DET-002",
        name="Suspicious API Keys",
        description="Detect anomalous or high-risk API key usage.",
        enabled=True,
        severity="MEDIUM",
        risk_score=50,
        type="python",
        datasource="cloudtrail_logs",
        logic_module="det_002_suspicious_api_keys",
        tags=["api", "cloudtrail"],
    )

    assert run(engine=None, rule=rule) == []
