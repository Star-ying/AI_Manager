import json
import os
from typing import Any

from Progress.utils.resource_helper import resource_path


class ConfigManager:
    def __init__(self):
        self.BASE_CONFIG_FILE = resource_path("database/base_config.json")
        self.CONFIG_FILE = resource_path("config.json")
        self.DEFAULT_CONFIG = None
        self.config = self.load_config()

    def load_config(self) -> dict:
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
        if not hasattr(self, '_default'):
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
        if not os.path.exists(new_path):
            try:
                os.makedirs(new_path)
            except Exception as e:
                print(f"❌ 无法创建路径 {new_path}: {e}")
                return False

        temp = self.config["paths"]["resources"]
        success = True
        for sub in [temp["music_path"], temp["document_path"]]:
            p = new_path + sub
            if not os.path.exists(p):
                try:
                    os.makedirs(p)
                except Exception as e:
                    print(f"❌ 创建子路径失败: {p}, {e}")
                    success = False
        if success:
            self.config["paths"]["resource_path"] = new_path
            self.save_config(self.config)
            print(f"✅ 资源路径已更新为: {new_path}")
        return success


# 全局实例
config = ConfigManager()
