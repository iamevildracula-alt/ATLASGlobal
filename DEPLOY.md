# ATLASGlobal: Deployment Guide

This guide details how to deploy the ATLASGlobal AI platform to Google Cloud Run.

## Prerequisites
1.  **Google Cloud Project**: Ensure you have an active GCP project.
2.  **gcloud CLI**: Installed and authenticated (`gcloud auth login`).
3.  **Docker**: Installed and running locally (optional, but recommended for testing).

## Option 1: One-Click Deployment (Script)
We have prepared a script to automate the build and deployment process.

1.  Open your terminal in the project root.
2.  Run the deployment script:
    ```bash
    ./deploy.sh
    ```
    *Note: On Windows, use Git Bash or WSL to run the script, or execute the commands inside it manually via PowerShell.*

## Option 2: Continuous Deployment (Cloud Build)
A `cloudbuild.yaml` file is included for CI/CD pipelines.

1.  Connect your GitHub repository to **Google Cloud Build**.
2.  Create a Trigger that watches the `main` branch.
3.  Set the Configuration to use `cloudbuild.yaml`.
4.  On every push to `main`, Google Cloud will:
    - Build the Docker image.
    - Push it to Google Container Registry (GCR).
    - Deploy the new revision to Cloud Run.

## Configuration
The application is configured via Environment Variables. You can set these in the Cloud Run console or via `gcloud`:

- `PORT`: 8000 (Default)
- `ENV`: `production`
- `DATABASE_URL`: (Connection string for your production PostgreSQL instance)

## Verification
Once deployed, Cloud Run will provide a URL (e.g., `https://atlas-global-core-xyz.a.run.app`).
Visit this URL to access the Mission Control interface.
