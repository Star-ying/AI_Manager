import sys
import os

def resource_path(*relative_path_parts) -> str:
    """
    获取打包后安全的资源路径。
    支持传入多段路径，也支持传入类似 './resources/Music' 的字符串（自动拆分）。
    """
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        # 使用当前文件的上级目录作为项目根目录（稳定）
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # 如果第一个参数是字符串且包含 / 或 \，尝试自动拆分
    if len(relative_path_parts) == 1 and isinstance(relative_path_parts[0], str):
        path_str = relative_path_parts[0]
        # 处理 ./ 开头
        if path_str.startswith('./'):
            path_str = path_str[2:]
        # 处理 / 开头
        elif path_str.startswith('/'):
            path_str = path_str[1:]
        # 按 / 或 \ 分割
        parts = path_str.replace('\\', '/').split('/')
        return os.path.join(base_path, *parts)
    
    # 正常处理多参数情况
    return os.path.join(base_path, *relative_path_parts)
