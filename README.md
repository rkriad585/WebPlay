# WebPlay

Self-hosted media streaming server — stream your video and audio collections
to any device on your network via a web browser.

> **Version:** v0.156.36 | **License:** MIT

---

## Features

- Stream `.mp4`, `.mkv`, `.avi`, `.mov`, `.flv`, `.webm`, `.mp3`, `.wav`, `.flac`
- On-the-fly transcoding via FFmpeg for unsupported formats
- Smart resume — remembers playback position (SQLite)
- Multiple audio track selection
- Subtitle support with automatic SRT to WebVTT conversion
- Binge mode — auto-plays next episode
- Mobile remote control via WebSocket
- Grid/list/folder views
- Search and filter
- Secured mode with API key authentication

## Quick Install

### Linux / macOS

```bash
curl -fsSL https://raw.githubusercontent.com/rkriad585/WebPlay/main/installer.sh | sh
```

### Windows (PowerShell)

```powershell
irm https://raw.githubusercontent.com/rkriad585/WebPlay/main/installer.ps1 | iex
```

After install, the `webplay` command is available globally.

### Prerequisites

- Python 3.11+
- FFmpeg (the installer will guide you)

### Manual Installation

```bash
git clone https://github.com/rkriad585/WebPlay.git
cd WebPlay
pip install -e .
```

## Usage

```bash
# Set media directory
webplay path /path/to/media

# Start with API key (secured mode)
webplay start

# Start without authentication (LAN)
webplay free

# Custom port
webplay free --port 8080

# Custom config file
webplay start --config /path/to/config.toml
```

## Uninstall

### Linux / macOS

```bash
curl -fsSL https://raw.githubusercontent.com/rkriad585/WebPlay/main/installer.sh | sh -s -- --selfuninstall
```

### Windows (PowerShell)

```powershell
Invoke-RestMethod -Uri "https://raw.githubusercontent.com/rkriad585/WebPlay/main/installer.ps1" | Invoke-Expression -ArgumentList "--selfuninstall"
```

Or manually:

```bash
pip uninstall webplay
rm -rf ~/.config/neostore/webplay
```

## Configuration

All settings are stored in `~/.config/neostore/webplay/config.toml`:

```toml
[server]
port = 5000
domain = ""

[auth]
api_key = ""

[media]
path = "/path/to/media"

[transcode]
preset = "ultrafast"
crf = 28
```

Override with environment variables: `TRANSCODE_PRESET`, `TRANSCODE_CRF`.

## Build Instructions

```bash
# Install dependencies
make install

# Run tests
make test

# Lint
make lint

# Format
make format
```

Or use the build script:

```bash
./build.sh install
./build.sh test
```

Windows:

```powershell
.\build.ps1 install
.\build.ps1 test
```

## Docker

Build and run:

```bash
# Build
docker build -t webplay .

# Run
docker run -d \
  --name webplay \
  -p 5000:5000 \
  -v /path/to/media:/media:ro \
  -e TRANSCODE_PRESET=ultrafast \
  webplay

# Or with docker compose
docker compose up -d
```

## Project Structure

```
WebPlay/
  app.py              # Flask application entry point
  cli.py              # CLI entry point (webplay command)
  config.py           # TOML configuration loader
  pyproject.toml      # Project metadata and build config
  requirements.txt    # Python dependencies
  .version            # Version file
  installer.sh        # Linux/macOS installer
  installer.ps1       # Windows installer
  build.sh            # Linux/macOS build script
  build.ps1           # Windows build script
  Makefile            # Build automation
  Dockerfile          # Docker image
  core/
    auth.py           # Authentication and path validation
    db.py             # SQLite database helpers
    media.py          # Media scanning, metadata, thumbnails
    utils.py          # Logging and helper functions
    paths.py          # Cross-platform path resolution
  templates/          # Jinja2 HTML templates
  static/             # Static assets
  tests/              # Test suite
  docs/               # Documentation
```

## Documentation

See the [docs](docs/) directory for detailed guides:

- [Setup Guide](docs/setup.md)
- [Usage Guide](docs/usage.md)
- [Configuration](docs/configuration.md)
- [CLI Reference](docs/cli.md)
- [Docker Guide](docs/docker.md)
- [Development](docs/development.md)
- [Deployment](docs/deployment.md)
- [Troubleshooting](docs/troubleshooting.md)

## Development Workflow

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Install dev dependencies: `pip install -r requirements.txt`
3. Run tests: `python -m pytest`
4. Format: `black .`
5. Lint: `ruff check .`
6. Commit and push, then open a PR.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License — see [LICENSE](LICENSE).

Copyright (c) 2025 RK Riad Khan
