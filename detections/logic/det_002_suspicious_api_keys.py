from datetime import datetime
from typing import List
from sqlalchemy import text
from sqlalchemy.engine import Engine
from detect.models import Alert
from detect.rule_loader import RuleSpec

HUMAN_USERS = {"alice", "bob", "security.engineer"}  # could come from DB/config
BUSINESS_HOURS_START = 9
BUSINESS_HOURS_END = 17


def run(engine: Engine, rule: RuleSpec) -> List[Alert]:
    with engine.begin() as conn:
        rows = conn.execute(
            text("""
                select event_name, user_identity, user_type, source_ip, aws_region, ts
                from cloudtrail_logs
                where event_name = 'CreateAccessKey'
                  and ts > now() - interval '1 day'
            """)
        ).mappings().all()

    alerts: List[Alert] = []
    now = datetime.utcnow()
    for idx, r in enumerate(rows):
        user = r["user_identity"]
        ts: datetime = r["ts"]
        hour = ts.hour

        if user not in HUMAN_USERS:
            continue
        if BUSINESS_HOURS_START <= hour < BUSINESS_HOURS_END:
            # in business hours, lower risk – you could skip or downgrade
            continue

        alerts.append(
            Alert(
                id=f"{rule.id}-{user}-{idx}",
                rule_id=rule.id,
                rule_name=rule.name,
                severity=rule.severity,
                risk_score=rule.risk_score,
                created_at=now,
                details={
                    "user": user,
                    "user_type": r["user_type"],
                    "source_ip": r["source_ip"],
                    "region": r["aws_region"],
                    "event_ts": str(ts),
                },
            )
        )

    return alerts
