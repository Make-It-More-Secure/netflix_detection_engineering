from importlib import import_module
from pathlib import Path
from typing import List
from datetime import datetime
from sqlalchemy.engine import Engine
from .rule_loader import RuleSpec, load_rules
from .alerts import write_alerts
from .db import get_engine

def run_all(rule_dir: Path, alerts_out: Path) -> None:
    engine = get_engine()
    rules = load_rules(rule_dir)
    all_alerts = []
    for rule in rules:
        if not rule.enabled:
            continue
        alerts = run_rule(rule, engine)
        all_alerts.extend(alerts)
    write_alerts(all_alerts, alerts_out)


def run_rule(rule: RuleSpec, engine: Engine):
    module = import_module(f"detections.logic.{rule.logic_module}")
    # convention: each logic module exposes `run(engine, rule: RuleSpec) -> List[Alert]`
    return module.run(engine, rule)