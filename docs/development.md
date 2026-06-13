# Development Guide

## Setup

```bash
git clone https://github.com/rkriad585/WebPlay.git
cd WebPlay
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
```

The `-e` flag installs in editable mode, so changes to the source code
are immediately reflected when running `webplay`.

## Project Architecture

```
WebPlay/
  app.py               # Flask routes, WebSocket, streaming
  cli.py               # CLI entry point (webplay command)
  config.py            # TOML config loader/writer
  core/
    auth.py            # @require_auth decorator, path validation
    db.py              # SQLite database (playback tracking)
    media.py           # Media scanning, metadata, thumbnails
    utils.py           # Logging, helpers
    paths.py           # Cross-platform path resolution
  templates/           # Jinja2 templates (HTML)
  static/              # Static assets
  tests/               # Pytest test suite
```

## Running in Development

```bash
webplay free --port 5000
```

The server auto-reloads in debug mode if you set `FLASK_DEBUG=1`.

## Running Tests

```bash
python -m pytest -v
```

All 21 tests should pass. Tests use temporary directories and don't
require FFmpeg (dummy files are used).

## Code Style

- Python: [Black](https://github.com/psf/black) with defaults
- Linting: [Ruff](https://github.com/astral-sh/ruff)
- Keep functions focused and small
- No unnecessary dependencies

## Adding a Route

1. Add the route function in `app.py`.
2. Decorate with `@require_auth` for auth protection.
3. Call `validate_media_path()` for any file path parameter.

## Database

Single table: `playback(path, time, finished)`

Use the context manager:

```python
with get_db(db_path) as conn:
    conn.execute("...")
```

## Config System

Config is read from TOML using `tomllib` (stdlib, Python 3.11+).

```python
get_setting("transcode", "preset", default="ultrafast")
```

## Building

```bash
make build    # or: ./build.sh install
make test     # or: ./build.sh test
make release  # or: ./build.sh release
```

## Versioning

The version is stored in `.version` as a single line (e.g., `v0.156.36`).
Update it before each release and create a git tag.
