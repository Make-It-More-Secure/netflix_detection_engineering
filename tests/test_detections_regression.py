import json
from pathlib import Path

import pytest

FIXTURES = Path("tests/detections")

def read_jsonl(p: Path):
    return [json.loads(line) for line in p.read_text().splitlines() if line.strip()]

@pytest.mark.skip(reason="Regression test fixtures incomplete - implement when full test data is available")
@pytest.mark.parametrize("det_name", [p.name for p in FIXTURES.iterdir() if p.is_dir()] if FIXTURES.exists() else [])
def test_detection_regression(det_name):
    """Regression test for detections using pre-defined fixtures.
    
    To fully implement:
    1. Create test fixtures in tests/detections/{det_name}/
    2. Add positive.jsonl, negative.jsonl, expected_alerts.json
    3. Implement detection logic to pass each fixture
    """
    d = FIXTURES / det_name
    positives = read_jsonl(d / "positive.jsonl")
    negatives = read_jsonl(d / "negative.jsonl")
    expected = json.loads((d / "expected_alerts.json").read_text())

    # TODO: replace with your platform calls:
    # - ingest(positives + negatives)
    # - run_detection(det_name or rule_id)
    # - get_alerts()

    alerts = []  # placeholder
    assert alerts == expected