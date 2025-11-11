import json
import llmlex
import openai
import numpy as np
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv
from prompts.system_prompt import System_prompt
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
print(state_data.shape, input_data.shape)
dt=0.001
num_variables = state_data.shape[0]
num_inputs = input_data.shape[0]
system_name = "Duffing Oscillator"
base64_img_ha = llmlex.images.generate_base64_image_ha(state_data, input_data, dt, 'ha_image_input.png')
# load system prompt
# system_prompt = open('prompts/system_prompt.md', 'r').read()
System_prompt = System_prompt.replace('system_name', system_name)
System_prompt = System_prompt.replace('num_variables', str(state_data.shape[0]))
System_prompt = System_prompt.replace('num_inputs', str(input_data.shape[0]))
print(System_prompt)


# Run symbolic regression
result_ha = llmlex.single_call_ha(client, base64_img_ha, state_data, input_data, model=model_name,system_prompt=system_prompt)

# # View results
print(f"HA dict: {result_ha['ha_dict']}")

# save the result to a json file
with open('single_call_ha.json', 'w') as f:
    json.dump(result_ha['ha_dict'], f)
# For more complex problems, use genetic algorithm approach
# populations = llmlex.run_genetic_ha(
#     client, base64_img_ha, state_data, input_data,
#     population_size=3, num_of_generations=2,
#     model=model_name,
#     system_prompt=system_prompt,
#     dt=dt,
#     total_time=10.0
# )

# # View results
# print(f"\nBest HA from genetic algorithm:")
# print(f"Score: {populations[-1][-1]['score']}")
# print(f"HA dict: {populations[-1][-1]['ha_dict']}")
# save the result to a json file
# with open('result_ha.json', 'w') as f:
#     json.dump(populations[-1][-1]['ha_dict'], f)
