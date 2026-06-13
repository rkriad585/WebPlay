# CLI Reference

WebPlay uses a Click-based command-line interface. All commands accept
`--config <path>` and `--help`.

## Global Options

| Flag | Description |
|------|-------------|
| `--selfuninstall` | Fully remove WebPlay from the system |
| `--config PATH` | Use a custom config file |
| `--help` | Show help message |

## Commands

### `path`

Set the media directory path.

```bash
webplay path /path/to/media
```

### `start`

Start the server in secured mode with a random API key.

```bash
webplay start
webplay start --port 8080
webplay start --domain example.com
webplay start --config /custom/config.toml
```

### `free`

Start the server in open mode (no authentication).

```bash
webplay free
webplay free --port 8080
```

### `key`

Print the saved API key.

```bash
webplay key
```

### `install-ffmpeg`

Auto-detect the operating system and install FFmpeg.

```bash
webplay install-ffmpeg
```

Supported package managers: `apt`, `dnf`, `yum`, `pacman`, `apk`,
`zypper`, `brew`, `winget`, `choco`, `scoop`.

### `self-update`

Check for updates and upgrade to the latest version.

```bash
webplay self-update

# With HTTP proxy
webplay self-update --proxy http://proxy:8080
```

The command:
1. Reads the current installed version
2. Fetches the latest version from GitHub
3. If a newer version is available, downloads and pip-installs it

## Options Detail

### `--port`

Server port. Default: `5000`.

### `--domain`

Public domain name for external URL display.

### `--config`

Path to a custom TOML config file. Default:
`~/.config/neostore/webplay/config.toml`.

## One-Line Install

### Linux / macOS

```bash
curl -fsSL https://raw.githubusercontent.com/rkriad585/WebPlay/main/installer.sh | sh
```

### Windows

```powershell
irm https://raw.githubusercontent.com/rkriad585/WebPlay/main/installer.ps1 | iex
```

## Uninstall

### Using the webplay command

```bash
webplay --selfuninstall
```

### Using the installer script

```bash
# Linux / macOS
curl -fsSL https://raw.githubusercontent.com/rkriad585/WebPlay/main/installer.sh | sh -s -- --selfuninstall

# Windows
Invoke-RestMethod -Uri "https://raw.githubusercontent.com/rkriad585/WebPlay/main/installer.ps1" | Invoke-Expression -ArgumentList "--selfuninstall"
```
