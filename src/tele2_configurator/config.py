"""Application configuration via environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Jira
    jira_url: str = ""
    jira_username: str = ""
    jira_api_token: str = ""
    jira_project_key: str = "TELE2"

    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"

    # Nokia NSP
    nokia_nsp_url: str = ""
    nokia_nsp_username: str = ""
    nokia_nsp_password: str = ""

    # TM Forum
    tmforum_url: str = ""
    tmforum_username: str = ""
    tmforum_password: str = ""

    # Tele2 Custom API
    custom_api_url: str = ""
    custom_api_key: str = ""

    # Email
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    email_from: str = ""

    # Dashboard
    dashboard_host: str = "0.0.0.0"
    dashboard_port: int = 8000
    dashboard_secret_key: str = ""

    # Operational
    poll_interval: int = 30
    dry_run: bool = True
    log_level: str = "INFO"


settings = Settings()
