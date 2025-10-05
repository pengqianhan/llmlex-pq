import llmlex
import openai
import numpy as np
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv

load_dotenv() # 加载.env文件中的环境变量

# Set up API client
client = openai.OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY") if os.getenv("OPENROUTER_API_KEY") else "<<<<<<your_api_key>>>>>>>", 
)
# model_name = "openai/gpt-4o"
# model_name = "moonshotai/kimi-vl-a3b-thinking:free" # not working
model_name = "qwen/qwen2.5-vl-32b-instruct:free"
# Generate data
x = np.linspace(-1, 1, 50)
y = np.sin(np.pi * x) + 0.1 * np.random.randn(50)
data = np.load('data_duffing/test_data0.npz')

# Generate image of data (or use your own)
fig, ax = plt.subplots()
ax.scatter(x, y)
base64_img = llmlex.images.generate_base64_image(fig, ax, x, y)

# Run symbolic regression
result = llmlex.single_call(client, base64_img, x, y, model=model_name)

# View results
print(f"Best function: {result['ansatz']}")
print(f"Parameters: {result['params']}")
print(f"Score: {result['score']}")

# For more complex problems, use genetic algorithm approach
# populations = llmlex.run_genetic(
#     client, base64_img, x, y, 
#     population_size=5, num_of_generations=3,
#     model=model_name
# )
