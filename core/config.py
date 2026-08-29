from pydantic_settings import BaseSettings, SettingsConfigDict


class EnterpriseSettings(BaseSettings):
    # App Information
    APP_NAME: str = "TalabaEnterprise"
    ENVIRONMENT: str = "production"  # local, staging, production
    DEBUG: bool = False
    
    # Telegram Bot
    BOT_TOKEN: str
    WEBHOOK_HOST: str = "https://talaba.uz"
    WEBHOOK_PATH: str = "/webhook/bot"
    
    # AI Engine (Alibaba Qwen / Gemini)
    QWEN_API_KEY: str
    QWEN_BASE_URL: str = "https://ws-3so6n0l7etszzq37.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1"
    QWEN_MODEL: str = "qwen-turbo"
    
    # Database (PostgreSQL + PgBouncer)
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgrespassword@db:5432/talaba_db"
    DB_POOL_SIZE: int = 30
    DB_MAX_OVERFLOW: int = 15
    
    # Cache & Queue (Redis / RabbitMQ)
    REDIS_URL: str = "redis://redis:6379/0"
    RABBITMQ_URL: str = "amqp://guest:guest@rabbitmq:5672//"
    
    # Object Storage (MinIO / S3)
    S3_ENDPOINT: str = "http://minio:9000"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin"
    S3_BUCKET: str = "talaba-storage"
    
    # Observability & Metrics
    PROMETHEUS_METRICS_PORT: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = EnterpriseSettings()
