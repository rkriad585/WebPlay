# Troubleshooting

## Common Issues

### `webplay: command not found`

**Symptom:** The `webplay` command is not available after installation.

**Fix:**
- Ensure the pip bin directory is in your PATH:
  ```bash
  export PATH="$PATH:$(python3 -c 'import sysconfig; print(sysconfig.get_path(\"scripts\"))')"
  ```
- Or reinstall: `pip install -e .`

### FFmpeg not found

**Error:** Metadata probes fail, thumbnails return 404, streams are empty.

**Fix:** Install FFmpeg:

```bash
webplay install-ffmpeg
```

Or manually install it for your OS.

### API key not working

**Symptom:** "Access Denied" page when opening the URL.

**Fix:**
1. Check the key in the URL matches the printed key.
2. Recover the saved key: `webplay key`
3. Restart with a new key: `webplay start`

### Port already in use

**Error:** `Address already in use`

**Fix:** Use a different port:
```bash
webplay free --port 8080
```

Or kill the existing process:
```bash
# Linux/macOS
lsof -ti:5000 | xargs kill -9

# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### No media files shown

**Symptom:** Gallery is empty.

**Checks:**
1. Is the media path set? `webplay path /correct/path`
2. Does the path contain video/audio files?
3. Are the file permissions correct (readable)?

### Database errors

**Symptom:** Playback position not saved.

**Fix:** Reset the database:
```bash
rm ~/.config/neostore/webplay/webplay.db
```

### Can't access from other devices

**Checks:**
1. Devices must be on the same network.
2. Firewall may block port 5000.
3. Use the LAN URL (printed on startup), not `127.0.0.1`.

### Subtitles not showing

- Only `.srt` format is supported (auto-converted to WebVTT).
- The subtitle file must have the same name as the video file.
  Example: `video.mkv` and `video.srt`.

## Logs

Check the log file for details:

```bash
cat ~/.config/neostore/webplay/history.log
```

## Getting Help

If issues persist, open an issue at:
https://github.com/rkriad585/WebPlay/issues
