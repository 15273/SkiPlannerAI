from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


def _default_repo_root() -> Path:
    # services/api/skiplanner_api/config.py -> repo root is parents[3]
    return Path(__file__).resolve().parent.parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(str(_default_repo_root() / ".env"),),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    api_env: str = "development"
    cors_origins: str = "http://localhost:8081,http://localhost:19006"
    repo_root: Path = _default_repo_root()
    amadeus_client_id: str = ""
    amadeus_client_secret: str = ""
    amadeus_hostname: str = "test.api.amadeus.com"
    database_url: str = "postgresql+asyncpg://mendikalish@localhost:5433/skiplanner"

    @property
    def seed_dir(self) -> Path:
        return self.repo_root / "data" / "seed"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
