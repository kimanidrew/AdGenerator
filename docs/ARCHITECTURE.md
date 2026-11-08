# KenyaAds AI Architecture

## Production topology

- **Frontend:** Next.js App Router deployed to Vercel.
- **Backend API:** FastAPI deployed as a separate always-on web service. Render is the proposed first provider; confirm the provider before deployment.
- **Database:** Neon managed PostgreSQL. Use a pooled connection string for application traffic and a direct connection string for Alembic migrations where required.
- **Queue:** Redis-compatible managed service for background job coordination.
- **Media storage:** S3-compatible object storage for generated images, audio, video and downloadable assets. Do not store large media files in PostgreSQL or on an ephemeral application filesystem.
- **GPU compute:** Kaggle notebooks initially, subject to Kaggle session availability and quotas. Kaggle is not an always-on inference server.
- **Model and adapter storage:** Private Hugging Face repositories and/or S3-compatible object storage, with immutable revisions and recorded checksums.

## Request and generation lifecycle

1. The Vercel frontend sends an authenticated request to the FastAPI API.
2. The API validates the request, writes the ad/job record to Neon and enqueues work.
3. A job coordinator dispatches work to an available Kaggle notebook run. Notebook runs poll or receive a bounded batch of jobs; they must not attempt to keep a Kaggle session alive indefinitely.
4. The notebook loads the selected model and adapter revisions, performs inference on the Kaggle GPU, and writes artifacts to object storage.
5. The notebook reports progress and completion to an authenticated backend callback or job-result endpoint.
6. The API updates Neon; the frontend reads status through polling or SSE and displays the resulting media using signed or otherwise access-controlled storage URLs.

Jobs must be idempotent, retryable and resumable where practical. If Kaggle capacity or quota is unavailable, jobs remain queued and the UI must communicate the delay honestly. Do not promise instant generation or continuous availability from Kaggle.

## GPU provider portability

Define a provider interface independent of the model implementation. The initial Kaggle adapter and future GPU-provider adapters must implement the same job contract for health/capability checks, submit, status, cancel where supported, logs and artifact results.

Keep model configuration separate from provider configuration. Record provider, GPU type when available, model ID/revision, adapter revision, dataset revision, code commit, parameters, metrics and artifact locations for every run. Switching GPU providers must not require changing the frontend or database schema.

Model portability is not automatic: check runtime, VRAM, precision, dependency and license compatibility before loading a model on another GPU provider.

## Training lifecycle

Only user-consented, rights-cleared and admin-approved data may enter training datasets. Apply PII removal, deduplication, quality checks and versioned manifests. Train in Kaggle initially, publish immutable checkpoints to private model storage, evaluate against a held-out benchmark, and require an explicit promotion gate before production use. Preserve rollback to the previous production revision.

## Local development (Windows 11)

Docker is optional. Developers can run the Next.js and FastAPI applications directly on Windows and connect to hosted Neon, Redis and object storage services using environment variables. No local GPU is required or used. Keep secrets in local environment files and hosting-provider secret stores; never commit them.

## Security and reliability baseline

- Argon2 password hashing and short-lived/rotatable JWT credentials.
- Optional AI-training consent defaults to false and is timestamped when granted.
- Validate ownership and authorization for every ad, job and media operation.
- Keep provider tokens and storage credentials server-side only.
- Use signed upload/download URLs where supported.
- Apply rate limits, request-size limits, timeouts, retries and audit logging.
- Honor deletion requests across application records and eligible training data.
- No paid hosted AI inference APIs are required by the design.
