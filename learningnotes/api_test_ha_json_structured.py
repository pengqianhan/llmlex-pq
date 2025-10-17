"""
使用结构化输出生成混合自动机 JSON
使用 Pydantic 模型定义 JSON schema，让 LLM 生成符合 json_readme.md 格式的输出
"""
import openai
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Optional, Any
import json

load_dotenv()

# ============ Pydantic 模型定义（符合 json_readme.md 格式）============

class ModeDefinition(BaseModel):
    """Define a single mode"""
    id: int = Field(description="Mode ID, integer")
    eq: str = Field(description="ODE of each variable in the mode, separated by commas. Example: 'x1[1] = 1, x2[2] = -3 * x2[1] - 25 * x2[0] + 25'. The left side of the equal sign is the highest order derivative, the right side is the expression")

class EdgeTransition(BaseModel):
    """Define transition edges between modes (no reset field)"""
    direction: str = Field(description="Transition direction, format 'u -> v', from mode u to mode v")
    condition: str = Field(description="Transition condition (guard), cannot contain variables not defined in var. Example: 'x1 >= 5'")

class AutomationStructure(BaseModel):
    """Core structure of the hybrid automaton (Note: key name is 'automation' not 'automaton')"""
    var: str = Field(description="Variable list, separated by commas, example: 'x1, x2'")
    input: str = Field(description="Input variable list, separated by commas, example: 'u1, u2'")
    mode: List[ModeDefinition] = Field(description="List of automaton modes")
    edge: List[EdgeTransition] = Field(description="List of transition edges between modes")

class ConfigSettings(BaseModel):
    """Configuration parameters for fitting the difference equation"""
    dt: float = Field(default=0.001, description="Discrete time, default 0.001")
    total_time: float = Field(default=10.0, description="Sampling total time, default 10")
    dim: int = Field(default=3, description="Dimension of the difference equation, default 3")
    # window_size: int = Field(default=10, description="Sliding window size, default 10")
    # clustering_method: str = Field(default="fit", description="Clustering method, default fit, options are fit and dis")
    # minus: bool = Field(default=False, description="Whether to minimize order, default false")
    # need_bias: bool = Field(default=True, description="Whether to include constant term, default true")
    # kernel: str = Field(default="linear", description="SVM kernel function, default linear")
    # other_items: str = Field(default="", description="Other nonlinear or cross terms for the difference equation, default empty")

class HybridAutomatonJSON(BaseModel):
    """Complete hybrid automaton JSON structure"""
    automation: AutomationStructure = Field(description="Automaton structure")
    init_state: List[Dict[str, Any]] = Field(description="Initial state list, each state contains mode and initial values of each variable")
    config: ConfigSettings = Field(description="Configuration parameters for fitting the difference equation")

# ============ API 调用 ============

def generate_ha_json_with_structured_output():
    """使用结构化输出生成混合自动机 JSON"""
    
    client = openai.OpenAI(
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        api_key=os.getenv("GEMINI_API_KEY") if os.getenv("GEMINI_API_KEY") else "<<<<<<your_api_key>>>>>>>",
    )
    model_name = "models/gemini-flash-lite-latest"
    
    # 加载目标格式的示例作为参考
    example_description = """
这是一个简单的二维混合系统示例。系统有：
- 两个状态变量：x1, x2
- 两个模式（mode 1 和 mode 2），每个模式有不同的动力学方程
- 两个转换边：当 x1 >= 5 时从模式1切换到模式2；当 x1 <= 0 时从模式2切换到模式1

模式 1 的方程：
  x1[1] = 1
  x2[2] = -3 * x2[1] - 25 * x2[0] + 25

模式 2 的方程：
  x1[1] = -1
  x2[2] = -3 * x2[1] - 25 * x2[0]

其中 x[k] 表示 x 的 k 阶微分。
等号左侧为最高阶微分，右侧是表达式。
"""
    
    # 构建提示
    system_prompt = """你是一个混合自动机专家。请根据用户提供的系统描述，生成符合指定格式的混合自动机 JSON 对象。

重要格式说明：
1. 顶层键名是 'automation'（不是 'automaton'）
2. 'var' 字段是逗号分隔的字符串，例如 "x1, x2"
3. 'eq' 字段包含所有变量的 ODE，用逗号分隔，例如 "x1[1] = 1, x2[2] = -3 * x2[1] - 25 * x2[0] + 25"
4. 'edge' 中只有 'direction' 和 'condition'，没有 'reset' 字段
5. 'init_state' 中，变量名直接作为键，例如 {"mode": 1, "x1": [0], "x2": [0]}
6. 'condition' 字段不能出现 var 中未定义的变量
7. x[k] 表示 x 的 k 阶微分，等号左侧为最高阶微分
"""
    
    user_prompt = f"""请根据以下描述生成一个混合自动机 JSON：

{example_description}

请生成包含以下内容的完整 JSON：
1. automation 结构（包含 var, mode, edge）
2. init_state 列表（至少包含 2 个不同的初始状态）
3. config 配置（使用默认值即可）
"""
    
    print("正在调用 API...")
    completion = client.beta.chat.completions.parse(
        model=model_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format=HybridAutomatonJSON,
    )
    
    # 提取结果
    result = completion.choices[0].message.parsed
    
    if result:
        print("\n生成的 JSON 结构：")
        print("=" * 60)
        # 转换为字典并格式化输出
        result_dict = result.model_dump()
        print(json.dumps(result_dict, indent=2, ensure_ascii=False))
        
        # 保存到文件
        output_file = "learningnotes/generated_duffing.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result_dict, f, indent=2, ensure_ascii=False)
        print(f"\n已保存到: {output_file}")
        
        return result_dict
    else:
        print("生成失败")
        return None

# ============ 测试函数 ============

def test_with_image():
    """结合图像输入生成混合自动机 JSON"""
    import numpy as np
    import sys
    sys.path.insert(0, '/home/phan635/HybridAutomata/baseline_ha/llmlex-pq')
    import llmlex
    
    client = openai.OpenAI(
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        api_key=os.getenv("GEMINI_API_KEY") if os.getenv("GEMINI_API_KEY") else "<<<<<<your_api_key>>>>>>>",
    )
    model_name = "models/gemini-flash-lite-latest"
    
    # 加载数据
    npz_file = np.load('/home/phan635/HybridAutomata/baseline_ha/llmlex-pq/data_duffing/test_data0.npz')
    state_data = npz_file['state']
    input_data = npz_file['input']
    dt = 0.001
    cnt = 0
    system_name = "Hybrid System"
    
    # 生成图像
    base64_img = llmlex.images.generate_base64_image_ha(
        state_data, input_data, dt, system_name, cnt, None
    )
    
    # 构建提示
    system_prompt_simple = """You are a hybrid automaton expert. Please analyze the hybrid system data in the image and identify:
1. The number of discrete modes (by detecting changes in dynamical behavior)
2. The ODE for each mode
3. The transition conditions (guards) between modes

Then generate a hybrid automaton JSON object that fits the specified format.

Important format notes:
1. The top-level key is 'automation' (not 'automaton')
2. The 'var' field is a comma-separated string
3. The 'eq' field contains all ODEs for the variables, separated by commas
4. In 'edge', only 'direction' and 'condition' fields are present; there is no 'reset' field
5. In 'init_state', variable names are used as keys directly
6. x[k] means the k-th derivative of x; the left side of the equation should be the highest order derivative
"""

    # load system prompt
    system_prompt_md = open('prompts/system_prompt.md', 'r').read()
    system_prompt = system_prompt_md
    print(system_prompt)
    user_prompt = """Please analyze the hybrid system data in the image and generate the corresponding hybrid automaton JSON.

Guidelines:
- Observe the mode switch points in the data
- Identify the dynamics of each mode
- Determine appropriate transition conditions
- Equation format: x[k] represents the k-th derivative of x
- Variable naming: use x1, x2, ... or a single variable name
"""
    
    print("正在调用 API（带图像）...")
    completion = client.beta.chat.completions.parse(
        model=model_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{base64_img}"}
                    }
                ]
            },
        ],
        response_format=HybridAutomatonJSON,
    )
    
    result = completion.choices[0].message.parsed
    
    if result:
        print("\n从图像生成的 JSON 结构：")
        print("=" * 60)
        result_dict = result.model_dump()
        print(json.dumps(result_dict, indent=2, ensure_ascii=False))
        
        output_file = "learningnotes/generated_duffing_from_image.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result_dict, f, indent=2, ensure_ascii=False)
        print(f"\n已保存到: {output_file}")
        
        return result_dict
    else:
        print("生成失败")
        return None

if __name__ == "__main__":
    # print("测试 1: 基于文本描述生成 JSON")
    # print("=" * 60)
    # result1 = generate_ha_json_with_structured_output()
    
    print("\n\n测试 2: 基于图像数据生成 JSON")
    print("=" * 60)
    result2 = test_with_image()

