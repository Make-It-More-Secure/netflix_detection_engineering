import logging
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application configuration. Load from .env file or environment variables."""
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "detectlab"
    db_user: str = "detect"
    db_password: str = "detect"
    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_pool_timeout: int = 30
    db_pool_recycle: int = 3600  # Recycle connections every hour

    # MinIO (optional)
    minio_endpoint: str = "http://localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "raw-logs"

    # Logging
    log_level: str = "INFO"


try:
    settings = Settings()
    logger.info(f"Configuration loaded: db={settings.db_host}:{settings.db_port}/{settings.db_name}")
except Exception as e:
    logger.error(f"Failed to load configuration: {e}")
    raise