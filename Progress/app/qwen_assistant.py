"""
【通义千问 Qwen】API集成模块
用于意图理解和任务处理（支持 expect_follow_up 字段）
"""

import json
import re
import logging
import requests
# 【留痕 2026-10-24】原 dashscope 原生 SDK 改 OpenAI 兼容协议（通用模板：base_url+key+model 三件套即可接任意网关）：
# import dashscope
# from dashscope import Generation
from threading import Lock

from database.config import config
from Progress.utils.logger_utils import log_time, log_step, log_var
from Progress.utils.logger_config import setup_logger
try:
    from Progress.utils.ai_tools import FUNCTION_SCHEMA
except ImportError:
    FUNCTION_SCHEMA = []

logger = logging.getLogger("ai_assistant")

LLM_API_KEY = config.get("ai_model", "api_key")
LLM_MODEL = config.get("ai_model", "model")
LLM_BASE_URL = config.get("ai_model", "base_url") or "https://dora.tinno.com/dora-ops/llm-proxy/v1"
# 原名保留一份供外部引用兼容：
DASHSCOPE_API_KEY = LLM_API_KEY
DASHSCOPE_MODEL = LLM_MODEL


class QWENAssistant:
    _instance = None
    _initialized = False
    _lock = Lock()  # 线程锁，保证线程安全

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                # 双重检查锁定（Double-Checked Locking）
                if cls._instance is None:
                    cls._instance = super(QWENAssistant, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # 防止重复初始化
        if QWENAssistant._initialized:
            return

        with QWENAssistant._lock:
            if QWENAssistant._initialized:
                return

            # === 正式初始化 ===
            if not LLM_API_KEY:
                raise ValueError("缺少 ai_model.api_key，请检查配置文件")
            self.api_key = LLM_API_KEY
            self.base_url = LLM_BASE_URL.rstrip("/")
            self.model_name = LLM_MODEL or 'qwen3.8-flash'
            # 原 dashscope 初始化已改 OpenAI 兼容：
            # dashscope.api_key = DASHSCOPE_API_KEY
            logger.info(f"✅ QWENAssistant 单例初始化完成，网关: {self.base_url} 模型: {self.model_name}")

            self.conversation_history = []

            # 动态生成 operation 列表文本
            operation_list_text = self._generate_operation_list()

            # 构建 system prompt
            self.system_prompt = f"""
你是一个智能语音控制助手，能够理解用户的自然语言指令，并将其转化为可执行的任务计划。

🎯 输出格式要求（必须遵守）：
{{
  "intent": "system_control",
  "task_type": "start_background_tasks",
  "execution_plan": [
    {{
      "operation": "函数名",
      "parameters": {{ ... }},
      "description": "该步骤的目的说明"
    }}
  ],
  "response_to_user": "你要对用户说的话（用中文）",
  "requires_confirmation": false,
  "mode": "parallel",
  "expect_follow_up": true
}}

📌 已知 operation 列表：
{operation_list_text}

📌 规则说明：
1. intent="chat" 仅用于闲聊。
2. execution_plan 必须与需求相关。
3. mode: parallel/serial。
4. requires_confirmation: 高风险操作设为 true。
5. expect_follow_up: 根据上下文判断是否预期后续提问。

🔥 关于 expect_follow_up 的判断标准：
- 多步操作、开放式问题 → True
- 明确结束语句 → False

⚠️ 重要警告：
- 不得输出额外文本；
- 不允许使用未知 operation；
- 必须返回纯 JSON。

现在，请根据用户的最新指令生成对应的 JSON 响应。
"""

            QWENAssistant._initialized = True

    def _generate_operation_list(self) -> str:
        """根据 FUNCTION_SCHEMA 生成操作列表描述"""
        lines = []
        for item in FUNCTION_SCHEMA:
            name = item["name"]
            desc = item["description"]
            params_desc = item.get("parameters", {})
            param_strs = [f"{k}: {v}" for k, v in params_desc.items()]
            params_display = "(" + ", ".join(param_strs) + ")" if param_strs else "()"
            lines.append(f"- {name}{params_display}：{desc}")
        return "\n".join(lines) if lines else "- 无可用操作"

    @classmethod
    def get_instance(cls):
        """提供公共访问点，确保初始化已完成"""
        if cls._instance is None:
            raise RuntimeError(
                "QWENAssistant 尚未初始化！请先确保所有 @ai_callable 函数已注册，并手动触发一次实例化。"
            )
        return cls._instance

    @log_time
    @log_step("处理语音指令")
    def process_voice_command(self, voice_text):
        log_var("原始输入", voice_text)

        if not voice_text.strip():
            return self._create_fallback_response("我没有听清楚，请重新说话。", expect_follow_up=False)

        self.conversation_history.append({"role": "user", "content": voice_text})

        try:
            messages = [{"role": "system", "content": self.system_prompt}]
            messages.extend(self.conversation_history[-10:])

            # 原 dashscope Generation.call 已改 OpenAI 兼容模板：
            # response = Generation.call(model=self.model_name, messages=messages,
            #                            temperature=0.5, top_p=0.8, max_tokens=1024)
            # if response.status_code != 200: ...
            # ai_output = response.output['text'].strip()
            resp = requests.post(
                self.base_url + "/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}",
                         "Content-Type": "application/json"},
                json={"model": self.model_name, "messages": messages,
                      "temperature": 0.5, "top_p": 0.8, "max_tokens": 1024},
                timeout=30,
            )

            if resp.status_code != 200:
                logger.error(f"LLM 网关调用失败: {resp.status_code}, {resp.text[:200]}")
                return self._create_fallback_response(f"服务暂时不可用: HTTP {resp.status_code}", expect_follow_up=False)

            ai_output = resp.json()["choices"][0]["message"]["content"].strip()
            log_var("模型输出", ai_output)

            self.conversation_history.append({"role": "assistant", "content": ai_output})

            parsed = self._extract_and_validate_json(ai_output)
            if parsed:
                return parsed
            else:
                clean_text = re.sub(r'json[\s\S]*?\n|', '', ai_output).strip()
                return self._create_fallback_response(clean_text, expect_follow_up=True)

        except Exception as e:
            logger.exception("处理语音指令时发生异常")
            return self._create_fallback_response("抱歉，我遇到了一些技术问题，请稍后再试。", expect_follow_up=False)

    def _extract_and_validate_json(self, text: str):
        try:
            data = json.loads(text)
            return self._validate_plan_structure(data)
        except json.JSONDecodeError:
            pass

        match = re.search(r'\{[\s\S]*\}', text)
        if not match:
            return None
        try:
            data = json.loads(match.group())
            return self._validate_plan_structure(data)
        except:
            return None

    def _validate_plan_structure(self, data: dict):
        if not isinstance(data, dict):
            logger.warning("输入数据不是字典类型")
            return None

        # 定义必需字段（仅适用于任务型）
        required_top_level = ["intent", "task_type", "execution_plan", "response_to_user", "requires_confirmation"]

        # 闲聊类意图列表（可配置）
        CHAT_INTENTS = {"chat"}

        intent = data.get("intent")

        # 如果没有 intent 字段，至少报错
        if not intent:
            logger.warning("缺少必要字段: intent")
            return None

        # === 情况1：如果是闲聊类意图，放宽校验 ===
        if intent in CHAT_INTENTS:
            logger.info(f"检测到闲聊意图 '{intent}'，启用宽松模式")

            # 自动设置其他默认值
            data.setdefault("task_type", "chat")
            data.setdefault("requires_confirmation", False)
            data.setdefault("mode", "single")
            data.setdefault("expect_follow_up", True)  # 通常希望继续对话

            # 不要求 execution_plan 存在，但如果存在则要合法
            if "execution_plan" in data:
                if not self._is_valid_execution_plan(data["execution_plan"]):
                    logger.warning("闲聊消息中的 execution_plan 不合法")
                    return None

            return data

        # === 情况2：任务型意图 → 严格校验 ===
        missing_fields = [field for field in required_top_level if field not in data]
        if missing_fields:
            logger.warning(f"任务型请求缺少必要字段: {missing_fields}")
            return None

        # 校验 execution_plan 中每个步骤的操作是否合法
        if not isinstance(data["execution_plan"], list):
            logger.warning("execution_plan 必须是一个数组")
            return None

        valid_operations = {item["name"] for item in FUNCTION_SCHEMA} | {"exit"}

        for step in data["execution_plan"]:
            op = step.get("operation")
            params = step.get("parameters", {})

            if not op or op not in valid_operations:
                logger.warning(f"无效操作: {op}")
                return None
            if not isinstance(params, dict):
                logger.warning(f"parameters 必须是对象: {params}")
                return None

        # === 自动补全可选字段 ===
        if "mode" not in data:
            # 并行模式：多个步骤可同时执行；串行则逐个执行
            data["mode"] = "parallel"  # 或可根据 task_type 判断

        if "expect_follow_up" not in data:
            ending_words = ['退出', '关闭', '停止', '拜拜', '再见', '不用了', '谢谢', '好的']
            is_ending = any(word in data.get("response_to_user", "") for word in ending_words)
            data["expect_follow_up"] = not is_ending

        # 确保布尔类型正确
        data["requires_confirmation"] = bool(data["requires_confirmation"])
        data["expect_follow_up"] = bool(data["expect_follow_up"])

        return data

    def _is_valid_execution_plan(self, plan):
        if not isinstance(plan, list):
            return False
        valid_operations = {item["name"] for item in FUNCTION_SCHEMA} | {"exit"}
        for step in plan:
            op = step.get("operation")
            params = step.get("parameters", {})
            if not op or op not in valid_operations:
                return False
            if not isinstance(params, dict):
                return False
        return True
    
    def _create_fallback_response(self, message: str, expect_follow_up: bool):
        return {
            "intent": "chat",
            "task_type": "reply",
            "response_to_user": message,
            "requires_confirmation": False,
            "execution_plan": [],
            "mode": "serial",
            "expect_follow_up": expect_follow_up
        }

    @log_time
    def generate_text(self, prompt, task_type="general"):
        log_var("任务类型", task_type)
        log_var("提示词长度", len(prompt))
        try:
            system_prompt = f"你是专业文本生成助手。\n任务类型：{task_type}\n要求：{prompt}"
            response = Generation.call(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=2000
            )
            if response.status_code == 200:
                result = response.output['text']
                log_var("生成结果长度", len(result))
                return result
            else:
                error_msg = f"文本生成失败: {response.message}"
                logger.error(error_msg)
                return error_msg
        except Exception as e:
            logger.exception("文本生成出错")
            return f"抱歉，生成文本时遇到错误：{str(e)}"

    @log_time
    def summarize_text(self, text):
        log_var("待总结文本长度", len(text))
        try:
            prompt = f"请总结以下文本的主要内容：\n\n{text}"
            response = Generation.call(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500
            )
            if response.status_code == 200:
                result = response.output['text']
                log_var("总结结果长度", len(result))
                return result
            else:
                error_msg = f"总结失败: {response.message}"
                logger.error(error_msg)
                return error_msg
        except Exception as e:
            logger.exception("文本总结出错")
            return f"抱歉，总结文本时遇到错误：{str(e)}"

    @log_time
    def translate_text(self, text, target_language="英文"):
        log_var("目标语言", target_language)
        log_var("原文长度", len(text))
        try:
            prompt = f"请将以下文本翻译成{target_language}：\n\n{text}"
            response = Generation.call(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1000
            )
            if response.status_code == 200:
                result = response.output['text']
                log_var("翻译结果长度", len(result))
                return result
            else:
                error_msg = f"翻译失败: {response.message}"
                logger.error(error_msg)
                return error_msg
        except Exception as e:
            logger.exception("文本翻译出错")
            return f"抱歉，翻译文本时遇到错误：{str(e)}"
