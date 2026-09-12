from functools import lru_cache
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=False)

    app_name: str = "lead-intake-api"
    environment: str = "local"
    max_resume_bytes: int = 10 * 1024 * 1024

    database_host: str = ""
    database_port: int = 5432
    database_name: str = "leads"
    database_username: str = ""
    database_password: str = ""
    database_sslmode: str = "disable"

    s3_endpoint: str = ""
    s3_region: str = "us-east-1"
    s3_bucket: str = "lead-resumes"
    s3_access_key: str = ""
    s3_secret_key: str = ""

    @property
    def database_url(self) -> str:
        if not self.database_host or not self.database_username or not self.database_password:
            raise RuntimeError("Database credentials are not configured")
        return (
            f"postgresql+asyncpg://{quote_plus(self.database_username)}:"
            f"{quote_plus(self.database_password)}@{self.database_host}:{self.database_port}/"
            f"{self.database_name}?ssl={self.database_sslmode}"
        )

    def validate_storage(self) -> None:
        if not all((self.s3_endpoint, self.s3_access_key, self.s3_secret_key, self.s3_bucket)):
            raise RuntimeError("S3 credentials are not configured")


@lru_cache
def get_settings() -> Settings:
    return Settings()