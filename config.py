from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    openai_api_key: str
    harness_account_id: str
    harness_api_key: str
    harness_api_url: str = "https://app.harness.io"
    mcp_server_path: Optional[str] = None
    harness_default_org_id: str
    harness_default_project_id: str

    # API Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # LangSmith Tracing (Optional)
    langchain_tracing_v2: str = "false"
    langchain_api_key: Optional[str] = None
    langchain_project: str = "harness-agent"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
