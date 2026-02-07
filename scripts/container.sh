#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="${ROOT_DIR}/docker-compose.yml"
ENV_FILE="${ROOT_DIR}/.env"
ENV_EXAMPLE_FILE="${ROOT_DIR}/.env.example"
PROJECT_NAME="siamese"

COMPOSE_CMD=()

usage() {
  cat <<'EOF'
Usage: scripts/container.sh <command> [docker compose args]

Commands:
  up       Build and start the app container in detached mode (default)
  down     Stop and remove the app container
  restart  Rebuild and restart the app container
  build    Build the app container image
  logs     Stream container logs
  status   Show container status
  help     Show this help message
EOF
}

info() {
  printf '[info] %s\n' "$*"
}

error() {
  printf '[error] %s\n' "$*" >&2
}

detect_compose_command() {
  if ! command -v docker >/dev/null 2>&1; then
    error "Docker is not installed or not on PATH."
    exit 1
  fi

  if docker compose version >/dev/null 2>&1; then
    COMPOSE_CMD=("docker" "compose")
    return
  fi

  if command -v docker-compose >/dev/null 2>&1; then
    COMPOSE_CMD=("docker-compose")
    return
  fi

  error "Neither 'docker compose' nor 'docker-compose' is available."
  exit 1
}

ensure_docker_daemon_running() {
  if ! docker info >/dev/null 2>&1; then
    error "Docker daemon is not running. Start Docker Desktop (or dockerd) and try again."
    exit 1
  fi
}

compose() {
  "${COMPOSE_CMD[@]}" --project-name "${PROJECT_NAME}" -f "${COMPOSE_FILE}" "$@"
}

get_env_value() {
  local key="$1"
  local raw=""

  if [[ -f "${ENV_FILE}" ]]; then
    raw="$(grep -E "^${key}=" "${ENV_FILE}" | tail -n 1 | cut -d= -f2- || true)"
  fi

  raw="${raw#\"}"
  raw="${raw%\"}"
  raw="${raw#\'}"
  raw="${raw%\'}"
  printf '%s' "${raw}"
}

ensure_env_file_exists() {
  if [[ -f "${ENV_FILE}" ]]; then
    return
  fi

  if [[ ! -f "${ENV_EXAMPLE_FILE}" ]]; then
    error "Missing ${ENV_FILE} and ${ENV_EXAMPLE_FILE}. Cannot continue."
    exit 1
  fi

  cp "${ENV_EXAMPLE_FILE}" "${ENV_FILE}"
  error "Created ${ENV_FILE} from ${ENV_EXAMPLE_FILE}. Add your Gemini API key and rerun."
  exit 1
}

ensure_api_key_present() {
  local gemini_key=""
  local fallback_key=""

  gemini_key="$(get_env_value "VITE_GEMINI_API_KEY")"
  fallback_key="$(get_env_value "VITE_API_KEY")"

  if [[ -n "${gemini_key}" && "${gemini_key}" != "your_gemini_api_key_here" ]]; then
    return
  fi

  if [[ -n "${fallback_key}" && "${fallback_key}" != "your_gemini_api_key_here" ]]; then
    return
  fi

  error "No Gemini API key found in ${ENV_FILE}."
  error "Set VITE_GEMINI_API_KEY (preferred) or VITE_API_KEY, then rerun."
  exit 1
}

action="${1:-up}"
if [[ $# -gt 0 ]]; then
  shift
fi

if [[ "${action}" == "help" || "${action}" == "-h" || "${action}" == "--help" ]]; then
  usage
  exit 0
fi

detect_compose_command
ensure_docker_daemon_running

case "${action}" in
  up)
    ensure_env_file_exists
    ensure_api_key_present
    info "Building and starting the container..."
    compose up --build -d "$@"
    info "App available at http://localhost:8080"
    compose ps
    ;;
  down)
    info "Stopping the container..."
    compose down "$@"
    ;;
  restart)
    ensure_env_file_exists
    ensure_api_key_present
    info "Restarting the container..."
    compose down
    compose up --build -d "$@"
    info "App available at http://localhost:8080"
    compose ps
    ;;
  build)
    info "Building the container image..."
    compose build "$@"
    ;;
  logs)
    if [[ $# -eq 0 ]]; then
      compose logs -f --tail=200 siamese
    else
      compose logs "$@"
    fi
    ;;
  status)
    compose ps
    ;;
  *)
    error "Unknown command: ${action}"
    usage
    exit 1
    ;;
esac
