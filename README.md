# KenyaAds AI

A platform for creating short-form adverts with Kenyan language, settings and cultural context. Phase 1 establishes the application foundation; AI inference and video generation arrive in later approved phases.

## Stack

- **Web:** Next.js App Router, TypeScript, Tailwind CSS (deploy to Vercel)
- **API:** Python 3.11, FastAPI, Pydantic, SQLAlchemy, Alembic
- **Auth:** JWT + Argon2 password hashing
- **Database:** Neon PostgreSQL
- **Object storage:** Cloudflare R2 (S3-compatible API)
- **Job queue:** Upstash/managed Redis-compatible service
- **GPU compute:** Kaggle notebooks initially; no local GPU required
- **Training/model artifacts:** Private Hugging Face repositories and/or R2

## Local development (Windows 11)

Docker is optional. See [docs/WINDOWS_SETUP.md](docs/WINDOWS_SETUP.md) for direct Windows setup instructions.

1. Install Git, Node.js LTS and Python 3.11.
2. Clone the repository.
3. Configure `api/.env` from the root `.env.example`; create `web/.env.local` with only `NEXT_PUBLIC_API_URL=http://localhost:8000`.
4. Run the web app and API in separate PowerShell windows.

The frontend runs at http://localhost:3000 and the API docs at http://localhost:8000/docs.

## Provider environment notes

- **Neon:** Use the pooled PostgreSQL URL in `DATABASE_URL`. The API converts the standard `postgresql://` scheme to the installed psycopg 3 dialect. Set `MIGRATION_DATABASE_URL` to Neon’s direct (non-pooler) URL when running Alembic migrations.
- **Upstash:** Set `REDIS_URL` to the TLS URL beginning `rediss://`. Do not include the `redis-cli --tls -u` command prefix.
- **Cloudflare R2:** Use the account S3 API endpoint `https://<ACCOUNT_ID>.r2.cloudflarestorage.com`, or set `R2_ACCOUNT_ID` and leave `STORAGE_ENDPOINT` blank for the API to construct it. Do not use the public `*.r2.dev` URL as the S3 endpoint. Use the R2 S3 Access Key ID and Secret Access Key as `STORAGE_ACCESS_KEY` and `STORAGE_SECRET_KEY`; the R2 API token string itself is not used by boto3.

Create a private R2 bucket and a bucket-scoped token with Object Read & Write access. The API creates short-lived presigned upload/download URLs. Keep credentials in backend secrets only; never use `NEXT_PUBLIC_` for secrets or commit populated environment files.

## Project layout

- `web/` — Next.js frontend
- `api/` — FastAPI API, authentication, database and storage integration
- `ml/` — model/provider interfaces
- `training/` — dataset and training policies
- `infra/` — deployment resources
- `docs/` — setup and architecture guides

## Safety

Training consent is optional and defaults off. Only rights-cleared, explicitly consented content may be considered for training. Never commit `.env`, credentials, private media or datasets. No paid hosted AI inference APIs are required by the design.

Kaggle GPU sessions are temporary and quota-limited. Generation jobs must be asynchronous and may wait for available capacity; Kaggle is not an always-on inference endpoint.
