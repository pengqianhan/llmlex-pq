#!/usr/bin/env python3
"""
演示如何用 lambda 形式生成初始 JSON (类似 get_prompt 的用法)

这个脚本展示了:
1. 使用简洁的 lambda 表达式定义 mode 方程
2. 自动生成符合 HybridAutomata.from_json() 的 JSON
3. 对比手动编写 JSON vs 自动生成
"""

import sys
import os
import json
import importlib.util

# 导入 llm 模块
spec = importlib.util.spec_from_file_location(
    "llm_module", 
    os.path.join(os.path.dirname(__file__), "llmlex", "llm.py")
)
llm_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(llm_module)

def example1_simple_oscillator():
    """
    示例 1: 简单的阻尼振荡器
    x1' = x2
    x2' = -x1 - 0.1*x2
    """
    print("=" * 70)
    print("示例 1: 简单阻尼振荡器 (单模式)")
    print("=" * 70)
    
    # 使用 lambda 风格定义
    json_obj = llm_module.generate_initial_ha_json(
        var_list=["x1", "x2"],
        mode_eqs={
            1: ["x2[0]", "-x1[0] - 0.1*x2[0]"]  # Mode 1
        }
    )
    
    print("\n生成的 JSON:")
    print(json.dumps(json_obj, indent=2, ensure_ascii=False))
    
    print("\n✓ 只需简单的 lambda 表达式")
    print("✓ 自动生成符合标准的 JSON 格式")
    print("✓ 类似 get_prompt 的使用方式\n")


def example2_two_mode_system():
    """
    示例 2: 两模式系统
    Mode 1: 线性
    Mode 2: 带立方非线性项
    """
    print("\n" + "=" * 70)
    print("示例 2: 两模式系统 (线性 <-> 非线性)")
    print("=" * 70)
    
    json_obj = llm_module.generate_initial_ha_json(
        var_list=["x1", "x2"],
        mode_eqs={
            1: ["x2[0]", "-x1[0] - 0.1*x2[0]"],              # 线性模式
            2: ["x2[0]", "-x1[0]**3 - 0.5*x2[0]"]           # 立方非线性
        },
        transitions=[
            {
                "direction": "1 -> 2",
                "condition": "abs(x1[0]) >= 1.0",
                "reset": {"x1": [], "x2": []}
            },
            {
                "direction": "2 -> 1",
                "condition": "abs(x1[0]) <= 0.5",
                "reset": {"x1": [], "x2": []}
            }
        ]
    )
    
    print("\n生成的 JSON:")
    print(json.dumps(json_obj, indent=2, ensure_ascii=False))
    
    print("\n✓ 多模式支持")
    print("✓ 包含转移条件 (transitions)")
    print("✓ 自动格式化方程\n")


def example3_duffing_with_input():
    """
    示例 3: Duffing 振荡器 (带输入)
    x'' + δx' + αx + βx³ = u
    """
    print("\n" + "=" * 70)
    print("示例 3: Duffing 振荡器 (带输入 u)")
    print("=" * 70)
    
    json_obj = llm_module.generate_initial_ha_json(
        var_list=["x"],
        mode_eqs={
            1: ["u - 0.5*x[1] + x[0] - 1.5*x[0]**3"],       # Mode 1
            2: ["u - 0.2*x[1] + x[0] - 0.5*x[0]**3"]        # Mode 2
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
    
    print("\n生成的 JSON:")
    print(json.dumps(json_obj, indent=2, ensure_ascii=False))
    
    print("\n✓ 支持输入变量 (input_vars)")
    print("✓ 高阶导数表示 (x[2] = ...)")
    print("✓ 复杂的非线性项\n")


def example4_comparison():
    """
    示例 4: 对比手动 JSON vs 自动生成
    """
    print("\n" + "=" * 70)
    print("示例 4: 对比手动编写 vs 自动生成")
    print("=" * 70)
    
    print("\n【传统方式】手动编写 JSON:")
    print("-" * 70)
    manual_json = """
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
"""
    print(manual_json)
    
    print("\n【新方式】Lambda 表达式自动生成:")
    print("-" * 70)
    print("""
from llmlex.llm import generate_initial_ha_json

json_obj = generate_initial_ha_json(
    var_list=["x1", "x2"],
    mode_eqs={
        1: ["x2[0]", "-x1[0] - 0.1*x2[0]"]
    }
)
""")
    
    json_obj = llm_module.generate_initial_ha_json(
        var_list=["x1", "x2"],
        mode_eqs={
            1: ["x2[0]", "-x1[0] - 0.1*x2[0]"]
        }
    )
    
    print("\n生成结果:")
    print(json.dumps(json_obj, indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 70)
    print("优势:")
    print("  ✓ 更简洁 - 类似 get_prompt 的用法")
    print("  ✓ 更直观 - 直接用数学表达式")
    print("  ✓ 更少错误 - 自动处理格式")
    print("  ✓ 更灵活 - 可选参数支持复杂场景")
    print("=" * 70 + "\n")


def example5_save_to_file():
    """
    示例 5: 保存为 JSON 文件
    """
    print("\n" + "=" * 70)
    print("示例 5: 保存为 JSON 文件")
    print("=" * 70)
    
    json_obj = llm_module.generate_initial_ha_json(
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
    
    # 保存到文件
    output_path = os.path.join(os.path.dirname(__file__), "generated_ha.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(json_obj, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ JSON 已保存到: {output_path}")
    print("\n文件内容:")
    print(json.dumps(json_obj, indent=2, ensure_ascii=False))
    
    print("\n可以这样使用:")
    print("  from llmlex.hybrid_automata import HybridAutomata")
    print("  ha = HybridAutomata.from_json(json_obj['automaton'])")


if __name__ == "__main__":
    # example1_simple_oscillator()
    # example2_two_mode_system()
    example3_duffing_with_input()
    example4_comparison()
    example5_save_to_file()
    
    print("\n" + "=" * 70)
    print("总结")
    print("=" * 70)
    print("""
现在可以用简洁的 lambda 形式来定义混合自动机的初始 JSON！

基本用法:
---------
from llmlex.llm import generate_initial_ha_json

json_obj = generate_initial_ha_json(
    var_list=["x1", "x2"],           # 状态变量
    mode_eqs={                        # 模式方程 (lambda 风格)
        1: ["x2[0]", "-x1[0]"],
        2: ["x2[0]", "-x1[0]**3"]
    },
    transitions=[...],                # 可选: 转移条件
    input_vars=["u"]                  # 可选: 输入变量
)

这与 get_prompt 的理念一致:
- get_prompt: 用 lambda 定义符号回归的起始点
- generate_initial_ha_json: 用 lambda 定义混合自动机的起始点

都是为了让定义更简洁、更直观！
""")
    print("=" * 70)

