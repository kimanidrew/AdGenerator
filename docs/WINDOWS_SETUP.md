# Windows 11 setup
1. Install Docker Desktop for Windows and choose its WSL 2 backend.
2. If prompted, allow WSL installation and restart Windows.
3. Start Docker Desktop and wait until the engine is running.
4. Open PowerShell and check: `wsl --version`, `docker --version`, `docker compose version`.
5. In Docker Desktop, confirm **Settings → General → Use the WSL 2 based engine**. If using Ubuntu WSL, enable it under **Settings → Resources → WSL Integration**.
6. Copy `.env.example` to `.env` and run `docker compose up --build` in the project folder.
7. Visit http://localhost:3000 and http://localhost:8000/docs.

Stop with Ctrl+C, then `docker compose down`. Do not share your `.env` file.

## Find your GPU later
Open PowerShell and run `nvidia-smi`. If unavailable, open **Task Manager → Performance → GPU** and note the GPU name and dedicated GPU memory (VRAM). Phase 1 does not require a GPU.
