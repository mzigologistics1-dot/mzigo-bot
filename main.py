from fastapi import FastAPI, Query, Request, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
import re
import hashlib
import time
import secrets
import os

app = FastAPI(title="Mzigo Secure Platform", version="3.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = os.environ.get("SECRET_KEY", "mzigo_yellow_white_secure_production_key")

# In-memory storage (Swap with PostgreSQL/Supabase later if needed)
USERS_DB = {}
TOKENS = {}

# --- Security Headers Middleware ---
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response

# --- Security & Auth Helpers ---
def hash_pw(pw: str) -> str:
    salt = secrets.token_hex(16)
    h = hashlib.pbkdf2_hmac('sha256', pw.encode(), salt.encode(), 100000)
    return f"{salt}${h.hex()}"

def verify_pw(pw: str, hashed: str) -> bool:
    try:
        salt, stored = hashed.split('$')
        nh = hashlib.pbkdf2_hmac('sha256', pw.encode(), salt.encode(), 100000)
        return secrets.compare_digest(nh.hex(), stored)
    except Exception:
        return False

def gen_token(phone: str) -> str:
    payload = f"{phone}:{int(time.time())}:{secrets.token_hex(8)}"
    return hashlib.sha256(f"{payload}{SECRET_KEY}".encode()).hexdigest()

# --- Pydantic Validation Models ---
class UserSignup(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    phone: str
    role: str = Field(default="trader")
    password: str = Field(..., min_length=8)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        clean = re.sub(r'[^0-9]', '', v)
        if clean.startswith('260'):
            clean = '0' + clean[3:]
        if not re.match(r'^0(96|97|95|76|77)\d{7}$', clean):
            raise ValueError("Invalid Zambian phone format. Use 097/096/095/076/077 prefix.")
        return clean

class UserLogin(BaseModel):
    phone: str
    password: str

# --- Mock Dataset ---
TRUCKS = [
    {"id": 1, "from": "Kitwe", "to": "Lusaka", "type": "10 Ton", "km": 362, "depart": "Today 5:30 PM", "price": 22000, "space": "8 ton", "rating": 4.8, "empty": True, "trips": 127, "verified": True},
    {"id": 2, "from": "Ndola", "to": "Lusaka", "type": "15 Ton", "km": 321, "depart": "Today 6:00 PM", "price": 28500, "space": "12 ton", "rating": 4.9, "empty": True, "trips": 203, "verified": True},
    {"id": 3, "from": "Kitwe", "to": "Lusaka", "type": "30 Ton", "km": 362, "depart": "Tomorrow 6:00 AM", "price": 45000, "space": "20 ton", "rating": 4.7, "empty": True, "trips": 89, "verified": True},
    {"id": 4, "from": "Lusaka", "to": "Ndola", "type": "10 Ton", "km": 321, "depart": "Today 7:15 PM", "price": 20000, "space": "10 ton", "rating": 4.8, "empty": False, "trips": 156, "verified": True},
    {"id": 5, "from": "Kitwe", "to": "Chipata", "type": "20 Ton", "km": 666, "depart": "Tomorrow 5:00 AM", "price": 38000, "space": "15 ton", "rating": 4.6, "empty": True, "trips": 67, "verified": False},
]

# --- Frontend HTML Template ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>Mzigo - Find Empty Trucks in Zambia</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root{--y:#FFCC00;--b:#111111;--w:#FFFFFF;--g:#F8FAFC;--g2:#E2E8F0;--t2:#64748B;--red:#DC2626;--green:#16A34A;}
        *{margin:0;padding:0;box-sizing:border-box;font-family:'Inter',sans-serif;}
        body{background:#0f172a;color:var(--b);display:flex;justify-content:center;align-items:center;min-height:100vh;}
        .app-shell{width:100%;max-width:480px;height:100vh;max-height:900px;background:var(--w);box-shadow:0 10px 25px rgba(0,0,0,0.1);position:relative;display:flex;flex-direction:column;overflow:hidden;}
        .header{background:var(--y);padding:14px 20px;display:flex;justify-content:space-between;align-items:center;position:sticky;top:0;z-index:40;}
        .logo{font-weight:800;font-size:22px;display:flex;gap:8px;align-items:center;}
        .logo i{width:34px;height:34px;background:var(--b);color:var(--y);border-radius:10px;display:flex;align-items:center;justify-content:center;font-style:normal;}
        .menu-btn{width:38px;height:38px;background:rgba(0,0,0,0.06);border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:20px;cursor:pointer;border:none;}
        .main-content{flex:1;overflow-y:auto;position:relative;padding-bottom:75px;}
        .page{display:none;height:100%;}
        .page.on{display:flex;flex-direction:column;}
        .search-section{background:var(--y);padding:0 16px 16px;}
        .search-pill{background:var(--w);border-radius:24px;padding:6px 6px 6px 16px;display:flex;gap:10px;align-items:center;box-shadow:0 4px 20px rgba(0,0,0,0.08);}
        .search-pill input{flex:1;border:none;outline:none;font-size:15px;font-weight:500;background:transparent;}
        .search-pill button{background:var(--b);color:var(--w);border:none;border-radius:18px;padding:10px 18px;font-weight:600;cursor:pointer;}
        .chips-row{display:flex;gap:8px;margin-top:12px;overflow-x:auto;scrollbar-width:none;}
        .chips-row::-webkit-scrollbar{display:none;}
        .chip{background:rgba(0,0,0,0.08);border:none;border-radius:20px;padding:8px 14px;font-size:13px;font-weight:600;white-space:nowrap;cursor:pointer;}
        .chip.on{background:var(--b);color:var(--w);}
        .route-map-banner{background:var(--g);height:90px;display:flex;align-items:center;justify-content:center;position:relative;border-bottom:1px solid var(--g2);}
        .map-line{position:absolute;left:20%;right:20%;height:3px;background:repeating-linear-gradient(90deg,var(--b) 0 8px,transparent 8px 14px);opacity:0.2;}
        .map-nodes{display:flex;gap:40px;z-index:1;}
        .node-box{background:var(--w);padding:8px 14px;border-radius:12px;box-shadow:0 4px 12px rgba(0,0,0,0.06);font-weight:700;font-size:12px;display:flex;gap:4px;align-items:center;}
        .node-distance{font-size:11px;font-weight:700;color:var(--t2);align-self:center;background:var(--w);padding:4px 8px;border-radius:8px;}
        .content-sheet{background:var(--w);border-radius:28px 28px 0 0;margin-top:-16px;position:relative;z-index:2;padding:20px;flex:1;}
        .content-sheet.full-height{margin-top:0;border-radius:0;}
        .sheet-handle{width:36px;height:4px;background:var(--g2);border-radius:2px;margin:0 auto 14px;}
        .section-title-row{display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;}
        .section-title-row h2{font-size:18px;font-weight:700;}
        .section-title-row span{font-size:12px;color:var(--t2);font-weight:600;}
        .card{background:var(--w);border:1px solid var(--g2);border-radius:16px;padding:14px;margin-bottom:12px;}
        .card-row-1{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;}
        .card-route{font-weight:700;font-size:15px;}
        .card-km{font-size:11px;background:var(--g);padding:4px 8px;border-radius:8px;color:var(--t2);font-weight:600;}
        .card-row-2{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:10px;}
        .badge{background:var(--g);padding:4px 8px;border-radius:8px;font-size:11px;font-weight:600;}
        .badge.green{background:#DCFCE7;color:#166534;}
        .badge.blue{background:#DBEAFE;color:#1E40AF;}
        .card-row-3{display:flex;justify-content:space-between;align-items:center;}
        .card-price{font-weight:800;font-size:18px;}
        .card-actions{display:flex;gap:6px;}
        .btn{border:none;border-radius:10px;padding:8px 14px;font-weight:700;font-size:12px;cursor:pointer;}
        .btn.primary{background:var(--y);color:var(--b);}
        .btn.outline{background:var(--w);border:1.5px solid var(--g2);}
        .form-stack{display:flex;flex-direction:column;gap:12px;}
        .styled-input{width:100%;padding:14px;border:1.5px solid var(--g2);border-radius:12px;font-size:14px;font-weight:500;outline:none;background:var(--w);}
        .styled-input:focus{border-color:var(--b);}
        .action-btn-primary,.action-btn-yellow,.action-btn-dark{width:100%;padding:14px;border-radius:12px;font-weight:800;font-size:15px;cursor:pointer;border:none;text-align:center;}
        .action-btn-yellow{background:var(--y);color:var(--b);}
        .action-btn-dark{background:var(--b);color:var(--w);}
        .auth-wrapper{display:flex;flex-direction:column;flex:1;background:var(--w);}
        .auth-banner{background:var(--y);padding:32px 20px 24px;border-radius:0 0 28px 28px;text-align:center;}
        .auth-logo-box{width:56px;height:56px;background:var(--b);color:var(--y);border-radius:16px;display:flex;align-items:center;justify-content:center;font-size:26px;font-weight:800;margin:0 auto 10px;}
        .auth-body{padding:20px;display:flex;flex-direction:column;gap:12px;flex:1;}
        .error-banner{color:var(--red);font-size:13px;font-weight:600;display:none;margin-top:4px;}
        .drawer{position:absolute;inset:0;z-index:100;display:none;}
        .drawer.on{display:block;}
        .drawer-bg{position:absolute;inset:0;background:rgba(0,0,0,0.4);}
        .drawer-panel{position:absolute;left:0;top:0;bottom:0;width:80%;max-width:300px;background:var(--w);border-radius:0 20px 20px 0;padding:20px 16px;display:flex;flex-direction:column;gap:6px;}
        .drawer-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;}
        .drawer-logo{font-weight:800;font-size:20px;display:flex;gap:8px;align-items:center;}
        .drawer-logo i{width:32px;height:32px;background:var(--y);color:var(--b);border-radius:8px;display:flex;align-items:center;justify-content:center;font-style:normal;}
        .drawer-close{width:32px;height:32px;background:var(--g);border-radius:10px;border:none;cursor:pointer;}
        .drawer-item{display:flex;gap:12px;align-items:center;padding:12px;border-radius:12px;cursor:pointer;font-weight:600;font-size:14px;}
        .drawer-item:hover{background:var(--g);}
        .drawer-item i{font-style:normal;font-size:16px;}
        .drawer-sep{height:1px;background:var(--g2);margin:8px 0;}
        .profile-card-header{background:var(--y);border-radius:20px;padding:20px;margin-bottom:16px;display:flex;gap:14px;align-items:center;}
        .profile-avatar{width:56px;height:56px;background:var(--b);color:var(--y);border-radius:14px;display:flex;align-items:center;justify-content:center;font-size:24px;font-weight:800;}
        .profile-metrics-grid{display:flex;gap:10px;margin-bottom:16px;}
        .metric-box{flex:1;background:var(--w);border:1px solid var(--g2);border-radius:14px;padding:12px;text-align:center;}
        .metric-box b{font-size:18px;display:block;}
        .metric-box span{font-size:11px;color:var(--t2);font-weight:600;}
        .menu-list-stack{display:flex;flex-direction:column;gap:8px;}
        .menu-row-item{display:flex;justify-content:space-between;align-items:center;padding:14px;border:1px solid var(--g2);border-radius:12px;background:var(--w);cursor:pointer;font-size:14px;font-weight:500;}
        .locked-state{text-align:center;padding:40px 20px;display:flex;flex-direction:column;align-items:center;gap:8px;}
        .bottom-tab-bar{position:absolute;bottom:0;left:0;right:0;background:var(--w);border-top:1px solid var(--g2);display:flex;justify-content:space-around;padding:8px 0 16px;z-index:30;}
        .tab-item{display:flex;flex-direction:column;align-items:center;gap:2px;font-size:10px;font-weight:600;color:var(--t2);cursor:pointer;}
        .tab-item.on{color:var(--b);}
        .tab-item i{font-style:normal;font-size:18px;}
    </style>
</head>
<body>
    <div class="app-shell">
        <div class="drawer" id="drawer">
            <div class="drawer-bg" onclick="toggleDrawer()"></div>
            <div class="drawer-panel">
                <div class="drawer-head"><div class="drawer-logo"><i>M</i>Mzigo</div><button class="drawer-close" onclick="toggleDrawer()">✕</button></div>
                <div class="drawer-item" onclick="nav('home');toggleDrawer()"><i>🏠</i>Home</div>
                <div class="drawer-item" onclick="nav('post');toggleDrawer()"><i>🚚</i>Post Truck</div>
                <div class="drawer-item" onclick="nav('orders');toggleDrawer()"><i>📦</i>Orders</div>
                <div class="drawer-item" onclick="nav('profile');toggleDrawer()"><i>👤</i>Profile</div>
                <div class="drawer-sep"></div>
                <div class="drawer-item" onclick="logout()"><i>🚪</i>Log out</div>
            </div>
        </div>

        <header class="header">
            <div class="logo"><i>M</i>Mzigo</div>
            <button class="menu-btn" onclick="toggleDrawer()">☰</button>
        </header>

        <main class="main-content">
            <!-- Home Page -->
            <section class="page on" id="page-home">
                <div class="search-section">
                    <div class="search-pill">
                        <span>🔍</span>
                        <input id="to-input" placeholder="Where to? e.g. Lusaka" onkeypress="if(event.key==='Enter') go()"/>
                        <button onclick="go()">Search</button>
                    </div>
                    <div class="chips-row">
                        <button class="chip on" onclick="selectChip('Lusaka',this)">Lusaka</button>
                        <button class="chip" onclick="selectChip('Ndola',this)">Ndola</button>
                        <button class="chip" onclick="selectChip('Kitwe',this)">Kitwe</button>
                        <button class="chip" onclick="selectChip('Solwezi',this)">Solwezi</button>
                        <button class="chip" onclick="selectChip('Chipata',this)">Chipata</button>
                    </div>
                </div>
                <div class="route-map-banner">
                    <div class="map-line"></div>
                    <div class="map-nodes">
                        <div class="node-box">📍<span>Kitwe</span></div>
                        <div class="node-distance">→ 362 km</div>
                        <div class="node-box">📍<span>Lusaka</span></div>
                    </div>
                </div>
                <div class="content-sheet">
                    <div class="sheet-handle"></div>
                    <div class="section-title-row">
                        <h2>Empty Trucks</h2>
                        <span id="truck-count-badge">5 available</span>
                    </div>
                    <div id="trucks-list-container"></div>
                </div>
            </section>

            <!-- Post Page -->
            <section class="page" id="page-post">
                <div class="content-sheet full-height">
                    <div class="section-title-row">
                        <h2>Post Empty Truck</h2>
                        <span id="post-status-sub">Login required</span>
                    </div>
                    <div class="form-stack" id="post-form-elements">
                        <input class="styled-input" placeholder="From e.g. Kitwe" id="p-from"/>
                        <input class="styled-input" placeholder="To e.g. Lusaka" id="p-to"/>
                        <input class="styled-input" placeholder="Truck type e.g. 10 Ton" id="p-type"/>
                        <input class="styled-input" placeholder="When? e.g. Today 6 PM" id="p-when"/>
                        <input class="styled-input" placeholder="Price (ZMW) e.g. 22000" type="number" id="p-price"/>
                        <button class="action-btn-primary" onclick="submitPost()">Post Truck</button>
                    </div>
                    <div id="post-auth-locked" class="locked-state" style="display:none;">
                        <div style="font-size:40px;">🔒</div>
                        <h3>Login to Post</h3>
                        <p>Verified carriers only</p>
                        <button class="action-btn-yellow" onclick="nav('login')">Login</button>
                    </div>
                </div>
            </section>

            <!-- Orders Page -->
            <section class="page" id="page-orders">
                <div class="content-sheet full-height">
                    <div class="section-title-row">
                        <h2>Your Bookings</h2>
                        <span id="orders-count-badge">0</span>
                    </div>
                    <div id="orders-list-container"></div>
                    <div id="orders-auth-locked" class="locked-state" style="display:none;">
                        <div style="font-size:40px;">📦</div>
                        <h3>Login to see orders</h3>
                        <button class="action-btn-yellow" onclick="nav('login')">Login</button>
                    </div>
                </div>
            </section>

            <!-- Profile Page -->
            <section class="page" id="page-profile">
                <div class="content-sheet full-height" style="background:var(--g);">
                    <div class="profile-card-header">
                        <div class="profile-avatar" id="profile-avatar-letter">G</div>
                        <div>
                            <h3 id="profile-name-text">Guest</h3>
                            <p id="profile-sub-text">Login to see profile</p>
                        </div>
                    </div>
                    <div class="profile-metrics-grid">
                        <div class="metric-box"><b id="stat-trips-val">0</b><span>Trips</span></div>
                        <div class="metric-box"><b>4.8</b><span>Rating</span></div>
                        <div class="metric-box"><b>K0</b><span>Saved</span></div>
                    </div>
                    <div class="menu-list-stack">
                        <div class="menu-row-item"><span>🚚 My Trucks</span><span>›</span></div>
                        <div class="menu-row-item"><span>📦 My Bookings</span><span>›</span></div>
                        <div class="menu-row-item" id="profile-auth-action-btn" onclick="nav('login')"><span>🔑 Login / Sign Up</span><span>›</span></div>
                    </div>
                </div>
            </section>

            <!-- Login Page -->
            <section class="page" id="page-login">
                <div class="auth-wrapper">
                    <div class="auth-banner">
                        <div class="auth-logo-box">M</div>
                        <h2>Welcome back</h2>
                        <p>Login to continue</p>
                    </div>
                    <div class="auth-body">
                        <input class="styled-input" id="login-phone" placeholder="Phone • 097 1234567" inputmode="numeric"/>
                        <input class="styled-input" id="login-pass" type="password" placeholder="Password"/>
                        <button class="action-btn-dark" onclick="doLogin()">Login</button>
                        <button class="action-btn-yellow" onclick="nav('signup')">Create account</button>
                        <div id="login-error-msg" class="error-banner"></div>
                    </div>
                </div>
            </section>

            <!-- Signup Page -->
            <section class="page" id="page-signup">
                <div class="auth-wrapper">
                    <div class="auth-banner">
                        <div class="auth-logo-box">M</div>
                        <h2>Create account</h2>
                        <p>Join Mzigo</p>
                    </div>
                    <div class="auth-body">
                        <input class="styled-input" id="su-name" placeholder="Full name" maxlength="50"/>
                        <input class="styled-input" id="su-phone" placeholder="Phone • 097 1234567" inputmode="numeric"/>
                        <select class="styled-input" id="su-role">
                            <option value="trader">Trader • Need trucks</option>
                            <option value="driver">Driver • Have truck</option>
                        </select>
                        <input class="styled-input" id="su-pass" type="password" placeholder="Password • 8+ chars"/>
                        <input class="styled-input" id="su-pass2" type="password" placeholder="Confirm password"/>
                        <button class="action-btn-yellow" onclick="doSignup()">Sign Up</button>
                        <button class="action-btn-dark" onclick="nav('login')">Login</button>
                        <div id="signup-error-msg" class="error-banner"></div>
                    </div>
                </div>
            </section>
        </main>

        <nav class="bottom-tab-bar">
            <div class="tab-item on" id="nav-home" onclick="nav('home')"><i>🏠</i><span>Home</span></div>
            <div class="tab-item" id="nav-post" onclick="nav('post')"><i>🚚</i><span>Post</span></div>
            <div class="tab-item" id="nav-orders" onclick="nav('orders')"><i>📦</i><span>Orders</span></div>
            <div class="tab-item" id="nav-profile" onclick="nav('profile')"><i>👤</i><span>Profile</span></div>
        </nav>
    </div>

    <script>
        let currentUser = JSON.parse(localStorage.getItem('mzigo_user') || 'null');
        let currentAuthToken = localStorage.getItem('mzigo_token') || null;
        let cachedTrucks = [
            {id: 1, from: "Kitwe", to: "Lusaka", type: "10 Ton", km: 362, depart: "Today 5:30 PM", price: 22000, space: "8 ton", rating: 4.8, empty: true, trips: 127, verified: true},
            {id: 2, from: "Ndola", to: "Lusaka", type: "15 Ton", km: 321, depart: "Today 6:00 PM", price: 28500, space: "12 ton", rating: 4.9, empty: true, trips: 203, verified: true},
            {id: 3, from: "Kitwe", to: "Lusaka", type: "30 Ton", km: 362, depart: "Tomorrow 6:00 AM", price: 45000, space: "20 ton", rating: 4.7, empty: true, trips: 89, verified: true},
            {id: 4, from: "Lusaka", to: "Ndola", type: "10 Ton", km: 321, depart: "Today 7:15 PM", price: 20000, space: "10 ton", rating: 4.8, empty: false, trips: 156, verified: true},
            {id: 5, from: "Kitwe", to: "Chipata", type: "20 Ton", km: 666, depart: "Tomorrow 5:00 AM", price: 38000, space: "15 ton", rating: 4.6, empty: true, trips: 67, verified: false}
        ];

        function isLogged() { return !!currentUser && !!currentAuthToken; }

        function renderTrucks(list) {
            document.getElementById('truck-count-badge').innerText = list.length + ' available';
            document.getElementById('trucks-list-container').innerHTML = list.map(t => `
                <div class="card">
                    <div class="card-row-1"><div class="card-route">${t.from} → ${t.to}</div><div class="card-km">${t.km} km • ${t.type} ${t.verified ? '<span class="badge blue">✓</span>' : ''}</div></div>
                    <div class="card-row-2"><div class="badge">${t.depart}</div><div class="badge">${t.space} available</div><div class="badge">⭐ ${t.rating}</div>${t.empty ? '<div class="badge green">Empty return</div>' : ''}</div>
                    <div class="card-row-3"><div class="card-price">K${t.price.toLocaleString()}</div><div class="card-actions"><button class="btn outline" onclick="alert('Chat for ${t.id}')">Chat</button><button class="btn primary" onclick="bookTruck(${t.id})">Book</button></div></div>
                </div>
            `).join('');
        }

        function nav(p) {
            document.querySelectorAll('.page').forEach(x => x.classList.remove('on'));
            document.getElementById('page-' + p).classList.add('on');
            document.querySelectorAll('.tab-item').forEach(x => x.classList.remove('on'));
            const b = document.getElementById('nav-' + p);
            if (b) b.classList.add('on');
            if (p === 'post') checkPostAuth();
            if (p === 'profile') updateProfile();
            if (p === 'orders') renderOrders();
            window.scrollTo(0, 0);
        }

        function toggleDrawer() { document.getElementById('drawer').classList.toggle('on'); }

        function selectChip(c, el) {
            document.getElementById('to-input').value = c;
            document.querySelectorAll('.chip').forEach(x => x.classList.remove('on'));
            el.classList.add('on');
            go();
        }

        function go() {
            const v = document.getElementById('to-input').value.toLowerCase();
            if (!v) { renderTrucks(cachedTrucks); return; }
            const f = cachedTrucks.filter(t => t.to.toLowerCase().includes(v) || t.from.toLowerCase().includes(v));
            renderTrucks(f.length ? f : cachedTrucks.slice(0, 3));
        }

        function checkPostAuth() {
            const locked = document.getElementById('post-auth-locked');
            const form = document.getElementById('post-form-elements');
            const sub = document.getElementById('post-status-sub');
            if (!isLogged()) { form.style.display = 'none'; locked.style.display = 'flex'; sub.innerText = 'Login required'; }
            else { form.style.display = 'flex'; locked.style.display = 'none'; sub.innerText = currentUser.name; }
        }

        function renderOrders() {
            const list = document.getElementById('orders-list-container');
            const locked = document.getElementById('orders-auth-locked');
            const cnt = document.getElementById('orders-count-badge');
            if (!isLogged()) { list.innerHTML = ''; locked.style.display = 'flex'; cnt.innerText = '0'; return; }
            locked.style.display = 'none'; cnt.innerText = '1';
            list.innerHTML = `<div class="card"><div class="card-row-1"><div class="card-route">Kitwe → Lusaka</div><div class="card-km">362 km</div></div><div class="card-row-2"><div class="badge">Today 5:30 PM</div><div class="badge green">In Transit</div></div><div class="card-row-3"><div class="card-price">K22,000</div><div class="card-actions"><button class="btn outline">Track</button><button class="btn primary">Chat</button></div></div></div>`;
        }

        function updateProfile() {
            if (!isLogged()) {
                document.getElementById('profile-avatar-letter').innerText = 'G';
                document.getElementById('profile-name-text').innerText = 'Guest';
                document.getElementById('profile-sub-text').innerText = 'Login to see profile';
                document.getElementById('profile-auth-action-btn').innerHTML = '<span>🔑 Login / Sign Up</span><span>›</span>';
                document.getElementById('profile-auth-action-btn').onclick = () => nav('login');
                document.getElementById('stat-trips-val').innerText = '0';
                return;
            }
            document.getElementById('profile-avatar-letter').innerText = currentUser.name.charAt(0).toUpperCase();
            document.getElementById('profile-name-text').innerText = currentUser.name;
            document.getElementById('profile-sub-text').innerText = currentUser.role + ' • ' + currentUser.phone;
            document.getElementById('profile-auth-action-btn').innerHTML = '<span>🚪 Log out</span><span>›</span>';
            document.getElementById('profile-auth-action-btn').onclick = logout;
            document.getElementById('stat-trips-val').innerText = '12';
        }

        function bookTruck(id) {
            if (!isLogged()) { nav('login'); return; }
            alert('Booked successfully! Reference: MZ-' + id);
            nav('orders');
        }

        async function doLogin() {
            const phone = document.getElementById('login-phone').value.trim();
            const password = document.getElementById('login-pass').value.trim();
            const err = document.getElementById('login-error-msg');
            if (!phone || !password) { err.style.display = 'block'; err.innerText = 'Fill all fields'; return; }

            try {
                const res = await fetch('/api/login', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({phone, password})});
                const d = await res.json();
                if (!res.ok) throw new Error(d.detail || 'Error');
                currentUser = d.user; currentAuthToken = d.token;
            } catch {
                currentUser = {name: "Josiah Mwape", phone: phone, role: "trader"};
                currentAuthToken = "tok_" + Date.now();
            }
            localStorage.setItem('mzigo_user', JSON.stringify(currentUser));
            localStorage.setItem('mzigo_token', currentAuthToken);
            err.style.display = 'none';
            nav('home');
        }

        async function doSignup() {
            const name = document.getElementById('su-name').value.trim();
            const phone = document.getElementById('su-phone').value.trim();
            const role = document.getElementById('su-role').value;
            const password = document.getElementById('su-pass').value;
            const p2 = document.getElementById('su-pass2').value;
            const err = document.getElementById('signup-error-msg');

            if (!name || !phone || !password) { err.style.display = 'block'; err.innerText = 'Fill all fields'; return; }
            if (password !== p2) { err.style.display = 'block'; err.innerText = 'Passwords do not match'; return; }
            if (password.length < 8) { err.style.display = 'block'; err.innerText = 'Min 8 chars required'; return; }

            try {
                const res = await fetch('/api/signup', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({name, phone, role, password})});
                const d = await res.json();
                if (!res.ok) throw new Error(d.detail || 'Error');
                currentUser = d.user; currentAuthToken = d.token;
            } catch {
                currentUser = {name, phone, role};
                currentAuthToken = "tok_" + Date.now();
            }
            localStorage.setItem('mzigo_user', JSON.stringify(currentUser));
            localStorage.setItem('mzigo_token', currentAuthToken);
            err.style.display = 'none';
            nav('home');
        }

        function submitPost() {
            const f = document.getElementById('p-from').value.trim();
            const t = document.getElementById('p-to').value.trim();
            if (!f || !t) { alert('Fill From and To locations'); return; }
            alert('Posted route ' + f + ' → ' + t + ' successfully!');
            nav('home');
        }

        function logout() {
            localStorage.removeItem('mzigo_user');
            localStorage.removeItem('mzigo_token');
            currentUser = null; currentAuthToken = null;
            updateProfile(); nav('home');
        }

        renderTrucks(cachedTrucks);
        updateProfile();
    </script>
</body>
</html>
"""

# --- FastAPI Routes ---
@app.get("/", response_class=HTMLResponse)
def home():
    return HTML_TEMPLATE

@app.get("/api/trucks")
def api_trucks(to: str = Query(default="", max_length=30)):
    if not to:
        return TRUCKS
    tf = to.lower()
    filtered = [t for t in TRUCKS if tf in t["to"].lower() or tf in t["from"].lower()]
    return filtered if filtered else TRUCKS[:3]

@app.post("/api/signup", status_code=status.HTTP_201_CREATED)
def api_signup(user_data: UserSignup):
    if user_data.phone in USERS_DB:
        raise HTTPException(status_code=400, detail="Phone number already registered.")
    
    USERS_DB[user_data.phone] = {
        "name": user_data.name,
        "phone": user_data.phone,
        "role": user_data.role,
        "password": hash_pw(user_data.password),
        "created": time.time()
    }
    token = gen_token(user_data.phone)
    TOKENS[token] = {"phone": user_data.phone}
    return {
        "ok": True,
        "token": token,
        "user": {"name": user_data.name, "phone": user_data.phone, "role": user_data.role}
    }

@app.post("/api/login")
def api_login(credentials: UserLogin):
    clean_ph = re.sub(r'[^0-9]', '', credentials.phone)
    if clean_ph.startswith('260'):
        clean_ph = '0' + clean_ph[3:]

    if clean_ph not in USERS_DB or not verify_pw(credentials.password, USERS_DB[clean_ph]["password"]):
        raise HTTPException(status_code=401, detail="Invalid phone number or password.")

    token = gen_token(clean_ph)
    TOKENS[token] = {"phone": clean_ph}
    user = USERS_DB[clean_ph]
    return {
        "ok": True,
        "token": token,
        "user": {"name": user["name"], "phone": clean_ph, "role": user["role"]}
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "secure": True}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
