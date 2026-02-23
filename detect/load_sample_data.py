import json
from datetime import datetime
from pathlib import Path

from sqlalchemy import text
from psycopg.types.json import Json

from .db import get_engine


def load_auth_logs(path: Path) -> None:
    engine = get_engine()
    with engine.begin() as conn, path.open() as f:
        for line in f:
            rec = json.loads(line)
            conn.execute(
                text(
                    """
                    insert into auth_logs (user_id, ip, country, user_agent, ts, success, raw)
                    values (:user_id, :ip, :country, :user_agent, :ts, :success, :raw)
                    """
                ),
                {
                    "user_id": rec["user_id"],
                    "ip": rec["ip"],
                    "country": rec["country"],
                    "user_agent": rec["user_agent"],
                    "ts": datetime.fromisoformat(rec["ts"].replace("Z", "+00:00")),
                    "success": rec.get("success"),
                    "raw": Json(rec),
                },
            )


def load_cloudtrail_logs(path: Path) -> None:
    engine = get_engine()
    with engine.begin() as conn, path.open() as f:
        for line in f:
            rec = json.loads(line)
            conn.execute(
                text(
                    """
                    insert into cloudtrail_logs (event_name, user_identity, user_type, role_arn, source_ip, aws_region, user_agent, ts, request_parameters, raw)
                    values (:event_name, :user_identity, :user_type, :role_arn, :source_ip, :aws_region, :user_agent, :ts, :request_parameters, :raw)
                    """
                ),
                {
                    "event_name": rec["event_name"],
                    "user_identity": rec["user_identity"],
                    "user_type": rec["user_type"],
                    "role_arn": rec["role_arn"],
                    "source_ip": rec["source_ip"],
                    "aws_region": rec["aws_region"],
                    "user_agent": rec["user_agent"],
                    "ts": datetime.fromisoformat(rec["ts"].replace("Z", "+00:00")),
                    "request_parameters": Json(rec.get("request_parameters", {})),
                    "raw": Json(rec),
                },
            )


if __name__ == "__main__":
    load_auth_logs(Path("data/sample/auth_logs.jsonl"))
    load_cloudtrail_logs(Path("data/sample/cloudtrail_logs.jsonl"))
