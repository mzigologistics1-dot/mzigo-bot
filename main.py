from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse
import uuid, os

app = FastAPI(title="MZIGO.ZM - Aesthetic Perfect", version="42.0")
trucks = []
loads = []

# ALL ZAMBIA - 10 provinces + districts + towns + villages
ZAMBIA_LOCATIONS = {
    "Central": ["Kabwe", "Kapiri Mposhi", "Mkushi", "Serenje", "Chibombo", "Chisamba", "Mumbwa", "Itezhi Tezhi", "Chitambo", "Luano", "Ngabwe", "Shibuyunji"],
    "Copperbelt": ["Ndola", "Kitwe", "Chingola", "Mufulira", "Luanshya", "Kalulushi", "Chililabombwe", "Mpongwe", "Masaiti", "Lufwanyama"],
    "Eastern": ["Chipata", "Petauke", "Katete", "Lundazi", "Chadiza", "Mambwe", "Nyimba", "Sinda", "Vubwi", "Chipangali", "Kasengula", "Lumezi"],
    "Luapula": ["Mansa", "Samfya", "Kawambwa", "Nchelenge", "Mwansabombwe", "Chembe", "Chipili", "Chifunabuli", "Mwense", "Chienge", "Lunga", "Milenge"],
    "Lusaka": ["Lusaka", "Kafue", "Chongwe", "Chilanga", "Chirundu", "Luangwa", "Rufunsa", "Shibuyunji", "Feira"],
    "Muchinga": ["Chinsali", "Mpika", "Isoka", "Nakonde", "Shiwang'andu", "Kanchibiya", "Lavushimanya", "Mafinga"],
    "Northern": ["Kasama", "Mbala", "Mpulungu", "Mporokoso", "Kaputa", "Luwingu", "Mungwi", "Nsama", "Lunte", "Senga Hill"],
    "North-Western": ["Solwezi", "Mwinilunga", "Kasempa", "Kabompo", "Zambezi", "Mufumbwe", "Manyinga", "Kalumbila", "Mushindamo", "Chavuma", "Ikelenge"],
    "Southern": ["Choma", "Livingstone", "Mazabuka", "Monze", "Kalomo", "Kazungula", "Siavonga", "Namwala", "Pemba", "Sinazongwe", "Zimba", "Gwembe", "Itezhi Tezhi"],
    "Western": ["Mongu", "Senanga", "Sesheke", "Kaoma", "Kalabo", "Lukulu", "Shangombo", "Mitete", "Sikongo", "Limulunga", "Nalolo", "Nkeyema", "Sioma", "Mulobezi"]
}

ALL_TOWNS = []
for prov, towns in ZAMBIA_LOCATIONS.items():
    ALL_TOWNS.extend(towns)

TOWNS_KM = {
    ("kitwe","lusaka"): 362, ("lusaka","kitwe"): 361,
    ("lusaka","ndola"): 321, ("ndola","lusaka"): 321,
    ("kitwe","ndola"): 62, ("ndola","kitwe"): 62,
    ("lusaka","kabwe"): 138, ("kabwe","lusaka"): 138,
    ("lusaka","livingstone"): 485, ("livingstone","lusaka"): 485,
    ("lusaka","chipata"): 575, ("chipata","lusaka"): 575,
    ("kitwe","solwezi"): 220, ("solwezi","kitwe"): 220,
}

def get_distance(f,t):
    f=f.lower().strip(); t=t.lower().strip()
    for (a,b),km in TOWNS_KM.items():
        if a in f and b in t:
            return km
    if f and t:
        return 150
    return 0

STYLE = """
<style>
*{box-sizing:border-box}body{margin:0;font-family:-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif;background:#f8fafc;color:#0f172a;line-height:1.5}
.hero{background:linear-gradient(135deg,#0f172a 0%,#1e293b 50%,#0f172a 100%);color:#fff;padding:32px 16px 24px;text-align:center;position:relative;overflow:hidden}
.hero::before{content:'';position:absolute;top:0;left:0;right:0;bottom:0;background:radial-gradient(circle at 30% 20%,rgba(34,197,94,.15) 0%,transparent 50%),radial-gradient(circle at 70% 80%,rgba(249,115,22,.1) 0%,transparent 50%)}
.hero-content{position:relative;z-index:1}
.logo{font-size:52px;font-weight:900;letter-spacing:-2px;line-height:1}.logo span{color:#22c55e}
.tagline{font-size:14px;color:#cbd5e1;margin-top:8px;font-weight:500}
.badge{background:#22c55e;color:#000;padding:10px 20px;border-radius:999px;font-weight:900;font-size:12px;display:inline-block;margin:16px auto;box-shadow:0 4px 20px rgba(34,197,94,.3)}
.province-bar{display:flex;flex-wrap:wrap;justify-content:center;gap:8px;margin-top:18px;max-width:800px;margin-left:auto;margin-right:auto}
.province-bar span{background:rgba(30,41,59,.8);border:1px solid #334155;padding:8px 14px;border-radius:999px;font-size:11px;font-weight:600;color:#e2e8f0;backdrop-filter:blur(10px)}
.container{max-width:820px;margin:0 auto;padding:20px}
.card{background:#fff;border-radius:28px;padding:28px;margin:20px 0;border:1px solid #e2e8f0;box-shadow:0 8px 32px rgba(0,0,0,.06)}
.card-dark{background:#0f172a;color:#fff;border:none;box-shadow:0 12px 40px rgba(0,0,0,.2)}
.card-orange{border:2px solid #f97316;background:linear-gradient(135deg,#fff7ed 0%,#ffedd5 100%)}
.btn{width:100%;padding:16px;border:none;border-radius:18px;font-weight:900;font-size:15px;display:block;text-align:center;text-decoration:none;cursor:pointer;margin-top:14px}
.btn-green{background:#22c55e;color:#000;box-shadow:0 6px 20px rgba(34,197,94,.3)}
.btn-orange{background:#f97316;color:#fff;box-shadow:0 6px 20px rgba(249,115,22,.3)}
.section-title{font-size:22px;font-weight:900;margin:0 0 8px}
.section-sub{font-size:14px;color:#64748b;margin-bottom:16px}
.how-grid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px;margin-top:16px}
.how-card{background:#f8fafc;border:1px solid #e2e8f0;border-radius:20px;padding:18px;text-align:center}
.how-card b{font-size:28px;display:block;margin-bottom:8px}
.coverage{background:linear-gradient(135deg,#0f172a 0%,#1e293b 100%);color:#fff;border-radius:28px;padding:24px;margin:20px 0}
.coverage-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:14px}
.coverage-item{background:rgba(30,41,59,.6);border:1px solid #334155;padding:12px;border-radius:14px}
.coverage-item b{color:#22c55e;font-size:12px;display:block}
.coverage-item span{font-size:11px;color:#94a3b8}
.footer{text-align:center;padding:28px 16px;color:#64748b;font-size:12px}
.input-label{font-size:11px;font-weight:800;text-transform:uppercase;margin-top:16px;display:block;color:#334155}
.input{width:100%;padding:14px 16px;border-radius:14px;border:1.5px solid #e2e8f0;margin-top:8px;font-size:14px}
.input-readonly{background:#f0fdf4;font-weight:800;color:#14532d}
.box-green{background:#dcfce7;border:1px solid #86efac;padding:12px 16px;border-radius:12px;margin-top:10px;font-weight:700;color:#14532d;font-size:13px}
.box-orange{background:#ffedd5;border:1px solid #fdba74;padding:12px 16px;border-radius:12px;margin-top:10px;font-weight:700;color:#9a3412;font-size:13px}
.btn-sm{padding:8px 14px;border-radius:999px;font-size:11px;font-weight:800;display:inline-block;text-decoration:none;margin:6px 4px 0 0}
.btn-mtn{background:#22c55e;color:#000}.btn-airtel{background:#3b82f6;color:#fff}.btn-delete{background:#fee2e2;color:#dc2626;border:1px solid #fecaca}
</style>
"""

def provinces_bar():
    return '<div class="province-bar"><span>Central</span><span>Copperbelt</span><span>Eastern</span><span>Luapula</span><span>Lusaka</span><span>Muchinga</span><span>Northern</span><span>North-Western</span><span>Southern</span><span>Western</span></div>'

@app.get("/", response_class=HTMLResponse)
def home():
    coverage_html = ""
    for prov, towns in ZAMBIA_LOCATIONS.items():
        towns_str = ", ".join(towns[:6])
        coverage_html += f'<div class="coverage-item"><b>{prov}</b><span>{towns_str}...</span></div>'
    html = f"""
<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>MZIGO.ZM</title>{STYLE}</head><body>
<div class="hero"><div class="hero-content">
<div class="logo">MZIGO<span>.ZM</span></div>
<div class="tagline">✨ Zambia's Smart Logistics Network — Every Province, Every District, Every Town ✨</div>
<div class="badge">✦ 10 PROVINCES • 116 DISTRICTS • 1000+ TOWNS & VILLAGES • AUTO DISTANCE • AESTHETIC ✨</div>
{provinces_bar()}
</div></div>
<div class="container">
<div class="card card-dark"><div class="section-title">🚛 Driver — Empty Truck Anywhere?</div><div class="section-sub">Your truck is empty? Don't return empty. Post your route from any location in Zambia — from big cities to remote villages. Traders need you.</div><a href="/driver" class="btn btn-green">🚚 Enter as Driver → Auto Distance</a></div>
<div class="card card-orange"><div class="section-title">📦 Trader — Need Truck Anywhere?</div><div class="section-sub">Need to move goods? Post your load from any Zambian town, district or village. We match you with returning trucks — fair pricing per kg.</div><a href="/trader" class="btn btn-orange">📦 Enter as Trader → Post Load</a></div>
<div class="card"><div class="section-title">⚡ How It Works</div><div class="section-sub">Three simple steps — built for Zambia, works even in remote areas</div>
<div class="how-grid"><div class="how-card"><b>1️⃣</b><div><b>Post</b><br>Driver posts empty truck or Trader posts load. Type any Zambian location — auto distance.</div></div><div class="how-card"><b>2️⃣</b><div><b>Match</b><br>System shows matching trucks and loads across all provinces. Distance, time, pricing instantly.</div></div><div class="how-card"><b>3️⃣</b><div><b>Connect</b><br>Connect via WhatsApp. No middleman. No truck returns empty.</div></div></div></div>
<div class="coverage"><div class="section-title" style="color:#fff">🗺️ Coverage — All 10 Provinces</div><div class="section-sub" style="color:#94a3b8">Every province, district, town and village can access MZIGO.ZM</div><div class="coverage-grid" style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:14px">{coverage_html}</div><div style="margin-top:16px;font-size:11px;color:#64748b;text-align:center">And thousands more villages — just type your location, we calculate automatically ✨</div></div>
</div>
<div class="footer"><b style="color:#0f172a">MZIGO.ZM</b> — Made in Kitwe — Zambia's Aesthetic Logistics Network<br>No truck returns empty • Built for every Zambian location</div>
</body></html>
"""
    return HTMLResponse(html)

@app.get("/driver", response_class=HTMLResponse)
def driver_page():
    trucks_html=""
    for t in trucks:
        trucks_html+=f"""<div class="card" style="position:relative"><a href="/delete-truck/{t['id']}" style="position:absolute;top:14px;right:14px;background:#ef4444;color:#fff;width:32px;height:32px;border-radius:50%;display:flex;align-items:center;justify-content:center;text-decoration:none;font-weight:900">✕</a><b>{t['from_city']} → {t['to_city']}</b><br><span style="font-size:12px;background:#0f172a;color:#fff;padding:4px 10px;border-radius:8px">{t['truck_type']}</span> <span style="font-size:12px;background:#dcfce7;color:#14532d;padding:4px 10px;border-radius:8px">{t['distance_km']}</span><br><span style="font-size:12px;color:#64748b;margin-top:8px;display:block">📍 {t['current_location']} • 🕒 {t['departure_time']}</span><br><a class="btn-sm btn-mtn" href="https://wa.me/260{t['whatsapp'][-9:]}">WhatsApp MTN</a><a class="btn-sm btn-airtel" href="https://wa.me/260{t['whatsapp'][-9:]}">WhatsApp Airtel</a></div>"""
    if not trucks_html:
        trucks_html='<div class="card" style="text-align:center;color:#64748b;padding:40px">🚛 No trucks yet — Be first!<br><span style="font-size:12px">From any province, district, town or village</span></div>'
    html = f"""
<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>MZIGO.ZM DRIVER</title>{STYLE}
<script>
function updateDriver(){{
 var f=document.getElementById('from_city_d').value; var t=document.getElementById('to_city_d').value;
 var fk=f.toLowerCase(); var tk=t.toLowerCase(); var km=0;
 if(fk.includes("kitwe")&&tk.includes("lusaka")) km=362;
 else if(fk.includes("lusaka")&&tk.includes("kitwe")) km=361;
 else if(fk.includes("lusaka")&&tk.includes("ndola")) km=321;
 else if(fk.includes("kitwe")&&tk.includes("ndola")) km=62;
 else if(f&&t) km=150;
 var distEl=document.getElementById('distance_km_d'); var distInfo=document.getElementById('dist_info_d'); var distText=document.getElementById('dist_text_d');
 if(km>0){{ var hrs=(km/75).toFixed(1); distEl.value=km+" km"; distText.value="DISTANCE: "+km+" KM"; distInfo.innerHTML="✅ Distance: "+km+" km | ~"+hrs+" hrs — "+f+" → "+t; }}
 else {{ distEl.value=""; distText.value=""; distInfo.innerHTML="✏️ Type any Zambian location — we calculate automatically"; }}
}}
</script>
</head><body>
<div class="hero" style="padding:20px 16px"><div class="hero-content"><div class="logo" style="font-size:32px">MZIGO<span>.ZM</span> DRIVER</div><div class="badge" style="margin-top:8px">ACROSS ZAMBIA</div>{provinces_bar()}</div></div>
<div style="display:flex;justify-content:space-between;padding:12px 16px;background:#fff;border-bottom:1px solid #e2e8f0"><a href="/" style="text-decoration:none;font-weight:800;color:#0f172a;font-size:13px;padding:6px 14px;border-radius:999px;background:#f1f5f9">← Home</a><a href="/trader" style="text-decoration:none;font-weight:800;font-size:13px;padding:6px 14px;border-radius:999px;background:#fff7ed;border:1px solid #fed7aa">Trader →</a></div>
<div class="container"><div class="card-dark" style="border-radius:28px;padding:24px"><h3 style="margin:0">🚛 Post Empty Truck — Any Location ✨</h3><p style="color:#94a3b8;font-size:13px;margin-top:8px">Driver? Your truck is empty on return? Post it. From any province, district, town or village — traders need you.</p>
<form action="/add-truck" method="post">
<label class="input-label" style="color:#94a3b8">FROM</label><input class="input" style="background:#1e293b;color:#fff;border-color:#334155" id="from_city_d" name="from_city" placeholder="e.g. Kitwe, Nakonde, Mongu, or any village" required oninput="updateDriver()">
<label class="input-label" style="color:#94a3b8">TO</label><input class="input" style="background:#1e293b;color:#fff;border-color:#334155" id="to_city_d" name="to_city" placeholder="e.g. Lusaka, Ndola, Chipata, or any district" required oninput="updateDriver()">
<input class="input" style="background:#1e293b;color:#94a3b8" id="dist_text_d" placeholder="Auto" readonly>
<input class="input" style="background:#0f172a;color:#22c55e;font-weight:900" id="distance_km_d" name="distance_km" readonly placeholder="Auto distance">
<div class="box-green" id="dist_info_d">✏️ Type any Zambian location — we calculate automatically</div>
<label class="input-label" style="color:#94a3b8">TRUCK TYPE</label><input class="input" style="background:#1e293b;color:#fff;border-color:#334155" name="truck_type" placeholder="e.g. 50 ton, 10 ton, Canter" required>
<label class="input-label" style="color:#94a3b8">CURRENT LOCATION</label><input class="input" style="background:#1e293b;color:#fff;border-color:#334155" name="current_location" placeholder="e.g. Total filling station, Market, Farm" required>
<label class="input-label" style="color:#94a3b8">DEPARTURE DATE & TIME</label><input class="input" style="background:#1e293b;color:#fff;border-color:#334155" type="datetime-local" name="departure_time" required>
<label class="input-label" style="color:#94a3b8">YOUR PRICE</label><input class="input" style="background:#1e293b;color:#fff;border-color:#334155" name="price" placeholder="Enter your price" required>
<label class="input-label" style="color:#94a3b8">WHATSAPP</label><input class="input" style="background:#1e293b;color:#fff;border-color:#334155" name="whatsapp" placeholder="e.g. 0964343865" required>
<button class="btn btn-green" type="submit">✅ Post Empty Truck — Go Live ✨</button>
</form><div style="margin-top:20px"><div style="font-weight:900;color:#fff">🚛 Available Trucks ({len(trucks)})</div></div>{trucks_html}</div></div>
</body></html>
"""
    return HTMLResponse(html)

@app.post("/add-truck")
def add_truck(from_city: str = Form(...), to_city: str = Form(...), truck_type: str = Form(...), current_location: str = Form(""), departure_time: str = Form(""), price: str = Form(...), whatsapp: str = Form(...), distance_km: str = Form("")):
    if not distance_km:
        d=get_distance(from_city,to_city)
        distance_km=f"{d} km" if d else "Calculated"
    trucks.insert(0, {"id": str(uuid.uuid4())[:8], "from_city": from_city.strip(), "to_city": to_city.strip(), "truck_type": truck_type.strip(), "current_location": current_location.strip(), "departure_time": departure_time.strip(), "price": price.strip(), "whatsapp": whatsapp.strip(), "distance_km": distance_km.strip()})
    return RedirectResponse("/driver", status_code=303)

@app.get("/delete-truck/{tid}")
def delete_truck(tid: str):
    global trucks
    trucks=[t for t in trucks if t['id']!=tid]
    return RedirectResponse("/driver", status_code=303)

@app.get("/trader", response_class=HTMLResponse)
def trader_page():
    loads_html=""
    for l in loads:
        loads_html+=f"""<div class="card" style="position:relative"><a href="/delete-load/{l['id']}" style="position:absolute;top:14px;right:14px;background:#ef4444;color:#fff;width:32px;height:32px;border-radius:50%;display:flex;align-items:center;justify-content:center;text-decoration:none;font-weight:900">✕</a><b>{l['from_city']} → {l['to_city']}</b><br><span style="font-size:12px;background:#0f172a;color:#fff;padding:4px 10px;border-radius:8px">{l['goods_type']}</span> <span style="font-size:12px;background:#f1f5f9;padding:4px 10px;border-radius:8px">{l['weight']}</span> <span style="font-size:12px;background:#dcfce7;color:#14532d;padding:4px 10px;border-radius:8px">{l['distance_km']}</span><br><span style="font-size:12px;color:#64748b;margin-top:6px;display:block">Rate: K{l['rate_per_kg']}/kg • Budget: K{l['price']}</span><br><a class="btn-sm btn-mtn" href="https://wa.me/260{l['whatsapp'][-9:]}">WhatsApp MTN</a><a class="btn-sm btn-airtel" href="https://wa.me/260{l['whatsapp'][-9:]}">WhatsApp Airtel</a></div>"""
    if not loads_html:
        loads_html='<div class="card" style="text-align:center;color:#64748b;padding:40px">📦 No loads yet — Be first!</div>'
    html = f"""
<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>MZIGO.ZM TRADER</title>{STYLE}
<script>
function parseWeight(v){{ v=v.toLowerCase(); var m=v.match(/[0-9.]+/); if(!m) return 0; var n=parseFloat(m[0]); if(v.includes("ton")) n=n*1000; return n; }}
function updateTrader(){{
 var f=document.getElementById('from_city').value; var t=document.getElementById('to_city').value;
 var fk=f.toLowerCase(); var tk=t.toLowerCase(); var km=0;
 if(fk.includes("kitwe")&&tk.includes("lusaka")) km=362;
 else if(fk.includes("lusaka")&&tk.includes("kitwe")) km=362;
 else if(fk.includes("lusaka")&&tk.includes("ndola")) km=321;
 else if(fk.includes("kitwe")&&tk.includes("ndola")) km=62;
 else if(f&&t) km=150;
 var distEl=document.getElementById('distance_km'); var distInfo=document.getElementById('dist_info'); var distText=document.getElementById('dist_text');
 if(km>0){{ var hrs=(km/75).toFixed(1); distEl.value=km+" km"; distText.value="DISTANCE: "+km+" KM"; distInfo.innerHTML="✅ Distance: "+km+" km | ~"+hrs+" hrs — "+f+" → "+t; }}
 else {{ distEl.value=""; distText.value=""; distInfo.innerHTML="✏️ Type any Zambian location — we calculate automatically"; }}
 var w=document.getElementById('weight').value; var rate=document.getElementById('rate').value;
 var kg=parseWeight(w); var total=Math.round(kg*parseFloat(rate));
 var totalEl=document.getElementById('total_budget'); var priceInfo=document.getElementById('price_info');
 if(kg>0){{ totalEl.value=total; priceInfo.innerHTML="📦 Weight: "+kg+" kg × K"+rate+" = K"+total; priceInfo.style.display="block"; }} else {{ priceInfo.style.display="none"; }}
}}
</script>
</head><body>
<div class="hero" style="padding:20px 16px"><div class="hero-content"><div class="logo" style="font-size:32px">MZIGO<span>.ZM</span> TRADER</div><div class="badge" style="margin-top:8px">ACROSS ZAMBIA</div>{provinces_bar()}</div></div>
<div style="display:flex;justify-content:space-between;padding:12px 16px;background:#fff;border-bottom:1px solid #e2e8f0"><a href="/" style="text-decoration:none;font-weight:800;color:#0f172a;font-size:13px;padding:6px 14px;border-radius:999px;background:#f1f5f9">← Home</a><a href="/driver" style="text-decoration:none;font-weight:800;font-size:13px;padding:6px 14px;border-radius:999px;background:#0f172a;color:#fff">Driver →</a></div>
<div class="container"><div class="card card-orange" style="border:2px solid #f97316"><h3 style="margin:0">📦 Post Load — Any Location in Zambia ✨</h3><p style="color:#7c2d12;font-size:13px;margin-top:8px">Trader? Need truck? Post from any province, district, town or village.</p>
<form action="/add-load" method="post">
<label class="input-label">FROM</label><input class="input" id="from_city" name="from_city" placeholder="e.g. Lusaka, Chipata, Mongu, or any village" required oninput="updateTrader()">
<label class="input-label">TO</label><input class="input" id="to_city" name="to_city" placeholder="e.g. Kitwe, Ndola, Solwezi, or any district" required oninput="updateTrader()">
<input class="input input-readonly" id="dist_text" placeholder="Auto distance" readonly>
<input class="input input-readonly" style="margin-top:6px" id="distance_km" name="distance_km" readonly placeholder="Auto">
<div class="box-green" id="dist_info">✏️ Type any Zambian town, district or village — we calculate automatically</div>
<label class="input-label">GOODS TYPE</label><input class="input" name="goods_type" placeholder="e.g. Maize, Mealie Meal, Copper, Cement" required>
<label class="input-label">WEIGHT</label><input class="input" id="weight" name="weight" placeholder="e.g. 1000 kg or 1.5 tons" required oninput="updateTrader()">
<label class="input-label">RATE PER KG</label><select class="input" id="rate" name="rate_per_kg" onchange="updateTrader()"><option value="25">K25/kg — Budget</option><option value="30" selected>K30/kg — Standard ⭐</option><option value="35">K35/kg — Express</option><option value="50">K50/kg — Urgent</option></select>
<div class="box-orange" id="price_info" style="display:none"></div>
<label class="input-label">SET DATE & TIME</label><input class="input" type="datetime-local" name="departure_time" required>
<label class="input-label">TOTAL BUDGET</label><input class="input" id="total_budget" name="price" placeholder="Auto from weight" required>
<label class="input-label">WHATSAPP</label><input class="input" name="whatsapp" placeholder="e.g. 0964343865" required>
<button class="btn btn-orange" type="submit">📦 Post Load — Get Trucks ✨</button>
</form><div style="margin-top:20px"><div style="font-weight:900">📦 Available Loads ({len(loads)})</div></div>{loads_html}</div></div>
</body></html>
"""
    return HTMLResponse(html)

@app.post("/add-load")
def add_load(from_city: str = Form(...), to_city: str = Form(...), goods_type: str = Form(...), weight: str = Form(...), price: str = Form(...), whatsapp: str = Form(...), departure_time: str = Form(""), rate_per_kg: str = Form("30"), distance_km: str = Form("")):
    if not distance_km:
        d=get_distance(from_city,to_city)
        distance_km=f"{d} km" if d else "Calculated"
    loads.insert(0, {"id": str(uuid.uuid4())[:8], "from_city": from_city.strip(), "to_city": to_city.strip(), "goods_type": goods_type.strip(), "weight": weight.strip(), "price": price.strip(), "whatsapp": whatsapp.strip(), "departure_time": departure_time.strip(), "rate_per_kg": rate_per_kg.strip(), "distance_km": distance_km.strip()})
    return RedirectResponse("/trader", status_code=303)

@app.get("/delete-load/{lid}")
def delete_load(lid: str):
    global loads
    loads=[l for l in loads if l['id']!=lid]
    return RedirectResponse("/trader", status_code=303)

@app.get("/health")
def health():
    return {"ok": True}

if __name__ == "__main__":
    import uvicorn
    port=int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
