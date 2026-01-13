# WebPlay 🎬

<p align="center">
  <img src="static/images/logo.svg" alt="WebPlay Logo" width="150" height="150" />
</p>


<p align="center">
  <b>The Next-Gen Self-Hosted Media Streaming Server.</b><br>
  <i>Material 3 • Liquid Glass • Nothing OS Design</i>
</p>

<p align="center">
  <a href="https://github.com/rkriad585/WebPlay/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License">
  </a>
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/Made%20with-Python-yellow.svg" alt="Python">
  </a>
  <a href="https://flask.palletsprojects.com/">
    <img src="https://img.shields.io/badge/Framework-Flask-red.svg" alt="Flask">
  </a>
</p>

---

## 📖 Introduction

**WebPlay** is a powerful, lightweight, and aesthetically stunning media player that turns your PC into a local streaming server. Built with Python and Flask, it allows you to stream your video and audio collections to any device on your network (Mobile, Tablet, Smart TV, or Laptop) via a web browser.

It combines the functionality of advanced players like **MX Player Pro** with the ease of a web interface, wrapped in a beautiful UI inspired by **Nothing OS** and **Glassmorphism**.

**GitHub Repository:** [https://github.com/rkriad585/WebPlay](https://github.com/rkriad585/WebPlay)

---

## 🚀 How It Works

WebPlay acts as a bridge between your local file system and your web browser.

1.  **Scanning:** When you start the app, it scans the directory you specify.
2.  **Hosting:** It starts a local web server (using Flask).
3.  **Transcoding:**
    *   **Native Play:** Files like `.mp4` and `.webm` are streamed directly to the browser with zero latency.
    *   **On-the-Fly Transcoding:** Unsupported formats (like `.mkv`, `.avi`, `.flv`) are converted in real-time using **FFmpeg** pipes, so you can watch *anything* without converting files manually.
4.  **Remote Control:** It opens a WebSocket connection, allowing you to use your smartphone as a remote control for the player running on your PC.

---

## ✨ Features

### 🎨 UI/UX Design
*   **Modern Aesthetics:** A blend of Material 3 Expressive, Liquid Glass (Blur effects), and Nothing OS (Dot matrix fonts).
*   **Fully Responsive:** Looks like a native app on Mobile, Tablet, and Desktop.

### 🎥 Advanced Player
*   **Format Support:** Plays `.mp4`, `.mkv`, `.avi`, `.mov`, `.flv`, `.webm`, `.mp3`, `.wav`, `.flac`.
*   **Smart Resume:** Remembers exactly where you left off, even if you close the browser (SQLite Database).
*   **Audio Tracks:** Select between multiple audio languages (e.g., English/Japanese) directly in the player.
*   **Subtitles:** Auto-converts `.srt` files to WebVTT for browser compatibility.
*   **Picture-in-Picture:** Watch media while multitasking.
*   **Binge Mode:** Automatically plays the next episode in the folder.

### 🛠️ Functionality
*   **Remote Control:** Scan a code/visit a link to control volume, seek, and play/pause from your phone.
*   **Watch Party:** Sync playback with other devices on the network.
*   **Folder View:** Browse media by folders (like MX Player) or a flat list.
*   **Smart Search:** Instantly filter videos by name.
*   **Hardware Acceleration:** Utilizes FFmpeg hardware capabilities where available.

---

## 📂 Project Structure

Here is how the project is organized.

```text
WebPlay/
  ├── app.py                # 🚀 The Main Application Entry Point (Routes & Logic)
  ├── config.py             # ⚙️ Configuration settings & Path persistence
  ├── requirements.txt      # 📦 List of Python dependencies
  ├── static/
  │   └── images
  │       └── logo.svg      # 🎨 Project Logo
  ├── core/                 # 🧠 Core Logic Module
  │   ├── media.py          #    Media scanning, Metadata extraction, Thumbnails
  │   └── utils.py          #    Styling, Logging, and Helper functions
  └── templates/            # 🖥️ HTML Frontend
      ├── base.html         #    Base layout (Navbar, Footer, CSS imports)
      ├── error.html        #    Beautiful "Access Denied" page
      ├── index.html        #    Home Gallery (Grid/List/Folder views)
      ├── player.html       #    Video Player interface
      └── remote.html       #    Mobile Remote Control interface
```

---

## 🛠️ Installation

### Prerequisites
1.  **Python 3.8+**: Ensure Python is installed.
2.  **FFmpeg**: This is **crucial**. WebPlay uses FFmpeg for metadata and transcoding.
    *   *Windows:* Download and add to System PATH.
    *   *Linux:* `sudo apt install ffmpeg`
    *   *Termux:* `pkg install ffmpeg`

### Steps
1.  **Clone the Repository**
    ```bash
    git clone https://github.com/rkriad585/WebPlay.git
    cd WebPlay
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

---

## 💻 Usage

WebPlay is controlled via the Command Line Interface (CLI).

### 1. Set Your Media Folder

Tell WebPlay where your videos/music are located.

  ```bash
  python app.py path "C:/Users/Name/Videos"
  # Or on Linux/Termux
  python app.py path "/storage/emulated/0/Movies"
  ```

### 2. Start in Secured Mode (Recommended)

Starts the server with a randomly generated API Key. Only users with the link can access files.

  ```bash
  python app.py start
  ```
  *Output:*

  ```text
  [INFO] Server starting at: http://127.0.0.1:5000?key=xxxxx-xxxxx
  [WARNING] Keep this key secret! Copy the full URL above.
  ```

### 3. Start in Free Mode

Starts the server without password protection. Useful for home LAN.

  ```bash
  python app.py free
  ```
  *Output:*
  
  ```text
  [INFO] Server starting at: http://127.0.0.1:5000
  ```

### 4. Custom Port

You can specify a port (default is 5000).

  ```bash
  python app.py free --port 8080
  ```

---

## ⚙️ Configuration

*   **Database:** Playback progress is stored in `webplay.db` (SQLite) automatically created in the root folder.
*   **Cache:** Thumbnails are cached in `.webplay_cache/` to speed up loading times.
*   **Settings:** The last used folder path is saved in `webplay_settings.json`.

To reset the app, simply delete `webplay.db` and `webplay_settings.json`.

---

## 🤝 Contributions & Issues

Contributions are welcome! If you have ideas for new features or found a bug:

1.  **Fork** the repository.
2.  **Create** a new branch (`git checkout -b feature/AmazingFeature`).
3.  **Commit** your changes (`git commit -m 'Add some AmazingFeature'`).
4.  **Push** to the branch (`git push origin feature/AmazingFeature`).
5.  **Open** a Pull Request.

If you encounter any issues, please check the [Issues](https://github.com/rkriad585/WebPlay/issues) tab.

---

## 🌐 Connect with Me

I love building open-source tools! Connect with me on social media:

| Platform | Username | Link |
| :--- | :--- | :--- |
| **GitHub** | @rkriad585 | [github.com/rkriad585](https://github.com/rkriad585) |
| **YouTube** | @rkriad585 | [youtube.com/@rkriad585](https://youtube.com/@rkriad585) |
| **Facebook** | @rkriad585 | [facebook.com/rkriad585](https://facebook.com/rkriad585) |
| **X (Twitter)**| @rk_riad585| [x.com/rk_riad585](https://x.com/rk_riad585) |
| **Instagram** | @rkriad585 | [instagram.com/rkriad585](https://instagram.com/rkriad585) |
| **Threads** | @rkriad585 | [threads.net/@rkriad585](https://threads.net/@rkriad585) |
| **Email** | rkriad585 | `rkriad585@gmail.com` |

---

## 📜 License

This project is distributed under the **MIT License**.
You are free to use, modify, and distribute this software.

## MIT License

Copyright (c) 2024 RK Riad

Permission is hereby granted, free of charge, to any person obtaining a copy of this software...

---

<p align="center">
  Made with ❤️ by <b>RK Riad</b>
</p>
