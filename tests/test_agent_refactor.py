import unittest
import json
from backend.app.agent import AgentRecommendation, is_capable_model, parse_agent_recommendation
from pydantic import ValidationError
from llama_index.llms.openai import OpenAI

class TestAgentRefactor(unittest.TestCase):
    def test_recommendation_validation(self):
        # Valid recommendation
        rec = AgentRecommendation(
            score=0.9, 
            reasoning="This is a very good course for you.", 
            tags=["Highly Recommended"]
        )
        self.assertEqual(rec.score, 0.9)
        
        # Invalid: High score with short reasoning
        with self.assertRaises(ValidationError):
            AgentRecommendation(
                score=0.9, 
                reasoning="Short.", 
                tags=["Tag"]
            )
            
        # Low score with short reasoning should be fine (if not explicitly blocked)
        rec_low = AgentRecommendation(
            score=0.1, 
            reasoning="Not fit.", 
            tags=["Irrelevant"]
        )
        self.assertEqual(rec_low.score, 0.1)

    def test_capable_model_helper(self):
        self.assertTrue(is_capable_model(OpenAI(model="gpt-4o")))

    def test_parse_agent_recommendation(self):
        # Normal JSON
        data = {"score": 0.8, "reasoning": "Excellent match for your skills.", "tags": ["AI"]}
        rec = parse_agent_recommendation(json.dumps(data))
        self.assertEqual(rec.score, 0.8)
        
        # Aliased fields (hallucinations from weak models)
        aliased_data = {
            "relevanceScore": 0.7,
            "conclusiveReasoning": "Good fit.",
            "descriptionTags": ["Tag1"]
        }
        rec_aliased = parse_agent_recommendation(json.dumps(aliased_data))
        self.assertEqual(rec_aliased.score, 0.7)
        self.assertEqual(rec_aliased.reasoning, "Good fit.")
        self.assertEqual(rec_aliased.tags, ["Tag1"])

        # JSON with extra text (regex fallback)
        text = "Based on my analysis, here is the result: ```json\n" + json.dumps(data) + "\n``` Let me know if you need more help."
        rec = parse_agent_recommendation(text)
        self.assertEqual(rec.score, 0.8)
        
        # Invalid JSON
        with self.assertRaises(ValueError):
            parse_agent_recommendation("This is not JSON at all.")

if __name__ == '__main__':
    unittest.main()
