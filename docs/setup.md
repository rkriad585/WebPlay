# Setup Guide

## Prerequisites

- Python 3.11 or newer
- FFmpeg installed and available on PATH
- Git (optional, for cloning)

## Install FFmpeg

**Linux (Debian/Ubuntu):**
```bash
sudo apt update && sudo apt install ffmpeg
```

**Linux (Arch):**
```bash
sudo pacman -S ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
Download from https://ffmpeg.org/download.html and add to PATH.

Or use WebPlay's auto-installer:
```bash
python app.py install-ffmpeg
```

## Install WebPlay

```bash
git clone https://github.com/rkriad585/WebPlay.git
cd WebPlay
pip install -r requirements.txt
```

## Set Media Path

```bash
python app.py path /path/to/your/media
```

## Start the Server

**Secured mode (recommended):**
```bash
python app.py start
```
This generates a random API key. The URL with the key is printed once.

**Open mode (LAN only):**
```bash
python app.py free
```

## Verify

Open the printed URL in your browser. You should see your media gallery.
