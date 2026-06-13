import os
import platform

PROJECT = "webplay"
NAMESPACE = "neostore"


def _home():
    return os.path.expanduser("~")


def _config_root():
    home = _home()
    if platform.system() == "Windows":
        base = os.environ.get("USERPROFILE", home)
    else:
        base = home
    return os.path.join(base, ".config", NAMESPACE)


def get_config_dir():
    return os.path.join(_config_root(), PROJECT)


def get_data_dir():
    return get_config_dir()


def get_logs_dir():
    return get_config_dir()


def get_downloads_dir():
    return os.path.join(_home(), "Downloads", NAMESPACE, PROJECT)


def get_config_path():
    return os.path.join(get_config_dir(), "config.toml")


def get_db_path():
    return os.path.join(get_data_dir(), "webplay.db")


def get_log_path():
    return os.path.join(get_logs_dir(), "history.log")


def get_key_path():
    return os.path.join(get_config_dir(), ".webplay_key.txt")


def get_cache_dir():
    return os.path.join(get_config_dir(), ".webplay_cache")


def ensure_all():
    for d in [get_config_dir(), get_data_dir(), get_logs_dir(), get_downloads_dir(), get_cache_dir()]:
        os.makedirs(d, exist_ok=True)
