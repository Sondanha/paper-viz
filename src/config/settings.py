# src/config/settings.py

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Anthropic 관련
    claude_api_key: str = Field(..., alias="ANTHROPIC_API_KEY")
    claude_model: str = Field("claude-3-opus-20240229", alias="CLAUDE_DEFAULT_MODEL")
    max_tokens: int = Field(2000, alias="CLAUDE_MAX_TOKENS")
    temperature: float = Field(0.2, alias="CLAUDE_TEMPERATURE")

    # 디버깅 아웃풋 경로
    debug_dir: str = Field("/tmp/viz_debug", alias="DEBUG_DIR")

settings = Settings()
