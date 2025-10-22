"""
【系统控制模块】System Controller
提供音乐播放、文件操作、应用启动、定时提醒等本地系统级功能
"""
import inspect
import os
import subprocess
import platform
import threading
import time
from typing import Any, Dict
import psutil
import pygame
from datetime import datetime
import logging
import schedule


from database import config
from Progress.utils.ai_tools import FUNCTION_SCHEMA, ai_callable
from Progress.utils.logger_utils import log_time, log_step, log_var, log_call
from Progress.utils.logger_config import setup_logger

""" import config
from utils.logger_utils import log_time, log_step, log_var, log_call
from utils.logger_config import setup_logger """

RESOURCE_PATH = config.resource_path
DEFAULT_MUSIC_PATH = os.path.join(RESOURCE_PATH, config.music_path)
DEFAULT_DOCUMENT_PATH = os.path.join(RESOURCE_PATH, config.doc_path)

logger = logging.getLogger("ai_assistant")


class SystemController:
    def __init__(self):
        self.system = platform.system()
        self.music_player = None
        self._init_music_player()

    @log_step("初始化音乐播放器")
    @log_time
    def _init_music_player(self):
        try:
            pygame.mixer.init()
            self.music_player = pygame.mixer.music
            logger.info("✅ 音乐播放器初始化成功")
        except Exception as e:
            logger.exception("❌ 音乐播放器初始化失败")
            self.music_player = None

    @log_step("播放音乐")
    @log_time    
    @ai_callable(
        description="播放音乐文件或指定歌手的歌曲",
        params={"path": "音乐文件路径", "artist": "歌手名称"},
        intent="music",
        action="play"
    )
    def play_music(self, music_path=None):
        target_path = music_path or DEFAULT_MUSIC_PATH
        if not os.path.exists(target_path):
            msg = f"📁 路径不存在: {target_path}"
            logger.warning(msg)
            return False, msg

        music_files = self._find_music_files(target_path)
        if not music_files:
            msg = "🎵 未找到支持的音乐文件"
            logger.info(msg)
            return False, msg

        try:
            self.stop_music()
            self.music_player.load(music_files[0])
            self.music_player.play()
            success_msg = f"🎶 正在播放: {os.path.basename(music_files[0])}"
            logger.info(success_msg)
            return True, success_msg
        except Exception as e:
            logger.exception("💥 播放音乐失败")
            return False, f"播放失败: {str(e)}"
    
    @ai_callable(
        description="停止当前播放的音乐",
        params={},
        intent="music",
        action="stop"
    )
    def stop_music(self):
        try:
            if self.music_player and pygame.mixer.get_init():
                self.music_player.stop()
                logger.info("⏹️ 音乐已停止")
            return True, "音乐已停止"
        except Exception as e:
            logger.exception("❌ 停止音乐失败")
            return False, f"停止失败: {str(e)}"

    @ai_callable(
        description="暂停当前正在播放的音乐。",
        params={},
        intent="muxic",
        action="pause"
    )
    def pause_music(self):
        """暂停音乐"""
        try:
            self.music_player.pause()
            return True, "音乐已暂停"
        except Exception as e:
            return False, f"暂停音乐失败: {str(e)}"
    
    @ai_callable(
        description="恢复播放当前正在播放的音乐。",
        params={},
        intent="music",
        action="resume"
    )
    def resume_music(self):
        """恢复音乐"""
        try:
            self.music_player.unpause()
            return True, "音乐已恢复"
        except Exception as e:
            return False, f"恢复音乐失败: {str(e)}"

    @ai_callable(
        description="打开应用程序或浏览器访问网址",
        params={"app_name": "应用名称（如 记事本、浏览器）", "url": "网页地址"},
        intent="system",
        action="open_app"
    )
    def open_application(self, app_name: str, url: str = None):
        """
        AI 调用入口：打开指定应用程序
        参数由 AI 解析后传入
        """
        # === 别名映射表 ===
        alias_map = {
            # 浏览器相关
            "浏览器": "browser", "browser": "browser",
            "chrome": "browser", "google chrome": "browser", "谷歌浏览器": "browser",
            "edge": "browser", "firefox": "browser", "safari": "browser",

            # 文本编辑器
            "记事本": "text_editor", "notepad": "text_editor", "text_editer": "text_editor", "文本编辑器": "text_editor",

            # 文件管理器
            "文件管理器": "explorer", "explorer": "explorer", "finder": "explorer",

            # 计算器
            "计算器": "calc", "calc": "calc", "calculator": "calc",

            # 终端
            "终端": "terminal", "terminal": "terminal", "cmd": "terminal", "powershell": "terminal",
            "shell": "terminal", "命令行": "terminal"
        }

        app_key = alias_map.get(app_name.strip())
        if not app_key:
            error_msg = f"🚫 不支持的应用: {app_name}。支持的应用有：浏览器、记事本、计算器、终端、文件管理器等。"
            logger.warning(error_msg)
            return False, error_msg

        try:
            if app_key == "browser":
                target_url = url or "https://www.baidu.com"
                success, msg = self._get_browser_command(target_url)
                logger.info(f"🌐 {msg}")
                return success, msg
            else:
                # 获取对应命令生成函数
                cmd_func_name = f"_get_{app_key}_command"
                cmd_func = getattr(self, cmd_func_name, None)
                if not cmd_func:
                    return False, f"❌ 缺少命令生成函数: {cmd_func_name}"

                cmd = cmd_func()
                subprocess.Popen(cmd, shell=True)
                success_msg = f"🚀 已发送指令打开 {app_name}"
                logger.info(success_msg)
                return True, success_msg

        except Exception as e:
            logger.exception(f"💥 启动应用失败: {app_name}")
            return False, f"启动失败: {str(e)}"

    @ai_callable(
        description="创建一个新文本文件并写入内容",
        params={"file_path": "文件路径", "content": "要写入的内容"},
        intent="file",
        action="create"
    )
    def create_file(self, file_path, content=""):
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, f"文件已创建: {file_path}"
        except Exception as e:
            logger.exception("❌ 创建文件失败")
            return False, f"创建失败: {str(e)}"
    
    @ai_callable(
        description="读取文本文件内容",
        params={"file_path": "文件路径"},
        intent="file",
        action="read"
    )
    def read_file(self, file_path):
        """读取文件"""
        try:
            with open(DEFAULT_DOCUMENT_PATH+file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return True, content
        except Exception as e:
            return False, f"读取文件失败: {str(e)}"
    
    @ai_callable(
        description="读取文本文件内容",
        params={"file_path": "文件路径","content":"写入的内容"},
        intent="file",
        action="write"
    )
    def write_file(self, file_path, content):
        """写入文件"""
        try:
            with open(DEFAULT_DOCUMENT_PATH+file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, f"文件已保存: {file_path}"
        except Exception as e:
            return False, f"写入文件失败: {str(e)}"
    
    @ai_callable(
        description="获取当前系统信息，包括操作系统、CPU、内存等。",
        params={},
        intent="system",
        action="get_system_info"
    )
    def get_system_info(self):
        """获取系统信息"""
        try:
            info = {
                "操作系统": platform.system(),
                "系统版本": platform.version(),
                "处理器": platform.processor(),
                "内存使用率": f"{psutil.virtual_memory().percent}%",
                "CPU使用率": f"{psutil.cpu_percent()}%",
                "磁盘使用率": f"{psutil.disk_usage('/').percent}%"
            }
            return True, info
        except Exception as e:
            return False, f"获取系统信息失败: {str(e)}"
    
    @ai_callable(
        description="设置一个定时提醒",
        params={"message": "提醒内容", "delay_minutes": "延迟分钟数"},
        intent="system",
        action="set_reminder"
    )
    def set_reminder(self, message, delay_minutes):
        """设置提醒"""
        try:
            self.task_counter += 1
            task_id = f"reminder_{self.task_counter}"
            
            def reminder_job():
                print(f"提醒: {message}")
                # 这里可以添加通知功能
            
            schedule.every(delay_minutes).minutes.do(reminder_job)
            self.scheduled_tasks[task_id] = {
                "message": message,
                "delay": delay_minutes,
                "created": datetime.now()
            }
            
            return True, f"提醒已设置: {delay_minutes}分钟后提醒 - {message}"
        except Exception as e:
            return False, f"设置提醒失败: {str(e)}"
    
    def run_scheduled_tasks(self):
        """运行定时任务"""
        schedule.run_pending()
    
    def _find_music_files(self, directory):
        """查找音乐文件"""
        music_extensions = ['.mp3', '.wav', '.flac', '.m4a', '.ogg']
        music_files = []
        
        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if any(file.lower().endswith(ext) for ext in music_extensions):
                        music_files.append(os.path.join(root, file))
        except Exception as e:
            print(f"搜索音乐文件失败: {e}")
        
        return music_files
    
    def _get_text_editor_command(self):
        """获取文本编辑器启动命令"""
        if self.system == "Windows":
            return "notepad"
        elif self.system == "Darwin":  # macOS
            return "open -a TextEdit"
        else:  # Linux
            return "gedit"
    
    def _get_explorer_command(self):
        """获取文件管理器启动命令"""
        if self.system == "Windows":
            return "explorer"
        elif self.system == "Darwin":  # macOS
            return "open -a Finder"
        else:  # Linux
            return "nautilus"
    
    def _get_calc_command(self):
        """获取计算器启动命令"""
        if self.system == "Windows":
            return "calc"
        elif self.system == "Darwin":  # macOS
            return "open -a Calculator"
        else:  # Linux
            return "gnome-calculator"
    
    def _get_terminal_command(self):
        """获取终端启动命令"""
        if self.system == "Windows":
            return "cmd"
        elif self.system == "Darwin":  # macOS
            return "open -a Terminal"
        else:  # Linux
            return "gnome-terminal"

    def _get_browser_command(self, url="https://www.baidu.com"):
        try:
            import webbrowser
            if webbrowser.open(url):
                logger.info(f"🌐 已使用默认浏览器打开: {url}")
                return True, f"正在打开浏览器访问: {url}"
            else:
                return False, "无法打开浏览器"
        except Exception as e:
            logger.error(f"❌ 浏览器打开异常: {e}")
            return False, str(e)
        
class TaskOrchestrator:
    def __init__(self, system_controller):
        self.system_controller = system_controller
        self.function_map = self._build_function_map()
        self.running_scheduled_tasks = False
        logger.info(f"🔧 任务编排器已加载 {len(self.function_map)} 个可调用函数")

    def _build_function_map(self) -> Dict[str, callable]:
        """构建函数名 → 方法对象的映射"""
        mapping = {}
        for item in FUNCTION_SCHEMA:
            func_name = item["name"]
            func = getattr(self.system_controller, func_name, None)
            if func and callable(func):
                mapping[func_name] = func
            else:
                logger.warning(f"⚠️ 未找到或不可调用: {func_name}")
        return mapping

    def _convert_arg_types(self, func: callable, args: dict) -> dict:
        """
        尝试将参数转为函数期望的类型（简单启发式）
        注意：Python 没有原生参数类型签名，这里做基础转换
        """
        converted = {}
        sig = inspect.signature(func)
        for name, param in sig.parameters.items():
            value = args.get(name)
            if value is None:
                continue

            # 简单类型推断（基于默认值）
            ann = param.annotation
            if isinstance(ann, type):
                try:
                    if ann == int and not isinstance(value, int):
                        converted[name] = int(value)
                    elif ann == float and not isinstance(value, float):
                        converted[name] = float(value)
                    else:
                        converted[name] = value
                except (ValueError, TypeError):
                    converted[name] = value  # 保持原始值，让函数自己处理
            else:
                converted[name] = value
        return converted

    def _start_scheduled_task_loop(self):
        """后台线程运行定时任务"""
        def run_loop():
            while self.running_scheduled_tasks:
                schedule.run_pending()
                time.sleep(1)

        if not self.running_scheduled_tasks:
            self.running_scheduled_tasks = True
            thread = threading.Thread(target=run_loop, daemon=True)
            thread.start()
            logger.info("⏰ 已启动定时任务监听循环")

    def execute_from_ai_decision(self, user_input: str) -> Dict[str, Any]:
        """
        主入口：接收用户输入 → AI 决策 → 执行函数 → 返回结构化结果
        """
        from utils.ai_tools import call_llm_to_choose_function  # 假设已定义

        # Step 1: AI 决策（模拟或真实 LLM）
        decision = call_llm_to_choose_function(user_input)
        if not decision:
            return {
                "success": False,
                "message": "抱歉，我没有理解您的请求。",
                "data": None
            }

        func_name = decision.get("function")
        args = decision.get("arguments", {})

        if not func_name:
            return {
                "success": False,
                "message": "AI 返回的函数名为空。",
                "data": None
            }

        # Step 2: 查找函数
        func = self.function_map.get(func_name)
        if not func:
            logger.warning(f"❌ 函数不存在: {func_name}")
            return {
                "success": False,
                "message": f"系统不支持操作：{func_name}",
                "data": None
            }

        # Step 3: 参数预处理（类型转换）
        try:
            safe_args = self._convert_arg_types(func, args)
        except Exception as e:
            logger.warning(f"参数转换失败: {e}")
            safe_args = args  # 使用原始参数

        # Step 4: 执行函数
        try:
            logger.info(f"🚀 正在执行: {func_name}({safe_args})")
            result = func(**safe_args)

            # 统一返回格式：(success: bool, message: str 或 dict)
            if isinstance(result, tuple):
                success, msg = result
            elif isinstance(result, dict):
                success = result.get("success", False)
                msg = result.get("message", str(result))
            else:
                success = True
                msg = str(result)

            # === 特殊逻辑：如果设置了提醒，启动后台调度循环 ===
            if func_name == "set_reminder" and success:
                self._start_scheduled_task_loop()

            # 返回标准格式
            return {
                "success": success,
                "message": msg,
                "data": None,
                "operation": func_name,
                "input": args
            }

        except TypeError as e:
            error_msg = f"参数错误，请检查输入格式: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "message": error_msg,
                "data": None
            }
        except Exception as e:
            logger.exception(f"💥 执行 {func_name} 时发生异常")
            return {
                "success": False,
                "message": f"执行失败：{str(e)}",
                "data": None
            }
        
if __name__ == "__main__":
    controller = SystemController()
    orchestrator = TaskOrchestrator(controller)

    test_inputs = [
        "播放我的音乐",
        "打开记事本",
        "创建 test.txt 文件，内容是 hello",
        "告诉我电脑用了多少内存",
        "10分钟后提醒我喝水",
        "停止音乐"
    ]

    for inp in test_inputs:
        print(f"\n👤 用户: {inp}")
        result = orchestrator.execute_from_ai_decision(inp)
        print(f"🤖 AI 助手: {result['message']}")
