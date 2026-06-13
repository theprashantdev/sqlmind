from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openrouter_api_key: str
    default_database_url: str = ""
    max_rows: int = 1000
    query_timeout: int = 10
    openrouter_model: str = "openai/gpt-4o-mini"

    class Config:
        env_file = ".env"

settings = Settings()
