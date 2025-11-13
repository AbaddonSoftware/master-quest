# Docker & Deployment Notes

## Cloud Build (API)

`docker/cloudbuild.api.yml` builds the API image, then runs Alembic migrations using that image before pushing to the registry. Set the following substitutions/secrets when triggering the build:

- `_IMAGE`: fully-qualified artifact repository destination (e.g. `us-central1-docker.pkg.dev/<project>/masterquest/api:latest`).
- `DATABASE_URL`: connection string pointing at the production database (provide via secret manager/env substitution).
- `SECRET_KEY` (optional): forwarded to the container if you need it during migrations.

## Cloud Run deployment flow

1. Trigger Cloud Build for the API (`gcloud builds submit --config docker/cloudbuild.api.yml`).
2. After the build succeeds (migrations applied), deploy the new image to Cloud Run (`gcloud run deploy masterquest-api --image $_IMAGE ...`).
3. Trigger Cloud Build for the web frontend if needed (`docker/cloudbuild.web.yml`).

## Local helpers

- `docker/scripts/run-migrations.sh`: run Alembic migrations with your current env (`DATABASE_URL` must be set) without starting the app server.
- `docker/scripts/entrypoint.sh`: production entry point, now only launches Gunicorn because migrations are handled ahead of time.
