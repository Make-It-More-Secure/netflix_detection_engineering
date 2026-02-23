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
        # Drop existing tables to ensure schema matches
        conn.execute(text("drop table if exists alerts;"))
        conn.execute(text("drop table if exists cloudtrail_logs;"))
        conn.execute(text("drop table if exists auth_logs;"))
        
        conn.execute(text("""
            create table auth_logs (
              id serial primary key,
              user_id text,
              ip text,
              country text,
              user_agent text,
              ts timestamptz,
              success boolean,
              failure_reason text,
              mfa_used boolean,
              device_id text,
              raw jsonb
            );
        """))
        conn.execute(text("""
            create table cloudtrail_logs (
              id serial primary key,
              event_name text,
              user_identity text,
              user_type text,
              role_arn text,
              source_ip text,
              aws_region text,
              user_agent text,
              ts timestamptz,
              request_parameters jsonb,
              raw jsonb
            );
        """))
        conn.execute(text("""
            create table alerts (
              id text primary key,
              rule_id text,
              rule_name text,
              severity text,
              risk_score int,
              created_at timestamptz,
              details jsonb
            );
        """))
