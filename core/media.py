import os
import subprocess
import ffmpeg
import hashlib
from datetime import datetime
from config import CACHE_DIR
from .utils import format_size

SUPPORTED_VIDEO = ('.mp4', '.mkv', '.avi', '.mov', '.webm', '.flv', '.wmv')
SUPPORTED_AUDIO = ('.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a')

def get_cached_thumbnail(file_path):
    """Returns path to cached thumb if exists, else None."""
    # Create a unique hash for the filename
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

def get_media_files(root_path):
    media_files = []
    for root, dirs, files in os.walk(root_path):
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
                except: continue
    return media_files

def get_video_metadata(file_path):
    """Extracts resolution, duration, audio tracks."""
    meta = {'duration': '0:00', 'resolution': 'N/A', 'codec': 'N/A', 'audio_tracks': []}
    try:
        probe = ffmpeg.probe(file_path)
        
        # Video Info
        video_stream = next((s for s in probe['streams'] if s['codec_type'] == 'video'), None)
        if video_stream:
            meta['resolution'] = f"{video_stream.get('width','?')}x{video_stream.get('height','?')}"
            meta['codec'] = video_stream.get('codec_name', 'unknown')
        
        duration = float(probe['format'].get('duration', 0))
        meta['seconds'] = duration
        meta['duration'] = f"{int(duration // 60)}:{int(duration % 60):02d}"

        # Audio Tracks Info
        audio_streams = [s for s in probe['streams'] if s['codec_type'] == 'audio']
        for idx, audio in enumerate(audio_streams):
            lang = audio.get('tags', {}).get('language', 'und')
            title = audio.get('tags', {}).get('title', f'Track {idx+1}')
            codec = audio.get('codec_name', 'aac')
            meta['audio_tracks'].append({
                'index': idx, # FFmpeg audio index usually starts at 0 relative to audio streams
                'label': f"{lang.upper()} - {title} ({codec})",
                'id': audio['index'] # Absolute stream index
            })
            
        return meta
    except Exception as e:
        print(f"Meta Error: {e}")
        return meta

def convert_srt_to_vtt(srt_path):
    try:
        import pysubs2
        subs = pysubs2.load(srt_path, encoding="utf-8")
        return subs.to_string(format_="vtt")
    except: return "WEBVTT\n\n"
