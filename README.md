# KenyaAds AI

A platform for creating short-form adverts with Kenyan language, settings and cultural context. Phase 1 established the foundation; Phase 2 adds script generation and an editable script studio.

## Stack

- **Web:** Next.js App Router, TypeScript, Tailwind CSS (Vercel Services)
- **API:** Python 3.12, FastAPI, Pydantic, SQLAlchemy, Alembic
- **Auth:** JWT + Argon2 password hashing
- **Database:** Neon PostgreSQL
- **Object storage:** Cloudflare R2 (S3-compatible API)
- **Job queue:** Upstash/managed Redis-compatible service
- **GPU compute:** Kaggle notebooks initially; no local GPU required
- **Training/model artifacts:** Private Hugging Face repositories and/or R2

## Phase 2 — script studio

Sign in and open `/create`. Enter an advert brief and select the product, industry, audience, language (English, Kiswahili or Sheng), duration (10–60 seconds), platform and tone. The API returns validated scene JSON with visual direction, voiceover, on-screen text, timing, caption, hashtags and a call to action. Edit the draft in the browser and copy the JSON or voiceover.

**Generation modes:**
- By default, a deterministic starter-template provider makes the feature usable without a model server. The UI labels these results as **Starter draft**, not AI output.
- To use a self-hosted LLM, configure `SCRIPT_LLM_BASE_URL`, `SCRIPT_LLM_MODEL`, and optionally `SCRIPT_LLM_API_KEY` on the API service. The endpoint must implement the OpenAI-compatible `/chat/completions` API and return the requested JSON. Example: Qwen served by vLLM on your own rented GPU infrastructure.

No paid third-party inference API or local GPU is required. Kaggle is temporary and quota-limited, not an always-on HTTP endpoint; the later job-dispatch phase will integrate bounded Kaggle jobs. Phase 2 drafts are not yet persisted to account history.

## Vercel deployment (web + API)

The repository root contains `vercel.json`, which configures two services in one Vercel project:
- `web`: Next.js, publicly routed at `/`.
- `api`: FastAPI, publicly routed at `/api` and `/api/*`.

The API entrypoint is `app.main:app` relative to the `api/` service root. Browser requests use same-origin relative `/api/...` URLs. Configure backend secrets on the API service only; do not set `NEXT_PUBLIC_API_URL` in production.

The Celery worker and scheduler remain external background processes. Kaggle remains asynchronous, temporary GPU compute rather than an always-on API host.

## Local development (Windows 11)

Docker is optional. See [docs/WINDOWS_SETUP.md](docs/WINDOWS_SETUP.md).
1. Install Git, Node.js LTS and Python 3.12.
2. Clone the repository.
3. Configure `api/.env` from the root `.env.example`; for split local development create `web/.env.local` with `NEXT_PUBLIC_API_URL=http://localhost:8000`.
4. Run the web app and API in separate PowerShell windows.

The frontend runs at http://localhost:3000 and API docs at http://localhost:8000/docs.

## Provider environment notes

- **Neon:** Use the pooled PostgreSQL URL in `DATABASE_URL` and direct (non-pooler) URL in `MIGRATION_DATABASE_URL` for Alembic.
- **Upstash:** Set `REDIS_URL` to the TLS URL beginning `rediss://`.
- **Cloudflare R2:** Use the account S3 API endpoint `https://<ACCOUNT_ID>.r2.cloudflarestorage.com` and S3 Access Key ID / Secret Access Key.
- **Self-hosted script model:** Set `SCRIPT_LLM_BASE_URL` to the base URL (ending in `/v1` when required by the server), `SCRIPT_LLM_MODEL` to the served model ID, and optional `SCRIPT_LLM_API_KEY`. These are API-only secrets/configuration.

## Project layout

- `web/` — Next.js frontend
- `api/` — FastAPI API, authentication, database and storage integration
- `ml/` — model/provider interfaces
- `training/` — dataset and training policies
- `infra/` — deployment resources
- `docs/` — setup and architecture guides

## Safety

Training consent is optional and defaults off. Only rights-cleared, explicitly consented content may be considered for training. Never commit `.env`, credentials, private media or datasets. Do not generate deceptive endorsements or unverified product claims.

Kaggle GPU sessions are temporary and quota-limited. Generation jobs must be asynchronous and may wait for available capacity; Kaggle is not an always-on inference endpoint.


## Phase 3 storyboard worker

Storyboard requests are queued by the Vercel API and processed by the external Celery worker. Run it from the `api` directory:

```bash
celery -A app.worker.celery_app.celery_app worker --loglevel=INFO
```

Configure `IMAGE_GENERATION_BASE_URL`, `IMAGE_GENERATION_MODEL`, and optional `IMAGE_GENERATION_API_KEY` for an HTTPS OpenAI-compatible image endpoint that returns PNG data in `data[0].b64_json`. The worker also needs the same `REDIS_URL` and R2 credentials. GPU inference stays on the hosted GPU provider, not on the user's computer or Vercel. The worker and image provider must be running before storyboard jobs can complete.
