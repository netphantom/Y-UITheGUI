#!/bin/sh
# Y-UI one-click installer / updater.
#
#   curl -fsSL https://raw.githubusercontent.com/netphantom/Y-UITheGUI/main/install.sh | sh
#
# Downloads the compose files into $YUI_DIR (default ~/y-ui), creates .env on first run
# (GPU auto-detected; an existing .env is never overwritten), then pulls and starts Y-UI.
# Run it again at any time to update to the latest images.
set -eu

REPO_RAW="${YUI_REPO_RAW:-https://raw.githubusercontent.com/netphantom/Y-UITheGUI/main}"
DIR="${YUI_DIR:-$HOME/y-ui}"
FILES="docker-compose.yml docker-compose.gpu.yml .env.example"

say() { printf '\033[1;35m▸\033[0m %s\n' "$*"; }
fail() { printf '\033[1;31m✗\033[0m %s\n' "$*" >&2; exit 1; }

# Set KEY=VALUE in .env, replacing an existing (possibly commented-out) line.
set_env() {
    if grep -qE "^#?[[:space:]]*$1=" .env; then
        sed -i.bak -E "s|^#?[[:space:]]*$1=.*|$1=$2|" .env && rm -f .env.bak
    else
        echo "$1=$2" >> .env
    fi
}

case "$(uname -s)" in
    MINGW* | MSYS* | CYGWIN*)
        fail "On Windows use PowerShell: irm https://raw.githubusercontent.com/netphantom/Y-UITheGUI/main/install.ps1 | iex" ;;
esac
command -v docker >/dev/null 2>&1 || fail "Docker is required: https://docs.docker.com/engine/install/"
docker compose version >/dev/null 2>&1 || fail "Docker Compose v2 is required (the 'docker compose' plugin)."

say "Installing into $DIR"
mkdir -p "$DIR"
cd "$DIR"
for file in $FILES; do
    curl -fsSL "$REPO_RAW/$file" -o "$file" || fail "Could not download $file"
done

if [ -f .env ]; then
    say "Keeping your existing .env"
else
    cp .env.example .env
    if command -v nvidia-smi >/dev/null 2>&1 && nvidia-smi >/dev/null 2>&1; then
        say "NVIDIA GPU found: using the YuE2 engine"
        # Native Linux only: WSL2 exposes the GPU through /dev/dxg instead.
        if [ -e /dev/nvidia-uvm ]; then
            set_env NVIDIA_UVM_MAJOR "$(( 0x$(stat -c '%t' /dev/nvidia-uvm) ))"
        fi
    else
        say "No NVIDIA GPU found: using the mock engine (UI demo, no real music)"
        set_env COMPOSE_FILE docker-compose.yml
        set_env YUI_ENGINE mock
    fi
fi

say "Pulling images"
docker compose pull
say "Starting Y-UI"
docker compose up -d

PORT="$(grep -E '^YUI_PORT=' .env | cut -d= -f2)"
say "Done! Open http://localhost:${PORT:-8080} and create the first (admin) account."
say "The first YuE2 start downloads the engine and model weights (~15 GB): follow it with"
printf '    cd %s && docker compose logs -f backend\n' "$DIR"
