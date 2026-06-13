# Deployment Guide

## Docker Deployment

The simplest way to deploy WebPlay is with Docker:

```bash
# Build
docker build -t webplay:latest .

# Run
docker run -d \
  --name webplay \
  --restart unless-stopped \
  -p 5000:5000 \
  -v /path/to/media:/media:ro \
  -e TRANSCODE_PRESET=ultrafast \
  -e TRANSCODE_CRF=28 \
  webplay
```

## One-Click Install (Non-Docker)

For direct deployment on a server:

```bash
curl -fsSL https://raw.githubusercontent.com/rkriad585/WebPlay/main/installer.sh | sh
webplay path /path/to/media
webplay start
```

## Docker Compose (Production)

```yaml
services:
  webplay:
    build: .
    image: webplay:latest
    ports:
      - "5000:5000"
    volumes:
      - /path/to/media:/media:ro
    environment:
      - WEBPLAY_DOMAIN=media.example.com
      - TRANSCODE_PRESET=ultrafast
      - TRANSCODE_CRF=28
    command: ["start", "--port", "5000"]
    restart: unless-stopped
```

Start:

```bash
docker compose up -d
```

View logs:

```bash
docker compose logs -f
```

## Reverse Proxy (Nginx)

```nginx
server {
    listen 443 ssl;
    server_name media.example.com;

    ssl_certificate /etc/ssl/certs/example.pem;
    ssl_certificate_key /etc/ssl/private/example.key;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Systemd Service (Linux)

Create `/etc/systemd/system/webplay.service`:

```ini
[Unit]
Description=WebPlay Media Server
After=network.target

[Service]
Type=simple
User=webplay
WorkingDirectory=/opt/webplay
ExecStart=/usr/local/bin/webplay start --port 5000
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable webplay
sudo systemctl start webplay
```

## Security Checklist

- [ ] Use secured mode (`start`) with API key
- [ ] Put behind a reverse proxy with HTTPS
- [ ] Restrict media volume to read-only (`:ro`)
- [ ] Keep WebPlay updated to latest version
- [ ] Use firewall rules to limit access
- [ ] Regularly check logs: `~/.config/neostore/webplay/history.log`
