from functools import wraps
import inspect

from Progress.app.qwen_assistant import QWENAssistant

# 全局注册表
REGISTERED_FUNCTIONS = {}
FUNCTION_SCHEMA = []
FUNCTION_MAP = {}  # (intent, action) -> method_name

_qwen_assistant = None


def ai_callable(*, description: str, params: dict, intent: str = None, action: str = None):
    """
    可被 AI 调用的函数装饰器
    :param description: 函数功能描述（供 LLM 理解）
    :param params: 参数说明 {"参数名": "说明"}
    :param intent: 意图类别，如 'music', 'file'（用于语义路由）
    :param action: 动作类型，如 'play', 'create'（用于语义路由）
    """
    def decorator(func):
        # 获取类方法信息（如果是实例方法）
        func_name = func.__name__

        # 注册元数据
        metadata = {
            "func": func,
            "description": description,
            "params": params,
            "intent": intent,
            "action": action,
            "signature": str(inspect.signature(func)) if hasattr(func, '__code__') else ""
        }

        REGISTERED_FUNCTIONS[func_name] = metadata

        # 构建 FUNCTION_SCHEMA（用于 prompt）
        FUNCTION_SCHEMA.append({
            "name": func_name,
            "description": description,
            "parameters": params
        })

        # 构建 FUNCTION_MAP（用于语义路由）
        if intent and action:
            key = (intent, action)
            if key in FUNCTION_MAP:
                raise ValueError(f"冲突：语义 ({intent}, {action}) 已被函数 {FUNCTION_MAP[key]} 占用")
            FUNCTION_MAP[key] = func_name

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        # 绑定元数据到函数本身（便于反射）
        wrapper._ai_metadata = metadata
        return wrapper

    return decorator


def get_qwen_assistant():
    global _qwen_assistant
    if _qwen_assistant is None:
        _qwen_assistant = QWENAssistant()
    return _qwen_assistant


def call_llm_to_choose_function(user_query: str) -> dict:
    """
    使用 Qwen 助手理解用户意图，并通过 FUNCTION_MAP 自动匹配函数
    返回格式: {"function": "func_name", "arguments": {...}}
    """
    assistant = get_qwen_assistant()

    try:
        ai_response = assistant.process_voice_command(user_query)
        intent = ai_response.get("intent")
        action = ai_response.get("action")
        params = ai_response.get("parameters", {})
        response_text = ai_response.get("response", "好的")

        # === 核心逻辑：使用自动构建的 FUNCTION_MAP ===
        func_name = FUNCTION_MAP.get((intent, action))

        if func_name and func_name in REGISTERED_FUNCTIONS:
            # 成功匹配到函数
            return {
                "function": func_name,
                "arguments": params
            }
        elif intent == "text":
            # 文本生成类任务
            return {
                "function": "_generate_text_task",
                "arguments": {"task_type": action, "prompt": user_query}
            }
        elif intent == "chat":
            # 对话类任务
            return {
                "function": "_speak_response",
                "arguments": {"message": response_text}
            }
        else:
            # 无法识别或无对应函数
            return {
                "function": "_speak_response",
                "arguments": {"message": f"抱歉，我还不能处理这个请求：{response_text}"}
            }

    except Exception as e:
        print(f"❌ AI 决策出错: {e}")
        return {}