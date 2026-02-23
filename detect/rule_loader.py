from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any
import yaml

@dataclass
class RuleSpec:
    id: str
    name: str
    description: str
    enabled: bool
    severity: str
    risk_score: int
    type: str
    datasource: str
    logic_module: str
    tags: List[str]


def load_rules(rule_dir: Path) -> List[RuleSpec]:
    rules: List[RuleSpec] = []
    for path in sorted(rule_dir.glob("*.yml")):
        with path.open() as f:
            data = yaml.safe_load(f)
        if not isinstance(data, dict):
            raise ValueError(
                f"Rule file must be a YAML object (got {type(data).__name__}): {path}"
            )
        rules.append(
            RuleSpec(
                id=data["id"],
                name=data["name"],
                description=data["description"],
                enabled=data.get("enabled", True),
                severity=data["severity"],
                risk_score=data["risk_score"],
                type=data["type"],
                datasource=data["datasource"],
                logic_module=data["logic_module"],
                tags=data.get("tags", []),
            )
        )
    return rules