import os
import random
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
import pyfiglet

console = Console()

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

def log_success(message):
    console.print(f"[bold green][SUCCESS][/bold green] {message}")

def log_warning(message):
    console.print(f"[bold yellow][WARNING][/bold yellow] {message}")

def log_error(message):
    console.print(f"[bold red][ERROR][/bold red] {message}")

def format_size(size_bytes):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"
