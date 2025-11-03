#!/usr/bin/env python3
"""
示例代码：演示 generate_base64_image_with_parents 的作用

这个函数在遗传算法中特别有用，它可以同时可视化：
1. 待拟合的目标数据（蓝色实线）
2. 多个"父代"候选函数（彩色虚线）

这样LLM可以看到多个候选函数的表现，从而生成更好的新函数。
"""

import numpy as np
import matplotlib.pyplot as plt
from llmlex.images import generate_base64_image_with_parents
import base64
from io import BytesIO
from PIL import Image
import os

def main():
    # 获取当前Python文件所在的目录
    script_dir = os.path.dirname(os.path.abspath(__file__))

    print("=" * 60)
    print("演示 generate_base64_image_with_parents 函数")
    print("=" * 60)

    # 1. 生成目标数据：一个复杂的函数
    x = np.linspace(0, 10, 100)
    # 目标函数: y = 2*sin(x) + 0.5*x
    y_target = 2 * np.sin(x) + 0.5 * x
    # 添加一些噪声
    np.random.seed(42)
    y_noisy = y_target + np.random.normal(0, 0.2, len(x))

    print("\n目标数据：")
    print(f"  真实函数: y = 2*sin(x) + 0.5*x")
    print(f"  数据点数: {len(x)}")
    print(f"  x 范围: [{x.min():.2f}, {x.max():.2f}]")

    # 2. 定义几个"父代"候选函数
    # 在 LLM-LEx 的遗传算法中，这些是之前代的优秀候选函数
    # 格式: [函数表达式字符串, 参数列表]
    parent_functions = [
        # 父函数1: 简单的正弦函数（接近但不完美）
        ["params[0] * np.sin(x)", [1.8]],

        # 父函数2: 简单的线性函数（只捕获了趋势）
        ["params[0] * x + params[1]", [0.6, -0.5]],

        # 父函数3: 正弦加常数（接近但缺少线性项）
        ["params[0] * np.sin(x) + params[1]", [2.1, 2.0]],

        # 父函数4: 更复杂的组合（很接近真实函数）
        ["params[0] * np.sin(x) + params[1] * x", [1.9, 0.45]],
    ]

    print("\n父代候选函数:")
    function_descriptions = [
        "1.8 * sin(x) - 只有正弦项",
        "0.6 * x - 0.5 - 只有线性项",
        "2.1 * sin(x) + 2.0 - 正弦加常数",
        "1.9 * sin(x) + 0.45 * x - 接近真实函数"
    ]
    for i, desc in enumerate(function_descriptions):
        print(f"  父函数{i+1}: {desc}")

    # 3. 生成包含父函数的可视化
    print("\n正在生成可视化...")
    base64_image = generate_base64_image_with_parents(
        x=x,
        y=y_noisy,
        parent_functions=parent_functions,
        actually_plot=False,  # 不直接显示，我们将解码后再显示
        title_override=None
    )

    print(f"✓ 生成成功!")
    print(f"  Base64 编码长度: {len(base64_image)} 字符")

    # 4. 将 base64 图像解码并保存/显示
    print("\n正在解码并保存图像...")
    image_data = base64.b64decode(base64_image)
    image = Image.open(BytesIO(image_data))

    # 保存图像到Python文件所在目录
    output_path = os.path.join(script_dir, "example_parents_visualization.png")
    image.save(output_path)
    print(f"✓ 图像已保存到: {output_path}")

    # 5. 可选：使用 matplotlib 显示图像
    print("\n显示图像...")
    plt.figure(figsize=(10, 6))
    plt.imshow(image)
    plt.axis('off')
    plt.title("generate_base64_image_with_parents 生成的图像", fontsize=14, pad=20)
    plt.tight_layout()
    output_path_with_frame = os.path.join(script_dir, "example_parents_with_frame.png")
    plt.savefig(output_path_with_frame, dpi=150, bbox_inches='tight')
    print(f"✓ 带框架的图像已保存到: {output_path_with_frame}")

    # 6. 解释图像内容
    print("\n" + "=" * 60)
    print("图像说明：")
    print("=" * 60)
    print("• 蓝色粗实线：待拟合的目标数据（带噪声）")
    print("• 彩色虚线：多个父代候选函数")
    print("  - 红色虚线 (curve_0): 1.8 * sin(x)")
    print("  - 绿色虚线 (curve_1): 0.6 * x - 0.5")
    print("  - 黄色虚线 (curve_2): 2.1 * sin(x) + 2.0")
    print("  - 紫色虚线 (curve_3): 1.9 * sin(x) + 0.45 * x (最接近)")
    print("\n用途：")
    print("  在遗传算法中，LLM 可以看到多个父函数的表现，")
    print("  从而结合它们的优点生成更好的子代函数。")
    print("=" * 60)

    # 7. 演示在 LLM-LEx 中的使用场景
    print("\n在 LLM-LEx 遗传算法中的使用:")
    print("  1. 第一代：随机生成多个函数，拟合数据")
    print("  2. 选择：保留拟合最好的函数作为'父代'")
    print("  3. 繁殖：将数据和父代函数一起可视化")
    print("  4. LLM 输入：图像 + 提示词")
    print("     '请观察图中的数据(蓝线)和候选函数(虚线)，")
    print("      结合它们的优点，提出一个更好的函数'")
    print("  5. LLM 输出：新的候选函数（子代）")
    print("  6. 重复：迭代优化直到收敛")

if __name__ == "__main__":
    main()
