from functools import lru_cache
from urllib.parse import quote_plus
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_host: str = ""
    database_port: int = 5432
    database_name: str = "leads"
    database_username: str = ""
    database_password: str = ""
    database_sslmode: str = "disable"
    oidc_issuer_url: str
    oidc_jwks_url: str
    s3_endpoint: str
    s3_region: str = "us-east-1"
    s3_bucket: str = "lead-resumes"
    s3_access_key: str
    s3_secret_key: str
    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{quote_plus(self.database_username)}:{quote_plus(self.database_password)}@{self.database_host}:{self.database_port}/{self.database_name}?ssl={self.database_sslmode}"

@lru_cache
def get_settings() -> Settings:
    return Settings()