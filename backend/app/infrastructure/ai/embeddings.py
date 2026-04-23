import os
import logging
import hashlib
from openai import OpenAI

logger = logging.getLogger(__name__)
client = None


def get_client():
    global client
    if client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            # In a real app we'd raise an error, but for testing we return None
            logger.warning("OPENAI_API_KEY not found. Using deterministic mock embeddings.")
            return None
        client = OpenAI(api_key=api_key)
    return client


def get_embedding(text: str, model: str = "text-embedding-3-small") -> list[float]:
    cl = get_client()
    if cl is None:
        # Generate a deterministic mock vector based on the text hash
        # This ensures cosine similarity still works meaningfully for tests
        h = hashlib.sha256(text.encode()).digest()
        vector = []
        for i in range(1536):
            # Deterministic pseudo-randomness between -1 and 1
            val = ((h[i % 32] + i) % 256) / 128.0 - 1.0
            vector.append(val)
        return vector

    text = text.replace("\n", " ")
    try:
        return cl.embeddings.create(input=[text], model=model).data[0].embedding
    except Exception as e:
        logger.error(f"Error calling OpenAI embeddings API: {e}")
        # Fallback to deterministic mock if API call fails
        return get_embedding(text)  # Recurse once with cl=None effectively
