# api_server.py
import threading
import time
from flask import Flask, request, jsonify
from werkzeug.serving import make_server
from flask_cors import CORS  # pip install flask-cors

# 假设这些函数来自你的主程序模块
# from Progress.app import get_ai_assistant, get_task_executor, get_tts_engine, get_voice_recognizer

# --- 全局状态共享 ---
current_status = {
    "is_listening": False,
    "is_tts_playing": False,
    "current_timeout": 8.0,
    "last_command_result": None,
    "timestamp": int(time.time())
}

# --- 模拟服务实例（实际项目中应替换为真实对象）---
class MockAssistant:
    def process_voice_command(self, text):
        return {"action": "mock_action", "target": text}

class MockExecutor:
    def execute_task_plan(self, plan):
        return {"success": True, "message": f"已执行 {plan['target']}", "data": {}}

class MockTTS:
    def speak(self, text, async_mode=False):
        print(f"[TTS] 正在播报: {text}")
        if not async_mode:
            time.sleep(1)  # 模拟播放延迟
        else:
            def _async_play():
                time.sleep(1)
            threading.Thread(target=_async_play, daemon=True).start()

class MockRecognizer:
    def start_listening(self):
        global current_status
        current_status["is_listening"] = True
        current_status["timestamp"] = int(time.time())
        print("🎙️ 开始监听用户语音...")

    def stop_listening(self):
        global current_status
        current_status["is_listening"] = False
        current_status["timestamp"] = int(time.time())

# 实例化模拟组件（上线时替换为真实导入）
assistant = MockAssistant()
executor = MockExecutor()
tts_engine = MockTTS()
recognizer = MockRecognizer()


class APIServer:
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)  # ✅ 启用跨域支持
        self.server = None
        self.thread = None
        self.running = False
        self._add_routes()

    def _update_status(self, **kwargs):
        """更新全局状态"""
        current_status.update(kwargs)
        current_status["timestamp"] = int(time.time())

    def _add_routes(self):
        """注册所有 API 路由"""

        # 1. GET /api/health - 健康检查
        @self.app.route('/api/health', methods=['GET'])
        def health():
            return jsonify({
                "status": "ok",
                "service": "ai_assistant",
                "timestamp": int(time.time())
            })

        # 2. GET /api/status - 查询当前状态
        @self.app.route('/api/status', methods=['GET'])
        def status():
            return jsonify({**current_status})

        # 3. POST /api/start - 启动助手
        @self.app.route('/api/start', methods=['POST'])
        def start():
            # 可以触发一些初始化逻辑
            self._update_status(is_listening=True)
            return jsonify({
                "status": "running",
                "message": "AI 助手已就绪",
                "features": ["voice", "tts", "file", "app_control"],
                "timestamp": int(time.time())
            })

        # 4. POST /api/command - 执行用户指令
        @self.app.route('/api/command', methods=['POST'])
        def handle_command():
            try:
                data = request.get_json()
                if not data or 'text' not in data:
                    return jsonify({
                        "success": False,
                        "response_to_user": "未收到有效指令"
                    }), 400

                text = data['text']
                context = data.get('context', {})
                options = data.get('options', {})
                should_speak = options.get('should_speak', True)
                return_plan = options.get('return_plan', False)

                print(f"📩 收到命令: '{text}' | 上下文: {context}")

                # 👇 调用 AI 助手核心逻辑（请替换为你的真实模块）
                # from Progress.app import get_ai_assistant, get_task_executor, get_tts_engine
                # assistant = get_ai_assistant()
                # executor = get_task_executor()
                # tts = get_tts_engine()

                decision = assistant.process_voice_command(text)
                result = executor.execute_task_plan(decision)

                ai_reply = result["message"]
                if not result["success"] and not ai_reply.startswith("抱歉"):
                    ai_reply = f"抱歉，{ai_reply}"

                # 更新状态：正在处理
                self._update_status(
                    is_processing=True,
                    last_command_result={"success": result["success"], "message": ai_reply, "operation": decision.get("action")}
                )

                # 异步播报
                if should_speak:
                    self._update_status(is_tts_playing=True)
                    tts_engine.speak(ai_reply, async_mode=True)
                    # 模拟 TTS 结束后恢复状态
                    def _finish_tts():
                        time.sleep(1)
                        self._update_status(is_tts_playing=False)
                    threading.Thread(target=_finish_tts, daemon=True).start()

                # 构造响应
                response_data = {
                    "success": result["success"],
                    "response_to_user": ai_reply,
                    "operation": decision.get("action"),
                    "details": result,
                    "should_speak": should_speak,
                    "timestamp": int(time.time()),
                }
                if return_plan:
                    response_data["plan"] = decision

                self._update_status(is_processing=False)
                return jsonify(response_data), 200

            except Exception as e:
                print(f"❌ 处理命令失败: {e}")
                return jsonify({
                    "success": False,
                    "error": str(e),
                    "timestamp": int(time.time())
                }), 500

        # 5. POST /api/tts/speak - 主动播报语音
        @self.app.route('/api/tts/speak', methods=['POST'])
        def speak():
            try:
                data = request.get_json()
                if not data or 'text' not in data:
                    return jsonify({"error": "Missing 'text'"}), 400

                text = data['text']
                print(f"[TTS] 请求播报: {text}")

                self._update_status(is_tts_playing=True)
                tts_engine.speak(text, async_mode=True)

                def _finish():
                    time.sleep(1)
                    self._update_status(is_tts_playing=False)

                threading.Thread(target=_finish, daemon=True).start()

                return jsonify({
                    "status": "speaking",
                    "text": text,
                    "timestamp": int(time.time())
                })
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        # 6. POST /api/wakeup - 远程唤醒
        @self.app.route('/api/wakeup', methods=['POST'])
        def wakeup():
            try:
                data = request.get_json() or {}
                device = data.get("device", "unknown")
                location = data.get("location", "unknown")

                print(f"🔔 远程唤醒信号来自 {device} @ {location}")

                # 播放提示音（可通过 pygame 或 winsound 实现）
                print("💡 滴—— 唤醒成功！")

                # 设置为倾听模式
                recognizer.start_listening()
                self._update_status(is_listening=True)

                return jsonify({
                    "status": "ready",
                    "message": "已进入倾听模式",
                    "timestamp": int(time.time())
                })
            except Exception as e:
                return jsonify({"error": str(e)}), 500

    def start(self, host="127.0.0.1", port=5000, debug=False):
        """启动 API 服务（非阻塞）"""
        if self.running:
            print("⚠️ API 服务器已在运行")
            return

        try:
            self.server = make_server(host, port, self.app)
            self.running = True

            def run_flask():
                print(f"🌐 AI 助手 API 已启动 → http://{host}:{port}/api")
                self.server.serve_forever()

            self.thread = threading.Thread(target=run_flask, daemon=True)
            self.thread.start()

        except Exception as e:
            print(f"❌ 启动 API 服务失败: {e}")
            raise

    def stop(self):
        """关闭 API 服务"""
        if not self.running:
            return

        print("🛑 正在关闭 API 服务...")
        try:
            self.server.shutdown()
        except:
            pass
        finally:
            self.running = False

        if self.thread:
            self.thread.join(timeout=3)
            if self.thread.is_alive():
                print("⚠️ API 服务线程未能及时退出")

        print("✅ API 服务已关闭")


# -----------------------------
# 使用示例
# -----------------------------
if __name__ == '__main__':
    api = APIServer()
    api.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        api.stop()
