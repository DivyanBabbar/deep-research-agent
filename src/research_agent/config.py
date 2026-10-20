from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Deep Research Agent"
    environment: str = "development"
    openai_api_key: str = ""
    openai_model: str = "gpt-4.1-mini"
    tavily_api_key: str = ""
    max_results: int = 8
    request_timeout_seconds: float = 45.0
    database_path: str = "data/research.db"
    log_level: str = "INFO"


settings = Settings()
