"""
Mzigo Logistics Platform - Enterprise Edition
Author: Mzigo Logistics & Engineering
Description: High-performance backend and frontend service for empty return truck tracking.
"""

from fastapi import FastAPI, Query, Request, HTTPException, status, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
import re
import hashlib
import time
import secrets
import os
import logging
import json
from typing import List, Dict, Any, Optional

# --- Logging Configuration ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("mzigo-backend")

app = FastAPI(
    title="Mzigo Secure Enterprise Logistics API",
    version="5.0.0",
    description="Scalable freight matching ecosystem across Zambian transport corridors."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = os.environ.get("SECRET_KEY", "mzigo_enterprise_yellow_secure_key_2026")

# --- In-Memory Enterprise Storage Tables ---
USERS_DB: Dict[str, Dict[str, Any]] = {}
TOKENS_DB: Dict[str, Dict[str, Any]] = {}
TRUCKS_DB: List[Dict[str, Any]] = [
    {"id": 1, "from": "Kitwe", "to": "Lusaka", "type": "10 Ton Flatbed", "km": 362, "depart": "Today 5:30 PM", "price": 22000, "space": "8 ton", "rating": 4.9, "empty": True, "verified": True, "operator": "Copperbelt Freight Ltd"},
    {"id": 2, "from": "Ndola", "to": "Lusaka", "type": "15 Ton Tipper", "km": 321, "depart": "Today 6:00 PM", "price": 28500, "space": "12 ton", "rating": 4.8, "empty": True, "verified": True, "operator": "Zambezi Haulage"},
    {"id": 3, "from": "Kitwe", "to": "Lusaka", "type": "30 Ton Superlink", "km": 362, "depart": "Tomorrow 6:00 AM", "price": 45000, "space": "20 ton", "rating": 5.0, "empty": True, "verified": True, "operator": "Savanna Transit"},
    {"id": 4, "from": "Lusaka", "to": "Ndola", "type": "10 Ton Box", "km": 321, "depart": "Today 7:15 PM", "price": 20000, "space": "10 ton", "rating": 4.7, "empty": False, "verified": True, "operator": "Capital Cargo"},
    {"id": 5, "from": "Kitwe", "to": "Chipata", "type": "20 Ton Curtainsider", "km": 666, "depart": "Tomorrow 5:00 AM", "price": 38000, "space": "15 ton", "rating": 4.6, "empty": True, "verified": False, "operator": "East Route Logistics"},
]
ORDERS_DB: List[Dict[str, Any]] = []

# --- Security Headers Middleware ---
@app.middleware("http")
async def enterprise_security_headers(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["X-Process-Time"] = str(process_time)
    return response

# --- Cryptographic Security Utilities ---
def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 120000)
    return f"{salt}${hashed.hex()}"

def verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt, stored_hex = stored_hash.split('$')
        computed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 120000)
        return secrets.compare_digest(computed.hex(), stored_hex)
    except Exception as e:
        logger.error(f"Password verification failure: {e}")
        return False

def generate_secure_token(phone: str) -> str:
    payload = f"{phone}:{int(time.time())}:{secrets.token_hex(16)}"
    token = hashlib.sha256(f"{payload}{SECRET_KEY}".encode()).hexdigest()
    TOKENS_DB[token] = {"phone": phone, "issued_at": time.time()}
    return token

# --- Pydantic Data Validation Schemas ---
class UserRegistrationSchema(BaseModel):
    name: str = Field(..., min_length=2, max_length=60)
    phone: str
    role: str = Field(default="trader")
    password: str = Field(..., min_length=8)

    @field_validator("phone")
    @classmethod
    def sanitize_and_validate_phone(cls, v: str) -> str:
        clean_digits = re.sub(r'[^0-9]', '', v)
        if clean_digits.startswith('260'):
            clean_digits = '0' + clean_digits[3:]
        if not re.match(r'^0(96|97|95|76|77)\d{7}$', clean_digits):
            raise ValueError("Invalid Zambian mobile network format. Use valid 097/096/095/076/077 prefix.")
        return clean_digits

class UserLoginSchema(BaseModel):
    phone: str
    password: str

class TruckListingSchema(BaseModel):
    from_location: str = Field(..., min_length=2, max_length=40, alias="from")
    to_location: str = Field(..., min_length=2, max_length=40, alias="to")
    truck_type: str = Field(..., max_length=30, alias="type")
    departure: str = Field(..., max_length=40, alias="depart")
    price: float = Field(..., gt=0)
    space: str = Field(default="10 ton")

class PaymentRequest(BaseModel):
    phone: str
    amount: float
    provider: str  # 'MTN' or 'Airtel'

# --- Frontend Single Page Application Template ---
MZIGO_HTML_UI = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>Mzigo - Zambia's Premier Empty Return Fleet Network</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-primary: #0B0F17;
            --surface-dark: #131B2E;
            --surface-card: #1E293B;
            --mzigo-yellow: #FFCC00;
            --mzigo-yellow-hover: #E6B800;
            --text-main: #F8FAFC;
            --text-muted: #94A3B8;
            --border-color: #334155;
            --accent-green: #10B981;
            --accent-blue: #3B82F6;
            --danger-red: #EF4444;
            --shadow-elevation: 0 20px 40px -15px rgba(0, 0, 0, 0.5);
        }
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Plus Jakarta Sans', sans-serif; }
        body { background: var(--bg-primary); color: var(--text-main); display: flex; justify-content: center; align-items: center; min-height: 100vh; }
        
        .app-container {
            width: 100%; max-width: 480px; height: 100vh; max-height: 920px;
            background: var(--surface-dark); box-shadow: var(--shadow-elevation);
            position: relative; display: flex; flex-direction: column; overflow: hidden;
            border: 1px solid var(--border-color);
        }

        .header-bar {
            background: rgba(19, 27, 46, 0.95); backdrop-filter: blur(12px);
            padding: 16px 20px; display: flex; justify-content: space-between; align-items: center;
            position: sticky; top: 0; z-index: 50; border-bottom: 1px solid var(--border-color);
        }
        .brand-logo { font-weight: 800; font-size: 22px; display: flex; gap: 10px; align-items: center; color: var(--text-main); }
        .brand-logo i {
            width: 36px; height: 36px; background: var(--mzigo-yellow); color: var(--bg-primary);
            border-radius: 10px; display: flex; align-items: center; justify-content: center; font-style: normal; font-weight: 800;
        }
        .menu-icon-btn {
            width: 40px; height: 40px; background: var(--surface-card); border: 1px solid var(--border-color);
            border-radius: 12px; color: var(--text-main); display: flex; align-items: center; justify-content: center;
            font-size: 18px; cursor: pointer; transition: 0.2s;
        }
        .menu-icon-btn:hover { border-color: var(--mzigo-yellow); }

        .viewport-content { flex: 1; overflow-y: auto; position: relative; padding-bottom: 85px; scrollbar-width: none; }
        .viewport-content::-webkit-scrollbar { display: none; }
        .page-view { display: none; height: 100%; flex-direction: column; }
        .page-view.active { display: flex; }

        .hero-banner {
            background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
            padding: 20px; border-bottom: 1px solid var(--border-color);
        }
        .search-input-group {
            background: var(--surface-card); border: 1.5px solid var(--border-color); border-radius: 16px;
            padding: 8px 8px 8px 16px; display: flex; align-items: center; gap: 10px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.3); transition: 0.2s;
        }
        .search-input-group:focus-within { border-color: var(--mzigo-yellow); }
        .search-input-group input { flex: 1; border: none; outline: none; background: transparent; color: var(--text-main); font-size: 15px; font-weight: 500; }
        .search-input-group button {
            background: var(--mzigo-yellow); color: var(--bg-primary); border: none; border-radius: 12px;
            padding: 10px 18px; font-weight: 700; font-size: 13px; cursor: pointer; transition: 0.2s;
        }
        .search-input-group button:hover { background: var(--mzigo-yellow-hover); }

        .corridor-chips { display: flex; gap: 8px; margin-top: 14px; overflow-x: auto; scrollbar-width: none; }
        .corridor-chips::-webkit-scrollbar { display: none; }
        .chip-pill {
            background: var(--surface-card); border: 1px solid var(--border-color); color: var(--text-muted);
            border-radius: 20px; padding: 6px 14px; font-size: 12px; font-weight: 600; white-space: nowrap; cursor: pointer; transition: 0.2s;
        }
        .chip-pill.selected { background: var(--mzigo-yellow); color: var(--bg-primary); border-color: var(--mzigo-yellow); }

        .feed-wrapper { padding: 20px; flex: 1; }
        .section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; }
        .section-header h2 { font-size: 16px; font-weight: 700; }
        .section-header span { font-size: 12px; color: var(--text-muted); font-weight: 600; }

        .truck-item-card {
            background: var(--surface-card); border: 1px solid var(--border-color); border-radius: 16px;
            padding: 16px; margin-bottom: 14px; transition: 0.2s; position: relative;
        }
        .truck-item-card:hover { border-color: var(--mzigo-yellow); transform: translateY(-2px); }
        .tic-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
        .tic-route { font-weight: 700; font-size: 15px; color: var(--text-main); }
        .tic-meta { font-size: 11px; background: rgba(255,255,255,0.05); padding: 4px 8px; border-radius: 6px; color: var(--text-muted); font-weight: 600; }
        
        .tic-badges { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 12px; }
        .badge { background: rgba(255,255,255,0.06); padding: 4px 8px; border-radius: 8px; font-size: 11px; font-weight: 600; color: var(--text-muted); }
        .badge.green { background: rgba(16, 185, 129, 0.15); color: #34D399; }
        .badge.blue { background: rgba(59, 130, 246, 0.15); color: #60A5FA; }

        .tic-bottom { display: flex; justify-content: space-between; align-items: center; border-top: 1px solid var(--border-color); padding-top: 12px; }
        .tic-price { font-weight: 800; font-size: 18px; color: var(--mzigo-yellow); }
        .tic-actions { display: flex; gap: 8px; }
        
        .btn-action-sm { border: none; border-radius: 10px; padding: 8px 14px; font-weight: 700; font-size: 12px; cursor: pointer; transition: 0.2s; }
        .btn-action-sm.outline { background: transparent; border: 1px solid var(--border-color); color: var(--text-main); }
        .btn-action-sm.fill { background: var(--mzigo-yellow); color: var(--bg-primary); }
        .btn-action-sm.fill:hover { background: var(--mzigo-yellow-hover); }

        .form-container { padding: 24px 20px; display: flex; flex-direction: column; gap: 14px; flex: 1; }
        .form-input {
            width: 100%; padding: 14px; background: var(--surface-card); border: 1.5px solid var(--border-color);
            border-radius: 12px; color: var(--text-main); font-size: 14px; outline: none; transition: 0.2s;
        }
        .form-input:focus { border-color: var(--mzigo-yellow); }
        
        .btn-primary-action {
            width: 100%; padding: 14px; border-radius: 12px; font-weight: 800; font-size: 15px; cursor: pointer; border: none; text-align: center; transition: 0.2s;
        }
        .btn-primary-action.yellow { background: var(--mzigo-yellow); color: var(--bg-primary); }
        .btn-primary-action.yellow:hover { background: var(--mzigo-yellow-hover); }
        .btn-primary-action.dark { background: var(--surface-card); border: 1px solid var(--border-color); color: var(--text-main); }

        .drawer-overlay { position: absolute; inset: 0; z-index: 100; display: none; background: rgba(0,0,0,0.6); backdrop-filter: blur(4px); }
        .drawer-overlay.open { display: block; }
        .drawer-sidebar { position: absolute; left: 0; top: 0; bottom: 0; width: 80%; max-width: 300px; background: var(--surface-dark); border-right: 1px solid var(--border-color); padding: 20px; display: flex; flex-direction: column; gap: 8px; }
        .drawer-link { display: flex; gap: 12px; align-items: center; padding: 12px; border-radius: 10px; cursor: pointer; font-weight: 600; color: var(--text-muted); transition: 0.2s; }
        .drawer-link:hover { background: var(--surface-card); color: var(--text-main); }

        .bottom-nav-bar {
            position: absolute; bottom: 0; left: 0; right: 0; background: rgba(19, 27, 46, 0.95);
            backdrop-filter: blur(12px); border-top: 1px solid var(--border-color); display: flex; justify-content: space-around;
            padding: 10px 0 16px; z-index: 40;
        }
        .nav-item-tab { display: flex; flex-direction: column; align-items: center; gap: 2px; font-size: 10px; font-weight: 600; color: var(--text-muted); cursor: pointer; transition: 0.2s; }
        .nav-item-tab.active { color: var(--mzigo-yellow); }
        .nav-item-tab i { font-style: normal; font-size: 18px; }
    </style>
</head>
<body>
    <div class="app-container">
        <div class="drawer-overlay" id="navDrawer" onclick="toggleDrawerMenu()">
            <div class="drawer-sidebar" onclick="event.stopPropagation()">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
                    <div class="brand-logo"><i>M</i>Mzigo</div>
                    <button class="menu-icon-btn" onclick="toggleDrawerMenu()">✕</button>
                </div>
                <div class="drawer-link" onclick="switchPage('home');toggleDrawerMenu()">🏠 Home Feed</div>
                <div class="drawer-link" onclick="switchPage('post');toggleDrawerMenu()">🚚 Post Empty Truck</div>
                <div class="drawer-link" onclick="switchPage('orders');toggleDrawerMenu()">📦 Active Orders</div>
                <div class="drawer-link" onclick="switchPage('profile');toggleDrawerMenu()">👤 User Profile</div>
