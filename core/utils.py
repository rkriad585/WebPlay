import os
import subprocess
from datetime import datetime
from rich.console import Console
from rich.style import Style

console = Console()

_LOG_FILE = None
_BANNER_WIDTH = 43


def set_log_file(path):
    global _LOG_FILE
    _LOG_FILE = path


def _write_log(message):
    if _LOG_FILE:
        try:
            with open(_LOG_FILE, 'a') as f:
                f.write(f"[{datetime.now().isoformat()}] {message}\n")
        except OSError:
            pass


def _right_pad(text, width):
    return text + ' ' * max(0, width - len(text))


def _banner_line(content, width=_BANNER_WIDTH):
    return '│ ' + _right_pad(content, width - 2) + ' │'


def _get_git_commit():
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--short', 'HEAD'],
            capture_output=True, text=True, timeout=5,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return 'unknown'


def _get_project_version():
    try:
        from importlib.metadata import version, PackageNotFoundError
        try:
            return version('webplay')
        except PackageNotFoundError:
            pass
    except ImportError:
        pass
    version_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.version')
    if os.path.isfile(version_file):
        with open(version_file) as f:
            return f.read().strip()
    return '0.0.0'


def _make_banner(project='webplay', author='RK Riad Khan', repo='rkriad585/WebPlay'):
    version = _get_project_version()
    commit = _get_git_commit()
    W = _BANNER_WIDTH

    half = (W - len(project) - 2) // 2
    top = '╭' + '─' * half + ' ' + project + ' ' + '─' * (W - half - len(project) - 3) + '╮'

    lines = [
        top,
        _banner_line(f'Author : {author}'),
        _banner_line(f'Version: {version}'),
        _banner_line(f'Commit : {commit}'),
        _banner_line(f'GitHub : {repo}'),
        '╰' + '─' * (W - 2) + '╯',
    ]
    return '\n'.join(lines)


def print_banner():
    banner = _make_banner()
    style = Style(color='cyan', bold=True)
    console.print(banner, style=style, highlight=False)

def log_info(message):
    console.print(f"[bold blue][INFO][/bold blue] {message}")
    _write_log(f"[INFO] {message}")

def log_success(message):
    console.print(f"[bold green][SUCCESS][/bold green] {message}")
    _write_log(f"[SUCCESS] {message}")

def log_warning(message):
    console.print(f"[bold yellow][WARNING][/bold yellow] {message}")
    _write_log(f"[WARNING] {message}")

def log_error(message):
    console.print(f"[bold red][ERROR][/bold red] {message}")
    _write_log(f"[ERROR] {message}")

def format_size(size_bytes):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"
