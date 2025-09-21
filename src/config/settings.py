from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    claude_api_key: str = Field(..., alias="ANTHROPIC_API_KEY")
    claude_model: str = Field("claude-3-opus-20240229", alias="CLAUDE_DEFAULT_MODEL")
    max_tokens: int = Field(2000, alias="CLAUDE_MAX_TOKENS")
    temperature: float = Field(0.2, alias="CLAUDE_TEMPERATURE")

settings = Settings()
