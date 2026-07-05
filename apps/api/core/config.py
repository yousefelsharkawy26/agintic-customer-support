from __future__ import annotations

from typing import Any

import structlog
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Customer Support API"
    debug: bool = False

    database_url: str = "postgresql+asyncpg://app_worker:CHANGE_ME@localhost:5432/customer_support"
    # Used by Alembic migrations only (neondb_owner / superuser).
    # NEVER read by the FastAPI application at runtime.
    alembic_database_url: str | None = None
    # Used by the out-of-band provisioning CLI only (app_provisioner role).
    # NEVER read by the FastAPI application at runtime.
    provisioner_database_url: str | None = None
    redis_url: str = "redis://localhost:6379/0"
    qdrant_url: str = "http://localhost:6333"

    jwt_secret: str = "dev-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440

    openai_api_key: str = ""
    anthropic_api_key: str = ""
    google_api_key: str = ""
    cohere_api_key: str = ""

    log_level: str = "INFO"
    log_format: str = "json"

    cors_origins: str = "*"
    worker_count: int = 4

    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_pool_timeout: int = 30
    db_pool_pre_ping: bool = True

    redis_pool_size: int = 20
    redis_socket_keepalive: bool = True
    redis_socket_connect_timeout: int = 5

    rate_limit_max: int = 60
    rate_limit_window: int = 60

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()


def configure_logging() -> None:
    processors: list[Any] = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.dev.set_exc_info,
    ]

    if settings.log_format == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
