# Cloud Run Deployment

## Required secrets/variables
- `VITE_GEMINI_API_KEY`
- `GCP_PROJECT_ID`
- `GCP_REGION`
- `GCP_REPOSITORY`
- `CLOUD_RUN_SERVICE`

## GitHub Actions path
The workflow `.github/workflows/deploy-cloud-run.yml` builds, pushes, and deploys the container image on push to `main` or manual dispatch.

## Runtime parity
Cloud Run uses the same image as local Docker and injects runtime environment variables in the deploy step.
