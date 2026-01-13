import os
import json

CONFIG_FILE = 'webplay_settings.json'
CACHE_DIR = os.path.join(os.getcwd(), '.webplay_cache')

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-webplay-secure'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///webplay.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Create cache dir if not exists
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

    @staticmethod
    def load_settings():
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
                return data.get('media_path', os.getcwd())
        return os.getcwd()

    @staticmethod
    def save_settings(path):
        with open(CONFIG_FILE, 'w') as f:
            json.dump({'media_path': path}, f)
