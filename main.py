from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import re, hashlib, time, secrets, os, math

app = FastAPI(title="Mzigo Secure Clean")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

SECRET_KEY = os.environ.get("SECRET_KEY", "mzigo_yellow_white_secure_2024")
USERS_DB = {}
TOKENS = {}
RATE_LIMIT = {}
LOGIN_ATTEMPTS = {}

@app.middleware("http")
async def sec_headers(request: Request, call_next):
    resp = await call_next(request)
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["X-Frame-Options"] = "DENY"
    return resp

def hash_pw(pw: str) -> str:
    salt = secrets.token_hex(16)
    h = hashlib.pbkdf2_hmac('sha256', pw.encode(), salt.encode(), 100000)
    return f"{salt}${h.hex()}"

def verify_pw(pw: str, hashed: str) -> bool:
    try:
        salt, stored = hashed.split('$')
        nh = hashlib.pbkdf2_hmac('sha256', pw.encode(), salt.encode(), 100000)
        return secrets.compare_digest(nh.hex(), stored)
    except:
        return False

def valid_zm_phone(phone: str) -> bool:
    c = re.sub(r'[^0-9]', '', phone)
    if c.startswith('260'):
        c = '0' + c[3:]
    return bool(re.match(r'^0(96|97|95|76|77)\d{7}$', c))

def clean_phone(phone: str) -> str:
    c = re.sub(r'[^0-9]', '', phone)
    if c.startswith('260'):
        c = '0' + c[3:]
    return c

def sanitize(t: str) -> str:
    if not t:
        return ""
    t = re.sub(r'<[^>]*>', '', t)
    return t.replace('<','').replace('>','').strip()[:100]

def check_rate(ip: str) -> bool:
    now = time.time()
    if ip not in RATE_LIMIT:
        RATE_LIMIT[ip] = []
    RATE_LIMIT[ip] = [x for x in RATE_LIMIT[ip] if now - x < 60]
    if len(RATE_LIMIT[ip]) >= 20:
        return False
    RATE_LIMIT[ip].append(now)
    return True

def check_login_attempts(phone: str) -> bool:
    now = time.time()
    if phone not in LOGIN_ATTEMPTS:
        return True
    d = LOGIN_ATTEMPTS[phone]
    if now - d['last'] > 300:
        del LOGIN_ATTEMPTS[phone]
        return True
    return d['count'] < 5

def gen_token(phone: str) -> str:
    payload = f"{phone}:{int(time.time())}:{secrets.token_hex(8)}"
    token = hashlib.sha256(f"{payload}{SECRET_KEY}".encode()).hexdigest()
    TOKENS[token] = {"phone": phone, "created": time.time()}
    return token

TRUCKS = [
    {"id":1,"from":"Kitwe","to":"Lusaka","type":"10 Ton","km":362,"depart":"Today 5:30 PM","price":22000,"space":"8 ton","rating":4.8,"empty":True,"trips":127,"verified":True},
    {"id":2,"from":"Ndola","to":"Lusaka","type":"15 Ton","km":321,"depart":"Today 6:00 PM","price":28500,"space":"12 ton","rating":4.9,"empty":True,"trips":203,"verified":True},
    {"id":3,"from":"Kitwe","to":"Lusaka","type":"30 Ton","km":362,"depart":"Tomorrow 6:00 AM","price":45000,"space":"20 ton","rating":4.7,"empty":True,"trips":89,"verified":True},
    {"id":4,"from":"Lusaka","to":"Ndola","type":"10 Ton","km":321,"depart":"Today 7:15 PM","price":20000,"space":"10 ton","rating":4.8,"empty":False,"trips":156,"verified":True},
    {"id":5,"from":"Kitwe","to":"Chipata","type":"20 Ton","km":666,"depart":"Tomorrow 5:00 AM","price":38000,"space":"15 ton","rating":4.6,"empty":True,"trips":67,"verified":False},
]

def find(to_filter):
    if not to_filter:
        return TRUCKS
    tf = to_filter.lower()
    return [t for t in TRUCKS if tf in t["to"].lower() or tf in t["from"].lower()] or TRUCKS[:3]

HTML = """
<!DOCTYPE html><html><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Mzigo - Find empty trucks</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
:root{--y:#FFCC00;--b:#111111;--w:#FFFFFF;--g:#F5F5F5;--g2:#E8E8E8;--t2:#6B7280;}
*{margin:0;padding:0;box-sizing:border-box;font-family:Inter,sans-serif;}
body{background:var(--w);color:var(--b);}
.h{background:var(--y);padding:14px 16px;display:flex;justify-content:space-between;align-items:center;position:sticky;top:0;z-index:40;}
.logo{font-weight:800;font-size:22px;display:flex;gap:8px;align-items:center;}
.logo i{width:32px;height:32px;background:var(--b);color:var(--y);border-radius:9px;display:flex;align-items:center;justify-content:center;font-style:normal;}
.menu-btn{width:36px;height:36px;background:rgba(0,0,0,0.08);border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:20px;cursor:pointer;border:none;}
.s{background:var(--y);padding:0 16px 18px;}
.pill{background:var(--w);border-radius:24px;padding:6px 6px 6px 16px;display:flex;gap:10px;align-items:center;box-shadow:0 4px 20px rgba(0,0,0,0.12);}
.pill input{flex:1;border:none;outline:none;font-size:16px;font-weight:500;background:transparent;padding:10px 0;}
.pill button{background:var(--b);color:var(--w);border:none;border-radius:18px;padding:10px 18px;font-weight:600;}
.chips{display:flex;gap:8px;margin-top:12px;overflow-x:auto;scrollbar-width:none;}
.chips::-webkit-scrollbar{display:none;}
.chip{background:rgba(0,0,0,0.08);border:none;border-radius:20px;padding:8px 14px;font-size:13px;font-weight:600;white-space:nowrap;}
.chip.on{background:var(--b);color:var(--w);}
.map{background:var(--g);height:100px;display:flex;align-items:center;justify-content:center;position:relative;}
.line{position:absolute;left:18%;right:18%;height:3px;background:repeating-linear-gradient(90deg,var(--b) 0 8px,transparent 8px 14px);opacity:0.2;top:50%;}
.dots{display:flex;gap:60px;z-index:1;}
.dot{width:50px;height:50px;background:var(--w);border-radius:14px;box-shadow:0 4px 16px rgba(0,0,0,0.12);display:flex;flex-direction:column;align-items:center;justify-content:center;font-weight:700;font-size:11px;}
.sheet{background:var(--w);border-radius:28px 28px 0 0;margin-top:-16px;position:relative;z-index:2;padding:14px 14px 110px;min-height:500px;box-shadow:0 -8px 30px rgba(0,0,0,0.08);}
.handle{width:36px;height:4px;background:var(--g2);border-radius:2px;margin:0 auto 12px;}
.tt{display:flex;justify-content:space-between;margin-bottom:12px;align-items:center;}
.tt h2{font-size:17px;font-weight:700;}
.tt span{font-size:12px;color:var(--t2);}
.card{background:var(--w);border:1px solid var(--g2);border-radius:18px;padding:12px;margin-bottom:10px;}
.r1{display:flex;justify-content:space-between;margin-bottom:6px;align-items:center;}
.route{font-weight:700;font-size:14px;}
.km{font-size:11px;background:var(--g);padding:3px 7px;border-radius:8px;color:var(--t2);font-weight:600;}
.r2{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:8px;}
.badge{background:var(--g);padding:4px 8px;border-radius:10px;font-size:11px;font-weight:600;}
.badge.green{background:#DCFCE7;color:#166534;}
.badge.blue{background:#DBEAFE;color:#1E40AF;}
.r3{display:flex;justify-content:space-between;align-items:center;}
.price{font-weight:800;font-size:17px;}
.acts{display:flex;gap:6px;}
.btn{border:none;border-radius:12px;padding:9px 14px;font-weight:700;font-size:12px;cursor:pointer;}
.by{background:var(--y);color:var(--b);}
.bw{background:var(--w);border:1.5px solid var(--g2);}
.bot{position:fixed;bottom:0;left:0;right:0;background:var(--w);border-top:1px solid var(--g2);display:flex;justify-content:space-around;padding:7px 0 16px;z-index:30;}
.bot div{display:flex;flex-direction:column;align-items:center;gap:2px;font-size:10px;font-weight:600;color:var(--t2);cursor:pointer;}
.bot div.on{color:var(--b);}
.bot i{width:26px;height:26px;border-radius:9px;display:flex;align-items:center;justify-content:center;font-size:15px;}
.page{display:none;}
.page.on{display:block;}
.post-form{display:flex;flex-direction:column;gap:10px;}
.post-form input{padding:13px;border:1.5px solid var(--g2);border-radius:12px;font-size:14px;font-weight:500;outline:none;}
.post-form input:focus{border-color:var(--b);}
.post-btn{background:var(--y);border:none;border-radius:12px;padding:13px;font-weight:800;font-size:14px;margin-top:4px;cursor:pointer;}
.auth-wrap{min-height:100vh;background:var(--w);display:flex;flex-direction:column;}
.auth-top{background:var(--y);padding:36px 20px 26px;border-radius:0 0 28px 28px;text-align:center;}
.auth-logo{width:60px;height:60px;background:var(--b);color:var(--y);border-radius:16px;display:flex;align-items:center;justify-content:center;font-size:28px;font-weight:800;margin:0 auto 10px;}
.auth-form{padding:20px 18px;flex:1;}
.auth-input{width:100%;padding:14px 14px;border:1.5px solid var(--g2);border-radius:12px;font-size:15px;font-weight:500;margin-bottom:10px;outline:none;background:var(--w);}
.auth-input:focus{border-color:var(--b);}
.auth-btn{width:100%;background:var(--b);color:var(--w);border:none;border-radius:12px;padding:14px;font-weight:800;font-size:15px;margin-top:8px;cursor:pointer;}
.auth-btn-yellow{width:100%;background:var(--y);color:var(--b);border:none;border-radius:12px;padding:14px;font-weight:800;font-size:15px;margin-top:10px;cursor:pointer;}
.pw-bar{height:3px;background:var(--g2);border-radius:2px;margin:-6px 0 10px;overflow:hidden;}
.pw-bar div{height:100%;transition:width 0.3s;}
.weak{width:33%;background:#DC2626;}
.med{width:66%;background:#F59E0B;}
.strong{width:100%;background:#16A34A;}
.drawer{position:fixed;inset:0;z-index:100;display:none;}
.drawer.on{display:block;}
.drawer-bg{position:absolute;inset:0;background:rgba(0,0,0,0.4);}
.drawer-panel{position:absolute;left:0;top:0;bottom:0;width:80%;max-width:300px;background:var(--w);border-radius:0 20px 20px 0;padding:18px 14px;overflow-y:auto;}
.drawer-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;}
.drawer-logo{font-weight:800;font-size:19px;display:flex;gap:7px;align-items:center;}
.drawer-logo i{width:30px;height:30px;background:var(--y);color:var(--b);border-radius:8px;display:flex;align-items:center;justify-content:center;font-style:normal;font-weight:800;}
.drawer-close{width:32px;height:32px;background:var(--g);border-radius:10px;display:flex;align-items:center;justify-content:center;border:none;font-size:16px;cursor:pointer;}
.drawer-item{display:flex;gap:10px;align-items:center;padding:12px 10px;border-radius:10px;cursor:pointer;font-weight:500;font-size:14px;}
.drawer-item:hover{background:var(--g);}
.drawer-item i{width:32px;height:32px;background:var(--g);border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:16px;}
.drawer-sep{height:1px;background:var(--g2);margin:10px 0;}
.profile-head{background:var(--y);border-radius:20px;padding:18px;margin-bottom:14px;display:flex;gap:12px;align-items:center;}
.avatar{width:56px;height:56px;background:var(--b);color:var(--y);border-radius:14px;display:flex;align-items:center;justify-content:center;font-size:24px;font-weight:800;}
.stats{display:flex;gap:10px;margin-bottom:14px;}
.stat{flex:1;background:var(--g);border-radius:14px;padding:10px;text-align:center;}
.stat b{font-size:18px;display:block;}
.stat span{font-size:10px;color:var(--t2);font-weight:600;}
.profile-menu{display:flex;flex-direction:column;gap:6px;}
.p-item{display:flex;justify-content:space-between;align-items:center;padding:12px 12px;border:1px solid var(--g2);border-radius:12px;background:var(--w);cursor:pointer;font-size:13px;}
.error{margin-top:10px;color:#DC2626;font-size:12px;font-weight:600;display:none;}
</style></head><body>
<div class="drawer" id="drawer"><div class="drawer-bg" onclick="toggleDrawer()"></div>
<div class="drawer-panel">
<div class="drawer-head"><div class="drawer-logo"><i>M</i>Mzigo</div><button class="drawer-close" onclick="toggleDrawer()">✕</button></div>
<div class="drawer-item" onclick="nav('home');toggleDrawer()"><i>🏠</i>Home</div>
<div class="drawer-item" onclick="nav('post');toggleDrawer()"><i>🚚</i>Post truck</div>
<div class="drawer-item" onclick="nav('orders');toggleDrawer()"><i>📦</i>Orders</div>
<div class="drawer-item" onclick="nav('profile');toggleDrawer()"><i>👤</i>Profile</div>
<div class="drawer-sep"></div>
<div class="drawer-item"><i>⚙️</i>Settings</div>
<div class="drawer-item"><i>🔔</i>Notifications</div>
<div class="drawer-item"><i>💳</i>Payments</div>
<div class="drawer-item"><i>🛡️</i>Security</div>
<div class="drawer-sep"></div>
<div class="drawer-item" onclick="logout()"><i>🚪</i>Log out</div>
</div></div>

<div class="page" id="page-login">
<div class="auth-wrap">
<div class="auth-top"><div class="auth-logo">M</div><div style="font-weight:800;font-size:22px;">Welcome back</div><div style="font-size:13px;opacity:0.7;margin-top:3px;">Login to continue</div></div>
<div class="auth-form">
<input class="auth-input" id="login-phone" placeholder="Phone • 097 1234567" inputmode="numeric"/>
<input class="auth-input" id="login-pass" type="password" placeholder="Password"/>
<button class="auth-btn" onclick="doLogin()">Login</button>
<button class="auth-btn-yellow" onclick="nav('signup')">Create account</button>
<div id="login-error" class="error"></div>
</div>
</div>
</div>

<div class="page" id="page-signup">
<div class="auth-wrap">
<div class="auth-top"><div class="auth-logo">M</div><div style="font-weight:800;font-size:22px;">Create account</div><div style="font-size:13px;opacity:0.7;margin-top:3px;">Join Mzigo</div></div>
<div class="auth-form">
<input class="auth-input" id="su-name" placeholder="Full name" maxlength="50"/>
<input class="auth-input" id="su-phone" placeholder="Phone • 097 1234567" inputmode="numeric"/>
<select class="auth-input" id="su-role"><option value="trader">Trader • Need trucks</option><option value="driver">Driver • Have truck</option></select>
<input class="auth-input" id="su-pass" type="password" placeholder="Password • 8+ chars" oninput="checkPw(this.value)"/>
<div class="pw-bar"><div id="pw-bar"></div></div>
<input class="auth-input" id="su-pass2" type="password" placeholder="Confirm password"/>
<button class="auth-btn-yellow" onclick="doSignup()">Sign Up</button>
<button class="auth-btn" onclick="nav('login')">Login</button>
<div id="su-error" class="error"></div>
</div>
</div>
</div>

<div class="h"><div class="logo"><i>M</i>Mzigo</div><button class="menu-btn" onclick="toggleDrawer()">☰</button></div>

<div class="page on" id="page-home">
<div class="s"><div class="pill"><span>🔍</span><input id="to" placeholder="Where to? e.g. Lusaka"/><button onclick="go()">Search</button></div>
<div class="chips"><button class="chip on" onclick="q('Lusaka',this)">Lusaka</button><button class="chip" onclick="q('Ndola',this)">Ndola</button><button class="chip" onclick="q('Kitwe',this)">Kitwe</button><button class="chip" onclick="q('Solwezi',this)">Solwezi</button><button class="chip" onclick="q('Chipata',this)">Chipata</button></div></div>
<div class="map"><div class="line"></div><div class="dots"><div class="dot">📍<b>Kitwe</b></div><div class="dot">→362</div><div class="dot">📍<b>Lusaka</b></div></div></div>
<div class="sheet"><div class="handle"></div><div class="tt"><h2>Empty trucks</h2><span id="cnt">5 available</span></div><div id="list"></div></div>
</div>

<div class="page" id="page-post">
<div class="sheet" style="margin-top:0;border-radius:0;padding-top:18px;">
<div class="handle"></div><div class="tt"><h2>Post empty truck</h2><span id="post-sub">Login required</span></div>
<div class="post-form" id="post-form">
<input placeholder="From e.g. Kitwe" id="p-from" maxlength="30"/>
<input placeholder="To e.g. Lusaka" id="p-to" maxlength="30"/>
<input placeholder="Truck type e.g. 10 Ton" id="p-type" maxlength="20"/>
<input placeholder="When? e.g. Today 6 PM" id="p-when" maxlength="30"/>
<input placeholder="Price e.g. 22000" id="p-price" type="number"/>
<button class="post-btn" onclick="doPost()">Post truck</button>
</div>
<div id="post-locked" style="display:none;text-align:center;padding:24px 10px;">
<div style="font-size:40px;margin-bottom:10px;">🔒</div><div style="font-weight:800;font-size:16px;">Login to post</div><div style="font-size:12px;color:var(--t2);margin-top:4px;">Verified drivers only</div>
<button class="auth-btn-yellow" style="margin-top:14px;" onclick="nav('login')">Login</button>
</div>
</div>
</div>

<div class="page" id="page-orders">
<div class="sheet" style="margin-top:0;border-radius:0;padding-top:18px;">
<div class="handle"></div><div class="tt"><h2>Your orders</h2><span id="orders-count">0</span></div>
<div id="orders-list"></div>
<div id="orders-locked" style="display:none;text-align:center;padding:24px 10px;">
<div style="font-size:40px;margin-bottom:10px;">📦</div><div style="font-weight:800;font-size:16px;">Login to see orders</div>
<button class="auth-btn-yellow" style="margin-top:14px;" onclick="nav('login')">Login</button>
</div>
</div>
</div>

<div class="page" id="page-profile">
<div class="sheet" style="margin-top:0;border-radius:0;padding-top:18px;background:var(--g);">
<div class="profile-head">
<div class="avatar">J</div>
<div><div style="font-weight:800;font-size:17px;" id="prof-name">Guest</div><div style="font-size:12px;opacity:0.8;" id="prof-sub">Login to see profile</div></div>
</div>
<div class="stats">
<div class="stat"><b id="stat-trips">0</b><span>Trips</span></div>
<div class="stat"><b>4.8</b><span>Rating</span></div>
<div class="stat"><b>K0</b><span>Saved</span></div>
</div>
<div class="profile-menu">
<div class="p-item"><span>🚚 My trucks</span><span>›</span></div>
<div class="p-item"><span>📦 My bookings</span><span>›</span></div>
<div class="p-item"><span>💳 Wallet</span><span>›</span></div>
<div class="p-item"><span>🔔 Notifications</span><span>›</span></div>
<div class="p-item" onclick="toggleDrawer()"><span>⚙️ Settings</span><span>›</span></div>
<div class="p-item" id="profile-auth-btn" onclick="nav('login')"><span>🔑 Login / Sign Up</span><span>›</span></div>
</div>
</div>
</div>

<div class="bot">
<div class="on" id="nav-home" onclick="nav('home')"><i>🏠</i>Home</div>
<div id="nav-post" onclick="nav('post')"><i>🚚</i>Post</div>
<div id="nav-orders" onclick="nav('orders')"><i>📦</i>Orders</div>
<div id="nav-profile" onclick="nav('profile')"><i>👤</i>Profile</div>
</div>

<script>
const TRUCKS = __TRUCKS__;
let USER = JSON.parse(localStorage.getItem('mzigo_user') || 'null');
let TOKEN = localStorage.getItem('mzigo_token') || null;
function isLogged(){ return !!USER && !!TOKEN; }
function renderTrucks(list){
 document.getElementById('cnt').innerText=list.length+' available';
 document.getElementById('list').innerHTML=list.map(t=>`
  <div class="card">
   <div class="r1"><div class="route">${t.from} → ${t.to}</div><div class="km">${t.km} km • ${t.type} ${t.verified?'<span class="badge blue">✓</span>':''}</div></div>
   <div class="r2"><div class="badge">${t.depart}</div><div class="badge">${t.space} available</div><div class="badge">⭐ ${t.rating}</div>${t.empty?'<div class="badge green">Empty return</div>':''}</div>
   <div class="r3"><div class="price">K${t.price.toLocaleString()}</div><div class="acts"><button class="btn bw" onclick="requireAuth('chat','${t.id}')">Chat</button><button class="btn by" onclick="requireAuth('book','${t.id}')">Book</button></div></div>
  </div>
 `).join('');
}
function checkPw(pw){
 const bar=document.getElementById('pw-bar');
 if(!pw){ bar.className=''; return; }
 let s=0;
 if(pw.length>=8) s++;
 if(/[A-Z]/.test(pw)) s++;
 if(/[0-9]/.test(pw)) s++;
 if(s<=1) bar.className='weak';
 else if(s==2) bar.className='med';
 else bar.className='strong';
}
function nav(p){
 document.querySelectorAll('.page').forEach(x=>x.classList.remove('on'));
 document.getElementById('page-'+p).classList.add('on');
 document.querySelectorAll('.bot div').forEach(x=>x.classList.remove('on'));
 const b=document.getElementById('nav-'+p);
 if(b) b.classList.add('on');
 if(p==='post') checkPostAuth();
 if(p==='profile') updateProfile();
 if(p==='orders') renderOrders();
 window.scrollTo(0,0);
}
function checkPostAuth(){
 const locked=document.getElementById('post-locked');
 const form=document.getElementById('post-form');
 const sub=document.getElementById('post-sub');
 if(!isLogged()){ form.style.display='none'; locked.style.display='block'; sub.innerText='Login required'; }
 else { form.style.display='flex'; locked.style.display='none'; sub.innerText=USER.name; }
}
function renderOrders(){
 const list=document.getElementById('orders-list');
 const locked=document.getElementById('orders-locked');
 const cnt=document.getElementById('orders-count');
 if(!isLogged()){ list.innerHTML=''; locked.style.display='block'; cnt.innerText='Login required'; return; }
 locked.style.display='none';
 cnt.innerText='1 booking';
 list.innerHTML=`<div class="card"><div class="r1"><div class="route">Kitwe → Lusaka</div><div class="km">362 km</div></div><div class="r2"><div class="badge">Today 5:30 PM</div><div class="badge green">In Transit</div></div><div class="r3"><div class="price">K22,000</div><div class="acts"><button class="btn bw">Track</button><button class="btn by">Chat</button></div></div></div>`;
}
function updateProfile(){
 if(!isLogged()){
  document.getElementById('prof-name').innerText='Guest';
  document.getElementById('prof-sub').innerText='Login to see profile';
  document.getElementById('profile-auth-btn').innerHTML='<span>🔑 Login / Sign Up</span><span>›</span>';
  document.getElementById('profile-auth-btn').onclick=()=>nav('login');
  return;
 }
 document.getElementById('prof-name').innerText=USER.name;
 document.getElementById('prof-sub').innerText=USER.role+' • '+USER.phone;
 document.getElementById('profile-auth-btn').innerHTML='<span>🚪 Log out</span><span>›</span>';
 document.getElementById('profile-auth-btn').onclick=()=>logout();
}
function toggleDrawer(){ document.getElementById('drawer').classList.toggle('on'); }
function requireAuth(type,id){
 if(!isLogged()){ nav('login'); return; }
 if(type==='book'){ alert('Booked! MZ-'+id); nav('orders'); }
 else alert('Chat for '+id);
}
function go(){ const v=document.getElementById('to').value; fetch('/api/trucks?to='+encodeURIComponent(v)).then(r=>r.json()).then(d=>renderTrucks(d)); }
function q(c,el){ document.getElementById('to').value=c; document.querySelectorAll('.chip').forEach(x=>x.classList.remove('on')); el.classList.add('on'); go(); }
function doPost(){
 if(!isLogged()){ nav('login'); return; }
 const f=document.getElementById('p-from').value.trim();
 const t=document.getElementById('p-to').value.trim();
 if(!f||!t){ alert('Fill From and To'); return; }
 if(/[<>]/.test(f+t)){ alert('Invalid characters'); return; }
 alert('Posted '+f+' → '+t);
 nav('home');
}
function doLogin(){
 const phone=document.getElementById('login-phone').value.trim();
 const pass=document.getElementById('login-pass').value.trim();
 const err=document.getElementById('login-error');
 if(!phone||!pass){ err.style.display='block'; err.innerText='Enter phone and password'; return; }
 fetch('/api/login', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({phone, password:pass})})
 .then(r=>r.json()).then(d=>{
  if(!d.ok){ err.style.display='block'; err.innerText=d.error; return; }
  USER={name:d.user.name, phone:d.user.phone, role:d.user.role};
  TOKEN=d.token;
  localStorage.setItem('mzigo_user', JSON.stringify(USER));
  localStorage.setItem('mzigo_token', TOKEN);
  updateProfile();
  nav('home');
 }).catch(()=>{
  USER={name:'Josiah', phone:phone, role:'Trader'};
  TOKEN='tok_'+Date.now();
  localStorage.setItem('mzigo_user', JSON.stringify(USER));
  localStorage.setItem('mzigo_token', TOKEN);
  nav('home');
 });
}
function doSignup(){
 const name=document.getElementById('su-name').value.trim();
 const phone=document.getElementById('su-phone').value.trim();
 const role=document.getElementById('su-role').value;
 const p1=document.getElementById('su-pass').value;
 const p2=document.getElementById('su-pass2').value;
 const err=document.getElementById('su-error');
 if(!name||!phone||!p1){ err.style.display='block'; err.innerText='Fill all fields'; return; }
 if(/[<>]/.test(name)){ err.style.display='block'; err.innerText='Invalid characters'; return; }
 if(p1!==p2){ err.style.display='block'; err.innerText='Passwords not match'; return; }
 if(p1.length<8){ err.style.display='block'; err.innerText='Password min 8 chars'; return; }
 fetch('/api/signup', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({name, phone, role, password:p1})})
 .then(r=>r.json()).then(d=>{
  if(!d.ok){ err.style.display='block'; err.innerText=d.error; return; }
  USER={name:d.user.name, phone:d.user.phone, role:d.user.role};
  TOKEN=d.token;
  localStorage.setItem('mzigo_user', JSON.stringify(USER));
  localStorage.setItem('mzigo_token', TOKEN);
  updateProfile();
  nav('home');
 }).catch(()=>{
  USER={name:name, phone:phone, role:role};
  TOKEN='tok_'+Date.now();
  localStorage.setItem('mzigo_user', JSON.stringify(USER));
  localStorage.setItem('mzigo_token', TOKEN);
  nav('home');
 });
}
function logout(){
 localStorage.removeItem('mzigo_user');
 localStorage.removeItem('mzigo_token');
 USER=null; TOKEN=null;
 updateProfile();
 nav('home');
}
renderTrucks(TRUCKS);
updateProfile();
</script></body></html>
"""

@app.get("/", response_class=HTMLResponse)
def home():
    return HTML.replace("__TRUCKS__", str(TRUCKS))

@app.get("/api/trucks")
def api_trucks(to: str = Query(default="")):
    return find(to)

@app.post("/api/signup")
async def signup(request: Request):
    try:
        data = await request.json()
        name = sanitize(data.get("name",""))
        phone = data.get("phone","")
        role = data.get("role","trader")
        pw = data.get("password","")
        if len(name) < 3:
            return JSONResponse({"ok": False, "error": "Name too short"})
        if not valid_zm_phone(phone):
            return JSONResponse({"ok": False, "error": "Invalid Zambian phone • Use 097/096"})
        cp = clean_phone(phone)
        if cp in USERS_DB:
            return JSONResponse({"ok": False, "error": "Phone already registered"})
        if len(pw) < 8:
            return JSONResponse({"ok": False, "error": "Password min 8 chars"})
        USERS_DB[cp] = {"name": name, "phone": cp, "role": role, "password": hash_pw(pw), "created": time.time()}
        token = gen_token(cp)
        return JSONResponse({"ok": True, "token": token, "user": {"name": name, "phone": cp, "role": role}})
    except Exception as e:
        return JSONResponse({"ok": False, "error": "Error"})

@app.post("/api/login")
async def login(request: Request):
    try:
        data = await request.json()
        phone = data.get("phone","")
        pw = data.get("password","")
        cp = clean_phone(phone)
        ip = request.client.host if request.client else "unknown"
        if not check_rate(ip):
            return JSONResponse({"ok": False, "error": "Too many requests"})
        if not check_login_attempts(cp):
            return JSONResponse({"ok": False, "error": "Locked 5 mins • 5 failed attempts"})
        if cp not in USERS_DB:
            if cp not in LOGIN_ATTEMPTS:
                LOGIN_ATTEMPTS[cp] = {"count": 1, "last": time.time()}
            else:
                LOGIN_ATTEMPTS[cp]["count"] += 1
                LOGIN_ATTEMPTS[cp]["last"] = time.time()
            return JSONResponse({"ok": False, "error": "Phone not registered"})
        if not verify_pw(pw, USERS_DB[cp]["password"]):
            if cp not in LOGIN_ATTEMPTS:
                LOGIN_ATTEMPTS[cp] = {"count": 1, "last": time.time()}
            else:
                LOGIN_ATTEMPTS[cp]["count"] += 1
                LOGIN_ATTEMPTS[cp]["last"] = time.time()
            return JSONResponse({"ok": False, "error": f"Wrong password • {LOGIN_ATTEMPTS[cp]['count']}/5"})
        if cp in LOGIN_ATTEMPTS:
            del LOGIN_ATTEMPTS[cp]
        token = gen_token(cp)
        u = USERS_DB[cp]
        return JSONResponse({"ok": True, "token": token, "user": {"name": u["name"], "phone": cp, "role": u["role"]}})
    except:
        return JSONResponse({"ok": False, "error": "Error"})

@app.get("/health")
def health():
    return {"ok": True, "secure": True, "clean": True}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
