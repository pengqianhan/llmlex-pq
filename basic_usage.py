import llmlex
import openai
import numpy as np
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv

load_dotenv() # 加载.env文件中的环境变量

# Set up API client
client = openai.OpenAI(
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key=os.getenv("GEMINI_API_KEY") if os.getenv("GEMINI_API_KEY") else "<<<<<<your_api_key>>>>>>>", 
)
model_name = "models/gemini-flash-lite-latest"
# Generate data
x = np.linspace(-1, 1, 50)
y = np.sin(np.pi * x) + 0.1 * np.random.randn(50)

# Generate image of data (or use your own)
fig, ax = plt.subplots()
ax.scatter(x, y)
base64_img = llmlex.images.generate_base64_image(fig, ax, x, y)

## basic usage
# # Run symbolic regression
# result = llmlex.single_call(client, base64_img, x, y, model=model_name)

# # View results
# print(f"Best function: {result['ansatz']}")
# print(f"Parameters: {result['params']}")
# print(f"Score: {result['score']}")

# For more complex problems, use genetic algorithm approach
populations = llmlex.run_genetic(
    client, base64_img, x, y, 
    population_size=5, num_of_generations=3,
    model=model_name
)

# View results
print(f"Best function: {populations[0][0]['ansatz']}")
print(f"Parameters: {populations[0][0]['params']}")
print(f"Score: {populations[0][0]['score']}")