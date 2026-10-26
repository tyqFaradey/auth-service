from pydantic import BaseModel, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class RunConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000


class SecurityConfig(BaseModel):
    access_secret: str
    refresh_secret: str
    algorithm: str = "HS256"
    access_token_expire: int = 10
    refresh_token_expire: int = 14


class RedisConfig(BaseModel):
    user: str
    password: str
    host: str
    port: str
    database: str

    @computed_field
    @property
    def url(self) -> str:
        return f"redis://:{self.password}@{self.host}:{self.port}/{self.database}"


class DatabaseConfig(BaseModel):
    user: str
    password: str
    host: str
    port: str
    database: str

    @computed_field
    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


class Settings(BaseSettings):
    run: RunConfig
    security: SecurityConfig
    database: DatabaseConfig
    redis: RedisConfig

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
