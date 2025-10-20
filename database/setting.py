import json
import os

# 配置文件名
CONFIG_FILE = "config.json"

# 默认配置
DEFAULT_CONFIG = {
    "shortcuts": {
        "save": "Ctrl+S",
        "open": "Ctrl+O",
        "exit": "Ctrl+Q",
        "undo": "Ctrl+Z"
    },
    "display": {
        "theme": "light",
        "window_size": [800, 600],
        "font": "Arial",
        "font_size": 12
    },
    "paths": {
        "resource_path": "./resources"
    }
}

def load_config():
    """
    加载配置文件。如果不存在或损坏，则创建默认配置。
    """
    if not os.path.exists(CONFIG_FILE):
        print(f"配置文件 {CONFIG_FILE} 不存在，正在创建默认配置...")
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()

    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            user_config = json.load(f)

        # 使用默认配置作为基础，更新用户配置（防止缺失字段）
        config = DEFAULT_CONFIG.copy()
        deep_update(config, user_config)

        return config
    except (json.JSONDecodeError, PermissionError) as e:
        print(f"读取配置失败：{e}。使用默认配置并备份原文件。")
        if os.path.exists(CONFIG_FILE):
            os.rename(CONFIG_FILE, CONFIG_FILE + ".backup")
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()

def deep_update(default, override):
    """
    递归更新嵌套字典，保留未被覆盖的键
    """
    for key, value in override.items():
        if isinstance(value, dict) and key in default and isinstance(default[key], dict):
            deep_update(default[key], value)
        else:
            default[key] = value

def save_config(config):
    """
    保存配置到 JSON 文件
    """
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        print(f"配置已保存至 {CONFIG_FILE}")
    except Exception as e:
        print(f"保存配置失败：{e}")

def update_shortcut(action, key_combination):
    """修改快捷键"""
    config = load_config()
    if action in config["shortcuts"]:
        config["shortcuts"][action] = key_combination
        save_config(config)
        print(f"快捷键 '{action}' 已更新为 '{key_combination}'")
    else:
        print(f"无效的操作: {action}")

def set_resource_path(new_path):
    """设置资源存储路径"""
    if not os.path.exists(new_path):
        try:
            os.makedirs(new_path)
            print(f"路径 {new_path} 已创建")
        except Exception as e:
            print(f"无法创建路径 {new_path}: {e}")
            return False
    config = load_config()
    config["paths"]["resource_path"] = new_path
    save_config(config)
    print(f"资源路径已设置为: {new_path}")
    return True

def get_display_settings():
    """获取显示设置"""
    config = load_config()
    return config["display"]
