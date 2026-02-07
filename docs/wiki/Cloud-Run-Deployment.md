# Cloud Run Deployment

## Required secrets/variables
- `GCP_WORKLOAD_IDENTITY_PROVIDER`
- `GCP_SERVICE_ACCOUNT`
- `VITE_GEMINI_API_KEY`
- `GCP_PROJECT_ID`
- `GCP_REGION`
- `GCP_REPOSITORY`
- `CLOUD_RUN_SERVICE`

## GitHub Actions path
The workflow `.github/workflows/deploy-cloud-run.yml` builds, pushes, and deploys the container image when required secrets are present.
If secrets are not configured, the workflow skips deployment instead of failing auth.
This supports setups where deployment is handled outside GitHub Actions (for example AI Studio).

## Runtime parity
Cloud Run uses the same image as local Docker and injects runtime environment variables in the deploy step.
