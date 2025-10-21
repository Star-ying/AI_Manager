import time
from Progress.app.voice_recognizer import VoiceRecognizer
from Progress.app.qwen_assistant import QWENAssistant
from Progress.app.system_controller import SystemController, TaskOrchestrator
from Progress.app.text_to_speech import VoiceFeedback


def handle_response(resp, controller: SystemController, orchestrator: TaskOrchestrator, speaker: VoiceFeedback):
    intent = resp.get("intent", "chat")
    action = resp.get("action", "reply")
    params = resp.get("parameters", {})
    reply = resp.get("response", "")

    if intent == "music":
        task = {"type": "music", "parameters": {"action": action}}
        result = orchestrator.execute_task_sequence([task])[0]
        speaker.speak_response(result["message"] if isinstance(result["message"], str) else reply)
    elif intent == "file":
        task = {"type": "file", "parameters": {"action": action, **params}}
        result = orchestrator.execute_task_sequence([task])[0]
        msg = result["message"]
        speaker.speak_response(msg if isinstance(msg, str) else reply)
    elif intent == "text":
        task = {"type": "text", "parameters": {"action": action, **params}}
        result = orchestrator.execute_task_sequence([task])[0]
        msg = result["message"]
        if isinstance(msg, str):
            print("\n=== 生成文本 ===\n" + msg + "\n================")
            speaker.speak_response("已生成文本")
        else:
            speaker.speak_response(reply)
    elif intent == "system":
        task = {"type": "system", "parameters": {"action": action, **params}}
        result = orchestrator.execute_task_sequence([task])[0]
        msg = result["message"]
        if isinstance(msg, dict):
            for k, v in msg.items():
                print(f"{k}: {v}")
            speaker.speak_response("系统信息已显示在终端")
        else:
            speaker.speak_response(msg if isinstance(msg, str) else reply)
    else:
        # 普通对话
        speaker.speak_response(reply)

def main():
    recognizer = VoiceRecognizer()
    assistant = QWENAssistant()
    controller = SystemController()
    orchestrator = TaskOrchestrator(controller, assistant)
    speaker = VoiceFeedback()

    print("语音控制AI助手已启动。说 '退出' 结束对话。")

    try:
        while True:
            text = recognizer.recognize_once()
            if not text:
                continue
            print(f"你说：{text}")

            if text.strip() in ("退出", "结束", "拜拜"):
                speaker.speak_response("好的，下次见。")
                break

            resp = assistant.process_voice_command(text)
            handle_response(resp, controller, orchestrator, speaker)

            time.sleep(0.1)

    except KeyboardInterrupt:
        pass
    finally:
        speaker.tts.cleanup()

if __name__ == "__main__":
    main()
    """#—————— 设置信息获取示例 ——————
    # 加载配置
    config = setting.load_config()
    print("当前配置：")
    print(json.dumps(config, indent=2, ensure_ascii=False))

    # 示例：修改快捷键
    config.update_shortcut("save", "Ctrl+Shift+S")

    # 示例：更改资源路径
    config.set_resource_path("./my_resources")

    # 示例：查看显示设置
    display = config.get_display_settings()
    print("当前显示设置:", display) """

    """# 获取 AI_model 配置
    api_key = config.get("ai_model", "api_key")
    model = config.get("ai_model", "model")

    # 获取语音识别设置
    lang = config.get("voice_recognition", "language")
    timeout = config.get("voice_recognition", "timeout")
    phrase_timeout = config.get("voice_recognition","phrase_timeout")

    # 获取 TTS 设置
    rate = config.get("tts", "rate")
    volume = config.get("tts", "volume")

    # 获取路径
    resource_path = config.get("paths","resource_path")
    music_path = config.get("paths", "default_music_path")
    doc_path = config.get("paths", "default_document_path")

    # 获取应用信息
    app_name = config.get("app", "name")
    app_version = config.get("app", "version") """