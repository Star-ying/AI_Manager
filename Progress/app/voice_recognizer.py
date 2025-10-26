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
from typing import Any, Dict
from vosk import Model, KaldiRecognizer
import pyaudio

from database.config import config
from Progress.utils.logger_utils import log_time, log_step, log_var, log_call
from Progress.utils.logger_config import setup_logger
from Progress.utils.resource_helper import get_internal_path

VOSK_MODEL_PATH = get_internal_path("models", "vosk-model-small-cn-0.22")

# --- 初始化日志器 ---
logger = logging.getLogger("ai_assistant")

class SpeechRecognizer:
    def __init__(self):
        # === Step 1: 初始化所有字段（避免 AttributeError）===
        self.model = None
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

        # 配置相关
        self._raw_config: Dict[str, Any] = {}
        self._voice_cfg = None  # 先设为 None，等 _load_config 后赋值

        # === Step 2: 初始化参数（这些值来自 JSON，并受边界保护）===
        self._current_timeout =config.get("voice_recognition","timeout","initial")
        self._min_volume_threshold = config.get("voice_recognition","volume_threshold","base")
        self._post_speech_short_wait = config.get("voice_recognition","post_speech_short_wait","value")
        self._post_speech_long_wait = config.get("voice_recognition","post_speech_long_wait","value")
        self.long_speech_threshold = config.get("voice_recognition","long_speech_threshold","value")

        # === Step 3: 初始化外部资源（依赖配置和路径）===
        self._load_model()
        self._init_audio_system()

        # === Step 4: 日志输出 ===
        logger.info("✅ 语音识别器初始化完成")
        self._log_current_settings()

    # --- current_timeout 带边界 ---
    @property
    def current_timeout(self) -> float:
        return self._current_timeout

    @current_timeout.setter
    def current_timeout(self, value: float):
        old = self._current_timeout
        min_val = config.get("voice_recognition","timeout","min")
        max_val = config.get("voice_recognition","timeout","max")

        if value < min_val:
            self._current_timeout = min_val
            logger.warning(f"⏱️ 超时时间 {value}s 过短 → 已限制为最小值 {min_val}s")
        elif value > max_val:
            self._current_timeout = max_val
            logger.warning(f"⏱️ 超时时间 {value}s 过长 → 已限制为最大值 {max_val}s")
        else:
            self._current_timeout = float(value)

        logger.debug(f"🔊 监听超时更新: {old:.1f} → {self._current_timeout:.1f}s")

    # --- volume threshold ---
    @property
    def min_volume_threshold(self) -> int:
        return self._min_volume_threshold

    @min_volume_threshold.setter
    def min_volume_threshold(self, value: int):
        old = self._min_volume_threshold
        min_val = config.get("voice_recognition","volume_threshold","min")
        max_val = config.get("voice_recognition","volume_threshold","max")

        if value < min_val:
            self._min_volume_threshold = min_val
            logger.warning(f"🎚️ 音量阈值 {value} 过低 → 已修正为 {min_val}")
        elif value > max_val:
            self._min_volume_threshold = max_val
            logger.warning(f"🎚️ 音量阈值 {value} 过高 → 已修正为 {max_val}")
        else:
            self._min_volume_threshold = int(value)

        logger.debug(f"🎤 音量阈值更新: {old} → {self._min_volume_threshold}")

    # --- post speech short wait ---
    @property
    def post_speech_short_wait(self) -> float:
        return self._post_speech_short_wait

    @post_speech_short_wait.setter
    def post_speech_short_wait(self, value: float):
        old = self._post_speech_short_wait
        min_val = config.get("voice_recognition","post_speech_short_wait","min")
        max_val = config.get("voice_recognition","post_speech_short_wait","max")

        if value < min_val:
            self._post_speech_short_wait = min_val
            logger.warning(f"⏸️ 短句等待 {value}s 太短 → 改为 {min_val}s")
        elif value > max_val:
            self._post_speech_short_wait = max_val
            logger.warning(f"⏸️ 短句等待 {value}s 太长 → 改为 {max_val}s")
        else:
            self._post_speech_short_wait = float(value)

        logger.debug(f"⏳ 短句静默等待: {old:.1f} → {self._post_speech_short_wait:.1f}s")

    # --- post speech long wait ---
    @property
    def post_speech_long_wait(self) -> float:
        return self._post_speech_long_wait

    @post_speech_long_wait.setter
    def post_speech_long_wait(self, value: float):
        old = self._post_speech_long_wait
        min_val = config.get("voice_recognition","post_speech_long_wait","min")
        max_val = config.get("voice_recognition","post_speech_long_wait","max")

        if value < min_val:
            self._post_speech_long_wait = min_val
            logger.warning(f"⏸️ 长句等待 {value}s 太短 → 改为 {min_val}s")
        elif value > max_val:
            self._post_speech_long_wait = max_val
            logger.warning(f"⏸️ 长句等待 {value}s 太长 → 改为 {max_val}s")
        else:
            self._post_speech_long_wait = float(value)

        logger.debug(f"⏳ 长句静默等待: {old:.1f} → {self._post_speech_long_wait:.1f}s")

    def _log_current_settings(self):
        logger.info("🔧 当前语音识别参数:")
        logger.info(f"   - 初始超时: {self.current_timeout}s")
        logger.info(f"   - 音量阈值: {self.min_volume_threshold}")
        logger.info(f"   - 短句等待: {self.post_speech_short_wait}s")
        logger.info(f"   - 长句等待: {self.post_speech_long_wait}s")
        logger.info(f"   - 长句阈值: {self.long_speech_threshold}s")

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
        """初始化 PyAudio 并创建全局 _recognizer"""
        try:
            self.audio = pyaudio.PyAudio()
            # 创建默认识别器（可在每次识别前 Reset）
            self._recognizer = KaldiRecognizer(self.model, self.sample_rate)
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
        """
        执行一次语音识别，支持外部指定超时时间。
        若未指定，则使用 self.current_timeout（受最小/最大值保护）
        """
        # === Step 1: 确定最终使用的 timeout 值 ===
        if timeout is None:
            use_timeout = self.current_timeout  # ✅ 自动受 property 保护
        else:
            # ❗即使外部传了，我们也必须 clamp 到合法范围
            min_t = config.get("voice_recognition","timeout","min")
            max_t = config.get("voice_recognition","timeout","max")

            if timeout < min_t:
                logger.warning(f"⚠️ 外部指定的超时时间 {timeout}s 小于最小允许值 {min_t}s，已修正")
                use_timeout = min_t
            elif timeout > max_t:
                logger.warning(f"⚠️ 外部指定的超时时间 {timeout}s 超过最大允许值 {max_t}s，已修正")
                use_timeout = max_t
            else:
                use_timeout = float(timeout)

        start_time = time.time()
        in_speech = False
        result_text = ""

        logger.debug(f"🎙️ 开始单次语音识别 (effective_timeout={use_timeout:.1f}s)...")

        # 🔴 如果正在播放 TTS，直接返回空
        if self.is_tts_playing:
            logger.info("🔇 TTS 正在播放，跳过本次识别")
            return ""

        logger.info("🔊 请说话...")

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

            while (time.time() - start_time) < use_timeout:
                # 再次检查播放状态（可能中途开始）
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

                # 注意：这里的判断已经由 use_timeout 控制
                if not in_speech and (time.time() - start_time) >= use_timeout:
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

# 全局实例（方便其他模块调用）
recognizer = SpeechRecognizer()
