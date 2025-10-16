import openai
import os
from dotenv import load_dotenv
import numpy as np
import matplotlib.pyplot as plt
import llmlex
import base64
load_dotenv() # 加载.env文件中的环境变量
client = openai.OpenAI(
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key=os.getenv("GEMINI_API_KEY") if os.getenv("GEMINI_API_KEY") else "<<<<<<your_api_key>>>>>>>", 
)
model_name = "models/gemini-flash-lite-latest"

# response = client.chat.completions.create(
#     model=model_name,
#     reasoning_effort="high",# default is "medium"
#     messages=[
#         {"role": "user", "content": "Explain how AI works in a few words"},
#     ],
# )

# print(response.choices[0].message.content)


# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

# Getting the base64 string
base64_image = encode_image("ha_image.png")

response = client.chat.completions.create(
  model=model_name,
  messages=[
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "What is in this image?",
        },
        {
          "type": "image_url",
          "image_url": {
            "url":  f"data:image/jpeg;base64,{base64_image}"
          },
        },
      ],
    }
  ],
)

print(response.choices[0].message.content)