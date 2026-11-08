# KenyaAds AI

A self-hosted platform for creating short-form adverts with Kenyan language, settings and cultural context. Phase 1 establishes the application foundation; AI inference/video generation arrives in later approved phases.

## Stack
- Web: Next.js App Router, TypeScript, Tailwind CSS
- API: Python 3.11, FastAPI, Pydantic, SQLAlchemy, Alembic
- Auth: JWT + Argon2 password hashing
- Services: PostgreSQL, Redis, Celery, MinIO
- Local Windows development: Docker Desktop with WSL 2

## Quick start (Windows 11)
1. Install Docker Desktop and enable its WSL 2 backend.
2. Copy `.env.example` to `.env`.
3. In PowerShell at the repository root, run `docker compose up --build`.
4. Open http://localhost:3000 and http://localhost:8000/docs.

Stop with `docker compose down`. `docker compose down -v` also deletes local database/object-store volumes.

## Layout
`web/` Next.js UI · `api/` FastAPI/auth/database · `ml/` provider interfaces · `training/` data/training policies · `infra/` deployment · `docs/` guides.

## Safety
Training consent is optional and defaults off. Only rights-cleared, explicitly consented content may be considered for training. Never commit `.env`, credentials, private media or datasets. No paid AI inference APIs are used.

GPU model and VRAM are not yet known; Phase 1 does not require a GPU. Identify them before selecting video/image models.
