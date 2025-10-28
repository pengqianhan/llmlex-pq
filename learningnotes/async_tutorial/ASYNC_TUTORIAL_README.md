# Python Async 编程教程 (Python Async Programming Tutorial)

本目录包含两个 Python 异步编程教程文件，专门为 llmlex 项目设计，展示了项目中实际使用的异步编程模式。

This directory contains two Python async programming tutorial files designed for the llmlex project, demonstrating async patterns actually used in the codebase.

## 📚 教程文件 (Tutorial Files)

### 1. `async_tutorial_quick.py` - 快速入门 (Quick Start)

**适合对象**: 完全不了解 async 的初学者  
**Suitable for**: Complete beginners to async

**运行时间**: ~5 秒  
**Runtime**: ~5 seconds

```bash
python async_tutorial_quick.py
```

**内容** (Content):
- ✅ 基础异步函数用法 (Basic async function usage)
- ✅ 并发 vs 顺序执行对比 (Concurrent vs sequential comparison)
- ✅ Semaphore 并发控制 (Semaphore concurrency control)
- ✅ 模拟真实 API 调用场景 (Simulated real API call scenarios)

### 2. `async_tutorial.py` - 完整教程 (Full Tutorial)

**适合对象**: 想深入了解异步编程和 llmlex 实现细节的开发者  
**Suitable for**: Developers wanting deep understanding of async and llmlex implementation

**运行时间**: ~70 秒 (包含速率限制演示)  
**Runtime**: ~70 seconds (includes rate limiting demo)

```bash
python async_tutorial.py
```

**内容** (Content):
- ✅ 所有快速入门的内容 (All quick start content)
- ✅ 指数退避重试策略 (Exponential backoff retry)
- ✅ 装饰器实现速率限制 (Rate limiting with decorators)
- ✅ 在不同环境中安全执行异步代码 (Safe async execution in different environments)
- ✅ 真实的 llmlex 使用场景分析 (Real llmlex use case analysis)
- ✅ 异步上下文管理器 (Async context managers)
- ✅ 异步生成器 (Async generators)
- ✅ 异常处理最佳实践 (Exception handling best practices)

## 🎯 学习路径 (Learning Path)

### 初学者路径 (Beginner Path)
1. 运行 `async_tutorial_quick.py` 快速了解基础概念
2. 阅读输出，理解并发执行的优势
3. 查看源代码，理解 `async`/`await` 语法
4. 运行 `async_tutorial.py` 学习高级概念

### 进阶路径 (Advanced Path)
1. 直接运行 `async_tutorial.py` 查看完整示例
2. 对照 llmlex 源码学习实际应用：
   - `llmlex/llmlex.py:741-782` - 并发生成种群
   - `llmlex/llmlex.py:505-620` - 异步单次调用
   - `llmlex/llm.py:92-154` - 异步速率限制
   - `llmlex/llm.py:738-837` - 异步模型调用

## 📖 核心概念映射 (Core Concepts Mapping)

| 概念 (Concept) | 快速教程 (Quick) | 完整教程 (Full) | llmlex 实际应用 (llmlex Usage) |
|---------------|-----------------|----------------|------------------------------|
| 基础协程 (Basic coroutines) | ✅ | ✅ | 所有 async def 函数 |
| 并发执行 (Concurrent execution) | ✅ | ✅ | `asyncio.gather()` 生成种群 |
| Semaphore 限流 | ✅ | ✅ | 限制并发 API 调用数 |
| 指数退避重试 (Exponential backoff) | ❌ | ✅ | API 失败重试策略 |
| 速率限制装饰器 (Rate limiting) | ❌ | ✅ | `@async_rate_limit_api_call` |
| 跨环境执行 (Cross-env execution) | ❌ | ✅ | `execute_async_in_loop()` |
| 异常处理 (Exception handling) | ❌ | ✅ | 处理 API 调用失败 |

## 🔍 代码示例对照表 (Code Reference Table)

### 示例 1: 并发生成种群 (Concurrent Population Generation)

**教程位置**: `async_tutorial.py` 示例 7  
**Tutorial Location**: `async_tutorial.py` Example 7

**llmlex 源码**: `llmlex/llmlex.py:741-782`  
**llmlex Source**: `llmlex/llmlex.py:741-782`

```python
# 教程简化版 (Tutorial simplified version)
async def generate_population(population_size: int = 20):
    semaphore = asyncio.Semaphore(10)
    
    async def create_individual(idx: int):
        async with semaphore:
            result = await simulate_llm_call(idx)
            return result
    
    tasks = [create_individual(i) for i in range(population_size)]
    results = await asyncio.gather(*tasks)
    return [r for r in results if r is not None]
```

### 示例 2: 速率限制 (Rate Limiting)

**教程位置**: `async_tutorial.py` 示例 5  
**Tutorial Location**: `async_tutorial.py` Example 5

**llmlex 源码**: `llmlex/llm.py:92-154`  
**llmlex Source**: `llmlex/llm.py:92-154`

```python
# 教程简化版 (Tutorial simplified version)
def async_rate_limit(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # 检查速率限制 (Check rate limit)
        if need_to_wait:
            await asyncio.sleep(wait_time)
        return await func(*args, **kwargs)
    return wrapper
```

### 示例 3: 指数退避重试 (Exponential Backoff Retry)

**教程位置**: `async_tutorial.py` 示例 4  
**Tutorial Location**: `async_tutorial.py` Example 4

**llmlex 源码**: `llmlex/llmlex.py:749-773`  
**llmlex Source**: `llmlex/llmlex.py:749-773`

```python
# 教程简化版 (Tutorial simplified version)
async def retry_with_backoff(max_attempts: int = 5):
    for attempt in range(max_attempts):
        try:
            backoff_time = 0.1 * (2 ** attempt)
            result = await api_call()
            return result
        except Exception as e:
            if attempt < max_attempts - 1:
                await asyncio.sleep(backoff_time)
```

## 💡 实用技巧 (Practical Tips)

### 1. 何时使用异步? (When to use async?)

✅ **适合使用** (Good use cases):
- 大量 I/O 操作（网络请求、文件读写）
- 需要并发处理多个任务
- API 调用密集的应用
- llmlex 场景：并发生成多个候选表达式

❌ **不适合使用** (Not suitable):
- CPU 密集型计算（使用多进程代替）
- 简单的顺序任务
- 单个快速操作

### 2. 常见错误 (Common Mistakes)

❌ **错误**: 忘记使用 `await`
```python
# 错误 (Wrong)
result = async_function()  # 返回 coroutine 对象，不是结果

# 正确 (Correct)
result = await async_function()
```

❌ **错误**: 在同步函数中调用异步函数
```python
# 错误 (Wrong)
def sync_function():
    result = await async_function()  # SyntaxError

# 正确 (Correct)
async def async_function_wrapper():
    result = await async_function()
    return result
```

❌ **错误**: 在锁内使用 `await`（阻塞其他协程）
```python
# 错误 (Wrong) - 在锁内等待会阻塞其他任务
with lock:
    result = await slow_operation()

# 正确 (Correct) - 在锁外执行异步操作
with lock:
    # 只做必要的同步检查
    need_to_wait = check_condition()

if need_to_wait:
    await asyncio.sleep(delay)  # 锁外等待
```

### 3. 调试技巧 (Debugging Tips)

```python
# 启用 asyncio 调试模式 (Enable asyncio debug mode)
import asyncio
asyncio.run(main(), debug=True)

# 或在代码中 (Or in code)
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🚀 性能优化建议 (Performance Optimization)

### 1. 使用 Semaphore 控制并发
```python
# 避免同时发起过多请求导致服务器过载
semaphore = asyncio.Semaphore(10)  # 最多 10 个并发
```

### 2. 使用超时控制
```python
# 避免单个请求卡住整个流程
try:
    result = await asyncio.wait_for(slow_operation(), timeout=30.0)
except asyncio.TimeoutError:
    print("操作超时")
```

### 3. 批量处理结果
```python
# 使用 gather 而不是逐个 await
results = await asyncio.gather(*tasks)  # 并发执行所有任务
```

## 📚 延伸阅读 (Further Reading)

### 官方文档 (Official Documentation)
- [Python asyncio 文档](https://docs.python.org/3/library/asyncio.html)
- [PEP 492 - Coroutines with async and await syntax](https://www.python.org/dev/peps/pep-0492/)

### 推荐教程 (Recommended Tutorials)
- [Real Python - Async IO in Python](https://realpython.com/async-io-python/)
- [FastAPI - Concurrency and async/await](https://fastapi.tiangolo.com/async/)

### llmlex 相关源码 (Related llmlex Source Code)
- `llmlex/llmlex.py` - 主要的异步逻辑
- `llmlex/llm.py` - API 调用和速率限制
- `llmlex/fit.py` - 拟合相关函数

## ❓ 常见问题 (FAQ)

### Q1: 为什么 llmlex 使用异步编程？
**A**: llmlex 需要并发调用多个 LLM API 来生成候选表达式。使用异步可以将生成时间从顺序执行的 N×T 秒减少到约 T 秒（N 为候选数量，T 为单次调用时间）。

### Q2: 速率限制演示为什么需要 60 秒？
**A**: 示例 5 设置了每分钟最多 5 次调用的限制，当尝试执行 10 次调用时，后 5 次必须等待 60 秒窗口期过去。这模拟了真实 API 的速率限制。

### Q3: 如何在 Jupyter Notebook 中运行这些示例？
**A**: 
```python
# 在 Jupyter 中可以直接使用 await
await demo_concurrent()

# 或者使用完整教程中的 execute_async_safely()
from async_tutorial import execute_async_safely
result = execute_async_safely(demo_concurrent())
```

### Q4: 异步代码如何调试？
**A**: 
1. 使用 `print()` 或 `logger.debug()` 追踪执行流程
2. 启用 asyncio 调试模式：`asyncio.run(main(), debug=True)`
3. 使用 `asyncio` 库的内置工具：`asyncio.create_task()` 可以设置 name 参数便于识别

### Q5: Semaphore 的数量应该设置为多少？
**A**: 
- API 调用：根据服务商的速率限制，通常 5-20
- llmlex 默认：10 个并发请求
- 本地 I/O：可以更高，50-100
- 权衡：更多并发 = 更快完成，但也更容易触发速率限制

## 🎓 学习检查清单 (Learning Checklist)

完成以下检查项，确保你已经掌握了异步编程的核心概念：

- [ ] 理解 `async def` 和 `await` 的基本语法
- [ ] 能够解释并发执行如何提升性能
- [ ] 知道如何使用 `asyncio.gather()` 并发执行多个任务
- [ ] 理解 Semaphore 的作用和使用场景
- [ ] 能够实现指数退避重试策略
- [ ] 理解速率限制的重要性和实现方法
- [ ] 知道如何处理异步代码中的异常
- [ ] 能够在不同环境（脚本、Jupyter）中运行异步代码
- [ ] 理解为什么不应该在锁内使用 `await`
- [ ] 能够阅读和理解 llmlex 中的异步代码

## 📝 练习建议 (Practice Suggestions)

### 初级练习 (Beginner)
1. 修改 `async_tutorial_quick.py`，改变并发数量，观察时间变化
2. 编写一个异步函数，模拟下载 5 个文件
3. 使用 Semaphore 限制同时下载的文件数为 2

### 中级练习 (Intermediate)
1. 实现一个带重试的异步 HTTP 客户端
2. 为你的异步函数添加超时控制
3. 实现一个简单的异步任务队列

### 高级练习 (Advanced)
1. 阅读 llmlex 源码，理解完整的异步流程
2. 为 llmlex 添加自定义的速率限制策略
3. 实现一个异步的批处理系统，支持优先级队列

---

**Happy Async Programming! 祝学习愉快！** 🚀

如有问题，请参考 llmlex 源码或提交 issue。  
For questions, refer to llmlex source code or submit an issue.

