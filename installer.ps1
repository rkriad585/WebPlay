#!/usr/bin/env pwsh
param(
    [switch]$selfuninstall
)

$ErrorActionPreference = "Stop"
$Repo = "rkriad585/WebPlay"
$Project = "webplay"

# ---- helpers ----
function Write-Info  { Write-Host "[INFO]  $($args[0])" -ForegroundColor Cyan }
function Write-Ok    { Write-Host "[OK]    $($args[0])" -ForegroundColor Green }
function Write-Warn  { Write-Host "[WARN]  $($args[0])" -ForegroundColor Yellow }
function Write-Err   { Write-Host "[ERROR] $($args[0])" -ForegroundColor Red -ErrorAction Continue }

# ---- platform detection ----
function Get-Architecture {
    $arch = if ([Environment]::Is64BitOperatingSystem) { "x86_64" } else { "i686" }
    return $arch
}

function Test-Python {
    $python = Get-Command python -ErrorAction SilentlyContinue
    if (-not $python) {
        $python = Get-Command python3 -ErrorAction SilentlyContinue
    }
    if (-not $python) {
        Write-Err "Python 3 is required but not found."
        Write-Err "Install Python 3 from https://python.org and try again."
        exit 1
    }

    $ver = & $python.Source -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
    if ([version]$ver -lt [version]"3.11") {
        Write-Err "Python 3.11+ is required (found $ver)."
        exit 1
    }
    Write-Ok "Python $ver detected"
    return $python.Source
}

function Test-Pip {
    $pip = Get-Command pip -ErrorAction SilentlyContinue
    if (-not $pip) {
        $pip = Get-Command pip3 -ErrorAction SilentlyContinue
    }
    if (-not $pip) {
        Write-Err "pip is not installed."
        Write-Err "Install pip and try again."
        exit 1
    }
    Write-Ok "pip detected"
    return $pip.Source
}

function Get-LatestVersion {
    $url = "https://api.github.com/repos/$Repo/releases/latest"
    try {
        $response = Invoke-WebRequest -Uri $url -UseBasicParsing -ErrorAction Stop
        $json = $response.Content | ConvertFrom-Json
        return $json.tag_name
    } catch {
        return $null
    }
}

function Download-Release {
    param([string]$Version)

    $url = "https://github.com/$Repo/archive/refs/tags/$Version.tar.gz"
    $archive = "$env:TEMP\webplay-release.tar.gz"
    $extractDir = "$env:TEMP\webplay-install"

    Write-Info "Downloading $Project $Version..."
    try {
        Invoke-WebRequest -Uri $url -OutFile $archive -UseBasicParsing -ErrorAction Stop
    } catch {
        Write-Err "Download failed: $_"
        exit 1
    }

    if (-not (Test-Path $archive)) {
        Write-Err "Download failed — file not found."
        exit 1
    }

    if (Test-Path $extractDir) {
        Remove-Item -Recurse -Force $extractDir
    }
    New-Item -ItemType Directory -Force -Path $extractDir | Out-Null

    tar -xzf $archive -C $extractDir
    $extracted = Get-ChildItem $extractDir -Directory | Select-Object -First 1
    Write-Ok "Downloaded and extracted $Version"
    return $extracted.FullName
}

function Install-Project {
    param([string]$SourcePath)

    Write-Info "Installing $Project..."
    & pip install --upgrade pip --quiet 2>$null
    & pip install $SourcePath --quiet
    if ($LASTEXITCODE -ne 0) {
        Write-Err "pip install failed."
        exit 1
    }
    Write-Ok "$Project installed via pip"

    $pipBin = & python -c "import sysconfig; print(sysconfig.get_path('scripts'))" 2>$null
    if ($pipBin -and (Test-Path "$pipBin\$Project.exe" -or (Test-Path "$pipBin\$Project"))) {
        Write-Info "Binary location: $pipBin\$Project"
        Add-ToPath $pipBin
    }
}

function Add-ToPath {
    param([string]$Dir)

    $userPath = [Environment]::GetEnvironmentVariable("PATH", "User")
    if ($userPath -split ";" | Where-Object { $_ -eq $Dir }) {
        Write-Ok "$Dir already in PATH"
        return
    }

    $newPath = "$Dir;$userPath"
    [Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
    $env:PATH = "$Dir;$env:PATH"
    Write-Warn "Added $Dir to user PATH"
    Write-Warn "Restart your terminal or refresh environment variables"
}

function Show-Banner {
    param([string]$Version)

    Write-Host ""
    Write-Host "╔══════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║       WebPlay v$Version installed!        ║" -ForegroundColor Green
    Write-Host "╚══════════════════════════════════════════╝" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Run:  webplay path C:\path\to\media"
    Write-Host "        webplay start"
    Write-Host ""
    Write-Host "  Docs: https://github.com/$Repo"
    Write-Host ""
}

function Uninstall-Project {
    Write-Info "Uninstalling $Project..."

    & pip uninstall $Project -y 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Ok "pip package removed"
    } else {
        Write-Warn "pip package not found"
    }

    $configDir = "$env:USERPROFILE\.config\neostore\$Project"
    if (Test-Path $configDir) {
        Remove-Item -Recurse -Force $configDir
        Write-Ok "Config directory removed: $configDir"
    }

    $cacheDir = "$env:USERPROFILE\.cache\neostore\$Project"
    if (Test-Path $cacheDir) {
        Remove-Item -Recurse -Force $cacheDir
        Write-Ok "Cache directory removed: $cacheDir"
    }

    $dataDir = "$env:LOCALAPPDATA\neostore\$Project"
    if (Test-Path $dataDir) {
        Remove-Item -Recurse -Force $dataDir
        Write-Ok "Data directory removed: $dataDir"
    }

    $downloadsDir = "$env:USERPROFILE\Downloads\neostore\$Project"
    if (Test-Path $downloadsDir) {
        Remove-Item -Recurse -Force $downloadsDir
        Write-Ok "Downloads directory removed: $downloadsDir"
    }

    Write-Info "Uninstall complete."
}

function Install-Main {
    Write-Host ""
    Write-Info "Installing $Project from $Repo"
    Write-Host ""

    # Detect architecture
    $arch = Get-Architecture
    Write-Info "Architecture: $arch"

    # Detect Python
    $pythonPath = Test-Python
    $pipPath = Test-Pip

    # Get latest version from GitHub
    $version = Get-LatestVersion
    if (-not $version) {
        Write-Err "Could not determine latest version from GitHub."
        Write-Info "Falling back to pip install from repository..."
        & pip install "git+https://github.com/$Repo.git" --quiet
        if ($LASTEXITCODE -eq 0) {
            Write-Ok "$Project installed from Git repository"
            Show-Banner "latest"
        }
        exit
    }

    # Download and install
    $sourcePath = Download-Release $version
    Install-Project $sourcePath
    Show-Banner $version
}

# ---- main ----
if ($selfuninstall) {
    Uninstall-Project
} else {
    Install-Main
}
