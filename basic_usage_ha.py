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
# model_name = "openai/gpt-5-nano-2025-08-07"
# model_name = "moonshotai/kimi-vl-a3b-thinking:free" # not working
model_name = "qwen/qwen2.5-vl-32b-instruct:free"
# Generate data
# x = np.linspace(-1, 1, 50)
# y = np.sin(np.pi * x) + 0.1 * np.random.randn(50)

# # Generate image of data (or use your own)
# fig, ax = plt.subplots()
# ax.scatter(x, y)
# base64_img = llmlex.images.generate_base64_image(fig, ax, x, y)

npz_file = np.load('data_duffing/test_data0.npz')
state_data = npz_file['state']
input_data = npz_file['input']
dt=0.001
cnt = 0
system_name = "Duffing Oscillator"
base64_img_ha = llmlex.images.generate_base64_image_ha(state_data, input_data, dt, system_name,cnt,None)


# Run symbolic regression
# result = llmlex.single_call(client, base64_img, x, y, model=model_name)
result_ha = llmlex.single_call_ha(client, base64_img_ha, state_data, input_data, model=model_name)

# View results
print(f"Best function: {result_ha['ansatz']}")
print(f"Parameters: {result_ha['params']}")
print(f"Score: {result_ha['score']}")

# For more complex problems, use genetic algorithm approach
# populations = llmlex.run_genetic(
#     client, base64_img, x, y, 
#     population_size=5, num_of_generations=3,
#     model=model_name
# )
