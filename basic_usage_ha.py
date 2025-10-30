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
# model_name = "models/gemini-flash-lite-latest"
model_name = "models/gemini-flash-latest"
# model_name = "models/gemini-2.5-pro"

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
