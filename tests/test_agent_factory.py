import os
import unittest
from unittest.mock import patch
from backend.app.agent import get_model
from backend.app.schemas.internal import ModelProvider
from llama_index.llms.openai import OpenAI

class TestAgentFactory(unittest.TestCase):
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test_openai_key"}, clear=True)
    def test_get_model_auto_uses_openai(self):
        model = get_model(ModelProvider.AUTO)
        self.assertIsInstance(model, OpenAI)
        self.assertEqual(model.model, 'gpt-4o-mini')

    @patch.dict(os.environ, {}, clear=True)
    def test_get_model_auto_fallback_to_openai_dummy(self):
        model = get_model(ModelProvider.AUTO)
        self.assertIsInstance(model, OpenAI)
        self.assertEqual(model.api_key, "sk-dummy")

if __name__ == '__main__':
    unittest.main()
