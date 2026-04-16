from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI
import inspect

llm = OpenAI(model="gpt-4o", api_api_key="sk-dummy")
agent = ReActAgent(tools=[], llm=llm)
print(f"run signature: {inspect.signature(agent.run)}")
