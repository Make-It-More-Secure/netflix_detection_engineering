import json
from datetime import datetime
from pathlib import Path
from sqlalchemy import text
from .db import get_engine


def load_auth_logs(path: Path) -> None:
    engine = get_engine()
    with engine.begin() as conn, path.open() as f:
        for line in f:
            rec = json.loads(line)
            conn.execute(
                text(
                    """
                    insert into auth_logs (user_id, ip, country, user_agent, ts, raw)
                    values (:user_id, :ip, :country, :user_agent, :ts, :raw)
                    """
                ),
                {
                    "user_id": rec["user_id"],
                    "ip": rec["ip"],
                    "country": rec["country"],
                    "user_agent": rec["user_agent"],
                    "ts": datetime.fromisoformat(rec["ts"].replace("Z", "+00:00")),
                    "raw": json.dumps(rec),
                },
            )


if __name__ == "__main__":
    load_auth_logs(Path("data/sample/auth_logs.jsonl"))
