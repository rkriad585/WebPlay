# Usage Guide

## Starting the Server

```bash
# Secured mode
python app.py start

# Free mode (no auth)
python app.py free

# Custom port
python app.py free --port 8080
```

## Gallery Views

The home page supports multiple views:

- **Grid view** — Thumbnail grid (default)
- **List view** — Compact list with details
- **Folder view** — Browse by directory structure

Switch views using the toolbar icons.

## Searching

Use the search bar to filter media by name. Search is scoped to the
current folder in folder view mode.

## Playing Media

Click any media file to open the player. Supported features:

- Play/pause, seek, volume control
- Fullscreen and picture-in-picture
- Multiple audio track selection
- Subtitle toggle
- Playback speed control

## Resume Playback

WebPlay remembers your position. When you reopen a file, it resumes
from where you left off. Position is saved on pause, on page unload,
and every 30 seconds during playback.

## Binge Mode

When a video ends, WebPlay automatically plays the next file in the
same folder. Files are sorted naturally (e.g., `episode_2` comes after
`episode_1`).

## Remote Control

Open the remote control URL on your phone to control playback:

1. Start the server.
2. Visit `/remote` on your phone (same network).
3. Use the remote to play/pause, seek, and adjust volume.

The remote connects via WebSocket and syncs with the player.

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Space / K | Play/pause |
| F | Fullscreen |
| M | Mute |
| Left/Right | Seek -/+ 5s |
| Up/Down | Volume +/- |
| 0-9 | Seek to 0%-90% |
