import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, 'webplay_settings.json')
CACHE_DIR = os.path.join(BASE_DIR, '.webplay_cache')

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-webplay-secure'
    DATABASE_PATH = os.path.join(BASE_DIR, 'webplay.db')

    @staticmethod
    def ensure_dirs():
        if not os.path.exists(CACHE_DIR):
            try:
                os.makedirs(CACHE_DIR)
            except OSError:
                pass

    @staticmethod
    def load_settings():
        path = BASE_DIR
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
