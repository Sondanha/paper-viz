# src\services\llm_client.py

from anthropic import Anthropic
from src.config.settings import settings

client = Anthropic(api_key=settings.claude_api_key)

def call_claude(prompt: str) -> str:
    """
    Claude API 호출 (Anthropic SDK 사용)
    인메모리로 섹션 단위 텍스트만 주고받음
    """
    response = client.messages.create(
        model=settings.claude_model,   
        max_tokens=settings.max_tokens,
        temperature=settings.temperature,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text
