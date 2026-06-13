# WebPlay — Agent Guide

## How to run

- Entry point: `python app.py <command>`
- Set media path first: `python app.py path /path/to/media`
- Secured mode (random API key): `python app.py start`
- Open mode (no auth): `python app.py free`
- Custom port: `python app.py free --port 8080` (default 5000)
- Custom config: `python app.py start --config /path/to/config.toml`
- API key is passed as `?key=<token>` query param on every URL. Key is printed once on startup and saved to `~/.config/neostore/webplay/.webplay_key.txt`. Recover with `python app.py key`.

## Project version

`.version` in the project root — a single line with a `v`-prefixed semantic version (e.g. `v0.1.0`). Update on each release; read it at build/deploy time.

## Config system

All state lives under `~/.config/neostore/webplay/`:
- `config.toml` — TOML settings (media path, transcode preset/CRF, domain, API key)
- `webplay.db` — SQLite playback database
- `history.log` — Timestamped log output
- `.webplay_cache/` — Thumbnail cache (100-file LRU)
- `.webplay_key.txt` — Last API key for `python app.py key` recovery

Exports/downloads go to `~/Downloads/neostore/webplay/`.

Use `--config <path>` on any CLI command to use a different config file. Config is read from TOML with `tomllib` (stdlib). The `--domain` flag on `start`/`free` overrides the config at runtime. Transcode settings are read from TOML `[transcode]` section, with `TRANSCODE_PRESET`/`TRANSCODE_CRF` env var fallback.

## Architecture

Backend modules:
- `app.py` — Flask routes, WebSocket events, streaming generator, CLI (click group), `ffmpeg_processes` dict (thread-safe via `threading.Lock`). DB init, auth decorator, and path validation extracted to modules below.
- `core/db.py` — `init_db(db_path)` and `get_db(db_path)` context manager. Single-table SQLite `playback(path, time, finished)`. Path is primary key. Only written on pause/beforeunload.
- `core/auth.py` — `@require_auth` decorator (checks `request.args.get('key')` against `app.config['API_KEY']`, returns 403 HTML/JSON), `validate_media_path(path, current_root)` (resolves symlinks via `os.path.realpath()`, rejects outside root).
- `core/media.py` — `get_media_files()` (30s TTL cache), `get_video_metadata()` (FFprobe subprocess, not ffmpeg-python), thumbnail gen/cache (100-file LRU eviction), SRT→VTT conversion.
- `core/utils.py` — rich logging, banner, `format_size()`.
- `config.py` — Settings persistence via `webplay_settings.json`, DB path, cache dir, `ensure_dirs()`.

`@require_auth` uses `current_app` proxy — no explicit app dependency. Any new route must be decorated with `@require_auth`.

## Key quirks

- **FFmpeg is a hard system dependency** (not a pip package). Without `ffmpeg` on PATH, metadata probes fail silently, thumbnails return 404, and transcoded streams produce empty responses. `ffmpeg-python` is **not** used — probes call `ffprobe` directly via subprocess.
- **Tests** live in `tests/test_app.py` (21 tests, run with `python3 -m pytest`).
- **No frontend build step** — Tailwind CSS, Plyr.js 3.7.8, jQuery 3.7.1, Socket.IO client 4.7.4 all loaded from CDN with SRI `integrity` + `crossorigin` in `templates/base.html`.
- **`python-dotenv` removed from requirements.txt** (was declared but never imported). `SECRET_KEY` defaults to `'dev-key-webplay-secure'`.
- **Streaming logic** (`app.py:137-188`): Native `.mp4`/`.webm` with `audio_index=0` → range-request byte serving (206 Partial Content, seekable). Everything else → FFmpeg pipe transcoded to fragmented MP4 (libx264+aac, ultrafast, frag_keyframe+empty_moov). `select.select()` with 1s timeout in generator prevents indefinite FFmpeg block. Audio track switching via `?audio_index=N` on `/stream`.
- **`GeneratorExit` handler** in stream generator for clean client disconnect without FFmpeg orphan.
- **Thumbnail cache** (`core/media.py`): MD5-hashed JPEGs in `.webplay_cache/`, max 100 files LRU eviction.
- **Database**: `core/db.py` — `get_db()` context manager replaces raw `sqlite3.connect/close`.

## CLI commands (click group)

Defined in `app.py`:
- `python app.py path <PATH>` — saves absolute path to `config.toml`
- `python app.py start --port N` — generates random API key, sets `app.config['API_KEY']`
- `python app.py free --port N` — sets `app.config['API_KEY'] = None`
- `python app.py key` — reprints the saved API key
- `python app.py install-ffmpeg` — auto-detect OS and install FFmpeg
- All commands accept `--config <path>` for custom config file

## WebSocket events (Socket.IO)

Defined in `app.py`:
- `connect` — returns False if API_KEY is set AND `request.args.get('key')` is invalid. Both `player.html` and `remote.html` pass the key via `io({ query: { key: ... } })`.
- `join` — takes `{room: string}`, calls `join_room(room)`
- `remote_cmd` — takes `{room, action, value}`, emits `player_event` to `room`
- Server runs `socketio.run(app, host='0.0.0.0', ...)` — accessible on LAN

## Routes

| Path | Purpose |
|---|---|
| `/` | Gallery — `?view=grid\|list&mode=folders\|all\|specific_folder&folder=&q=` |
| `/player` | Video player — `?path=` |
| `/remote` | Mobile remote control UI |
| `/stream` | Video stream — `?path=&audio_index=N` |
| `/thumbnail` | Thumbnail JPEG — `?path=&t=HH:MM:SS` |
| `/subtitle` | WebVTT — `?path=` |
| `/api/save_progress` | POST `{path, time}` → SQLite |
| `/api/rename` | POST `{old_path, new_name}` → `os.rename()` |

## Navigation URL pattern

A context processor (`app.py`) auto-injects `k` into all templates:
```
k = ('&key=' + request.args.get('key')) if request.args.get('key') else ''
```
Use `{{ k }}` in hrefs. Do NOT add `{% set k = ... %}` in templates — it is already available.

## Template JS escaping

Use Jinja2's `| tojson` filter for any server-side value rendered inside `<script>` tags. This provides proper JS string escaping (handles backslashes, quotes, etc.). Do NOT use `| e` (HTML escape) in JS contexts — it does not prevent XSS from filenames containing backslashes.

## Path traversal protection

`core/auth.py:validate_media_path()` — call on every route that accesses filesystem paths. Resolves symlinks via `os.path.realpath()` and rejects any path outside `CURRENT_ROOT`.

## Database

`core/db.py` — `init_db(db_path)` auto-creates single-table SQLite `playback(path, time, finished)`. Path is primary key, `finished` is unused (always `0`). Use `with get_db(db_path) as conn:` for all DB access (context manager closes automatically).

## Reset

Delete `~/.config/neostore/webplay/webplay.db` and `~/.config/neostore/webplay/config.toml` to wipe all state.

## Testing

- `python3 -m pytest` (requires `pytest` to be installed)
- Test file: `tests/test_app.py` — 21 tests covering auth, path traversal, rename, gallery, and save_progress
- Uses `tempfile.TemporaryDirectory()` for isolated media directories
- No FFmpeg fixture — tests that don't need ffmpeg use dummy files


