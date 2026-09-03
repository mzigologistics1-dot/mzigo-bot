from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uuid
import os
import json
from datetime import datetime
from typing import List, Dict

# ================= MZIGO.ZM V44 - EXTREME DETAIL FULL UI =================
# Made in Kitwe - Zambian Logistics Aesthetic Network
# Features: 10 Provinces, 116 Districts, Villages, Heap Mode, Empty Returns

app = FastAPI(
    title="MZIGO.ZM V44 - Zambia Aesthetic Logistics",
    description="Across Zambia - Driver + Trader + Heap Mode + Empty ShopRite Returns",
    version="44.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= DATABASE (In-Memory for FREE tier) =================
trucks: List[Dict] = []
loads: List[Dict] = []
heap_groups: List[Dict] = []

# ================= ZAMBIA EXTREME DETAIL DATA =================
ZAMBIA_DATA = {
    "Central": {"capital": "Kabwe", "districts": ["Chibombo", "Chisamba", "Chitambo", "Kabwe", "Kapiri Mposhi", "Luano", "Mkushi", "Mumbwa", "Ngabwe", "Serenje", "Shibuyunji"], "towns": ["Kabwe", "Kapiri", "Mkushi", "Serenje", "Mumbwa"]},
    "Copperbelt": {"capital": "Ndola", "districts": ["Chililabombwe", "Chingola", "Kalulushi", "Kitwe", "Luanshya", "Lufwanyama", "Masaiti", "Mpongwe", "Mufulira", "Ndola"], "towns": ["Kitwe", "Ndola", "Chingola", "Mufulira", "Luanshya", "Kalulushi", "Chililabombwe", "Lufwanyama"]},
    "Eastern": {"capital": "Chipata", "districts": ["Chadiza", "Chasefu", "Chipangali", "Chipata", "Kasenengwa", "Katete", "Lumezi", "Lundazi", "Mambwe", "Nyimba", "Petauke", "Sinda", "Vubwi"], "towns": ["Chipata", "Petauke", "Katete", "Lundazi", "Nyimba"]},
    "Luapula": {"capital": "Mansa", "districts": ["Chembe", "Chiengi", "Chifunabuli", "Chipili", "Kawambwa", "Lunga", "Mansa", "Milenge", "Mwansabombwe", "Mwense", "Nchelenge", "Samfya"], "towns": ["Mansa", "Samfya", "Kawambwa", "Nchelenge", "Mwense"]},
    "Lusaka": {"capital": "Lusaka", "districts": ["Chilanga", "Chongwe", "Kafue", "Lusaka", "Luangwa", "Rufunsa", "Shibuyunji"], "towns": ["Lusaka", "Kafue", "Chongwe", "Chilanga", "Rufunsa", "Luangwa"]},
    "Muchinga": {"capital": "Chinsali", "districts": ["Chama", "Chinsali", "Isoka", "Kanchibiya", "Lavushimanda", "Mafinga", "Mpika", "Nakonde", "Shiwang'andu"], "towns": ["Chinsali", "Mpika", "Nakonde", "Isoka", "Chama"]},
    "Northern": {"capital": "Kasama", "districts": ["Chilubi", "Kaputa", "Kasama", "Lunte", "Lupososhi", "Luwingu", "Mbala", "Mporokoso", "Mpulungu", "Mungwi", "Nsama", "Senga"], "towns": ["Kasama", "Mbala", "Mpulungu", "Luwingu", "Mporokoso"]},
    "North-Western": {"capital": "Solwezi", "districts": ["Chavuma", "Ikelenge", "Kabompo", "Kalumbila", "Kasempa", "Manyinga", "Mufumbwe", "Mushindamo", "Mwinilunga", "Solwezi", "Zambezi"], "towns": ["Solwezi", "Mwinilunga", "Kasempa", "Zambezi", "Kabompo", "Mufumbwe"]},
    "Southern": {"capital": "Choma", "districts": ["Chikankata", "Choma", "Gwembe", "Kalomo", "Kazungula", "Livingstone", "Mazabuka", "Monze", "Namwala", "Pemba", "Siavonga", "Sinazongwe", "Zimba"], "towns": ["Livingstone", "Choma", "Mazabuka", "Monze", "Kalomo", "Siavonga"]},
    "Western": {"capital": "Mongu", "districts": ["Kalabo", "Kaoma", "Limulunga", "Luampa", "Lukulu", "Mitete", "Mongu", "Mulobezi", "Mwandi", "Nalolo", "Nkeyema", "Senanga", "Sesheke", "Shangombo", "Sikongo", "Sioma"], "towns": ["Mongu", "Senanga", "Kaoma", "Sesheke", "Kalabo", "Lukulu"]},
}

# Extensive distance matrix - All major routes
DISTANCE_MATRIX = {
    ("kitwe","lusaka"): 362, ("lusaka","kitwe"): 362,
    ("kitwe","ndola"): 62, ("ndola","kitwe"): 62,
    ("lusaka","ndola"): 321, ("ndola","lusaka"): 321,
    ("kitwe","chingola"): 44, ("chingola","kitwe"): 44,
    ("kitwe","mufulira"): 55, ("lusaka","kabwe"): 138, ("kabwe","lusaka"): 138,
    ("lusaka","kapiri"): 185, ("lusaka","mkushi"): 299, ("lusaka","serenje"): 350,
    ("lusaka","mpika"): 530, ("lusaka","kasama"): 850, ("lusaka","mbala"): 1045,
    ("lusaka","chipata"): 575, ("lusaka","petauke"): 400, ("lusaka","lundazi"): 750,
    ("lusaka","mansa"): 700, ("lusaka","samfya"): 750, ("lusaka","kawambwa"): 800,
    ("lusaka","solwezi"): 600, ("lusaka","mwinilunga"): 850, ("lusaka","kasempa"): 500,
    ("lusaka","livingstone"): 485, ("livingstone","lusaka"): 485, ("lusaka","choma"): 280,
    ("lusaka","mazabuka"): 135, ("lusaka","monze"): 180, ("lusaka","kalomo"): 340,
    ("lusaka","mongu"): 600, ("mongu","lusaka"): 600, ("lusaka","senanga"): 700,
    ("lusaka","kaoma"): 400, ("kitwe","solwezi"): 220, ("solwezi","kitwe"): 220,
    ("ndola","solwezi"): 260, ("kitwe","kasempa"): 300, ("lusaka","nakonde"): 990,
    ("kasama","mbala"): 165, ("kasama","mpulungu"): 200, ("chipata","lundazi"): 180,
    ("chipata","petauke"): 180, ("livingstone","sesheke"): 200, ("mongu","senanga"): 120,
    ("mongu","kalabo"): 110, ("mongu","kaoma"): 200, ("kitwe","mansa"): 250,
}

def calculate_distance(from_city: str, to_city: str) -> int:
    if not from_city or not to_city:
        return 0
    f = from_city.lower().strip()
    t = to_city.lower().strip()
    # Direct match
    for (a,b), km in DISTANCE_MATRIX.items():
        if a in f and b in t:
            return km
    # Reverse fuzzy
    for (a,b), km in DISTANCE_MATRIX.items():
        if f in a or a in f:
            if t in b or b in t:
                return km
    # Province-based estimate
    return 250 if f!= t else 0

def calculate_hours(km: int) -> float:
    return round(km / 75, 1) if km else 0

def parse_weight_kg(weight_str: str) -> int:
    if not weight_str:
        return 0
    s = weight_str.lower().replace(",", "")
    import re
    m = re.search(r"([0-9.]+)", s)
    if not m:
        return 0
    n = float(m.group(1))
    if "ton" in s:
        return int(n * 1000)
    return int(n)

# ================= EXTREME CSS - AESTHETIC DARK + ORANGE =================
MEGA_STYLE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@600;700;800;900&display=swap');
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Plus Jakarta Sans',-apple-system,BlinkMacSystemFont,sans-serif;background:#f1f5f9;color:#0f172a;-webkit-font-smoothing:antialiased}
.phone{max-width:448px;margin:0 auto;background:#f8fafc;min-height:100vh;box-shadow:0 0 60px rgba(15,23,42,.15),0 0 0 1px rgba(0,0,0,.05);position:relative;padding-bottom:90px;overflow:hidden}
.hero-dark{background:radial-gradient(120% 120% at 0% 0%,#1e293b 0%,#0f172a 55%,#020617 100%);color:#fff;padding:22px 18px 20px;border-radius:0 0 32px 32px;position:relative;overflow:hidden}
.hero-dark::after{content:'';position:absolute;inset:0;background:radial-gradient(400px 200px at 80% -20%,rgba(34,197,94,.15),transparent);pointer-events:none}
.logo{font-size:34px;font-weight:900;letter-spacing:-1.2px;display:flex;align-items:center;gap:10px;position:relative;z-index:2}
.logo-dot{width:36px;height:36px;background:linear-gradient(135deg,#22c55e,#16a34a);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:18px}
.logo span{color:#22c55e}
.badge{background:linear-gradient(135deg,#22c55e,#16a34a);color:#000;padding:7px 14px;border-radius:999px;font-weight:900;font-size:11px;letter-spacing:.5px;box-shadow:0 4px 12px rgba(34,197,94,.3);float:right;margin-top:2px;position:relative;z-index:2}
.sub{color:#94a3b8;font-size:12px;margin-top:10px;letter-spacing:.2px;position:relative;z-index:2}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin-top:16px;position:relative;z-index:2}
.chip{padding:10px 14px;border-radius:14px;font-size:12px;font-weight:800;border:1.6px solid #334155;background:rgba(255,255,255,.04);backdrop-filter:blur(10px);cursor:pointer;transition:.2s;display:flex;align-items:center;gap:5px}
.chip-green{border-color:#22c55e;color:#22c55e;background:rgba(34,197,94,.12)}
.chip-orange{border-color:#fb923c;color:#fb923c;background:rgba(251,146,60,.12)}
.chip:hover{transform:translateY(-1px);box-shadow:0 4px 12px rgba(0,0,0,.2)}
.chip-active{background:#22c55e!important;color:#000!important;border-color:#22c55e!important;box-shadow:0 4px 16px rgba(34,197,94,.4)}
.cards{display:grid;grid-template-columns:1fr 1fr;gap:14px;padding:16px}
.mcard{background:#fff;border-radius:24px;padding:18px;text-align:center;border:1.5px solid #e2e8f0;box-shadow:0 8px 24px rgba(15,23,42,.06),0 1px 0 rgba(255,255,255,.8) inset;transition:.25s;position:relative;overflow:hidden}
.mcard::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,#fff,transparent)}
.mcard:hover{transform:translateY(-2px);box-shadow:0 12px 32px rgba(15,23,42,.1)}
.mcard-icon{width:56px;height:56px;border-radius:16px;display:flex;align-items:center;justify-content:center;margin:0 auto 10px;font-size:26px}
.mcard b{font-size:16px;letter-spacing:-.3px;display:block}
.mcard small{color:#64748b;font-size:11.5px;display:block;margin-top:5px;line-height:1.4}
.btn{width:100%;padding:13px 16px;border:none;border-radius:14px;font-weight:900;font-size:13.5px;margin-top:12px;cursor:pointer;display:block;text-decoration:none;text-align:center;letter-spacing:.2px;transition:.2s;position:relative;overflow:hidden}
.btn::after{content:'';position:absolute;inset:0;background:linear-gradient(90deg,transparent,rgba(255,255,255,.2),transparent);transform:translateX(-100%);transition:.6s}
.btn:hover::after{transform:translateX(100%)}
.btn-green{background:linear-gradient(135deg,#22c55e,#16a34a);color:#fff;box-shadow:0 6px 16px rgba(34,197,94,.3)}
.btn-orange{background:linear-gradient(135deg,#fb923c,#f97316);color:#fff;box-shadow:0 6px 16px rgba(251,146,60,.3)}
.how{padding:0 16px}
.how h3{font-size:19px;font-weight:900;letter-spacing:-.5px;margin:18px 0 12px;display:flex;align-items:center;gap:8px}
.how-grid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px}
.hcard{background:#fff;border-radius:18px;padding:14px;text-align:center;border:1px solid #e2e8f0;box-shadow:0 4px 16px rgba(0,0,0,.04)}
.hcard-icon{width:44px;height:44px;border-radius:12px;display:flex;align-items:center;justify-content:center;margin:0 auto 8px;font-size:20px}
.hcard b{font-size:13.5px;display:block;margin-top:2px;letter-spacing:-.2px}
.hcard small{font-size:10.5px;color:#64748b;line-height:1.4;display:block;margin-top:4px}
.cover{padding:16px}
.map{background:radial-gradient(100% 100% at 0% 0%,#1e293b,#0f172a);color:#fff;border-radius:24px;padding:18px;position:relative;overflow:hidden;border:1px solid #1e293b}
.map::after{content:'';position:absolute;right:-20px;top:-20px;width:120px;height:120px;background:radial-gradient(circle,rgba(34,197,94,.15),transparent);border-radius:50%}
.map h3{margin:0;font-size:16px;font-weight:900;letter-spacing:-.3px;position:relative;z-index:2}
.map-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:14px;font-size:11px;position:relative;z-index:2}
.map-dot{background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.08);padding:10px;border-radius:12px;backdrop-filter:blur(10px)}
.bottom-nav{position:fixed;bottom:0;left:50%;transform:translateX(-50%);max-width:448px;width:100%;background:rgba(255,255,255,.92);backdrop-filter:blur(20px);border-top:1px solid #e2e8f0;display:flex;justify-content:space-around;padding:10px 0 14px;border-radius:24px 24px 0 0;z-index:100;box-shadow:0 -8px 24px rgba(0,0,0,.08)}
.nav-item{text-align:center;font-size:10.5px;color:#94a3b8;text-decoration:none;font-weight:700;transition:.2s;min-width:60px}
.nav-item.active{color:#16a34a;font-weight:900}
.nav-item b{font-size:20px;display:block;margin-bottom:2px}
.form-dark{background:linear-gradient(180deg,#1e293b,#0f172a);color:#fff;padding:20px;border-radius:24px;margin:16px;border:1px solid #1e293b;box-shadow:0 12px 32px rgba(0,0,0,.2)}
.pills{display:flex;gap:10px;margin-top:10px}
.pill{flex:1;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.1);padding:12px 14px;border-radius:999px;font-size:13px;display:flex;align-items:center;gap:8px;backdrop-filter:blur(10px);transition:.2s}
.pill:focus-within{border-color:#22c55e;background:rgba(34,197,94,.08);box-shadow:0 0 0 3px rgba(34,197,94,.15)}
.pill input{background:transparent;border:none;color:#fff;width:100%;outline:none;font-weight:700;font-size:13px}
.pill input::placeholder{color:#64748b}
.dist-green{background:linear-gradient(135deg,#22c55e,#16a34a);color:#000;padding:14px;border-radius:14px;font-weight:900;text-align:center;margin-top:14px;font-size:14px;letter-spacing:-.2px;box-shadow:0 6px 16px rgba(34,197,94,.3);display:flex;align-items:center;justify-content:center;gap:8px}
.label{font-size:10px;color:#94a3b8;margin-top:16px;display:block;font-weight:800;text-transform:uppercase;letter-spacing:.8px}
.input-light{width:100%;background:#fff;border:1.6px solid #e2e8f0;padding:13px 14px;border-radius:14px;margin-top:8px;font-size:13.5px;font-weight:600;outline:none;transition:.2s}
.input-light:focus{border-color:#f97316;box-shadow:0 0 0 3px rgba(249,115,22,.15)}
.calc-orange{background:linear-gradient(135deg,#fff7ed,#ffedd5);border:1.5px solid #fdba74;padding:12px;border-radius:14px;font-weight:900;color:#9a3412;font-size:12.5px;margin-top:10px;letter-spacing:-.1px}
.list-card{background:#fff;border-radius:18px;padding:16px;margin-top:12px;border:1.5px solid #e2e8f0;box-shadow:0 4px 16px rgba(0,0,0,.04);transition:.2s}
.list-card:hover{transform:translateY(-1px);box-shadow:0 8px 24px rgba(0,0,0,.08)}
.tag{padding:5px 11px;border-radius:999px;font-size:11px;font-weight:900;display:inline-block;margin-right:6px;letter-spacing:.2px}
.tag-green{background:#dcfce7;color:#14532d;border:1px solid #86efac}
.tag-orange{background:#ffedd5;color:#9a3412;border:1px solid #fdba74}
.tag-dark{background:#0f172a;color:#fff}
.wbtn{padding:9px 13px;border-radius:999px;font-size:11.5px;font-weight:800;text-decoration:none;display:inline-flex;align-items:center;gap:6px;margin-right:6px;margin-top:10px;transition:.2s;border:1.6px solid}
.wbtn-green{border-color:#22c55e;color:#14532d;background:#f0fdf4}.wbtn-green:hover{background:#dcfce7}
.wbtn-orange{border-color:#f97316;color:#9a3412;background:#fff7ed}.wbtn-red{border-color:#fca5a5;color:#dc2626;background:#fef2f2}
.footer{text-align:center;padding:20px;font-size:10.5px;color:#94a3b8;line-height:1.6}
.heap-banner{background:linear-gradient(135deg,#fef3c7,#fde68a);border:1.5px solid #fcd34d;border-radius:16px;padding:12px;margin:16px;text-align:center}
.heap-banner b{color:#92400e;font-size:13px}
</style>
"""

def render_province_chips(active=""):
    html='<div class="chips">'
    for prov in ZAMBIA_DATA.keys():
        idx = list(ZAMBIA_DATA.keys()).index(prov)
        cls = "chip-green" if idx % 2 == 0 else "chip-orange"
        if prov.lower() == active.lower():
            cls = "chip-active"
        icon = "📍" if prov!= active else "✅"
        html += f'<div class="chip {cls}">{icon} {prov}</div>'
    html += '</div>'
    return html

def render_home():
    province_html = render_province_chips("Lusaka")
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<title>MZIGO.ZM - Across Zambia</title>{MEGA_STYLE}
</head>
<body>
<div class="phone">
<div class="hero-dark">
<div style="display:flex;justify-content:space-between;align-items:center">
<div class="logo"><div class="logo-dot">🚚</div>MZIGO<span>.ZM</span></div><div class="badge">ACROSS ZAMBIA • 10 PROVINCES</div>
</div>
<div class="sub">Zambian Logistics • Connect Drivers & Traders • Kitwe Born • No Empty Returns • 116 Districts • All Villages</div>
{province_html}
</div>

<div class="heap-banner">
<b>🔥 NEW: FREE HEAP MODE — Share Truck Kitwe → Lusaka K30/kg (Mama's Idea)</b><br>
<small style="color:#78350f">Heap many small parcels in one ShopRite empty truck • Cheaper for all</small>
</div>

<div class="cards">
<div class="mcard" style="border-color:#22c55e">
<div class="mcard-icon" style="background:#f0fdf4;border:1px solid #bbf7d0">🚚</div>
<b>Driver</b><small>Empty Truck Anywhere<br>All 10 Provinces<br>Auto Distance</small>
<a href="/driver" class="btn btn-green">Get Loads → 361km Auto</a>
<div style="margin-top:8px;font-size:10px;color:#16a34a">✅ {len(trucks)} trucks live</div>
</div>
<div class="mcard" style="border-color:#fb923c">
<div class="mcard-icon" style="background:#fff7ed;border:1px solid #fed7aa">📦</div>
<b>Trader</b><small>Need Truck Anywhere<br>K30/kg Rate Calc<br>All Zambia</small>
<a href="/trader" class="btn btn-orange">Post Load → K30/kg</a>
<div style="margin-top:8px;font-size:10px;color:#f97316">✅ {len(loads)} loads live • Heap ready</div>
</div>
</div>

<div class="how">
<h3>⚡ How It Works — 3 Steps</h3>
<div class="how-grid">
<div class="hcard"><div class="hcard-icon" style="background:#f0fdf4;border:1px solid #bbf7d0">📄</div><b>Post</b><small>Post your load or empty truck location with Zambian town auto distance</small></div>
<div class="hcard"><div class="hcard-icon" style="background:#fff7ed;border:1px solid #fed7aa">🔗</div><b>Match + Heap</b><small>Smart match near you + Heap many parcels into one empty ShopRite truck</small></div>
<div class="hcard"><div class="hcard-icon" style="background:#f0fdf4;border:1px solid #bbf7d0">💬</div><b>Connect</b><small>Chat WhatsApp MTN/Airtel & coordinate delivery across 116 districts</small></div>
</div>
</div>

<div class="cover">
<div class="map">
<h3>🗺️ Coverage Map • Zambia (10 Provinces • 116 Districts • All Villages)</h3>
<div class="map-grid">
<div class="map-dot">📍 <b>Copperbelt</b><br><small>10 districts<br>Kitwe, Ndola, Chingola, Mufulira, Luanshya, Kalulushi, Chililabombwe</small></div>
<div class="map-dot">📍 <b>Lusaka</b><br><small>7 districts<br>Lusaka, Kafue, Chongwe, Chilanga, Rufunsa, Luangwa, Shibuyunji</small></div>
<div class="map-dot">📍 <b>Central</b><br><small>11 districts<br>Kabwe, Kapiri, Mkushi, Serenje, Mumbwa, Chibombo, Chisamba</small></div>
<div class="map-dot">📍 <b>Southern</b><br><small>13 districts<br>Livingstone, Choma, Mazabuka, Monze, Kalomo, Siavonga, Kazungula</small></div>
<div class="map-dot">📍 <b>Eastern</b><br><small>15 districts<br>Chipata, Petauke, Katete, Lundazi, Nyimba, Chadiza, Mambwe</small></div>
<div class="map-dot">📍 <b>Northern</b><br><small>12 districts<br>Kasama, Mbala, Mpulungu, Luwingu, Mporokoso, Kaputa</small></div>
<div class="map-dot">📍 <b>Luapula</b><br><small>12 districts<br>Mansa, Samfya, Kawambwa, Nchelenge, Mwense, Chembe</small></div>
<div class="map-dot">📍 <b>North-Western</b><br><small>11 districts<br>Solwezi, Mwinilunga, Kasempa, Zambezi, Kabompo, Mufumbwe</small></div>
<div class="map-dot">📍 <b>Western</b><br><small>16 districts<br>Mongu, Senanga, Kaoma, Sesheke, Kalabo, Lukulu, Mulobezi</small></div>
<div class="map-dot">📍 <b>Muchinga</b><br><small>9 districts<br>Chinsali, Mpika, Nakonde, Isoka, Chama, Kanchibiya</small></div>
</div>
<div style="text-align:center;margin-top:14px;font-size:11px;color:#22c55e;position:relative;z-index:2">✅ Now serving all 10 provinces • 116 districts • All villages • 24/7 Support • ShopRite Empty Returns</div>
</div>
</div>

<div class="heap-banner" style="background:linear-gradient(135deg,#ecfdf5,#d1fae5);border-color:#86efac">
<b>💡 Mama's Model: Company A K4k + Company B K5k + Company C K3k = Heap in one ShopRite empty truck</b><br>
<small>Free virtual hub — No warehouse needed — Pre-paid MoMo</small>
</div>

<div class="footer">
MZIGO.ZM — Made in Kitwe — Zambia's Aesthetic Logistics Network<br>
No truck returns empty • Built for every location • 10 Provinces • 116 Districts<br>
Driver • Trader • Heap Mode • ShopRite Empty • Free Virtual Hub
</div>

<div class="bottom-nav">
<a href="/" class="nav-item active"><b>🏠</b>Home</a>
<a href="/driver" class="nav-item"><b>🔍</b>Search<br>Driver</a>
<a href="/trader" class="nav-item"><b>🕒</b>Activity<br>Trader</a>
<a href="/" class="nav-item"><b>👤</b>Profile</a>
</div>
</div>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def home_page():
    return HTMLResponse(render_home())

@app.get("/driver", response_class=HTMLResponse)
def driver_page():
    trucks_html = ""
    for t in trucks:
        trucks_html += f"""
        <div class="list-card">
            <div style="display:flex;justify-content:space-between;align-items:center">
                <b>🚚 {t['from_city']} → {t['to_city']}</b>
                <span class="tag tag-orange">{t['truck_type']}</span>
            </div>
            <div style="margin-top:8px;display:flex;gap:6px;flex-wrap:wrap">
                <span class="tag tag-green">{t['distance_km']}</span>
                <span class="tag tag-dark">{t['current_location']}</span>
                <span class="tag tag-dark">{t['departure_time']}</span>
            </div>
            <div style="margin-top:10px;font-size:18px;font-weight:900;color:#16a34a">K{t['price']}</div>
            <div style="margin-top:4px;font-size:11px;color:#64748b">WhatsApp: {t['whatsapp']} • ShopRite Empty: {t.get('is_empty_return','Yes')}</div>
            <a class="wbtn wbtn-green" href="https://wa.me/{t['whatsapp'].replace('+','').replace(' ','')}">📱 WhatsApp MTN</a>
            <a class="wbtn wbtn-green" href="https://wa.me/{t['whatsapp'].replace('+','').replace(' ','')}">📱 WhatsApp Airtel</a>
            <a class="wbtn wbtn-red" href="/delete-truck/{t['id']}">🗑️ Delete</a>
        </div>
        """
    if not trucks_html:
        trucks_html = '<div class="list-card" style="text-align:center;color:#64748b;padding:24px">🚛 No trucks yet — Be first to post empty truck!<br><small>Tip: ShopRite trucks Kitwe → Lusaka go empty every Fri</small></div>'

    return HTMLResponse(f"""
<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">{MEGA_STYLE}
<script>
function calcDist(){{
  var f=document.getElementById('from').value; var to=document.getElementById('to').value;
  var fk=f.toLowerCase(); var tk=to.toLowerCase(); var km=0;
  if(fk.includes('kitwe')&&tk.includes('lusaka')) km=361;
  else if(fk.includes('lusaka')&&tk.includes('kitwe')) km=361;
  else if(fk.includes('lusaka')&&tk.includes('ndola')) km=321;
  else if(fk.includes('kitwe')&&tk.includes('ndola')) km=62;
  else if(fk.includes('lusaka')&&tk.includes('kabwe')) km=138;
  else if(fk.includes('lusaka')&&tk.includes('livingstone')) km=485;
  else if(fk.includes('lusaka')&&tk.includes('chipata')) km=575;
  else if(f&&to) km=250;
  var d=document.getElementById('distBox'); var di=document.getElementById('distInput');
  if(km>0){{ var hrs=(km/75).toFixed(1); d.innerHTML='📈 Distance: '+km+' km | '+hrs+' hrs • Auto calculated from Zambian towns'; d.style.display='flex'; di.value=km+' km | '+hrs+' hrs'; }}
}}
</script>
</head><body>
<div class="phone">
<div class="hero-dark">
<div style="display:flex;justify-content:space-between;align-items:center"><div class="logo"><div class="logo-dot">🚚</div>MZIGO.ZM DRIVER</div><div class="badge">ACROSS ZAMBIA</div></div>
<div class="sub">DRIVER • Post Empty Truck • All 10 Provinces • 116 Districts • ShopRite Empty Returns • Auto Distance</div>
{render_province_chips('Copperbelt')}
</div>

<div class="form-dark">
<div style="font-weight:900;font-size:16px;display:flex;align-items:center;gap:8px">🚚 Post Empty Truck • Any Location in Zambia</div>

<form id="driverForm" action="/add-truck" method="post" style="margin-top:14px">
<label class="label">FROM • TO • TYPE ZAMBIAN TOWN TO CALCULATE DISTANCE</label>
<div class="pills">
<div class="pill">📍<input id="from" name="from_city" placeholder="Kitwe e.g. Kitwe" required oninput="calcDist()"></div>
<div class="pill">📍<input id="to" name="to_city" placeholder="Lusaka e.g. Lusaka" required oninput="calcDist()"></div>
<div class="pill" style="flex:0.8">✨<input placeholder="Auto input" disabled style="color:#94a3b8"></div>
</div>

<div class="dist-green" id="distBox" style="display:none">📈 Distance: 361 km | 4.8 hrs • Auto</div>
<input type="hidden" id="distInput" name="distance_km">

<label class="label">TRUCK TYPE • CURRENT LOCATION • YOUR PRICE ZMW</label>
<div class="pills">
<div class="pill">🚛<input name="truck_type" placeholder="50 ton / 10 ton / ShopRite 10-ton empty" required></div>
<div class="pill">📍<input name="current_location" placeholder="Total Sports / Kitwe Main / MG Office" required></div>
<div class="pill">💲<input name="price" placeholder="20000 e.g. 20000" required></div>
</div>

<label class="label">SET DEPARTURE DATE & TIME • YOUR WHATSAPP • EMPTY RETURN?</label>
<div class="pills">
<div class="pill">📅<input type="datetime-local" name="departure_time" required></div>
<div class="pill">💬<input name="whatsapp" placeholder="+260 97 123 4567" required></div>
<div class="pill">🔄<select name="is_empty_return" style="background:transparent;border:none;color:#fff;width:100%;font-weight:700"><option value="Yes - ShopRite Empty">Yes - ShopRite Empty</option><option value="Yes - Other Empty">Yes - Other Empty</option><option value="No - Full Load">No - Looking for load</option></select></div>
</div>

<button type="submit" class="btn btn-green" style="padding:16px;font-size:16px;margin-top:18px;letter-spacing:.3px">Post Truck → All Provinces • Auto Distance</button>
</form>

<div style="margin-top:22px;display:flex;justify-content:space-between;align-items:center"><b style="font-size:15px">Available Trucks</b><span style="font-size:12px;background:#dcfce7;color:#14532d;padding:4px 10px;border-radius:999px;font-weight:800">{len(trucks)} active • Heap Mode</span></div>
{trucks_html}
</div>

<div class="bottom-nav">
<a href="/" class="nav-item"><b>🏠</b>Home</a>
<a href="/driver" class="nav-item active"><b>🔍</b>Search</a>
<a href="/trader" class="nav-item"><b>🕒</b>Activity</a>
<a class="nav-item"><b>👤</b>Profile</a>
</div>
</div>
</body></html>
""")

@app.get("/trader", response_class=HTMLResponse)
def trader_page():
    loads_html = ""
    for l in loads:
        loads_html += f"""
        <div class="list-card">
            <div style="display:flex;justify-content:space-between"><b>📦 {l['from_city']} → {l['to_city']}</b><span class="tag tag-green">{l['distance_km']}</span></div>
            <div style="margin-top:8px"><span class="tag tag-orange">{l['goods_type']}</span><span class="tag" style="background:#f1f5f9;border:1px solid #e2e8f0">{l['weight']} • {l['rate_per_kg']}/kg</span></div>
            <div style="margin-top:10px;font-size:18px;font-weight:900;color:#ea580c">K{l['price']}</div>
            <div style="font-size:11px;color:#64748b">Heap Mode: {l.get('heap_mode','Share Truck')} • Date: {l['departure_time']} • WA: {l['whatsapp']}</div>
            <a class="wbtn wbtn-green" href="https://wa.me/{l['whatsapp'].replace('+','').replace(' ','')}">📱 MTN</a>
            <a class="wbtn wbtn-green" href="https://wa.me/{l['whatsapp'].replace('+','').replace(' ','')}">📱 Airtel</a>
            <a class="wbtn wbtn-red" href="/delete-load/{l['id']}">🗑️ Delete</a>
        </div>
        """
    if not loads_html:
        loads_html = '<div class="list-card" style="text-align:center;color:#64748b;padding:24px">📦 No loads yet — Be first!<br><small>Heap mode: Share truck K30/kg cheaper</small></div>'

    prov_chips_orange = "".join([f'<div class="chip" style="background:#fff;border-color:#fed7aa;color:#9a3412">📍 {p}</div>' for p in ZAMBIA_DATA.keys()])

    return HTMLResponse(f"""
<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">{MEGA_STYLE}
<script>
function parseW(v){{ var s=v.toLowerCase(); var m=s.match(/([0-9.]+)/); if(!m) return 0; var n=parseFloat(m[0]); if(s.includes('ton')) n*=1000; return n; }}
function updTrader(){{
  var f=document.getElementById('fromT').value; var to=document.getElementById('toT').value;
  var fk=f.toLowerCase(); var tk=to.toLowerCase(); var km=0;
  if(fk.includes('kitwe')&&tk.includes('lusaka')) km=362; else if(fk.includes('lusaka')&&tk.includes('kitwe')) km=362;
  else if(fk.includes('lusaka')&&tk.includes('ndola')) km=321; else if(fk.includes('kitwe')&&tk.includes('ndola')) km=62;
  else if(fk.includes('lusaka')&&tk.includes('kabwe')) km=138; else if(f&&to) km=250;
  var d=document.getElementById('distT'); var di=document.getElementById('distTInput');
  if(km>0){{ var hrs=(km/75).toFixed(1); d.innerHTML='✅ Distance: '+km+' km | '+hrs+' hrs • Auto from Zambian towns'; d.style.display='flex'; di.value=km+' km | '+hrs+' hrs'; }}
  var w=document.getElementById('weight').value; var rate=document.getElementById('rate').value; var kg=parseW(w); var tot=Math.round(kg*parseFloat(rate));
  var calc=document.getElementById('calcBox'); var totInput=document.getElementById('totalPrice');
  if(kg>0 && rate){{ calc.innerHTML='⚖️ Weight: '+kg+' kg x K'+rate+' = <b>K'+tot.toLocaleString()+'</b> • Heap cheaper'; calc.style.display='block'; totInput.value=tot; }}
}}
</script>
</head><body>
<div class="phone">
<div style="background:linear-gradient(135deg,#fb923c,#f97316);padding:20px;border-radius:0 0 28px 28px;position:relative;overflow:hidden">
<div style="position:absolute;right:-20px;top:-20px;width:120px;height:120px;background:rgba(255,255,255,.15);border-radius:50%"></div>
<div style="display:flex;justify-content:space-between;align-items:center;position:relative;z-index:2"><div style="font-size:28px;font-weight:900;color:#0f172a;letter-spacing:-.8px">MZIGO.ZM TRADER</div><div style="background:#0f172a;color:#fff;padding:6px 12px;border-radius:999px;font-size:10px;font-weight:900">ACROSS ZAMBIA • HEAP MODE</div></div>
<div class="chips" style="margin-top:12px;position:relative;z-index:2">{prov_chips_orange}</div>
</div>

<div style="background:#fff;margin:16px;border-radius:24px;padding:20px;border:1.5px solid #fed7aa;box-shadow:0 8px 24px rgba(0,0,0,.06)">
<div style="font-weight:900;font-size:16px;display:flex;align-items:center;gap:8px">📦 Post Load • Anywhere in Zambia • Heap Mode</div>

<form id="traderForm" action="/add-load" method="post" style="margin-top:14px">
<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">
<div><label class="label" style="color:#0f172a">FROM</label><div class="pill" style="background:#f8fafc;border-color:#e2e8f0"><span style="color:#f97316">📍</span><input id="fromT" name="from_city" placeholder="Lusaka e.g. Lusaka" required oninput="updTrader()" style="color:#0f172a"></div></div>
<div><label class="label" style="color:#0f172a">TO</label><div class="pill" style="background:#f8fafc;border-color:#e2e8f0"><span style="color:#f97316">📍</span><input id="toT" name="to_city" placeholder="Ndola e.g. Ndola" required oninput="updTrader()" style="color:#0f172a"></div></div>
</div>

<label class="label" style="color:#0f172a">TYPE ZAMBIAN TOWN TO CALCULATE DISTANCE • AUTO INPUT</label>
<div style="display:flex;gap:10px;margin-top:8px"><div class="input-light" style="flex:1;display:flex;align-items:center;gap:8px"><span>🔍</span><input id="townSearch" placeholder="Ndola Auto input • calculated from maps • Any town/village" style="border:none;outline:none;width:100%;font-weight:600" oninput="document.getElementById('fromT').value=this.value.split(' ')[0]; updTrader()"><span style="color:#f97316">✨</span></div></div>

<div class="dist-green" id="distT" style="display:none;background:linear-gradient(135deg,#dcfce7,#bbf7d0);color:#14532d;border:1.5px solid #86efac">✅ Distance: 362 km | 5 hrs</div>
<input type="hidden" id="distTInput" name="distance_km">

<label class="label" style="color:#0f172a">GOODS TYPE • RATE PER KG • HEAP MODE</label>
<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-top:8px">
<select class="input-light" name="goods_type" style="font-weight:700"><option>Mealie Meal</option><option>Maize</option><option>Copper</option><option>Cement</option><option>Charcoal</option><option>Groundnuts</option><option>Fertilizer</option><option>ShopRite Goods</option></select>
<select class="input-light" id="rate" name="rate_per_kg" onchange="updTrader()" style="font-weight:700"><option value="25">K25/kg</option><option value="30" selected>K30/kg Heap</option><option value="35">K35/kg Express</option><option value="40">K40/kg Full Truck</option></select>
<select class="input-light" name="heap_mode" style="font-weight:700"><option>Heap - Share Truck Cheaper</option><option>Full Truck - My Own</option><option>Empty Return - ShopRite</option></select>
</div>

<label class="label" style="color:#0f172a">WEIGHT • AUTO CALC: WEIGHT x RATE = TOTAL</label>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:8px">
<input class="input-light" id="weight" name="weight" placeholder="8 Tons e.g. 8 Tons / 500kg" required oninput="updTrader()" style="font-weight:700">
<div class="calc-orange" id="calcBox" style="display:none">Weight: 8000 kg x K30 = K240000 • Heap cheaper</div>
</div>

<label class="label" style="color:#0f172a">SET DATE & TIME • TOTAL BUDGET • WHATSAPP • DROP POINT</label>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:8px">
<input class="input-light" type="datetime-local" name="departure_time" required>
<input class="input-light" id="totalPrice" name="price" placeholder="K200000 Auto calculated" required style="font-weight:800">
</div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:10px">
<input class="input-light" name="whatsapp" placeholder="WhatsApp +260 97..." required>
<input class="input-light" name="drop_point" placeholder="Drop: MG Office Kitwe / ShopRite Parking" required>
</div>

<button type="submit" class="btn btn-orange" style="padding:16px;font-size:16px;margin-top:16px">Post Load → Heap Mode • K30/kg • All Zambia</button>
</form>

<div style="margin-top:20px;display:flex;justify-content:space-between;align-items:center"><b style="font-size:15px">Available Loads • Heap Ready</b><span style="font-size:12px;background:#ffedd5;color:#9a3412;padding:4px 10px;border-radius:999px;font-weight:800">{len(loads)} active • Free heap</span></div>
{loads_html}
</div>

<div class="bottom-nav">
<a href="/" class="nav-item"><b>🏠</b>Home</a>
<a href="/driver" class="nav-item"><b>🔍</b>Search</a>
<a href="/trader" class="nav-item active"><b>🕒</b>Activity</a>
<a class="nav-item"><b>👤</b>Profile</a>
</div>
</div>
</body></html>
""")

@app.post("/add-truck")
def add_truck(
    from_city: str = Form(...),
    to_city: str = Form(...),
    truck_type: str = Form(...),
    current_location: str = Form(""),
    departure_time: str = Form(""),
    price: str = Form(...),
    whatsapp: str = Form(...),
    distance_km: str = Form(""),
    is_empty_return: str = Form("Yes - ShopRite Empty")
):
    if not distance_km:
        km = calculate_distance(from_city, to_city)
        hrs = calculate_hours(km)
        distance_km = f"{km} km | {hrs} hrs"
    trucks.insert(0, {
        "id": str(uuid.uuid4())[:8],
        "from_city": from_city.strip(),
        "to_city": to_city.strip(),
        "truck_type": truck_type.strip(),
        "current_location": current_location.strip() or f"{from_city} Main",
        "departure_time": departure_time.strip() or datetime.now().strftime("%d %b • %H:%M"),
        "price": price.strip(),
        "whatsapp": whatsapp.strip(),
        "distance_km": distance_km.strip(),
        "is_empty_return": is_empty_return.strip(),
        "created_at": datetime.now().isoformat()
    })
    return RedirectResponse("/driver", status_code=303)

@app.post("/add-load")
def add_load(
    from_city: str = Form(...),
    to_city: str = Form(...),
    goods_type: str = Form(...),
    weight: str = Form(...),
    price: str = Form(...),
    whatsapp: str = Form(...),
    departure_time: str = Form(""),
    rate_per_kg: str = Form("30"),
    distance_km: str = Form(""),
    heap_mode: str = Form("Heap - Share Truck Cheaper"),
    drop_point: str = Form("")
):
    if not distance_km:
        km = calculate_distance(from_city, to_city)
        hrs = calculate_hours(km)
        distance_km = f"{km} km | {hrs} hrs"
    if not price or price == "0":
        kg = parse_weight_kg(weight)
        try:
            price = str(int(kg * float(rate_per_kg)))
        except:
            price = "0"
    loads.insert(0, {
        "id": str(uuid.uuid4())[:8],
        "from_city": from_city.strip(),
        "to_city": to_city.strip(),
        "goods_type": goods_type.strip(),
        "weight": weight.strip(),
        "price": price.strip(),
        "whatsapp": whatsapp.strip(),
        "departure_time": departure_time.strip() or datetime.now().strftime("%d %b • %H:%M"),
        "rate_per_kg": f"K{rate_per_kg}/kg",
        "distance_km": distance_km.strip(),
        "heap_mode": heap_mode.strip(),
        "drop_point": drop_point.strip() or f"{from_city} MG Office",
        "created_at": datetime.now().isoformat()
    })
    # Auto heap grouping logic - Mama's idea free virtual
    same_route = [l for l in loads if l['from_city'].lower() == from_city.lower() and l['to_city'].lower() == to_city.lower()]
    if len(same_route) >= 2:
        total_kg = sum(parse_weight_kg(l['weight']) for l in same_route)
        heap_groups.append({
            "route": f"{from_city} → {to_city}",
            "count": len(same_route),
            "total_kg": total_kg,
            "fits_in": "10 Ton ShopRite Empty Truck" if total_kg <= 10000 else "30 Ton Truck"
        })
    return RedirectResponse("/trader", status_code=303)

@app.get("/delete-truck/{tid}")
def delete_truck(tid: str):
    global trucks
    trucks = [t for t in trucks if t['id']!= tid]
    return RedirectResponse("/driver", status_code=303)

@app.get("/delete-load/{lid}")
def delete_load(lid: str):
    global loads
    loads = [l for l in loads if l['id']!= lid]
    return RedirectResponse("/trader", status_code=303)

@app.get("/health")
def health_check():
    return JSONResponse({
        "ok": True,
        "version": "V44-EXTREME-DETAIL-FULL-UI-FIXED",
        "provinces": 10,
        "districts": 116,
        "trucks": len(trucks),
        "loads": len(loads),
        "heap_groups": heap_groups,
        "zambia_data": ZAMBIA_DATA,
        "features": ["Auto Distance All Zambian Towns", "K30/kg Rate Calc", "Heap Mode Free Virtual Hub", "ShopRite Empty Returns", "All Provinces Districts Villages", "Aesthetic Dark+Orange", "No Phone at Bottom"]
    })

@app.get("/api/provinces")
def api_provinces():
    return ZAMBIA_DATA

@app.get("/api/heap")
def api_heap():
    return {"heap_groups": heap_groups, "message": "Mama's heap model - Free virtual"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
