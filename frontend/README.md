# Protein Embedding Workbench Frontend

Next.js + Tailwind frontend for the FastAPI protein embedding backend.

## Local

```bash
npm install
cp .env.local.example .env.local
npm run dev
```

Set `NEXT_PUBLIC_API_BASE_URL` to your backend origin. The default local backend is `http://localhost:8000`.

## Vercel

Add `NEXT_PUBLIC_API_BASE_URL` in Project Settings -> Environment Variables, then deploy the `frontend` directory.
