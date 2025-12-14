import json
import os

CONFIG_FILE = "config.cfg"

DEFAULT_CONFIG = {
    "api_url": "https://api.siliconflow.cn/v1/chat/completions",
    "api_key": "YOUR_API_KEY_HERE",
    "model": "deepseek-ai/DeepSeek-OCR"
}

class ConfigManager:
    def __init__(self, config_file=CONFIG_FILE):
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self):
        if not os.path.exists(self.config_file):
            self.save_config(DEFAULT_CONFIG)
            return DEFAULT_CONFIG
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return DEFAULT_CONFIG

    def save_config(self, config_data):
        self.config = config_data
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=4)

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value
        self.save_config(self.config)
