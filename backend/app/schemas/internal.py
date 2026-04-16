from enum import Enum

class ModelProvider(str, Enum):
    OPENAI = "openai"
    AUTO = "auto"
