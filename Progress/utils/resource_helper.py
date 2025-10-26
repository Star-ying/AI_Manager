# utils/resource_helper.py

import os
import sys
from typing import Optional

def get_app_path() -> str:
    """获取应用根目录（用于 config.json、logs/ 等可写目录）"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_internal_path(*relative_path_parts) -> str:
    """获取内嵌资源路径（用于访问 _MEIPASS 中的模型、base_config 等）"""
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, *relative_path_parts)

def resource_path(*sub_paths: str) -> str:
    """
    通用用户资源路径解析（基于 config 的 resource_path）
    用于 Music、Documents、logs 等外部可写路径
    """
    from database.config import config

    raw_base = config.get("paths", "resource_path")  # 如 "resources" 或 "./data"

    if os.path.isabs(raw_base):
        base_path = raw_base
    else:
        base_path = os.path.join(get_app_path(), raw_base)

    full_path = os.path.normpath(base_path)
    for part in sub_paths:
        clean_part = str(part).strip().lstrip('./\\/\\')
        for p in clean_part.replace('\\', '/').split('/'):
            if p:
                full_path = os.path.join(full_path, p)
    return os.path.normpath(full_path)

def ensure_directory(path: str) -> bool:
    """确保目录存在"""
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except Exception as e:
        print(f"❌ 创建目录失败: {path}, 错误: {e}")
        return False
