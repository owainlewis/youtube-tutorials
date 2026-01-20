from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    database_url: str
    openai_api_key: str
    anthropic_api_key: str

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
