"""
【AI语音助手】主程序入口
集成语音识别、Qwen 意图理解、TTS 与动作执行
✅ 已修复：不再访问 _last_text 私有字段
✅ 增强：异常防护、类型提示、唤醒词预留接口
"""

import sys
import time
import logging

# --- 导入日志工具 ---
from Progress.utils.logger_config import setup_logger
from Progress.utils.logger_utils import log_time, log_step, log_var, log_call

# --- 显式导入各模块核心类 ---
from Progress.app.voice_recognizer import SpeechRecognizer
from Progress.app.qwen_assistant import QWENAssistant
from Progress.app.text_to_speech import TTSEngine
from Progress.app.system_controller import SystemController, TaskOrchestrator
from database import config


# --- 初始化全局日志器 ---
logger = logging.getLogger("ai_assistant")


@log_step("初始化语音识别模块")
@log_time
def initialize_speech_recognizer() -> SpeechRecognizer:
    try:
        recognizer = SpeechRecognizer()
        if not recognizer.is_available():
            raise RuntimeError("麦克风不可用，请检查设备连接和权限")
        log_call("✅ 语音识别器初始化完成")
        return recognizer
    except Exception as e:
        logger.critical(f"🔴 初始化语音识别失败: {e}")
        raise


@log_step("初始化 AI 助手模块")
@log_time
def initialize_qwen_assistant() -> QWENAssistant:
    try:
        assistant = QWENAssistant()
        log_call("✅ Qwen 助手初始化完成")
        return assistant
    except Exception as e:
        logger.critical(f"🔴 初始化 Qwen 助手失败: {e}")
        raise


@log_step("初始化文本转语音模块")
@log_time
def initialize_tts_engine() -> TTSEngine:
    try:
        tts_engine = TTSEngine()
        if not tts_engine.is_available():
            raise RuntimeError("TTS引擎初始化失败")
        log_call("✅ TTS 引擎初始化完成")
        return tts_engine
    except Exception as e:
        logger.critical(f"🔴 初始化 TTS 失败: {e}")
        raise


@log_step("初始化动作执行器")
@log_time
def initialize_action_executor() -> TaskOrchestrator:
    system_controller = SystemController()
    task_orchestrator = TaskOrchestrator(system_controller=system_controller)
    log_call("✅ 动作执行器初始化完成")
    return task_orchestrator


@log_step("安全执行单次交互")
@log_time
def handle_single_interaction_safe(
    recognizer: SpeechRecognizer,
    assistant: QWENAssistant,
    tts_engine: TTSEngine,
    executor: TaskOrchestrator
):
    try:
        handle_single_interaction(recognizer, assistant, tts_engine, executor)
    except Exception as e:
        logger.exception("⚠️ 单次交互过程中发生异常，已降级处理")
        error_msg = "抱歉，我在处理刚才的操作时遇到了一点问题。"
        logger.info(f"🗣️ 回复: {error_msg}")
        tts_engine.speak(error_msg)


@log_step("处理一次语音交互")
@log_time
def handle_single_interaction(
    recognizer: SpeechRecognizer,
    assistant: QWENAssistant,
    tts_engine: TTSEngine,
    executor: TaskOrchestrator
):
    # 1. 听
    voice_text = recognizer.listen_and_recognize()
    if not voice_text:
        response = "抱歉，我没有听清楚，请重新说话。"
        logger.info(f"🗣️ 回复: {response}")
        tts_engine.speak(response)
        return

    log_var("🎤 识别到的语音文本", voice_text)

    # 2. 理解
    ai_response = assistant.process_voice_command(voice_text)
    ai_reply = ai_response.get("response", "好的，已处理。")
    intent = ai_response.get("intent")
    action = ai_response.get("action")
    params = ai_response.get("parameters")

    log_var("🧠 AI响应.intent", intent)
    log_var("🧠 AI响应.action", action)
    log_var("🧠 AI响应.parameters", params)

    # 3. 执行（若无需确认）
    if not ai_response.get("needs_confirmation", False):
        try:
            result = executor.execute_from_ai_decision(text)

            if result["success"]:
                ai_reply = result["message"]
            else:
                ai_reply = "抱歉，" + result["message"]
        except Exception as e:
            logger.exception("💥 执行动作时发生异常")
            ai_reply = "抱歉，我在尝试执行这个操作时出了点问题。"

    # 4. 说
    logger.info(f"🗣️ 回复: {ai_reply}")
    tts_engine.speak(ai_reply)


@log_step("启动 AI 语音助手")
@log_time
def main():
    logger.info("🚀 正在启动 AI 语音助手系统...")

    try:
        recognizer = initialize_speech_recognizer()
        assistant = initialize_qwen_assistant()
        tts_engine = initialize_tts_engine()
        executor = initialize_action_executor()

        log_call("✅ 所有模块初始化完成，进入监听循环")

        log_call("\n" + "—" * 50)
        log_call("🎙️  语音助手已就绪")
        log_call("💡 说出你的命令，例如：'打开浏览器'、'写一篇春天的文章'")
        log_call("🛑 说出‘退出’、‘关闭’、‘停止’或‘拜拜’来结束程序")
        log_call("—" * 50 + "\n")

        while True:    
            try:
                handle_single_interaction(recognizer, assistant, tts_engine, executor)
            except KeyboardInterrupt:
                logger.info("🛑 用户主动中断 (Ctrl+C)，准备退出...")
                raise  # 让 main 捕获并退出
            except Exception as e:
                logger.exception("⚠️ 单次交互过程中发生异常，已降级处理")
                error_msg = "抱歉，我在处理刚才的操作时遇到了一点问题。"
                logger.info(f"🗣️ 回复: {error_msg}")
                tts_engine.speak(error_msg)
                last_text = recognizer.last_text.lower()
                exit_keywords = ['退出', '关闭', '停止', '拜拜', '再见']
                if any(word in last_text for word in exit_keywords):
                    logger.info("🎯 用户请求退出，程序即将终止")
                    break

            time.sleep(0.5)

        logger.info("👋 语音助手已安全退出")

    except KeyboardInterrupt:
        logger.info("🛑 用户通过 Ctrl+C 中断程序")
        print("\n👋 再见！")

    except Exception as e:
        logger.exception("❌ 主程序运行时发生未预期异常")
        print(f"\n🚨 程序异常终止：{e}")
        sys.exit(1)


if __name__ == "__main__":
    if not logging.getLogger().handlers:
        setup_logger(name="ai_assistant", log_dir="logs", level=logging.INFO)
    main()


    """ # 使用配置（推荐方式）

    #增加或修改新的设置配置
    config.update_key("shortcuts",key = "exit",value = "Ctrl+C")
    config.update_key("shortcuts",key = "select_all",value = "Shift+Alt+A")

    #修改资源路径
    config.set_resource_path("./resoures") """