# WebPlay Build Script for Windows (PowerShell)
param(
    [ValidateSet('clean', 'install', 'test', 'lint', 'format', 'run', 'docker-build', 'docker-run', 'release', 'all')]
    [string]$Command = 'help'
)

$Version = if (Test-Path '.version') { Get-Content '.version' -Raw }.Trim() else { 'v0.0.0' }

function Invoke-Clean {
    Write-Host "Cleaning build artifacts..." -ForegroundColor Cyan
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue 'build', 'dist', '*.egg-info', '.pytest_cache', '__pycache__'
    Get-ChildItem -Recurse -Filter '*.pyc' | Remove-Item -Force
    Write-Host "Clean complete." -ForegroundColor Green
}

function Invoke-Install {
    Write-Host "Installing dependencies..." -ForegroundColor Cyan
    pip install --upgrade pip
    pip install -r requirements.txt
    Write-Host "Dependencies installed." -ForegroundColor Green
}

function Invoke-Test {
    Write-Host "Running tests..." -ForegroundColor Cyan
    python -m pytest -v
    Write-Host "Tests complete." -ForegroundColor Green
}

function Invoke-Lint {
    Write-Host "Linting..." -ForegroundColor Cyan
    python -m ruff check . 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "No linter found (ruff). Install with: pip install ruff" -ForegroundColor Yellow
    }
}

function Invoke-Format {
    Write-Host "Formatting..." -ForegroundColor Cyan
    python -m black . 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "black not found. Install with: pip install black" -ForegroundColor Yellow
    }
}

function Invoke-Run {
    Write-Host "Starting WebPlay in free mode..." -ForegroundColor Cyan
    python app.py free
}

function Invoke-DockerBuild {
    Write-Host "Building Docker image..." -ForegroundColor Cyan
    docker build -t "webplay:$Version" -t webplay:latest .
    Write-Host "Docker image built: webplay:$Version" -ForegroundColor Green
}

function Invoke-DockerRun {
    Write-Host "Running WebPlay container..." -ForegroundColor Cyan
    docker run -d `
        --name webplay `
        -p 5000:5000 `
        -v "${PWD}/media:/media:ro" `
        -e WEBPLAY_DOMAIN= `
        -e TRANSCODE_PRESET=ultrafast `
        -e TRANSCODE_CRF=28 `
        webplay:latest
    Write-Host "Container started on http://localhost:5000" -ForegroundColor Green
}

function Invoke-Release {
    Write-Host "Building release artifacts..." -ForegroundColor Cyan
    New-Item -ItemType Directory -Force -Path 'dist' | Out-Null
    # Create tar file containing the project
    tar -czf "dist/webplay-$Version.tar.gz" `
        --exclude=__pycache__ `
        --exclude='*.pyc' `
        --exclude=.git `
        --exclude=.webplay_cache `
        --exclude=webplay.db `
        --exclude=build `
        --exclude=dist `
        .
    Write-Host "Release archive: dist/webplay-$Version.tar.gz" -ForegroundColor Green
}

switch ($Command) {
    'clean'        { Invoke-Clean }
    'install'      { Invoke-Install }
    'test'         { Invoke-Test }
    'lint'         { Invoke-Lint }
    'format'       { Invoke-Format }
    'run'          { Invoke-Run }
    'docker-build' { Invoke-DockerBuild }
    'docker-run'   { Invoke-DockerRun }
    'release'      { Invoke-Release }
    'all'          {
        Invoke-Clean
        Invoke-Install
        Invoke-Lint
        Invoke-Test
    }
    default {
        Write-Host @"
WebPlay Build Script v$Version

Usage: .\build.ps1 <command>

Commands:
  clean        Remove build artifacts
  install      Install Python dependencies
  test         Run test suite
  lint         Lint source code
  format       Format source code
  run          Start WebPlay in free mode
  docker-build Build Docker image
  docker-run   Run Docker container
  release      Create release archive
  all          Run clean, install, lint, test
"@
    }
}
