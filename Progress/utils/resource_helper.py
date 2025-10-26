# Progress/utils/resource_helper.py
import os
import sys
from typing import Optional


def get_internal_path(*relative_path_parts) -> str:
    """
    获取内部资源路径（如 base_config.json），适用于开发和打包环境。
    示例: get_internal_path("database", "base_config.json")
    """
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        # __file__ → Progress/utils/resource_helper.py
        current_dir = os.path.dirname(os.path.abspath(__file__))
        progress_root = os.path.dirname(current_dir)  # Progress/
        project_root = os.path.dirname(progress_root)  # AI_Manager/
        base_path = project_root
    return os.path.join(base_path, *relative_path_parts)


def get_app_path() -> str:
    """
    获取应用运行数据保存路径（config.json、日志等）
    打包后：exe 所在目录
    开发时：AI_Manager/ 根目录
    """
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        progress_root = os.path.dirname(current_dir)
        project_root = os.path.dirname(progress_root)
        return project_root


def resource_path(*sub_paths: str, base_key: str = "resource_path") -> str:
    """
    通用用户资源路径解析（基于 config 的 resource_path）
    示例: resource_path("Music", "bgm.mp3") → <resource_path>/Music/bgm.mp3
    :param sub_paths: 子路径组件
    :param base_key: 在 config.paths 中的键名，默认 "resource_path"
    """
    # 延迟导入，避免循环依赖
    from database.config import config

    raw_base = config.get("paths", base_key)
    if not raw_base:
        raise ValueError(f"配置项 paths.{base_key} 未设置")

    if os.path.isabs(raw_base):
        base_path = raw_base
    else:
        base_path = os.path.join(get_app_path(), raw_base)

    full_path = os.path.normpath(base_path)
    for part in sub_paths:
        clean_part = str(part).strip().lstrip(r'./\ ')
        for p in clean_part.replace('\\', '/').split('/'):
            if p:
                full_path = os.path.join(full_path, p)
    return os.path.normpath(full_path)


def ensure_directory(path: str) -> bool:
    """
    确保目录存在。若 path 是文件路径，则创建其父目录。
    """
    dir_path = path
    basename = os.path.basename(dir_path)
    if '.' in basename and len(basename) > 1 and not basename.startswith('.'):
        dir_path = os.path.dirname(path)

    if not dir_path or dir_path in ('.', './', '..'):
        return True

    try:
        os.makedirs(dir_path, exist_ok=True)
        return True
    except PermissionError:
        print(f"❌ 权限不足，无法创建目录: {dir_path}")
        return False
    except Exception as e:
        print(f"❌ 创建目录失败: {dir_path}, 错误: {type(e).__name__}: {e}")
        return False
