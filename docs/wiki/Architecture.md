# Architecture

Siamese ships as a containerized SPA.

- Build stage: Vite compiles static assets.
- Runtime stage: Nginx serves assets and injects runtime config via `env-config.js`.
- App stage: React app reads runtime API key and performs in-browser artifact processing + Gemini analysis.

See `docs/architecture.md` for details.
