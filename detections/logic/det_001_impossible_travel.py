import logging
from datetime import datetime, timezone
import hashlib
import json
from typing import List

from sqlalchemy import text
from sqlalchemy.engine import Engine

from detect.models import Alert
from detect.rule_loader import RuleSpec

logger = logging.getLogger(__name__)

# Very naive: if same user changes country within 30 minutes -> alert
WINDOW_MINUTES = 30


def _stable_alert_id(rule_id: str, row: dict) -> str:
    payload = {
        "user_id": row["user_id"],
        "from_country": row["prev_country"],
        "to_country": row["country"],
        "from_ts": row["prev_ts"].isoformat(),
        "to_ts": row["ts"].isoformat(),
    }
    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()[:16]
    return f"{rule_id}-{digest}"


def run(engine: Engine, rule: RuleSpec) -> List[Alert]:
    """Detect impossible travel: same user in different countries within time window."""
    try:
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
                      where ts > now() - interval '7 days'  -- Performance: limit lookback window
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
        
        logger.debug(f"Found {len(rows)} impossible travel candidates")
    except Exception as e:
        logger.error(f"Error querying impossible travel data: {e}")
        raise

    alerts: List[Alert] = []
    now = datetime.now(timezone.utc)
    for r in rows:
        try:
            alert_id = _stable_alert_id(rule.id, r)
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
                        "from_country": r["prev_country"],
                        "to_country": r["country"],
                        "from_ts": str(r["prev_ts"]),
                        "to_ts": str(r["ts"]),
                        "time_delta_minutes": round((r["ts"] - r["prev_ts"]).total_seconds() / 60),
                    },
                )
            )
        except Exception as e:
            logger.error(f"Error creating alert from row {r}: {e}")
            continue
    
    logger.info(f"Generated {len(alerts)} alerts")
    return alerts
