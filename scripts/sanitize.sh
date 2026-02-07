#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

info() {
  printf '[info] %s\n' "$*"
}

error() {
  printf '[error] %s\n' "$*" >&2
}

if ! command -v git >/dev/null 2>&1; then
  error "git is required to run repository sanitization checks."
  exit 1
fi

if git ls-files --error-unmatch .env >/dev/null 2>&1; then
  error ".env is tracked by git. Remove it from tracking with: git rm --cached .env"
  exit 1
fi

tracked_files=()
while IFS= read -r file; do
  tracked_files+=("${file}")
done < <(git ls-files)
if [[ ${#tracked_files[@]} -eq 0 ]]; then
  info "No tracked files found. Nothing to scan."
  exit 0
fi

scan_pattern() {
  local pattern="$1"
  local label="$2"
  local matches=""

  if command -v rg >/dev/null 2>&1; then
    matches="$(rg -n --no-heading -e "${pattern}" "${tracked_files[@]}" || true)"
  else
    matches="$(grep -nE "${pattern}" "${tracked_files[@]}" 2>/dev/null || true)"
  fi

  if [[ -n "${matches}" ]]; then
    error "Potential ${label} detected:"
    printf '%s\n' "${matches}" >&2
    return 1
  fi

  return 0
}

failed=0

scan_pattern 'AIza[0-9A-Za-z_-]{35}' 'Google API key material' || failed=1
scan_pattern '-----BEGIN (RSA|EC|OPENSSH|DSA|PRIVATE) KEY-----' 'private key material' || failed=1

if [[ "${failed}" -ne 0 ]]; then
  error "Sanitization checks failed."
  exit 1
fi

info "Sanitization checks passed."
