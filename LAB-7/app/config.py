"""
Pydantic Settings Configuration
Experiment 07 — Deep Research Agent Workflow (MR23-1CS0436)
"""

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    LLM_PROVIDER: str = "mock"
    OPENAI_API_KEY: str = ""
    PORT: int = 8006
    HOST: str = "127.0.0.1"
    MAX_REFLECTION_ITERATIONS: int = 3
    SAMPLE_TOPICS_FILE_PATH: str = "data/sample_topics.json"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
