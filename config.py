import os
import tomllib
from core.paths import get_config_path, get_db_path, get_cache_dir, get_downloads_dir, ensure_all

_config_data = {}
SETTINGS_PATH = None


def load_toml(config_path=None):
    global _config_data
    path = config_path or get_config_path()
    _config_data = {}
    if os.path.exists(path):
        try:
            with open(path, 'rb') as f:
                _config_data = tomllib.load(f)
        except Exception:
            pass
    return _config_data


def get_setting(*keys, default=None):
    d = _config_data
    for k in keys:
        if isinstance(d, dict):
            d = d.get(k)
        else:
            return default
    return d if d is not None else default


def _escape_toml(val):
    if isinstance(val, bool):
        return str(val).lower()
    if isinstance(val, int):
        return str(val)
    if isinstance(val, float):
        return str(val)
    s = str(val).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{s}"'


def save_config(data, config_path=None):
    path = config_path or get_config_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    parts = []
    for section, keys in [
        ("server", ["port", "domain"]),
        ("auth", ["api_key"]),
        ("media", ["path"]),
        ("transcode", ["preset", "crf"]),
    ]:
        sv = {k: data.get(k) for k in keys if k in data}
        if not sv:
            continue
        parts.append(f"[{section}]")
        for k, v in sv.items():
            parts.append(f'{k} = {_escape_toml(v)}')
        parts.append("")
    with open(path, "w") as f:
        f.write("\n".join(parts) + "\n")
    global _config_data
    _config_data = data


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-webplay-secure'
    DATABASE_PATH = get_db_path()
    CACHE_DIR = get_cache_dir()

    @staticmethod
    def ensure_dirs():
        ensure_all()

    @staticmethod
    def load_settings():
        load_toml()
        return get_setting("media", "path") or os.getcwd()

    @staticmethod
    def save_settings(path):
        save_config({"path": path})
