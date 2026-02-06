<div align="center">
<img width="1200" height="475" alt="GHBanner" src="https://github.com/user-attachments/assets/0aa67016-6eaf-458a-adb2-6e31a0763ed6" />
</div>

# Siamese - Incident Analysis Workspace

Siamese is a secure, frontend-only incident analysis tool powered by Google's Gemini models. It allows Site Reliability Engineers (SREs) to upload log artifacts locally in the browser and generate structured, AI-driven root cause analysis reports.

## Architecture

*   **Frontend**: React 19 (Client-side SPA)
*   **Build System**: Vite
*   **Styling**: Tailwind CSS & Lucide React
*   **AI Integration**: Google GenAI SDK (`@google/genai`)
*   **Privacy**: File parsing happens entirely in the browser memory. Only text content is sent to the Gemini API for analysis; no artifacts are persisted on any backend.

## Deployment on Google Cloud Run

This application is designed to run as a stateless container on Google Cloud Run.

### Prerequisites
1.  A Google Cloud Project.
2.  A valid [Gemini API Key](https://aistudio.google.com/).

### Environment Variables
The application requires the following environment variable to be set in the runtime environment:

*   `API_KEY`: Your Gemini API Key.

> **Note:** Since this is a client-side application served via Vite, the API key needs to be available at build time or handled via a proxy for production security. For this demo, we assume the key is provided via `process.env`.

### Port Configuration
Google Cloud Run injects a `PORT` environment variable (defaulting to `8080`) into the container. The application server must listen on this port.

To support this, the `package.json` includes a custom `start` script:

```bash
"start": "vite preview --host 0.0.0.0 --port ${PORT:-8080}"
```

### Deploy Commands

1.  **Build the Container**
    ```bash
    gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/siamese
    ```

2.  **Deploy Service**
    ```bash
    gcloud run deploy siamese \
      --image gcr.io/YOUR_PROJECT_ID/siamese \
      --platform managed \
      --allow-unauthenticated \
      --set-env-vars API_KEY=your_api_key
    ```
