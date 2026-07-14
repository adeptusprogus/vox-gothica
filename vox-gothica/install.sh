#!/usr/bin/env bash
# Vox Gothica installer — macOS & Linux.
#
# Default: download pre-built binary from GitHub Releases (no Python).
#
#   curl -fsSL https://raw.githubusercontent.com/adeptusprogus/vox-gothica/main/vox-gothica/install.sh | bash
#
# Options:
#   --version v0.2.0   specific release (default: latest)
#   --from-source      build via pip/pipx (needs Python 3.10+)
#   --pyz              zipapp into ~/.local/bin (needs Python 3.10+)
#   --fix-path         append ~/.local/bin to shell rc (~/.zshrc or ~/.bashrc)
set -euo pipefail

REPO="adeptusprogus/vox-gothica"
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="${HOME}/.local/bin"
PATH_MARKER="# vox-gothica PATH"
PATH_EXPORT='export PATH="$HOME/.local/bin:$PATH"'
VERSION=""
FROM_SOURCE=0
PYZ=0
FIX_PATH=0

say()  { printf '⚙ %s\n' "$*"; }
warn() { printf '⚙ %s\n' "$*" >&2; }
die()  { printf '⚙ HERESIS: %s\n' "$*" >&2; exit 1; }

while [[ $# -gt 0 ]]; do
    case "$1" in
        --version) VERSION="$2"; shift 2 ;;
        --from-source) FROM_SOURCE=1; shift ;;
        --pyz) PYZ=1; shift ;;
        --fix-path) FIX_PATH=1; shift ;;
        -h|--help)
            sed -n '2,13p' "$0"
            exit 0
            ;;
        *) die "Unknown option: $1 (try --help)" ;;
    esac
done

path_has_bin_dir() {
    case ":$PATH:" in
        *":$BIN_DIR:"*) return 0 ;;
    esac
    return 1
}

shell_rc_file() {
    if [[ -n "${ZSH_VERSION:-}" ]] && [[ -f "${HOME}/.zshrc" ]]; then
        echo "${HOME}/.zshrc"
    elif [[ "${SHELL:-}" == *zsh* ]] && [[ -f "${HOME}/.zshrc" ]]; then
        echo "${HOME}/.zshrc"
    elif [[ -f "${HOME}/.bashrc" ]]; then
        echo "${HOME}/.bashrc"
    elif [[ -f "${HOME}/.zshrc" ]]; then
        echo "${HOME}/.zshrc"
    else
        echo "${HOME}/.zshrc"
    fi
}

path_line_in_rc() {
    local rc="$1"
    [[ -f "$rc" ]] || return 1
    grep -qE '^[[:space:]]*export[[:space:]]+PATH=.*\.local/bin' "$rc" 2>/dev/null
}

fix_path_in_rc() {
    local rc
    rc="$(shell_rc_file)"
    if path_line_in_rc "$rc" || grep -qF "$PATH_MARKER" "$rc" 2>/dev/null; then
        say "PATH already configured in ${rc}"
        return 0
    fi
    printf '\n%s\n%s\n' "$PATH_MARKER" "$PATH_EXPORT" >>"$rc"
    say "Appended PATH to ${rc}"
    say "Reload your shell:  source ${rc}"
}

warn_path_required() {
    local rc
    rc="$(shell_rc_file)"
    warn ""
    warn "═══════════════════════════════════════════════════════════════"
    warn " ACTION REQUIRED — gothica is installed but not on your PATH"
    warn "═══════════════════════════════════════════════════════════════"
    warn " Binary: ${BIN_DIR}/gothica"
    warn ""
    warn " The installer cannot change your shell automatically unless"
    warn " you pass --fix-path. Until PATH is set, 'gothica' will fail"
    warn " with: zsh: command not found: gothica"
    warn ""
    warn " [1] This terminal only (temporary):"
    warn "     export PATH=\"\$HOME/.local/bin:\$PATH\""
    warn "     gothica versio"
    warn ""
    warn " [2] Every new terminal — add to ${rc}:"
    warn "     ${PATH_EXPORT}"
    warn "     source ${rc}"
    warn ""
    warn " [3] Let the installer patch ${rc} for you:"
    warn "     ./install.sh --fix-path"
    warn "     source ${rc}"
    warn ""
    warn " [4] Run by full path (always works):"
    warn "     ${BIN_DIR}/gothica versio"
    warn "═══════════════════════════════════════════════════════════════"
    warn ""
}

find_python() {
    for p in python3.13 python3.12 python3.11 python3.10 python3; do
        if command -v "$p" >/dev/null 2>&1; then
            if "$p" -c 'import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)'; then
                echo "$p"; return
            fi
        fi
    done
    die "Python >= 3.10 was not found."
}

detect_asset() {
    local os arch
    os="$(uname -s)"
    arch="$(uname -m)"
    case "$os" in
        Darwin)
            case "$arch" in
                arm64)  echo "gothica-darwin-arm64" ;;
                x86_64) echo "gothica-darwin-amd64" ;;
                *) die "Unsupported macOS architecture: $arch" ;;
            esac ;;
        Linux)
            case "$arch" in
                x86_64|amd64) echo "gothica-linux-amd64" ;;
                *) die "Unsupported Linux architecture: $arch (build from source with --from-source)" ;;
            esac ;;
        *)
            die "Unsupported OS: $os — use install.ps1 on Windows"
            ;;
    esac
}

resolve_version() {
    if [[ -n "$VERSION" ]]; then
        echo "$VERSION"
        return
    fi
    local tag
    tag="$(curl -fsSL "https://api.github.com/repos/${REPO}/releases/latest" \
        | sed -n 's/.*"tag_name": *"\([^"]*\)".*/\1/p' | head -1)"
    [[ -n "$tag" ]] || die "Could not resolve latest release from GitHub."
    echo "$tag"
}

install_binary() {
    local tag asset url tmp
    tag="$(resolve_version)"
    asset="$(detect_asset)"
    url="https://github.com/${REPO}/releases/download/${tag}/${asset}"
    say "Fetching ${tag} → ${asset} ..."
    mkdir -p "$BIN_DIR"
    tmp="$(mktemp)"
    curl -fsSL "$url" -o "$tmp"
    chmod +x "$tmp"
    mv "$tmp" "$BIN_DIR/gothica"
    say "Installed: $BIN_DIR/gothica (${tag})"
}

install_from_source() {
    local PY
    PY="$(find_python)"
    say "Python found: $($PY --version)"
    if command -v pipx >/dev/null 2>&1; then
        say "Consecrating via pipx ..."
        pipx install --force "$DIR"
        say "pipx installs into ~/.local/bin — ensure it is on PATH (see below)."
    else
        say "Consecrating via pip (--user) ..."
        "$PY" -m pip install --user --quiet --upgrade "$DIR" \
            || "$PY" -m pip install --user --quiet --upgrade --break-system-packages "$DIR"
        say "pip --user installs scripts into ~/.local/bin — ensure it is on PATH (see below)."
    fi
}

install_pyz() {
    local PY
    PY="$(find_python)"
    say "Python found: $($PY --version)"
    say "Forging single-file gothica.pyz ..."
    local TMP
    TMP="$(mktemp -d)"
    cp -r "$DIR/gothica" "$TMP/gothica"
    printf 'import sys\nfrom gothica.cli import main\nsys.exit(main())\n' > "$TMP/__main__.py"
    mkdir -p "$BIN_DIR"
    "$PY" -m zipapp "$TMP" -o "$BIN_DIR/gothica" -p "/usr/bin/env $PY"
    chmod +x "$BIN_DIR/gothica"
    rm -rf "$TMP"
    say "Installed: $BIN_DIR/gothica (zipapp)"
}

# --- main rite ---
if [[ "$FROM_SOURCE" -eq 1 ]]; then
    install_from_source
elif [[ "$PYZ" -eq 1 ]]; then
    install_pyz
else
    if ! command -v curl >/dev/null 2>&1; then
        die "curl is required for binary install. Install curl or use --from-source."
    fi
    install_binary
fi

if [[ "$FIX_PATH" -eq 1 ]]; then
    fix_path_in_rc
fi

PATH_OK=0
if path_has_bin_dir; then
    PATH_OK=1
else
    warn_path_required
    export PATH="${BIN_DIR}:${PATH}"
    PATH_OK=1
    say "PATH adjusted for the remainder of this install script only."
fi

if [[ -x "${BIN_DIR}/gothica" ]]; then
    say "Verification:"
    "${BIN_DIR}/gothica" versio
elif command -v gothica >/dev/null 2>&1; then
    say "Verification:"
    gothica versio
else
    die "Install finished but gothica binary is missing at ${BIN_DIR}/gothica"
fi

if [[ "$FIX_PATH" -eq 0 ]] && ! path_line_in_rc "$(shell_rc_file)"; then
    warn "REMINDER: new terminals still need PATH (see ACTION REQUIRED above)."
    warn "Quick fix:  ./install.sh --fix-path && source $(shell_rc_file)"
fi

say "For fabricae you also need terraform (or use the Docker image)."
say "The Machine Spirit is appeased."
