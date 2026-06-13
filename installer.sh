#!/usr/bin/env bash
set -euo pipefail

REPO="rkriad585/WebPlay"
PROJECT="webplay"
INSTALL_DIR="${INSTALL_DIR:-/usr/local/lib/$PROJECT}"
BIN_DIR="${BIN_DIR:-/usr/local/bin}"
TMP_DIR=$(mktemp -d)
trap 'rm -rf "$TMP_DIR"' EXIT

# ---- colors ----
RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

info()  { echo -e "${CYAN}[INFO]${NC}  $*"; }
ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
err()   { echo -e "${RED}[ERROR]${NC} $*" >&2; }

# ---- platform detection ----
detect_arch() {
    local arch
    arch=$(uname -m)
    case "$arch" in
        x86_64|amd64)  echo "x86_64" ;;
        aarch64|arm64) echo "aarch64" ;;
        i686|i386)     echo "i686"   ;;
        *)             echo "$arch"  ;;
    esac
}

require_python() {
    if command -v python3 &>/dev/null; then
        PYTHON=python3
    elif command -v python &>/dev/null; then
        PYTHON=python
    else
        err "Python 3 is required but not found."
        err "Install Python 3 from https://python.org and try again."
        exit 1
    fi

    local ver
    ver=$("$PYTHON" --version 2>&1 | grep -oP '\d+\.\d+')
    if awk -v v="$ver" 'BEGIN { exit (v < 3.11) }'; then
        err "Python 3.11+ is required (found $ver)."
        exit 1
    fi
    ok "Python $ver detected"
}

require_pip() {
    if ! command -v pip3 &>/dev/null && ! "$PYTHON" -m pip --version &>/dev/null; then
        err "pip is not installed."
        err "Install pip and try again."
        exit 1
    fi
    ok "pip detected"
}

require_curl() {
    if command -v curl &>/dev/null; then
        DOWNLOAD_CMD="curl -sL"
    elif command -v wget &>/dev/null; then
        DOWNLOAD_CMD="wget -qO-"
    else
        err "Either curl or wget is required."
        exit 1
    fi
}

get_latest_version() {
    local url="https://api.github.com/repos/$REPO/releases/latest"
    $DOWNLOAD_CMD "$url" | grep '"tag_name"' | head -1 | sed 's/.*"tag_name": "//;s/".*//'
}

download_release() {
    local version="$1"
    local url="https://github.com/$REPO/archive/refs/tags/$version.tar.gz"
    local archive="$TMP_DIR/release.tar.gz"

    info "Downloading $PROJECT $version..."
    if command -v curl &>/dev/null; then
        curl -sL "$url" -o "$archive"
    else
        wget -q "$url" -O "$archive"
    fi

    if [ ! -f "$archive" ] || [ ! -s "$archive" ]; then
        err "Download failed."
        exit 1
    fi

    tar -xzf "$archive" -C "$TMP_DIR"
    EXTRACTED_DIR=$(find "$TMP_DIR" -maxdepth 1 -type d | tail -1)
    ok "Downloaded and extracted $version"
}

install_project() {
    info "Installing $PROJECT..."
    "$PYTHON" -m pip install --upgrade pip --quiet
    "$PYTHON" -m pip install "$EXTRACTED_DIR" --quiet
    ok "$PROJECT installed via pip"

    local pip_bin
    pip_bin=$("$PYTHON" -c "import sysconfig; print(sysconfig.get_path('scripts'))" 2>/dev/null || "$PYTHON" -m site --user-base 2>/dev/null)
    if [ -d "$pip_bin" ]; then
        local cmd_path="$pip_bin/$PROJECT"
        if [ -f "$cmd_path" ]; then
            info "Binary location: $cmd_path"
            ensure_path "$pip_bin"
        fi
    fi
}

ensure_path() {
    local dir="$1"
    case "${SHELL:-}" in
        *zsh*)  PROFILE="${ZDOTDIR:-$HOME}/.zshrc" ;;
        *bash*) PROFILE="$HOME/.bashrc" ;;
        *)      PROFILE="$HOME/.profile" ;;
    esac

    if echo ":$PATH:" | grep -q ":$dir:"; then
        ok "$dir already in PATH"
        return
    fi

    if [ -f "$PROFILE" ]; then
        {
            echo ""
            echo "# Added by $PROJECT installer"
            echo "export PATH=\"$dir:\$PATH\""
        } >> "$PROFILE"
        warn "Added $dir to PATH in $PROFILE"
        warn "Restart your shell or run: export PATH=\"$dir:\$PATH\""
    else
        warn "Could not update PATH automatically."
        warn "Add the following to your shell profile:"
        warn "  export PATH=\"$dir:\$PATH\""
    fi
}

show_banner() {
    local version="$1"
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║       WebPlay v${version} installed!        ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════╝${NC}"
    echo ""
    echo "  Run:  webplay path /path/to/media"
    echo "        webplay start"
    echo ""
    echo "  Docs: https://github.com/$REPO"
    echo ""
}

uninstall_project() {
    info "Uninstalling $PROJECT..."

    "$PYTHON" -m pip uninstall "$PROJECT" -y 2>/dev/null && ok "pip package removed" || warn "pip package not found"

    local config_dir="${XDG_CONFIG_HOME:-$HOME/.config}/neostore/$PROJECT"
    if [ -d "$config_dir" ]; then
        rm -rf "$config_dir"
        ok "Config directory removed: $config_dir"
    fi

    local cache_dir="${XDG_CACHE_HOME:-$HOME/.cache}/neostore/$PROJECT"
    if [ -d "$cache_dir" ]; then
        rm -rf "$cache_dir"
        ok "Cache directory removed: $cache_dir"
    fi

    local data_dir="${XDG_DATA_HOME:-$HOME/.local/share}/neostore/$PROJECT"
    if [ -d "$data_dir" ]; then
        rm -rf "$data_dir"
        ok "Data directory removed: $data_dir"
    fi

    local downloads_dir="$HOME/Downloads/neostore/$PROJECT"
    if [ -d "$downloads_dir" ]; then
        rm -rf "$downloads_dir"
        ok "Downloads directory removed: $downloads_dir"
    fi

    if [ -d "$INSTALL_DIR" ]; then
        rm -rf "$INSTALL_DIR"
        ok "Install directory removed: $INSTALL_DIR"
    fi

    info "Uninstall complete."
}

# ---- main ----
main() {
    if [ "${1:-}" = "--selfuninstall" ]; then
        require_python
        uninstall_project
        exit 0
    fi

    echo ""
    info "Installing $PROJECT from $REPO"
    echo ""

    require_python
    require_pip
    require_curl

    local version
    version=$(get_latest_version)
    if [ -z "$version" ]; then
        err "Could not determine latest version from GitHub."
        info "Falling back to pip install from repository..."
        "$PYTHON" -m pip install "git+https://github.com/$REPO.git" --quiet
        ok "$PROJECT installed from Git repository"
        show_banner "latest"
        exit 0
    fi

    download_release "$version"
    install_project
    show_banner "$version"
}

main "$@"
