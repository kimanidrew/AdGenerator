# ML provider interfaces

KenyaAds AI keeps model choice separate from the compute provider. The script service supports an optional OpenAI-compatible endpoint for a **self-hosted** model (for example, Qwen served by vLLM on rented GPU infrastructure). Configure `SCRIPT_LLM_BASE_URL`, `SCRIPT_LLM_MODEL` and, only when the endpoint requires it, `SCRIPT_LLM_API_KEY`.

No paid third-party inference API is required or used by the default configuration. When no self-hosted endpoint is configured, the API labels its deterministic output as a **starter template**, not an AI-model result.

Kaggle GPU sessions are temporary and quota-limited; they are not a continuously available HTTP inference server. A Kaggle job-dispatch adapter can be added in the later GPU/training phase without changing the script request or response schema. Do not run GPU inference on the user's local computer.

Before adopting a model, check its commercial license, runtime, VRAM, precision and dependency requirements. Record model IDs and immutable revisions for reproducibility.
