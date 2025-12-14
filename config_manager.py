import json
import os

# Get the absolute path to the directory where this file is located
current_dir = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(current_dir, "config.cfg")

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
            config = DEFAULT_CONFIG.copy()
            # Still check env var even if new config created
            env_key = os.environ.get("DEEPSEEK_API_KEY")
            if env_key:
                config["api_key"] = env_key
            return config
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except (json.JSONDecodeError, IOError):
            config = DEFAULT_CONFIG.copy()

        # Environment variable override for API Key
        env_key = os.environ.get("DEEPSEEK_API_KEY")
        if env_key:
            config["api_key"] = env_key
            
        return config

    def save_config(self, config_data):
        self.config = config_data
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=4)

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value
        self.save_config(self.config)
