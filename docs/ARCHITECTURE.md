# Architecture
Browser -> Next.js (:3000) -> FastAPI (:8000) -> PostgreSQL (:5432).
FastAPI uses Redis (:6379) as the Celery broker/backend. MinIO provides S3-compatible media storage (:9000; console :9001). Worker and beat services are provisioned for future background jobs.

## Hybrid compute
Web/API/data services can run locally or on a rented server. GPU inference is a separate worker/provider deployment and will be configured after GPU inventory. No paid hosted AI inference APIs are included.

## Security baseline
Passwords are Argon2 hashed. JWT and service credentials are environment variables. Training consent is optional, defaults false, and is timestamped only when granted. Future training must use rights-cleared opted-in content and honor deletion requests.
