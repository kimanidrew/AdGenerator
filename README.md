# KenyaAds AI

A platform for creating short-form adverts with Kenyan language, settings and cultural context. Phase 1 establishes the application foundation; AI inference and video generation arrive in later approved phases.

## Stack

- **Web:** Next.js App Router, TypeScript, Tailwind CSS (deploy to Vercel)
- **API:** Python 3.11, FastAPI, Pydantic, SQLAlchemy, Alembic
- **Auth:** JWT + Argon2 password hashing
- **Database:** Neon PostgreSQL
- **Object storage:** Cloudflare R2 (S3-compatible API)
- **Job queue:** Managed Redis-compatible service (provider to be selected)
- **GPU compute:** Kaggle notebooks initially; no local GPU required
- **Training/model artifacts:** Private Hugging Face repositories and/or R2

## Local development (Windows 11)

Docker is optional. See [docs/WINDOWS_SETUP.md](docs/WINDOWS_SETUP.md) for direct Windows setup instructions.

1. Install Git, Node.js LTS and Python 3.11.
2. Clone the repository.
3. Configure the frontend and backend environment files using `.env.example`.
4. Run the web app and API in separate PowerShell windows.

The frontend runs at http://localhost:3000 and the API docs at http://localhost:8000/docs.

## Cloudflare R2

Create a private bucket named `kenyaads-media` and an R2 API token scoped to that bucket with Object Read & Write access. Configure `STORAGE_ENDPOINT`, `STORAGE_BUCKET`, `STORAGE_REGION=auto`, `STORAGE_ACCESS_KEY` and `STORAGE_SECRET_KEY` in the backend environment. See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

Never commit real credentials. R2 credentials must remain server-side; use short-lived presigned URLs for browser uploads/downloads.

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
