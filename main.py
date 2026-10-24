"""
AI 语音助手主入口
"""

import sys
import time
import signal
import threading
from typing import Any

from Progress.utils.logger_config import setup_logger
from Progress.app import (
    get_system_controller,
    get_task_executor,
    get_tts_engine,
    get_voice_recognizer,
    get_ai_assistant
)
import api_server
from api_server import APIServer
from Progress.utils.logger_utils import log_call, log_step, log_time

logger = setup_logger("ai_assistant")
_shutdown_event = threading.Event()

def signal_handler(signum, frame):
    logger.info(f"🛑 收到信号 {signum}，准备退出...")
    _shutdown_event.set()

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

_last_silence_warn = 0  # 记录最后一次静音警告时间

@log_step("处理一次交互")
@log_time
def handle_single_interaction() -> bool:
    try:
        rec = get_voice_recognizer()
        assistant = get_ai_assistant()
        executor = get_task_executor()
        tts = get_tts_engine()

        api_server.current_status["is_listening"] = rec.is_enabled()
        text = rec.listen_and_recognize()

        if _shutdown_event.is_set():
            logger.info("🛑 收到关闭信号，停止交互")
            return False

        if text:
            api_server.last_transcribed_text = text

        if not text:
            global _last_silence_warn
            now = time.time()
            if now - _last_silence_warn > 30:
                logger.info("🔇 当前未检测到语音输入，请说话唤醒...")
                _last_silence_warn = now
            return True

        logger.info(f"🗣️ 用户说: '{text}'")
        api_server.current_status.update({"is_processing": True, "timestamp": int(time.time())})
        decision = assistant.process_voice_command(text)
        result = executor.execute_task_plan(decision)
        api_server.current_status.update({
            "is_processing": False,
            "last_command_result": {
                "success": result["success"],
                "message": result["message"],
                "operation": "voice_loop",
            },
            "timestamp": int(time.time()),
        })

        ai_reply = result["message"]
        if not result["success"] and not ai_reply.startswith("抱歉"):
            ai_reply = f"抱歉，{ai_reply}"

        api_server.current_status["is_tts_playing"] = True
        tts.speak(ai_reply, block=True)
        api_server.current_status["is_tts_playing"] = False

        expect_follow_up = decision.get("expect_follow_up", False)
        rec.current_timeout = 8 if expect_follow_up else 3

        return not result.get("should_exit", False)

    except Exception as e:
        logger.exception("❌ 交互出错")
        try:
            get_tts_engine().speak("抱歉，遇到错误，请稍后再试。", True)
        except:
            pass  # 即使播报也失败，也不影响流程
        return True


def main():
    logger.info("🚀 AI 语音助手正在启动...")

    # 启动 API 服务（非阻塞）
    try:
        api = APIServer()
        api.start()
        logger.info("🌐 API 服务已启动: http://127.0.0.1:5001/api")
    except Exception as e:
        logger.error(f"❌ 启动 API 服务失败: {e}")
        sys.exit(1)

    # 主交互循环
    logger.info("👂 助手已就绪，请开始说话...")
    while not _shutdown_event.is_set():
        try:
            should_continue = handle_single_interaction()
            if not should_continue:
                logger.info("👋 收到退出指令，准备关闭...")
                break
        except KeyboardInterrupt:
            api.stop()
            break
        except Exception as e:
            logger.exception("🔁 主循环异常，恢复中...")
            time.sleep(1)

    api.stop()
    # 清理资源
    logger.info("🧹 正在清理资源...")
    try:
        get_tts_engine().stop()
    except Exception as e:
        logger.warning(f"TTS 停止失败: {e}")

    try:
        get_voice_recognizer().close()  # 推荐方法
    except Exception as e:
        logger.warning(f"语音识别器关闭失败: {e}")

    logger.info("👋 助手已退出")
    sys.exit(0)


if __name__ == "__main__":
    main()
