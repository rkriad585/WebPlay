import os
import re
import shutil
import subprocess
import signal
import atexit
import threading
import select
from flask import Flask, render_template, request, Response, send_file, jsonify, abort
from flask_socketio import SocketIO, emit, join_room

from core.utils import print_banner, log_info, log_success, log_error, log_warning, set_log_file
from core.media import get_media_files, get_video_metadata, convert_srt_to_vtt, get_cached_thumbnail, save_thumbnail_to_cache
from core.auth import require_auth, validate_media_path
from core.db import get_db, init_db
from core.paths import get_key_path, get_cache_dir, get_log_path
from core.themes import resolve_theme, get_theme_css, get_theme_list, DEFAULT_THEME
from config import Config, load_toml, get_setting, save_config, _config_data

app = Flask(__name__)
app.config.from_object(Config)
socketio = SocketIO(app, cors_allowed_origins=[])

ffmpeg_processes = []
ffmpeg_lock = threading.Lock()

Config.ensure_dirs()
load_toml()
set_log_file(get_log_path())
app.config['DATABASE_PATH'] = get_setting("db", "path") or Config.DATABASE_PATH
init_db(app.config['DATABASE_PATH'])
CURRENT_ROOT = get_setting("media", "path") or Config.load_settings()

if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):
    log_warning("FFmpeg/FFprobe not found. Run 'python app.py install-ffmpeg' to auto-install.")


def _current_theme():
    name = get_setting("theme", "name") or DEFAULT_THEME
    return resolve_theme(name)


@app.context_processor
def inject_globals():
    k = ('&key=' + request.args.get('key')) if request.args.get('key') else ''
    theme = _current_theme()
    theme_display_list = [
        {"slug": slug, "display": resolve_theme(slug)["name"]}
        for slug in get_theme_list()
    ]
    return dict(
        k=k,
        theme_name=theme.get("name", DEFAULT_THEME),
        theme_mode=theme.get("mode", "dark"),
        theme_palette=theme["palette"],
        theme_css=get_theme_css(theme),
        theme_list=theme_display_list,
    )


def cleanup_ffmpeg():
    with ffmpeg_lock:
        for proc in ffmpeg_processes[:]:
            try:
                proc.kill()
                proc.wait(timeout=2)
            except Exception:
                pass
        ffmpeg_processes.clear()


atexit.register(cleanup_ffmpeg)
signal.signal(signal.SIGTERM, lambda sig, frame: cleanup_ffmpeg())
signal.signal(signal.SIGINT, lambda sig, frame: cleanup_ffmpeg())


@app.route('/')
@require_auth
def index():
    view_mode = request.args.get('view', 'grid')
    browse_mode = request.args.get('mode', 'folders')
    search_query = request.args.get('q', '').lower()
    target_folder = request.args.get('folder')

    all_media = get_media_files(CURRENT_ROOT)

    if search_query:
        if browse_mode == 'specific_folder' and target_folder:
            media = [m for m in all_media if os.path.dirname(m['path']) == target_folder and search_query in m['name'].lower()]
        else:
            browse_mode = 'all'
            media = [m for m in all_media if search_query in m['name'].lower()]
    elif browse_mode == 'folders':
        folders_dict = {}
        for m in all_media:
            parent_dir = os.path.dirname(m['path'])
            folder_name = os.path.basename(parent_dir) or "Root"
            if parent_dir not in folders_dict:
                folders_dict[parent_dir] = {
                    'name': folder_name, 'path': parent_dir, 'count': 0,
                    'items': [], 'latest_thumb': m['path'] if m['type'] == 'video' else None
                }
            d = folders_dict[parent_dir]
            d['count'] += 1
            d['items'].append(m)
            if m['type'] == 'video' and d['latest_thumb'] is None:
                d['latest_thumb'] = m['path']
        for d in folders_dict.values():
            if d['latest_thumb'] is None and d['items']:
                d['latest_thumb'] = d['items'][0]['path']
        media = sorted(list(folders_dict.values()), key=lambda x: x['name'].lower())
    elif browse_mode == 'specific_folder' and target_folder:
        media = sorted([m for m in all_media if os.path.dirname(m['path']) == target_folder], key=lambda x: x['name'].lower())
    else:
        media = sorted(all_media, key=lambda x: x['name'].lower())

    return render_template('index.html', media=media, view=view_mode, mode=browse_mode,
                           target_folder_name=os.path.basename(target_folder) if target_folder else "Library", root=CURRENT_ROOT)


@app.route('/player')
@require_auth
def player():
    file_path = validate_media_path(request.args.get('path'), CURRENT_ROOT)
    if not file_path: return "File not found", 404

    meta = get_video_metadata(file_path)
    base_name = os.path.splitext(file_path)[0]
    has_sub = os.path.exists(base_name + '.srt')

    start_time = 0
    try:
        with get_db(app.config['DATABASE_PATH']) as conn:
            c = conn.cursor()
            c.execute("SELECT time FROM playback WHERE path=?", (file_path,))
            row = c.fetchone()
            start_time = row[0] if row else 0
    except Exception:
        log_error(f"Failed to load playback state for {file_path}")

    def natural_key(s):
        return [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', s)]
    next_video = None
    parent_dir = os.path.dirname(file_path)
    siblings = sorted([f for f in os.listdir(parent_dir) if f.lower().endswith(('.mp4','.mkv','.avi','.webm'))], key=natural_key)
    fname = os.path.basename(file_path)
    try:
        curr_idx = siblings.index(fname)
        if curr_idx + 1 < len(siblings):
            next_video = os.path.join(parent_dir, siblings[curr_idx + 1])
    except (ValueError, OSError): pass

    return render_template('player.html', path=file_path, meta=meta, has_sub=has_sub,
                           start_time=start_time, filename=fname, next_video=next_video)


@app.route('/remote')
@require_auth
def remote_ui():
    return render_template('remote.html')


@app.route('/stream')
@require_auth
def stream():
    path = validate_media_path(request.args.get('path'), CURRENT_ROOT)
    audio_idx = request.args.get('audio_index', default=0, type=int)
    if audio_idx < 0: audio_idx = 0
    if not path: abort(404)

    ext = os.path.splitext(path)[1].lower()

    mime_map = {
        '.mp4': 'video/mp4',
        '.webm': 'video/webm',
    }
    mime = mime_map.get(ext, 'video/mp4')

    if ext in ['.mp4', '.webm'] and audio_idx == 0:
        range_header = request.headers.get('Range', None)
        if not range_header: return send_file(path, mimetype=mime)
        size = os.path.getsize(path)
        byte1, byte2 = 0, None
        try:
            m = range_header.replace('bytes=', '').split('-')
            byte1 = int(m[0])
            if len(m) > 1 and m[1]: byte2 = int(m[1])
        except (ValueError, IndexError):
            return send_file(path, mimetype=mime)
        length = size - byte1
        if byte2: length = byte2 + 1 - byte1
        with open(path, 'rb') as f:
            f.seek(byte1)
            data = f.read(length)
        rv = Response(data, 206, mimetype=mime, direct_passthrough=True)
        rv.headers.add('Content-Range', 'bytes {0}-{1}/{2}'.format(byte1, byte1 + length - 1, size))
        return rv
    else:
        def generate():
            cmd = ['ffmpeg', '-re', '-i', path,
                   '-map', '0:v:0', '-map', f'0:a:{audio_idx}?',
                   '-c:v', 'libx264', '-preset', get_setting('transcode', 'preset') or os.environ.get('TRANSCODE_PRESET', 'ultrafast'), '-crf', str(get_setting('transcode', 'crf') or os.environ.get('TRANSCODE_CRF', '28')),
                   '-c:a', 'aac', '-movflags', 'frag_keyframe+empty_moov',
                   '-f', 'mp4', '-']

            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            with ffmpeg_lock:
                ffmpeg_processes.append(process)
            try:
                while True:
                    r, _, _ = select.select([process.stdout], [], [], 1.0)
                    if not r:
                        continue
                    data = process.stdout.read(1024 * 1024)
                    if not data:
                        break
                    yield data
            except GeneratorExit:
                pass
            finally:
                process.kill()
                process.wait(timeout=5)
                with ffmpeg_lock:
                    try:
                        ffmpeg_processes.remove(process)
                    except ValueError:
                        pass
        return Response(generate(), mimetype='video/mp4')


@app.route('/thumbnail')
@require_auth
def thumbnail():
    path = validate_media_path(request.args.get('path'), CURRENT_ROOT)
    timestamp = request.args.get('t', '00:00:10')
    if not path: return "", 404

    if timestamp == '00:00:10':
        cached = get_cached_thumbnail(path)
        if cached: return send_file(cached)

    try:
        cmd = ['ffmpeg', '-ss', timestamp, '-i', path, '-vframes', '1', '-q:v', '5', '-vf', 'scale=480:-1', '-f', 'image2', '-']
        out, _ = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).communicate(timeout=30)

        if not out:
            return "", 404

        if timestamp == '00:00:10':
            save_thumbnail_to_cache(path, out)

        return Response(out, mimetype='image/jpeg')
    except Exception:
        return "", 404


@app.route('/subtitle')
@require_auth
def get_subtitle():
    path = validate_media_path(request.args.get('path'), CURRENT_ROOT)
    if not path: return "", 404
    base = os.path.splitext(path)[0]
    if os.path.exists(base+'.srt'): return Response(convert_srt_to_vtt(base+'.srt'), mimetype='text/vtt')
    return "", 404


@app.route('/api/save_progress', methods=['POST'])
@require_auth
def save_progress():
    data = request.json
    if not data:
        return jsonify(success=False, error="Invalid request"), 400
    file_path = data.get('path')
    play_time = data.get('time')
    if not file_path or play_time is None:
        return jsonify(success=False, error="Missing path or time"), 400
    try:
        play_time = float(play_time)
        if play_time < 0:
            return jsonify(success=False, error="Invalid time"), 400
    except (TypeError, ValueError):
        return jsonify(success=False, error="Invalid time"), 400
    finished = 1 if data.get('finished') else 0
    try:
        with get_db(app.config['DATABASE_PATH']) as conn:
            conn.execute("INSERT OR REPLACE INTO playback (path, time, finished) VALUES (?, ?, ?)", (file_path, play_time, finished))
    except Exception:
        return jsonify(success=False, error="Database error"), 500
    return jsonify(success=True)


@app.route('/api/theme', methods=['POST'])
@require_auth
def set_theme():
    data = request.json
    if not data or "name" not in data:
        return jsonify(success=False, error="Missing theme name"), 400
    name = data["name"]
    theme = resolve_theme(name)
    if theme.get("name") != name and name not in [k for k in get_theme_list()]:
        return jsonify(success=False, error="Unknown theme"), 400
    cfg = dict(_config_data)
    cfg["theme"] = {"name": name, "mode": theme["mode"]}
    save_config(cfg)
    return jsonify(success=True, name=name, mode=theme["mode"])


@app.route('/api/rename', methods=['POST'])
@require_auth
def rename_file():
    data = request.json
    old_path = validate_media_path(data.get('old_path') if data else None, CURRENT_ROOT)
    new_name_raw = data.get('new_name') if data else None
    if not old_path or not new_name_raw:
        return jsonify(success=False), 400
    directory = os.path.dirname(old_path)
    ext = os.path.splitext(old_path)[1]
    safe_name = "".join([c for c in new_name_raw if c.isalpha() or c.isdigit() or c in " ._-"]).strip()
    if not safe_name:
        return jsonify(success=False, message="Invalid name"), 400
    name_no_ext = safe_name[:-len(ext)] if safe_name.lower().endswith(ext.lower()) else safe_name
    new_path = os.path.join(directory, name_no_ext + ext)
    if os.path.exists(new_path):
        return jsonify(success=False, message="Target file already exists"), 409
    try:
        os.rename(old_path, new_path)
        return jsonify(success=True, new_path=new_path)
    except Exception as e:
        log_error(f"Rename failed: {e}")
        return jsonify(success=False, message="Rename failed"), 500


@socketio.on('connect')
def on_connect():
    required_key = app.config.get('API_KEY')
    if required_key:
        key = request.args.get('key')
        if not key or key != required_key:
            return False


@socketio.on('join')
def on_join(data):
    if not data or 'room' not in data:
        return
    room = data['room']
    join_room(room)


@socketio.on('remote_cmd')
def handle_remote(data):
    if not data or 'room' not in data or 'action' not in data:
        return
    emit('player_event', data, to=data['room'])
