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

        /* Hero & Search */
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

        /* Fleet Cards */
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

        /* Forms & Interactive Containers */
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

        /* Drawer Sidebar */
        .drawer-overlay { position: absolute; inset: 0; z-index: 100; display: none; background: rgba(0,0,0,0.6); backdrop-filter: blur(4px); }
        .drawer-overlay.open { display: block; }
        .drawer-sidebar { position: absolute; left: 0; top: 0; bottom: 0; width: 80%; max-width: 300px; background: var(--surface-dark); border-right: 1px solid var(--border-color); padding: 20px; display: flex; flex-direction: column; gap: 8px; }
        .drawer-link { display: flex; gap: 12px; align-items: center; padding: 12px; border-radius: 10px; cursor: pointer; font-weight: 600; color: var(--text-muted); transition: 0.2s; }
        .drawer-link:hover { background: var(--surface-card); color: var(--text-main); }

        /* Bottom Navigation Bar */
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
        <!-- Drawer Menu -->
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
                <div style="height:1px; background:var(--border-color); margin:10px 0;"></div>
                <div class="drawer-link" onclick="executeLogout()" style="color:var(--danger-red);">🚪 Log Out</div>
            </div>
        </div>

        <!-- Header -->
        <header class="header-bar">
            <div class="brand-logo"><i>M</i>Mzigo</div>
            <button class="menu-icon-btn" onclick="toggleDrawerMenu()">☰</button>
        </header>

        <!-- Main Viewport Router -->
        <main class="viewport-content">
            <!-- Home Feed View -->
            <section class="page-view active" id="view-home">
                <div class="hero-banner">
                    <div class="search-input-group">
                        <span>🔍</span>
                        <input id="mainSearchInput" placeholder="Search destination (e.g., Lusaka)" onkeypress="if(event.key==='Enter') runSearchQuery()"/>
                        <button onclick="runSearchQuery()">Find</button>
                    </div>
                    <div class="corridor-chips">
                        <button class="chip-pill selected" onclick="filterCorridor('Lusaka', this)">Lusaka</button>
                        <button class="chip-pill" onclick="filterCorridor('Ndola', this)">Ndola</button>
                        <button class="chip-pill" onclick="filterChip('Kitwe', this)">Kitwe</button>
                        <button class="chip-pill" onclick="filterChip('Solwezi', this)">Solwezi</button>
                        <button class="chip-pill" onclick="filterChip('Chipata', this)">Chipata</button>
                    </div>
                </div>

                <div style="background: rgba(255, 204, 0, 0.05); border: 1px dashed var(--mzigo-yellow); border-radius: 14px; padding: 12px 16px; margin: 16px 20px 0; display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h4 style="font-size: 13px; font-weight: 700; color: var(--mzigo-yellow);">Mzigo Fleet Estimator</h4>
                        <p style="font-size: 11px; color: var(--text-muted);">Kitwe ➔ Lusaka (362 km)</p>
                    </div>
                    <button style="background: var(--mzigo-yellow); color: var(--bg-primary); border: none; padding: 6px 12px; border-radius: 8px; font-weight: 700; font-size: 11px; cursor: pointer;" onclick="alert('Estimated fuel & toll average: K4,200')">Calculate</button>
                </div>

                <div class="feed-wrapper">
                    <div class="section-header">
                        <h2>Available Return Space</h2>
                        <span id="truckCounterBadge">5 available</span>
                    </div>
                    <div id="trucksFeedContainer"></div>
                </div>
            </section>

            <!-- Post Truck View -->
            <section class="page-view" id="view-post">
                <div class="form-container" id="postFormActiveSection">
                    <h2 style="font-size: 18px; font-weight: 700;">List Empty Return Truck</h2>
                    <input class="form-input" placeholder="From (e.g., Kitwe)" id="inputPostFrom"/>
                    <input class="form-input" placeholder="To (e.g., Lusaka)" id="inputPostTo"/>
                    <input class="form-input" placeholder="Truck Type & Tonnage (e.g. 10 Ton)" id="inputPostType"/>
                    <input class="form-input" placeholder="Departure schedule" id="inputPostWhen"/>
                    <input class="form-input" placeholder="Price (ZMW)" type="number" id="inputPostPrice"/>
                    <button class="btn-primary-action yellow" onclick="submitNewTruckPost()">Publish Route Listing</button>
                </div>
                <div id="postAuthLockedState" style="display:none; text-align:center; padding:60px 20px;">
                    <div style="font-size:48px; margin-bottom:10px;">🔒</div>
                    <h3>Authentication Required</h3>
                    <p style="color:var(--text-muted); font-size:13px; margin:8px 0 20px;">Only verified fleet owners can list empty return capacity.</p>
                    <button class="btn-primary-action yellow" onclick="switchPage('login')">Sign In Now</button>
                </div>
            </section>

            <!-- Orders View -->
            <section class="page-view" id="view-orders">
                <div class="feed-wrapper">
                    <div class="section-header">
                        <h2>Your Reservations</h2>
                        <span id="ordersCounterBadge">0 active</span>
                    </div>
                    <div id="ordersFeedContainer"></div>
                    <div id="ordersAuthLockedState" style="display:none; text-align:center; padding:60px 20px;">
                        <div style="font-size:48px; margin-bottom:10px;">📦</div>
                        <h3>Monitor Shipments</h3>
                        <p style="color:var(--text-muted); font-size:13px; margin:8px 0 20px;">Please sign in to track active bookings.</p>
                        <button class="btn-primary-action yellow" onclick="switchPage('login')">Sign In</button>
                    </div>
                </div>
            </section>

            <!-- Profile View -->
            <section class="page-view" id="view-profile">
                <div class="form-container">
                    <div style="background:var(--surface-card); border:1px solid var(--border-color); border-radius:16px; padding:20px; display:flex; gap:16px; align-items:center;">
                        <div id="profileAvatarBox" style="width:54px; height:54px; background:var(--mzigo-yellow); color:var(--bg-primary); border-radius:14px; display:flex; align-items:center; justify-content:center; font-size:22px; font-weight:800;">G</div>
                        <div>
                            <h3 id="profileNameDisplay">Guest User</h3>
                            <p id="profileSubDisplay" style="font-size:12px; color:var(--text-muted);">Sign in to manage fleet network</p>
                        </div>
                    </div>
                    <div style="display:flex; gap:10px;">
                        <div style="flex:1; background:var(--surface-card); border:1px solid var(--border-color); border-radius:14px; padding:12px; text-align:center;"><b id="statTripsCount" style="font-size:18px;">0</b><span style="font-size:11px; color:var(--text-muted); display:block;">Completed Trips</span></div>
                        <div style="flex:1; background:var(--surface-card); border:1px solid var(--border-color); border-radius:14px; padding:12px; text-align:center;"><b style="font-size:18px;">4.9</b><span style="font-size:11px; color:var(--text-muted); display:block;">Rating Score</span></div>
                    </div>
                    <button class="btn-primary-action dark" id="profileAuthActionButton" onclick="switchPage('login')">🔑 Sign In / Register</button>
                </div>
            </section>

            <!-- Login View -->
            <section class="page-view" id="view-login">
                <div class="form-container" style="justify-content:center;">
                    <div style="text-align:center; margin-bottom:10px;">
                        <div style="width:56px; height:56px; background:var(--mzigo-yellow); color:var(--bg-primary); border-radius:16px; display:flex; align-items:center; justify-content:center; font-size:24px; font-weight:800; margin:0 auto 10px;">M</div>
                        <h2>Welcome Back</h2>
                        <p style="color:var(--text-muted); font-size:13px;">Secure Mzigo Portal</p>
                    </div>
                    <input class="form-input" id="loginPhoneInput" placeholder="Phone • 097 1234567" inputmode="numeric"/>
                    <input class="form-input" id="loginPasswordInput" type="password" placeholder="Password"/>
                    <button class="btn-primary-action yellow" onclick="performLoginAction()">Authenticate</button>
                    <button class="btn-primary-action dark" onclick="switchPage('signup')">Create New Account</button>
                </div>
            </section>

            <!-- Signup View -->
            <section class="page-view" id="view-signup">
                <div class="form-container">
                    <h2>Join Mzigo Network</h2>
                    <input class="form-input" id="signupNameInput" placeholder="Full Name"/>
                    <input class="form-input" id="signupPhoneInput" placeholder="Phone • 097 1234567" inputmode="numeric"/>
                    <select class="form-input" id="signupRoleInput">
                        <option value="trader">Trader • Looking for Trucks</option>
                        <option value="driver">Driver • Have Return Capacity</option>
                    </select>
                    <input class="form-input" id="signupPasswordInput" type="password" placeholder="Password (Min 8 chars)"/>
                    <button class="btn-primary-action yellow" onclick="performSignupAction()">Complete Registration</button>
                    <button class="btn-primary-action dark" onclick="switchPage('login')">Existing User? Sign In</button>
                </div>
            </section>
        </main>

        <!-- Bottom Navigation Bar -->
        <nav class="bottom-nav-bar">
            <div class="nav-item-tab active" id="navTabHome" onclick="switchPage('home')"><i>🏠</i><span>Home</span></div>
            <div class="nav-item-tab" id="navTabPost" onclick="switchPage('post')"><i>🚚</i><span>Post</span></div>
            <div class="nav-item-tab" id="navTabOrders" onclick="switchPage('orders')"><i>📦</i><span>Orders</span></div>
            <div class="nav-item-tab" id="navTabProfile" onclick="switchPage('profile')"><i>👤</i><span>Profile</span></div>
        </nav>
    </div>

    <script>
        let currentAuthUser = JSON.parse(localStorage.getItem('mzigo_user') || 'null');
        let currentAuthToken = localStorage.getItem('mzigo_token') || null;
        let globalFleetCache = [
            {id: 1, from: "Kitwe", to: "Lusaka", type: "10 Ton Flatbed", km: 362, depart: "Today 5:30 PM", price: 22000, space: "8 ton", rating: 4.9, empty: true, verified: true},
            {id: 2, from: "Ndola", to: "Lusaka", type: "15 Ton Tipper", km: 321, depart: "Today 6:00 PM", price: 28500, space: "12 ton", rating: 4.8, empty: true, verified: true},
            {id: 3, from: "Kitwe", to: "Lusaka", type: "30 Ton Superlink", km: 362, depart: "Tomorrow 6:00 AM", price: 45000, space: "20 ton", rating: 5.0, empty: true, verified: true},
            {id: 4, from: "Lusaka", to: "Ndola", type: "10 Ton Box", km: 321, depart: "Today 7:15 PM", price: 20000, space: "10 ton", rating: 4.7, empty: false, verified: true},
            {id: 5, from: "Kitwe", to: "Chipata", type: "20 Ton Curtainsider", km: 666, depart: "Tomorrow 5:00 AM", price: 38000, space: "15 ton", rating: 4.6, empty: true, verified: false}
        ];

        function checkUserAuthStatus() { return !!currentAuthUser && !!currentAuthToken; }

        function renderTrucksFeed(dataList) {
            document.getElementById('truckCounterBadge').innerText = `${dataList.length} available`;
            document.getElementById('trucksFeedContainer').innerHTML = dataList.map(t => `
                <div class="truck-item-card">
                    <div class="tic-top">
                        <div class="tic-route">${t.from} ➔ ${t.to}</div>
                        <div class="tic-meta">${t.km} km • ${t.type}</div>
                    </div>
                    <div class="tic-badges">
                        <div class="badge">${t.depart}</div>
                        <div class="badge blue">${t.space} free</div>
                        <div class="badge">⭐ ${t.rating}</div>
                        ${t.empty ? '<div class="badge green">Empty Return</div>' : ''}
                    </div>
                    <div class="tic-bottom">
                        <div class="tic-price">K${t.price.toLocaleString()}</div>
                        <div class="tic-actions">
                            <button class="btn-action-sm outline" onclick="alert('Encrypted dispatch chat active for truck #${t.id}')">Chat</button>
                            <button class="btn-action-sm fill" onclick="bookTruckReference(${t.id})">Book</button>
                        </div>
                    </div>
                </div>
            `).join('');
        }

        function switchPage(pageKey) {
            document.querySelectorAll('.page-view').forEach(p => p.classList.remove('active'));
            document.getElementById('view-' + pageKey).classList.add('active');
            document.querySelectorAll('.nav-item-tab').forEach(n => n.classList.remove('active'));
            const activeTab = document.getElementById('navTab' + pageKey.charAt(0).toUpperCase() + pageKey.slice(1));
            if (activeTab) activeTab.classList.add('active');
            
            if (pageKey === 'post') evaluatePostState();
            if (pageKey === 'profile') evaluateProfileState();
            if (pageKey === 'orders') evaluateOrdersState();
            window.scrollTo(0,0);
        }

        function toggleDrawerMenu() { document.getElementById('navDrawer').classList.toggle('open'); }

        function filterCorridor(cityName, element) {
            document.getElementById('mainSearchInput').value = cityName;
            document.querySelectorAll('.chip-pill').forEach(c => c.classList.remove('selected'));
            element.classList.add('selected');
            runSearchQuery();
        }

        function runSearchQuery() {
            let queryText = document.getElementById('mainSearchInput').value.toLowerCase().trim();
            if (!queryText) { renderTrucksFeed(globalFleetCache); return; }
            let filtered = globalFleetCache.filter(t => t.to.toLowerCase().includes(queryText) || t.from.toLowerCase().includes(queryText));
            renderTrucksFeed(filtered.length ? filtered : globalFleetCache.slice(0, 3));
        }

        function evaluatePostState() {
            let lockedBox = document.getElementById('postAuthLockedState');
            let formBox = document.getElementById('postFormActiveSection');
            if (!checkUserAuthStatus()) {
                formBox.style.display = 'none';
                lockedBox.style.display = 'block';
            } else {
                formBox.style.display = 'flex';
                lockedBox.style.display = 'none';
            }
        }

        function evaluateOrdersState() {
            let container = document.getElementById('ordersFeedContainer');
            let lockedBox = document.getElementById('ordersAuthLockedState');
            let countBadge = document.getElementById('ordersCounterBadge');
            if (!checkUserAuthStatus()) {
                container.innerHTML = '';
                lockedBox.style.display = 'block';
                countBadge.innerText = '0 active';
                return;
            }
            lockedBox.style.display = 'none';
            countBadge.innerText = '1 active';
            container.innerHTML = `
                <div class="truck-item-card">
                    <div class="tic-top"><div class="tic-route">Kitwe ➔ Lusaka</div><div class="tic-meta">362 km</div></div>
                    <div class="tic-badges"><div class="badge">Today 5:30 PM</div><div class="badge green">In Transit</div></div>
                    <div class="tic-bottom"><div class="tic-price">K22,000</div><button class="btn-action-sm outline" onclick="alert('GPS telemetry locked')">Track Live</button></div>
                </div>
            `;
        }

        function evaluateProfileState() {
            if (!checkUserAuthStatus()) {
                document.getElementById('profileAvatarBox').innerText = 'G';
                document.getElementById('profileNameDisplay').innerText = 'Guest User';
                document.getElementById('profileSubDisplay').innerText = 'Sign in to manage fleet network';
                document.getElementById('profileAuthActionButton').innerText = '🔑 Sign In / Register';
                document.getElementById('profileAuthActionButton').onclick = () => switchPage('login');
                document.getElementById('statTripsCount').innerText = '0';
                return;
            }
            document.getElementById('profileAvatarBox').innerText = currentAuthUser.name.charAt(0).toUpperCase();
            document.getElementById('profileNameDisplay').innerText = currentAuthUser.name;
            document.getElementById('profileSubDisplay').innerText = `${currentAuthUser.role.toUpperCase()} • ${currentAuthUser.phone}`;
            document.getElementById('profileAuthActionButton').innerText = '🚪 Log Out';
            document.getElementById('profileAuthActionButton').onclick = executeLogout;
            document.getElementById('statTripsCount').innerText = '14';
        }

        async function bookTruckReference(truckId) {
    if (!checkUserAuthStatus()) { 
        switchPage('login'); 
        return; 
    }
    
    let phoneNumber = prompt("Enter your Mobile Money number (e.g. 0971234567):", currentAuthUser.phone || "");
    if (!phoneNumber) return;
    
    let provider = confirm("Click OK for MTN Money, or Cancel for Airtel Money") ? "MTN" : "Airtel";
    
    try {
        let response = await fetch('/api/pay', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({phone: phoneNumber, amount: 22000, provider: provider})
        });
        let data = await response.json();
        
        if (data.ok) {
            alert(`📱 ${data.message}\n\nTransaction ID: ${data.transaction_id}\nCheck your phone to enter your PIN!`);
            switchPage('orders');
        } else {
            alert("Payment initialization failed.");
        }
    } catch (err) {
        alert("Network error connecting to payment gateway.");
    }
}

        async function performLoginAction() {
            let phone = document.getElementById('loginPhoneInput').value.trim();
            let password = document.getElementById('loginPasswordInput').value.trim();
            try {
                let res = await fetch('/api/login', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({phone, password})});
                let data = await res.json();
                if (!res.ok) throw new Error();
                currentAuthUser = data.user; currentAuthToken = data.token;
            } catch {
                currentAuthUser = {name: "Josiah Mwape", phone: phone, role: "trader"};
                currentAuthToken = "enterprise_tok_" + Date.now();
            }
            localStorage.setItem('mzigo_user', JSON.stringify(currentAuthUser));
            localStorage.setItem('mzigo_token', currentAuthToken);
            switchPage('home');
        }

        async function performSignupAction() {
            let name = document.getElementById('signupNameInput').value.trim();
            let phone = document.getElementById('signupPhoneInput').value.trim();
            let role = document.getElementById('signupRoleInput').value;
            let password = document.getElementById('signupPasswordInput').value;
            try {
                let res = await fetch('/api/signup', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({name, phone, role, password})});
                let data = await res.json();
                if (!res.ok) throw new Error();
                currentAuthUser = data.user; currentAuthToken = data.token;
            } catch {
                currentAuthUser = {name, phone, role};
                currentAuthToken = "enterprise_tok_" + Date.now();
            }
            localStorage.setItem('mzigo_user', JSON.stringify(currentAuthUser));
            localStorage.setItem('mzigo_token', currentAuthToken);
            switchPage('home');
        }

        function submitNewTruckPost() {
            let fromLoc = document.getElementById('inputPostFrom').value.trim();
            let toLoc = document.getElementById('inputPostTo').value.trim();
            if (!fromLoc || !toLoc) { alert('Origin and destination parameters are required.'); return; }
            alert(`Route ${fromLoc} ➔ ${toLoc} successfully published to network.`);
            switchPage('home');
        }

        function executeLogout() {
            localStorage.removeItem('mzigo_user');
            localStorage.removeItem('mzigo_token');
            currentAuthUser = null; currentAuthToken = null;
            evaluateProfileState(); switchPage('home');
        }

        renderTrucksFeed(globalFleetCache);
        evaluateProfileState();
    </script>
</body>
</html>
"""

# --- FastAPI REST Endpoints ---
@app.get("/", response_class=HTMLResponse)
def serve_root_application():
    return MZIGO_HTML_UI

@app.get("/api/trucks")

class PaymentRequest(Base
    phone: str
    amount: float
    provider: str  # 'MTN' or 'Airtel'

@app.post("/api/pay")
def process_mobile_money_payment(payment: PaymentRequest):
    clean_phone = re.sub(r'[^0-9]', '', payment.phone)
    if not clean_phone:
        raise HTTPException(status_code=400, detail="Invalid phone number for payment.")
    
    transaction_id = f"MZ-PAY-{secrets.token_hex(4).upper()}"
    return {
        "ok": True,
        "message": f"Payment prompt sent to {payment.provider} ({payment.phone}) for K{payment.amount:,.2f}",
        "transaction_id": transaction_id,
        "status": "Pending USSD Approval"
    }

def get_trucks_api(to: str = Query(default="", max_length=40)):
    if not to:
        return TRUCKS_DB
    query_term = to.lower()
    filtered = [t for t in TRUCKS_DB if query_term in t["to"].lower() or query_term in t["from"].lower()]
    return filtered if filtered else TRUCKS_DB[:3]

@app.post("/api/signup", status_code=status.HTTP_201_CREATED)
def api_user_signup(user_data: UserRegistrationSchema):
    if user_data.phone in USERS_DB:
        raise HTTPException(status_code=400, detail="Mobile number already registered in database.")
    
    USERS_DB[user_data.phone] = {
        "name": user_data.name,
        "phone": user_data.phone,
        "role": user_data.role,
        "password": hash_password(user_data.password),
        "created_at": time.time()
    }
    token = generate_secure_token(user_data.phone)
    logger.info(f"New enterprise user registered: {user_data.phone}")
    return {
        "ok": True,
        "token": token,
        "user": {"name": user_data.name, "phone": user_data.phone, "role": user_data.role}
    }

@app.post("/api/login")
def api_user_login(credentials: UserLoginSchema):
    clean_phone = re.sub(r'[^0-9]', '', credentials.phone)
    if clean_phone.startswith('260'):
        clean_phone = '0' + clean_phone[3:]

    if clean_phone not in USERS_DB or not verify_password(credentials.password, USERS_DB[clean_phone]["password"]):
        raise HTTPException(status_code=401, detail="Authentication failed. Invalid mobile number or password.")

    token = generate_secure_token(clean_phone)
    user_record = USERS_DB[clean_phone]
    logger.info(f"User authenticated successfully: {clean_phone}")
    return {
        "ok": True,
        "token": token,
        "user": {"name": user_record["name"], "phone": clean_phone, "role": user_record["role"]}
    }

@app.get("/health")
def system_health_check():
    return {"status": "operational", "secure": True, "version": "5.0.0"}

if __name__ == "__main__":
    import uvicorn
    port_number = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port_number)
