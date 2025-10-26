"""
单例管理中心
确保模块按顺序初始化，并延迟加载
"""

from threading import Lock

from Progress.utils.logger_utils import log_call

_system_controller = None
_task_orchestrator = None
_tts_engine = None
_voice_recognizer = None
_qwen_assistant = None

_lock = Lock()
_initialized = False

def _ensure_init():
    global _initialized
    if _initialized:
        return
    with _lock:
        if _initialized:
            return
        initialize_all()
        _initialized = True

def get_system_controller(): _ensure_init(); return _system_controller
def get_task_executor(): _ensure_init(); return _task_orchestrator
def get_tts_engine(): _ensure_init(); return _tts_engine
def get_voice_recognizer(): _ensure_init(); return _voice_recognizer
def get_ai_assistant(): _ensure_init(); return _qwen_assistant

def initialize_all():
    global _system_controller, _task_orchestrator, _tts_engine, _voice_recognizer, _qwen_assistant
    from Progress.utils.logger_config import setup_logger
    logger = setup_logger("ai_assistant")

    logger.info("🚀 启动 AI 助手...")

    from database.config import config

    # 1. 控制器（触发 @ai_callable 注册）
    from Progress.app.system_controller import SystemController
    _system_controller = SystemController()

    # 2. 任务执行器（自动启动后台循环）
    from Progress.app.system_controller import TaskOrchestrator
    _task_orchestrator = TaskOrchestrator(_system_controller)

    # 4. TTS 引擎
    from Progress.app.text_to_speech import TextToSpeechEngine
    _tts_engine = TextToSpeechEngine()

    # 3. 语音识别器
    from Progress.app.voice_recognizer import SpeechRecognizer
    _voice_recognizer = SpeechRecognizer(tts_engine = _tts_engine)

    # 5. QWEN 助手
    from Progress.app.qwen_assistant import QWENAssistant
    _qwen_assistant = QWENAssistant()

    # 6. 启动 TTS 子线程
    _tts_engine.start()

    logger.info("🎉 所有模块初始化完成！")

    log_call("🎙️ AI 助手已就绪！说出指令试试吧～")
