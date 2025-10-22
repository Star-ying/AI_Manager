"""
【语音合成模块】Text-to-Speech (TTS)
将文本转换为语音输出，支持中断、队列和多语音切换
"""
import pyttsx3
import threading
import queue
import logging

from database import config
from Progress.utils.logger_utils import log_time, log_step, log_var, log_call
from Progress.utils.logger_config import setup_logger

TTS_RATE = config.rate
TTS_VOLUME = config.volume

logger = logging.getLogger("ai_assistant")


class TTSEngine:
    def __init__(self):
        self.engine = None
        self.is_speaking = False
        self.speech_queue = queue.Queue()
        self.speech_thread = None
        self.stop_speaking = False
        self._initialize_engine()

    @log_step("初始化语音合成引擎")
    @log_time
    def _initialize_engine(self):
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', TTS_RATE)
            self.engine.setProperty('volume', TTS_VOLUME)

            voices = self.engine.getProperty('voices')
            selected_voice = next((v for v in voices if any(kw in v.name.lower() for kw in ['chinese', 'zh'])), None)
            if selected_voice:
                self.engine.setProperty('voice', selected_voice.id)
                log_call(f"已选择中文语音: {selected_voice.name}")
            elif voices:
                self.engine.setProperty('voice', voices[0].id)

            logger.info("✅ 语音合成引擎初始化成功")
        except Exception as e:
            logger.exception("❌ 语音合成引擎初始化失败")
            self.engine = None

    @log_time
    def speak(self, text, interrupt=True):
        if not self.is_available() or not text.strip():
            return False

        cleaned = text.strip()
        if interrupt:
            self.stop_current_speech()

        self.speech_queue.put(cleaned)
        if not self.speech_thread or not self.speech_thread.is_alive():
            self.speech_thread = threading.Thread(target=self._speech_worker, daemon=True)
            self.speech_thread.start()

        return True

    @log_time
    def _speech_worker(self):
        while not self.stop_speaking:
            try:
                text = self.speech_queue.get(timeout=1.0)
                if text is None:
                    break
                self.is_speaking = True
                self.engine.say(text)
                self.engine.runAndWait()
                self.is_speaking = False
                self.speech_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                logger.exception("❌ 语音工作线程异常")
                self.is_speaking = False

    @log_time
    def stop_current_speech(self):
        try:
            if self.is_speaking and self.engine:
                self.engine.stop()
                self.is_speaking = False
            while not self.speech_queue.empty():
                self.speech_queue.get_nowait()
                self.speech_queue.task_done()
        except Exception as e:
            logger.exception("❌ 停止语音失败")

    def is_available(self):
        return self.engine is not None
