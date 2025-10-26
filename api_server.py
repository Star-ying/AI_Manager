"""
【AI 助手】HTTP API 服务
基于 Flask 实现语音控制、状态查询、远程唤醒等功能
✅ 自动依赖注入 | ✅ API Key 认证 | ✅ 异步执行 | ✅ 安全退出
"""

import threading
import time
from typing import Callable, Any, Dict, Optional
from functools import wraps

from flask import Flask, request, jsonify, Response
from werkzeug.serving import make_server

from database.config import config
from Progress.app import (
    get_ai_assistant,
    get_task_executor,
    get_tts_engine,
    get_voice_recognizer,
)
from Progress.utils.logger_config import setup_logger

logger = setup_logger("api_server")


def require_api_key(f: Callable) -> Callable:
    """装饰器：API 密钥认证"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not config.get("security", "enable_api_key", fallback=False):
            return f(*args, **kwargs)

        auth = request.headers.get("Authorization")
        expected_key = config.get("security", "api_key")

        if not auth or not auth.startswith("Bearer ") or auth.split()[1] != expected_key:
            return jsonify({"error": "Unauthorized: Invalid or missing API key"}), 401
        return f(*args, **kwargs)
    return decorated


class APIServer:
    def __init__(self):
        self.app = Flask(__name__)
        self.server = None
        self.thread = None
        self.running = False
        self._setup_routes()
        self.last_result = None

    def _setup_routes(self):
        """定义所有 API 路由"""
        app = self.app

        # ========================
        # 🔹 GET /api/health - 健康检查
        # ========================
        @app.route('/api/health', methods=['GET'])
        def health():
            return jsonify({
                "status": "ok",
                "service": "ai_voice_assistant_api",
                "timestamp": int(time.time())
            })

        # ========================
        # 🔹 GET /api/status - 当前状态
        # ========================
        @app.route('/api/status', methods=['GET'])
        @require_api_key
        def get_status():
            try:
                recognizer = get_voice_recognizer()
                last_result = getattr(self, 'last_result', {
                    "success": True,
                    "message": "等待指令...",
                    "operation": "idle"
                })
                return jsonify({
                    "status": "running",
                    "is_tts_playing": recognizer.is_tts_playing,
                    "is_listening": True,
                    "current_timeout": recognizer.current_timeout,
                    "last_command_result": last_result,
                    "timestamp": int(time.time())
                })
            except Exception as e:
                logger.error(f"获取状态失败: {e}")
                return jsonify({"error": "Internal Server Error"}), 500

        # ========================
        # 🔹 POST /api/command - 发送自然语言指令
        # ========================
        @app.route('/api/command', methods=['POST'])
        @require_api_key
        def handle_command():
            data = request.get_json()
            if not data:
                return jsonify({"error": "请求体为空"}), 400

            text = data.get("text", "").strip()
            if not text:
                return jsonify({"error": "缺少 'text' 字段"}), 400

            context = data.get("context", {})
            should_speak = data.get("options", {}).get("should_speak", True)

            logger.info(f"🗣️ [API] 收到命令: '{text}' | 设备: {context.get('device')}")

            try:
                assistant = get_ai_assistant()
                executor = get_task_executor()
                tts_engine = get_tts_engine()
                recognizer = get_voice_recognizer()

                decision = assistant.process_voice_command(text)
                expect_follow_up = decision.get("expect_follow_up", False)

                result = executor.execute_task_plan(decision)

                # 更新最后结果
                last_result = {
                    "success": result["success"],
                    "message": result["message"],
                    "operation": result.get("operation", "unknown")
                }
                self.last_result = last_result  # 存储为实例属性

                ai_reply = result["message"]
                if not result["success"] and not ai_reply.startswith("抱歉"):
                    ai_reply = f"抱歉，{ai_reply}"

                # 异步播报
                def speak_later():
                    time.sleep(0.3)
                    if should_speak:
                        try:
                            tts_engine.speak(ai_reply,True)
                        except Exception as e:
                            logger.warning(f"TTS 播报失败: {e}")

                threading.Thread(target=speak_later, daemon=True).start()

                # 动态设置下次监听时间
                recognizer.current_timeout = 8 if expect_follow_up else 3

                return jsonify({
                    "success": result["success"],
                    "response_to_user": ai_reply,
                    "expect_follow_up": expect_follow_up,
                    "current_timeout": recognizer.current_timeout,
                    "execution_result": result,
                    "plan": decision,
                    "timestamp": int(time.time())
                })

            except Exception as e:
                logger.exception("❌ 执行命令出错")
                return jsonify({
                    "success": False,
                    "response_to_user": "抱歉，处理请求时发生错误。",
                    "error": str(e),
                    "timestamp": int(time.time())
                }), 500

        # ========================
        # 🔹 POST /api/tts_speak - 文本转语音播报
        # ========================
        @app.route('/api/tts_speak', methods=['POST'])
        @require_api_key
        def api_tts_speak():
            data = request.get_json()
            text = data.get("text", "").strip() if data else ""
            if not text:
                return jsonify({"error": "缺少 'text' 字段"}), 400

            def _speak():
                try:
                    tts_engine = get_tts_engine()
                    tts_engine.speak(text)
                except Exception as e:
                    logger.error(f"🔊 TTS 播报失败: {e}")

            threading.Thread(target=_speak, daemon=True).start()

            return jsonify({
                "status": "speaking",
                "text": text,
                "timestamp": int(time.time())
            })

        # ========================
        # 🔹 POST /api/wakeup - 远程唤醒
        # ========================
        @app.route('/api/wakeup', methods=['POST'])
        @require_api_key
        def wakeup():
            try:
                recognizer = get_voice_recognizer()
                # 可以触发一次 listen，或者仅标记状态
                logger.info("🟢 收到远程唤醒信号")
                return jsonify({
                    "status": "awake",
                    "message": "助手已唤醒",
                    "timestamp": int(time.time())
                })
            except Exception as e:
                logger.error(f"唤醒失败: {e}")
                return jsonify({"error": "Wake-up failed"}), 500

    def start(self, host: str = None, port: int = None, debug: bool = False):
        """
        启动 API 服务（非阻塞）
        """
        if self.running:
            logger.warning("⚠️ API 服务器已在运行")
            return

        host = host or config.get("api", "host", fallback="127.0.0.1")
        port = port or config.get("api", "port", fallback=5000)
        debug = debug or config.get("api", "debug", fallback=False)

        try:
            self.server = make_server(host, port, self.app)
            self.running = True

            def run_flask():
                logger.info(f"🌐 API 服务启动在 http://{host}:{port}/")
                self.server.serve_forever()

            self.thread = threading.Thread(target=run_flask, daemon=True)
            self.thread.start()

        except Exception as e:
            logger.critical(f"❌ 启动 API 服务失败: {e}")
            raise

    def stop(self):
        """安全关闭 API 服务"""
        if not self.running:
            return

        logger.info("🛑 正在关闭 API 服务...")
        self.running = False

        if self.server:
            self.server.shutdown()
            self.server = None

        if self.thread:
            self.thread.join(timeout=3)
            logger.debug("✅ API 服务线程已停止")

    @property
    def is_running(self) -> bool:
        return self.running


# --- 全局单例 ---
_api_server = None


def get_api_server() -> APIServer:
    """获取唯一的 API 服务器实例"""
    global _api_server
    if _api_server is None:
        _api_server = APIServer()
    return _api_server
