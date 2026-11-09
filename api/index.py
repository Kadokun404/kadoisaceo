import os
import re
import time
import hashlib
from typing import Optional, Dict
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

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

# Startup timestamp untuk hitung uptime
STARTUP_TIME = time.time()

# Simple in-memory rate limiting (IP -> list of timestamps)
RATE_LIMIT_STORE: Dict[str, list] = {}
MAX_REQUESTS_PER_MINUTE = 30

def check_rate_limit(client_ip: str) -> bool:
    now = time.time()
    timestamps = RATE_LIMIT_STORE.get(client_ip, [])
    # Filter hanya request dalam 60 detik terakhir
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
    """Membaca file templates/index.html dengan fallback path resolver"""
    possible_paths = [
        os.path.join(os.path.dirname(__file__), "..", "templates", "index.html"),
        os.path.join(os.path.dirname(__file__), "templates", "index.html"),
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

    # Buat slug yang bersih
    slug = re.sub(r"[^\w\s-]", "", raw_text.lower()).strip()
    slug = re.sub(r"[-\s]+", "-", slug)

    # SHA-256 hash checksum
    sha256_hash = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()

    # Perkiraan waktu baca (asumsi rata-rata 200 kata per menit)
    reading_time_sec = round((word_count / 200) * 60, 2) if word_count > 0 else 0.0

    # Cek palindrome sederhana
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
        "email": "kado@sang.ceo",
        "channels": {
            "saweria": "https://saweria.co/Kadokun404",
            "trakteer": "https://trakteer.id/kadokun",
            "qris": "available_on_modal"
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
