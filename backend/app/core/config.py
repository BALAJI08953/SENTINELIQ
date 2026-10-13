from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SENTINELIQ_", env_file=".env", extra="ignore")
    database_url: str = "sqlite:///./sentineliq.db"
    env: str = "development"


settings = Settings()
