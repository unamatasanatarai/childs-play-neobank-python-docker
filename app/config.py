from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App Settings
    PROJECT_NAME: str = "Child'sPay Core"
    VERSION: str = "1.1.0"

    # Database Settings
    DATABASE_URL: str = (
        "postgresql+asyncpg://admin:development_password@db:5432/childspay_ledger"
    )

    # Security Settings
    JWT_SECRET: str = "super-secret-atomic-key-123"  # Change this in production!
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
