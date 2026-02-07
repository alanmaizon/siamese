# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]
### Added
- Runtime config loading through `env-config.js` for container parity.
- Dockerfile, Nginx runtime entrypoint, and `docker-compose.yml`.
- CI workflow and Cloud Run deployment workflow.
- SDLC docs: contributing, security, templates, and wiki docs.
- Container automation script (`scripts/container.sh`) with npm wrappers.
- Repository sanitization script (`scripts/sanitize.sh`) and CI gate.
- Documentation index at `docs/README.md`.

### Changed
- Vite env handling moved to `import.meta.env` + runtime config fallback.
- Docker/local run docs now use the scripted container workflow.
