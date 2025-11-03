# 遗传算法中 Population 变量的详细分析

本文档详细解释了 `llmlex/llmlex.py` 中遗传算法部分的关键变量和代码逻辑。

## 目录
- [1. Population 变量结构](#1-population-变量结构)
- [2. 父代选择机制](#2-父代选择机制)
- [3. 完整的遗传算法流程](#3-完整的遗传算法流程)

---

## 1. Population 变量结构

### 1.1 代码位置
文件：`llmlex/llmlex.py:644`

```python
# Use our helper function to safely execute the async code in any context
population = execute_async_in_loop(generate_population())
```

### 1.2 变量含义

**`population`** 是一个**列表（list）**，代表**单个 generation（代）中的所有个体**。

#### 结构示意：
```python
population = [individual_1, individual_2, individual_3, ..., individual_n]
```

其中：
- **个体数量** = `population_size`（默认为 5）
- 每个 **individual（个体）** 是一个**字典（dict）**

### 1.3 单个个体（Individual）的数据结构

```python
individual = {
    'ansatz': 'params[0] * np.sin(params[1] * x)',  # LLM生成的数学表达式
    'params': [1.0, 3.14],                          # 拟合后的参数值（numpy array）
    'score': -0.052,                                # 拟合质量分数（负的归一化卡方值，越接近0越好）
    'Num_params': 2,                                # 表达式中的参数个数
    'response': '...',                              # LLM的原始响应文本
    'prompt': '...',                                # 发送给LLM的提示词
    'function_list': None                           # 父代函数列表（用于遗传算法的交叉操作）
}
```

#### 各字段详解：

| 字段名 | 类型 | 含义 | 示例 |
|--------|------|------|------|
| `ansatz` | str | LLM生成的数学表达式，使用 `params[i]` 表示参数 | `'params[0] * np.sin(params[1] * x)'` |
| `params` | numpy.ndarray | 通过曲线拟合得到的参数值 | `array([1.0, 3.14])` |
| `score` | float | 拟合质量分数（负的归一化卡方值） | `-0.052` |
| `Num_params` | int | 表达式中的参数个数 | `2` |
| `response` | str | LLM的原始响应文本 | `'Based on the plot, I suggest...'` |
| `prompt` | str | 发送给LLM的提示词 | `'Given the following data...'` |
| `function_list` | list/None | 父代函数列表，用于遗传算法 | `[('sin(x)', [1.0]), ('cos(x)', [2.0])]` |

### 1.4 Population vs Populations

#### 区别：
- **`population`**（单数）：表示**单个 generation** 的所有个体
- **`populations`**（复数）：表示**所有 generation** 的列表

#### 代码示例（`llmlex/llmlex.py:738`）：
```python
population.sort(key=lambda x: x['score'])  # 按分数排序（越小越好）
populations.append(population)              # 将当前代添加到所有代的列表中
```

#### 结构对比：
```python
# population - 单个 generation
population = [individual_1, individual_2, ..., individual_n]

# populations - 所有 generations
populations = [
    generation_0,  # 第0代（初始代）
    generation_1,  # 第1代
    generation_2,  # 第2代
    ...
]
```

### 1.5 初始代的生成过程

代码位置：`llmlex/llmlex.py:603-641`

```python
async def generate_population():
    tasks = []
    semaphore = asyncio.Semaphore(10)  # 限制并发请求数为10

    async def create_individual():
        # 为每个个体进行最多5次尝试
        max_attempts = 5
        for attempt in range(max_attempts):
            try:
                # 计算指数退避延迟
                backoff_time = 0.1 * (2 ** attempt)  # 0.1s, 0.2s, 0.4s, 0.8s, 1.6s

                # 调用LLM生成表达式并拟合
                result = await async_single_call(
                    client, base64_image, x, y, model=model,
                    system_prompt=system_prompt,
                    stats=api_stats, imports=imports
                )
                if result is not None:
                    return result

                # 如果失败，等待后重试
                await asyncio.sleep(backoff_time)
            except Exception as e:
                logger.error(f"Error in attempt {attempt+1}/{max_attempts}: {e}")
                await asyncio.sleep(backoff_time)

        return None

    # 为种群中的每个个体创建任务
    for i in range(population_size):  # 默认 population_size = 5
        tasks.append(create_individual())

    # 并发执行所有任务
    results = await asyncio.gather(*tasks)
    return [r for r in results if r is not None]  # 过滤掉失败的个体
```

**关键特点**：
- 使用**异步并发**生成所有个体，提高效率
- 使用 `Semaphore(10)` 限制同时发送的API请求数
- 每个个体失败时会进行**指数退避重试**（最多5次）
- 最终返回成功生成的所有个体

---

## 2. 父代选择机制

### 2.1 核心代码

文件：`llmlex/llmlex.py:778-781`

```python
selected_population = [np.random.choice(populations[-1], size=2,
                                       p=probs, replace=True)
                       for _ in range(population_size)]

func_lists = [[(pops[0]['ansatz'], pops[0]['params']),
               (pops[1]['ansatz'], pops[1]['params'])]
              for pops in selected_population]
```

### 2.2 详细解释

#### 问题：这段代码是只从最近一代中随机抽取两个个体作为父代吗？

**答案：不完全对！**

#### 正确理解：

这段代码执行的是：
1. **重复 `population_size` 次**（默认5次）
2. 每次都从**最近一代** `populations[-1]` 中**随机选择 2 个个体**
3. 选择概率由 `probs` 决定（基于适应度的概率分布）
4. `replace=True` 表示**有放回抽样**（同一个体可被多次选中）

### 2.3 参数详解

```python
np.random.choice(
    populations[-1],    # 从最近一代的种群中选择
    size=2,             # 每次选择2个个体（作为一对父代）
    p=probs,            # 选择概率分布（基于适应度）
    replace=True        # 有放回抽样（允许重复选择）
)
```

| 参数 | 含义 | 作用 |
|------|------|------|
| `populations[-1]` | 最近一代的种群 | 选择的来源 |
| `size=2` | 每次选2个 | 形成一对父代 |
| `p=probs` | 概率分布 | 适应度高的个体被选中概率更大 |
| `replace=True` | 有放回抽样 | 优秀个体可能被多次用作父代 |

### 2.4 结果结构

```python
selected_population = [
    [parent1_a, parent2_a],  # 第1对父代 → 生成第1个子代
    [parent1_b, parent2_b],  # 第2对父代 → 生成第2个子代
    [parent1_c, parent2_c],  # 第3对父代 → 生成第3个子代
    [parent1_d, parent2_d],  # 第4对父代 → 生成第4个子代
    [parent1_e, parent2_e],  # 第5对父代 → 生成第5个子代
]
```

每对父代（`[parent1, parent2]`）都是从 `populations[-1]` 中独立选择的两个个体字典。

### 2.5 提取父代函数信息

代码位置：`llmlex/llmlex.py:781`

```python
func_lists = [[(pops[0]['ansatz'], pops[0]['params']),
               (pops[1]['ansatz'], pops[1]['params'])]
              for pops in selected_population]
```

**作用**：从每对父代中提取 `ansatz` 和 `params`，用于后续的交叉（crossover）操作。

#### 示例：
```python
# 假设 selected_population[0] = [parent1, parent2]
# 其中：
#   parent1 = {'ansatz': 'params[0] * x', 'params': [2.0], ...}
#   parent2 = {'ansatz': 'params[0] * x**2', 'params': [1.5], ...}

# 则 func_lists[0] 为：
func_lists[0] = [
    ('params[0] * x', [2.0]),      # 父代1的函数信息
    ('params[0] * x**2', [1.5])    # 父代2的函数信息
]
```

### 2.6 选择概率计算

代码位置：`llmlex/llmlex.py:757-775`

```python
# 获取所有个体的分数
scores = np.array([ind['score'] for ind in populations[-1]])
finite_scores = scores[np.isfinite(scores)]

if len(finite_scores) == 0:
    # 如果没有有效分数，使用均匀分布
    probs = np.ones(len(scores)) / len(scores)
else:
    # 归一化分数到 [0, 1]
    normalized_scores = (scores - np.min(finite_scores)) / (np.max(finite_scores) - np.min(finite_scores) + 1e-6)
    normalized_scores = np.nan_to_num(normalized_scores, nan=0.0, posinf=0.0, neginf=0.0)

    # 使用 softmax 计算选择概率（带温度参数）
    exp_scores = np.exp((normalized_scores - np.max(normalized_scores)) / temperature)
    exp_scores = np.nan_to_num(exp_scores, nan=0.0)

    if np.sum(exp_scores) < 1e-10:
        probs = np.ones_like(exp_scores) / len(exp_scores)
    else:
        probs = exp_scores / np.sum(exp_scores)
```

**关键点**：
- **分数越高**（越接近0），被选中的概率**越大**
- 使用 **softmax with temperature** 控制选择压力
- 处理无效值（NaN, Inf）确保概率分布有效

---

## 3. 完整的遗传算法流程

### 3.1 算法概览

```
┌─────────────────────────────────────────────────┐
│  Step 1: 生成初始代 (Generation 0)              │
│  population = generate_population()             │
│  populations.append(population)                 │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│  Step 2: 进化循环 (Generations 1 to N)          │
│  for generation in range(1, num_of_generations):│
└─────────────────────────────────────────────────┘
                    ↓
    ┌───────────────────────────────────┐
    │ 2.1 计算选择概率                   │
    │ probs = calculate_probabilities() │
    └───────────────────────────────────┘
                    ↓
    ┌───────────────────────────────────┐
    │ 2.2 选择父代                       │
    │ selected_population = select()    │
    └───────────────────────────────────┘
                    ↓
    ┌───────────────────────────────────┐
    │ 2.3 交叉 + 变异（通过LLM）         │
    │ offspring = crossover_mutate()    │
    └───────────────────────────────────┘
                    ↓
    ┌───────────────────────────────────┐
    │ 2.4 精英保留（可选）               │
    │ population.append(best_individual)│
    └───────────────────────────────────┘
                    ↓
    ┌───────────────────────────────────┐
    │ 2.5 添加到种群历史                 │
    │ populations.append(population)    │
    └───────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│  Step 3: 返回所有代的种群                       │
│  return populations                             │
└─────────────────────────────────────────────────┘
```

### 3.2 关键代码片段

#### 3.2.1 初始化

```python
# llmlex/llmlex.py:580-590
populations = []

# Generate initial population (Generation 0)
use_async = True
logger.info(f"Generating initial population asynchronously")

# ... (异步生成代码见 1.5 节)

population = execute_async_in_loop(generate_population())
logger.info(f"Generated {len(population)} individuals")

# 处理分数并排序
population.sort(key=lambda x: x['score'])
populations.append(population)
```

#### 3.2.2 进化循环

```python
# llmlex/llmlex.py:740-850
for generation in range(1, num_of_generations):
    logger.info(f"=== Generation {generation}/{num_of_generations-1} ===")

    # 获取当前最佳个体
    best_pop = populations[-1][0]

    # 计算选择概率（见 2.6 节）
    # ...

    # 选择父代（见 2.1-2.5 节）
    selected_population = [np.random.choice(populations[-1], size=2,
                                           p=probs, replace=True)
                           for _ in range(population_size)]

    # 提取父代函数信息
    func_lists = [[(pops[0]['ansatz'], pops[0]['params']),
                   (pops[1]['ansatz'], pops[1]['params'])]
                  for pops in selected_population]

    # 生成新一代
    population = []
    if elite:
        population.append(best_pop)  # 精英保留

    # 通过交叉和变异生成新个体
    # ... (异步生成，类似初始代)

    # 排序并添加到历史
    population.sort(key=lambda x: x['score'])
    populations.append(population)
```

### 3.3 与传统遗传算法的区别

| 传统遗传算法 | LLMLEx 遗传算法 |
|-------------|----------------|
| 使用位串或树结构表示基因 | 使用数学表达式字符串（ansatz） |
| 显式定义交叉算子（如单点交叉） | 通过 LLM 理解父代函数并生成新函数 |
| 显式定义变异算子（如翻转位） | LLM 自主进行创新和变异 |
| 适应度函数需人工设计 | 使用曲线拟合的归一化卡方值 |
| 选择、交叉、变异分步进行 | LLM 同时完成交叉和变异 |

### 3.4 LLM 如何执行交叉和变异

当调用 `async_single_call()` 时，会将父代函数信息加入到提示词中：

```python
# llmlex/llm.py: get_prompt() 函数
prompt = f"""
Given the following plot of data, suggest a mathematical function that fits the data.

Parent functions for reference:
1. {func_list[0][0]} with parameters {func_list[0][1]}
2. {func_list[1][0]} with parameters {func_list[1][1]}

Please suggest a new function that combines or improves upon these parent functions.
"""
```

**LLM 的角色**：
- 理解父代函数的结构和特点
- 进行**智能交叉**（组合父代的优点）
- 进行**智能变异**（创新性改进）
- 生成新的数学表达式

---

## 4. 总结

### 4.1 关键要点

1. **`population`** 是单个 generation 中所有个体的列表
2. 每个个体包含完整的函数信息（表达式、参数、分数等）
3. 父代选择采用**基于适应度的轮盘赌选择**，重复 `population_size` 次
4. 每次选择**2个父代**，用于生成**1个子代**
5. LLM 同时完成交叉和变异操作
6. 可选的**精英保留**机制确保最优解不丢失

### 4.2 数据流图

```
Generation 0:
population = [ind1, ind2, ind3, ind4, ind5]
    ↓ (append)
populations = [[ind1, ind2, ind3, ind4, ind5]]

Generation 1:
    ↓ (select from populations[-1])
selected_population = [[ind1, ind3], [ind2, ind2], [ind1, ind4], [ind5, ind2], [ind3, ind5]]
    ↓ (crossover + mutate via LLM)
population = [new_ind1, new_ind2, new_ind3, new_ind4, new_ind5]
    ↓ (append)
populations = [
    [ind1, ind2, ind3, ind4, ind5],           # Gen 0
    [new_ind1, new_ind2, new_ind3, ...]       # Gen 1
]

... (repeat for num_of_generations)
```

### 4.3 参考文献

- 代码文件：`llmlex/llmlex.py`
- 相关函数：
  - `run_genetic()` - 主函数 (行 500+)
  - `generate_population()` - 生成种群 (行 603)
  - `async_single_call()` - 生成单个个体 (行 300+)
  - `get_prompt()` - 构造提示词 (`llmlex/llm.py`)

---

**文档创建日期**：2025-11-03
**作者**：基于代码分析和问答整理
**相关代码版本**：llmlex-pq 当前版本
