import json
import os
from typing import Any
class ConfigManager:
    def __init__(self):
        # 配置文件名
        self.BASE_CONFIG_FILE = "./database/base_config.json"
        self.CONFIG_FILE = "./config.json"
        self.DEFAULT_CONFIG = ""
        # 默认配置
        with open(self.BASE_CONFIG_FILE,'r',encoding='utf-8') as f:
            self.DEFAULT_CONFIG = json.load(f)
        self.config = self.load_config()

    def load_config(self)-> json:
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

    def save_config(self, config)-> bool:
        """
        保存配置到 JSON 文件
        """
        try:
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存配置失败：{e}")
            return False

    def update_key(self, *section, key, value)-> bool:
        """增加或修改设置"""
        try:
            data = self.config
            for k in section:
                data = data[k]
            data[key] = value
            self.save_config(self.config)
            return True
        except Exception:
            return False

    def create_path(self,new_path)-> bool:
        if not os.path.exists(new_path):
            try:
                os.makedirs(new_path)
                print(f"路径 {new_path} 已创建")
                return True
            except Exception as e:
                print(f"无法创建路径 {new_path}: {e}")
                return False
        return True

    def set_resource_path(self, new_path)-> bool:
        """设置资源存储路径"""
        if not self.create_path(new_path):
            return False
        self.config["paths"]["resource_path"] = new_path
        temp = self.config["paths"]["resources"]
        for k in temp:
            self.create_path(new_path+temp[k])
        self.save_config(self.config)
        print(f"资源路径已设置为: {new_path}")
        return True

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

""" # 使用配置（推荐方式）

#增加或修改新的设置配置
config.update_key("shortcuts",key = "exit",value = "Ctrl+C")
config.update_key("shortcuts",key = "select_all",value = "Shift+Alt+A")

#修改资源路径
config.set_resource_path("./resoures")

#获取设置配置
display = config.get("display")

# 获取 AI_model 配置
api_key = config.get("ai_model", "api_key")
model = config.get("ai_model", "model") """