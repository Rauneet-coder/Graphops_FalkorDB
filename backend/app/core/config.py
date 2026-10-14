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
