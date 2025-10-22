# utils/log_utils.py
import logging
import time
from functools import wraps

# 全局 logger
logger = logging.getLogger("ai_assistant")

def log_step(message: str):
    """
    装饰器：记录某个操作步骤的开始
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(f"🔄 开始执行: {message}")
            return func(*args, **kwargs)
        return wrapper
    return decorator

def log_time(func):
    """
    装饰器：记录函数执行耗时，并捕获异常堆栈
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        func_name = func.__name__
        logger.debug(f"▶️ 进入函数: {func_name}, 参数: args={args}, kwargs={kwargs}")

        try:
            result = func(*args, **kwargs)
            duration = time.time() - start
            logger.debug(f"✅ 函数 '{func_name}' 执行完成，耗时: {duration:.3f}s")
            return result
        except Exception as e:
            duration = time.time() - start
            logger.error(f"❌ 函数 '{func_name}' 执行失败，耗时: {duration:.3f}s", exc_info=True)
            raise
    return wrapper

def log_var(name: str, value):
    """
    快速记录变量值（可用于调试）
    """
    logger.debug(f"{name} = {value}")

def log_call(location: str):
    """
    记录某处代码被调用
    """
    logger.debug(f"📌 调用点: {location}")
