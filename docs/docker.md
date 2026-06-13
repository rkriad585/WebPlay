# Docker Guide

## Building

```bash
# Build the image
docker build -t webplay .

# Build with a specific version tag
docker build -t webplay:v0.156.36 -t webplay:latest .
```

## Running

### Basic

```bash
docker run -d \
  --name webplay \
  -p 5000:5000 \
  -v /path/to/media:/media:ro \
  webplay
```

### With environment variables

```bash
docker run -d \
  --name webplay \
  -p 8080:5000 \
  -v /path/to/media:/media:ro \
  -e WEBPLAY_DOMAIN=example.com \
  -e TRANSCODE_PRESET=medium \
  -e TRANSCODE_CRF=23 \
  webplay
```

### Secured mode

```bash
docker run -d \
  --name webplay \
  -p 5000:5000 \
  -v /path/to/media:/media:ro \
  webplay start --port 5000
```

## Docker Compose

```yaml
services:
  webplay:
    build: .
    image: webplay:latest
    ports:
      - "5000:5000"
    volumes:
      - ./media:/media:ro
    environment:
      - WEBPLAY_DOMAIN=
      - TRANSCODE_PRESET=ultrafast
      - TRANSCODE_CRF=28
    command: ["free", "--port", "5000"]
    restart: unless-stopped
```

Start with:

```bash
docker compose up -d
```

## Multi-stage Build

The Dockerfile uses a multi-stage build:

1. **Builder stage** — installs Python dependencies
2. **Runtime stage** — copies only the installed packages, keeping the
   final image small

FFmpeg is installed in the runtime stage from system packages.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `WEBPLAY_DOMAIN` | `""` | Public domain |
| `TRANSCODE_PRESET` | `ultrafast` | FFmpeg preset |
| `TRANSCODE_CRF` | `28` | FFmpeg quality |
