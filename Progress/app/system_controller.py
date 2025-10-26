import inspect
import os
import platform
import random
import subprocess
import threading
import time
import psutil
import pygame
import schedule
from datetime import datetime
from typing import Tuple, List, Optional, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass

from database.config import config
from Progress.utils.ai_tools import FUNCTION_SCHEMA, ai_callable
from Progress.utils.logger_utils import log_time, log_step, log_var, log_call
from Progress.utils.logger_config import setup_logger
from Progress.utils.resource_helper import resource_path

# 初始化日志
logger = setup_logger("ai_assistant")

# 从配置读取路径
MUSIC_REL_PATH = config.get("paths", "resources", "music_path")     # 如 "Music"
DOC_REL_PATH = config.get("paths", "resources", "document_path")    # 如 "Documents"

DEFAULT_MUSIC_PATH = resource_path(MUSIC_REL_PATH)
DEFAULT_DOCUMENT_PATH = resource_path(DOC_REL_PATH)

TERMINAL_OPERATIONS = {"exit"}


@dataclass
class TaskResult:
    success: bool
    message: str
    operation: str
    data: dict = None
    timestamp: float = None

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "message": self.message,
            "operation": self.operation,
            "data": self.data or {}
        }


class SystemController:
    def __init__(self):
        self.system = platform.system()
        self.music_player = None
        self._init_music_player()

        # === 音乐播放状态 ===
        self.current_playlist: List[str] = []
        self.current_index: int = 0
        self.is_paused: bool = False
        self.loop_mode: str = "all"  # "none", "all", "one", "shuffle"
        self.MUSIC_END_EVENT = pygame.USEREVENT + 1
        pygame.mixer.music.set_endevent(self.MUSIC_END_EVENT)

        # === 其他任务状态 ===
        self.task_counter = 0
        self.scheduled_tasks = {}

    @log_step("初始化音乐播放器")
    @log_time
    def _init_music_player(self):
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self.music_player = pygame.mixer.music
            logger.info("✅ 音乐播放器初始化成功")
        except Exception as e:
            logger.exception("❌ 音乐播放器初始化失败")
            self.music_player = None

    # ======================
    # 🎵 音乐播放相关功能
    # ======================

    @ai_callable(
        description="加载指定目录下的所有音乐文件到播放列表，默认使用配置的音乐路径。",
        params={"path": "音乐文件夹路径（可选）"},
        intent="music",
        action="load_playlist",
        concurrent=True
    )
    def load_playlist(self, path: str = None) -> Tuple[bool, str]:
        target_path = path or DEFAULT_MUSIC_PATH
        if not os.path.exists(target_path):
            msg = f"📁 路径不存在: {target_path}"
            logger.warning(msg)
            return False, msg

        music_files = self._find_music_files(target_path)
        if not music_files:
            return False, "🎵 未找到任何支持的音乐文件（.mp3/.wav/.flac/.m4a/.ogg）"

        self.current_playlist = music_files
        self.current_index = 0
        self.is_paused = False
        msg = f"✅ 已加载 {len(music_files)} 首歌曲到播放列表"
        logger.info(msg)
        return True, msg

    @ai_callable(
        description="开始播放音乐。若尚未加载播放列表，则先加载默认路径下的所有音乐。",
        params={"path": "自定义音乐路径（可选）"},
        intent="music",
        action="play",
        concurrent=True
    )
    def play_music(self, path: str = None) -> Tuple[bool, str]:
        if not self.current_playlist:
            success, msg = self.load_playlist(path)
            if not success:
                return success, msg

        return self._play_current_track()

    @ai_callable(
        description="暂停当前正在播放的音乐。",
        params={},
        intent="music",
        action="pause"
    )
    def pause_music(self) -> Tuple[bool, str]:
        try:
            if self.current_playlist and pygame.mixer.get_init() and pygame.mixer.music.get_busy():
                pygame.mixer.music.pause()
                self.is_paused = True
                track_name = os.path.basename(self.current_playlist[self.current_index])
                msg = f"⏸️ 音乐已暂停: {track_name}"
                logger.info(msg)
                return True, msg
            return False, "当前没有正在播放的音乐"
        except Exception as e:
            logger.exception("⏸️ 暂停失败")
            return False, f"暂停失败: {str(e)}"

    @ai_callable(
        description="恢复播放当前暂停的音乐。",
        params={},
        intent="music",
        action="resume"
    )
    def resume_music(self) -> Tuple[bool, str]:
        try:
            if self.is_paused and pygame.mixer.music.get_busy():
                pygame.mixer.music.unpause()
                self.is_paused = False
                track_name = os.path.basename(self.current_playlist[self.current_index])
                msg = f"▶️ 音乐已恢复: {track_name}"
                logger.info(msg)
                return True, msg
            return False, "当前没有暂停的音乐"
        except Exception as e:
            logger.exception("▶️ 恢复失败")
            return False, f"恢复失败: {str(e)}"

    @ai_callable(
        description="停止音乐播放，并清空播放状态。",
        params={},
        intent="music",
        action="stop"
    )
    def stop_music(self) -> Tuple[bool, str]:
        try:
            if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
            self.is_paused = False
            logger.info("⏹️ 音乐已停止")
            return True, "音乐已停止"
        except Exception as e:
            logger.exception("⏹️ 停止失败")
            return False, f"停止失败: {str(e)}"

    @ai_callable(
        description="播放播放列表中的下一首歌曲。",
        params={},
        intent="music",
        action="next"
    )
    def play_next(self) -> Tuple[bool, str]:
        if not self.current_playlist:
            return False, "❌ 播放列表为空，请先加载音乐"

        if len(self.current_playlist) == 1:
            return self._play_current_track()  # 重新播放唯一一首

        if self.loop_mode == "shuffle":
            next_idx = random.randint(0, len(self.current_playlist) - 1)
        else:
            next_idx = (self.current_index + 1) % len(self.current_playlist)

        self.current_index = next_idx
        return self._play_current_track()

    @ai_callable(
        description="播放播放列表中的上一首歌曲。",
        params={},
        intent="music",
        action="previous"
    )
    def play_previous(self) -> Tuple[bool, str]:
        if not self.current_playlist:
            return False, "❌ 播放列表为空"

        prev_idx = (self.current_index - 1) % len(self.current_playlist)
        self.current_index = prev_idx
        return self._play_current_track()

    @ai_callable(
        description="设置音乐播放循环模式：'none'(不循环), 'all'(列表循环), 'one'(单曲循环), 'shuffle'(随机播放)",
        params={"mode": "循环模式字符串"},
        intent="music",
        action="set_loop"
    )
    def set_loop_mode(self, mode: str = "all") -> Tuple[bool, str]:
        valid_modes = {"none", "all", "one", "shuffle"}
        if mode not in valid_modes:
            return False, f"❌ 不支持的模式: {mode}，可用值: {valid_modes}"

        self.loop_mode = mode
        mode_names = {
            "none": "顺序播放",
            "all": "列表循环",
            "one": "单曲循环",
            "shuffle": "随机播放"
        }
        msg = f"🔁 播放模式已设为: {mode_names[mode]}"
        logger.info(msg)
        return True, msg

    def _play_current_track(self) -> Tuple[bool, str]:
        """私有方法：播放当前索引对应的歌曲"""
        try:
            if not self.current_playlist:
                return False, "播放列表为空"

            file_path = self.current_playlist[self.current_index]
            if not os.path.exists(file_path):
                return False, f"文件不存在: {file_path}"

            self.music_player.load(file_path)
            self.music_player.play()
            self.is_paused = False

            track_name = os.path.basename(file_path)
            success_msg = f"🎶 正在播放 [{self.current_index + 1}/{len(self.current_playlist)}]: {track_name}"
            logger.info(success_msg)
            return True, success_msg
        except Exception as e:
            logger.exception("💥 播放失败")
            return False, f"播放失败: {str(e)}"

    def _find_music_files(self, directory: str) -> List[str]:
        """查找指定目录下所有支持的音乐文件"""
        music_extensions = {'.mp3', '.wav', '.flac', '.m4a', '.ogg'}
        music_files = []
        try:
            for root, _, files in os.walk(directory):
                for file in files:
                    if any(file.lower().endswith(ext) for ext in music_extensions):
                        music_files.append(os.path.join(root, file))
        except Exception as e:
            logger.error(f"搜索音乐文件失败: {e}")
        return sorted(music_files)

    # ======================
    # 💻 系统与文件操作
    # ======================

    @ai_callable(
        description="获取当前系统信息，包括操作系统、CPU、内存、磁盘等状态。",
        params={},
        intent="system",
        action="get_system_info",
        concurrent=True
    )
    def get_system_info(self) -> Tuple[bool, str]:
        try:
            os_name = platform.system()
            os_version = platform.version()
            processor = platform.processor() or "Unknown"

            cpu_usage = psutil.cpu_percent(interval=0.1)
            mem = psutil.virtual_memory()
            mem_used_gb = mem.used / (1024 ** 3)
            mem_total_gb = mem.total / (1024 ** 3)

            root_disk = "C:\\" if os_name == "Windows" else "/"
            disk = psutil.disk_usage(root_disk)
            disk_free_gb = disk.free / (1024 ** 3)
            disk_percent = disk.percent

            spoken_text = (
                f"我现在为您汇报系统状态。操作系统是{os_name}，"
                f"系统版本为{os_version}，处理器型号是{processor}。"
                f"目前CPU使用率为{cpu_usage:.1f}%，内存使用了{mem_used_gb:.1f}GB，"
                f"总共{mem_total_gb:.1f}GB，占用率为{mem.percent:.0f}%。"
                f"主磁盘使用率为{disk_percent:.0f}%，剩余可用空间约为{disk_free_gb:.1f}GB。"
                "以上就是当前系统的运行情况。"
            )
            return True, spoken_text
        except Exception as e:
            error_msg = f"抱歉，无法获取系统信息。错误原因：{str(e)}。请检查权限或重试。"
            return False, error_msg

    @ai_callable(
        description="打开应用程序或浏览器访问网址",
        params={"app_name": "应用名称，如 记事本、浏览器", "url": "网页地址（可选）"},
        intent="system",
        action="open_app",
        concurrent=True
    )
    def open_application(self, app_name: str, url: str = None) -> Tuple[bool, str]:
        alias_map = {
            "浏览器": "browser", "browser": "browser",
            "chrome": "browser", "google chrome": "browser", "谷歌浏览器": "browser",
            "edge": "browser", "firefox": "browser", "safari": "browser",
            "记事本": "text_editor", "notepad": "text_editor",
            "文本编辑器": "text_editor", "文件管理器": "explorer",
            "explorer": "explorer", "finder": "explorer",
            "计算器": "calc", "calc": "calc", "calculator": "calc",
            "终端": "terminal", "cmd": "terminal", "powershell": "terminal"
        }

        key = alias_map.get(app_name.strip().lower())
        if not key:
            return False, f"🚫 不支持的应用: {app_name}。支持：浏览器、记事本、计算器、终端等。"

        try:
            if key == "browser":
                target_url = url or "https://www.baidu.com"
                import webbrowser
                if webbrowser.open(target_url):
                    return True, f"正在打开浏览器访问: {target_url}"
                return False, "无法打开浏览器"
            else:
                cmd_func = getattr(self, f"_get_{key}_command", None)
                if not cmd_func:
                    return False, f"缺少命令生成函数: _get_{key}_command"
                cmd = cmd_func()
                subprocess.Popen(cmd, shell=True)
                return True, f"🚀 已发送指令打开 {app_name}"
        except Exception as e:
            logger.exception(f"启动应用失败: {app_name}")
            return False, f"启动失败: {str(e)}"

    def _get_text_editor_command(self): return "notepad" if self.system == "Windows" else "open -a TextEdit" if self.system == "Darwin" else "gedit"
    def _get_explorer_command(self): return "explorer" if self.system == "Windows" else "open -a Finder" if self.system == "Darwin" else "nautilus"
    def _get_calc_command(self): return "calc" if self.system == "Windows" else "open -a Calculator" if self.system == "Darwin" else "gnome-calculator"
    def _get_terminal_command(self): return "cmd" if self.system == "Windows" else "open -a Terminal" if self.system == "Darwin" else "gnome-terminal"

    @ai_callable(
        description="创建一个新文本文件并写入内容。",
        params={"file_name": "文件名", "content": "要写入的内容"},
        intent="file",
        action="create",
        concurrent=True
    )
    def create_file(self, file_name: str, content: str = "") -> Tuple[bool, str]:
        file_path = os.path.join(DEFAULT_DOCUMENT_PATH, file_name)
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, f"文件已创建: {file_path}"
        except Exception as e:
            logger.exception("创建文件失败")
            return False, f"创建失败: {str(e)}"

    @ai_callable(
        description="读取文本文件内容。",
        params={"file_name": "文件名"},
        intent="file",
        action="read",
        concurrent=True
    )
    def read_file(self, file_name: str) -> Tuple[bool, str]:
        file_path = os.path.join(DEFAULT_DOCUMENT_PATH, file_name)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return True, content
        except Exception as e:
            return False, f"读取失败: {str(e)}"

    @ai_callable(
        description="向指定文件写入内容（覆盖原内容）。",
        params={"file_name": "文件名", "content": "要写入的内容"},
        intent="file",
        action="write",
        concurrent=True
    )
    def write_file(self, file_name: str, content: str) -> Tuple[bool, str]:
        file_path = os.path.join(DEFAULT_DOCUMENT_PATH, file_name)
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, f"文件已保存: {file_name}"
        except Exception as e:
            return False, f"写入失败: {str(e)}"

    @ai_callable(
        description="设置一个定时提醒，在指定分钟后触发。",
        params={"message": "提醒内容", "delay_minutes": "延迟分钟数"},
        intent="system",
        action="set_reminder",
        concurrent=True
    )
    def set_reminder(self, message: str, delay_minutes: float) -> Tuple[bool, str]:
        try:
            self.task_counter += 1
            task_id = f"reminder_{self.task_counter}"

            def job():
                print(f"🔔 提醒: {message}")
                # 可在此调用 TTS 播报提醒

            schedule.every(delay_minutes).minutes.do(job)
            self.scheduled_tasks[task_id] = {
                "message": message,
                "delay": delay_minutes,
                "created": datetime.now()
            }
            return True, f"提醒已设置: {delay_minutes} 分钟后提醒 - {message}"
        except Exception as e:
            return False, f"设置提醒失败: {str(e)}"

    @ai_callable(
        description="退出语音助手应用程序。",
        params={},
        intent="system",
        action="exit",
        concurrent=False
    )
    def exit(self) -> Tuple[bool, str]:
        logger.info("🛑 用户请求退出，准备关闭语音助手...")
        return True, "正在关闭语音助手"

    @ai_callable(
        description="并发执行多个任务。",
        params={"tasks": "任务列表，每个包含 operation 和 arguments"},
        intent="system",
        action="execute_concurrent",
        concurrent=True
    )
    def _run_parallel_tasks(self, tasks: List[dict]) -> Tuple[bool, str]:
        def run_single(task):
            op = task.get("operation")
            args = task.get("arguments", {})
            func = getattr(self, op, None)
            if func and callable(func):
                try:
                    func(**args)
                except Exception as e:
                    logger.error(f"执行任务 {op} 失败: {e}")

        for task in tasks:
            t = threading.Thread(target=run_single, args=(task,), daemon=True)
            t.start()

        return True, f"已并发执行 {len(tasks)} 个任务"


class TaskOrchestrator:
    def __init__(self, system_controller: SystemController):
        self.system_controller = system_controller
        self.function_map = self._build_function_map()
        self.running_scheduled_tasks = False
        self.last_result = None
        logger.info(f"🔧 任务编排器已加载 {len(self.function_map)} 个可调用函数")

        # ✅ 自动启动后台任务监听
        self._start_scheduled_task_loop()

    def _build_function_map(self) -> Dict[str, callable]:
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
        converted = {}
        sig = inspect.signature(func)
        for name, param in sig.parameters.items():
            value = args.get(name)
            if value is None:
                continue
            ann = param.annotation
            if isinstance(ann, type):
                try:
                    if ann == int and not isinstance(value, int):
                        converted[name] = int(float(value))  # 支持 "3.0" → 3
                    elif ann == float and not isinstance(value, float):
                        converted[name] = float(value)
                    else:
                        converted[name] = value
                except (ValueError, TypeError):
                    converted[name] = value
            else:
                converted[name] = value
        return converted

    def _start_scheduled_task_loop(self):
        def run_loop():
            while self.running_scheduled_tasks:
                schedule.run_pending()
                time.sleep(1)
        if not self.running_scheduled_tasks:
            self.running_scheduled_tasks = True
            thread = threading.Thread(target=run_loop, daemon=True)
            thread.start()
            logger.info("⏰ 已启动定时任务监听循环")

    def run_single_step(self, step: dict) -> TaskResult:
        op = step.get("operation")
        params = step.get("parameters", {})
        func = self.function_map.get(op)
        if not func:
            msg = f"不支持的操作: {op}"
            logger.warning(f"⚠️ {msg}")
            return TaskResult(False, msg, op)

        try:
            safe_params = self._convert_arg_types(func, params)
            result = func(**safe_params)
            if isinstance(result, tuple):
                success, message = result
                return TaskResult(bool(success), str(message), op)
            return TaskResult(True, str(result), op)
        except Exception as e:
            logger.exception(f"执行 {op} 失败")
            return TaskResult(False, str(e), op)

    @log_step("执行多任务计划")
    @log_time
    def execute_task_plan(self, plan: dict = None) -> Dict[str, Any]:
        execution_plan = plan.get("execution_plan", [])
        mode = plan.get("mode", "parallel").lower()
        response_to_user = plan.get("response_to_user", "任务已提交。")
        if not execution_plan:
            return {
                "success": True,
                "message": response_to_user,
                "operation": "task_plan"
            }

        normal_steps = []
        terminal_step = None
        for step in execution_plan:
            op = step.get("operation")
            if op in TERMINAL_OPERATIONS:
                terminal_step = step
            else:
                normal_steps.append(step)

        all_results: List[TaskResult] = []
        all_success = True

        if normal_steps:
            if mode == "parallel":
                with ThreadPoolExecutor() as executor:
                    future_to_step = {executor.submit(self.run_single_step, step): step for step in normal_steps}
                    for future in as_completed(future_to_step):
                        res = future.result()
                        all_results.append(res)
                        if not res.success:
                            all_success = False
            else:
                for step in normal_steps:
                    res = self.run_single_step(step)
                    all_results.append(res)
                    if not res.success:
                        all_success = False
                        break

        final_terminal_result = None
        should_exit_flag = False
        if terminal_step and all_success:
            final_terminal_result = self.run_single_step(terminal_step)
            all_results.append(final_terminal_result)
            if not final_terminal_result.success:
                all_success = False
            elif final_terminal_result.operation == "exit":
                should_exit_flag = True

        messages = [r.message for r in all_results if r.message]
        final_message = " | ".join(messages) if messages else response_to_user

        response = {
            "success": all_success,
            "message": final_message.strip(),
            "operation": "task_plan",
            "input": plan,
            "step_results": [r.to_dict() for r in all_results],
            "data": {
                "plan_mode": mode,
                "terminal_executed": terminal_step is not None,
                "result_count": len(all_results)
            }
        }

        if should_exit_flag:
            response["should_exit"] = True

        self.last_result = response
        return response

    def run_scheduled_tasks(self):
        """处理定时任务和 Pygame 事件"""
        schedule.run_pending()
        for event in pygame.event.get():
            if event.type == self.system_controller.MUSIC_END_EVENT:
                self._handle_music_ended()

    def _handle_music_ended(self):
        ctrl = self.system_controller
        if not ctrl.current_playlist:
            return
        if ctrl.loop_mode == "one":
            ctrl._play_current_track()
        elif ctrl.loop_mode in ("all", "shuffle"):
            ctrl.play_next()
