import threading
import queue
import time
from typing import Optional
from Progress.utils.logger_config import setup_logger

logger = setup_logger("tts_engine")

class TextToSpeechEngine:
    def __init__(self):
        self._tts_queue = queue.Queue()
        self._stop_event = threading.Event()
        self._worker_thread: Optional[threading.Thread] = None
        self._is_playing = False
        self._lock = threading.Lock()  # 保护 _is_playing

    def start(self):
        if self._worker_thread is None:
            self._worker_thread = threading.Thread(target=self._playback_worker, daemon=True)
            self._worker_thread.start()
            logger.info("🎧 TTS 引擎已启动")

    def stop(self):
        self._stop_event.set()
        self._tts_queue.put(None)  # 唤醒线程
        if self._worker_thread:
            self._worker_thread.join(timeout=2)
        logger.info("🛑 TTS 引擎已停止")

    def speak(self, text: str, block: bool = False):
        if not text.strip():
            return

        with self._lock:
            if self._is_playing:
                logger.warning("🎙️ TTS 正在播放，跳过: %s", text[:50])
                return
            self._is_playing = True

        logger.info("📢 推送 TTS 文本: %s", text)
        self._tts_queue.put(text)
        if block:
            while self._is_playing and not self._stop_event.is_set():
                time.sleep(0.1)

    def _synthesize_and_play_audio(self, text: str):
        # 这里调用 pyttsx3 / edge-tts / vosk-tts 等
        try:
            # 示例：pyttsx3
            import pyttsx3
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()  # 同步播放完成
        except Exception as e:
            logger.error("❌ TTS 播放异常: %s", e)
            raise

    def _playback_worker(self):
        while not self._stop_event.is_set():
            try:
                text = self._tts_queue.get(timeout=1)
                if text is None:
                    break

                try:
                    logger.info("🔊 开始播放 TTS: %s", text[:60])
                    self._synthesize_and_play_audio(text)
                    logger.info("✅ TTS 播放完成")
                except Exception as e:
                    logger.error("💥 播放失败: %s", e)
                finally:
                    with self._lock:
                        self._is_playing = False  # ✅ 必须释放！

                self._tts_queue.task_done()
            except queue.Empty:
                continue
        logger.info("⏹️ TTS 工作线程退出")
    
    def is_playing(self) -> bool:
        with self._lock:
            return self._is_playing