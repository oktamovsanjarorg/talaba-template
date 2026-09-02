from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Talaba AI"
    ENVIRONMENT: str = "production"
    DEBUG: bool = False

    # Telegram Bot
    BOT_TOKEN: str

    # AI Engine (Alibaba Qwen)
    QWEN_API_KEY: str
    QWEN_BASE_URL: str = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
    QWEN_MODEL: str = "qwen-turbo"

    # Shifrlash (AES/Fernet)
    ENCRYPTION_KEY: str

    # Database (PostgreSQL)
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgrespassword@db:5432/talaba_db"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"
    REDIS_PASSWORD: str = ""

    # Observability
    PROMETHEUS_METRICS_PORT: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
