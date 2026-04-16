from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI
import os

llm = OpenAI(model="gpt-4o", api_key="sk-dummy")
agent = ReActAgent(tools=[], llm=llm)
print(f"Methods: {[m for m in dir(agent) if not m.startswith('_')]}")
if hasattr(agent, 'achat'):
    print("achat found")
else:
    print("achat NOT found")
