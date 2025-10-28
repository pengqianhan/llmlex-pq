"""
如何在你的代码中使用 async 模式
How to use async patterns in your code

这个示例展示了如何将教程中学到的异步模式应用到实际项目中。
This example shows how to apply async patterns learned from the tutorial to real projects.
"""

import asyncio
import time
from typing import List, Dict, Any


# 场景 1: 并发处理数据 (Scenario 1: Concurrent Data Processing)
# ============================================================

async def process_item(item_id: int, processing_time: float = 0.5) -> Dict[str, Any]:
    """
    模拟处理单个数据项（如分析数据、调用 API 等）
    Simulate processing a single data item (e.g., analyzing data, calling API)
    """
    await asyncio.sleep(processing_time)
    return {
        "id": item_id,
        "result": f"Processed item {item_id}",
        "timestamp": time.time()
    }


async def process_batch_concurrent(items: List[int]) -> List[Dict[str, Any]]:
    """
    并发处理一批数据项
    Process a batch of items concurrently
    
    类似 llmlex 中的 generate_population 模式
    Similar to generate_population pattern in llmlex
    """
    print(f"\n并发处理 {len(items)} 个数据项...")
    start = time.time()
    
    # 创建所有任务 (Create all tasks)
    tasks = [process_item(item_id) for item_id in items]
    
    # 并发执行 (Execute concurrently)
    results = await asyncio.gather(*tasks)
    
    elapsed = time.time() - start
    print(f"✓ 完成！耗时 {elapsed:.2f} 秒 ({len(items)/elapsed:.1f} 项/秒)")
    
    return results


# 场景 2: 带限流的并发处理 (Scenario 2: Rate-Limited Concurrent Processing)
# ============================================================

async def rate_limited_api_call(
    item_id: int,
    semaphore: asyncio.Semaphore,
    delay: float = 0.3
) -> Dict[str, Any]:
    """
    带速率限制的 API 调用
    Rate-limited API call
    
    使用 Semaphore 控制并发数，避免超过 API 限制
    Use Semaphore to control concurrency, avoiding API limits
    """
    async with semaphore:
        print(f"  → 调用 API: 项目 {item_id}")
        await asyncio.sleep(delay)
        print(f"  ✓ 完成: 项目 {item_id}")
        return {"id": item_id, "status": "success"}


async def process_with_rate_limit(
    items: List[int],
    max_concurrent: int = 5
) -> List[Dict[str, Any]]:
    """
    带速率限制的批量处理
    Batch processing with rate limiting
    
    类似 llmlex 中的并发控制模式
    Similar to concurrency control pattern in llmlex
    """
    print(f"\n带速率限制的处理（最多 {max_concurrent} 个并发）...")
    start = time.time()
    
    # 创建信号量 (Create semaphore)
    semaphore = asyncio.Semaphore(max_concurrent)
    
    # 创建任务 (Create tasks)
    tasks = [
        rate_limited_api_call(item_id, semaphore)
        for item_id in items
    ]
    
    # 并发执行 (Execute concurrently)
    results = await asyncio.gather(*tasks)
    
    elapsed = time.time() - start
    print(f"✓ 完成！耗时 {elapsed:.2f} 秒")
    
    return results


# 场景 3: 带重试的处理 (Scenario 3: Processing with Retry)
# ============================================================

class TemporaryError(Exception):
    """模拟临时错误"""
    pass


async def unreliable_operation(item_id: int, fail_probability: float = 0.3):
    """
    模拟可能失败的操作
    Simulate an operation that might fail
    """
    import random
    await asyncio.sleep(0.2)
    
    if random.random() < fail_probability:
        raise TemporaryError(f"临时错误: 项目 {item_id}")
    
    return {"id": item_id, "status": "success"}


async def process_with_retry(
    item_id: int,
    max_retries: int = 3
) -> Dict[str, Any]:
    """
    带指数退避重试的处理
    Processing with exponential backoff retry
    
    类似 llmlex 中的 retry_with_backoff 模式
    Similar to retry_with_backoff pattern in llmlex
    """
    for attempt in range(max_retries):
        try:
            # 计算退避时间 (Calculate backoff time)
            backoff_time = 0.1 * (2 ** attempt)
            
            result = await unreliable_operation(item_id)
            
            if attempt > 0:
                print(f"  ✓ 项目 {item_id} 重试成功（第 {attempt + 1} 次尝试）")
            
            return result
            
        except TemporaryError as e:
            if attempt < max_retries - 1:
                print(f"  ⚠ 项目 {item_id} 失败，{backoff_time:.1f}秒后重试...")
                await asyncio.sleep(backoff_time)
            else:
                print(f"  ✗ 项目 {item_id} 最终失败")
                return {"id": item_id, "status": "failed", "error": str(e)}


async def batch_process_with_retry(items: List[int]) -> List[Dict[str, Any]]:
    """
    批量处理，每个项目都带重试
    Batch processing with retry for each item
    """
    print(f"\n带重试的批量处理...")
    
    tasks = [process_with_retry(item_id) for item_id in items]
    results = await asyncio.gather(*tasks)
    
    successful = sum(1 for r in results if r.get("status") == "success")
    print(f"✓ 完成！成功: {successful}/{len(items)}")
    
    return results


# 场景 4: 组合使用多种模式 (Scenario 4: Combining Multiple Patterns)
# ============================================================

async def advanced_batch_processing(
    items: List[int],
    max_concurrent: int = 5,
    max_retries: int = 3
) -> List[Dict[str, Any]]:
    """
    高级批量处理：结合速率限制和重试
    Advanced batch processing: combining rate limiting and retry
    
    这是 llmlex 实际使用的模式
    This is the pattern actually used in llmlex
    """
    print(f"\n高级批量处理（{len(items)} 个项目）...")
    print(f"  - 最多并发: {max_concurrent}")
    print(f"  - 最多重试: {max_retries}")
    
    start = time.time()
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def process_with_limits(item_id: int):
        async with semaphore:
            return await process_with_retry(item_id, max_retries)
    
    tasks = [process_with_limits(item_id) for item_id in items]
    results = await asyncio.gather(*tasks)
    
    elapsed = time.time() - start
    successful = sum(1 for r in results if r.get("status") == "success")
    
    print(f"\n✓ 批处理完成！")
    print(f"  - 总耗时: {elapsed:.2f} 秒")
    print(f"  - 成功: {successful}/{len(items)}")
    print(f"  - 吞吐量: {len(items)/elapsed:.1f} 项/秒")
    
    return results


# 主函数 (Main Function)
# ============================================================

async def main():
    """运行所有示例"""
    print("=" * 60)
    print("Async 使用示例 (Async Usage Examples)")
    print("=" * 60)
    
    # 示例 1: 简单并发处理
    print("\n【示例 1】简单并发处理")
    await process_batch_concurrent(list(range(10)))
    
    # 示例 2: 带速率限制的处理
    print("\n【示例 2】带速率限制的处理")
    await process_with_rate_limit(list(range(10)), max_concurrent=3)
    
    # 示例 3: 带重试的处理
    print("\n【示例 3】带重试的处理")
    await batch_process_with_retry(list(range(8)))
    
    # 示例 4: 高级批量处理
    print("\n【示例 4】高级批量处理（组合模式）")
    await advanced_batch_processing(
        list(range(15)),
        max_concurrent=5,
        max_retries=3
    )
    
    print("\n" + "=" * 60)
    print("所有示例完成！")
    print("=" * 60)
    
    print("""
💡 关键要点 (Key Takeaways):

1. 使用 asyncio.gather() 并发执行多个任务
   Use asyncio.gather() to execute multiple tasks concurrently

2. 使用 Semaphore 控制并发数，避免过载
   Use Semaphore to control concurrency and avoid overload

3. 使用指数退避重试提高成功率
   Use exponential backoff retry to improve success rate

4. 组合使用多种模式处理复杂场景
   Combine multiple patterns for complex scenarios

5. 参考 llmlex 源码学习更多实际应用
   Refer to llmlex source code for more real-world applications

📚 相关教程 (Related Tutorials):
   - python async_tutorial_quick.py  (快速入门)
   - python async_tutorial.py         (完整教程)
   - cat ASYNC_TUTORIAL_README.md    (详细文档)
""")


if __name__ == "__main__":
    asyncio.run(main())

