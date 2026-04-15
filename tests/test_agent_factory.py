import os
import unittest
from unittest.mock import patch
from backend.app.agent import get_model
from backend.app.schemas.internal import ModelProvider
from llama_index.llms.openai import OpenAI
from llama_index.llms.ollama import Ollama

class TestAgentFactory(unittest.TestCase):
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test_openai_key"}, clear=True)
    def test_get_model_auto_prefers_openai_if_set(self):
        model = get_model(ModelProvider.AUTO)
        self.assertIsInstance(model, OpenAI)
        self.assertEqual(model.model, 'gpt-4o')

    @patch.dict(os.environ, {"OLLAMA_BASE_URL": "http://localhost:11434"}, clear=True)
    def test_get_model_auto_prefers_ollama_if_set(self):
        # Clear OpenAI to avoid picking it
        with patch.dict(os.environ, {"OPENAI_API_KEY": ""}):
            model = get_model(ModelProvider.AUTO)
            self.assertIsInstance(model, Ollama)
            self.assertEqual(model.model, 'llama3.2')

    @patch.dict(os.environ, {}, clear=True)
    def test_get_model_auto_fallback_to_openai_dummy(self):
        model = get_model(ModelProvider.AUTO)
        self.assertIsInstance(model, OpenAI)
        self.assertEqual(model.api_key, "sk-dummy")

if __name__ == '__main__':
    unittest.main()
