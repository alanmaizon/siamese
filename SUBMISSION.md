# Siamese - Gemini 3 Hackathon Submission

## Project
- Name: Siamese
- Category: AI-assisted incident analysis / SRE tooling
- Demo: https://siamese-911931794549.us-west1.run.app/
- Repository: https://github.com/alanmaizon/siamese

## What problem it solves
Incident triage is often slow because responders must manually parse large log sets, reconstruct timelines, and produce reports under pressure. Siamese reduces that overhead by converting uploaded artifacts into a structured incident report with evidence-backed root-cause analysis.

## Solution
Siamese is a browser-first incident analysis workspace powered by Gemini. Users upload artifacts, ask an incident question, and receive a structured output:
- `summary`
- `timeline`
- `root_causes`
- `evidence`
- `mitigations`
- `follow_ups`
- `confidence`

## How Gemini is used
- Model access is implemented with `@google/genai`.
- Prompts combine user question + uploaded artifact context.
- Responses are constrained with a JSON schema for deterministic structure.
- The system instruction enforces evidence-grounded reasoning and explicit confidence scoring.

## Architecture
- Frontend: React 19 + TypeScript + Vite
- Runtime: Nginx container serving static SPA
- Config strategy: runtime env injection via `env-config.js` for local/Docker/Cloud Run parity
- Deployment: Google Cloud Run
- CI/CD: GitHub Actions (typecheck, build, docker build, Cloud Run deploy workflow)

Detailed architecture docs:
- `docs/architecture.md`
- `docs/wiki/Architecture.md`

## SDLC quality and repository completeness
This repository includes:
- Contribution policy: `CONTRIBUTING.md`
- Security policy: `SECURITY.md`
- Code of conduct: `CODE_OF_CONDUCT.md`
- Changelog: `CHANGELOG.md`
- Issue templates + PR template in `.github/`
- CI workflow: `.github/workflows/ci.yml`
- CD workflow: `.github/workflows/deploy-cloud-run.yml` (optional; skips when deploy secrets are not configured)
- In-repo wiki docs under `docs/wiki/`

## Local run instructions
### Node
1. `npm install`
2. `cp .env.example .env.local`
3. Set `VITE_GEMINI_API_KEY`
4. `npm run dev`

### Docker
1. `cp .env.example .env`
2. Set `VITE_GEMINI_API_KEY`
3. `npm run container:up`
4. Open `http://localhost:8080`
5. `npm run container:logs` for runtime troubleshooting

## Sanitization and organization
- Repository hygiene checks: `npm run sanitize`
- Container automation script: `scripts/container.sh`
- Documentation index: `docs/README.md`

## Roadmap and future implementation
Planned issues are already tracked in GitHub:
- https://github.com/alanmaizon/siamese/issues/1
- https://github.com/alanmaizon/siamese/issues/2
- https://github.com/alanmaizon/siamese/issues/3
- https://github.com/alanmaizon/siamese/issues/4
- https://github.com/alanmaizon/siamese/issues/5
- https://github.com/alanmaizon/siamese/issues/6

Scope details are documented in:
- `docs/roadmap-issues.md`
- `docs/wiki/Roadmap.md`

## Why this is hackathon-ready
- Live deployed demo
- Containerized, portable architecture
- Clear documentation and reproducible setup
- CI/CD workflows defined
- Structured forward roadmap with tracked issues
