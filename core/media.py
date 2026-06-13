import os
import json
import subprocess
import hashlib
import threading
import time
from datetime import datetime
from config import CACHE_DIR
from .utils import format_size, log_error

MAX_CACHE_FILES = 100
MEDIA_CACHE_TTL = 30

SUPPORTED_VIDEO = ('.mp4', '.mkv', '.avi', '.mov', '.webm', '.flv', '.wmv')
SUPPORTED_AUDIO = ('.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a')

_media_cache = None
_media_cache_time = 0
_media_cache_lock = threading.Lock()


def get_cached_thumbnail(file_path):
    file_hash = hashlib.md5(file_path.encode('utf-8')).hexdigest()
    cache_path = os.path.join(CACHE_DIR, f"{file_hash}.jpg")
    if os.path.exists(cache_path):
        return cache_path
    return None


def save_thumbnail_to_cache(file_path, image_data):
    file_hash = hashlib.md5(file_path.encode('utf-8')).hexdigest()
    cache_path = os.path.join(CACHE_DIR, f"{file_hash}.jpg")
    with open(cache_path, 'wb') as f:
        f.write(image_data)
    evict_old_thumbnails()


def evict_old_thumbnails():
    files = []
    for fname in os.listdir(CACHE_DIR):
        fpath = os.path.join(CACHE_DIR, fname)
        if os.path.isfile(fpath) and fname.endswith('.jpg'):
            files.append((fpath, os.path.getmtime(fpath)))
    if len(files) > MAX_CACHE_FILES:
        files.sort(key=lambda x: x[1])
        for fpath, _ in files[:len(files) - MAX_CACHE_FILES]:
            try:
                os.remove(fpath)
            except OSError:
                pass


def invalidate_media_cache():
    global _media_cache, _media_cache_time
    with _media_cache_lock:
        _media_cache = None
        _media_cache_time = 0


def get_media_files(root_path):
    global _media_cache, _media_cache_time
    now = time.time()
    with _media_cache_lock:
        if _media_cache is not None and (now - _media_cache_time) < MEDIA_CACHE_TTL:
            return _media_cache

    media_files = []
    for root, dirs, files in os.walk(root_path, onerror=lambda e: None):
        for file in files:
            if file.lower().endswith(SUPPORTED_VIDEO) or file.lower().endswith(SUPPORTED_AUDIO):
                full_path = os.path.join(root, file)
                try:
                    stats = os.stat(full_path)
                    media_files.append({
                        'name': file,
                        'path': full_path,
                        'type': 'video' if file.lower().endswith(SUPPORTED_VIDEO) else 'audio',
                        'size': format_size(stats.st_size),
                        'size_bytes': stats.st_size,
                        'added': datetime.fromtimestamp(stats.st_ctime).strftime('%Y-%m-%d %H:%M'),
                        'date_short': datetime.fromtimestamp(stats.st_ctime).strftime('%b %d'),
                        'date_obj': stats.st_ctime,
                        'ext': os.path.splitext(file)[1].lower().replace('.', '').upper()
                    })
                except OSError:
                    continue
    with _media_cache_lock:
        _media_cache = media_files
        _media_cache_time = now
    return media_files


def format_duration(seconds):
    seconds = int(seconds)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def probe_file(file_path):
    cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json',
           '-show_format', '-show_streams', file_path]
    try:
        out, _ = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).communicate(timeout=30)
        return json.loads(out)
    except Exception:
        return None


def get_video_metadata(file_path):
    meta = {'duration': '0:00', 'seconds': 0, 'resolution': 'N/A', 'codec': 'N/A', 'audio_tracks': []}
    try:
        probe = probe_file(file_path)
        if not probe:
            return meta
        streams = probe.get('streams', [])

        video_stream = next((s for s in streams if s['codec_type'] == 'video'), None)
        if video_stream:
            meta['resolution'] = f"{video_stream.get('width','?')}x{video_stream.get('height','?')}"
            meta['codec'] = video_stream.get('codec_name', 'unknown')

        duration = float(probe.get('format', {}).get('duration', 0))
        meta['seconds'] = duration
        meta['duration'] = format_duration(duration)

        audio_streams = [s for s in streams if s['codec_type'] == 'audio']
        for idx, audio in enumerate(audio_streams):
            lang = audio.get('tags', {}).get('language', 'und')
            title = audio.get('tags', {}).get('title', f'Track {idx+1}')
            codec = audio.get('codec_name', 'aac')
            meta['audio_tracks'].append({
                'index': idx,
                'label': f"{lang.upper()} - {title} ({codec})",
                'id': audio['index']
            })

        return meta
    except Exception as e:
        log_error(f"Metadata probe failed: {e}")
        return meta


def convert_srt_to_vtt(srt_path):
    try:
        import pysubs2
        subs = pysubs2.load(srt_path, encoding="utf-8")
        return subs.to_string(format_="vtt")
    except Exception:
        return "WEBVTT\n\n"
