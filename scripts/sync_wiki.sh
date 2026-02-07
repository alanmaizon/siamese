#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WIKI_SOURCE_DIR="${ROOT_DIR}/docs/wiki"

info() {
  printf '[info] %s\n' "$*"
}

error() {
  printf '[error] %s\n' "$*" >&2
}

if ! command -v git >/dev/null 2>&1; then
  error "git is required."
  exit 1
fi

if [[ ! -d "${WIKI_SOURCE_DIR}" ]]; then
  error "Wiki source folder not found: ${WIKI_SOURCE_DIR}"
  exit 1
fi

origin_url="$(git -C "${ROOT_DIR}" config --get remote.origin.url || true)"
if [[ -z "${origin_url}" ]]; then
  error "Unable to read remote.origin.url."
  exit 1
fi

repo_path=""
if [[ "${origin_url}" =~ ^https://github\.com/([^/]+/[^/.]+)(\.git)?$ ]]; then
  repo_path="${BASH_REMATCH[1]}"
elif [[ "${origin_url}" =~ ^git@github\.com:([^/]+/[^/.]+)(\.git)?$ ]]; then
  repo_path="${BASH_REMATCH[1]}"
else
  error "Unsupported GitHub remote format: ${origin_url}"
  exit 1
fi

wiki_remote="https://github.com/${repo_path}.wiki.git"
tmp_dir="$(mktemp -d /tmp/wiki-sync-XXXXXX)"
trap 'rm -rf "${tmp_dir}"' EXIT

info "Cloning wiki repository..."
if ! git clone --depth 1 "${wiki_remote}" "${tmp_dir}" >/dev/null 2>&1; then
  info "Wiki repository not initialized; creating a fresh wiki repo clone."
  git -C "${tmp_dir}" init >/dev/null
  git -C "${tmp_dir}" remote add origin "${wiki_remote}"
fi

find "${tmp_dir}" -mindepth 1 -maxdepth 1 ! -name '.git' -exec rm -rf {} +
cp "${WIKI_SOURCE_DIR}"/*.md "${tmp_dir}/"

cat > "${tmp_dir}/_Footer.md" <<'EOF'
[Home](Home) | [Architecture](Architecture) | [Local Development](Local-Development) | [Cloud Run Deployment](Cloud-Run-Deployment) | [SDLC](SDLC) | [Roadmap](Roadmap)
EOF

if git -C "${tmp_dir}" diff --quiet && git -C "${tmp_dir}" diff --cached --quiet; then
  info "No wiki changes detected."
  exit 0
fi

git -C "${tmp_dir}" add -A
if git -C "${tmp_dir}" diff --cached --quiet; then
  info "No wiki changes to commit."
  exit 0
fi

git -C "${tmp_dir}" commit -m "docs: sync wiki content from docs/wiki" >/dev/null
info "Pushing wiki updates..."
git -C "${tmp_dir}" push origin HEAD:master

info "Wiki updated: https://github.com/${repo_path}/wiki"
