"""
离线语音识别模块（基于 Vosk）
支持防自反馈机制：当 TTS 播放时不监听
"""

import threading
import time
import logging
import json
import os
from vosk import Model, KaldiRecognizer
import pyaudio

from Progress.app import get_tts_engine
from database.config import config
from Progress.utils.logger_config import setup_logger
from Progress.utils.resource_helper import get_internal_path

logger = logging.getLogger("ai_assistant")

VOSK_MODEL_PATH = get_internal_path("models", "vosk-model-small-cn-0.22")

# 全局实例（供 TTS 调用）
recognizer = None

class SpeechRecognizer:
    def __init__(self, tts_engine):
        global recognizer
        recognizer = self  # 自注册为全局对象

        self.model = None
        self.audio = None
        self.tts_engine = tts_engine
        self._is_tts_playing = False
        self._tts_lock = threading.Lock()

        self.sample_rate = 16000
        self.chunk_size = 1600

        self._current_timeout = config.get("voice_recognition", "timeout", "initial")
        self._min_volume_threshold = config.get("voice_recognition", "volume_threshold", "base")
        self._post_speech_short_wait = config.get("voice_recognition", "post_speech_short_wait", "value")
        self._post_speech_long_wait = config.get("voice_recognition", "post_speech_long_wait", "value")
        self.long_speech_threshold = config.get("voice_recognition", "long_speech_threshold", "value")

        self._load_model()
        self._init_audio_system()
        logger.info("✅ 语音识别器初始化完成")

    @property
    def current_timeout(self):
        return self._current_timeout

    @current_timeout.setter
    def current_timeout(self, value):
        min_val = config.get("voice_recognition", "timeout", "min")
        max_val = config.get("voice_recognition", "timeout", "max")
        old = self._current_timeout
        self._current_timeout = max(min_val, min(max_val, float(value)))
        logger.debug(f"⏱️ 监听超时: {old:.1f} → {self._current_timeout:.1f}s")

    @property
    def is_tts_playing(self):
        with self._tts_lock:
            return self._is_tts_playing

    def set_tts_playing(self, status: bool):
        with self._tts_lock:
            self._is_tts_playing = status
        if not status:
            logger.debug("🟢 TTS 结束，恢复监听")

    def _load_model(self):
        if not os.path.exists(VOSK_MODEL_PATH):
            raise FileNotFoundError(f"模型路径不存在: {VOSK_MODEL_PATH}")
        self.model = Model(VOSK_MODEL_PATH)
        logger.info("✅ Vosk 模型加载成功")

    def _init_audio_system(self):
        try:
            self.audio = pyaudio.PyAudio()
            logger.debug("✅ PyAudio 初始化完成")
        except Exception as e:
            logger.exception("❌ 初始化音频系统失败")
            raise

    def listen_and_recognize(self, timeout=None) -> str:
        use_timeout = timeout or self.current_timeout
        min_t = config.get("voice_recognition", "timeout", "min")
        max_t = config.get("voice_recognition", "timeout", "max")
        use_timeout = max(min_t, min(max_t, float(use_timeout)))

        if self.tts_engine.is_playing():
            logger.info("🔇 TTS 正在播放，跳过本次语音识别")
            return None
        
        stream = None
        try:
            _recognizer = KaldiRecognizer(self.model, self.sample_rate)
            stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )

            start_time = time.time()
            in_speech = False
            result_text = ""

            logger.info("🎙️ 请说话...")

            while (time.time() - start_time) < use_timeout:
                if self.is_tts_playing:
                    logger.info("🔇 TTS 开始播放，中断识别")
                    break

                data = stream.read(self.chunk_size, exception_on_overflow=False)

                if _recognizer.AcceptWaveform(data):
                    final_result = json.loads(_recognizer.Result())
                    text = final_result.get("text", "").strip()
                    if text:
                        result_text = text
                        break
                else:
                    partial = json.loads(_recognizer.PartialResult())
                    if partial.get("partial", "").strip():
                        in_speech = True

            return result_text

        except Exception as e:
            logger.exception("🔴 识别异常")
            return ""
        finally:
            if stream:
                try:
                    stream.stop_stream()
                    stream.close()
                except:
                    pass
