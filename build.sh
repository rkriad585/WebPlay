#!/usr/bin/env bash
set -euo pipefail

VERSION=$(cat .version 2>/dev/null || echo "v0.0.0")
echo "Building WebPlay $VERSION ..."

clean() {
    echo "Cleaning build artifacts..."
    rm -rf build/ dist/ *.egg-info/ .pytest_cache/ __pycache__/ core/__pycache__/
    find . -name "*.pyc" -delete
    echo "Clean complete."
}

install() {
    echo "Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    echo "Dependencies installed."
}

test() {
    echo "Running tests..."
    python -m pytest -v
    echo "Tests complete."
}

lint() {
    echo "Linting..."
    if command -v ruff &>/dev/null; then
        ruff check .
    elif command -v flake8 &>/dev/null; then
        flake8 .
    else
        echo "No linter found. Install ruff or flake8."
    fi
}

format() {
    echo "Formatting..."
    if command -v black &>/dev/null; then
        black .
    else
        echo "black not found. Install with: pip install black"
    fi
}

run() {
    echo "Starting WebPlay in free mode..."
    python app.py free
}

docker_build() {
    echo "Building Docker image..."
    docker build -t webplay:"$VERSION" -t webplay:latest .
    echo "Docker image built: webplay:$VERSION"
}

docker_run() {
    echo "Running WebPlay container..."
    docker run -d \
        --name webplay \
        -p 5000:5000 \
        -v "$(pwd)/media:/media:ro" \
        -e WEBPLAY_DOMAIN= \
        -e TRANSCODE_PRESET=ultrafast \
        -e TRANSCODE_CRF=28 \
        webplay:latest
    echo "Container started on http://localhost:5000"
}

release() {
    echo "Building release artifacts..."
    mkdir -p dist/
    tar -czf "dist/webplay-${VERSION}.tar.gz" \
        --exclude="__pycache__" \
        --exclude="*.pyc" \
        --exclude=".git" \
        --exclude=".webplay_cache" \
        --exclude="webplay.db" \
        --exclude="build" \
        --exclude="dist" \
        .
    echo "Release archive: dist/webplay-${VERSION}.tar.gz"
}

case "${1:-help}" in
    clean) clean ;;
    install) install ;;
    test) test ;;
    lint) lint ;;
    format) format ;;
    run) run ;;
    docker-build) docker_build ;;
    docker-run) docker_run ;;
    release) release ;;
    all)
        clean
        install
        lint
        test
        run
        ;;
    *)
        echo "WebPlay Build Script v$(cat .version 2>/dev/null || echo '?')"
        echo ""
        echo "Usage: ./build.sh <command>"
        echo ""
        echo "Commands:"
        echo "  clean        Remove build artifacts"
        echo "  install      Install Python dependencies"
        echo "  test         Run test suite"
        echo "  lint         Lint source code"
        echo "  format       Format source code"
        echo "  run          Start WebPlay in free mode"
        echo "  docker-build Build Docker image"
        echo "  docker-run   Run Docker container"
        echo "  release      Create release archive"
        echo "  all          Run clean, install, lint, test"
        ;;
esac
