import logging
import hashlib
from datetime import datetime, timezone
from typing import List
from sqlalchemy import text
from sqlalchemy.engine import Engine
from detect.models import Alert
from detect.rule_loader import RuleSpec

logger = logging.getLogger(__name__)

HUMAN_USERS = {"alice", "bob", "security.engineer"}  # could come from DB/config
BUSINESS_HOURS_START = 9
BUSINESS_HOURS_END = 17


def run(engine: Engine, rule: RuleSpec) -> List[Alert]:
    """Detect suspicious access key creation outside business hours."""
    try:
        with engine.begin() as conn:
            rows = conn.execute(
                text("""
                    select event_name, user_identity, user_type, source_ip, aws_region, ts
                    from cloudtrail_logs
                    where event_name = 'CreateAccessKey'
                      and ts > now() - interval '1 day'
                """)
            ).mappings().all()
        
        logger.debug(f"Found {len(rows)} CreateAccessKey events")
    except Exception as e:
        logger.error(f"Error querying suspicious access key data: {e}")
        raise

    alerts: List[Alert] = []
    now = datetime.now(timezone.utc)
    
    for idx, r in enumerate(rows):
        try:
            user = r["user_identity"]
            ts: datetime = r["ts"]
            hour = ts.hour

            if user not in HUMAN_USERS:
                logger.debug(f"Skipping non-human user: {user}")
                continue
            
            if BUSINESS_HOURS_START <= hour < BUSINESS_HOURS_END:
                # in business hours, lower risk – you could skip or downgrade
                logger.debug(f"Skipping {user} - event during business hours")
                continue

            # Create deterministic alert ID
            alert_seed = f"{rule.id}-{user}-{ts.isoformat()}"
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
                        "user": user,
                        "user_type": r["user_type"],
                        "source_ip": r["source_ip"],
                        "region": r["aws_region"],
                        "event_ts": str(ts),
                        "hour_of_day": hour,
                    },
                )
            )
        except Exception as e:
            logger.error(f"Error creating alert from row {r}: {e}")
            continue
    
    logger.info(f"Generated {len(alerts)} alerts")
    return alerts
