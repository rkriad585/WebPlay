import os
import secrets
import sqlite3
import subprocess
import click
import json
from flask import Flask, render_template, request, Response, send_file, jsonify, abort
from flask_socketio import SocketIO, emit, join_room

from core.utils import print_banner, log_info, log_success, log_error, log_warning
from core.media import get_media_files, get_video_metadata, convert_srt_to_vtt, get_cached_thumbnail, save_thumbnail_to_cache
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
# Allow CORS for remote control
socketio = SocketIO(app, cors_allowed_origins="*")

# Database Setup
def init_db():
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    db_path = db_uri.replace('sqlite:///', '') if db_uri.startswith('sqlite:///') else 'webplay.db'
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS playback (path TEXT PRIMARY KEY, time REAL, finished INTEGER)''')
    conn.commit()
    conn.close()

init_db()
CURRENT_ROOT = Config.load_settings()

@app.route('/')
def index():
    auth_key = request.args.get('key')
    required_key = app.config.get('API_KEY')
    if required_key and auth_key != required_key: return render_template('error.html'), 403

    view_mode = request.args.get('view', 'grid')
    browse_mode = request.args.get('mode', 'folders')
    search_query = request.args.get('q', '').lower()
    target_folder = request.args.get('folder')
    
    all_media = get_media_files(CURRENT_ROOT)
    
    if search_query:
        browse_mode = 'all'
        media = [m for m in all_media if search_query in m['name'].lower()]
    elif browse_mode == 'folders':
        folders_dict = {}
        for m in all_media:
            parent_dir = os.path.dirname(m['path'])
            folder_name = os.path.basename(parent_dir) or "Root"
            if parent_dir not in folders_dict:
                folders_dict[parent_dir] = {'name': folder_name, 'path': parent_dir, 'count': 0, 'items': [], 'latest_thumb': m['path']}
            folders_dict[parent_dir]['count'] += 1
            folders_dict[parent_dir]['items'].append(m)
        media = sorted(list(folders_dict.values()), key=lambda x: x['name'].lower())
    elif browse_mode == 'specific_folder' and target_folder:
        media = sorted([m for m in all_media if os.path.dirname(m['path']) == target_folder], key=lambda x: x['name'].lower())
    else:
        media = sorted(all_media, key=lambda x: x['name'].lower())

    return render_template('index.html', media=media, view=view_mode, mode=browse_mode, 
                           target_folder_name=os.path.basename(target_folder) if target_folder else "Library", root=CURRENT_ROOT)

@app.route('/player')
def player():
    file_path = request.args.get('path')
    if not file_path or not os.path.exists(file_path): return "File not found", 404
        
    meta = get_video_metadata(file_path)
    base_name = os.path.splitext(file_path)[0]
    has_sub = os.path.exists(base_name + '.srt')
    
    start_time = 0
    try:
        conn = sqlite3.connect('webplay.db')
        c = conn.cursor()
        c.execute("SELECT time FROM playback WHERE path=?", (file_path,))
        row = c.fetchone()
        start_time = row[0] if row else 0
        conn.close()
    except: pass

    # Generate next video link for Binge Mode
    next_video = None
    parent_dir = os.path.dirname(file_path)
    siblings = sorted([f for f in os.listdir(parent_dir) if f.lower().endswith(('.mp4','.mkv','.avi','.webm'))])
    fname = os.path.basename(file_path)
    try:
        curr_idx = siblings.index(fname)
        if curr_idx + 1 < len(siblings):
            next_video = os.path.join(parent_dir, siblings[curr_idx + 1])
    except: pass

    return render_template('player.html', path=file_path, meta=meta, has_sub=has_sub, 
                           start_time=start_time, filename=fname, next_video=next_video)

@app.route('/remote')
def remote_ui():
    """Renders the smartphone remote interface."""
    return render_template('remote.html')

@app.route('/stream')
def stream():
    path = request.args.get('path')
    audio_idx = request.args.get('audio_index', default=0, type=int) # New: Audio selection
    if not path or not os.path.exists(path): abort(404)

    ext = os.path.splitext(path)[1].lower()
    
    # Direct play if MP4 and no specific audio track requested (default 0)
    if ext in ['.mp4', '.webm'] and audio_idx == 0:
        range_header = request.headers.get('Range', None)
        if not range_header: return send_file(path)
        size = os.path.getsize(path)
        byte1, byte2 = 0, None
        m = range_header.replace('bytes=', '').split('-')
        byte1 = int(m[0])
        if m[1]: byte2 = int(m[1])
        length = size - byte1
        if byte2: length = byte2 + 1 - byte1
        with open(path, 'rb') as f:
            f.seek(byte1)
            data = f.read(length)
        rv = Response(data, 206, mimetype='video/mp4', direct_passthrough=True)
        rv.headers.add('Content-Range', 'bytes {0}-{1}/{2}'.format(byte1, byte1 + length - 1, size))
        return rv
    else:
        # Transcode with specific Audio Map
        def generate():
            # -map 0:v:0 -> Map first video stream
            # -map 0:a:audio_idx -> Map selected audio stream
            cmd = ['ffmpeg', '-re', '-i', path, 
                   '-map', '0:v:0', '-map', f'0:a:{audio_idx}?', 
                   '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '28',
                   '-c:a', 'aac', '-movflags', 'frag_keyframe+empty_moov', 
                   '-f', 'mp4', '-']
            
            # Hardware accel flags (optional try)
            # cmd.insert(1, '-hwaccel')
            # cmd.insert(2, 'auto')

            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            try:
                while True:
                    data = process.stdout.read(1024 * 1024)
                    if not data: break
                    yield data
            finally:
                process.kill()
        return Response(generate(), mimetype='video/mp4')

@app.route('/thumbnail')
def thumbnail():
    path = request.args.get('path')
    timestamp = request.args.get('t', '00:00:10') # For Scrubbing/Preview
    if not path or not os.path.exists(path): return "", 404
    
    # Check Cache (only for default timestamp)
    if timestamp == '00:00:10':
        cached = get_cached_thumbnail(path)
        if cached: return send_file(cached)

    try:
        cmd = ['ffmpeg', '-ss', timestamp, '-i', path, '-vframes', '1', '-q:v', '5', '-vf', 'scale=480:-1', '-f', 'image2', '-']
        out, _ = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).communicate()
        
        # Save to cache if it's the main thumb
        if timestamp == '00:00:10' and out:
            save_thumbnail_to_cache(path, out)
            
        return Response(out, mimetype='image/jpeg')
    except: return "", 404 

@app.route('/subtitle')
def get_subtitle():
    path = request.args.get('path')
    if not path: return "", 404
    base = os.path.splitext(path)[0]
    if os.path.exists(base+'.srt'): return Response(convert_srt_to_vtt(base+'.srt'), mimetype='text/vtt')
    return "", 404

@app.route('/api/save_progress', methods=['POST'])
def save_progress():
    data = request.json
    try:
        conn = sqlite3.connect('webplay.db')
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO playback (path, time, finished) VALUES (?, ?, 0)", (data.get('path'), data.get('time')))
        conn.commit()
        conn.close()
    except: pass
    return jsonify(success=True)

@app.route('/api/rename', methods=['POST'])
def rename_file():
    data = request.json
    old_path, new_name = data.get('old_path'), data.get('new_name')
    if not old_path or not new_name or not os.path.exists(old_path): return jsonify(success=False)
    directory = os.path.dirname(old_path)
    safe_name = "".join([c for c in new_name if c.isalpha() or c.isdigit() or c in " ._-"]).strip()
    try:
        os.rename(old_path, os.path.join(directory, safe_name + os.path.splitext(old_path)[1]))
        return jsonify(success=True, new_path=os.path.join(directory, safe_name + os.path.splitext(old_path)[1]))
    except str as e: return jsonify(success=False, message=str(e))

# --- SOCKET IO EVENTS ---
@socketio.on('join')
def on_join(data):
    room = data['room']
    join_room(room)
    # log_info(f"Client joined room: {room}")

@socketio.on('remote_cmd')
def handle_remote(data):
    # data = {action: 'play'|'pause'|'seek', value: ...}
    emit('player_event', data, to=data['room'])

@click.group()
def cli():
    """WebPlay: Media Player"""
    pass

@cli.command()
@click.argument('path', type=click.Path(exists=True))
def path(path):
    Config.save_settings(os.path.abspath(path))
    print_banner()
    log_success(f"Media path: {path}")

@cli.command()
@click.option('--port', default=5000)
def start(port):
    print_banner()
    key = secrets.token_urlsafe(16)
    app.config['API_KEY'] = key
    log_info(f"Server: http://127.0.0.1:{port}?key={key}")
    log_warning("Copy key above.")
    socketio.run(app, host='0.0.0.0', port=port, debug=False)

@cli.command()
@click.option('--port', default=5000)
def free(port):
    print_banner()
    app.config['API_KEY'] = None
    log_info(f"Server: http://127.0.0.1:{port}")
    socketio.run(app, host='0.0.0.0', port=port, debug=False)

if __name__ == '__main__':
    cli()
