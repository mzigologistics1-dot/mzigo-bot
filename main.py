from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uuid, os, re, json
from datetime import datetime
from typing import List, Dict, Optional

app = FastAPI(title="MZIGO.ZM V45 Fixed Readable ZMW Mega", version="45.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

trucks_db: List[Dict] = []
loads_db: List[Dict] = []
heap_db: List[Dict] = []

ZAMBIA_PROVINCES_COMPLETE = {
    "Central": {"capital": "Kabwe", "population": 1774000, "area_km2": 94394, "districts": [
            {"name": "Chibombo", "towns": ["Chibombo", "Liteta"], "villages": ["Chibombo Village"]},
            {"name": "Chisamba", "towns": ["Chisamba"], "villages": ["Chisamba Village"]},
            {"name": "Chitambo", "towns": ["Chitambo"], "villages": ["Chitambo Mission"]},
            {"name": "Kabwe", "towns": ["Kabwe", "Bwacha", "Highridge"], "villages": ["Kabwe Rural"]},
            {"name": "Kapiri Mposhi", "towns": ["Kapiri Mposhi", "Tazara"], "villages": ["Kapiri Village"]},
            {"name": "Luano", "towns": ["Luano"], "villages": ["Luano Village"]},
            {"name": "Mkushi", "towns": ["Mkushi"], "villages": ["Mkushi Boma"]},
            {"name": "Mumbwa", "towns": ["Mumbwa"], "villages": ["Mumbwa Village"]},
            {"name": "Ngabwe", "towns": ["Ngabwe"], "villages": ["Ngabwe Rural"]},
            {"name": "Serenje", "towns": ["Serenje"], "villages": ["Serenje Boma"]},
            {"name": "Shibuyunji", "towns": ["Shibuyunji"], "villages": ["Shibuyunji Village"]},
        ]},
    "Copperbelt": {"capital": "Ndola", "population": 2600000, "area_km2": 31328, "districts": [
            {"name": "Chililabombwe", "towns": ["Chililabombwe", "Konkola"], "villages": ["Main"]},
            {"name": "Chingola", "towns": ["Chingola", "Chiwempala", "Nchanga"], "villages": ["Central"]},
            {"name": "Kalulushi", "towns": ["Kalulushi"], "villages": ["Kalulushi Boma"]},
            {"name": "Kitwe", "towns": ["Kitwe", "Wusakile", "Chimwemwe", "Nkana", "Mindolo", "Kwacha", "Riverside", "Parklands"], "villages": ["Kitwe Central", "Garnerton"]},
            {"name": "Luanshya", "towns": ["Luanshya", "Roan", "Mpatamatu"], "villages": ["Luanshya Boma"]},
            {"name": "Lufwanyama", "towns": ["Lufwanyama"], "villages": ["Lufwanyama Village"]},
            {"name": "Masaiti", "towns": ["Masaiti"], "villages": ["Masaiti Village"]},
            {"name": "Mpongwe", "towns": ["Mpongwe"], "villages": ["Mpongwe Central"]},
            {"name": "Mufulira", "towns": ["Mufulira", "Kantanshi", "Butondo"], "villages": ["Mufulira Central"]},
            {"name": "Ndola", "towns": ["Ndola", "Kansenshi", "Hillcrest", "Chifubu", "Masala", "Mushili"], "villages": ["Ndola Central"]},
        ]},
    "Eastern": {"capital": "Chipata", "population": 2000000, "area_km2": 51819, "districts": [
            {"name": "Chadiza", "towns": ["Chadiza"], "villages": ["Chadiza Village"]},
            {"name": "Chipata", "towns": ["Chipata", "Kapata"], "villages": ["Chipata Township"]},
            {"name": "Katete", "towns": ["Katete"], "villages": ["Katete Central"]},
            {"name": "Lundazi", "towns": ["Lundazi"], "villages": ["Lundazi Central"]},
            {"name": "Mambwe", "towns": ["Mambwe"], "villages": ["Mambwe Village"]},
            {"name": "Nyimba", "towns": ["Nyimba"], "villages": ["Nyimba Village"]},
            {"name": "Petauke", "towns": ["Petauke"], "villages": ["Petauke Central"]},
            {"name": "Sinda", "towns": ["Sinda"], "villages": ["Sinda Village"]},
        ]},
    "Luapula": {"capital": "Mansa", "population": 1300000, "area_km2": 50567, "districts": [
            {"name": "Kawambwa", "towns": ["Kawambwa", "Mbereshi"], "villages": ["Kawambwa Central"]},
            {"name": "Mansa", "towns": ["Mansa", "Senama"], "villages": ["Mansa Township"]},
            {"name": "Mwense", "towns": ["Mwense"], "villages": ["Mwense Village"]},
            {"name": "Nchelenge", "towns": ["Nchelenge", "Kashikishi"], "villages": ["Nchelenge Central"]},
            {"name": "Samfya", "towns": ["Samfya", "Bangweulu"], "villages": ["Samfya Central"]},
        ]},
    "Lusaka": {"capital": "Lusaka", "population": 3400000, "area_km2": 21896, "districts": [
            {"name": "Chilanga", "towns": ["Chilanga"], "villages": ["Chilanga Village"]},
            {"name": "Chongwe", "towns": ["Chongwe"], "villages": ["Chongwe Central"]},
            {"name": "Kafue", "towns": ["Kafue"], "villages": ["Kafue Township"]},
            {"name": "Lusaka", "towns": ["Lusaka", "Kabulonga", "Woodlands", "Kalingalinga", "Mtendere", "Kanyama", "Chilenje", "Chelstone", "Matero"], "villages": ["Lusaka Central"]},
            {"name": "Luangwa", "towns": ["Luangwa"], "villages": ["Luangwa Village"]},
            {"name": "Rufunsa", "towns": ["Rufunsa"], "villages": ["Rufunsa Village"]},
        ]},
    "Muchinga": {"capital": "Chinsali", "population": 900000, "area_km2": 87806, "districts": [
            {"name": "Chinsali", "towns": ["Chinsali"], "villages": ["Chinsali Central"]},
            {"name": "Isoka", "towns": ["Isoka"], "villages": ["Isoka Village"]},
            {"name": "Mpika", "towns": ["Mpika", "Chilonga"], "villages": ["Mpika Central"]},
            {"name": "Nakonde", "towns": ["Nakonde"], "villages": ["Nakonde Central"]},
        ]},
    "Northern": {"capital": "Kasama", "population": 1500000, "area_km2": 77407, "districts": [
            {"name": "Kasama", "towns": ["Kasama"], "villages": ["Kasama Township"]},
            {"name": "Mbala", "towns": ["Mbala"], "villages": ["Mbala Central"]},
            {"name": "Mporokoso", "towns": ["Mporokoso"], "villages": ["Mporokoso Village"]},
            {"name": "Mpulungu", "towns": ["Mpulungu"], "villages": ["Mpulungu Harbour"]},
        ]},
    "North-Western": {"capital": "Solwezi", "population": 1000000, "area_km2": 125826, "districts": [
            {"name": "Solwezi", "towns": ["Solwezi", "Kansanshi"], "villages": ["Solwezi Central"]},
            {"name": "Mwinilunga", "towns": ["Mwinilunga"], "villages": ["Mwinilunga Central"]},
            {"name": "Kasempa", "towns": ["Kasempa"], "villages": ["Kasempa Village"]},
            {"name": "Zambezi", "towns": ["Zambezi"], "villages": ["Zambezi Village"]},
        ]},
    "Southern": {"capital": "Choma", "population": 2200000, "area_km2": 85283, "districts": [
            {"name": "Choma", "towns": ["Choma"], "villages": ["Choma Township"]},
            {"name": "Livingstone", "towns": ["Livingstone", "Dambwa"], "villages": ["Livingstone City"]},
            {"name": "Mazabuka", "towns": ["Mazabuka", "Nakambala"], "villages": ["Mazabuka Township"]},
            {"name": "Monze", "towns": ["Monze"], "villages": ["Monze Central"]},
            {"name": "Kalomo", "towns": ["Kalomo"], "villages": ["Kalomo Central"]},
        ]},
    "Western": {"capital": "Mongu", "population": 1100000, "area_km2": 126386, "districts": [
            {"name": "Mongu", "towns": ["Mongu", "Lealui"], "villages": ["Mongu Township"]},
            {"name": "Senanga", "towns": ["Senanga"], "villages": ["Senanga Central"]},
            {"name": "Kaoma", "towns": ["Kaoma"], "villages": ["Kaoma Central"]},
            {"name": "Sesheke", "towns": ["Sesheke"], "villages": ["Sesheke Village"]},
        ]},
}

DISTANCE_MATRIX_KM = {
    ("kitwe","lusaka"): 362, ("lusaka","kitwe"): 362,
    ("ndola","lusaka"): 321, ("lusaka","ndola"): 321,
    ("kitwe","ndola"): 62, ("ndola","kitwe"): 62,
    ("chingola","kitwe"): 44, ("kitwe","chingola"): 44,
    ("lusaka","kabwe"): 138, ("kabwe","lusaka"): 138,
    ("lusaka","kapiri mposhi"): 185, ("lusaka","mkushi"): 299,
    ("lusaka","serenje"): 350, ("lusaka","mumbwa"): 150,
    ("lusaka","mpika"): 530, ("lusaka","kasama"): 850,
    ("lusaka","mbala"): 1045, ("kasama","mbala"): 165,
    ("lusaka","chipata"): 575, ("chipata","lusaka"): 575,
    ("lusaka","petauke"): 400, ("chipata","lundazi"): 180,
    ("lusaka","mansa"): 700, ("kitwe","mansa"): 250,
    ("lusaka","solwezi"): 600, ("kitwe","solwezi"): 220,
    ("ndola","solwezi"): 260, ("solwezi","mwinilunga"): 250,
    ("lusaka","livingstone"): 485, ("livingstone","lusaka"): 485,
    ("lusaka","choma"): 280, ("lusaka","mazabuka"): 135,
    ("lusaka","monze"): 180, ("lusaka","kalomo"): 340,
    ("lusaka","mongu"): 600, ("mongu","lusaka"): 600,
    ("mongu","senanga"): 120, ("mongu","kalabo"): 110,
    ("kitwe","chipata"): 650, ("livingstone","mongu"): 400,
}

TRUCK_TYPES_ZAMBIA = ["2 Ton Canter","3.5 Ton Light Truck","5 Ton Truck","7 Ton Truck","10 Ton Truck","15 Ton Truck","20 Ton Truck","30 Ton Truck","50 Ton Truck","60 Ton Horse & Trailer","ShopRite 10-Ton Empty Return","Zambeef 15-Ton Empty","Trade Kings 20-Ton Empty"]
GOODS_TYPES_ZAMBIA = ["Mealie Meal","Maize","Copper Cathode","Cement","Charcoal","Groundnuts","Fertilizer","ShopRite Groceries","Zambeef Meat","Cooking Oil","Sugar","Rice","Beans","Soya Beans","Wheat","Timber","Steel","Building Materials"]

def calc_distance_km(f,t):
    if not f or not t: return 0
    f=f.lower().strip(); t=t.lower().strip()
    if f==t: return 0
    for (a,b),km in DISTANCE_MATRIX_KM.items():
        if a in f and b in t: return km
    return 200

def calc_hours_from_km(km): return round(km/70.0,1) if km else 0.0
def parse_weight_to_kg(w):
    if not w: return 0
    s=w.lower(); m=re.search(r"([0-9]*\.?[0-9]+)",s)
    if not m: return 0
    n=float(m.group(1))
    if "ton" in s: return int(n*1000)
    return int(n)

MEGA_CSS = """
<style>
*{box-sizing:border-box;margin:0;padding:0}body{font-family:-apple-system,BlinkMacSystemFont,sans-serif;background:#f1f5f9;color:#0f172a}
.phone{max-width:448px;margin:0 auto;background:#f8fafc;min-height:100vh;box-shadow:0 0 60px rgba(15,23,42,.12);position:relative;padding-bottom:96px;overflow-x:hidden}
.hero-dark{background:radial-gradient(120% 120% at 0% 0%,#1e293b 0%,#0f172a 60%,#020617 100%);color:#fff;padding:22px 18px 20px;border-radius:0 0 32px 32px;position:relative}
.logo-row{display:flex;justify-content:space-between;align-items:center}
.logo{font-size:33px;font-weight:900;letter-spacing:-1.2px;display:flex;align-items:center;gap:10px}
.logo-box{width:38px;height:38px;background:linear-gradient(135deg,#22c55e,#16a34a);border-radius:11px;display:flex;align-items:center;justify-content:center;font-size:20px}
.logo span{color:#22c55e}.badge-across{background:linear-gradient(135deg,#22c55e,#16a34a);color:#000;padding:7px 14px;border-radius:999px;font-weight:900;font-size:11px}
.sub-title{color:#94a3b8;font-size:12px;margin-top:10px;line-height:1.4}
.chips-wrap{display:flex;flex-wrap:wrap;gap:8px;margin-top:16px}
.chip-prov{padding:10px 14px;border-radius:14px;font-size:12px;font-weight:800;border:1.6px solid #334155;background:rgba(255,255,255,.05);display:flex;align-items:center;gap:5px}
.chip-green{border-color:#22c55e;color:#86efac;background:rgba(34,197,94,.12)}.chip-orange{border-color:#fb923c;color:#fed7aa;background:rgba(251,146,60,.12)}.chip-active{background:#22c55e!important;color:#000!important;border-color:#22c55e!important}
.cards-home{display:grid;grid-template-columns:1fr 1fr;gap:14px;padding:16px}
.card-home{background:#fff;border-radius:24px;padding:18px;text-align:center;border:1.5px solid #e2e8f0;box-shadow:0 8px 28px rgba(15,23,42,.06)}
.card-home-icon{width:58px;height:58px;border-radius:16px;display:flex;align-items:center;justify-content:center;margin:0 auto 10px;font-size:27px;border:1px solid #e2e8f0}
.btn-home{width:100%;padding:13px 16px;border:none;border-radius:14px;font-weight:900;font-size:13.5px;margin-top:12px;cursor:pointer;display:block;text-decoration:none;text-align:center}
.btn-green{background:linear-gradient(135deg,#22c55e,#16a34a);color:#fff}.btn-orange{background:linear-gradient(135deg,#fb923c,#f97316);color:#fff}
.how-section{padding:0 16px}.how-grid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:11px}
.how-card{background:#fff;border-radius:18px;padding:14px;text-align:center;border:1px solid #e2e8f0}
.cover-section{padding:16px}.map-card{background:radial-gradient(100% 100% at 0% 0%,#1e293b,#0f172a);color:#fff;border-radius:24px;padding:18px;border:1px solid #1e293b}
.map-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:14px;font-size:11px}.map-item{background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.1);padding:10px;border-radius:12px}
.bottom-nav-fixed{position:fixed;bottom:0;left:50%;transform:translateX(-50%);max-width:448px;width:100%;background:rgba(255,255,255,.96);backdrop-filter:blur(20px);border-top:1px solid #e2e8f0;display:flex;justify-content:space-around;padding:10px 0 14px;border-radius:24px 24px 0 0;z-index:100}
.nav-link{text-align:center;font-size:10.5px;color:#94a3b8;text-decoration:none;font-weight:700;min-width:64px}.nav-link.active{color:#16a34a;font-weight:900}.nav-link b{font-size:20px;display:block}
.form-driver{background:linear-gradient(180deg,#1e293b 0%,#0f172a 100%);color:#fff;padding:20px;border-radius:24px;margin:16px;border:1px solid #1e293b}
.form-title{font-weight:900;font-size:17px;display:flex;align-items:center;gap:8px}
.label-field{font-size:10.5px;color:#94a3b8;margin-top:16px;display:block;font-weight:800;text-transform:uppercase;letter-spacing:.8px}
.pills-row{display:flex;gap:10px;margin-top:10px;flex-wrap:wrap}
.pill-input{flex:1;min-width:120px;background:rgba(255,255,255,.07);border:1.5px solid rgba(255,255,255,.12);padding:13px 15px;border-radius:999px;font-size:14px;display:flex;align-items:center;gap:9px}
.pill-input:focus-within{border-color:#22c55e;background:rgba(34,197,94,.1);box-shadow:0 0 0 4px rgba(34,197,94,.16)}
.pill-input input,.pill-input select{background:transparent;border:none;color:#fff;width:100%;outline:none;font-weight:700;font-size:14px;min-width:0}
.pill-input input::placeholder{color:#94a3b8}
.dist-box-green{background:linear-gradient(135deg,#22c55e,#16a34a);color:#000;padding:14px 16px;border-radius:14px;font-weight:900;text-align:center;margin-top:14px;font-size:14px;display:flex;align-items:center;justify-content:center;gap:8px}
.input-light-zm{width:100%;background:#fff;border:1.6px solid #e2e8f0;padding:13px 15px;border-radius:14px;margin-top:8px;font-size:14px;font-weight:600;outline:none;color:#0f172a}
.calc-box-orange{background:linear-gradient(135deg,#fff7ed,#ffedd5);border:1.5px solid #fdba74;padding:12px 14px;border-radius:14px;font-weight:800;color:#9a3412;font-size:13px;margin-top:10px}
.list-card-zm{background:#fff;border-radius:18px;padding:16px;margin-top:12px;border:1.5px solid #e2e8f0}
.tag-zm{padding:5px 11px;border-radius:999px;font-size:11px;font-weight:900;display:inline-block;margin-right:6px;border:1px solid}
.tag-green-zm{background:#dcfce7;color:#14532d;border-color:#86efac}.tag-orange-zm{background:#ffedd5;color:#9a3412;border-color:#fdba74}.tag-dark-zm{background:#0f172a;color:#fff;border-color:#0f172a}
.wbtn-zm{padding:9px 13px;border-radius:999px;font-size:12px;font-weight:800;text-decoration:none;display:inline-flex;align-items:center;gap:6px;margin-right:6px;margin-top:10px;border:1.6px solid}
.wbtn-green-zm{border-color:#22c55e;color:#14532d;background:#f0fdf4}.wbtn-red-zm{border-color:#fca5a5;color:#dc2626;background:#fef2f2}
.footer-zm{text-align:center;padding:22px 16px;font-size:10.5px;color:#94a3b8;line-height:1.7}
</style>
"""

def chips_html(active_prov=""):
    html='<div class="chips-wrap">'
    for prov in ZAMBIA_PROVINCES_COMPLETE.keys():
        idx = list(ZAMBIA_PROVINCES_COMPLETE.keys()).index(prov)
        base = "chip-green" if idx % 2 == 0 else "chip-orange"
        if prov.lower() == active_prov.lower(): base = "chip-active"
        icon = "📍" if prov.lower()!=active_prov.lower() else "✅"
        html+=f'<div class="chip-prov {base}">{icon} {prov}</div>'
    html+='</div>'
    return html

def chips_orange_html():
    html='<div class="chips-wrap">'
    for prov in ZAMBIA_PROVINCES_COMPLETE.keys():
        html+=f'<div class="chip-prov" style="background:#fff;border-color:#fed7aa;color:#9a3412">📍 {prov}</div>'
    html+='</div>'
    return html

@app.get("/", response_class=HTMLResponse)
def home():
    return HTMLResponse(f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>MZIGO.ZM</title>{MEGA_CSS}</head><body>
<div class="phone"><div class="hero-dark"><div class="logo-row"><div class="logo"><div class="logo-box">🚚</div>MZIGO<span>.ZM</span></div><div class="badge-across">ACROSS ZAMBIA</div></div>
<div class="sub-title">Zambian Logistics • Connect Drivers & Traders • No Truck Returns Empty • 10 Provinces • 116 Districts • All Villages • Zambian Kwacha ZMW K</div>{chips_html('Lusaka')}</div>
<div class="cards-home">
<div class="card-home" style="border-color:#22c55e"><div class="card-home-icon" style="background:#f0fdf4">🚚</div><b>Driver</b><small>Empty Truck Anywhere<br>All Provinces • ZMW<br>Auto Distance</small><a href="/driver" class="btn-home btn-green">Get Loads → ZMW K</a><div style="margin-top:8px;font-size:11px;color:#16a34a;font-weight:800">✅ {len(trucks_db)} trucks • ZMW</div></div>
<div class="card-home" style="border-color:#fb923c"><div class="card-home-icon" style="background:#fff7ed">📦</div><b>Trader</b><small>Need Truck Anywhere<br>ZMW K30/kg Calc<br>All Zambia</small><a href="/trader" class="btn-home btn-orange">Post Load → ZMW K</a><div style="margin-top:8px;font-size:11px;color:#f97316;font-weight:800">✅ {len(loads_db)} loads • ZMW</div></div>
</div>
<div class="how-section"><h3>⚡ How It Works</h3><div class="how-grid">
<div class="how-card"><b>Post</b><br><small>Post load or truck • Any town • ZMW K</small></div>
<div class="how-card"><b>Match</b><br><small>Smart match • 10 provinces • ZMW</small></div>
<div class="how-card"><b>Connect</b><br><small>WhatsApp MTN/Airtel • ZMW K</small></div>
</div></div>
<div class="cover-section"><div class="map-card"><h3>🗺️ Coverage Map • Zambia (10 Provinces • 116 Districts) • ZMW</h3><div class="map-grid">
<div class="map-item">📍 Copperbelt<br><small>10 districts • Kitwe, Ndola, Chingola</small></div>
<div class="map-item">📍 Lusaka<br><small>7 districts • Lusaka, Kafue, Chongwe</small></div>
<div class="map-item">📍 Central<br><small>11 districts • Kabwe, Kapiri, Mkushi</small></div>
<div class="map-item">📍 Southern<br><small>13 districts • Livingstone, Choma, Mazabuka</small></div>
</div><div style="text-align:center;margin-top:14px;font-size:11px;color:#22c55e;font-weight:800">✅ All 10 provinces • 116 districts • ZMW Zambian Kwacha • 24/7</div></div></div>
<div class="footer-zm">MZIGO.ZM — Made in Kitwe — Zambia's Aesthetic Logistics Network<br>Currency: Zambian Kwacha (ZMW) K • No Mama banner • Readable fixed<br>Driver • Trader • ZMW K • Made for Zambia</div>
<div class="bottom-nav-fixed"><a href="/" class="nav-link active"><b>🏠</b>Home</a><a href="/driver" class="nav-link"><b>🔍</b>Search</a><a href="/trader" class="nav-link"><b>🕒</b>Activity</a><a class="nav-link"><b>👤</b>Profile</a></div>
</div></body></html>""")

@app.get("/driver", response_class=HTMLResponse)
def driver():
    trucks_html="".join([f"""<div class="list-card-zm"><b>🚚 {t['from_city']} → {t['to_city']}</b> <span class="tag-zm tag-orange-zm">{t['truck_type']}</span><div style="margin-top:8px"><span class="tag-zm tag-green-zm">📏 {t['distance_km']}</span><span class="tag-zm tag-dark-zm">📍 {t['current_location']}</span></div><div style="margin-top:10px;font-size:19px;font-weight:900;color:#16a34a">K {t['price']} ZMW</div><div style="font-size:11px;color:#64748b">WhatsApp: {t['whatsapp']}</div><a class="wbtn-zm wbtn-green-zm" href="https://wa.me/{t['whatsapp'].replace('+','').replace(' ','')}">📱 MTN</a><a class="wbtn-zm wbtn-green-zm" href="https://wa.me/{t['whatsapp'].replace('+','').replace(' ','')}">📱 Airtel</a><a class="wbtn-zm wbtn-red-zm" href="/delete-truck/{t['id']}">🗑️ Delete</a></div>""" for t in trucks_db]) or '<div class="list-card-zm" style="text-align:center;color:#64748b;padding:26px">🚛 No trucks yet — Be first!<br><small>ZMW K • Readable fixed</small></div>'
    truck_opts="".join([f'<option>{tt}</option>' for tt in TRUCK_TYPES_ZAMBIA])
    return HTMLResponse(f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">{MEGA_CSS}
<script>
function calcDriverDist(){{
  var f=document.getElementById('fromCity').value; var to=document.getElementById('toCity').value;
  var fk=f.toLowerCase(); var tk=to.toLowerCase(); var km=0;
  if(fk.includes('kitwe')&&tk.includes('lusaka')) km=362; else if(fk.includes('lusaka')&&tk.includes('kitwe')) km=362;
  else if(fk.includes('lusaka')&&tk.includes('ndola')) km=321; else if(fk.includes('kitwe')&&tk.includes('ndola')) km=62;
  else if(fk.includes('lusaka')&&tk.includes('kabwe')) km=138; else if(f&&to) km=200;
  var box=document.getElementById('distBoxDriver'); var input=document.getElementById('distInputDriver');
  if(km>0){{ var hrs=(km/70).toFixed(1); box.innerHTML='📏 Distance: '+km+' km | '+hrs+' hrs • Auto • ZMW K'; box.style.display='flex'; input.value=km+' km | '+hrs+' hrs'; }}
}}
</script>
</head><body><div class="phone"><div class="hero-dark"><div class="logo-row"><div class="logo"><div class="logo-box">🚚</div>MZIGO.ZM DRIVER</div><div class="badge-across">ACROSS ZAMBIA • ZMW K</div></div><div class="sub-title">DRIVER • Post Empty Truck • All 10 Provinces • 116 Districts • ZMW K • Readable Fixed</div>{chips_html('Copperbelt')}</div>
<div class="form-driver"><div class="form-title">🚚 Post Empty Truck • Any Location in Zambia • ZMW K</div>
<form action="/add-truck" method="post" style="margin-top:14px">
<label class="label-field">FROM • TO • TYPE ZAMBIAN TOWN TO CALCULATE DISTANCE • AUTO</label>
<div class="pills-row"><div class="pill-input">📍<input id="fromCity" name="from_city" placeholder="Kitwe" required oninput="calcDriverDist()"></div><div class="pill-input">📍<input id="toCity" name="to_city" placeholder="Lusaka" required oninput="calcDriverDist()"></div><div class="pill-input" style="flex:0.7;opacity:.8">✨<input placeholder="Auto" disabled></div></div>
<div class="dist-box-green" id="distBoxDriver" style="display:none">📏 Distance: 362 km | 5.1 hrs • Auto • ZMW K</div><input type="hidden" id="distInputDriver" name="distance_km">
<label class="label-field">TRUCK TYPE • CURRENT LOCATION • YOUR PRICE ZMW (Zambian Kwacha K)</label>
<div class="pills-row"><div class="pill-input">🚛<select name="truck_type" required>{truck_opts}</select></div><div class="pill-input">📍<input name="current_location" placeholder="Total Sports, Kitwe" required></div><div class="pill-input">💰<span style="color:#22c55e;font-weight:900">K</span><input name="price" placeholder="20000 ZMW" required></div></div>
<label class="label-field">SET DEPARTURE DATE & TIME • YOUR WHATSAPP • EMPTY RETURN? • ZMW K</label>
<div class="pills-row"><div class="pill-input">📅<input type="datetime-local" name="departure_time" required></div><div class="pill-input">💬<input name="whatsapp" placeholder="+260 97 123 4567" required></div><div class="pill-input">🔄<select name="is_empty_return" required><option>Yes - ShopRite Empty Return ZMW</option><option>Yes - Other Empty Return ZMW</option><option>No - Seeking Load ZMW</option></select></div></div>
<button type="submit" class="btn-home btn-green" style="padding:17px;font-size:16px;margin-top:18px">Post Truck → All Provinces • Auto Distance • ZMW K</button>
<div style="text-align:center;margin-top:10px;font-size:11px;color:#94a3b8">All prices in Zambian Kwacha ZMW (K) • Readable inputs fixed • No cut-off</div>
</form><div style="margin-top:22px;display:flex;justify-content:space-between"><b>Available Trucks • ZMW K</b><span style="font-size:12px;background:#dcfce7;color:#14532d;padding:5px 12px;border-radius:999px;font-weight:800">{len(trucks_db)} active • ZMW</span></div>{trucks_html}</div>
<div class="bottom-nav-fixed"><a href="/" class="nav-link"><b>🏠</b>Home</a><a href="/driver" class="nav-link active"><b>🔍</b>Search</a><a href="/trader" class="nav-link"><b>🕒</b>Activity</a><a class="nav-link"><b>👤</b>Profile</a></div></div></body></html>""")

@app.get("/trader", response_class=HTMLResponse)
def trader():
    loads_html="".join([f"""<div class="list-card-zm"><b>📦 {l['from_city']} → {l['to_city']}</b> <span class="tag-zm tag-green-zm">{l['distance_km']}</span><div style="margin-top:8px"><span class="tag-zm tag-orange-zm">{l['goods_type']}</span><span class="tag-zm" style="background:#f1f5f9">{l['weight']} • {l['rate_per_kg']}</span></div><div style="margin-top:10px;font-size:19px;font-weight:900;color:#ea580c">K {l['price']} ZMW</div><div style="font-size:11px;color:#64748b">Drop: {l.get('drop_point','MG Office')} • {l['departure_time']}</div><a class="wbtn-zm wbtn-green-zm" href="https://wa.me/{l['whatsapp'].replace('+','').replace(' ','')}">📱 MTN</a><a class="wbtn-zm wbtn-green-zm" href="https://wa.me/{l['whatsapp'].replace('+','').replace(' ','')}">📱 Airtel</a><a class="wbtn-zm wbtn-red-zm" href="/delete-load/{l['id']}">🗑️ Delete</a></div>""" for l in loads_db]) or '<div class="list-card-zm" style="text-align:center;color:#64748b;padding:26px">📦 No loads yet — Be first!<br><small>ZMW K30/kg • Readable</small></div>'
    goods_opts="".join([f'<option>{g}</option>' for g in GOODS_TYPES_ZAMBIA])
    return HTMLResponse(f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">{MEGA_CSS}
<script>
function parseWeightKg(v){{ var s=v.toLowerCase(); var m=s.match(/([0-9]*\\.?[0-9]+)/); if(!m) return 0; var n=parseFloat(m[0]); if(s.includes('ton')) n*=1000; return n; }}
function updateTrader(){{
  var f=document.getElementById('fromT').value; var to=document.getElementById('toT').value;
  var fk=f.toLowerCase(); var tk=to.toLowerCase(); var km=0;
  if(fk.includes('kitwe')&&tk.includes('lusaka')) km=362; else if(fk.includes('lusaka')&&tk.includes('kitwe')) km=362;
  else if(fk.includes('lusaka')&&tk.includes('ndola')) km=321; else if(f&&to) km=200;
  var d=document.getElementById('distBoxTrader'); var di=document.getElementById('distInputTrader');
  if(km>0){{ var hrs=(km/70).toFixed(1); d.innerHTML='✅ Distance: '+km+' km | '+hrs+' hrs • Auto • ZMW K'; d.style.display='flex'; di.value=km+' km | '+hrs+' hrs'; }}
  var w=document.getElementById('weightT').value; var rate=document.getElementById('rateT').value; var kg=parseWeightKg(w); var total=Math.round(kg*parseFloat(rate));
  var calc=document.getElementById('calcTrader'); var tot=document.getElementById('totalTrader');
  if(kg>0 && rate){{ calc.innerHTML='⚖️ Weight: '+kg.toLocaleString()+' kg × K'+rate+'/kg = K'+total.toLocaleString()+' ZMW'; calc.style.display='block'; tot.value=total; }}
}}
</script>
</head><body><div class="phone"><div style="background:linear-gradient(135deg,#fb923c,#f97316);padding:20px;border-radius:0 0 28px 28px"><div style="display:flex;justify-content:space-between;align-items:center"><div style="font-size:27px;font-weight:900;color:#0f172a">MZIGO.ZM TRADER</div><div style="background:#0f172a;color:#fff;padding:6px 12px;border-radius:999px;font-size:10px;font-weight:900">ACROSS ZAMBIA • ZMW K</div></div><div style="margin-top:12px">{chips_orange_html()}</div></div>
<div style="background:#fff;margin:16px;border-radius:24px;padding:20px;border:1.5px solid #fed7aa">
<div style="font-weight:900;font-size:16px">📦 Post Load • Anywhere in Zambia • ZMW K</div>
<form action="/add-load" method="post" style="margin-top:14px">
<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px"><div><label class="label-field" style="color:#0f172a">FROM</label><div class="pill-input" style="background:#f8fafc;border-color:#e2e8f0"><span>📍</span><input id="fromT" name="from_city" placeholder="Lusaka" required oninput="updateTrader()" style="color:#0f172a"></div></div><div><label class="label-field" style="color:#0f172a">TO</label><div class="pill-input" style="background:#f8fafc;border-color:#e2e8f0"><span>📍</span><input id="toT" name="to_city" placeholder="Ndola" required oninput="updateTrader()" style="color:#0f172a"></div></div></div>
<label class="label-field" style="color:#0f172a">TYPE ZAMBIAN TOWN TO CALCULATE DISTANCE • AUTO</label><div class="input-light-zm" style="display:flex;align-items:center;gap:8px">🔍<input id="townSearch" placeholder="Ndola • Any town • Auto • ZMW K" style="border:none;outline:none;width:100%;font-weight:600;color:#0f172a" oninput="document.getElementById('fromT').value=this.value.split(' ')[0]; updateTrader()">✨</div>
<div class="dist-box-green" id="distBoxTrader" style="display:none;background:linear-gradient(135deg,#dcfce7,#bbf7d0);color:#14532d;border:1.5px solid #86efac">✅ Distance: 362 km | 5.1 hrs • Auto • ZMW K</div><input type="hidden" id="distInputTrader" name="distance_km">
<label class="label-field" style="color:#0f172a">GOODS TYPE • RATE PER KG (ZMW K) • SHARE MODE</label>
<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-top:8px"><select class="input-light-zm" name="goods_type" required>{goods_opts}</select><select class="input-light-zm" id="rateT" name="rate_per_kg" onchange="updateTrader()" required><option value="25">K25/kg ZMW</option><option value="30" selected>K30/kg ZMW</option><option value="35">K35/kg ZMW</option><option value="40">K40/kg ZMW</option><option value="50">K50/kg ZMW</option></select><select class="input-light-zm" name="heap_mode" required><option>Share Truck - Cheaper ZMW K</option><option>Full Truck - My Own ZMW K</option><option>Express - Fast ZMW K</option></select></div>
<label class="label-field" style="color:#0f172a">WEIGHT • AUTO CALC: WEIGHT × RATE = TOTAL ZMW K</label><div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:8px"><input class="input-light-zm" id="weightT" name="weight" placeholder="8 Tons or 500kg" required oninput="updateTrader()"><div class="calc-box-orange" id="calcTrader" style="display:none">⚖️ Weight: 8000 kg × K30/kg = K240,000 ZMW</div></div>
<label class="label-field" style="color:#0f172a">SET DATE & TIME • TOTAL BUDGET ZMW K • WHATSAPP • DROP POINT</label><div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:8px"><input class="input-light-zm" type="datetime-local" name="departure_time" required><input class="input-light-zm" id="totalTrader" name="price" placeholder="K240000 ZMW Auto" required></div><div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:10px"><input class="input-light-zm" name="whatsapp" placeholder="WhatsApp +260 97 123 4567" required><input class="input-light-zm" name="drop_point" placeholder="Drop: MG Office / ShopRite Parking" required></div>
<button type="submit" class="btn-home btn-orange" style="padding:17px;font-size:16px;margin-top:16px">Post Load → ZMW K • All Zambia • Readable</button><div style="text-align:center;margin-top:10px;font-size:11px;color:#94a3b8">All prices in Zambian Kwacha ZMW (K) • K30/kg • Readable fixed</div>
</form><div style="margin-top:20px;display:flex;justify-content:space-between"><b>Available Loads • ZMW K</b><span style="font-size:12px;background:#ffedd5;color:#9a3412;padding:5px 12px;border-radius:999px;font-weight:800">{len(loads_db)} active • ZMW</span></div>{loads_html}</div>
<div class="bottom-nav-fixed"><a href="/" class="nav-link"><b>🏠</b>Home</a><a href="/driver" class="nav-link"><b>🔍</b>Search</a><a href="/trader" class="nav-link active"><b>🕒</b>Activity</a><a class="nav-link"><b>👤</b>Profile</a></div></div></body></html>""")

@app.post("/add-truck")
def add_truck(from_city: str=Form(...), to_city: str=Form(...), truck_type: str=Form(...), current_location: str=Form(""), departure_time: str=Form(""), price: str=Form(...), whatsapp: str=Form(...), distance_km: str=Form(""), is_empty_return: str=Form("Yes - ShopRite Empty Return")):
    if not distance_km: km=calc_distance_km(from_city,to_city); hrs=calc_hours_from_km(km); distance_km=f"{km} km | {hrs} hrs"
    clean_price=re.sub(r"[^0-9]","",price) or "0"
    trucks_db.insert(0,{"id":str(uuid.uuid4())[:8],"from_city":from_city.strip().title(),"to_city":to_city.strip().title(),"truck_type":truck_type.strip(),"current_location":current_location.strip() or f"{from_city.strip().title()} Main","departure_time":departure_time.strip() or datetime.now().strftime("%d %b • %H:%M"),"price":clean_price,"whatsapp":whatsapp.strip(),"distance_km":distance_km.strip(),"is_empty_return":is_empty_return.strip(),"created_at":datetime.now().isoformat(),"currency":"ZMW","currency_symbol":"K"})
    return RedirectResponse("/driver",303)

@app.post("/add-load")
def add_load(from_city: str=Form(...), to_city: str=Form(...), goods_type: str=Form(...), weight: str=Form(...), price: str=Form(...), whatsapp: str=Form(...), departure_time: str=Form(""), rate_per_kg: str=Form("30"), distance_km: str=Form(""), heap_mode: str=Form("Share Truck - Cheaper ZMW"), drop_point: str=Form("")):
    if not distance_km: km=calc_distance_km(from_city,to_city); hrs=calc_hours_from_km(km); distance_km=f"{km} km | {hrs} hrs"
    clean_price=re.sub(r"[^0-9]","",price) or "0"
    if clean_price=="0": kg=parse_weight_to_kg(weight); r=float(re.sub(r"[^0-9.]","",rate_per_kg) or "30"); clean_price=str(int(kg*r))
    loads_db.insert(0,{"id":str(uuid.uuid4())[:8],"from_city":from_city.strip().title(),"to_city":to_city.strip().title(),"goods_type":goods_type.strip(),"weight":weight.strip(),"price":clean_price,"whatsapp":whatsapp.strip(),"departure_time":departure_time.strip() or datetime.now().strftime("%d %b • %H:%M"),"rate_per_kg":f"K{re.sub(r'[^0-9]','',rate_per_kg)}/kg ZMW","distance_km":distance_km.strip(),"heap_mode":heap_mode.strip(),"drop_point":drop_point.strip() or f"{from_city.strip().title()} MG Office","created_at":datetime.now().isoformat(),"currency":"ZMW","currency_symbol":"K"})
    return RedirectResponse("/trader",303)

@app.get("/delete-truck/{tid}")
def delete_truck(tid:str):
    global trucks_db; trucks_db=[t for t in trucks_db if t['id']!=tid]; return RedirectResponse("/driver",303)
@app.get("/delete-load/{lid}")
def delete_load(lid:str):
    global loads_db; loads_db=[l for l in loads_db if l['id']!=lid]; return RedirectResponse("/trader",303)
@app.get("/health")
def health(): return JSONResponse({"ok":True,"version":"V45-FIXED-READABLE-ZMW-MEGA","currency":"ZMW K","fixes":["No Mama banner","Readable inputs","ZMW K everywhere"]})
if __name__=="__main__":
    import uvicorn; port=int(os.environ.get("PORT",10000)); uvicorn.run(app,host="0.0.0.0",port=port)
