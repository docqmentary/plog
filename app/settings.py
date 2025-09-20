from __future__ import annotations

from functools import lru_cache

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = Field(default="dev")
    database_url: str = Field(default="sqlite:///./plog.db")
    openai_api_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices("openai_api_key", "OPENAI_API_KEY"),
    )
    naver_search_client_id: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "naver_search_client_id",
            "NAVER_SEARCH_CLIENT_ID",
        ),
    )
    naver_search_client_secret: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "naver_search_client_secret",
            "NAVER_SEARCH_CLIENT_SECRET",
        ),
    )
    naver_searchad_access_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices("naver_searchad_access_key", "NAVER_SEARCHAD_ACCESS_KEY"),
    )
    naver_searchad_secret_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices("naver_searchad_secret_key", "NAVER_SEARCHAD_SECRET_KEY"),
    )
    dev_allow_http_fetch: bool = Field(
        default=False,
        validation_alias=AliasChoices("dev_allow_http_fetch", "DEV_ALLOW_HTTP_FETCH"),
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


__all__ = ["Settings", "get_settings"]
