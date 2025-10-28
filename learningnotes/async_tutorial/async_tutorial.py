"""
Python Async 编程教程 (Python Async Programming Tutorial)
=======================================================

本教程结合 llmlex 仓库中的实际用法，讲解 Python 异步编程的核心概念。
This tutorial explains Python async programming concepts using real examples from the llmlex repository.

作者: Generated for llmlex-pq repository
日期: 2025-10-28
"""

import asyncio
import time
import threading
from functools import wraps
from typing import List, Any


# =============================================================================
# 第一部分：异步编程基础 (Part 1: Async Programming Basics)
# =============================================================================

def introduction():
    """
    什么是异步编程？(What is Async Programming?)
    
    异步编程允许程序在等待某些操作（如 I/O、网络请求）完成时，
    继续执行其他任务，而不是阻塞等待。
    
    Async programming allows a program to continue executing other tasks
    while waiting for operations (like I/O, network requests) to complete,
    rather than blocking and waiting.
    
    关键概念 (Key Concepts):
    - coroutine (协程): 使用 async def 定义的异步函数
    - await: 等待协程完成的关键字
    - event loop (事件循环): 管理和调度协程执行的核心
    - task (任务): 包装的协程，可以并发执行
    """
    print("=" * 70)
    print("异步编程简介 (Introduction to Async Programming)")
    print("=" * 70)


# =============================================================================
# 示例 1: 基本的协程 (Example 1: Basic Coroutine)
# =============================================================================

async def simple_coroutine():
    """
    最简单的协程示例
    A simple coroutine example
    """
    print("协程开始执行 (Coroutine started)")
    await asyncio.sleep(1)  # 模拟 I/O 操作 (Simulate I/O operation)
    print("协程执行完成 (Coroutine completed)")
    return "返回值 (Return value)"


def example_1_basic_coroutine():
    """运行基本协程示例"""
    print("\n" + "=" * 70)
    print("示例 1: 基本协程 (Example 1: Basic Coroutine)")
    print("=" * 70)
    
    # 运行协程的方式 (Ways to run a coroutine)
    result = asyncio.run(simple_coroutine())
    print(f"结果 (Result): {result}")


# =============================================================================
# 示例 2: 并发执行多个协程 (Example 2: Concurrent Coroutines)
# =============================================================================

async def fetch_data(name: str, delay: float) -> str:
    """
    模拟异步获取数据（如 API 调用）
    Simulate async data fetching (like API calls)
    """
    print(f"开始获取 {name} (Starting to fetch {name})")
    await asyncio.sleep(delay)  # 模拟网络延迟 (Simulate network delay)
    print(f"完成获取 {name} (Finished fetching {name})")
    return f"数据来自 {name} (Data from {name})"


async def sequential_execution():
    """顺序执行 - 较慢 (Sequential execution - slower)"""
    print("\n顺序执行 (Sequential Execution):")
    start = time.time()
    
    result1 = await fetch_data("API-1", 2.0)
    result2 = await fetch_data("API-2", 1.5)
    result3 = await fetch_data("API-3", 1.0)
    
    elapsed = time.time() - start
    print(f"总耗时: {elapsed:.2f} 秒 (Total time: {elapsed:.2f} seconds)")
    return [result1, result2, result3]


async def concurrent_execution():
    """并发执行 - 更快 (Concurrent execution - faster)"""
    print("\n并发执行 (Concurrent Execution):")
    start = time.time()
    
    # asyncio.gather 并发执行多个协程 (Run multiple coroutines concurrently)
    results = await asyncio.gather(
        fetch_data("API-1", 2.0),
        fetch_data("API-2", 1.5),
        fetch_data("API-3", 1.0)
    )
    
    elapsed = time.time() - start
    print(f"总耗时: {elapsed:.2f} 秒 (Total time: {elapsed:.2f} seconds)")
    return results


def example_2_concurrent():
    """演示顺序 vs 并发执行"""
    print("\n" + "=" * 70)
    print("示例 2: 并发执行 (Example 2: Concurrent Execution)")
    print("=" * 70)
    
    print("\n注意：顺序执行需要 4.5 秒，并发执行只需要 2 秒！")
    print("Note: Sequential takes 4.5s, concurrent takes only 2s!")
    
    asyncio.run(sequential_execution())
    asyncio.run(concurrent_execution())


# =============================================================================
# 示例 3: 使用 Semaphore 限制并发数 (Example 3: Semaphore for Concurrency Control)
# llmlex 实际案例：限制同时进行的 API 调用数量
# Real llmlex use case: Limiting concurrent API calls
# =============================================================================

async def rate_limited_task(task_id: int, semaphore: asyncio.Semaphore, delay: float):
    """
    使用信号量控制并发的任务
    Task with semaphore-controlled concurrency
    
    这是 llmlex/llmlex.py 中 generate_population() 的简化版本
    This is a simplified version of generate_population() in llmlex/llmlex.py
    
    参考代码位置: llmlex/llmlex.py:743
    Reference: llmlex/llmlex.py:743
    """
    async with semaphore:  # 获取信号量许可 (Acquire semaphore permit)
        print(f"任务 {task_id} 开始执行 (Task {task_id} started)")
        await asyncio.sleep(delay)
        print(f"任务 {task_id} 完成 (Task {task_id} completed)")
        return f"结果 {task_id} (Result {task_id})"


async def run_with_semaphore():
    """
    模拟 llmlex 中的并发控制策略
    Simulate concurrency control strategy from llmlex
    
    在 llmlex 中，我们限制最多同时进行 10 个 API 调用：
    In llmlex, we limit to at most 10 concurrent API calls:
    
    semaphore = asyncio.Semaphore(10)  # 限制并发请求数为 10
    """
    print("\n使用 Semaphore 限制并发 (Using Semaphore to Limit Concurrency):")
    
    # 创建信号量，限制最多 3 个并发任务 (Create semaphore, limit to 3 concurrent tasks)
    semaphore = asyncio.Semaphore(3)
    
    # 创建 10 个任务 (Create 10 tasks)
    tasks = [
        rate_limited_task(i, semaphore, 1.0)
        for i in range(10)
    ]
    
    start = time.time()
    results = await asyncio.gather(*tasks)
    elapsed = time.time() - start
    
    print(f"\n完成 10 个任务，总耗时: {elapsed:.2f} 秒")
    print(f"Completed 10 tasks, total time: {elapsed:.2f} seconds")
    print(f"注意：每批 3 个任务并发执行 (Note: 3 tasks run concurrently per batch)")


def example_3_semaphore():
    """演示信号量控制并发"""
    print("\n" + "=" * 70)
    print("示例 3: Semaphore 并发控制 (Example 3: Semaphore Control)")
    print("=" * 70)
    asyncio.run(run_with_semaphore())


# =============================================================================
# 示例 4: 指数退避重试 (Example 4: Exponential Backoff Retry)
# llmlex 实际案例：API 调用失败时的重试策略
# Real llmlex use case: Retry strategy for failed API calls
# =============================================================================

async def unreliable_api_call(task_id: int, fail_count: int = 2):
    """
    模拟不可靠的 API 调用（前几次会失败）
    Simulate unreliable API call (fails first few times)
    """
    global call_counter
    call_counter = getattr(unreliable_api_call, 'counter', 0)
    
    if call_counter < fail_count:
        unreliable_api_call.counter = call_counter + 1
        raise Exception(f"API 调用失败 (API call failed) - 尝试 {call_counter + 1}")
    
    # 重置计数器 (Reset counter)
    unreliable_api_call.counter = 0
    return f"成功！任务 {task_id} (Success! Task {task_id})"


async def retry_with_backoff(task_id: int, max_attempts: int = 5):
    """
    使用指数退避策略重试
    Retry with exponential backoff strategy
    
    这是 llmlex/llmlex.py 中 create_individual() 的简化版本
    This is a simplified version of create_individual() in llmlex/llmlex.py
    
    参考代码位置: llmlex/llmlex.py:745-773
    Reference: llmlex/llmlex.py:745-773
    """
    for attempt in range(max_attempts):
        try:
            # 计算指数退避延迟 (Calculate exponential backoff delay)
            backoff_time = 0.1 * (2 ** attempt)  # 0.1s, 0.2s, 0.4s, 0.8s, 1.6s
            
            print(f"任务 {task_id} - 尝试 {attempt + 1}/{max_attempts}")
            print(f"Task {task_id} - Attempt {attempt + 1}/{max_attempts}")
            
            result = await unreliable_api_call(task_id, fail_count=2)
            print(f"✓ {result}")
            return result
            
        except Exception as e:
            print(f"✗ 错误 (Error): {e}")
            if attempt < max_attempts - 1:
                print(f"  等待 {backoff_time:.1f} 秒后重试...")
                print(f"  Waiting {backoff_time:.1f}s before retry...")
                await asyncio.sleep(backoff_time)
            else:
                print(f"  所有尝试均失败 (All attempts failed)")
                return None


async def run_retry_demo():
    """运行重试演示"""
    result = await retry_with_backoff(1)
    return result


def example_4_retry():
    """演示指数退避重试"""
    print("\n" + "=" * 70)
    print("示例 4: 指数退避重试 (Example 4: Exponential Backoff Retry)")
    print("=" * 70)
    print("\n这个策略在 llmlex 中用于处理 API 调用失败的情况")
    print("This strategy is used in llmlex to handle failed API calls\n")
    
    asyncio.run(run_retry_demo())


# =============================================================================
# 示例 5: 装饰器限流 (Example 5: Rate Limiting Decorator)
# llmlex 实际案例：限制 API 调用频率
# Real llmlex use case: Rate limiting for API calls
# =============================================================================

class RateLimiter:
    """
    简化版的速率限制器
    Simplified rate limiter
    
    这是 llmlex/llm.py 中 async_rate_limit_api_call 的简化版本
    This is a simplified version of async_rate_limit_api_call in llmlex/llm.py
    
    参考代码位置: llmlex/llm.py:92-154
    Reference: llmlex/llm.py:92-154
    """
    def __init__(self, max_calls_per_minute: int = 10):
        self.max_calls_per_minute = max_calls_per_minute
        self.call_times = []
        self.lock = threading.Lock()
    
    def async_rate_limit(self, func):
        """
        异步速率限制装饰器
        Async rate limiting decorator
        """
        @wraps(func)
        async def wrapper(*args, **kwargs):
            need_to_wait = False
            wait_time = 0
            
            # 使用锁检查速率限制 (Use lock to check rate limit)
            with self.lock:
                current_time = time.time()
                
                # 清理 60 秒前的调用记录 (Clean up calls older than 60 seconds)
                self.call_times = [t for t in self.call_times if current_time - t < 60]
                
                # 检查是否超过速率限制 (Check if exceeding rate limit)
                if len(self.call_times) >= self.max_calls_per_minute:
                    oldest_call = min(self.call_times)
                    wait_time = 60 - (current_time - oldest_call)
                    
                    if wait_time > 0:
                        need_to_wait = True
            
            # 在锁外等待（不阻塞其他任务）(Wait outside lock - don't block other tasks)
            if need_to_wait:
                print(f"⏰ 达到速率限制！等待 {wait_time:.2f} 秒")
                print(f"⏰ Rate limit reached! Waiting {wait_time:.2f} seconds")
                await asyncio.sleep(wait_time)
                
                # 重新获取锁，记录本次调用 (Re-acquire lock, record this call)
                with self.lock:
                    current_time = time.time()
                    self.call_times.append(current_time)
            else:
                # 记录调用时间 (Record call time)
                with self.lock:
                    current_time = time.time()
                    self.call_times.append(current_time)
            
            # 执行实际的 API 调用 (Execute actual API call)
            return await func(*args, **kwargs)
        
        return wrapper


# 创建全局速率限制器实例 (Create global rate limiter instance)
rate_limiter = RateLimiter(max_calls_per_minute=5)  # 限制为每分钟 5 次调用


@rate_limiter.async_rate_limit
async def rate_limited_api_call(call_id: int):
    """
    被速率限制的 API 调用
    Rate-limited API call
    """
    print(f"✓ API 调用 {call_id} 执行中... (API call {call_id} executing...)")
    await asyncio.sleep(0.1)
    return f"结果 {call_id} (Result {call_id})"


async def run_rate_limited_calls():
    """运行速率限制演示"""
    print("\n尝试快速执行 10 次 API 调用（限制为每分钟 5 次）")
    print("Trying to make 10 API calls quickly (limited to 5 per minute)")
    print()
    
    start = time.time()
    
    # 并发执行 10 次调用 (Execute 10 calls concurrently)
    tasks = [rate_limited_api_call(i) for i in range(10)]
    results = await asyncio.gather(*tasks)
    
    elapsed = time.time() - start
    print(f"\n完成 10 次调用，总耗时: {elapsed:.2f} 秒")
    print(f"Completed 10 calls, total time: {elapsed:.2f} seconds")


def example_5_rate_limiting():
    """演示速率限制"""
    print("\n" + "=" * 70)
    print("示例 5: 速率限制装饰器 (Example 5: Rate Limiting Decorator)")
    print("=" * 70)
    asyncio.run(run_rate_limited_calls())


# =============================================================================
# 示例 6: 在不同环境中运行异步代码 (Example 6: Running Async in Different Contexts)
# llmlex 实际案例：处理 Jupyter、测试环境和普通脚本的事件循环
# Real llmlex use case: Handling event loops in Jupyter, tests, and scripts
# =============================================================================

def execute_async_safely(coro):
    """
    安全地在任何环境中执行异步代码
    Safely execute async code in any environment
    
    这是 llmlex/llmlex.py 中 execute_async_in_loop() 的简化版本
    This is a simplified version of execute_async_in_loop() in llmlex/llmlex.py
    
    参考代码位置: llmlex/llmlex.py:52-96
    Reference: llmlex/llmlex.py:52-96
    
    处理三种情况 (Handles three cases):
    1. 没有事件循环 - 创建新的 (No event loop - create new one)
    2. 有事件循环但未运行 - 使用现有的 (Event loop exists but not running - use it)
    3. 事件循环正在运行 - 在其中调度任务 (Event loop is running - schedule task in it)
       （例如在 Jupyter notebook 中）(e.g., in Jupyter notebook)
    """
    current_loop = None
    try:
        current_loop = asyncio.get_event_loop()
    except RuntimeError:
        # 没有事件循环 (No event loop)
        pass
    
    # 情况 1: 有运行中的事件循环 (Case 1: Running event loop)
    if current_loop and current_loop.is_running():
        print("检测到运行中的事件循环（如 Jupyter）")
        print("Detected running event loop (like Jupyter)")
        
        # 创建任务并轮询等待 (Create task and poll for result)
        future = asyncio.ensure_future(coro, loop=current_loop)
        while not future.done():
            time.sleep(0.1)
        return future.result()
    
    # 情况 2 和 3: 没有循环或循环未运行 (Case 2 & 3: No loop or loop not running)
    else:
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        try:
            return new_loop.run_until_complete(coro)
        finally:
            new_loop.close()
            if current_loop:
                asyncio.set_event_loop(current_loop)


async def sample_async_task():
    """示例异步任务"""
    await asyncio.sleep(0.5)
    return "任务完成！(Task completed!)"


def example_6_safe_execution():
    """演示安全的异步执行"""
    print("\n" + "=" * 70)
    print("示例 6: 安全的异步执行 (Example 6: Safe Async Execution)")
    print("=" * 70)
    print("\n这个函数可以在任何环境中运行（包括 Jupyter）")
    print("This function works in any environment (including Jupyter)\n")
    
    result = execute_async_safely(sample_async_task())
    print(f"结果 (Result): {result}")


# =============================================================================
# 示例 7: 真实的 llmlex 使用场景 (Example 7: Real llmlex Use Case)
# 生成初始种群 - 并发生成多个候选解
# Generate initial population - concurrently generate multiple candidates
# =============================================================================

async def simulate_llm_call(individual_id: int, delay: float = 1.0):
    """
    模拟 LLM API 调用生成一个候选解
    Simulate LLM API call to generate a candidate solution
    """
    await asyncio.sleep(delay)  # 模拟网络延迟 (Simulate network delay)
    
    # 模拟返回一个数学表达式 (Simulate returning a mathematical expression)
    expressions = [
        "params[0] * x + params[1]",
        "params[0] * np.sin(params[1] * x)",
        "params[0] * x**2 + params[1] * x + params[2]",
        "params[0] * np.exp(params[1] * x)",
    ]
    import random
    return {
        "id": individual_id,
        "expression": random.choice(expressions),
        "score": random.random()
    }


async def generate_population(population_size: int = 20):
    """
    生成初始种群
    Generate initial population
    
    这是 llmlex/llmlex.py 中实际使用的模式
    This is the actual pattern used in llmlex/llmlex.py
    
    参考代码位置: llmlex/llmlex.py:741-782
    Reference: llmlex/llmlex.py:741-782
    """
    print(f"\n开始生成包含 {population_size} 个个体的种群...")
    print(f"Starting to generate population with {population_size} individuals...")
    
    tasks = []
    semaphore = asyncio.Semaphore(10)  # 限制并发请求为 10 个
    
    async def create_individual(idx: int):
        async with semaphore:
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    # 指数退避 (Exponential backoff)
                    backoff_time = 0.1 * (2 ** attempt)
                    
                    result = await simulate_llm_call(idx, delay=0.5)
                    return result
                    
                except Exception as e:
                    if attempt < max_attempts - 1:
                        print(f"个体 {idx} 失败，重试... (Individual {idx} failed, retrying...)")
                        await asyncio.sleep(backoff_time)
                    else:
                        return None
    
    # 创建所有任务 (Create all tasks)
    for i in range(population_size):
        tasks.append(create_individual(i))
    
    # 并发执行所有任务 (Execute all tasks concurrently)
    start = time.time()
    results = await asyncio.gather(*tasks)
    elapsed = time.time() - start
    
    # 过滤掉失败的结果 (Filter out failed results)
    population = [r for r in results if r is not None]
    
    print(f"\n生成完成！(Generation completed!)")
    print(f"成功生成 {len(population)}/{population_size} 个个体")
    print(f"Successfully generated {len(population)}/{population_size} individuals")
    print(f"总耗时: {elapsed:.2f} 秒 (Total time: {elapsed:.2f} seconds)")
    
    # 显示前几个结果 (Show first few results)
    print("\n前 3 个个体 (First 3 individuals):")
    for ind in population[:3]:
        print(f"  ID {ind['id']}: {ind['expression']}, score={ind['score']:.3f}")
    
    return population


def example_7_real_use_case():
    """演示真实的 llmlex 使用场景"""
    print("\n" + "=" * 70)
    print("示例 7: 真实场景 - 并发生成种群 (Example 7: Real Use Case)")
    print("=" * 70)
    print("\n在 llmlex 中，我们使用异步编程来并发生成多个候选数学表达式")
    print("In llmlex, we use async to concurrently generate multiple candidate expressions")
    
    asyncio.run(generate_population(20))


# =============================================================================
# 示例 8: 异步上下文管理器 (Example 8: Async Context Managers)
# =============================================================================

class AsyncResource:
    """异步资源管理示例"""
    
    def __init__(self, name: str):
        self.name = name
    
    async def __aenter__(self):
        print(f"开始获取资源: {self.name} (Acquiring resource: {self.name})")
        await asyncio.sleep(0.5)  # 模拟异步初始化
        print(f"资源就绪: {self.name} (Resource ready: {self.name})")
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        print(f"释放资源: {self.name} (Releasing resource: {self.name})")
        await asyncio.sleep(0.3)  # 模拟异步清理
        print(f"资源已释放: {self.name} (Resource released: {self.name})")
    
    async def use(self):
        print(f"使用资源: {self.name} (Using resource: {self.name})")
        await asyncio.sleep(0.2)


async def use_async_resource():
    """使用异步上下文管理器"""
    async with AsyncResource("Database Connection") as resource:
        await resource.use()
        # 资源会在退出 with 块时自动释放
        # Resource will be automatically released when exiting the with block


def example_8_async_context():
    """演示异步上下文管理器"""
    print("\n" + "=" * 70)
    print("示例 8: 异步上下文管理器 (Example 8: Async Context Managers)")
    print("=" * 70)
    print()
    asyncio.run(use_async_resource())


# =============================================================================
# 示例 9: 异步生成器 (Example 9: Async Generators)
# =============================================================================

async def async_number_generator(n: int):
    """
    异步生成器示例
    Async generator example
    """
    for i in range(n):
        await asyncio.sleep(0.3)  # 模拟异步操作
        yield i


async def consume_async_generator():
    """消费异步生成器"""
    print("从异步生成器读取数据 (Reading from async generator):")
    async for number in async_number_generator(5):
        print(f"  收到数字 (Received number): {number}")


def example_9_async_generator():
    """演示异步生成器"""
    print("\n" + "=" * 70)
    print("示例 9: 异步生成器 (Example 9: Async Generators)")
    print("=" * 70)
    print()
    asyncio.run(consume_async_generator())


# =============================================================================
# 示例 10: 处理异常 (Example 10: Exception Handling)
# =============================================================================

async def task_that_may_fail(task_id: int, should_fail: bool = False):
    """可能失败的任务"""
    await asyncio.sleep(0.5)
    if should_fail:
        raise ValueError(f"任务 {task_id} 失败了！(Task {task_id} failed!)")
    return f"任务 {task_id} 成功 (Task {task_id} succeeded)"


async def handle_exceptions_individually():
    """单独处理每个任务的异常"""
    print("\n方法 1: 使用 try-except 单独处理 (Method 1: Handle individually)")
    
    tasks = [
        task_that_may_fail(1, False),
        task_that_may_fail(2, True),  # 这个会失败
        task_that_may_fail(3, False),
    ]
    
    results = []
    for task in asyncio.as_completed(tasks):
        try:
            result = await task
            print(f"✓ {result}")
            results.append(result)
        except Exception as e:
            print(f"✗ 错误 (Error): {e}")
            results.append(None)
    
    return results


async def handle_exceptions_with_gather():
    """使用 gather 的 return_exceptions 参数"""
    print("\n方法 2: 使用 gather(return_exceptions=True)")
    print("Method 2: Using gather(return_exceptions=True)")
    
    results = await asyncio.gather(
        task_that_may_fail(1, False),
        task_that_may_fail(2, True),  # 这个会失败
        task_that_may_fail(3, False),
        return_exceptions=True  # 返回异常而不是抛出
    )
    
    for i, result in enumerate(results, 1):
        if isinstance(result, Exception):
            print(f"✗ 任务 {i} 失败: {result} (Task {i} failed: {result})")
        else:
            print(f"✓ 任务 {i}: {result}")
    
    return results


def example_10_exception_handling():
    """演示异常处理"""
    print("\n" + "=" * 70)
    print("示例 10: 异常处理 (Example 10: Exception Handling)")
    print("=" * 70)
    
    asyncio.run(handle_exceptions_individually())
    asyncio.run(handle_exceptions_with_gather())


# =============================================================================
# 主程序 (Main Program)
# =============================================================================

def print_summary():
    """打印总结"""
    print("\n" + "=" * 70)
    print("异步编程核心要点总结 (Key Takeaways)")
    print("=" * 70)
    print("""
1. 使用 async def 定义协程 (Define coroutines with async def)
2. 使用 await 等待协程完成 (Use await to wait for coroutines)
3. asyncio.gather() 并发执行多个协程 (Run multiple coroutines concurrently)
4. Semaphore 控制并发数量 (Control concurrency with Semaphore)
5. 指数退避提高重试成功率 (Exponential backoff improves retry success)
6. 装饰器实现速率限制 (Rate limiting with decorators)
7. 在锁外执行 await 避免阻塞 (Execute await outside locks to avoid blocking)
8. 使用 return_exceptions=True 处理部分失败 (Handle partial failures)

在 llmlex 中的应用 (Applications in llmlex):
- 并发生成多个候选表达式 (Concurrent candidate generation)
- API 速率限制 (API rate limiting)
- 自动重试失败的调用 (Automatic retry for failed calls)
- 在不同环境（Jupyter、脚本、测试）中安全运行
  (Safe execution in different environments)
""")


def main():
    """运行所有示例"""
    print("""
╔════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║         Python Async 编程教程 (Python Async Tutorial)             ║
║              基于 llmlex 仓库实际用法 (Based on llmlex)           ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
""")
    
    introduction()
    
    # 运行所有示例 (Run all examples)
    example_1_basic_coroutine()
    example_2_concurrent()
    example_3_semaphore()
    example_4_retry()
    example_5_rate_limiting()
    example_6_safe_execution()
    example_7_real_use_case()
    example_8_async_context()
    example_9_async_generator()
    example_10_exception_handling()
    
    print_summary()
    
    print("\n" + "=" * 70)
    print("教程完成！(Tutorial completed!)")
    print("=" * 70)
    print("""
进一步学习资源 (Further Learning Resources):
- Python 官方文档: https://docs.python.org/3/library/asyncio.html
- Real Python: https://realpython.com/async-io-python/
- llmlex 源码: llmlex/llmlex.py, llmlex/llm.py

在 llmlex 中查看实际应用 (See real applications in llmlex):
- llmlex/llmlex.py:741-782 (generate_population)
- llmlex/llmlex.py:505-620 (async_single_call)
- llmlex/llm.py:92-154 (async_rate_limit_api_call)
- llmlex/llm.py:738-837 (async_call_model)
""")


if __name__ == "__main__":
    main()

