from pathlib import Path
from typing import List

from sqlalchemy import text
from psycopg.types.json import Json

from .models import Alert
from .db import get_engine


def write_alerts(alerts: List[Alert], path: Path) -> None:
    # write jsonl (optional but nice)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        for alert in alerts:
            f.write(alert.model_dump_json())
            f.write("\n")

    # persist to DB
    engine = get_engine()
    with engine.begin() as conn:
        for a in alerts:
            conn.execute(
                text("""
                    insert into alerts (id, rule_id, rule_name, severity, risk_score, created_at, details)
                    values (:id, :rule_id, :rule_name, :severity, :risk_score, :created_at, :details)
                    on conflict (id) do update set
                      rule_name = excluded.rule_name,
                      severity = excluded.severity,
                      risk_score = excluded.risk_score,
                      created_at = excluded.created_at,
                      details = excluded.details
                """),
                {
                    "id": a.id,
                    "rule_id": a.rule_id,
                    "rule_name": a.rule_name,
                    "severity": a.severity,
                    "risk_score": a.risk_score,
                    "created_at": a.created_at,
                    "details": Json(a.details),
                },
            )
