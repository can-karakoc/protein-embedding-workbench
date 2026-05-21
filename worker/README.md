# Worker Placeholder

Move long-running embedding jobs here later.

Possible stack:

- Celery + Redis
- RQ + Redis
- Dramatiq
- Modal/RunPod for GPU-backed inference later

For the MVP, keep embedding inference inside the FastAPI backend.
