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

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
