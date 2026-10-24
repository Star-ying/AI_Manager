# database/config.py
import json
import os
import sys
from typing import Any, Dict, Optional
from pathlib import Path


# 确保 Progress 包可导入
if 'Progress' not in sys.modules:
    project_root = str(Path(__file__).parent.parent)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    # 尝试导入 Progress，验证可用性
    try:
        import Progress
    except ImportError as e:
        print(f"⚠️ 无法导入 Progress 模块，请检查路径: {project_root}, 错误: {e}")


class ConfigManager:
    def __init__(self):
        # 延迟导入 resource_helper，避免启动时循环依赖
        from Progress.utils.resource_helper import get_internal_path, get_app_path

        self.BASE_CONFIG_FILE = get_internal_path("database", "base_config.json")
        self.CONFIG_FILE = os.path.join(get_app_path(), "config.json")
        # 密钥外置：项目根 .env（照 AI_talk setting.py 同款 dotenv_values 机制，不入 git）
        self.ENV_FILE = Path(__file__).resolve().parent.parent / ".env"
        self.DEFAULT_CONFIG: Optional[Dict] = None
        self.config = self.load_config()
        self._overlay_env()

    def _overlay_env(self):
        """用 .env 里的密钥覆盖内存配置（优先级最高；文件缺失则保持原样）"""
        if not os.path.exists(self.ENV_FILE):
            return
        try:
            try:
                from dotenv import dotenv_values
                env = {k: v for k, v in dotenv_values(self.ENV_FILE).items() if v}
            except ImportError:
                env = {}
                for line in open(self.ENV_FILE, encoding="utf-8"):
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, _, v = line.partition("=")
                        v = v.split("#")[0].strip()  # 剔除行内注释（AI_talk .env 同款写法）
                        if v:
                            env[k.strip()] = v
        except Exception as e:
            print(f"⚠️ .env 读取失败，保持 json 配置: {e}")
            return
        mapping = {
            "LLM_API_KEY": ("ai_model", "api_key"),
            "LLM_BASE_URL": ("ai_model", "base_url"),
            "LLM_MODEL": ("ai_model", "model"),
        }
        for k, path in mapping.items():
            if k in env:
                self.deep_update(self.config, {path[0]: {path[1]: env[k]}})

    def _load_default(self) -> Dict:
        """加载默认配置模板"""
        if self.DEFAULT_CONFIG is None:
            if not os.path.exists(self.BASE_CONFIG_FILE):
                raise FileNotFoundError(f"❌ 默认配置文件不存在: {self.BASE_CONFIG_FILE}")
            try:
                with open(self.BASE_CONFIG_FILE, 'r', encoding='utf-8') as f:
                    self.DEFAULT_CONFIG = json.load(f)
            except Exception as e:
                raise RuntimeError(f"❌ 无法读取默认配置文件: {e}")
        return self.DEFAULT_CONFIG.copy()

    def load_config(self) -> Dict:
        """加载用户配置，若不存在则生成"""
        if not os.path.exists(self.CONFIG_FILE):
            print(f"🔧 配置文件 {self.CONFIG_FILE} 不存在，正在基于默认模板创建...")
            default = self._load_default()
            if self.save_config(default):
                print(f"✅ 默认配置已生成: {self.CONFIG_FILE}")
            else:
                print(f"❌ 默认配置生成失败，请检查路径权限: {os.path.dirname(self.CONFIG_FILE)}")
            return default

        try:
            with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
            default = self._load_default()
            merged = default.copy()
            self.deep_update(merged, user_config)
            return merged
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            print(f"⚠️ 配置文件格式错误或编码异常: {e}")
            return self._recover_from_corrupted()
        except PermissionError as e:
            print(f"⚠️ 无权限读取配置文件: {e}")
            return self._recover_from_corrupted()
        except Exception as e:
            print(f"⚠️ 未知错误导致配置加载失败: {type(e).__name__}: {e}")
            return self._recover_from_corrupted()

    def _recover_from_corrupted(self) -> Dict:
        """配置损坏时尝试备份并重建"""
        backup_file = self.CONFIG_FILE + ".backup"
        try:
            if os.path.exists(self.CONFIG_FILE):
                os.rename(self.CONFIG_FILE, backup_file)
                print(f"📁 原始损坏配置已备份为: {backup_file}")
            default = self._load_default()
            self.save_config(default)
            print(f"✅ 已使用默认配置重建 {self.CONFIG_FILE}")
            return default
        except Exception as e:
            print(f"❌ 自动恢复失败: {e}，将返回内存中默认配置")
            return self._load_default()

    def deep_update(self, default: Dict, override: Dict):
        """递归更新嵌套字典"""
        for k, v in override.items():
            if (k in default and isinstance(default[k], dict) and 
                    isinstance(v, dict)):
                self.deep_update(default[k], v)
            else:
                default[k] = v

    def save_config(self, config: Dict) -> bool:
        """保存当前配置到 config.json"""
        try:
            from Progress.utils.resource_helper import ensure_directory

            config_dir = os.path.dirname(self.CONFIG_FILE)
            if not ensure_directory(config_dir):
                print(f"❌ 无法创建配置目录: {config_dir}")
                return False

            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            return True
        except PermissionError:
            print(f"❌ 权限不足，无法写入配置文件: {self.CONFIG_FILE}")
            return False
        except Exception as e:
            print(f"❌ 保存配置失败: {type(e).__name__}: {e}")
            return False

    def get(self, *keys, default=None) -> Any:
        """
        安全获取配置项
        示例: config.get("ai_model", "api_key", default="none")
        """
        data = self.config
        try:
            for k in keys:
                data = data[k]
            return data
        except (KeyError, TypeError):
            return default

    def set(self, value, *keys):
        """
        设置配置项（内存中），需调用 save() 才持久化
        示例: config.set("new_value", "app", "name")
        """
        data = self.config
        for k in keys[:-1]:
            if k not in data or not isinstance(data[k], dict):
                data[k] = {}
            data = data[k]
        data[keys[-1]] = value

    def save(self) -> bool:
        """将当前内存中的配置保存到文件"""
        return self.save_config(self.config)

# 全局单例
config = ConfigManager()
