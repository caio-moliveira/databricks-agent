from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DATABRICKS_TOKEN"),
    base_url=os.getenv("base_url"),
)

response = client.chat.completions.create(
    model="databricks-meta-llama-3-1-405b-instruct",
    messages=[{"role": "user", "content": "What is Databricks?"}],
    temperature=0,
    extra_body={"usage_context": {"project": "project1"}},
)
answer = response.choices[0].message.content
print("Answer:", answer)
