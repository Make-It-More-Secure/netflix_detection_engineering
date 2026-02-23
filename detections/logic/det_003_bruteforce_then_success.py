import logging
import hashlib
from datetime import datetime, timezone
from typing import List
from sqlalchemy import text
from sqlalchemy.engine import Engine
from detect.models import Alert
from detect.rule_loader import RuleSpec

logger = logging.getLogger(__name__)

WINDOW_MINUTES = 10
FAIL_THRESHOLD = 5


def run(engine: Engine, rule: RuleSpec) -> List[Alert]:
    """Detect brute force: multiple failed logins followed by successful login."""
    try:
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
                      where ts > now() - interval '1 day'  -- Performance: limit lookback window
                    )
                    select user_id, ip, ts, fail_count_window
                    from ordered
                    where success = true
                      and fail_count_window >= :fail_threshold
                      and ts > now() - (:window || ' minutes')::interval
                """),
                {"fail_threshold": FAIL_THRESHOLD, "window": WINDOW_MINUTES},
            ).mappings().all()
        
        logger.debug(f"Found {len(rows)} brute force candidates")
    except Exception as e:
        logger.error(f"Error querying brute force data: {e}")
        raise

    now = datetime.now(timezone.utc)
    alerts: List[Alert] = []
    for idx, r in enumerate(rows):
        try:
            # Create deterministic alert ID using hash to avoid duplicates
            alert_seed = f"{rule.id}-{r['user_id']}-{r['ip']}-{r['ts'].isoformat()}"
            alert_id = f"{rule.id}-{hashlib.sha256(alert_seed.encode()).hexdigest()[:16]}"
            
            alerts.append(
                Alert(
                    id=alert_id,
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
                        "threshold": FAIL_THRESHOLD,
                    },
                )
            )
        except Exception as e:
            logger.error(f"Error creating alert from row {r}: {e}")
            continue
    
    logger.info(f"Generated {len(alerts)} alerts")
    return alerts
