# KenyaAds AI Architecture

## Production topology

- **Vercel project:** One repository deployment with two Vercel Services.
- **Web service:** Next.js App Router, rooted at `web/`, publicly routed at `/`.
- **API service:** FastAPI, rooted at `api/`, entrypoint `app.main:app`, publicly routed at `/api` and `/api/*`.
- **Service bindings:** None currently. Browser API calls use same-origin relative `/api/...` URLs.
- **Background worker and scheduler:** External deployment, not Vercel HTTP services. They consume the managed Redis queue and use the same database configuration.
- **Database:** Neon managed PostgreSQL. Use a pooled connection string for application traffic and a direct connection string for Alembic migrations where required.
- **Queue:** Redis-compatible managed service.
- **Media and artifact storage:** Cloudflare R2 using its S3-compatible API. Store generated images, audio, video, user uploads, training datasets and downloadable assets in a private R2 bucket.
- **GPU compute:** Kaggle notebooks initially, subject to Kaggle session availability and quotas. Kaggle is not an always-on inference server.
- **Model and adapter storage:** Private Hugging Face repositories and/or R2, with immutable revisions and recorded checksums.

## Phase 2 — script generation

The authenticated API endpoint `POST /api/scripts/generate` accepts an advert brief and options for product, industry, audience, language, duration, platform and tone. It returns a Pydantic-validated JSON script with ordered scenes, per-scene timing, visual direction, voiceover, on-screen text, caption, hashtags and a call to action. Scene durations must add up exactly to the requested runtime.

The provider boundary lives in `api/app/services/script_generator.py`:
- With `SCRIPT_LLM_BASE_URL` configured, the API calls a self-hosted OpenAI-compatible chat-completions endpoint and validates the returned JSON.
- Without it, the API returns a deterministic starter template and explicitly labels the result `starter_template`; it does not pretend a model generated it.
- Model ID, endpoint and optional API key are configuration, not frontend concerns. Keep secrets on the API service only.

The Next.js `/create` studio requires a logged-in user, submits the brief, and lets the user edit each scene, title, caption, hashtags and call to action. Phase 2 drafts are held in browser memory only; persistent projects, history, background job progress and Kaggle job dispatch are later phase work.

## Vercel Services routing

The root `vercel.json` defines `api` and `web` as separate services. Public rewrites are ordered from most specific to least specific:
1. `/api` → `api`
2. `/api/*` → `api`
3. `/*` → `web`

The rewrites preserve the incoming path. FastAPI therefore receives `/api/auth/signup` and `/api/scripts/generate`, matching the router prefixes. The API service does not currently expose its health endpoints publicly through these rewrites.

The frontend uses relative `/api/...` URLs by default. For split local development only, `web/.env.local` may set `NEXT_PUBLIC_API_URL=http://localhost:8000`. Do not set that variable in Vercel production.

## Cloudflare R2 configuration

Create a private R2 bucket and an R2 API token scoped to that bucket with Object Read & Write permissions. Configure `STORAGE_ENDPOINT=https://<ACCOUNT_ID>.r2.cloudflarestorage.com`, `STORAGE_BUCKET`, `STORAGE_REGION=auto`, `STORAGE_ACCESS_KEY` and `STORAGE_SECRET_KEY`, or set `R2_ACCOUNT_ID` and leave the endpoint blank. Keep credentials server-side and the bucket private.

## Request and media generation lifecycle

Later asynchronous media phases will write ad/job records to Neon, enqueue work in managed Redis, and dispatch bounded jobs to an available Kaggle notebook through an external coordinator. The notebook writes artifacts to private R2 storage and reports completion to the API. Kaggle capacity and quota can delay work; never treat it as an always-on endpoint.

## GPU provider portability

Keep model configuration separate from GPU provider configuration. Provider adapters should expose a common job contract for health/capability checks, submit, status, cancellation where supported, logs and artifact results. Record provider, GPU type, model ID/revision, adapter revision, dataset revision, code commit, parameters, metrics and artifact locations. Model portability still requires runtime, VRAM, precision, dependency and license checks.

## Training lifecycle

Only user-consented, rights-cleared and admin-approved data may enter training datasets. Apply PII removal, deduplication, quality checks and versioned manifests. Train in Kaggle initially, publish immutable checkpoints to private model storage, evaluate against a held-out benchmark, and require an explicit promotion gate before production use. Preserve rollback to the previous production revision.

## Local development (Windows 11)

Docker is optional. Developers can run Next.js and FastAPI directly on Windows and connect to hosted Neon, Redis and Cloudflare R2. No local GPU is required or used. Keep secrets in local environment files and hosting-provider secret stores; never commit them.

## Security and reliability baseline

- Argon2 password hashing and short-lived/rotatable JWT credentials.
- Optional AI-training consent defaults to false and is timestamped when granted.
- Validate ownership and authorization for every ad, job and media operation.
- Keep provider tokens and storage credentials server-side only.
- Use short-lived signed upload/download URLs; validate object keys, MIME types and size limits server-side.
- Apply rate limits, request-size limits, timeouts, retries and audit logging.
- Honor deletion requests across application records and eligible training data.
- No paid hosted AI inference APIs are required by the design.
