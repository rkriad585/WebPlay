import os
import json

CONFIG_FILE = 'webplay_settings.json'
CACHE_DIR = os.path.join(os.getcwd(), '.webplay_cache')

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-webplay-secure'
    DATABASE_PATH = 'webplay.db'

    @staticmethod
    def ensure_dirs():
        if not os.path.exists(CACHE_DIR):
            try:
                os.makedirs(CACHE_DIR)
            except OSError:
                pass

    @staticmethod
    def load_settings():
        path = os.getcwd()
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    data = json.load(f)
                    path = data.get('media_path', path)
            except (json.JSONDecodeError, OSError):
                pass
        return path

    @staticmethod
    def save_settings(path):
        with open(CONFIG_FILE, 'w') as f:
            json.dump({'media_path': path}, f)
