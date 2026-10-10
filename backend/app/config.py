"""Application settings, read from environment variables (prefix ``YUI_``) or a ``.env`` file."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="YUI_", env_file=".env", extra="ignore")

    # --- Storage -------------------------------------------------------------
    data_dir: Path = Path("./data")

    # --- Auth ----------------------------------------------------------------
    session_ttl_hours: int = 24 * 14
    allow_registration: bool = True
    # Set to true when served over HTTPS (e.g. exposed to the internet behind a TLS proxy).
    cookie_secure: bool = False
    cors_origins: list[str] = []

    # --- Generation engine ---------------------------------------------------
    # "mock" produces a short synthetic tone: useful for UI work on machines without a GPU.
    engine: Literal["yue2", "mock"] = "yue2"
    model_id: str = "m-a-p/YuE2-3B"
    device: str = "cuda"
    max_variants: int = 2

    # --- Auto update ---------------------------------------------------------
    auto_update: bool = True
    yue_repo: str = "multimodal-art-projection/YuE"
    yue_package: str = "yue2-infer"
    # Pin a release tag (e.g. "yue2-v0.1.6") to disable "latest" tracking.
    yue_pinned_tag: str | None = None

    @property
    def db_url(self) -> str:
        return f"sqlite:///{self.data_dir / 'yui.sqlite3'}"

    @property
    def songs_dir(self) -> Path:
        return self.data_dir / "songs"


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.songs_dir.mkdir(parents=True, exist_ok=True)
    return settings
