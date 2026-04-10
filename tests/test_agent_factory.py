import os
import unittest
from unittest.mock import patch
from backend.app.agent import get_model
from backend.app.models import ModelProvider
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.models.test import TestModel

class TestAgentFactory(unittest.TestCase):
    @patch.dict(os.environ, {"GOOGLE_API_KEY": "test_google_key"})
    def test_get_model_auto_prefers_gemini(self):
        model = get_model(ModelProvider.AUTO)
        self.assertIsInstance(model, GoogleModel)

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test_openai_key"}, clear=True)
    def test_get_model_auto_falls_back_to_openai(self):
        # Ensure GOOGLE_API_KEY is not set
        model = get_model(ModelProvider.AUTO)
        self.assertIsInstance(model, OpenAIChatModel)
        self.assertEqual(model.model_name, 'gpt-4o')

    @patch.dict(os.environ, {}, clear=True)
    def test_get_model_auto_fallback_to_test(self):
        model = get_model(ModelProvider.AUTO)
        self.assertIsInstance(model, TestModel)

if __name__ == '__main__':
    unittest.main()
