# kadoisaceo 🚀

Official developer portfolio and REST API hub of **Kado**, deployed live on [kado.sang.ceo](https://kado.sang.ceo).

[![FastAPI](https://img.shields.io/badge/FastAPI-1.0-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Vercel](https://img.shields.io/badge/Vercel-Deployed-000000?style=flat-square&logo=vercel&logoColor=white)](https://vercel.com)

---

## ⚡ Features

- **High-Performance Python Backend:** Powered by **FastAPI** with ASGI architecture.
- **Interactive REST API Playground:** Real-time text inspection endpoint (`POST /api/playground/inspect`) with genuine latency metrics measured in JavaScript.
- **Auto-Generated Swagger Docs:** Full interactive documentation available at `/docs` and ReDoc at `/redoc`.
- **Integrated Terminal Console:** Interactive bash-style terminal emulator supporting `help`, `about`, `skills`, `projects`, `api`, and `coffee`.
- **2-Step Streamlined Support:** Minimalist and non-intrusive Buy Me a Coffee flow supporting Saweria, Trakteer, and static QRIS.
- **Accessibility & UX First:** Respects `prefers-reduced-motion`, responsive mobile-first UI with Tailwind CSS and glassmorphism obsidian theme.

---

## 🛠️ Project Structure

```text
kadoisaceo/
├── api/
│   └── index.py            # FastAPI main application & serverless handler
├── templates/
│   └── index.html          # Modern, responsive single-page frontend
├── requirements.txt        # Python dependencies
├── vercel.json             # Vercel serverless routing configuration
└── README.md
```

---

## 🚀 Local Development

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Kadokun404/kadoisaceo.git
   cd kadoisaceo
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the local dev server:**
   ```bash
   uvicorn api.index:app --reload --port 8000
   ```

4. **Open in browser:**
   - Web Portfolio: [http://localhost:8000](http://localhost:8000)
   - Swagger API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🌐 Deploy to Vercel

1. Import this repository in [Vercel](https://vercel.com/new).
2. Click **Deploy** (Vercel automatically provisions the Python runtime via `vercel.json` and `api/index.py`).
3. Under **Settings → Domains**, assign `kado.sang.ceo`.

---

© 2026 [Kado](https://kado.sang.ceo). All rights reserved.
