from functools import lru_cache
from urllib.parse import urlsplit, urlunsplit

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str = "postgresql+psycopg://kenyaads:kenyaads@localhost:5432/kenyaads"
    migration_database_url: str | None = None
    redis_url: str = "redis://localhost:6379/0"
    cors_origins: str = "http://localhost:3000"
    jwt_secret: str = "development-only-secret-change-before-deploy"
    jwt_expire_minutes: int = 60

    # Optional OpenAI-compatible endpoint for a self-hosted model (e.g. vLLM).
    # Leave blank to use the transparent, deterministic starter-script provider.
    script_llm_base_url: str | None = None
    script_llm_model: str = "Qwen/Qwen2.5-3B-Instruct"
    script_llm_api_key: str | None = None
    script_llm_timeout_seconds: int = 55

    # Hosted OpenAI-compatible image generation gateway; inference stays off this server.
    image_generation_base_url: str | None = None
    image_generation_model: str = "stabilityai/sdxl-turbo"
    image_generation_api_key: str | None = None
    image_generation_timeout_seconds: int = 180

    # Cloudflare R2 uses its account-specific S3 API endpoint, never the public r2.dev URL.
    storage_provider: str = "cloudflare_r2"
    r2_account_id: str | None = None
    storage_endpoint: str | None = None
    storage_bucket: str = "kenyaads-media"
    storage_region: str = "auto"
    storage_access_key: str | None = None
    storage_secret_key: str | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @field_validator("database_url", "migration_database_url", mode="before")
    @classmethod
    def normalize_postgres_url(cls, value):
        if not value:
            return value
        value = str(value).strip().strip('"').strip("'")
        if value.startswith("postgres://"):
            return "postgresql+psycopg://" + value[len("postgres://"):]
        if value.startswith("postgresql://"):
            return "postgresql+psycopg://" + value[len("postgresql://"):]
        return value

    @field_validator("redis_url", mode="before")
    @classmethod
    def normalize_redis_url(cls, value):
        if not value:
            return value
        value = str(value).strip().strip('"').strip("'")
        # Upstash's copyable CLI command is not a URL; accept it but store only its URL.
        if value.startswith("redis-cli "):
            parts = value.split()
            if "-u" not in parts:
                raise ValueError("REDIS_URL CLI command must include -u followed by a URL")
            value = parts[parts.index("-u") + 1]
        if value.startswith("redis://") and ".upstash.io" in value:
            value = "rediss://" + value[len("redis://"):]
        return value

    @field_validator("storage_endpoint", mode="before")
    @classmethod
    def validate_r2_endpoint(cls, value):
        if not value:
            return value
        value = str(value).strip().strip('"').strip("'").rstrip("/")
        if "r2.dev" in value:
            raise ValueError(
                "STORAGE_ENDPOINT must be the account S3 API endpoint "
                "(https://<ACCOUNT_ID>.r2.cloudflarestorage.com), not an r2.dev public URL"
            )
        parsed = urlsplit(value)
        if parsed.scheme != "https" or not parsed.netloc:
            raise ValueError("STORAGE_ENDPOINT must be a valid HTTPS URL")
        return urlunsplit((parsed.scheme, parsed.netloc, "", "", ""))

    @property
    def effective_storage_endpoint(self) -> str | None:
        if self.storage_endpoint:
            return self.storage_endpoint
        if self.r2_account_id:
            return f"https://{self.r2_account_id}.r2.cloudflarestorage.com"
        return None

    @property
    def cors_origin_list(self) -> list[str]:
        return [x.strip() for x in self.cors_origins.split(",") if x.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
