from datetime import datetime, timezone
from typing import List

from sqlalchemy import text
from sqlalchemy.engine import Engine

from detect.models import Alert
from detect.rule_loader import RuleSpec


# Very naive: if same user changes country within 30 minutes -> alert
WINDOW_MINUTES = 30


def run(engine: Engine, rule: RuleSpec) -> List[Alert]:
    with engine.begin() as conn:
        rows = conn.execute(
            text(
                """
                with ordered as (
                  select
                    user_id,
                    country,
                    ts,
                    lag(country) over (partition by user_id order by ts) as prev_country,
                    lag(ts) over (partition by user_id order by ts) as prev_ts
                  from auth_logs
                )
                select user_id, country, ts, prev_country, prev_ts
                from ordered
                where prev_country is not null
                  and country <> prev_country
                  and ts - prev_ts <= (:window || ' minutes')::interval
                """
            ),
            {"window": WINDOW_MINUTES},
        ).mappings().all()

    alerts: List[Alert] = []
    now = datetime.now(timezone.utc)
    for idx, r in enumerate(rows):
        alerts.append(
            Alert(
                id=f"{rule.id}-{idx}",
                rule_id=rule.id,
                rule_name=rule.name,
                severity=rule.severity,
                risk_score=rule.risk_score,
                created_at=now,
                details={
                    "user_id": r["user_id"],
                    "from_country": r["prev_country"],
                    "to_country": r["country"],
                    "from_ts": str(r["prev_ts"]),
                    "to_ts": str(r["ts"]),
                },
            )
        )
    return alerts
