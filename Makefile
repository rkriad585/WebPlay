VERSION := $(shell cat .version 2>/dev/null || echo "v0.0.0")
PIP := pip
PYTHON := python
DOCKER := docker
IMAGE := webplay

.PHONY: help build run clean test lint format install release docker-build docker-run

help:
	@echo "WebPlay v$(VERSION)"
	@echo ""
	@echo "Usage: make <target>"
	@echo ""
	@echo "Targets:"
	@echo "  install      Install Python dependencies"
	@echo "  run          Start WebPlay in free mode"
	@echo "  test         Run test suite"
	@echo "  lint         Lint source code"
	@echo "  format       Format source code"
	@echo "  clean        Remove build artifacts"
	@echo "  release      Create release archive"
	@echo "  docker-build Build Docker image"
	@echo "  docker-run   Run Docker container"
	@echo "  build        Alias for install"

install:
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

run:
	$(PYTHON) app.py free

test:
	$(PYTHON) -m pytest -v

lint:
	ruff check . || flake8 . || echo "No linter found (install ruff or flake8)"

format:
	black . || echo "black not found (install with: pip install black)"

clean:
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ __pycache__/ core/__pycache__/
	find . -name "*.pyc" -delete
	@echo "Clean complete."

release:
	mkdir -p dist/
	tar -czf dist/webplay-$(VERSION).tar.gz \
		--exclude="__pycache__" \
		--exclude="*.pyc" \
		--exclude=".git" \
		--exclude=".webplay_cache" \
		--exclude="webplay.db" \
		--exclude="build" \
		--exclude="dist" \
		.
	@echo "Release archive: dist/webplay-$(VERSION).tar.gz"

docker-build:
	$(DOCKER) build -t $(IMAGE):$(VERSION) -t $(IMAGE):latest .

docker-run:
	$(DOCKER) run -d \
		--name webplay \
		-p 5000:5000 \
		-v "$(PWD)/media:/media:ro" \
		-e WEBPLAY_DOMAIN= \
		-e TRANSCODE_PRESET=ultrafast \
		-e TRANSCODE_CRF=28 \
		$(IMAGE):latest
	@echo "Container started on http://localhost:5000"

build: install
