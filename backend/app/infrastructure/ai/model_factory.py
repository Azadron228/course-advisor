import logging
from llama_index.llms.openai import OpenAI
from llama_index.core.llms import LLM
from app.domain.recommendation.entities import ModelProvider
from app.core.config import settings

logger = logging.getLogger(__name__)


class ModelFactory:
    """Central factory for managing and instantiating LLM models."""

    @staticmethod
    def create_llm(
        provider: ModelProvider = ModelProvider.AUTO,
        temperature: float = 0.1,
        max_tokens: int = 8192,
        **kwargs
    ) -> LLM:
        """Create a LlamaIndex LLM instance based on the chosen provider."""
        # Auto-detection logic - default to OpenAI
        if provider == ModelProvider.AUTO:
            provider = ModelProvider.OPENAI

        if provider == ModelProvider.OPENAI:
            api_key = settings.OPENAI_API_KEY
            if not api_key or api_key in ("sk-placeholder-key", "sk-dummy", "your-openai-api-key-here"):
                raise ValueError(
                    "OPENAI_API_KEY is missing or invalid. Please provide a valid OpenAI API key."
                )

            model_name = kwargs.get("model", "gpt-4o")
            return OpenAI(
                model=model_name,
                api_key=api_key,
                temperature=temperature,
                max_tokens=max_tokens,
                **{k: v for k, v in kwargs.items() if k != "model"}
            )

        raise ValueError(f"Unsupported model provider: {provider}")


def get_model(provider: ModelProvider = ModelProvider.AUTO) -> LLM:
    """Helper function maintaining compatibility with the existing get_model API."""
    return ModelFactory.create_llm(provider=provider)
