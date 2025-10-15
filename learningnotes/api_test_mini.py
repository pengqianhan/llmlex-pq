import openai
import os
from dotenv import load_dotenv
import numpy as np
import matplotlib.pyplot as plt
import llmlex
load_dotenv() # 加载.env文件中的环境变量
client = openai.OpenAI(
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key=os.getenv("GEMINI_API_KEY") if os.getenv("GEMINI_API_KEY") else "<<<<<<your_api_key>>>>>>>", 
)
model_name = "models/gemini-flash-lite-latest"

response = client.chat.completions.create(
    model=model_name,
    messages=[
        {"role": "user", "content": "Explain how AI works in a few words"},
    ],
)

print(response.choices[0].message.content)
