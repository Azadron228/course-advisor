from enum import Enum

class ModelProvider(str, Enum):
    OPENAI = "openai"
    OLLAMA = "ollama"
    GEMINI = "gemini"
    AUTO = "auto"
