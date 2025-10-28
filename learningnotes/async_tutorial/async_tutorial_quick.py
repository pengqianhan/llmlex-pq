"""
Python Async 快速入门 (Quick Start Guide)
=========================================

本文件提供了 async_tutorial.py 的快速示例。
This file provides quick examples from async_tutorial.py.

运行完整教程: python async_tutorial.py
Run full tutorial: python async_tutorial.py
"""

import asyncio
import time


# 示例 1: 基础异步函数 (Example 1: Basic Async Function)
async def greet(name: str, delay: float):
    """异步问候函数"""
    print(f"开始问候 {name}... (Starting to greet {name}...)")
    await asyncio.sleep(delay)  # 模拟 I/O 操作
    print(f"你好 {name}！(Hello {name}!)")
    return f"问候 {name} 完成 (Greeted {name})"


# 示例 2: 并发执行 (Example 2: Concurrent Execution)
async def demo_concurrent():
    """演示并发执行的优势"""
    print("\n" + "=" * 60)
    print("并发 vs 顺序执行对比 (Concurrent vs Sequential)")
    print("=" * 60)
    
    # 顺序执行 (Sequential)
    print("\n顺序执行 (Sequential):")
    start = time.time()
    await greet("Alice", 1.0)
    await greet("Bob", 1.0)
    await greet("Carol", 1.0)
    sequential_time = time.time() - start
    print(f"顺序耗时: {sequential_time:.2f}秒 (Sequential time: {sequential_time:.2f}s)")
    
    # 并发执行 (Concurrent)
    print("\n并发执行 (Concurrent):")
    start = time.time()
    await asyncio.gather(
        greet("Alice", 1.0),
        greet("Bob", 1.0),
        greet("Carol", 1.0),
    )
    concurrent_time = time.time() - start
    print(f"并发耗时: {concurrent_time:.2f}秒 (Concurrent time: {concurrent_time:.2f}s)")
    
    speedup = sequential_time / concurrent_time
    print(f"\n⚡ 速度提升: {speedup:.1f}x 倍！(Speedup: {speedup:.1f}x!)")


# 示例 3: 限制并发数 (Example 3: Semaphore)
async def demo_semaphore():
    """演示如何限制并发数量"""
    print("\n" + "=" * 60)
    print("使用 Semaphore 限制并发 (Using Semaphore)")
    print("=" * 60)
    print("同时最多 2 个任务运行 (Max 2 concurrent tasks)\n")
    
    semaphore = asyncio.Semaphore(2)  # 限制为 2 个并发
    
    async def limited_task(task_id: int):
        async with semaphore:
            print(f"  任务 {task_id} 开始 (Task {task_id} started)")
            await asyncio.sleep(1.0)
            print(f"  任务 {task_id} 完成 (Task {task_id} completed)")
    
    tasks = [limited_task(i) for i in range(6)]
    await asyncio.gather(*tasks)


# 示例 4: 真实场景 - 模拟 API 调用 (Example 4: Real Use Case - API Calls)
async def demo_api_calls():
    """模拟真实的 API 调用场景（如 llmlex 中的用法）"""
    print("\n" + "=" * 60)
    print("真实场景：并发 API 调用 (Real Use Case: Concurrent API Calls)")
    print("=" * 60)
    
    async def mock_api_call(api_id: int):
        """模拟 API 调用"""
        await asyncio.sleep(0.5)  # 模拟网络延迟
        return {
            "id": api_id,
            "data": f"来自 API-{api_id} 的数据 (Data from API-{api_id})",
            "status": "success"
        }
    
    print("\n并发调用 10 个 API...")
    print("Making 10 concurrent API calls...")
    
    start = time.time()
    results = await asyncio.gather(*[mock_api_call(i) for i in range(10)])
    elapsed = time.time() - start
    
    print(f"\n✓ 完成！耗时: {elapsed:.2f}秒 (Completed in {elapsed:.2f}s)")
    print(f"✓ 成功获取 {len(results)} 个结果 (Got {len(results)} results)")
    print(f"✓ 前 3 个结果 (First 3 results):")
    for r in results[:3]:
        print(f"   - {r['data']}")


# 主函数 (Main Function)
async def main():
    """运行所有示例"""
    print("""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║      Python Async 快速入门 (Quick Start Guide)          ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
""")
    
    await demo_concurrent()
    await demo_semaphore()
    await demo_api_calls()
    
    print("\n" + "=" * 60)
    print("快速入门完成！(Quick start completed!)")
    print("=" * 60)
    print("""
运行完整教程查看更多高级示例：
Run full tutorial for more advanced examples:

    python async_tutorial.py

教程内容包括：(Tutorial includes:)
- 指数退避重试策略 (Exponential backoff retry)
- 速率限制装饰器 (Rate limiting decorators)
- 异步上下文管理器 (Async context managers)
- 异步生成器 (Async generators)
- 异常处理最佳实践 (Exception handling best practices)
- llmlex 中的实际应用案例 (Real llmlex use cases)
""")


if __name__ == "__main__":
    asyncio.run(main())

