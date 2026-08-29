# VANGUARD — Deployment Guide

## Architecture Overview
* **Frontend (Next.js)** → Deploy to Vercel (free, instant)
* **Backend (FastAPI + WebSocket)** → Deploy to Railway or Render (free tier available)
* **CSV Data** (bundled)

---

## Step 1: Deploy Backend (Railway — Recommended)

> [!IMPORTANT]
> The backend MUST be deployed first because the frontend needs the backend URL.

### Option A: Railway (Recommended — supports WebSockets natively)
1. Sign up at [railway.app](https://railway.app/) with GitHub
2. Create New Project → Deploy from GitHub Repo
3. Set root directory to `aegis`
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
6. Add environment variable: `PORT=8000`
7. Deploy — Railway gives you a URL like `https://aegis-backend-xxxx.railway.app`

### Option B: Render (Free Tier)
1. Sign up at [render.com](https://render.com/) with GitHub
2. New Web Service → Connect your repo
3. Root Directory: `aegis`
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
6. Instance Type: Free (512MB RAM is enough)

> [!WARNING]
> Render free tier has a 15-minute sleep timer. First request after sleep takes ~30s. Railway free tier is better for demos — no cold starts.

---

## Step 2: Update Frontend API URL

Edit `aegis/frontend/src/hooks/useApi.ts` to point to the deployed backend:
```diff
- const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
+ const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://your-backend-url.railway.app";
```
*Or better — set it via environment variable in Vercel (Step 3).*

---

## Step 3: Deploy Frontend (Vercel)

1. Sign up at [vercel.com](https://vercel.com/) with GitHub
2. Import Project → Select your repo
3. Framework Preset: Next.js (auto-detected)
4. Root Directory: `aegis/frontend`
5. Environment Variables:

| Variable | Value |
| --- | --- |
| `NEXT_PUBLIC_API_URL` | `https://your-backend-url.railway.app` |
| `NEXT_PUBLIC_WS_URL` | `wss://your-backend-url.railway.app` |

6. Deploy → Vercel gives you a URL like `https://vanguard-aegis.vercel.app`

---

## Step 4: Update WebSocket URL

The WebSocket connection in the frontend also needs to point to the deployed backend. Check `useApi.ts` — the WS URL should use `wss://` (secure WebSocket) for production:
```typescript
const WS_BASE = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000";
```

---

## ⚡ Latency Considerations

> [!NOTE]
> **Will backend latency affect the user experience?**
> Short Answer: Minimal impact

| Operation | Local Latency | Deployed Latency | User Impact |
| --- | --- | --- | --- |
| REST API calls | ~5ms | ~100-200ms | Negligible — data loads on mount |
| WebSocket stream | ~1ms | ~50-150ms | Minimal — 1.5s tick interval absorbs this |
| CSV data loading | ~2s | ~2s (once on startup) | None — only on server boot |

**Why it works:**
* The simulation ticks every 1.5 seconds — even with 200ms network latency, each tick arrives well before the next one
* Initial data loads once (metrics, attacks, SHAP) — a 200ms delay on page load is imperceptible
* WebSocket frames are tiny (~2-5KB per tick) — even on slow connections they transfer in <50ms
* The CSV data stays on the server — no large file transfers to the client

**Potential Issue: Cold Starts**
* **Render Free Tier:** Server sleeps after 15 min inactivity. First request takes ~30s. *Mitigate: Visit the backend URL 2 minutes before your demo to wake it up.*
* **Railway Free Tier:** No cold start issue, server stays warm.

---

## Quick Deploy Checklist
- [ ] Backend deployed and accessible at `https://your-url`
- [ ] Test: `curl https://your-url/api/blue-team/metrics` returns JSON
- [ ] Test: WebSocket connects at `wss://your-url/ws/live-feed`
- [ ] Frontend `NEXT_PUBLIC_API_URL` set in Vercel env vars
- [ ] Frontend `NEXT_PUBLIC_WS_URL` set in Vercel env vars
- [ ] Frontend deployed and loads at Vercel URL
- [ ] Simulator page: "Launch Attack" button works
- [ ] Landing page: All data sections load correctly

---

## CORS Configuration
The backend already has CORS configured in `main.py`. Verify it allows your Vercel domain:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For hackathon — restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```
> [!TIP]
> For the hackathon demo, `allow_origins=["*"]` is fine. For production, restrict to your Vercel domain.
