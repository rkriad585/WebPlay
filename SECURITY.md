# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| latest  | :white_check_mark: |

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability,
please **do not** open a public issue. Instead, report it privately:

- Email: rkriad585@gmail.com

Please include as much detail as possible:
- Steps to reproduce
- Impact description
- Suggested fix (if available)

You should receive a response within 48 hours. We'll keep you informed
as we work on a fix.

## Security Best Practices

When deploying WebPlay:

1. **Use secured mode** (`python app.py start`) with the auto-generated API key.
2. **Do not expose port 5000** directly to the internet without a reverse proxy.
3. **Keep dependencies updated** — review `requirements.txt` regularly.
4. **Validate media paths** — WebPlay rejects paths outside the configured media directory.
5. **Use HTTPS** in production — put WebPlay behind Nginx/Caddy with TLS.
