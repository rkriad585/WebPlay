import os
import secrets
import shutil
import socket
import subprocess
import platform

import click

from app import app, socketio
from core.utils import print_banner, log_info, log_success, log_error, log_warning
from config import load_toml, save_config
from core.paths import get_key_path


def _detect_install_cmd():
    system = platform.system()
    if system == 'Linux':
        for pm, pkgs in [('apt', ['install', '-y', 'ffmpeg']), ('dnf', ['install', '-y', 'ffmpeg']),
                         ('yum', ['install', '-y', 'ffmpeg']), ('pacman', ['-S', '--noconfirm', 'ffmpeg']),
                         ('apk', ['add', 'ffmpeg']), ('zypper', ['install', '-y', 'ffmpeg'])]:
            if shutil.which(pm):
                return ['sudo', pm] + pkgs
    elif system == 'Darwin' and shutil.which('brew'):
        return ['brew', 'install', 'ffmpeg']
    elif system == 'Windows':
        for pm, pkgs in [('winget', ['install', 'FFmpeg']), ('choco', ['install', '-y', 'ffmpeg']),
                         ('scoop', ['install', 'ffmpeg'])]:
            if shutil.which(pm):
                return [pm] + pkgs
    return None


def get_lan_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.1)
        s.connect(("1.1.1.1", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        pass
    return '127.0.0.1'


def get_public_url():
    domain = os.environ.get('WEBPLAY_DOMAIN')
    if domain:
        return domain
    fqdn = socket.getfqdn()
    if fqdn and '.' in fqdn and not fqdn.startswith('localhost') and not fqdn.endswith('.local'):
        if fqdn not in ('127.0.0.1', '::1'):
            return fqdn
    return None


def _print_urls(port, key=None):
    lan = get_lan_ip()
    qs = f'?key={key}' if key else ''
    log_info(f"Local:  http://127.0.0.1:{port}{qs}")
    log_info(f"LAN:    http://{lan}:{port}{qs}")
    public = get_public_url()
    if public:
        log_info(f"Domain: http://{public}:{port}{qs}")


@click.group()
def cli():
    """WebPlay: Media Player"""
    pass


@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--config', 'config_path', default=None, help='Path to config.toml')
def path(path, config_path):
    save_config({"path": os.path.abspath(path)}, config_path)
    load_toml(config_path)
    print_banner()
    log_success(f"Media path: {path}")


@cli.command()
@click.option('--port', default=5000)
@click.option('--domain', envvar='WEBPLAY_DOMAIN', default=None, help='Public domain name')
@click.option('--config', 'config_path', default=None, help='Path to config.toml')
def free(port, domain, config_path):
    if config_path:
        load_toml(config_path)
    print_banner()
    app.config['API_KEY'] = None
    if domain:
        os.environ['WEBPLAY_DOMAIN'] = domain
    _print_urls(port)
    socketio.run(app, host='0.0.0.0', port=port, debug=False)


@cli.command()
@click.option('--port', default=5000)
@click.option('--domain', envvar='WEBPLAY_DOMAIN', default=None, help='Public domain name')
@click.option('--key', 'key_arg', default=None, help='Use a specific API key (default: random)')
@click.option('--config', 'config_path', default=None, help='Path to config.toml')
def start(port, domain, key_arg, config_path):
    if config_path:
        load_toml(config_path)
    print_banner()
    key = key_arg or secrets.token_urlsafe(16)
    app.config['API_KEY'] = key
    if domain:
        os.environ['WEBPLAY_DOMAIN'] = domain
    kf = get_key_path()
    try:
        with open(kf, 'w') as f:
            f.write(key + '\n')
    except OSError:
        pass
    _print_urls(port, key)
    if key_arg:
        log_info(f"Using provided key: {key}")
    log_warning(f"API key saved to {kf}")
    socketio.run(app, host='0.0.0.0', port=port, debug=False)


@cli.command()
def key():
    """Print the saved API key from the last start."""
    kf = get_key_path()
    if os.path.exists(kf):
        with open(kf) as f:
            saved = f.read().strip()
        if saved:
            log_info(f"API key: {saved}")
            return
    log_error("No saved API key found. Run 'python app.py start' first.")


@cli.command()
def install_ffmpeg():
    """Detect system and auto-install FFmpeg."""
    print_banner()
    if shutil.which('ffmpeg') and shutil.which('ffprobe'):
        log_success("FFmpeg is already installed!")
        return

    cmd = _detect_install_cmd()
    if not cmd:
        log_error("Could not detect package manager. Install FFmpeg manually:")
        log_info("  Ubuntu/Debian: sudo apt install ffmpeg")
        log_info("  Fedora: sudo dnf install ffmpeg")
        log_info("  Arch: sudo pacman -S ffmpeg")
        log_info("  macOS: brew install ffmpeg")
        log_info("  Windows: winget install FFmpeg")
        return

    log_warning(f"About to run: {' '.join(cmd)}")
    if click.confirm("Proceed with installation?", default=True):
        try:
            subprocess.run(cmd, check=True)
            log_success("FFmpeg installed successfully!")
        except subprocess.CalledProcessError:
            log_error("Installation failed. Install FFmpeg manually.")
        except FileNotFoundError:
            log_error("sudo not available. Run manually:")
            log_info(f"  {' '.join(cmd)}")
    else:
        log_info("Installation skipped.")


def main():
    cli()


if __name__ == '__main__':
    main()
