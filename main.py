"""
AI 语音助手主入口
"""

import sys
import time
import signal
import threading
from Progress.utils.logger_config import setup_logger
from Progress.app import (
    get_system_controller,
    get_task_executor,
    get_tts_engine,
    get_voice_recognizer,
    get_ai_assistant
)
from Progress.utils.logger_utils import log_call, log_step, log_time

logger = setup_logger("ai_assistant")
_shutdown_event = threading.Event()

def signal_handler(signum, frame):
    logger.info(f"🛑 收到信号 {signum}，准备退出...")
    _shutdown_event.set()

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

@log_step("处理一次交互")
@log_time
def handle_single_interaction() -> bool:
    try:
        rec = get_voice_recognizer()
        assistant = get_ai_assistant()
        executor = get_task_executor()
        tts = get_tts_engine()

        text = rec.listen_and_recognize()
        
        # 🔴 如果 shutdown 已被设置，可以退出
        if _shutdown_event.is_set():
            logger.info("🛑 收到关闭信号，停止交互")
            return False

        # 🟢 如果只是没听到语音，不要退出，而是继续监听
        if not text:
            logger.debug("🔇 未检测到有效语音，进入下一轮监听...")
            return True  # ✅ 继续运行！

        logger.info(f"🗣️ 用户说: '{text}'")
        decision = assistant.process_voice_command(text)
        result = executor.execute_task_plan(decision)

        ai_reply = result["message"]
        if not result["success"] and not ai_reply.startswith("抱歉"):
            ai_reply = f"抱歉，{ai_reply}"

        tts.speak(ai_reply,True)  # 异步播报，不阻塞

        expect_follow_up = decision.get("expect_follow_up", False)
        rec.current_timeout = 8 if expect_follow_up else 3

        return not (result.get("should_exit") is True)
    except Exception as e:
        logger.exception("❌ 交互出错")
        get_tts_engine().speak("抱歉，遇到错误，请稍后再试。")
        return True

def main():
    while not _shutdown_event.is_set():
        try:
            if not handle_single_interaction():
                break
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.exception("🔁 主循环异常，恢复中...")
            time.sleep(1)

    # 清理
    get_tts_engine().stop()
    pyaudio_instance = get_voice_recognizer().audio
    if pyaudio_instance:
        pyaudio_instance.terminate()
    logger.info("👋 助手已退出")
    sys.exit(0)

if __name__ == "__main__":
    main()
