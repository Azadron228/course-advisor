import os
from openai import OpenAI

client = None

def get_client():
    global client
    if client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
             # In a real app we'd raise an error, but for testing we might return a mock
             return None
        client = OpenAI(api_key=api_key)
    return client

def get_embedding(text: str, model: str = "text-embedding-3-small") -> list[float]:
    cl = get_client()
    if cl is None:
        # Return a mock vector if no client (for local testing/no key)
        # This is 1536 dimensions as per design
        return [0.0] * 1536
        
    text = text.replace("\n", " ")
    return cl.embeddings.create(input=[text], model=model).data[0].embedding
