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

""" import config
from utils.logger_utils import log_time, log_step, log_var, log_call
from utils.logger_config import setup_logger """

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
你是一个智能语音控制助手，能够理解用户的语音指令并执行相应的任务。

你的主要能力包括：
1. 播放音乐和控制媒体
2. 文件操作（创建、读取、编辑文件）
3. 文本生成（写文章、总结、翻译等）
4. 系统控制（打开应用、设置提醒等）
5. 多步骤任务编排

当用户发出指令时，你需要：
1. 理解用户的意图
2. 确定需要执行的具体操作
3. 返回结构化的响应，包含操作类型和参数

🎯 响应格式必须是严格合法的 JSON：
{
    "intent": "操作类型",
    "action": "具体动作",
    "parameters": {"参数名": "参数值"},
    "response": "给用户的回复",
    "needs_confirmation": true/false
}


📌 支持的操作类型：
- music: 音乐相关操作
- file: 文件操作
- text: 文本生成
- system: 系统控制
- task: 多步骤任务
- chat: 普通对话

❗注意事项
请始终用中文回复用户。
创建和写入是不同的操作
"""

    @log_time
    @log_step("处理语音指令")
    def process_voice_command(self, voice_text):
        log_var("原始输入", voice_text)

        if not voice_text.strip():
            return self._create_response("chat", "empty", {}, "我没有听清楚，请重新说话。", False)

        self.conversation_history.append({"role": "user", "content": voice_text})

        try:
            messages = [{"role": "system", "content": self.system_prompt}]
            messages.extend(self.conversation_history[-10:])

            response = Generation.call(
                model=self.model_name,
                messages=messages,
                temperature=0.5,
                top_p=0.8,
                max_tokens=1024
            )

            if response.status_code != 200:
                logger.error(f"Qwen API 调用失败: {response.status_code}, {response.message}")
                return self._create_response("chat", "error", {}, f"服务暂时不可用: {response.message}", False)

            ai_response = response.output['text'].strip()
            log_var("模型输出", ai_response)

            self.conversation_history.append({"role": "assistant", "content": ai_response})

            # 尝试解析 JSON
            try:
                parsed = json.loads(ai_response)
                return parsed
            except json.JSONDecodeError:
                json_match = re.search(r'\{[\s\S]*\}', ai_response)
                if json_match:
                    try:
                        return json.loads(json_match.group())
                    except:
                        pass
                return self._create_response("chat", "reply", {}, ai_response, False)

        except Exception as e:
            logger.exception("处理语音指令时发生未预期异常")
            return self._create_response("chat", "error", {}, "抱歉，我遇到了一些技术问题，请稍后再试。", False)

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

# =============================
# 🧪 测试代码
# =============================
if __name__ == "__main__":
    # 初始化全局日志系统
    setup_logger(name="ai_assistant", log_dir="logs")

    assistant = QWENAssistant()

    test_commands = [
        "播放周杰伦的歌曲",
        "写一篇关于气候变化的文章",
        "把这段话翻译成英文：今天天气真好",
        "总结一下人工智能的发展历程",
        "你好啊",
        "打开浏览器",
        "在当前文件夹创建一个测试文本并写入我的世界"
    ]

    for cmd in test_commands:
        print(f"\n🔊 用户指令: {cmd}")
        result = assistant.process_voice_command(cmd)
        print("🤖 AI响应:")
        print(json.dumps(result, ensure_ascii=False, indent=2))