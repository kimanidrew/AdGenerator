# Windows 11 development setup (without Docker)

Docker is optional and is not required for this project. Your Windows computer runs the website and API for development only; it does not run AI inference or model training.

## Install prerequisites

1. Install Git for Windows.
2. Install Node.js LTS (includes npm).
3. Install Python 3.11.
4. Clone the repository and open PowerShell in the project directory.

## Frontend

```powershell
cd web
npm install
Copy-Item .env.example .env.local -ErrorAction SilentlyContinue
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

## Hosted dependencies

Configure development credentials in local environment files for:
- Neon PostgreSQL
- Managed Redis
- S3-compatible object storage

Use the variable names documented in `.env.example`. Do not commit `.env`, `.env.local`, credentials, API tokens or private keys. Use separate development resources where possible.

The API may require database migrations before first use:
```powershell
alembic upgrade head
```

Run that command from the API directory with the virtual environment activated and the database URL configured.

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
- Production frontend deployment is on Vercel. The FastAPI backend, Redis and object storage are separate hosted services.
- Never paste secrets into chat or commit them to Git.
