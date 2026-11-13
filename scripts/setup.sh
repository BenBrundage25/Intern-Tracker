#!/usr/bin/env bash
# One-shot dev environment setup. Safe to re-run: every step checks before acting.
#
#   ./scripts/setup.sh                 # everything
#   SKIP_OLLAMA=1 ./scripts/setup.sh   # skip the Ollama install and model pull
#   OLLAMA_MODEL=qwen2.5:7b ./scripts/setup.sh
#
# Docker Desktop is the one thing this can't install (it's a Windows app). Install it,
# then enable Settings -> Resources -> WSL Integration -> Ubuntu.
set -euo pipefail

cd "$(dirname "$0")/.."

NODE_MAJOR=22
OLLAMA_MODEL="${OLLAMA_MODEL:-llama3.2:3b}"

ok()   { printf '\033[32m✓\033[0m %s\n' "$*"; }
warn() { printf '\033[33m!\033[0m %s\n' "$*"; }
step() { printf '\n\033[1m== %s\033[0m\n' "$*"; }
have() { command -v "$1" >/dev/null 2>&1; }

step "uv"
if ! have uv; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
fi
ok "uv $(uv --version | cut -d' ' -f2)"

step "Python dependencies"
uv sync
ok "installed from uv.lock"

step "Node.js $NODE_MAJOR"
export NVM_DIR="${NVM_DIR:-$HOME/.nvm}"
if [ ! -s "$NVM_DIR/nvm.sh" ]; then
  curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
fi
# shellcheck disable=SC1091
. "$NVM_DIR/nvm.sh"
if [ "$(node -p 'process.versions.node.split(".")[0]' 2>/dev/null || echo 0)" -lt "$NODE_MAJOR" ]; then
  nvm install "$NODE_MAJOR"
  nvm alias default "$NODE_MAJOR"
fi
ok "node $(node --version)"

step "Ollama"
if [ -n "${SKIP_OLLAMA:-}" ]; then
  warn "skipped (SKIP_OLLAMA set)"
else
  if ! have ollama; then
    curl -fsSL https://ollama.com/install.sh | sh   # asks for your sudo password
  fi
  if ! ollama list >/dev/null 2>&1; then
    # No systemd service running; start a server just for the pull.
    nohup ollama serve >/tmp/ollama-setup.log 2>&1 &
    for _ in $(seq 1 20); do ollama list >/dev/null 2>&1 && break; sleep 0.5; done
  fi
  if ollama list | awk 'NR>1 {print $1}' | grep -qx "$OLLAMA_MODEL"; then
    ok "model $OLLAMA_MODEL already pulled"
  else
    ollama pull "$OLLAMA_MODEL"
    ok "pulled $OLLAMA_MODEL"
  fi
fi

step ".env"
if [ -f .env ]; then
  ok ".env exists (left untouched)"
else
  cp .env.example .env
  ok "created .env from .env.example"
fi

step "Postgres"
if have docker && docker info >/dev/null 2>&1; then
  docker compose up -d --wait postgres
  uv run alembic -c backend/alembic.ini upgrade head
  ok "database running and migrated"
else
  warn "Docker not available. Install Docker Desktop, enable WSL integration, re-run."
fi

step "Dataset"
if [ -f data/raw/postings.csv ]; then
  ok "data/raw/postings.csv found. Next: make load"
else
  mkdir -p data/raw
  warn "Download postings.csv from kaggle.com/datasets/arshkon/linkedin-job-postings into data/raw/"
fi
