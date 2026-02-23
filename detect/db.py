from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from .config import settings

def get_engine() -> Engine:
    url = (
        f"postgresql+psycopg://{settings.db_user}:{settings.db_password}"
        f"@{settings.db_host}:{settings.db_port}/{settings.db_name}"
    )
    return create_engine(url, future=True)

def init_schema(engine: Engine) -> None:
    with engine.begin() as conn:
        conn.execute(text("""
            create table if not exists auth_logs (
              id serial primary key,
              user_id text,
              ip text,
              country text,
              user_agent text,
              ts timestamptz,
              raw jsonb
            );
        """))
        conn.execute(text("""
            create table if not exists cloudtrail_logs (
              id serial primary key,
              event_name text,
              user_identity text,
              source_ip text,
              aws_region text,
              ts timestamptz,
              raw jsonb
            );
        """))
        conn.execute(text("""
            create table if not exists alerts (
              id text primary key,
              rule_id text,
              rule_name text,
              severity text,
              risk_score int,
              created_at timestamptz,
              details jsonb
            );
        """))
