# KenyaAds AI Architecture

## Production topology

- **Vercel project:** One repository deployment with two Vercel Services.
- **Web service:** Next.js App Router, rooted at `web/`, publicly routed at `/`.
- **API service:** FastAPI, rooted at `api/`, entrypoint `app.main:app`, publicly routed at `/api` and `/api/*`.
- **Service bindings:** None currently. Browser API calls use same-origin relative `/api/...` URLs; there are no confirmed server-to-server service calls.
- **Background worker and scheduler:** External deployment, not Vercel HTTP services. They consume the managed Redis queue and use the same database configuration.
- **Database:** Neon managed PostgreSQL. Use a pooled connection string for application traffic and a direct connection string for Alembic migrations where required.
- **Queue:** Redis-compatible managed service.
- **Media and artifact storage:** Cloudflare R2 using its S3-compatible API. Store generated images, audio, video, user uploads, training datasets and downloadable assets in a private R2 bucket. Do not store large media files in PostgreSQL or on an ephemeral application filesystem.
- **GPU compute:** Kaggle notebooks initially, subject to Kaggle session availability and quotas. Kaggle is not an always-on inference server.
- **Model and adapter storage:** Private Hugging Face repositories and/or R2, with immutable revisions and recorded checksums.

## Vercel Services routing

The root `vercel.json` defines `api` and `web` as separate services. Public rewrites are ordered from most specific to least specific:

1. `/api` → `api`
2. `/api/*` → `api`
3. `/*` → `web`

The rewrites preserve the incoming path. FastAPI therefore continues to receive `/api/auth/signup` and `/api/auth/login`, matching the existing router prefix. The API service does not currently expose its health endpoints publicly through these rewrites.

The frontend authentication form uses relative `/api/auth/...` URLs by default. For split local development only, `web/.env.local` may set `NEXT_PUBLIC_API_URL=http://localhost:8000`. Do not set that variable in the Vercel production environment. Same-origin browser requests do not require CORS; retain the configured CORS origins only for separate local or external clients.

Vercel Services are currently a beta feature. Run `vercel dev` from the repository root with a current Vercel CLI to test the services together.

## Cloudflare R2 configuration

Create a private R2 bucket (initial name: `kenyaads-media`) and an R2 API token scoped to that bucket with Object Read & Write permissions. Configure the backend with:

- `STORAGE_PROVIDER=cloudflare_r2`
- `STORAGE_ENDPOINT=https://<ACCOUNT_ID>.r2.cloudflarestorage.com`
- `STORAGE_BUCKET=kenyaads-media`
- `STORAGE_REGION=auto`
- `STORAGE_ACCESS_KEY` and `STORAGE_SECRET_KEY` from the R2 token

The API uses the S3-compatible endpoint through boto3. The helper in `api/app/storage.py` creates short-lived presigned PUT and GET URLs. Keep the bucket private and credentials server-side; never place R2 secrets in frontend variables or commit real credentials. Authorize ownership and validate upload type/size in the API before issuing a presigned URL. Configure CORS on the R2 bucket only for the required frontend origins and methods when browser-direct uploads are introduced.

The storage helper is infrastructure plumbing; upload routes, ownership checks, lifecycle cleanup and production bucket policies must be added in the relevant feature phase.

## Request and generation lifecycle

1. The Vercel frontend sends an authenticated request to the FastAPI API.
2. The API validates the request, writes the ad/job record to Neon and enqueues work.
3. An external job coordinator/worker dispatches work to an available Kaggle notebook run. Notebook runs poll or receive a bounded batch of jobs; they must not attempt to keep a Kaggle session alive indefinitely.
4. The notebook loads the selected model and adapter revisions, performs inference on the Kaggle GPU, and writes artifacts to private Cloudflare R2 storage.
5. The notebook reports progress and completion to an authenticated backend callback or job-result endpoint.
6. The API updates Neon; the frontend reads status through polling or SSE and receives short-lived media URLs from the API.

Jobs must be idempotent, retryable and resumable where practical. If Kaggle capacity or quota is unavailable, jobs remain queued and the UI must communicate the delay honestly. Do not promise instant generation or continuous availability from Kaggle.

## GPU provider portability

Define a provider interface independent of the model implementation. The initial Kaggle adapter and future GPU-provider adapters must implement the same job contract for health/capability checks, submit, status, cancel where supported, logs and artifact results.

Keep model configuration separate from provider configuration. Record provider, GPU type when available, model ID/revision, adapter revision, dataset revision, code commit, parameters, metrics and artifact locations for every run. Switching GPU providers must not require changing the frontend or database schema.

Model portability is not automatic: check runtime, VRAM, precision, dependency and license compatibility before loading a model on another GPU provider.

## Training lifecycle

Only user-consented, rights-cleared and admin-approved data may enter training datasets. Apply PII removal, deduplication, quality checks and versioned manifests. Train in Kaggle initially, publish immutable checkpoints to private model storage, evaluate against a held-out benchmark, and require an explicit promotion gate before production use. Preserve rollback to the previous production revision.

## Local development (Windows 11)

Docker is optional. Developers can run the Next.js and FastAPI applications directly on Windows and connect to hosted Neon, Redis and Cloudflare R2 using environment variables. No local GPU is required or used. Keep secrets in local environment files and hosting-provider secret stores; never commit them.

## Security and reliability baseline

- Argon2 password hashing and short-lived/rotatable JWT credentials.
- Optional AI-training consent defaults to false and is timestamped when granted.
- Validate ownership and authorization for every ad, job and media operation.
- Keep provider tokens and storage credentials server-side only.
- Use short-lived signed upload/download URLs; validate object keys, MIME types and size limits server-side.
- Apply rate limits, request-size limits, timeouts, retries and audit logging.
- Honor deletion requests across application records and eligible training data.
- No paid hosted AI inference APIs are required by the design.
