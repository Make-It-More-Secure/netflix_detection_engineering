import json
from pathlib import Path

import pytest

FIXTURES = Path("tests/detections")

def read_jsonl(p: Path):
    return [json.loads(line) for line in p.read_text().splitlines() if line.strip()]

@pytest.mark.parametrize("det_name", [p.name for p in FIXTURES.iterdir() if p.is_dir()])
def test_detection_regression(det_name):
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