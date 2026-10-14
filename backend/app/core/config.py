from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SENTINELIQ_", env_file=".env", extra="ignore")
    database_url: str = "sqlite:///./sentineliq.db"
    env: str = "development"
    backend_host: str = "127.0.0.1"
    backend_port: int = 8000
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174"
    llm_provider: str = "deterministic"
    llm_base_url: str | None = None
    llm_api_key: str | None = None
    llm_model: str | None = None

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]


settings = Settings()
