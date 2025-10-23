"""
【语音识别模块】Speech Recognition (Offline)
使用麦克风进行实时语音识别，基于 Vosk 离线模型
支持单次识别 & 持续监听模式
音量可视化、模型路径检查、资源安全释放
"""
import threading
import time
import logging
import json
import os
from vosk import Model, KaldiRecognizer
import pyaudio

from database import config
from Progress.utils.logger_utils import log_time, log_step, log_var, log_call
from Progress.utils.logger_config import setup_logger

# --- 配置参数 ---
VOICE_TIMEOUT = config.timeout  # 最大等待语音输入时间（秒）
VOICE_PHRASE_TIMEOUT = config.phrase_timeout  # 单句话最长录音时间
VOSK_MODEL_PATH = "./vosk-model-small-cn-0.22"

# --- 初始化日志器 ---
logger = logging.getLogger("ai_assistant")
# 定义最小有效音量阈值
MIN_VOLUME_THRESHOLD = 600  # 可调（根据环境测试）


class SpeechRecognizer:
    def __init__(self):
        self.model = None
        self.recognizer = None
        self.audio = None
        self.is_listening = False
        self.callback = None  # 用户注册的回调函数：callback(text)
        self._last_text = ""
        self._listen_thread = None

        self.sample_rate = 16000  # Vosk 要求采样率 16kHz
        self.chunk_size = 1600     # 推荐帧大小（对应 ~100ms）

        # 🔒 TTS 播放状态标志（由外部控制）
        self._is_tts_playing = False
        self._tts_lock = threading.Lock()

        self._load_model()
        self._init_audio_system()

    @property
    def is_tts_playing(self) -> bool:
        with self._tts_lock:
            return self._is_tts_playing

    def set_tts_playing(self, status: bool):
        """供 TTS 模块调用：通知当前是否正在播放"""
        with self._tts_lock:
            self._is_tts_playing = status
        if not status:
            logger.debug("🟢 TTS 播放结束，语音识别恢复")

    @log_step("加载 Vosk 离线模型")
    @log_time
    def _load_model(self):
        """加载本地 Vosk 模型"""
        if not os.path.exists(VOSK_MODEL_PATH):
            raise FileNotFoundError(f"❌ Vosk 模型路径不存在: {VOSK_MODEL_PATH}\n","请从 https://alphacephei.com/vosk/models 下载中文小模型并解压至此路径")

        try:
            logger.info(f"📦 正在加载模型: {VOSK_MODEL_PATH}")
            self.model = Model(VOSK_MODEL_PATH)
            log_call("✅ 模型加载成功")
        except Exception as e:
            logger.critical(f"🔴 加载 Vosk 模型失败: {e}")
            raise RuntimeError("Failed to load Vosk model") from e

    @log_step("初始化音频系统")
    @log_time
    def _init_audio_system(self):
        """初始化 PyAudio 并创建全局 recognizer"""
        try:
            self.audio = pyaudio.PyAudio()
            # 创建默认识别器（可在每次识别前 Reset）
            self.recognizer = KaldiRecognizer(self.model, self.sample_rate)
            logger.debug("✅ 音频系统初始化完成")
        except Exception as e:
            logger.exception("❌ 初始化音频系统失败")
            raise

    @property
    def last_text(self) -> str:
        return self._last_text

    def is_available(self) -> bool:
        """检查麦克风是否可用"""
        if not self.audio:
            return False
        try:
            stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            stream.close()
            return True
        except Exception as e:
            logger.error(f"🔴 麦克风不可用或无权限: {e}")
            return False

    @log_step("执行单次语音识别")
    @log_time
    def listen_and_recognize(self, timeout=None) -> str:
        timeout = timeout or VOICE_TIMEOUT
        start_time = time.time()
        in_speech = False
        result_text = ""

        logger.debug(f"🎙️ 开始单次语音识别 (timeout={timeout:.1f}s)...")

        # 🔴 如果正在播放 TTS，直接返回空
        if self.is_tts_playing:
            logger.info("🔇 TTS 正在播放，跳过本次识别")
            return ""

        logger.info("🔊 请说话...")

        stream = None
        try:
            recognizer = KaldiRecognizer(self.model, self.sample_rate)

            stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )

            while (time.time() - start_time) < timeout:
                # 再次检查播放状态（可能中途开始）
                if self.is_tts_playing:
                    logger.info("🔇 TTS 开始播放，中断识别")
                    break

                data = stream.read(self.chunk_size, exception_on_overflow=False)

                if recognizer.AcceptWaveform(data):
                    final_result = json.loads(recognizer.Result())
                    text = final_result.get("text", "").strip()
                    if text:
                        result_text = text
                        break
                else:
                    partial = json.loads(recognizer.PartialResult())
                    if partial.get("partial", "").strip():
                        in_speech = True

                if not in_speech and (time.time() - start_time) >= timeout:
                    logger.info("💤 超时未检测到语音输入")
                    break

            if result_text:
                self._last_text = result_text
                logger.info(f"🎯 识别结果: '{result_text}'")
                return result_text
            else:
                logger.info("❓ 未识别到有效内容")
                self._last_text = ""
                return ""

        except Exception as e:
            logger.exception("🔴 执行单次语音识别时发生异常")
            self._last_text = ""
            return ""
        finally:
            if stream:
                try:
                    stream.stop_stream()
                    stream.close()
                except Exception as e:
                    logger.warning(f"⚠️ 关闭音频流失败: {e}")

    @log_step("启动持续语音监听")
    def start_listening(self, callback=None, language=None):
        """
        启动后台线程持续监听语音输入
        :param callback: 回调函数，接受一个字符串参数 text
        :param language: 语言代码（忽略，由模型决定）
        """
        if self.is_listening:
            logger.warning("⚠️ 已在监听中，忽略重复启动")
            return

        if not callable(callback):
            logger.error("🔴 回调函数无效，请传入可调用对象")
            return

        self.callback = callback
        self.is_listening = True

        self._listen_thread = threading.Thread(target=self._background_listen, args=(language,), daemon=True)
        self._listen_thread.start()
        logger.info("🟢 已启动后台语音监听")

    @log_step("停止语音监听")
    def stop_listening(self):
        """安全停止后台监听"""
        if not self.is_listening:
            return

        self.is_listening = False
        logger.info("🛑 正在停止语音监听...")

        if self._listen_thread and self._listen_thread != threading.current_thread():
            self._listen_thread.join(timeout=3)
            if self._listen_thread.is_alive():
                logger.warning("🟡 监听线程未能及时退出（可能阻塞）")
        elif self._listen_thread == threading.current_thread():
            logger.error("❌ 无法在当前线程中 join 自己！请检查调用栈")
        else:
            logger.debug("No thread to join")

        logger.info("✅ 语音监听已停止")

    def _background_listen(self, language=None):
        """后台循环监听线程"""
        logger.debug("🎧 后台监听线程已启动")

        stream = None
        try:
            stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
        except Exception as e:
            logger.error(f"🔴 无法打开音频流: {e}")
            return

        try:
            while self.is_listening:
                # 🔴 检查是否正处于 TTS 播放中 → 跳过本次读取
                if self.is_tts_playing:
                    time.sleep(0.1)  # 减少 CPU 占用
                    continue

                try:
                    data = stream.read(self.chunk_size, exception_on_overflow=False)

                    if self.recognizer.AcceptWaveform(data):
                        result_json = self.recognizer.Result()
                        result_dict = json.loads(result_json)
                        text = result_dict.get("text", "").strip()
                        if text and self.callback:
                            logger.info(f"🔔 回调触发: '{text}'")
                            self.callback(text)
                        self.recognizer.Reset()
                    else:
                        partial = json.loads(self.recognizer.PartialResult())
                        partial_text = partial.get("partial", "")
                        if partial_text.strip():
                            logger.debug(f"🗣️ 当前语音片段: '{partial_text}'")

                except Exception as e:
                    logger.exception("Background listening error")
                time.sleep(0.05)

        finally:
            if stream:
                stream.stop_stream()
                stream.close()
            logger.debug("🔚 后台监听线程退出")



recognizer = SpeechRecognizer()
