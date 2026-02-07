# Siamese - Incident Analysis Workspace

Siamese is a containerized incident-analysis app that turns uploaded logs into a structured incident report using Gemini.

## Live links
- [Demo Google Cloud Run](https://siamese-911931794549.us-west1.run.app/)
- [Demo Google AI Studio](https://aistudio.google.com/apps/drive/1Xa8N0nooOlibltLEKU0b3jSQHqGHxG_2)

## Screenshots
![Siamese screenshot at 2026-02-06 16:43:19](img/Screenshot%202026-02-06%20at%2016.43.19.png)
![Siamese screenshot at 2026-02-06 19:29:02](img/Screenshot%202026-02-06%20at%2019.29.02.png)
![Siamese screenshot at 2026-02-06 19:31:37](img/Screenshot%202026-02-06%20at%2019.31.37.png)

## Hackathon focus
- Browser-first UX for rapid incident triage.
- Structured JSON outputs: summary, timeline, root causes, evidence, mitigations, follow-ups, confidence.
- Containerized architecture that runs locally and mirrors Cloud Run deployment behavior.

## Stack
- React 19 + TypeScript + Vite
- Google GenAI SDK (`@google/genai`)
- Nginx runtime container
- GitHub Actions for CI/CD

## Runtime configuration
The app reads API key values in this order:
1. `window.__SIAMESE_CONFIG__.geminiApiKey` from `env-config.js` (runtime-injected in container)
2. `VITE_GEMINI_API_KEY`
3. `VITE_API_KEY`

## Quick start (local)
### Option A: Node
1. `npm install`
2. `cp .env.example .env.local`
3. Set `VITE_GEMINI_API_KEY`
4. `npm run dev`

### Option B: Docker
1. `cp .env.example .env`
2. Set `VITE_GEMINI_API_KEY`
3. `npm run container:up`
4. Open `http://localhost:8080`
5. Use `npm run container:logs` to inspect startup logs

Container helper commands:
- `npm run container:status` to check running services
- `npm run container:restart` to rebuild and restart
- `npm run container:down` to stop and remove containers
- `npm run container:help` to print all supported container commands

## Repository hygiene
- Run `npm run sanitize` before opening a PR.
- The sanitize script verifies `.env` is not tracked and checks tracked files for obvious key material.
- Full docs index: `docs/README.md`

## Testing
- Run all automated tests: `npm test`
- Watch mode while developing: `npm run test:watch`
- Run browser smoke tests: `npm run test:e2e`
- Current suite covers:
  - API key resolution precedence in `config.ts`
  - Gemini service request/response handling in `services/geminiService.ts`
  - App flow checks in `App.tsx` (validation, successful analysis rendering, service error handling)
  - End-to-end smoke flow (landing -> workspace -> validation error path) in `e2e/smoke.spec.ts`

## CI/CD
- CI workflow: `.github/workflows/ci.yml`
  - `npm test`
  - `npm run test:e2e`
  - `npm run typecheck`
  - `npm run build`
  - `docker build`
- CD workflow: `.github/workflows/deploy-cloud-run.yml`
  - Optional Cloud Run deploy path through GitHub Actions
  - Auto-skips if required GCP/GitHub secrets are not configured
  - Manual/external deployment (for example AI Studio) remains supported

## Containerized architecture
- Multi-stage Docker build (`node:20-alpine` -> `nginx:alpine`)
- Nginx serves SPA and injects runtime config via `docker/nginx/entrypoint.sh`
- Same image behavior locally and on Cloud Run (`PORT 8080`)

Detailed design: `docs/architecture.md`

## SDLC and governance
- Contributing: `CONTRIBUTING.md`
- Security policy: `SECURITY.md`
- Code of conduct: `CODE_OF_CONDUCT.md`
- Changelog: `CHANGELOG.md`
- Issue templates and PR template in `.github/`

## Wiki section (in-repo)
- `docs/wiki/Home.md`
- `docs/wiki/Architecture.md`
- `docs/wiki/Local-Development.md`
- `docs/wiki/Cloud-Run-Deployment.md`
- `docs/wiki/SDLC.md`
- `docs/wiki/Roadmap.md`

## Future implementation issues
Planned backlog: `docs/roadmap-issues.md`
