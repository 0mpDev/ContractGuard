# Deploying RiskLens AI

Architecture: **Next.js frontend (Vercel)** → **FastAPI backend (Render, Docker)** → **Postgres (Supabase)**. LLM = Groq.
Deploy in this order: database → backend → frontend → (tighten CORS).

## 0. Push to GitHub
Push this repo (keep `backend/` and `frontend/` as top-level folders).

## 1. Database — Supabase
1. Create a project at supabase.com → **Project Settings → Database → Connection string**.
2. Copy the **Session pooler** URI (`postgresql://postgres.xxxx:PASSWORD@aws-0-...pooler.supabase.com:5432/postgres`). Use this, not the direct URL, on hosts without IPv6.
3. Tables are created automatically on first backend start (`init_db()`).

## 2. Backend — Render
1. Render → **New → Web Service** → connect your GitHub repo.
2. Settings: **Root Directory** `backend`, **Runtime** `Docker` (it uses `backend/Dockerfile`, which installs Tesseract).
3. Environment variables:
   | Key | Value |
   |---|---|
   | `GROQ_API_KEY` | from console.groq.com |
   | `DATABASE_URL` | the Supabase URI from step 1 |
   | `ALLOWED_ORIGINS` | set after step 3 (your Vercel URL) — leave blank for now |
4. Deploy. Verify: `https://<your-api>.onrender.com/contracts/model-health` → `"status": "configured"`, and `/dashboard/health` → `"connected": true`.

## 3. Frontend — Vercel
1. Vercel → **Add New Project** → import the repo.
2. **Root Directory:** `frontend` (framework auto-detected as Next.js).
3. Environment variable: `NEXT_PUBLIC_API_URL` = `https://<your-api>.onrender.com` (no trailing slash).
   This is baked in at build time → if you change it, **redeploy**.
4. Deploy.

## 4. Lock down CORS
Back in Render, set `ALLOWED_ORIGINS=https://<your-app>.vercel.app` and redeploy the backend.

## Smoke test
Open the Vercel URL → Login (Analyst) → upload a PDF → wait ~30-60s → contract detail page loads → try Submit to Manager → log in as Manager and approve.

## Known limitations to be aware of
- **No real authentication.** "Login" just stores role/email in browser localStorage, and the API has no auth. Anyone with the URL can act as a manager or call the API directly. Fine for a demo; add auth (e.g. Supabase Auth + JWT checks in FastAPI) before real use.
- **Uploaded PDFs live on the container's local disk**, which is wiped on every Render deploy/restart on the free tier. Analysis results are in Postgres so the app keeps working, but "Generate Recommendations" loses the original-text context, and citations can't be rebuilt, for contracts uploaded before a restart. Fix: attach a Render persistent disk mounted at `/app/uploads`, or move files to Supabase Storage/S3.
- **Free-tier cold starts:** Render free services sleep after inactivity; first request can take ~30-60s. Uploads also take 30-60s of LLM time — keep the request timeout in mind.
- Groq free tier rate limits apply (the README mentions a model fallback chain, but the code currently only uses `llama-3.3-70b-versatile`).
