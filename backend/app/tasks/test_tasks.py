import json
import logging
from sqlalchemy import select
from app.infrastructure.db.session import SessionLocal
from app.infrastructure.db.models import CourseMaterialORM, PracticeTestORM
from datetime import datetime, timezone
import os

try:
    from llama_index.llms.openai import OpenAI
except ImportError:
    OpenAI = None
    import openai

logger = logging.getLogger(__name__)

async def generate_practice_test(ctx, material_id: int):
    with SessionLocal() as db:
        test = db.execute(select(PracticeTestORM).where(PracticeTestORM.material_id == material_id)).scalar_one_or_none()
        if test:
            return
        
        material = db.execute(select(CourseMaterialORM).where(CourseMaterialORM.id == material_id)).scalar_one_or_none()
        if not material:
            return
        
        content = material.content
        prompt = f"""Generate a 3-question multiple choice practice test based ONLY on the following text.
Return ONLY valid JSON in this exact structure, nothing else:
{{
    "questions": [
        {{
            "question": "What is X?",
            "options": ["A", "B", "C", "D"],
            "correct_answer_index": 0,
            "explanation": "Because the text says..."
        }}
    ]
}}

Text:
{content[:8000]}
"""
        try:
            if OpenAI:
                llm = OpenAI(model="gpt-4o", temperature=0.1)
                response = await llm.acomplete(prompt)
                json_str = response.text.strip()
            else:
                client = openai.AsyncOpenAI()
                response = await client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1
                )
                json_str = response.choices[0].message.content.strip()

            if json_str.startswith("```json"):
                json_str = json_str[7:]
            if json_str.endswith("```"):
                json_str = json_str[:-3]
                
            test_content = json.loads(json_str)
            new_test = PracticeTestORM(
                material_id=material_id,
                content=test_content,
                created_at=datetime.now(timezone.utc)
            )
            db.add(new_test)
            db.commit()
            logger.info(f"Generated practice test for material {material_id}")
        except Exception as e:
            logger.error(f"Error generating test for material {material_id}: {e}")
