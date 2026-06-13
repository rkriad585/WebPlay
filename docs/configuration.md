# Configuration Guide

## Config File Location

WebPlay stores configuration in `~/.config/neostore/webplay/config.toml`.

Use `--config <path>` to use a custom config file:

```bash
python app.py start --config /path/to/config.toml
```

## Config File Format

```toml
[server]
port = 5000
domain = ""

[auth]
api_key = ""

[media]
path = "/path/to/media"

[transcode]
preset = "ultrafast"
crf = 28
```

## Sections

### `[server]`

| Key | Default | Description |
|-----|---------|-------------|
| `port` | `5000` | Server port |
| `domain` | `""` | Public domain for URL display |

### `[auth]`

| Key | Default | Description |
|-----|---------|-------------|
| `api_key` | (auto) | API key for secured mode |

### `[media]`

| Key | Default | Description |
|-----|---------|-------------|
| `path` | `""` | Absolute path to media directory |

### `[transcode]`

| Key | Default | Description |
|-----|---------|-------------|
| `preset` | `"ultrafast"` | FFmpeg transcode preset |
| `crf` | `28` | FFmpeg CRF value (quality) |

## Environment Variables

| Variable | Overrides |
|----------|-----------|
| `TRANSCODE_PRESET` | `[transcode].preset` |
| `TRANSCODE_CRF` | `[transcode].crf` |
| `WEBPLAY_DOMAIN` | `[server].domain` |

## CLI Flags

Flags take precedence over config file and environment variables:

```bash
python app.py start --port 8080 --domain example.com
```

## API Key

The API key is generated on `start` and saved to
`~/.config/neostore/webplay/.webplay_key.txt`. Recover it with:

```bash
python app.py key
```

## Data Directory

| Item | Location |
|------|----------|
| Config | `~/.config/neostore/webplay/config.toml` |
| Database | `~/.config/neostore/webplay/webplay.db` |
| Thumbnails | `~/.config/neostore/webplay/.webplay_cache/` |
| Logs | `~/.config/neostore/webplay/history.log` |
| Key backup | `~/.config/neostore/webplay/.webplay_key.txt` |
| Downloads | `~/Downloads/neostore/webplay/` |

## Reset

Delete both files to reset all state:

```bash
rm -f ~/.config/neostore/webplay/webplay.db ~/.config/neostore/webplay/config.toml
```
