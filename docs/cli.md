# CLI Reference

WebPlay uses a Click-based command-line interface. All commands accept
`--config <path>` and `--help`.

## Global Options

| Flag | Description |
|------|-------------|
| `--config PATH` | Use a custom config file |
| `--help` | Show help message |

## Commands

### `path`

Set the media directory path.

```bash
python app.py path /path/to/media
```

### `start`

Start the server in secured mode with a random API key.

```bash
python app.py start
python app.py start --port 8080
python app.py start --domain example.com
python app.py start --config /custom/config.toml
```

### `free`

Start the server in open mode (no authentication).

```bash
python app.py free
python app.py free --port 8080
```

### `key`

Print the saved API key.

```bash
python app.py key
```

### `install-ffmpeg`

Auto-detect the operating system and install FFmpeg.

```bash
python app.py install-ffmpeg
```

Supported package managers: `apt`, `dnf`, `yum`, `pacman`, `apk`,
`zypper`, `brew`, `winget`, `choco`, `scoop`.

## Options Detail

### `--port`

Server port. Default: `5000`.

### `--domain`

Public domain name for external URL display.

### `--config`

Path to a custom TOML config file. Default:
`~/.config/neostore/webplay/config.toml`.
