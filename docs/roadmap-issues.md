# Future Implementation Issues

GitHub tracker:
- https://github.com/alanmaizon/siamese/issues/1
- https://github.com/alanmaizon/siamese/issues/2
- https://github.com/alanmaizon/siamese/issues/3
- https://github.com/alanmaizon/siamese/issues/4
- https://github.com/alanmaizon/siamese/issues/5
- https://github.com/alanmaizon/siamese/issues/6

These sections define the scope and acceptance criteria.

## 1) Backend Gemini proxy with token broker
- Problem: API key is visible to client.
- Outcome: Frontend calls backend endpoint, backend holds Gemini credential.
- Acceptance:
  - `/api/analyze` endpoint replaces direct client call.
  - No Gemini key in browser network payloads.

## 2) Authentication and RBAC
- Problem: no user identity or project isolation.
- Outcome: login + role-based access to incidents.
- Acceptance:
  - Protected routes.
  - Role checks for incident actions.

## 3) Incident persistence
- Problem: analysis results are transient.
- Outcome: incident records stored and searchable.
- Acceptance:
  - CRUD for incidents.
  - Timeline and report history retained.

## 4) Integrations for ingestion
- Problem: requires manual upload.
- Outcome: pull data from cloud/logging and incident tools.
- Acceptance:
  - At least one cloud log source.
  - At least one ticketing/alerting connector.

## 5) Evaluation harness
- Problem: no quality regression guard.
- Outcome: benchmark set and scoring for RCA quality.
- Acceptance:
  - Baseline incident corpus.
  - CI job with pass/fail quality threshold.

## 6) Security hardening
- Problem: minimal controls for enterprise usage.
- Outcome: auditability and abuse controls.
- Acceptance:
  - Structured audit logs.
  - Rate limits for analysis requests.
