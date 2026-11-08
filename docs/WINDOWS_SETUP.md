# Windows 11 development setup (without Docker)

Docker is optional and is not required for this project. Your Windows computer runs the website and API for development only; it does not run AI inference or model training.

## Install prerequisites

1. Install Git for Windows.
2. Install Node.js LTS (includes npm).
3. Install Python 3.11.
4. Clone the repository and open PowerShell in the project directory.

## Configure environment

Copy the root `.env.example` to `api/.env` for backend settings, then fill in your hosted Neon, Redis and Cloudflare R2 credentials. Create `web/.env.local` with the frontend API URL:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Do not put database, JWT, Redis or R2 secrets in `web/.env.local`. Never commit populated environment files or paste secrets into chat.

For Cloudflare R2, create a private bucket (for example `kenyaads-media`) and a bucket-scoped R2 API token with Object Read & Write permissions. Set `STORAGE_ENDPOINT`, `STORAGE_BUCKET`, `STORAGE_REGION=auto`, `STORAGE_ACCESS_KEY` and `STORAGE_SECRET_KEY` in `api/.env`. The endpoint format is `https://<ACCOUNT_ID>.r2.cloudflarestorage.com`.

## Frontend

```powershell
cd web
npm install
npm run dev
```

The frontend should be available at http://localhost:3000.

## Backend

Open a second PowerShell window:

```powershell
cd api
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The API documentation should be available at http://localhost:8000/docs.

If PowerShell blocks virtual-environment activation, use:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## Database setup

The API may require database migrations before first use:

```powershell
alembic upgrade head
```

Run that command from the API directory with the virtual environment activated and the Neon database URL configured.

## Verify

- Open http://localhost:3000.
- Open http://localhost:8000/health.
- Open http://localhost:8000/docs.
- Register a test account and verify login.
- Confirm the API can connect to Neon.

## Important

- No Docker installation is required for this workflow.
- No local GPU is required or used.
- Kaggle GPU jobs are remote, asynchronous jobs and may wait for available quota/session capacity.
- Production frontend deployment is on Vercel. The FastAPI backend and managed Redis are separate hosted services.
- Cloudflare R2 stores media and artifacts; keep the bucket private and issue short-lived presigned URLs through the API.
- Never paste secrets into chat or commit them to Git.
