# Security Policy

## Supported versions
This repository currently supports the `main` branch only.

## Reporting a vulnerability
Please open a private security advisory in GitHub if available, or contact the maintainer directly before public disclosure.

## Current security model
- Frontend-only app with runtime-injected Gemini key.
- No server-side storage of incident artifacts.
- Container image serves static assets with Nginx.

## Security hardening backlog
- Move model calls behind a backend proxy.
- Add user authentication and RBAC.
- Add request rate limiting and audit logs.
