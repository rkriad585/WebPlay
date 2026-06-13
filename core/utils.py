import os
import random
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
import pyfiglet

console = Console()

_LOG_FILE = None


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


def print_banner():
    """Prints the WebPlay ASCII Banner."""
    fonts = ['slant', 'standard', 'doom', 'cybermedium']
    try:
        f = pyfiglet.Figlet(font=random.choice(fonts))
        banner = f.renderText('WebPlay')
    except:
        banner = "WebPlay"
    
    text = Text(banner, style="bold cyan")
    console.print(text)
    
    console.print(Panel.fit(
        "[bold green]Media Player & Streamer[/bold green]\n"
        "[italic]Author: RKRIAD585[/italic]",
        border_style="cyan"
    ))

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
