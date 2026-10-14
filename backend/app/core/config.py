import json
from typing import Annotated, Literal
from urllib.parse import urlsplit

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "GraphOps API"
    VERSION: str = "0.1.0"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: Literal["development", "test", "production"] = "development"

    FALKORDB_HOST: str = Field(default="localhost", min_length=1)
    FALKORDB_PORT: int = Field(default=6379, ge=1, le=65535)
    FALKORDB_GRAPH: str = Field(default="graphops", pattern=r"^[A-Za-z][A-Za-z0-9_-]{0,63}$")
    FALKORDB_CONNECT_TIMEOUT_SECONDS: float = Field(default=1, gt=0, le=10)
    FALKORDB_SOCKET_TIMEOUT_SECONDS: float = Field(default=2, gt=0, le=30)
    FALKORDB_QUERY_TIMEOUT_MS: int = Field(default=500, ge=50, le=10000)
    GRAPH_WORKERS: int = Field(default=4, ge=1, le=16)
    GRAPH_INIT_RETRY_SECONDS: float = Field(default=1, ge=0.05, le=30)

    CORS_ORIGINS: Annotated[list[str], NoDecode] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: object) -> list[str]:
        if isinstance(value, str):
            value = value.strip()
            if value.startswith("["):
                value = json.loads(value)
            else:
                value = [origin.strip() for origin in value.split(",")]
        if not isinstance(value, list) or not value:
            raise ValueError("CORS_ORIGINS must be a nonempty list of HTTP(S) origins")
        for origin in value:
            if not isinstance(origin, str):
                raise ValueError("CORS origins must be strings")  # noqa: TRY004
            parsed = urlsplit(origin)
            if (
                parsed.scheme not in {"http", "https"}
                or not parsed.hostname
                or parsed.username is not None
                or parsed.password is not None
                or parsed.path
                or parsed.query
                or parsed.fragment
                or any(character.isspace() for character in origin)
            ):
                raise ValueError("Each CORS origin must contain only scheme, host, and optional port")
            _ = parsed.port  # Reject malformed/out-of-range ports.
        return value

    @model_validator(mode="after")
    def check_timeout_order(self) -> "Settings":
        if self.FALKORDB_QUERY_TIMEOUT_MS >= self.FALKORDB_SOCKET_TIMEOUT_SECONDS * 1000:
            raise ValueError("Graph query timeout must be shorter than socket timeout")
        return self

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
