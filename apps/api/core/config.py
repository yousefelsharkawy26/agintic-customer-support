from __future__ import annotations

from typing import Any

import structlog
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Customer Support API"
    debug: bool = False

    database_url: str = (
        "postgresql+asyncpg://cs_user:cs_dev_password@localhost:5432/customer_support"
    )
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
