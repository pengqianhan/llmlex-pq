# 快速开始: Lambda 风格 JSON 生成

## 问题

传统上，创建混合自动机的初始 JSON 需要手动编写复杂的 JSON 结构：

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

这很繁琐且容易出错！

## 解决方案

现在可以用 **lambda 风格** 来定义，就像 `get_prompt` 一样简洁：

```python
from llmlex.llm import generate_initial_ha_json

json_obj = generate_initial_ha_json(
    var_list=["x1", "x2"],
    mode_eqs={
        1: ["x2[0]", "-x1[0] - 0.1*x2[0]"]
    }
)
```

## 核心理念

### 一致的设计

**符号回归** (`get_prompt`):
```python
curve_0 = lambda x, *params: params[0]
curve_1 = lambda x, *params: params[0] * x
```

**混合自动机** (`generate_initial_ha_json`):
```python
mode_eqs = {
    1: ["x2[0]", "-x1[0] - 0.1*x2[0]"],
    2: ["x2[0]", "-x1[0]**3 - 0.5*x2[0]"]
}
```

两者都使用简洁的表达式！✨

## 快速示例

### 示例 1: 简单振荡器

```python
json_obj = generate_initial_ha_json(
    var_list=["x1", "x2"],
    mode_eqs={
        1: ["x2[0]", "-x1[0]"]
    }
)
```

### 示例 2: 带转移的两模式系统

```python
json_obj = generate_initial_ha_json(
    var_list=["x1", "x2"],
    mode_eqs={
        1: ["x2[0]", "-x1[0] - 0.1*x2[0]"],    # 线性
        2: ["x2[0]", "-x1[0]**3 - 0.5*x2[0]"]  # 非线性
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

### 示例 3: Duffing 振荡器 (带输入)

```python
json_obj = generate_initial_ha_json(
    var_list=["x"],
    mode_eqs={
        1: ["u - 0.5*x[1] + x[0] - 1.5*x[0]**3"],
        2: ["u - 0.2*x[1] + x[0] - 0.5*x[0]**3"]
    },
    transitions=[...],
    input_vars=["u"]
)
```

## 试试看！

```bash
# 运行示例
python example_lambda_to_json.py

# 运行测试
python test_lambda_json_simple.py
```

## 更多信息

详细文档: [`LAMBDA_JSON_GUIDE.md`](LAMBDA_JSON_GUIDE.md)

---

**现在定义混合自动机就像定义符号回归一样简单！** 🚀

