# Lambda 风格生成初始 JSON 指南

## 概述

现在可以用简洁的 **lambda 表达式** 来生成混合自动机的初始 JSON，这与 `get_prompt` 的理念一致！

### 设计理念

- **`get_prompt`**: 用 lambda 定义符号回归的起始点
  ```python
  curve_0 = lambda x, *params: params[0]
  curve_1 = lambda x, *params: ...
  ```

- **`generate_initial_ha_json`**: 用 lambda 定义混合自动机的起始点
  ```python
  mode_eqs = {
      1: ["x2[0]", "-x1[0]"],
      2: ["x2[0]", "-x1[0]**3"]
  }
  ```

两者都是为了让定义**更简洁、更直观**！

---

## 基本用法

### 1. 导入函数

```python
from llmlex.llm import generate_initial_ha_json
# 或者
from llmlex import generate_initial_ha_json
```

### 2. 定义混合自动机

```python
json_obj = generate_initial_ha_json(
    var_list=["x1", "x2"],           # 状态变量
    mode_eqs={                        # 模式方程 (lambda 风格)
        1: ["x2[0]", "-x1[0] - 0.1*x2[0]"],
        2: ["x2[0]", "-x1[0]**3 - 0.5*x2[0]"]
    },
    transitions=[                     # 可选: 转移条件
        {
            "direction": "1 -> 2",
            "condition": "abs(x1[0]) >= 1.0",
            "reset": {"x1": [], "x2": []}
        }
    ],
    input_vars=["u"]                  # 可选: 输入变量
)
```

### 3. 生成的 JSON

```json
{
  "automaton": {
    "var": "x1, x2",
    "mode": [
      {
        "id": 1,
        "eq": "x1[1] = x2[0],x2[1] = -x1[0] - 0.1*x2[0]"
      },
      {
        "id": 2,
        "eq": "x1[1] = x2[0],x2[1] = -x1[0]**3 - 0.5*x2[0]"
      }
    ],
    "edge": [...]
  }
}
```

---

## 详细示例

### 示例 1: 简单阻尼振荡器

```python
json_obj = generate_initial_ha_json(
    var_list=["x1", "x2"],
    mode_eqs={
        1: ["x2[0]", "-x1[0] - 0.1*x2[0]"]
    }
)
```

**数学意义:**
- x1' = x2
- x2' = -x1 - 0.1*x2

### 示例 2: Duffing 振荡器 (带输入)

```python
json_obj = generate_initial_ha_json(
    var_list=["x"],
    mode_eqs={
        1: ["u - 0.5*x[1] + x[0] - 1.5*x[0]**3"],
        2: ["u - 0.2*x[1] + x[0] - 0.5*x[0]**3"]
    },
    transitions=[
        {
            "direction": "1 -> 2",
            "condition": "abs(x) <= 0.8",
            "reset": {"x": ["", "x[1] * 0.95"]}
        },
        {
            "direction": "2 -> 1",
            "condition": "abs(x) >= 1.2",
            "reset": {"x": ["", "x[1] * 0.95"]}
        }
    ],
    input_vars=["u"]
)
```

**数学意义:**
- Mode 1: x'' = u - 0.5*x' + x - 1.5*x³
- Mode 2: x'' = u - 0.2*x' + x - 0.5*x³
- 带有输入 u 和模式切换条件

### 示例 3: 多变量系统

```python
json_obj = generate_initial_ha_json(
    var_list=["x1", "x2", "x3"],
    mode_eqs={
        1: ["x2[0]", "-x1[0]", "x1[0]*x2[0]"],
        2: ["x2[0]", "-x1[0]**3", "0.5*x3[0]"]
    },
    transitions=[
        {
            "direction": "1 -> 2",
            "condition": "x1[0]**2 + x2[0]**2 >= 4.0",
            "reset": {"x1": [], "x2": [], "x3": []}
        }
    ]
)
```

---

## API 参考

### `generate_initial_ha_json`

**参数:**

- `var_list` (list): **必需**. 状态变量列表
  - 例如: `["x1", "x2"]` 或 `["x"]`

- `mode_eqs` (dict): **必需**. 模式方程字典
  - 键: 模式 ID (整数)
  - 值: 方程列表 (每个变量一个方程)
  - 例如: `{1: ["x2[0]", "-x1[0]"]}`

- `transitions` (list, 可选): 转移条件列表
  - 每个元素是一个字典，包含:
    - `direction`: 字符串 "mode_from -> mode_to"
    - `condition`: 条件表达式 (字符串)
    - `reset`: 重置映射 (字典)

- `input_vars` (list, 可选): 输入变量列表
  - 例如: `["u"]` 或 `["u1", "u2"]`

**返回:**

- `dict`: 符合 `HybridAutomata.from_json()` 格式的 JSON 对象

---

## 与手动编写 JSON 的对比

### 传统方式 (手动编写)

```json
{
  "automaton": {
    "var": "x1, x2",
    "mode": [
      {
        "id": 1,
        "eq": "x1[1] = x2[0],x2[1] = -x1[0] - 0.1*x2[0]"
      }
    ],
    "edge": []
  }
}
```

需要:
- ❌ 手动拼接方程字符串
- ❌ 记住 JSON 格式细节
- ❌ 小心逗号、引号等语法
- ❌ 容易出错

### Lambda 方式 (自动生成)

```python
json_obj = generate_initial_ha_json(
    var_list=["x1", "x2"],
    mode_eqs={
        1: ["x2[0]", "-x1[0] - 0.1*x2[0]"]
    }
)
```

优势:
- ✅ 只关注数学表达式
- ✅ 自动处理格式
- ✅ 类型安全 (Python 检查)
- ✅ 更简洁直观

---

## 与 `get_prompt` 的一致性

### 符号回归 (`get_prompt`)

```python
from llmlex import get_prompt

# 定义起始函数 (lambda 风格)
function_list = [
    ("params[0]", 1),
    ("params[0] * x", 1)
]

prompt = get_prompt(function_list)
# 输出:
# curve_0 = lambda x, *params: params[0]
# curve_1 = lambda x, *params: params[0] * x
# curve_2 = lambda x, *params:
```

### 混合自动机 (`generate_initial_ha_json`)

```python
from llmlex import generate_initial_ha_json

# 定义起始模式 (lambda 风格)
json_obj = generate_initial_ha_json(
    var_list=["x1", "x2"],
    mode_eqs={
        1: ["x2[0]", "-x1[0]"],
        2: ["x2[0]", "-x1[0]**3"]
    }
)
# 输出: 完整的 JSON 对象
```

**共同点:**
- 都使用简洁的表达式定义
- 都自动生成符合标准的格式
- 都易于编程式生成和修改

---

## 完整工作流程

### 1. 生成初始 JSON

```python
from llmlex import generate_initial_ha_json

initial_json = generate_initial_ha_json(
    var_list=["x1", "x2"],
    mode_eqs={
        1: ["x2[0]", "-x1[0] - 0.1*x2[0]"],
        2: ["x2[0]", "-x1[0]**3 - 0.5*x2[0]"]
    },
    transitions=[
        {
            "direction": "1 -> 2",
            "condition": "abs(x1[0]) >= 1.0",
            "reset": {"x1": [], "x2": []}
        }
    ]
)
```

### 2. 保存到文件 (可选)

```python
import json

with open('my_hybrid_automaton.json', 'w') as f:
    json.dump(initial_json, f, indent=2)
```

### 3. 使用 LLM 提取

from llmlex.llm import call_model

# 生成 prompt (带示例)
mode_list = [
    ("x2[0]", 1),
    ("-x1[0] - 0.1*x2[0]", 2)
]

# 调用 LLM
response = call_model(
    client=my_client,
    model="gpt-4-vision",
    image=base64_image,
    prompt=prompt
)
```

### 4. 加载混合自动机

```python
from llmlex.hybrid_automata import HybridAutomata

ha = HybridAutomata.from_json(initial_json['automaton'])
```

---

## 进阶用法

### 编程式生成多个模式

```python
def create_piecewise_oscillator(n_modes=3):
    """创建分段线性振荡器"""
    mode_eqs = {}
    transitions = []
    
    for i in range(1, n_modes + 1):
        # 每个模式有不同的阻尼
        damping = 0.1 * i
        mode_eqs[i] = ["x2[0]", f"-x1[0] - {damping}*x2[0]"]
        
        # 添加转移条件
        if i < n_modes:
            transitions.append({
                "direction": f"{i} -> {i+1}",
                "condition": f"abs(x1[0]) >= {i}",
                "reset": {"x1": [], "x2": []}
            })
    
    return generate_initial_ha_json(
        var_list=["x1", "x2"],
        mode_eqs=mode_eqs,
        transitions=transitions
    )

# 使用
json_obj = create_piecewise_oscillator(n_modes=5)
```

### 从数学公式自动转换

```python
def convert_second_order_to_first_order(equation_str):
    """
    将二阶 ODE 转换为一阶系统
    例如: "x'' + 0.1*x' + x = 0" -> ["x2[0]", "-x1[0] - 0.1*x2[0]"]
    """
    # 实现转换逻辑...
    pass

# 使用
second_order_eq = "x'' + 0.5*x' + x + x**3 = u"
first_order_eqs = convert_second_order_to_first_order(second_order_eq)

json_obj = generate_initial_ha_json(
    var_list=["x"],
    mode_eqs={1: first_order_eqs},
    input_vars=["u"]
)
```

---

## 总结

### 何时使用

✅ **推荐使用 `generate_initial_ha_json`**:
- 快速原型设计
- 编程式生成 HA
- 避免手动编写 JSON
- 需要批量创建多个 HA

❌ **直接编写 JSON** (如果):
- 需要精确控制每个细节
- 已有现成的 JSON 文件
- 不需要编程式生成

### 主要优势

1. **简洁**: 只需关注数学表达式
2. **直观**: 类似 `get_prompt` 的用法
3. **安全**: 自动处理格式和语法
4. **灵活**: 支持复杂场景 (多模式、输入、转移)

### 下一步

查看更多示例:
```bash
python example_lambda_to_json.py
```

阅读完整文档:
- `example_ha_prompt_usage.py` - Prompt 生成示例
- `demo_prompt_ha.py` - 快速演示
- `CHANGES_SUMMARY.md` - 混合自动机支持总结

---

**快乐建模！** 🎉

