import openai
import os
from dotenv import load_dotenv
import numpy as np
import matplotlib.pyplot as plt
import llmlex
load_dotenv() # 加载.env文件中的环境变量

# Set up API client for openrouter
# client = openai.OpenAI(
#     base_url="https://openrouter.ai/api/v1",
#     api_key=os.getenv("OPENROUTER_API_KEY") if os.getenv("OPENROUTER_API_KEY") else "<<<<<<your_api_key>>>>>>>", 
# )
# model = "qwen/qwen2.5-vl-32b-instruct:free"

# Set up API client for gemini
client = openai.OpenAI(
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key=os.getenv("GEMINI_API_KEY") if os.getenv("GEMINI_API_KEY") else "<<<<<<your_api_key>>>>>>>", 
)
model_name = "models/gemini-flash-lite-latest"

print("Model: ", model_name)
system_prompt = ("You are a symbolic regression expert. Analyze the data in the image and provide an improved mathematical ansatz. "
                         "Respond with ONLY the ansatz formula, without any explanation or commentary. Ensure it is in valid python. You may use numpy functions. "
                         "params is a list of parameters that can be of any length or complexity. "
                        )
prompt = "import numpy as np\ncurve_0 = lambda x, *params: params[0] "
x = np.linspace(-1, 1, 50)
y = np.sin(np.pi * x) + 0.1 * np.random.randn(50)

# Generate image of data (or use your own)
fig, ax = plt.subplots()
ax.scatter(x, y)
image = llmlex.images.generate_base64_image(fig, ax, x, y)
response = client.chat.completions.create(
            model=model_name,
            # reasoning_effort="high",# default is "medium"
            messages=[
                { "role": "system", 
                 "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{image}"},
                        },
                        {
                            "type": "text",
                            "text": prompt,
                        },
                    ],
                }
            ],
            max_tokens=1028,
            temperature=1,# default is 1
            
        )

print("response: \n", response.choices[0].message.content)