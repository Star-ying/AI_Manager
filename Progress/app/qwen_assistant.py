"""
【通义千问 Qwen】API集成模块
用于意图理解和任务处理（支持 expect_follow_up 字段）
"""

import json
import re
import logging
import dashscope
from dashscope import Generation

from database.config import config
from Progress.utils.logger_utils import log_time, log_step, log_var
from Progress.utils.logger_config import setup_logger

# --- 初始化日志器 ---
logger = logging.getLogger("ai_assistant")

DASHSCOPE_API_KEY = config.get("ai_model","api_key")
DASHSCOPE_MODEL = config.get("ai_model","model")


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
  "execution_plan": [                   // 执行步骤列表
    {
      "operation": "函数名",
      "parameters": { ... },
      "description": "该步骤的目的说明"
    }
  ],
  "response_to_user": "你要对用户说的话（用中文）",
  "requires_confirmation": false,
  "mode": "parallel",
  "expect_follow_up": true              // 🔥 新增字段：是否预期用户会继续提问？
}

📌 已知 operation 列表：
- play_music()
- stop_music()
- pause_music()
- resume_music()
- open_application(app_name: str)
- create_file(file_name: str, content: str)
- read_file(file_name: str)
- write_file(file_name: str, content: str)
- set_reminder(reminder_time: str, message: str)
- exit()

📌 规则说明：
1. intent="chat" 仅用于闲聊、问天气等非操作类请求。
2. execution_plan 必须与用户需求直接相关，禁止虚构或添加无关操作。
3. mode: 并行(parallel)/串行(serial)，按依赖关系选择。
4. requires_confirmation: 删除、覆盖文件等高风险操作设为 true。
5. expect_follow_up: ⚠️ 新增关键字段！

🔥 关于 expect_follow_up 的判断标准：
- 用户正在进行多步操作（如“帮我写一篇文章” → 可能接着说“保存到桌面”）→ True
- 用户提出开放式问题（如“介绍一下人工智能”）→ True
- 用户表达未完成感（如“还有呢？”、“然后呢？”、“接下来怎么办”）→ True
- 明确结束语句（如“关闭程序”、“不用了”、“谢谢”）→ False
- 单条命令已完成闭环（如“打开记事本”）且无延伸迹象 → False

💡 示例：
  用户：“我想学习 Python”
  → expect_follow_up = True （用户可能继续问怎么学、推荐书籍等）

  用户：“播放音乐”
  → expect_follow_up = True （可能会切歌、暂停）

  用户：“退出”
  → expect_follow_up = False

⚠️ 重要警告：
- 绝不允许省略任何字段；
- 不得输出额外文本（如注释、解释）；
- 不允许使用未知 operation；
- 必须返回纯 JSON。

现在，请根据用户的最新指令生成对应的 JSON 响应。
"""

    @log_time
    @log_step("处理语音指令")
    def process_voice_command(self, voice_text):
        log_var("原始输入", voice_text)

        if not voice_text.strip():
            return self._create_fallback_response("我没有听清楚，请重新说话。", expect_follow_up=False)

        self.conversation_history.append({"role": "user", "content": voice_text})

        try:
            messages = [{"role": "system", "content": self.system_prompt}]
            messages.extend(self.conversation_history[-10:])  # 最近10轮上下文

            response = Generation.call(
                model=self.model_name,
                messages=messages,
                temperature=0.5,
                top_p=0.8,
                max_tokens=1024
            )

            if response.status_code != 200:
                logger.error(f"Qwen API 调用失败: {response.status_code}, {response.message}")
                return self._create_fallback_response(f"服务暂时不可用: {response.message}", expect_follow_up=False)

            ai_output = response.output['text'].strip()
            log_var("模型输出", ai_output)

            self.conversation_history.append({"role": "assistant", "content": ai_output})

            # === 解析并验证 JSON ===
            parsed = self._extract_and_validate_json(ai_output)
            if parsed:
                return parsed
            else:
                # 降级响应：假设只是普通聊天
                clean_text = re.sub(r'json[\s\S]*?|', '', ai_output).strip()
                return self._create_fallback_response(clean_text, expect_follow_up=True)

        except Exception as e:
            logger.exception("处理语音指令时发生异常")
            return self._create_fallback_response("抱歉，我遇到了一些技术问题，请稍后再试。", expect_follow_up=False)

    def _extract_and_validate_json(self, text: str):
        """从文本中提取 JSON 并验证结构（含 expect_follow_up）"""
        try:
            data = json.loads(text)
            return self._validate_plan_structure(data)
        except json.JSONDecodeError:
            pass

        # 尝试正则提取第一个大括号内容
        match = re.search(r'\{[\s\S]*\}', text)
        if not match:
            return None
        try:
            data = json.loads(match.group())
            return self._validate_plan_structure(data)
        except:
            return None

    def _validate_plan_structure(self, data: dict):
        """验证结构并补全字段"""
        required_top_level = ["intent", "task_type", "execution_plan", "response_to_user", "requires_confirmation"]
        for field in required_top_level:
            if field not in data:
                logger.warning(f"缺少必要字段: {field}")
                return None

        valid_operations = {
            "play_music", "stop_music", "pause_music", "resume_music",
            "open_application", "create_file", "read_file", "write_file",
            "set_reminder", "exit"
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
        if "expect_follow_up" not in data:
            # 启发式补全
            ending_words = ['退出', '关闭', '停止', '拜拜', '再见', '不用了', '谢谢']
            is_ending = any(word in data.get("response_to_user", "") for word in ending_words)
            data["expect_follow_up"] = not is_ending

        return data

    def _create_fallback_response(self, message: str, expect_follow_up: bool):
        """降级响应，包含 expect_follow_up 字段"""
        return {
            "intent": "chat",
            "task_type": "reply",
            "response_to_user": message,
            "requires_confirmation": False,
            "execution_plan": [],
            "mode": "serial",
            "expect_follow_up": expect_follow_up  # 👈 新增
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

# 实例化全局助手
assistant = QWENAssistant()