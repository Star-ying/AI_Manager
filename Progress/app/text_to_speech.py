import threading
import queue
import comtypes.client
from comtypes.gen import SpeechLib
import pyttsx3
from Progress.app.voice_recognizer import recognizer

class TextToSpeechEngine:
    def __init__(self):
        self.queue = queue.Queue()
        self._running = False
        self._thread = None
        self.speaker = None  # 只用于主线程占位或控制

    def start(self):
        """启动TTS引擎"""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()
        print("🔊 TTS 引擎已启动")

    def _worker(self):
        """工作线程：负责所有TTS操作"""
        print("🎧 TTS 工作线程运行中...")

        # ✅ 关键：在子线程中初始化 COM 并创建 speaker
        comtypes.CoInitialize()  # 初始化当前线程为单线程套间 (STA)
        try:
            self.speaker = comtypes.client.CreateObject("SAPI.SpVoice")
        except Exception as e:
            print(f"❌ 初始化 TTS 失败: {e}")
            comtypes.CoUninitialize()
            return

        while self._running:
            try:
                text = self.queue.get(timeout=1)
                if text is None:
                    break
                print(f"📢 正在播报: {text}")
                try:
                    self.speaker.Speak(text, SpeechLib.SVSFlagsAsync)
                except Exception as e:
                    print(f"🗣️ 播报失败: {e}")
                self.queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"❌ 处理任务时出错: {e}")

        # 清理
        self.speaker = None
        comtypes.CoUninitialize()  # 显式反初始化
        print("🔚 TTS 工作线程退出")

    def speak(self,text: str):
        # 通知语音识别器：我要开始说了
        recognizer.set_tts_playing(True)

        try:
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()  # 必须阻塞等待完成
        finally:
            # 说完后通知可以继续听
            recognizer.set_tts_playing(False)

    def stop(self):
        """安全关闭"""
        print("🔇 开始关闭 TTS 引擎...")
        self._running = False
        self.queue.put(None)  # 发送停止信号
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=3)
        print("✅ TTS 引擎已关闭")

tts_engine = TextToSpeechEngine()
tts_engine.start()

# if __name__ == "__main__":
#     tts_engine = TextToSpeechEngine()
#     tts_engine.start()

#     try:
#         tts_engine.speak("你好，我是AI助手。")
#         tts_engine.speak("这是第二次说话，应该能正常播放。")
#         tts_engine.speak("第三次测试，看看是不是还能响。")
#         time.sleep(10)  # 给足够时间完成所有语音
#     finally:
#         tts_engine.stop()
