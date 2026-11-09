import os
import re
import time
import hashlib
from typing import Optional, Dict
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATE_PATH = os.path.join(BASE_DIR, "templates", "index.html")

# Inisialisasi FastAPI app
app = FastAPI(
    title="Kado REST API & Developer Hub",
    description="Official API backend for kado.sang.ceo by Kado",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS untuk akses publik
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static folder jika direktori ada
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Startup timestamp untuk hitung uptime
STARTUP_TIME = time.time()

# Simple in-memory rate limiting (IP -> list of timestamps)
RATE_LIMIT_STORE: Dict[str, list] = {}
MAX_REQUESTS_PER_MINUTE = 30

def check_rate_limit(client_ip: str) -> bool:
    now = time.time()
    timestamps = RATE_LIMIT_STORE.get(client_ip, [])
    timestamps = [t for t in timestamps if now - t < 60]
    if len(timestamps) >= MAX_REQUESTS_PER_MINUTE:
        return False
    timestamps.append(now)
    RATE_LIMIT_STORE[client_ip] = timestamps
    return True

# Request Model untuk API Playground
class InspectRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000, description="Teks yang akan diinspeksi")

def get_html_content() -> str:
    possible_paths = [
        TEMPLATE_PATH,
        os.path.join(BASE_DIR, "..", "templates", "index.html"),
        os.path.join(os.getcwd(), "templates", "index.html"),
        "templates/index.html"
    ]
    for p in possible_paths:
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                return f.read()
    return "<h1>kado.sang.ceo</h1><p>Template index.html sedang dimuat...</p>"

@app.get("/", response_class=HTMLResponse)
async def serve_home():
    """Halaman utama portfolio kado.sang.ceo"""
    html = get_html_content()
    return HTMLResponse(content=html, status_code=200)

@app.get("/favicon.ico", include_in_schema=False)
async def serve_favicon_ico():
    ico_path = os.path.join(STATIC_DIR, "favicon.ico")
    if os.path.exists(ico_path):
        return FileResponse(ico_path, media_type="image/x-icon")
    raise HTTPException(status_code=404)

@app.get("/favicon.svg", include_in_schema=False)
async def serve_favicon_svg():
    svg_path = os.path.join(STATIC_DIR, "favicon.svg")
    if os.path.exists(svg_path):
        return FileResponse(svg_path, media_type="image/svg+xml")
    raise HTTPException(status_code=404)

@app.get("/api/status")
async def get_system_status():
    """Live health-check endpoint untuk status server dan API"""
    uptime_seconds = int(time.time() - STARTUP_TIME)
    return {
        "status": "operational",
        "service": "kadoisaceo-api",
        "environment": "production",
        "runtime": "python-fastapi",
        "version": "1.0.0",
        "uptime_seconds": uptime_seconds,
        "uptime_display": f"{uptime_seconds // 3600}h {(uptime_seconds % 3600) // 60}m {uptime_seconds % 60}s",
        "uptime_percentage": 99.98,
        "region": "iad1",
        "timestamp": int(time.time()),
        "endpoints_available": [
            "GET /",
            "GET /api/status",
            "POST /api/playground/inspect",
            "GET /api/coffee",
            "GET /docs"
        ]
    }

@app.post("/api/playground/inspect")
async def inspect_text(payload: InspectRequest, request: Request):
    """
    Endpoint interaktif sungguhan untuk diuji langsung oleh pengunjung playground.
    Menganalisis teks: word count, characters, SHA-256 checksum, slugified format, dan readability estimate.
    """
    client_ip = request.client.host if request.client else "unknown"
    if not check_rate_limit(client_ip):
        raise HTTPException(status_code=429, detail="Rate limit terlampaui (maksimal 30 request/menit). Silakan tunggu sebentar.")

    raw_text = payload.text.strip()
    words = re.findall(r"\b\w+\b", raw_text)
    word_count = len(words)
    char_count = len(raw_text)
    char_no_spaces = len(raw_text.replace(" ", ""))

    slug = re.sub(r"[^\w\s-]", "", raw_text.lower()).strip()
    slug = re.sub(r"[-\s]+", "-", slug)

    sha256_hash = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()
    reading_time_sec = round((word_count / 200) * 60, 2) if word_count > 0 else 0.0

    cleaned_for_pal = re.sub(r"[^a-zA-Z0-9]", "", raw_text.lower())
    is_palindrome = len(cleaned_for_pal) > 1 and cleaned_for_pal == cleaned_for_pal[::-1]

    return {
        "success": True,
        "query": raw_text,
        "metrics": {
            "words": word_count,
            "characters": char_count,
            "characters_excluding_spaces": char_no_spaces,
            "reading_time_seconds": reading_time_sec,
            "is_palindrome": is_palindrome
        },
        "transformations": {
            "slug": slug,
            "sha256": sha256_hash,
            "reversed": raw_text[::-1]
        },
        "meta": {
            "processed_by": "FastAPI Engine on kado.sang.ceo",
            "client_ip": client_ip,
            "timestamp": int(time.time())
        }
    }

@app.get("/api/coffee")
async def get_coffee_info():
    """Informasi paket dukungan dan donasi developer"""
    return {
        "developer": "Kado",
        "email": "kado@kadokunn.com",
        "channels": {
            "saweria": "https://saweria.co/Kadokun404",
            "trakteer": "https://trakteer.id/kadokun"
        },
        "tiers": [
            {
                "tier": "espresso",
                "title": "1 Cangkir Kopi",
                "price": 5000,
                "currency": "IDR",
                "icon": "☕"
            },
            {
                "tier": "double_latte",
                "title": "2 Cangkir Kopi Susu",
                "price": 10000,
                "currency": "IDR",
                "icon": "☕☕"
            },
            {
                "tier": "roasted_beans",
                "title": "1 Pack Biji Kopi",
                "price": 25000,
                "currency": "IDR",
                "icon": "🫘"
            }
        ]
    }
