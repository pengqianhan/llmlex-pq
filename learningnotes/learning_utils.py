"""
Learning utilities for understanding and debugging LLMLEx data structures.
"""


def explain_population_structure(population):
    """
    打印并讲解 population 变量的结构和内容。
    
    Args:
        population: 包含个体（individuals）的列表，每个个体代表一个候选的数学表达式及其拟合结果
    
    Returns:
        None (仅打印输出)
    """
    print("\n" + "="*80)
    print("【population 变量讲解】")
    print("="*80)
    print(f"\n1. population 的类型: {type(population)}")
    print(f"   - 这是一个列表，包含了 {len(population)} 个个体（individuals）")
    print(f"   - 每个个体代表一个候选的数学表达式（ansatz）及其拟合结果")

    if population:
        print(f"\n2. 单个个体的结构（以第一个为例）:")
        first_individual = population[0]
        print(f"   类型: {type(first_individual)}")
        print(f"   包含的键: {list(first_individual.keys())}")

        print(f"\n3. 每个键的含义和值:")
        print(f"   - 'ansatz': {first_individual['ansatz']}")
        print(f"     含义: LLM生成的数学表达式（使用params[i]表示参数）")

        print(f"\n   - 'params': {first_individual['params']}")
        print(f"     含义: 拟合得到的参数值（对应ansatz中的params[0], params[1]等）")

        print(f"\n   - 'score': {first_individual['score']}")
        print(f"     含义: 拟合质量分数（负的归一化卡方值，越接近0越好）")

        print(f"\n   - 'Num_params': {first_individual['Num_params']}")
        print(f"     含义: 表达式中的参数个数")

        print(f"\n   - 'response': {first_individual['response'][:100] if first_individual['response'] else None}...")
        print(f"     含义: LLM的原始响应文本（已截断显示）")

        print(f"\n   - 'prompt': {first_individual['prompt'][:100] if first_individual['prompt'] else None}...")
        print(f"     含义: 发送给LLM的提示词（已截断显示）")

        print(f"\n   - 'function_list': {first_individual.get('function_list', None)}")
        print(f"     含义: 父代函数列表（用于遗传算法中的继承）")

        print(f"\n4. 完整的 population 列表预览:")
        for i, ind in enumerate(population[:3]):  # 只显示前3个
            print(f"\n   个体 #{i}:")
            print(f"     ansatz: {ind['ansatz']}")
            print(f"     score: {ind['score']:.6f}")
            print(f"     params: {ind['params']}")

        if len(population) > 3:
            print(f"\n   ... (还有 {len(population) - 3} 个个体)")

    print("\n" + "="*80)
    print("【讲解结束】")
    print("="*80 + "\n")

