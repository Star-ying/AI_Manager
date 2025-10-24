from functools import wraps
import inspect
import logging

from Progress.app.qwen_assistant import assistant

# 全局注册表
REGISTERED_FUNCTIONS = {}
FUNCTION_SCHEMA = []
FUNCTION_MAP = {}  # (intent, action) -> method_name

logger = logging.getLogger("ai_assistant")

def ai_callable(
    *,
    description: str,
    params: dict,
    intent: str = None,
    action: str = None,
    concurrent: bool = False  # 新增：是否允许并发执行
):
    def decorator(func):
        func_name = func.__name__

        metadata = {
            "func": func,
            "description": description,
            "params": params,
            "intent": intent,
            "action": action,
            "signature": str(inspect.signature(func)),
            "concurrent": concurrent  # 记录是否可并发
        }

        REGISTERED_FUNCTIONS[func_name] = metadata

        FUNCTION_SCHEMA.append({
            "name": func_name,
            "description": description,
            "parameters": params
        })

        if intent and action:
            key = (intent, action)
            if key in FUNCTION_MAP:
                raise ValueError(f"冲突：语义 ({intent}, {action}) 已被函数 {FUNCTION_MAP[key]} 占用")
            FUNCTION_MAP[key] = func_name

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        wrapper._ai_metadata = metadata
        return wrapper
    return decorator
