# Setup Guide

## Prerequisites

- Python 3.11 or newer
- FFmpeg installed and available on PATH
- Git (optional, for manual install)

## One-Click Install

The fastest way to install WebPlay is with the installer script.

### Linux / macOS

```bash
curl -fsSL https://raw.githubusercontent.com/rkriad585/WebPlay/main/installer.sh | sh
```

### Windows (PowerShell)

```powershell
irm https://raw.githubusercontent.com/rkriad585/WebPlay/main/installer.ps1 | iex
```

The installer will:
1. Detect your Python version
2. Download the latest release from GitHub
3. Install via pip
4. Add the `webplay` command to your PATH

After installation, the `webplay` command is available globally.

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
webplay install-ffmpeg
```

## Manual Installation

```bash
git clone https://github.com/rkriad585/WebPlay.git
cd WebPlay
pip install -e .
```

This makes the `webplay` command globally available.

## Set Media Path

```bash
webplay path /path/to/your/media
```

## Start the Server

**Secured mode (recommended):**
```bash
webplay start
```
This generates a random API key. The URL with the key is printed once.

**Open mode (LAN only):**
```bash
webplay free
```

## Verify

Open the printed URL in your browser. You should see your media gallery.
