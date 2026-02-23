from abc import ABC, abstractmethod
from typing import List, Dict
from app.config import settings


class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, messages: List[Dict[str, str]]) -> str:
        pass


def get_provider() -> LLMProvider:
    if settings.OPENAI_API_KEY:
        from app.llm.openai_provider import OpenAIProvider
        return OpenAIProvider()
    from app.llm.mock_provider import MockProvider
    return MockProvider()
