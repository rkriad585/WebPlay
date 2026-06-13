# WebPlay Documentation

Welcome to the WebPlay documentation. WebPlay is a self-hosted media
streaming server that lets you stream your video and audio collection
to any device on your network.

## Getting Started

- [Setup Guide](setup.md) — Install and configure WebPlay
- [Usage Guide](usage.md) — How to use WebPlay
- [Configuration](configuration.md) — Configuration options

## Quick Install

### Linux / macOS

```bash
curl -fsSL https://raw.githubusercontent.com/rkriad585/WebPlay/main/installer.sh | sh
```

### Windows

```powershell
irm https://raw.githubusercontent.com/rkriad585/WebPlay/main/installer.ps1 | iex
```

After install, run `webplay path /path/to/media` to set your media folder,
then `webplay start` to begin streaming.

## Reference

- [CLI Reference](cli.md) — Command-line interface
- [Docker Guide](docker.md) — Running with Docker
- [Troubleshooting](troubleshooting.md) — Common issues

## Development

- [Development](development.md) — Setting up the dev environment
- [Deployment](deployment.md) — Production deployment
