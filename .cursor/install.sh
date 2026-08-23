#!/usr/bin/env bash
# Idempotent Cloud Agent bootstrap for spectre007-agents.
#
# The repository is currently a greenfield project, so this script installs
# dependencies only when a recognized manifest is present. It is safe to run
# repeatedly and on an empty checkout (each ecosystem is guarded by a file
# existence check), and it grows with the project as manifests are added.

set -euo pipefail

log() { printf '\n[install] %s\n' "$*"; }

# --- Node.js -----------------------------------------------------------------
if [ -f package.json ]; then
  if [ -f pnpm-lock.yaml ]; then
    log "pnpm install --frozen-lockfile"
    corepack enable >/dev/null 2>&1 || true
    pnpm install --frozen-lockfile
  elif [ -f yarn.lock ]; then
    log "yarn install --frozen-lockfile"
    corepack enable >/dev/null 2>&1 || true
    yarn install --frozen-lockfile
  elif [ -f package-lock.json ]; then
    log "npm ci"
    npm ci
  else
    log "npm install (no lockfile present)"
    npm install
  fi
fi

# --- Python ------------------------------------------------------------------
if [ -f uv.lock ] || { [ -f pyproject.toml ] && command -v uv >/dev/null 2>&1; }; then
  log "uv sync"
  uv sync
elif [ -f poetry.lock ] || { [ -f pyproject.toml ] && command -v poetry >/dev/null 2>&1; }; then
  log "poetry install"
  poetry install
elif [ -f requirements.txt ]; then
  log "pip install -r requirements.txt"
  python3 -m pip install --user -r requirements.txt
fi

# --- Rust --------------------------------------------------------------------
if [ -f Cargo.toml ]; then
  log "cargo fetch"
  cargo fetch
fi

# --- Go ----------------------------------------------------------------------
if [ -f go.mod ]; then
  log "go mod download"
  go mod download
fi

log "bootstrap complete"
