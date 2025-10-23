"""
【通义千问 Qwen】API集成模块
用于意图理解和任务处理
"""
import json
import re
import logging
import dashscope
from dashscope import Generation
from database import config
from Progress.utils.logger_utils import log_time, log_step, log_var, log_call
from Progress.utils.logger_config import setup_logger

# --- 初始化日志器 ---
logger = logging.getLogger("ai_assistant")

DASHSCOPE_API_KEY = config.api_key
DASHSCOPE_MODEL = config.model


class QWENAssistant:
    def __init__(self):
        if not DASHSCOPE_API_KEY:
            raise ValueError("缺少 DASHSCOPE_API_KEY，请检查配置文件")
        dashscope.api_key = DASHSCOPE_API_KEY

        self.model_name = DASHSCOPE_MODEL or 'qwen-max'
        logger.info(f"✅ QWENAssistant 初始化完成，使用模型: {self.model_name}")

        self.conversation_history = []

        self.system_prompt = """
你是一个智能语音控制助手，能够理解用户的自然语言指令，并将其转化为可执行的任务计划。

你的职责是：
- 准确理解用户意图；
- 若涉及多个动作，需拆解为【执行计划】；
- 输出一个严格符合规范的 JSON 对象，供系统解析执行；
- 所有回复必须使用中文（仅限于 response_to_user 字段）；

🎯 输出格式要求（必须遵守）：
{
  "intent": "system_control",           // 意图类型："system_control"
  "task_type": "start_background_tasks",// 任务类型的简要描述（动态生成）
  "execution_plan": [                   // 执行步骤列表（每个步骤包含 operation, parameters, description）
    {
      "operation": "函数名",             // 必须是已知操作之一
      "parameters": { ... },            // 参数对象（按需提供）
      "description": "该步骤的目的说明"
    }
  ],
  "response_to_user": "你要对用户说的话（用中文）",
  "requires_confirmation": false,       // 是否需要用户确认后再执行
  "mode": "parallel"                    // 执行模式："parallel"（并行）或 "serial"（串行）
}

📌 已知 operation 列表（不可拼写错误）：
- play_music(music_path: str)
- stop_music()
- pause_music()
- resume_music()
- open_application(app_name: str)
- create_file(file_name: str, content?: str)
- read_file(file_name: str)
- write_file(file_name: str, content: str)
- set_reminder(reminder_time: str, message: str)
- exit()

📌 规则说明：
1. 只有当用户明确要求执行系统级任务时，才设置 intent="system_control"；
   否则设为 intent="chat"（例如闲聊、问天气、讲笑话等）。

2. execution_plan 中的每一步都必须与用户需求直接相关；
   ❌ 禁止添加无关操作（如随便加 speak_response 或 play_music）！

3. mode 决定执行方式：
   - 如果各步骤互不依赖 → "parallel"
   - 如果有先后依赖（如先打开再写入）→ "serial"

4. response_to_user 是你对用户的自然语言反馈，必须简洁友好，使用中文。

5. requires_confirmation：
   - 涉及删除、覆盖文件、长时间运行任务 → true
   - 普通操作（打开应用、播放音乐）→ false

⚠️ 重要警告：
- 绝不允许照搬示例中的参数或路径！必须根据用户输入提取真实信息。
- 不得虚构不存在的 operation 或 parameter 名称。
- 不得省略任何字段，所有 key 都必须存在。
- 不得输出额外文本（如解释、注释、
```json
``` 包裹符），只输出纯 JSON 对象。

✅ 正确行为示例：

用户说：“帮我写一份自我介绍到 D:/intro.txt，并打开看看”
→ 应返回包含 write_file 和 read_file 的 serial 计划。

用户说：“播放 C:/Music/background.mp3 并告诉我准备好了”
→ 可以并行执行 play_music 和 speak_response。

用户说：“今天过得怎么样？”
→ intent="chat"，response_to_user="我很好，谢谢！"

🚫 错误行为：
- 把所有指令都变成和示例一样的操作组合；
- 在没有请求的情况下自动添加 speak_response；
- 使用未定义的操作如 run_script、send_email。

现在，请根据用户的最新指令生成对应的 JSON 响应。
"""

    @log_time
    @log_step("处理语音指令")
    def process_voice_command(self, voice_text):
        log_var("原始输入", voice_text)

        if not voice_text.strip():
            return self._create_fallback_response("我没有听清楚，请重新说话。")

        self.conversation_history.append({"role": "user", "content": voice_text})

        try:
            messages = [{"role": "system", "content": self.system_prompt}]
            messages.extend(self.conversation_history[-10:])  # 保留最近上下文

            response = Generation.call(
                model=self.model_name,
                messages=messages,
                temperature=0.5,
                top_p=0.8,
                max_tokens=1024
            )

            if response.status_code != 200:
                logger.error(f"Qwen API 调用失败: {response.status_code}, {response.message}")
                return self._create_fallback_response(f"服务暂时不可用: {response.message}")

            ai_output = response.output['text'].strip()
            log_var("模型输出", ai_output)

            self.conversation_history.append({"role": "assistant", "content": ai_output})

            # === 尝试解析 JSON ===
            parsed = self._extract_and_validate_json(ai_output)
            if parsed:
                return parsed
            else:
                # 若无法解析为有效计划，则降级为普通对话
                return self._create_fallback_response(ai_output)

        except Exception as e:
            logger.exception("处理语音指令时发生异常")
            return self._create_fallback_response("抱歉，我遇到了一些技术问题，请稍后再试。")

    def _extract_and_validate_json(self, text: str):
        """从文本中提取 JSON 并验证结构"""
        try:
            # 方法1：直接加载
            data = json.loads(text)
            return self._validate_plan_structure(data)
        except json.JSONDecodeError:
            pass

        # 方法2：正则匹配第一个大括号包裹的内容
        match = re.search(r'\{[\s\S]*\}', text)
        if not match:
            return None

        try:
            data = json.loads(match.group())
            return self._validate_plan_structure(data)
        except:
            return None

    def _validate_plan_structure(self, data: dict):
        """验证是否符合多任务计划格式"""
        required_top_level = ["intent", "task_type", "execution_plan", "response_to_user", "requires_confirmation"]
        for field in required_top_level:
            if field not in data:
                logger.warning(f"缺少必要字段: {field}")
                return None

        valid_operations = {
            "play_music", "stop_music", "pause_music", "resume_music",
            "open_application", "create_file", "read_file", "write_file",
            "set_reminder", "speak_response", "exit"
        }

        for step in data["execution_plan"]:
            op = step.get("operation")
            params = step.get("parameters", {})

            if not op or op not in valid_operations:
                logger.warning(f"无效操作: {op}")
                return None

            if not isinstance(params, dict):
                logger.warning(f"parameters 必须是对象: {params}")
                return None

        # 补全默认值
        if "mode" not in data:
            data["mode"] = "parallel"

        return data

    def _create_fallback_response(self, message: str):
        """降级响应：用于非结构化输出"""
        return {
            "intent": "chat",
            "task_type": "reply",
            "response_to_user": message,
            "requires_confirmation": False,
            "execution_plan": [],
            "mode": "serial"
        }

    def _create_response(self, intent, action, parameters, response, needs_confirmation):
        resp = {"intent": intent, "action": action, "parameters": parameters, "response": response, "needs_confirmation": needs_confirmation}
        log_var("返回响应", resp)
        return resp

    @log_time
    def generate_text(self, prompt, task_type="general"):
        log_var("任务类型", task_type)
        log_var("提示词长度", len(prompt))

        try:
            system_prompt = f"""
你是一个专业的文本生成助手。根据用户的要求生成高质量的文本内容。

任务类型：{task_type}
要求：{prompt}

请生成相应的文本内容，确保内容准确、有逻辑、语言流畅。
"""
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

assistant = QWENAssistant()