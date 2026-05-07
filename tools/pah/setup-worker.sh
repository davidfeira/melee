#!/usr/bin/env bash
# tools/pah/setup-worker.sh — one-command p@h worker bootstrap for Linux/macOS.
#
# From a fresh machine (note: CONTROLLER_URL is on the BASH side of the pipe,
# not curl, so the env var actually reaches the script):
#   curl -fsSL http://<controller-ip>:7777/kit/setup-worker.sh \
#     | CONTROLLER_URL=http://<controller-ip>:7777 bash
#
# Or from a checkout:
#   CONTROLLER_URL=http://192.168.1.50:8080 ./tools/pah/setup-worker.sh
#
# Env vars:
#   CONTROLLER_URL      Required. http://<controller-ip>:<port>
#   REPO_URL            git URL to clone (default: davidfeira/melee fork)
#   BRANCH              git branch to check out (default: master)
#   INSTALL_DIR         where to clone (default: $HOME/melee-pah-worker)
#   CORES               worker core count (default: nproc - 1, min 1)
#   MEMORY_GB           worker memory (default: 75% of total RAM)
#   PRIV_SEED           controller-issued seed (fetched from CONTROLLER_URL/kit if unset)
#
# What this script does:
#   1. Install missing prereqs (python3, git) via apt/brew (no-op if present)
#   2. Clone or update the repo into INSTALL_DIR
#   3. Create a venv under vendor/decomp-permuter/.venv-linux
#   4. Pip-install the permuter dependencies
#   5. Fetch the worker pah.conf from $CONTROLLER_URL/kit/pah.conf
#   6. Start pah.py run-server in the foreground (so the user sees logs)
#
# Idempotent: re-running on the same box updates the checkout and restarts the
# worker. Safe to interrupt — no daemon installed; ctrl-c kills the worker.

set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/davidfeira/melee.git}"
BRANCH="${BRANCH:-master}"
INSTALL_DIR="${INSTALL_DIR:-$HOME/melee-pah-worker}"
CORES="${CORES:-}"
MEMORY_GB="${MEMORY_GB:-}"

if [[ -z "${CONTROLLER_URL:-}" ]]; then
  echo "CONTROLLER_URL is required." >&2
  echo "" >&2
  echo "If you piped curl into bash, put the env var on bash:" >&2
  echo "  curl -fsSL <url>/kit/setup-worker.sh | CONTROLLER_URL=<url> bash" >&2
  echo "" >&2
  echo "Or if running directly:" >&2
  echo "  CONTROLLER_URL=<url> $0" >&2
  exit 2
fi

# strip trailing slash
CONTROLLER_URL="${CONTROLLER_URL%/}"

OS="$(uname -s)"
case "$OS" in
  Linux)
    PKG_MGR=""
    for cand in apt-get dnf pacman; do
      if command -v "$cand" >/dev/null 2>&1; then
        PKG_MGR="$cand"
        break
      fi
    done
    ;;
  Darwin)
    PKG_MGR="brew"
    ;;
  *)
    echo "Unsupported OS: $OS (need Linux or macOS)" >&2
    exit 3
    ;;
esac

ensure_pkg() {
  local pkg="$1"
  if command -v "$pkg" >/dev/null 2>&1; then
    return 0
  fi
  echo "Missing $pkg; trying $PKG_MGR install..."
  case "$PKG_MGR" in
    apt-get)  sudo apt-get update -qq && sudo apt-get install -y "$pkg" ;;
    dnf)      sudo dnf install -y "$pkg" ;;
    pacman)   sudo pacman -S --noconfirm "$pkg" ;;
    brew)     brew install "$pkg" ;;
    *)        echo "no package manager detected; install $pkg manually" >&2; exit 4 ;;
  esac
}

ensure_pkg git
ensure_pkg python3
# python3-venv is a separate apt package on Debian/Ubuntu.
if [[ "$PKG_MGR" == "apt-get" ]]; then
  if ! python3 -c 'import venv' 2>/dev/null; then
    sudo apt-get install -y python3-venv
  fi
fi

# Docker — pah.py run-server uses it to sandbox each permuter invocation.
# On macOS we need Docker Desktop (GUI install); on Linux we install the
# `docker.io` / `docker` apt package and add the user to the docker group.
if ! command -v docker >/dev/null 2>&1; then
  case "$OS" in
    Darwin)
      echo "Docker not found. Install Docker Desktop from docker.com first," >&2
      echo "then re-run this bootstrap. (Homebrew: brew install --cask docker)" >&2
      exit 5
      ;;
    Linux)
      case "$PKG_MGR" in
        apt-get)  sudo apt-get install -y docker.io docker-compose-plugin || sudo apt-get install -y docker.io ;;
        dnf)      sudo dnf install -y docker docker-compose ;;
        pacman)   sudo pacman -S --noconfirm docker ;;
      esac
      sudo systemctl enable --now docker 2>/dev/null || true
      sudo usermod -aG docker "$USER" 2>/dev/null || true
      if ! docker info >/dev/null 2>&1; then
        echo "Docker installed but the current shell can't talk to it. Log out and log" >&2
        echo "back in (or run \`newgrp docker\`), then re-run this bootstrap." >&2
        exit 6
      fi
      ;;
  esac
fi
if ! docker info >/dev/null 2>&1; then
  echo "Docker is installed but not running. Start it (Docker Desktop on macOS," >&2
  echo "\`sudo systemctl start docker\` on Linux), then re-run." >&2
  exit 7
fi

# Resolve cores/memory if not set.
if [[ -z "$CORES" ]]; then
  total_cores=$(nproc 2>/dev/null || sysctl -n hw.ncpu)
  CORES=$((total_cores > 1 ? total_cores - 1 : 1))
fi
if [[ -z "$MEMORY_GB" ]]; then
  case "$OS" in
    Linux)
      total_kb=$(awk '/MemTotal/ {print $2}' /proc/meminfo)
      MEMORY_GB=$((total_kb * 75 / 100 / 1024 / 1024))
      ;;
    Darwin)
      total_bytes=$(sysctl -n hw.memsize)
      MEMORY_GB=$((total_bytes * 75 / 100 / 1024 / 1024 / 1024))
      ;;
  esac
  [[ "$MEMORY_GB" -lt 1 ]] && MEMORY_GB=1
fi

echo "==> worker config: $CORES cores, ${MEMORY_GB}GB memory"
echo "==> controller:    $CONTROLLER_URL"
echo "==> install dir:   $INSTALL_DIR"

# Clone or update repo.
if [[ -d "$INSTALL_DIR/.git" ]]; then
  echo "==> updating existing checkout"
  git -C "$INSTALL_DIR" fetch origin --quiet
  git -C "$INSTALL_DIR" checkout "$BRANCH" --quiet
  git -C "$INSTALL_DIR" pull --ff-only --quiet
else
  echo "==> cloning $REPO_URL ($BRANCH)"
  git clone --branch "$BRANCH" --depth 1 "$REPO_URL" "$INSTALL_DIR"
fi

cd "$INSTALL_DIR"

# Permuter venv.
PERM_DIR="$INSTALL_DIR/vendor/decomp-permuter"
VENV_DIR="$PERM_DIR/.venv-linux"
if [[ ! -d "$PERM_DIR" ]]; then
  echo "vendor/decomp-permuter missing — branch may be wrong, or vendor not committed" >&2
  exit 5
fi
if [[ ! -d "$VENV_DIR" ]]; then
  echo "==> creating permuter venv"
  python3 -m venv "$VENV_DIR"
fi
"$VENV_DIR/bin/pip" install --quiet --upgrade pip
"$VENV_DIR/bin/pip" install --quiet -r "$PERM_DIR/requirements.txt" 2>/dev/null \
  || "$VENV_DIR/bin/pip" install --quiet pynacl pycparser levenshtein rapidfuzz toml attrs requests

# Fetch worker config from controller (priv_seed + docker_image fields are
# enough for run-server; controller endpoint comes from the URL itself).
PAH_CONF="$INSTALL_DIR/pah.conf"
echo "==> fetching $CONTROLLER_URL/kit/pah.conf"
if ! curl -fsSL "$CONTROLLER_URL/kit/pah.conf" -o "$PAH_CONF"; then
  echo "Could not fetch pah.conf from controller. Is the controller running and reachable?" >&2
  echo "Run on the main machine:  python tools/pah/start-controller.ps1" >&2
  echo "Then verify:              curl $CONTROLLER_URL/kit/pah.conf" >&2
  exit 6
fi

# Start the worker in the foreground so the user sees activity / can ctrl-c.
echo "==> starting worker — ctrl-c to stop"
echo
exec "$VENV_DIR/bin/python" "$PERM_DIR/pah.py" run-server \
  --cores "$CORES" --memory "$MEMORY_GB"
