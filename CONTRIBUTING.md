# Contributing

## Development setup
1. Install Node.js 20+.
2. Install dependencies: `npm install`
3. Create env file: `cp .env.example .env.local`
4. Start dev server: `npm run dev`

## Quality gates
- `npm run typecheck`
- `npm run build`
- `docker build -t siamese:local .`

## Pull request rules
- Keep PRs scoped to one concern.
- Update docs when behavior or architecture changes.
- Add or update issue references in PR description.
- Ensure CI is green before merge.

## Branching
- `main` stays deployable.
- Use short-lived feature branches: `feat/<topic>` or `fix/<topic>`.
