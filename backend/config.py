"""
InsightAgent Backend Configuration
Pydantic BaseSettings managing database connections, LLM credentials, and timeouts.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env", override=True)


class Settings(BaseSettings):
    PROJECT_NAME: str = "InsightAgent"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'database' / 'insight_brokerage.db'}")
    DB_TIMEOUT_MS: int = 2500

    # MCP Server
    MCP_SERVER_URL: str = os.getenv("MCP_SERVER_URL", "http://localhost:8001/sse")
    MCP_USE_IN_PROCESS: bool = os.getenv("MCP_USE_IN_PROCESS", "true").lower() == "true"

    # LLM Settings (Multi-provider support: Gemini, OpenAI, Anthropic, Mock)
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "auto") # "gemini", "openai", "mock", "auto"
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", os.getenv("GOOGLE_API_KEY", ""))
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "gemini-3-flash-preview")

    # Guardrails & Retries
    MAX_SQL_RETRIES: int = 2
    MAX_ROWS_RETURNED: int = 500

    model_config = {"env_file": ".env", "extra": "allow"}


settings = Settings()
