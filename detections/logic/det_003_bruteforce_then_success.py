from datetime import datetime
from typing import List
from sqlalchemy import text
from sqlalchemy.engine import Engine
from detect.models import Alert
from detect.rule_loader import RuleSpec

WINDOW_MINUTES = 10
FAIL_THRESHOLD = 5


def run(engine: Engine, rule: RuleSpec) -> List[Alert]:
    # we assume auth_logs.success is boolean
    with engine.begin() as conn:
        rows = conn.execute(
            text("""
                with ordered as (
                  select
                    user_id,
                    ip,
                    ts,
                    success,
                    lag(success) over (partition by user_id, ip order by ts) as prev_success,
                    count(*) filter (where success = false)
                       over (partition by user_id, ip order by ts
                             rows between 10 preceding and current row) as fail_count_window
                  from auth_logs
                )
                select user_id, ip, ts, fail_count_window
                from ordered
                where success = true
                  and fail_count_window >= :fail_threshold
                  and ts > now() - (:window || ' minutes')::interval
            """),
            {"fail_threshold": FAIL_THRESHOLD, "window": WINDOW_MINUTES},
        ).mappings().all()

    now = datetime.utcnow()
    alerts: List[Alert] = []
    for idx, r in enumerate(rows):
        alerts.append(
            Alert(
                id=f"{rule.id}-{r['user_id']}-{idx}",
                rule_id=rule.id,
                rule_name=rule.name,
                severity=rule.severity,
                risk_score=rule.risk_score,
                created_at=now,
                details={
                    "user_id": r["user_id"],
                    "ip": r["ip"],
                    "login_ts": str(r["ts"]),
                    "failed_attempts_prior": r["fail_count_window"],
                },
            )
        )
    return alerts
