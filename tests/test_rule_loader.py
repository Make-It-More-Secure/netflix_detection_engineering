import tempfile
from pathlib import Path

import pytest

from detect.rule_loader import load_rules, RuleSpec


def test_load_rules_loads_valid_yml():
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "det_001.yml"
        path.write_text(
            """
id: DET-001
name: Test Rule
description: A test.
enabled: true
severity: HIGH
risk_score: 80
type: python
datasource: auth_logs
logic_module: det_001_test
tags: [auth]
"""
        )
        rules = load_rules(Path(d))
    assert len(rules) == 1
    assert rules[0].id == "DET-001"
    assert rules[0].name == "Test Rule"
    assert rules[0].enabled is True
    assert rules[0].tags == ["auth"]


def test_load_rules_skips_empty_yml():
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "empty.yml").write_text("")
        with pytest.raises(ValueError, match="YAML object"):
            load_rules(Path(d))
