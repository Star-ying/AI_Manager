# database/config.py
import json
import os
from typing import Any

from Progress.utils.resource_helper import get_app_path, get_internal_path


class ConfigManager:
    def __init__(self):
        # 🔧 使用 get_internal_path 加载内置默认配置（可打包）
        self.BASE_CONFIG_FILE = get_internal_path("database", "base_config.json")

        # 📁 使用 get_app_path 定位外部配置文件（不可打包！）
        self.CONFIG_FILE = os.path.join(get_app_path(), "config.json")

        self.DEFAULT_CONFIG = None
        self.config = self.load_config()

    def load_config(self) -> dict:
        # 如果没有外部 config.json，自动生成
        if not os.path.exists(self.CONFIG_FILE):
            print(f"🔧 配置文件 {self.CONFIG_FILE} 不存在，正在创建默认配置...")
            default = self._load_default()
            self.save_config(default)
            return default.copy()

        try:
            with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                user_config = json.load(f)

            default = self._load_default()
            config = default.copy()
            self.deep_update(config, user_config)
            return config
        except (json.JSONDecodeError, PermissionError) as e:
            print(f"⚠️ 读取配置失败：{e}。使用默认配置并备份原文件。")
            if os.path.exists(self.CONFIG_FILE):
                os.rename(self.CONFIG_FILE, self.CONFIG_FILE + ".backup")
            default = self._load_default()
            self.save_config(default)
            return default.copy()

    def _load_default(self) -> dict:
        if self.DEFAULT_CONFIG is None:
            with open(self.BASE_CONFIG_FILE, 'r', encoding='utf-8') as f:
                self.DEFAULT_CONFIG = json.load(f)
        return self.DEFAULT_CONFIG

    def deep_update(self, default: dict, override: dict):
        for k, v in override.items():
            if isinstance(v, dict) and k in default and isinstance(default[k], dict):
                self.deep_update(default[k], v)
            else:
                default[k] = v

    def save_config(self, config: dict) -> bool:
        try:
            # 确保外部 config.json 所在目录存在
            os.makedirs(os.path.dirname(self.CONFIG_FILE), exist_ok=True)
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ 保存配置失败：{e}")
            return False

    def get(self, *keys) -> Any:
        data = self.config
        try:
            for k in keys:
                data = data[k]
            return data
        except KeyError as e:
            raise KeyError(f"配置项 {' -> '.join(keys)} 未找到") from e

    def set_resource_path(self, new_path: str) -> bool:
        """
        设置新的资源根目录（如 D:\\MyResources）
        自动创建 music_path 和 document_path 子目录
        """
        abs_new_path = os.path.abspath(new_path)
        if not os.path.exists(abs_new_path):
            try:
                os.makedirs(abs_new_path, exist_ok=True)
                print(f"📁 已创建资源根目录: {abs_new_path}")
            except Exception as e:
                print(f"❌ 无法创建路径 {abs_new_path}: {e}")
                return False

        # 获取子路径（如 /Music）
        temp = self.config["paths"]["resources"]
        success = True
        for sub_key in ["music_path", "document_path"]:
            sub_rel = temp[sub_key].strip("/\\")
            sub_abs = os.path.join(abs_new_path, sub_rel)
            if not os.path.exists(sub_abs):
                try:
                    os.makedirs(sub_abs, exist_ok=True)
                    print(f"📁 已创建子目录: {sub_abs}")
                except Exception as e:
                    print(f"❌ 创建子路径失败: {sub_abs}, {e}")
                    success = False

        if success:
            # 更新内存中的配置
            self.config["paths"]["resource_path"] = abs_new_path
            # 保存到 config.json
            self.save_config(self.config)
            print(f"✅ 资源路径已更新为: {abs_new_path}")
        return success


# 全局实例
config = ConfigManager()
