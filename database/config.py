import json
import os
from typing import Any, Dict

class ConfigManager:
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = {}
        self.load_config()

    def load_config(self):
        """加载 JSON 配置文件，并应用环境变量覆盖"""
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(f"配置文件 {self.config_file} 不存在！")

        with open(self.config_file, 'r', encoding='utf-8') as f:
            try:
                self.config = json.load(f)
            except json.JSONDecodeError as e:
                raise ValueError(f"配置文件格式错误：{e}")

        # 应用环境变量覆盖（优先级最高）
        self._apply_env_overrides()

    def _apply_env_overrides(self):
        """从环境变量中读取配置进行覆盖（如 DASHSCOPE_API_KEY）"""
        env_mapping = {
            "DASHSCOPE_API_KEY": ("ai_model", "api_key"),
            "DASHSCOPE_MODEL": ("ai_model", "model"),
            "VOICE_RECOGNITION_LANGUAGE": ("voice_recognition", "language"),
            "VOICE_TIMEOUT": ("voice_recognition", "timeout"),
            "VOICE_PHRASE_TIMEOUT": ("voice_recognition", "phrase_timeout"),
            "TTS_RATE": ("tts", "rate"),
            "TTS_VOLUME": ("tts", "volume"),
            "RESOURES_PATH": ("paths","resource_path"),
            "DEFAULT_MUSIC_PATH": ("paths", "default_music_path"),
            "DEFAULT_DOCUMENT_PATH": ("paths", "default_document_path")
        }

        for env_key, (section, key) in env_mapping.items():
            env_value = os.getenv(env_key)
            if env_value is not None:
                # 自动转换数字类型
                if isinstance(self.config[section][key], bool):
                    self.config[section][key] = env_value.lower() in ('true', '1', 'yes')
                elif isinstance(self.config[section][key], (int, float)):
                    try:
                        self.config[section][key] = type(self.config[section][key])(env_value)
                    except (ValueError, TypeError):
                        print(f"警告：无法转换环境变量 {env_key} 的值 '{env_value}' 为正确类型")
                else:
                    self.config[section][key] = env_value

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

    def set_temp(self, *keys, value: Any):
        """
        临时修改内存中的配置（不保存到文件）
        """
        data = self.config
        for k in keys[:-1]:
            data = data[k]
        data[keys[-1]] = value


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