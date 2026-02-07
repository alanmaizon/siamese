# Containerized Architecture

## Goal
Run the exact same artifact locally and on Google Cloud Run with runtime configuration only.

## Components
- React + Vite SPA for incident analysis UI.
- Gemini integration in browser (`@google/genai`).
- Nginx container serving static assets.
- Runtime env injector (`docker/nginx/entrypoint.sh`) that writes `/env-config.js`.

## Request flow
1. User opens app.
2. Browser loads `env-config.js`.
3. App resolves Gemini key from runtime config (`window.__SIAMESE_CONFIG__`) or Vite env fallback.
4. Uploaded artifacts are parsed in browser memory.
5. Prompt is sent directly to Gemini API.

## Local to Cloud Run parity
- Container listens on `8080` in both environments.
- Runtime env key (`VITE_GEMINI_API_KEY`) is injected at startup, so no image rebuild is required.
- SPA fallback routing handled by Nginx (`try_files $uri /index.html`).

## Tradeoffs
- Current model call path is client-side for hackathon speed.
- For production, move Gemini calls to a backend proxy to avoid exposing API keys client-side.
