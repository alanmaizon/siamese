# SDLC

## Governance artifacts in this repo
- `CONTRIBUTING.md`
- `CODE_OF_CONDUCT.md`
- `SECURITY.md`
- `.github/ISSUE_TEMPLATE/*`
- `.github/PULL_REQUEST_TEMPLATE.md`
- `CHANGELOG.md`

## CI gates
- Repository sanitize check (`npm run sanitize`)
- TypeScript typecheck
- Production build
- Docker image build

## Release posture
Main branch is treated as releasable, with Cloud Run deployment automated via GitHub Actions.
