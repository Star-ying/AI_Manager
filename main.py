"""
【AI语音助手】主程序入口
集成语音识别、Qwen 意图理解、TTS 与动作执行
✅ 使用 AI 动态控制下一轮监听超时时间（expect_follow_up）
"""

import sys
import threading
import time
import logging

# --- 导入日志工具 ---
from Progress.utils.logger_config import setup_logger
from Progress.utils.logger_utils import log_call, log_time, log_step, log_var

# --- 显式导入各模块核心实例 ---
from Progress.app.voice_recognizer import recognizer
from Progress.app.qwen_assistant import assistant
from Progress.app.text_to_speech import tts_engine
from Progress.app.system_controller import executor
from database.config import config  # 注意路径修正
from api_server import create_api_server  # 新方式

# 创建 API 服务（但不绑定具体实例）
api_app, init_api_deps = create_api_server()

def run_api_server(host='127.0.0.1', port=5000):
    app, init_deps = create_api_server()
    init_deps(ass=assistant, exec=executor, tts=tts_engine, rec=recognizer)
    threading.Thread(
        target=lambda: app.run(
            host=host,
            port=port,
            debug=False,
            threaded=True,
            use_reloader=False
        ),
        daemon=True
    ).start()
    logger.info(f"🌐 API 服务器已启动：http://{host}:{port}")

# ✅ 在全局作用域创建 logger 前必须先初始化
logger = None  # 先占位

@log_step("处理一次语音交互（AI动态控制等待）")
@log_time
def handle_single_interaction():
    # ✅ 显式传入动态超时
    text = recognizer.listen_and_recognize(timeout=recognizer.current_timeout)

    if not text:
        logger.info("🔇 未检测到语音")
        return False

    logger.info(f"🗣️ 用户说: '{text}'")

    decision = assistant.process_voice_command(text)
    expect_follow_up = decision.get("expect_follow_up", False)

    result = executor.execute_task_plan(decision)
    
    if result["success"]:
        ai_reply = str(result["message"])
        logger.info(f"✅ 操作成功: {result['operation']} -> {ai_reply}")
    else:
        error_msg = result["message"]
        ai_reply = f"抱歉，{error_msg if '抱歉' not in error_msg else error_msg[3:]}"
        logger.warning(f"❌ 执行失败: {error_msg}")

    # 🔁 动态设置下一次识别的等待策略
    if expect_follow_up:
        recognizer.current_timeout = 8
        logger.debug(f"🧠 AI 预期后续提问，已设置下次等待时间为 {recognizer.current_timeout}s")
    else:
        recognizer.current_timeout = 3
        logger.debug(f"🔚 AI 认为对话结束，已设置下次等待时间为 {recognizer.current_timeout}s")

    logger.info(f"🤖 回复: {ai_reply}")
    tts_engine.speak(ai_reply)

    return result.get("should_exit", False)

@log_step("启动 AI 语音助手")
@log_time
def main():
    global logger
    # ✅ 关键：先初始化日志系统
    logger = setup_logger(name="ai_assistant", level=logging.DEBUG)
    
    logger.info("🚀 正在启动 AI 语音助手系统...")

    run_api_server(host='127.0.0.1', port=5000)

    try:
        tts_engine.start()
        log_call("✅ 所有模块初始化完成，进入监听循环")

        log_call("\n" + "—" * 50)
        log_call("🎙️  语音助手已就绪")
        log_call("💡 说出你的命令，例如：'打开浏览器'、'写一篇春天的文章'")
        log_call("🛑 说出‘退出’、‘关闭’、‘停止’或‘拜拜’来结束程序")
        log_call("—" * 50 + "\n")

        while True:
            try:
                should_exit = handle_single_interaction()
                if should_exit:
                    break  # 退出主循环

            except KeyboardInterrupt:
                logger.info("🛑 用户主动中断 (Ctrl+C)")
                break
            except Exception as e:
                logger.exception("⚠️ 单次交互过程中发生异常，已降级处理")
                error_msg = "抱歉，我在处理刚才的操作时遇到了一点问题。"
                logger.info(f"🗣️ 回复: {error_msg}")
                tts_engine.speak(error_msg)

            time.sleep(0.5)

        # 清理资源
        tts_engine.stop()
        logger.info("👋 语音助手已安全退出")

    except KeyboardInterrupt:
        logger.info("🛑 用户通过 Ctrl+C 中断程序")
        print("\n👋 再见！")

    except Exception as e:
        logger.exception("❌ 主程序运行时发生未预期异常")
        print(f"\n🚨 程序异常终止：{e}")
        sys.exit(1)

# ========================
#   主入口 & 自检流程
# ========================
if __name__ == "__main__":
    # 1. 检查 Vosk 是否安装
    try:
        import vosk
        print(f"🔍 Vosk 安装路径: {vosk.__file__}")
    except ImportError as e:
        print(f"❌ 无法导入 vosk: {e}")
        sys.exit(1)

    # 2. 初始化日志器后进行健康检查
    logger = setup_logger(name="ai_assistant", level=logging.DEBUG)

    # 3. 启动主程序
    main()
