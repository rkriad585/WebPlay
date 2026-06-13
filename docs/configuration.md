# Configuration Guide

## Config File Location

WebPlay stores configuration in `~/.config/neostore/webplay/config.toml`.

Use `--config <path>` to use a custom config file:

```bash
webplay start --config /path/to/config.toml
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

[theme]
name = "dark"
mode = "dark"
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

### `[theme]`

| Key | Default | Description |
|-----|---------|-------------|
| `name` | `"dark"` | Theme slug (see available themes below) |
| `mode` | `"dark"` | `"dark"` or `"light"` — overridden by theme |

Available themes: `dark`, `midnight_blue`, `forest_night`, `violet_dusk`, `warm_ember`, `cherry_red`, `amoled`, `light_clean`, `ocean_breeze`, `sunny_day`, `mint_fresh`, `lavender`.

Themes can be switched at runtime via the palette icon in the navbar or by POSTing to `/api/theme` with `{"name": "theme_slug"}`.

## Environment Variables

| Variable | Overrides |
|----------|-----------|
| `TRANSCODE_PRESET` | `[transcode].preset` |
| `TRANSCODE_CRF` | `[transcode].crf` |
| `WEBPLAY_DOMAIN` | `[server].domain` |

## CLI Flags

Flags take precedence over config file and environment variables:

```bash
webplay start --port 8080 --domain example.com
```

## API Key

The API key is generated on `start` and saved to
`~/.config/neostore/webplay/.webplay_key.txt`. Recover it with:

```bash
webplay key
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
