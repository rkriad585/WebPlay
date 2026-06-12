# WebPlay — Agent Guide

## How to run

- Entry point: `python app.py <command>`
- Set media path first: `python app.py path /path/to/media`
- Secured mode (random API key): `python app.py start`
- Open mode (no auth): `python app.py free`
- Custom port: `python app.py free --port 8080` (default 5000)
- API key is passed as `?key=<token>` query param on every URL. Key is printed once on startup; there is no way to recover it without restarting.

## Architecture

All backend logic lives in a single file: `app.py` (Flask routes, WebSocket events, streaming, CLI). Supporting modules:
- `core/media.py` — `get_media_files()`, `get_video_metadata()` (ffmpeg probe), thumbnail gen/cache, SRT→VTT conversion
- `core/utils.py` — rich logging, banner, `format_size()`
- `config.py` — Settings persistence via `webplay_settings.json`, DB path, cache dir

`@require_auth` decorator on every route checks `request.args.get('key')` against `app.config['API_KEY']`. Returns 403 HTML page or JSON depending on path prefix.

## Key quirks

- **FFmpeg is a hard system dependency** (not a pip package). Without `ffmpeg` on PATH, metadata probes fail silently, thumbnails return 404, and transcoded streams produce empty responses.
- **Tests** live in `tests/test_app.py` (21 tests, run with `python3 -m pytest`).
- **No frontend build step** — Tailwind CSS, Plyr.js, jQuery, Socket.IO client all loaded from CDN in `templates/base.html`.
- **`python-dotenv` is listed in requirements.txt but not actually used** in any source file. `SECRET_KEY` defaults to `'dev-key-webplay-secure'`.
- **Streaming logic** (`app.py:137-188`): Native `.mp4`/`.webm` with `audio_index=0` → range-request byte serving (206 Partial Content, seekable). Everything else → FFmpeg pipe transcoded to fragmented MP4 (libx264+ aac, ultrafast, frag_keyframe+empty_moov). Audio track switching via `?audio_index=N` on `/stream`.
- **Thumbnail cache** (`core/media.py`): MD5-hashed JPEGs in `.webplay_cache/`, max 100 files LRU eviction.
- **Database**: Single-table SQLite `playback(path, time, finished)` created automatically at `app.py:22-28`. Path is primary key. Only written on pause/beforeunload (player.js).

## CLI commands (click group)

Defined in `app.py:282-310`:
- `python app.py path <PATH>` — saves absolute path to `webplay_settings.json`
- `python app.py start --port N` — generates random API key, sets `app.config['API_KEY']`
- `python app.py free --port N` — sets `app.config['API_KEY'] = None`

## WebSocket events (Socket.IO)

Defined in `app.py:263-280`:
- `connect` — returns False (rejects) if API_KEY is set AND `request.args.get('key')` is invalid. Both `player.html` and `remote.html` pass the key via `io({ query: { key: ... } })`.
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

Templates forward the API key through every link using:
```
{% set k = '&key=' + request.args.get('key') if request.args.get('key') else '' %}
```
Any new route or link must include this pattern, or secured-mode navigation breaks.

## Template JS escaping

Use Jinja2's `| tojson` filter for any server-side value rendered inside `<script>` tags. This provides proper JS string escaping (handles backslashes, quotes, etc.). Do NOT use `| e` (HTML escape) in JS contexts — it does not prevent XSS from filenames containing backslashes.

## Path traversal protection

All file-accessing routes (`/player`, `/stream`, `/thumbnail`, `/subtitle`, `/api/rename`) use `_validate_media_path()` at `app.py:58-67`. This resolves symlinks via `os.path.realpath()` and rejects any path outside `CURRENT_ROOT`. Any new route that accesses filesystem paths must use this function.

## Database

Single-table SQLite `playback(path, time, finished)` created automatically at `app.py:22-28`. Path is primary key. The `finished` column is unused — always written as `0`.

## Testing

- `python3 -m pytest` (requires `pytest` to be installed)
- Test file: `tests/test_app.py` — 21 tests covering auth, path traversal, rename, gallery, and save_progress
- Uses `tempfile.TemporaryDirectory()` for isolated media directories
- No FFmpeg fixture — tests that don't need ffmpeg use dummy files

## Reset

Delete `webplay.db` and `webplay_settings.json` to wipe all state.
