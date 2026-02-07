#!/bin/sh
set -eu

cat > /usr/share/nginx/html/env-config.js <<EOC
window.__SIAMESE_CONFIG__ = {
  geminiApiKey: "${VITE_GEMINI_API_KEY:-${VITE_API_KEY:-}}",
};
EOC

exec "$@"
