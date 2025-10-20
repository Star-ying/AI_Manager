import json
import os
from pathlib import Path
from typing import Any
class ConfigManager:
    def __init__(self):
        # 配置文件名
        self.BASE_CONFIG_FILE = "./database/base_config.json"
        self.CONFIG_FILE = "config.json"
        self.DEFAULT_CONFIG = ""
        # 默认配置
        with open(self.BASE_CONFIG_FILE,'r',encoding='utf-8') as f:
            self.DEFAULT_CONFIG = json.load(f)
        self.config = self.load_config()

    def load_config(self):
        """
        加载配置文件。如果不存在或损坏，则创建默认配置。
        """
        if not os.path.exists(self.CONFIG_FILE):
            print(f"配置文件 {self.CONFIG_FILE} 不存在，正在创建默认配置...")
            self.save_config(self.DEFAULT_CONFIG)
            return self.DEFAULT_CONFIG.copy()

        try:
            with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                user_config = json.load(f)

            # 使用默认配置作为基础，更新用户配置（防止缺失字段）
            config = self.DEFAULT_CONFIG.copy()
            self.deep_update(config, user_config)

            return config
        except (json.JSONDecodeError, PermissionError) as e:
            print(f"读取配置失败：{e}。使用默认配置并备份原文件。")
            if os.path.exists(self.CONFIG_FILE):
                os.rename(self.CONFIG_FILE, self.CONFIG_FILE + ".backup")
            self.save_config(self.DEFAULT_CONFIG)
            return self.DEFAULT_CONFIG.copy()

    def deep_update(self, default, override):
        """
        递归更新嵌套字典，保留未被覆盖的键
        """
        for key, value in override.items():
            if isinstance(value, dict) and key in default and isinstance(default[key], dict):
                self.deep_update(default[key], value)
            else:
                default[key] = value

    def save_config(self, config):
        """
        保存配置到 JSON 文件
        """
        try:
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            print(f"配置已保存至 {self.CONFIG_FILE}")
        except Exception as e:
            print(f"保存配置失败：{e}")

    def update_shortcut(self, action, key_combination):
        """修改快捷键"""
        config = self.load_config()
        if action in config["shortcuts"]:
            config["shortcuts"][action] = key_combination
            self.save_config(config)
            print(f"快捷键 '{action}' 已更新为 '{key_combination}'")
        else:
            print(f"无效的操作: {action}")

    def set_resource_path(self, new_path):
        """设置资源存储路径"""
        if not os.path.exists(new_path):
            try:
                os.makedirs(new_path)
                print(f"路径 {new_path} 已创建")
            except Exception as e:
                print(f"无法创建路径 {new_path}: {e}")
                return False
        config = self.load_config()
        config["paths"]["resource_path"] = new_path
        self.save_config(config)
        print(f"资源路径已设置为: {new_path}")
        return True

    def get_display_settings(self):
        """获取显示设置"""
        config = self.load_config()
        return config["display"]

    def add_json_property(self, section, key, value):
        """
        向 JSON 文件的指定 section 添加一个键值对
        如果 section 不存在，则自动创建
        """
        file_path = Path(self.self.config_file)

        # 1. 读取现有配置
        if not file_path.exists():
            print(f"文件 {file_path} 不存在，创建新文件。")
            data = {}
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    print("警告：JSON 解析错误，使用空配置。")
                    data = {}

        # 2. 确保 section 存在（支持嵌套字典）
        if section not in data:
            data[section] = {}

        # 3. 添加或更新属性
        data[section][key] = value

        # 4. 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        print(f"已添加 {section}.{key} = {value}")

    def get(self, *keys) -> Any:
        """
        安全获取嵌套配置项
        示例：config.get("ai_model", "api_key")
        """
        data = self.config
        try:
            for k in keys:
                data = data[k]
            return data
        except KeyError as e:
            raise KeyError(f"配置项 {' -> '.join(keys)} 未找到") from e

# 全局实例（单例模式）
config = ConfigManager()
# 使用配置（推荐方式）

# 获取 AI_model 配置
api_key = config.get("ai_model", "api_key")
model = config.get("ai_model", "model")

# 获取语音识别设置
lang = config.get("voice_recognition", "language")
timeout = config.get("voice_recognition", "timeout")
phrase_timeout = config.get("voice_recognition","phrase_timeout")

# 获取 TTS 设置
rate = config.get("tts", "rate")
volume = config.get("tts", "volume")

# 获取路径
resource_path = config.get("paths","resource_path")
music_path = config.get("paths", "default_music_path")
doc_path = config.get("paths", "default_document_path")

# 获取应用信息
app_name = config.get("app", "name")
app_version = config.get("app", "version")
