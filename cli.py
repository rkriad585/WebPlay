import os
import sys
import re
import secrets
import shutil
import socket
import subprocess
import platform
import textwrap
import tempfile
import urllib.request
from importlib.metadata import version as _pkg_version, PackageNotFoundError

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


PROJECT_NAME = "webplay"
PROJECT_REPO = "rkriad585/WebPlay"
PROJECT_RAW = f"https://raw.githubusercontent.com/{PROJECT_REPO}/main"
CONFIG_DIR_NAME = f"neostore/{PROJECT_NAME}"


def _get_current_version():
    try:
        return _pkg_version(PROJECT_NAME)
    except PackageNotFoundError:
        pass
    version_file = os.path.join(os.path.dirname(__file__), ".version")
    if os.path.isfile(version_file):
        with open(version_file) as f:
            return f.read().strip().lstrip("v")
    return "0.0.0"


def _fetch_remote_version():
    url = f"{PROJECT_RAW}/.version"
    try:
        with urllib.request.urlopen(url, timeout=15) as r:
            if r.status == 200:
                return r.read().decode().strip().lstrip("v")
    except Exception:
        pass
    return None


def _compare_versions(current, remote):
    def _parts(v):
        return [int(x) for x in re.split(r"[._-]", v) if x.isdigit()]
    return _parts(remote) > _parts(current)


def _get_config_dir():
    if platform.system() == "Windows":
        base = os.environ.get("USERPROFILE", "")
    else:
        base = os.environ.get("HOME", "")
    return os.path.join(base, ".config", CONFIG_DIR_NAME)


def _get_binary_path():
    if getattr(sys, 'frozen', False):
        return sys.executable
    if platform.system() == "Windows":
        resolved = shutil.which("webplay")
        if resolved:
            try:
                resolved = os.path.realpath(resolved)
            except OSError:
                pass
        return resolved
    return shutil.which("webplay")


def _uninstall():
    banner = textwrap.dedent(f"""\
    {'=' * 50}
    >>> Uninstalling {PROJECT_NAME}...
    {'=' * 50}""")
    log_info(banner)

    config_dir = _get_config_dir()
    binary = _get_binary_path()

    pip_uninstall = shutil.which("pip") or shutil.which("pip3")
    if pip_uninstall:
        try:
            subprocess.run([pip_uninstall, "uninstall", PROJECT_NAME, "-y"],
                           capture_output=True, timeout=30)
            log_success("pip package removed")
        except Exception:
            log_warning("pip uninstall failed (may already be removed)")
    else:
        log_warning("pip not found — skipping package removal")

    if os.path.isdir(config_dir):
        log_info(f"Removing config directory: {config_dir}")
        try:
            for root, dirs, files in os.walk(config_dir, topdown=False):
                for name in files:
                    fp = os.path.join(root, name)
                    try:
                        os.remove(fp)
                    except OSError:
                        pass
                for name in dirs:
                    dp = os.path.join(root, name)
                    try:
                        os.rmdir(dp)
                    except OSError:
                        pass
            os.rmdir(config_dir)
            log_success("Config directory removed")
        except OSError as e:
            log_error(f"Failed to remove config directory: {e}")
    else:
        log_info("Config directory not found — skipping")

    if binary and os.path.isfile(binary):
        bin_dir = os.path.dirname(binary)
        log_info(f"Removing binary: {binary}")

        if platform.system() == "Windows":
            config_dir_lower = config_dir.lower().rstrip("\\/")
            bin_dir_lower = bin_dir.lower().rstrip("\\/")

            if config_dir_lower in bin_dir_lower:
                bat_path = os.path.join(
                    os.environ.get("TEMP", os.environ.get("TMP", "C:\\")),
                    f"uninstall_{PROJECT_NAME}.bat"
                )
                with open(bat_path, "w") as f:
                    f.write(f"@echo off\r\n")
                    f.write(f"timeout /t 1 /nobreak >nul\r\n")
                    f.write(f"del /f /q \"{binary}\" >nul 2>&1\r\n")
                    f.write(f"rmdir /s /q \"{config_dir}\" >nul 2>&1\r\n")
                    f.write(f"del /f /q \"{bat_path}\" >nul 2>&1\r\n")
                subprocess.Popen(
                    ["cmd", "/C", "start", "/B", bat_path],
                    shell=True, close_fds=True
                )
                log_info("Created delayed deletion script for running binary")
            else:
                bat_path = os.path.join(
                    os.environ.get("TEMP", os.environ.get("TMP", "C:\\")),
                    f"uninstall_{PROJECT_NAME}.bat"
                )
                with open(bat_path, "w") as f:
                    f.write(f"@echo off\r\n")
                    f.write(f"timeout /t 1 /nobreak >nul\r\n")
                    f.write(f"del /f /q \"{binary}\" >nul 2>&1\r\n")
                    f.write(f"del /f /q \"{bat_path}\" >nul 2>&1\r\n")
                subprocess.Popen(
                    ["cmd", "/C", "start", "/B", bat_path],
                    shell=True, close_fds=True
                )
                log_info("Created delayed deletion script for binary")
        else:
            try:
                os.remove(binary)
                log_success("Binary removed")
            except OSError as e:
                log_error(f"Failed to remove binary: {e}")

        parent = os.path.dirname(bin_dir) if bin_dir else ""
        grandparent = os.path.dirname(parent) if parent else ""
        for d in [bin_dir, parent, grandparent]:
            if d and "neostore" in d and os.path.isdir(d):
                try:
                    os.rmdir(d)
                except OSError:
                    pass
    else:
        log_info("Binary not found — skipping")

    log_info("")
    log_info("PATH cleanup instructions:")
    if platform.system() == "Windows":
        log_info("  Remove from PATH manually:")
        log_info("    Settings > System > About > Advanced system settings")
        log_info("    > Environment Variables > User PATH")
        log_info(f"    Look for entries containing 'neostore\\{PROJECT_NAME}'")
    else:
        log_info("  Check your shell profile (~/.bashrc, ~/.zshrc, ~/.profile)")
        log_info(f"  for PATH entries containing 'neostore/{PROJECT_NAME}' and remove them")
        log_info("  Then run: exec $SHELL")

    log_info("")
    log_success(f"{PROJECT_NAME} has been uninstalled.")
    log_info(f"Reinstall anytime with the installer script or 'pip install .'")
    sys.exit(0)


@click.group(invoke_without_command=True)
@click.option("--selfuninstall", is_flag=True, help="Fully remove WebPlay from the system")
@click.pass_context
def cli(ctx, selfuninstall):
    """WebPlay: Media Player"""
    if selfuninstall:
        _uninstall()
    ctx.ensure_object(dict)


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


@cli.command()
@click.option("--proxy", default=None, help="HTTP proxy URL (e.g. http://proxy:8080)")
def self_update(proxy):
    """Check for updates and upgrade to the latest version."""
    print_banner()
    log_info(f"Checking for updates...")

    current = _get_current_version()
    log_info(f"Current version: v{current}")

    if proxy:
        os.environ["HTTP_PROXY"] = proxy
        os.environ["HTTPS_PROXY"] = proxy
        log_info(f"Using proxy: {proxy}")

    remote = _fetch_remote_version()
    if remote is None:
        log_error("Could not fetch latest version from GitHub.")
        log_info("Check your internet connection and try again.")
        return

    log_info(f"Latest version:  v{remote}")

    if not _compare_versions(current, remote):
        log_success(f"You are already up-to-date (v{current}).")
        return

    log_info(f"Update available: v{current} -> v{remote}")
    log_info("Downloading latest release...")

    tmp_dir = tempfile.mkdtemp(prefix=f"{PROJECT_NAME}_update_")
    archive_path = os.path.join(tmp_dir, f"{PROJECT_NAME}.tar.gz")
    download_url = (
        f"https://github.com/{PROJECT_REPO}/archive/refs/tags/v{remote}.tar.gz"
    )

    try:
        urllib.request.urlretrieve(download_url, archive_path)
        size_kb = os.path.getsize(archive_path) / 1024
        log_info(f"Downloaded ({size_kb:.1f} KB)")
    except Exception as e:
        log_error(f"Download failed: {e}")
        shutil.rmtree(tmp_dir, ignore_errors=True)
        return

    log_info("Installing update via pip...")
    pip = shutil.which("pip") or shutil.which("pip3")
    if not pip:
        log_error("pip not found — cannot update.")
        shutil.rmtree(tmp_dir, ignore_errors=True)
        return

    result = subprocess.run(
        [pip, "install", "--upgrade", archive_path],
        capture_output=True, text=True, timeout=120
    )

    shutil.rmtree(tmp_dir, ignore_errors=True)

    if result.returncode != 0:
        log_error("Update installation failed.")
        log_error(result.stderr.strip())
        return

    log_success(f"Updated to v{remote}!")
    log_info("Restart WebPlay to use the new version.")


def main():
    cli()


if __name__ == '__main__':
    main()
