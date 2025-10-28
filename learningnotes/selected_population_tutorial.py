"""
Python 语法讲解和演示：np.random.choice 列表推导式
Demonstration of the genetic algorithm parent selection mechanism
"""

import numpy as np

print("=" * 70)
print("原始代码解析 (Original Code Analysis)")
print("=" * 70)

# 原始代码：
# selected_population = [np.random.choice(populations[-1], size=2,
#                                        p=probs, replace=True) for _ in range(population_size)]

print("""
这段代码的作用：从当前代的种群中，根据适应度概率选择父代个体进行繁殖

关键语法点：
1. 列表推导式 (List Comprehension): [... for _ in range(population_size)]
2. np.random.choice(): NumPy 的加权随机选择函数
3. size=2: 每次选择 2 个个体作为父母
4. p=probs: 根据概率分布进行选择（适应度越高，被选中概率越大）
5. replace=True: 允许重复选择（同一个体可以被多次选为父代）
""")

print("\n" + "=" * 70)
print("实例 1: 基础的 np.random.choice 演示")
print("=" * 70)

# 简单示例：从数组中随机选择
fruits = np.array(['apple', 'banana', 'cherry', 'date', 'elderberry'])
print(f"水果列表: {fruits}")

# 随机选择 1 个
single_choice = np.random.choice(fruits)
print(f"\n随机选择 1 个: {single_choice}")

# 随机选择 3 个（允许重复）
multiple_choices = np.random.choice(fruits, size=3, replace=True)
print(f"随机选择 3 个（允许重复）: {multiple_choices}")

# 随机选择 3 个（不允许重复）
unique_choices = np.random.choice(fruits, size=3, replace=False)
print(f"随机选择 3 个（不允许重复）: {unique_choices}")


print("\n" + "=" * 70)
print("实例 2: 带概率的随机选择（模拟轮盘赌选择）")
print("=" * 70)

# 模拟一个小型种群
individuals = np.array(['个体A', '个体B', '个体C', '个体D', '个体E'])
# 假设这些是它们的适应度分数（越高越好）
fitness_scores = np.array([10, 30, 50, 5, 5])

# 计算选择概率（归一化）
probabilities = fitness_scores / np.sum(fitness_scores)

print(f"种群: {individuals}")
print(f"适应度分数: {fitness_scores}")
print(f"选择概率: {probabilities}")
print(f"  个体A: {probabilities[0]:.2%}")
print(f"  个体B: {probabilities[1]:.2%}")
print(f"  个体C: {probabilities[2]:.2%}")
print(f"  个体D: {probabilities[3]:.2%}")
print(f"  个体E: {probabilities[4]:.2%}")

# 根据概率选择 2 个父代（模拟原始代码中的 size=2）
parents = np.random.choice(individuals, size=2, p=probabilities, replace=True)
print(f"\n选中的父代: {parents}")

# 统计实验：进行 1000 次选择，看概率分布
print("\n进行 1000 次选择实验，统计每个个体被选中的次数:")
selection_counts = {ind: 0 for ind in individuals}
for _ in range(1000):
    selected = np.random.choice(individuals, size=1, p=probabilities, replace=True)[0]
    selection_counts[selected] += 1

for ind, count in selection_counts.items():
    print(f"  {ind}: {count} 次 ({count/1000:.1%})")


print("\n" + "=" * 70)
print("实例 3: 完整模拟遗传算法的父代选择过程")
print("=" * 70)

# 模拟一个更真实的遗传算法场景
# 种群中每个个体是一个字典，包含基因型和适应度
class Individual:
    def __init__(self, gene, fitness):
        self.gene = gene
        self.fitness = fitness
    
    def __repr__(self):
        return f"Individual(gene={self.gene}, fit={self.fitness:.2f})"

# 创建一个种群
population_size = 5
current_generation = [
    Individual("方程1: x^2", 0.85),
    Individual("方程2: 2*x", 0.60),
    Individual("方程3: x^3 + x", 0.95),
    Individual("方程4: sin(x)", 0.40),
    Individual("方程5: exp(x)", 0.75),
]

print("当前种群:")
for i, ind in enumerate(current_generation):
    print(f"  [{i}] {ind}")

# 提取适应度分数并计算选择概率
fitness_values = np.array([ind.fitness for ind in current_generation])
probs = fitness_values / np.sum(fitness_values)

print(f"\n选择概率分布:")
for i, (ind, prob) in enumerate(zip(current_generation, probs)):
    print(f"  [{i}] {ind.gene}: {prob:.2%}")

# 原始代码的核心逻辑：选择父代配对
print(f"\n为下一代选择 {population_size} 对父代:")
print(f'current_generation: {current_generation}')
selected_population = [
    np.random.choice(current_generation, size=2, p=probs, replace=True) 
    for _ in range(population_size)
]


for i, parents in enumerate(selected_population):
    print(f"  配对 {i+1}: ")
    print(f"    父代1: {parents[0]}")
    print(f"    父代2: {parents[1]}")


print("\n" + "=" * 70)
print("实例 4: 列表推导式逐步拆解")
print("=" * 70)

print("列表推导式语法: [表达式 for 变量 in 可迭代对象]")
print("\n等价的 for 循环写法:\n")

# 使用列表推导式（紧凑）
print("# 方式 1: 列表推导式")
print("selected_population = [np.random.choice(current_generation, size=2,")
print("                       p=probs, replace=True) for _ in range(3)]")
compact_result = [
    np.random.choice(current_generation, size=2, p=probs, replace=True) 
    for _ in range(3)
]
print(f"结果长度: {len(compact_result)}")

# 使用传统 for 循环（展开）
print("\n# 方式 2: 传统 for 循环（等价写法）")
print("selected_population = []")
print("for _ in range(3):")
print("    pair = np.random.choice(current_generation, size=2,")
print("                           p=probs, replace=True)")
print("    selected_population.append(pair)")
expanded_result = []
for _ in range(3):
    pair = np.random.choice(current_generation, size=2, p=probs, replace=True)
    expanded_result.append(pair)
print(f"结果长度: {len(expanded_result)}")


print("\n" + "=" * 70)
print("总结 (Summary)")
print("=" * 70)
print("""
原始代码的完整流程：
1. populations[-1]: 获取当前代（最后一代）的种群
2. probs: 基于适应度计算的选择概率（适应度高→概率大）
3. np.random.choice(..., size=2, p=probs, replace=True): 
   - 根据概率分布随机选择 2 个个体作为父母
   - replace=True 允许同一个体被选中两次（自交）
4. [... for _ in range(population_size)]:
   - 重复选择过程 population_size 次
   - 产生 population_size 对父代配对
5. 这些父代配对将用于生成下一代种群（通过交叉、变异等操作）

这是遗传算法中经典的"轮盘赌选择"(Roulette Wheel Selection)机制：
- 优秀个体（高适应度）有更高概率被选为父代
- 但较差个体也有小概率被选中，保持种群多样性
- 允许重复选择保证了优秀基因可以多次传递
""")

print("\n运行完成！")

