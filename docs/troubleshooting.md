# Troubleshooting

## Common Issues

### FFmpeg not found

**Error:** Metadata probes fail, thumbnails return 404, streams are empty.

**Fix:** Install FFmpeg:

```bash
python app.py install-ffmpeg
```

Or manually install it for your OS.

### API key not working

**Symptom:** "Access Denied" page when opening the URL.

**Fix:**
1. Check the key in the URL matches the printed key.
2. Recover the saved key: `python app.py key`
3. Restart with a new key: `python app.py start`

### Port already in use

**Error:** `Address already in use`

**Fix:** Use a different port:
```bash
python app.py free --port 8080
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
1. Is the media path set? `python app.py path /correct/path`
2. Does the path contain video/audio files?
3. Are the file permissions correct (readable by the webplay user)?

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
