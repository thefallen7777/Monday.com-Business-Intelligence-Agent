from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    llm_provider: str = "groq"
    llm_api_key: str
    llm_base_url: str
    llm_model: str = "llama-3.3-70b-versatile"

    monday_api_token: str
    monday_api_url: str = "https://api.monday.com/v2"
    monday_api_version: str = "2026-04"

    deals_board_name: str = "Deals"
    work_orders_board_name: str = "Work Orders"

    app_env: str = "development"
    port: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


settings = Settings()