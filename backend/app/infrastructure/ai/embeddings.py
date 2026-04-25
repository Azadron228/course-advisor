import logging
from openai import OpenAI
from app.core.config import settings

logger = logging.getLogger(__name__)
client = None


def get_client():
    global client
    if client is None:
        api_key = settings.OPENAI_API_KEY
        if not api_key or api_key == "sk-placeholder-key" or api_key == "your-openai-api-key-here":
            raise ValueError("OPENAI_API_KEY is missing or invalid. Please provide a valid OpenAI API key.")
        client = OpenAI(api_key=api_key)
    return client


def get_embedding(text: str, model: str = "text-embedding-3-small") -> list[float]:
    cl = get_client()
    text = text.replace("\n", " ")
    return cl.embeddings.create(input=[text], model=model).data[0].embedding
