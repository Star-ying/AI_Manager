# api_server.py
from flask import Flask, request, jsonify
import threading
import time

from database.config import config

def create_api_server():
    """
    工厂函数：创建 Flask 应用实例
    返回: (app, init_dependencies)
    """
    app = Flask(__name__)

    # --- 核心组件占位符 ---
    assistant = None
    executor = None
    tts_engine = None
    recognizer = None

    def init_dependencies(ass, exec, tts, rec):
        nonlocal assistant, executor, tts_engine, recognizer
        assistant = ass
        executor = exec
        tts_engine = tts
        recognizer = rec
        print("✅ API 服务已注入核心模块")

    last_result = {"success": True, "message": "等待指令...", "operation": "idle"}
    
    # --- 装饰器：API 密钥认证 ---
    def require_api_key(f):
        from functools import wraps
        @wraps(f)
        def decorated(*args, **kwargs):
            if not config.get("security", "enable_api_key"):
                return f(*args, **kwargs)

            auth = request.headers.get("Authorization")
            expected_key = config.get("security", "api_key")

            if not auth or not auth.startswith("Bearer ") or auth.split()[1] != expected_key:
                return jsonify({"error": "Unauthorized: Invalid or missing API key"}), 401
            return f(*args, **kwargs)
        return decorated

    # ========================
    # 🔹 GET /api/health
    # ========================
    @app.route('/api/health', methods=['GET'])
    def health():
        return jsonify({
            "status": "ok",
            "service": "ai_voice_assistant",
            "timestamp": int(time.time())
        })

    # ========================
    # 🔹 GET /api/status
    # ========================
    @app.route('/api/status', methods=['GET'])
    def get_status():
        if not recognizer:
            return jsonify({"error": "未初始化"}), 500
        return jsonify({
            "status": "running",
            "is_tts_playing": recognizer.is_tts_playing,
            "is_listening": True,
            "current_timeout": recognizer.current_timeout,
            "last_command_result": last_result,
            "timestamp": int(time.time())
        })

    # ========================
    # 🔹 POST /api/start
    # ========================
    @app.route('/api/start', methods=['POST'])
    def start():
        return jsonify({
            "status": "ready",
            "message": "AI 助手服务已启动",
            "features": ["voice", "tts", "file", "app_control", "music"],
            "timestamp": int(time.time())
        })

    # ========================
    # 🔹 POST /api/command
    # ========================
    @app.route('/api/command', methods=['POST'])
    def handle_command():
        nonlocal last_result

        if not all([assistant, executor, tts_engine, recognizer]):
            return jsonify({"error": "依赖未初始化"}), 500

        data = request.get_json()
        if not data:
            return jsonify({"error": "请求体为空"}), 400

        text = data.get("text", "").strip()
        if not text:
            return jsonify({"error": "缺少 'text' 字段"}), 400

        context = data.get("context", {})
        should_speak = data.get("options", {}).get("should_speak", True)

        print(f"🗣️ [API] 收到命令: '{text}' | 设备: {context.get('device')}")

        try:
            decision = assistant.process_voice_command(text)
            expect_follow_up = decision.get("expect_follow_up", False)

            result = executor.execute_task_plan(decision)

            # 更新最后结果
            last_result = {
                "success": result["success"],
                "message": result["message"],
                "operation": result.get("operation", "unknown")
            }

            ai_reply = result["message"]
            if not result["success"] and not ai_reply.startswith("抱歉"):
                ai_reply = f"抱歉，{ai_reply}"

            # 异步播报
            def speak_later():
                time.sleep(0.3)
                if should_speak:
                    tts_engine.speak(ai_reply)

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
            print(f"❌ [API] 执行命令出错: {e}")
            return jsonify({
                "success": False,
                "response_to_user": "抱歉，处理请求时发生错误。",
                "error": str(e),
                "timestamp": int(time.time())
            }), 500

    # ========================
    # 🔹 POST /api/tts_speak
    # ========================
    @app.route('/api/tts_speak', methods=['POST'])
    def api_tts_speak():
        if not tts_engine:
            return jsonify({"error": "TTS 引擎未就绪"}), 500

        data = request.get_json()
        text = data.get("text", "").strip() if data else ""
        if not text:
            return jsonify({"error": "缺少 'text' 字段"}), 400

        def _speak():
            try:
                tts_engine.speak(text)
            except Exception as e:
                print(f"🔊 TTS 播报失败: {e}")

        threading.Thread(target=_speak, daemon=True).start()

        return jsonify({
            "status": "speaking",
            "text": text,
            "timestamp": int(time.time())
        })

    # ========================
    # 🔹 POST /api/wakeup
    # ========================
    @app.route('/api/wakeup', methods=['POST'])
    def wakeup():
        if not recognizer:
            return jsonify({"error": "语音识别器未初始化"}), 500
        recognizer.is_listening = True
        print("🟢 收到远程唤醒信号")
        return jsonify({
            "status": "awake",
            "message": "助手已唤醒",
            "timestamp": int(time.time())
        })

    return app, init_dependencies
