import logging
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.pool import QueuePool
from .config import settings

logger = logging.getLogger(__name__)

_engine: Engine = None

def get_engine() -> Engine:
    """Get or create a database engine with connection pooling."""
    global _engine
    if _engine is not None:
        return _engine
    
    try:
        url = (
            f"postgresql+psycopg://{settings.db_user}:{settings.db_password}"
            f"@{settings.db_host}:{settings.db_port}/{settings.db_name}"
        )
        
        _engine = create_engine(
            url,
            future=True,
            poolclass=QueuePool,
            pool_size=settings.db_pool_size,
            max_overflow=settings.db_max_overflow,
            pool_timeout=settings.db_pool_timeout,
            pool_recycle=settings.db_pool_recycle,
            echo=False,
        )
        
        # Test connection
        with _engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        logger.info("Database engine initialized successfully")
        return _engine
        
    except Exception as e:
        logger.error(f"Failed to initialize database engine: {e}")
        raise

def init_schema(engine: Engine) -> None:
    """Initialize database schema. Drops and recreates tables for clean state."""
    try:
        with engine.begin() as conn:
            # Drop existing tables
            logger.info("Dropping existing tables...")
            conn.execute(text("drop table if exists alerts cascade;"))
            conn.execute(text("drop table if exists cloudtrail_logs cascade;"))
            conn.execute(text("drop table if exists auth_logs cascade;"))
            
            # Create auth_logs with indices
            logger.info("Creating auth_logs table...")
            conn.execute(text("""
                create table auth_logs (
                  id serial primary key,
                  user_id text not null,
                  ip text not null,
                  country text,
                  user_agent text,
                  ts timestamptz not null,
                  success boolean,
                  failure_reason text,
                  mfa_used boolean,
                  device_id text,
                  raw jsonb,
                  created_at timestamptz default now()
                );
            """))
            conn.execute(text("create index idx_auth_logs_user_id_ts on auth_logs(user_id, ts);"))
            conn.execute(text("create index idx_auth_logs_ip_ts on auth_logs(ip, ts);"))
            conn.execute(text("create index idx_auth_logs_ts on auth_logs(ts);"))
            
            # Create cloudtrail_logs with indices
            logger.info("Creating cloudtrail_logs table...")
            conn.execute(text("""
                create table cloudtrail_logs (
                  id serial primary key,
                  event_name text not null,
                  user_identity text not null,
                  user_type text,
                  role_arn text,
                  source_ip text,
                  aws_region text,
                  user_agent text,
                  ts timestamptz not null,
                  request_parameters jsonb,
                  raw jsonb,
                  created_at timestamptz default now()
                );
            """))
            conn.execute(text("create index idx_cloudtrail_event_ts on cloudtrail_logs(event_name, ts);"))
            conn.execute(text("create index idx_cloudtrail_user_ts on cloudtrail_logs(user_identity, ts);"))
            conn.execute(text("create index idx_cloudtrail_ts on cloudtrail_logs(ts);"))
            
            # Create alerts table with indices
            logger.info("Creating alerts table...")
            conn.execute(text("""
                create table alerts (
                  id text primary key,
                  rule_id text not null,
                  rule_name text not null,
                  severity text not null,
                  risk_score int not null,
                  created_at timestamptz not null,
                  details jsonb,
                  updated_at timestamptz default now()
                );
            """))
            conn.execute(text("create index idx_alerts_rule_id on alerts(rule_id);"))
            conn.execute(text("create index idx_alerts_timestamp on alerts(created_at desc);"))
            conn.execute(text("create index idx_alerts_severity on alerts(severity);"))
            
            logger.info("Schema initialization completed successfully")
            
    except Exception as e:
        logger.error(f"Failed to initialize schema: {e}")
        raise
