# Contributing to WebPlay

Thank you for considering contributing to WebPlay! We welcome contributions
of all kinds: bug fixes, new features, documentation improvements, and more.

## Getting Started

1. Fork the repository.
2. Clone your fork:
   ```bash
   git clone https://github.com/your-username/WebPlay.git
   cd WebPlay
   ```
3. Create a branch for your work:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Setup

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Running Tests

```bash
python -m pytest -v
```

All tests must pass before your contribution is merged.

## Code Style

- Use [Black](https://github.com/psf/black) for Python formatting.
- Use [Ruff](https://github.com/astral-sh/ruff) for linting.
- Keep functions focused and small.
- Write meaningful docstrings where needed.

## Commit Guidelines

- Use clear, descriptive commit messages.
- Reference issue numbers when applicable.
- Keep commits focused on single changes.

## Pull Request Process

1. Ensure your code builds and tests pass.
2. Update documentation if adding or changing features.
3. Create a pull request against the `main` branch.
4. We'll review your PR and provide feedback.

## Code of Conduct

All contributors must adhere to our [Code of Conduct](CODE_OF_CONDUCT.md).

## Questions?

Open an issue or reach out to rkriad585@gmail.com.
