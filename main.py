from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import math
import os
from datetime import datetime, timedelta
import random

app = FastAPI(title="Mzigo - Find empty trucks")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Zambia towns GPS - 70 towns for distance calc
ZAMBIA_TOWNS = {
    "Kitwe": (-12.8013, 28.2132),
    "Lusaka": (-15.4067, 28.2871),
    "Ndola": (-12.9587, 28.6366),
    "Kabwe": (-14.4469, 28.4464),
    "Livingstone": (-17.8419, 25.8543),
    "Chipata": (-13.6469, 32.5884),
    "Kasama": (-10.2092, 31.1809),
    "Solwezi": (-12.1807, 26.3890),
    "Chingola": (-12.5283, 27.8569),
    "Mufulira": (-12.5361, 28.2385),
    "Luanshya": (-13.1350, 28.4021),
    "Kalulushi": (-12.8377, 28.0913),
    "Chililabombwe": (-12.3655, 27.8364),
    "Mongu": (-15.2546, 23.1282),
    "Mazabuka": (-15.8615, 27.7439),
    "Choma": (-16.8103, 27.1316),
    "Monze": (-16.2713, 27.4756),
    "Kafue": (-15.7714, 28.1826),
    "Kapiri Mposhi": (-13.9788, 28.6841),
    "Mkushi": (-13.6224, 29.3924),
    "Serenje": (-13.2326, 30.2328),
    "Mpika": (-11.8371, 31.4528),
    "Chinsali": (-10.5507, 32.0704),
    "Isoka": (-10.1557, 32.6363),
    "Nakonde": (-9.3447, 32.7581),
    "Mansa": (-11.1995, 28.8931),
    "Samfya": (-11.3619, 29.5562),
    "Kawambwa": (-9.7943, 28.7713),
    "Mwense": (-10.3831, 28.6990),
    "Chipili": (-11.2000, 29.0000),
    "Chembe": (-11.8000, 28.7000),
    "Mwinilunga": (-11.7357, 24.4297),
    "Zambezi": (-13.5431, 23.1097),
    "Kabompo": (-13.6000, 24.2000),
    "Kasempa": (-13.4581, 25.8360),
    "Kaoma": (-14.7833, 24.8000),
    "Senanga": (-16.1167, 23.2667),
    "Sesheke": (-17.4833, 24.3000),
    "Sioma": (-16.7000, 23.6000),
    "Lukulu": (-14.3833, 23.0333),
    "Kalabo": (-14.9936, 22.6811),
    "Shangombo": (-16.3167, 22.1000),
    "Chadiza": (-14.0640, 32.4365),
    "Kasenengwa": (-13.5000, 32.6000),
    "Lumezi": (-12.3000, 33.2000),
    "Lundazi": (-12.2941, 33.1746),
    "Mambwe": (-13.3500, 32.0000),
    "Nyimba": (-14.5567, 30.8144),
    "Petauke": (-14.2425, 31.3256),
    "Sinda": (-14.5000, 32.0000),
    "Vubwi": (-14.0000, 32.9000),
    "Katete": (-14.0548, 32.0446),
    "Chama": (-11.2167, 32.3500),
    "Mafinga": (-10.2000, 33.3000),
    "Mpulungu": (-8.7756, 31.1236),
    "Mbala": (-8.8402, 31.3609),
    "Mporokoso": (-9.3667, 30.1000),
    "Kaputa": (-8.5000, 29.2000),
    "Nsama": (-8.8000, 30.2000),
    "Chienge": (-8.6000, 29.1000),
    "Nchelenge": (-9.3500, 28.7333),
    "Mwansabombwe": (-9.8000, 28.9000),
    "Milenge": (-11.9000, 28.9000),
    "Lufwanyama": (-13.0000, 27.5000),
    "Masaiti": (-13.2000, 28.4000),
    "Mpongwe": (-13.5000, 28.1000),
    "Lunga": (-11.5000, 29.3000),
    "Lufubu": (-12.0000, 28.8000),
    "Chibombo": (-14.6597, 28.0921),
    "Mumbwa": (-14.9858, 27.0617),
    "Itezhi Tezhi": (-15.7583, 26.0333),
    "Namwala": (-15.7500, 26.4500),
    "Pemba": (-16.5333, 27.3667),
    "Gwembe": (-16.5000, 27.6000),
    "Sinazongwe": (-17.2667, 27.4500),
    "Kalomo": (-17.0456, 26.5004),
    "Zimba": (-17.3167, 26.2000),
}

def calc_distance_km(from_town, to_town):
    # Haversine with road factor 1.38 - Kitwe-Lusaka verified 362km
    a = ZAMBIA_TOWNS.get(from_town)
    b = ZAMBIA_TOWNS.get(to_town)
    if not a or not b:
        return None
    lat1, lon1 = a
    lat2, lon2 = b
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    x = math.sin(dlat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(x), math.sqrt(1-x))
    straight = R * c
    road = straight * 1.38
    # verified fixes
    if (from_town == "Kitwe" and to_town == "Lusaka") or (from_town == "Lusaka" and to_town == "Kitwe"):
        return 362
    if (from_town == "Ndola" and to_town == "Lusaka") or (from_town == "Lusaka" and to_town == "Ndola"):
        return 321
    if (from_town == "Kitwe" and to_town == "Ndola") or (from_town == "Ndola" and to_town == "Kitwe"):
        return 58
    return int(round(road))

# Live empty trucks - Yango style list - NO PHONE NUMBERS IN UI
TRUCKS = [
    {"id": 1, "from": "Kitwe", "to": "Lusaka", "type": "10 Ton", "depart": "Today 5:30 PM", "price": 22000, "space": "8 ton", "rating": 4.8, "empty": True},
    {"id": 2, "from": "Ndola", "to": "Lusaka", "type": "15 Ton", "depart": "Today 6:00 PM", "price": 28500, "space": "12 ton", "rating": 4.9, "empty": True},
    {"id": 3, "from": "Kitwe", "to": "Lusaka", "type": "30 Ton", "depart": "Tomorrow 6:00 AM", "price": 45000, "space": "20 ton", "rating": 4.7, "empty": True},
    {"id": 4, "from": "Lusaka", "to": "Ndola", "type": "10 Ton", "depart": "Today 7:15 PM", "price": 20000, "space": "10 ton", "rating": 4.8, "empty": False},
    {"id": 5, "from": "Kitwe", "to": "Chipata", "type": "20 Ton", "depart": "Tomorrow 5:00 AM", "price": 38000, "space": "15 ton", "rating": 4.6, "empty": True},
    {"id": 6, "from": "Solwezi", "to": "Lusaka", "type": "30 Ton", "depart": "Today 8:00 PM", "price": 52000, "space": "25 ton", "rating": 4.9, "empty": True},
    {"id": 7, "from": "Livingstone", "to": "Lusaka", "type": "10 Ton", "depart": "Tomorrow 7:00 AM", "price": 26000, "space": "6 ton", "rating": 4.7, "empty": True},
    {"id": 8, "from": "Kitwe", "to": "Solwezi", "type": "15 Ton", "depart": "Today 6:30 PM", "price": 18500, "space": "10 ton", "rating": 4.8, "empty": False},
    {"id": 9, "from": "Lusaka", "to": "Kitwe", "type": "20 Ton", "depart": "Tomorrow 6:30 AM", "price": 24000, "space": "18 ton", "rating": 4.9, "empty": True},
    {"id": 10, "from": "Ndola", "to": "Solwezi", "type": "10 Ton", "depart": "Today 5:45 PM", "price": 19500, "space": "7 ton", "rating": 4.5, "empty": True},
    {"id": 11, "from": "Kabwe", "to": "Lusaka", "type": "5 Ton", "depart": "Today 6:15 PM", "price": 12000, "space": "3 ton", "rating": 4.6, "empty": True},
    {"id": 12, "from": "Chipata", "to": "Lusaka", "type": "30 Ton", "depart": "Tomorrow 4:00 AM", "price": 48000, "space": "22 ton", "rating": 4.8, "empty": True},
    {"id": 13, "from": "Kitwe", "to": "Livingstone", "type": "15 Ton", "depart": "Tomorrow 8:00 AM", "price": 35000, "space": "12 ton", "rating": 4.7, "empty": False},
    {"id": 14, "from": "Mansa", "to": "Ndola", "type": "10 Ton", "depart": "Today 7:00 PM", "price": 18000, "space": "9 ton", "rating": 4.6, "empty": True},
    {"id": 15, "from": "Lusaka", "to": "Chipata", "type": "20 Ton", "depart": "Tomorrow 5:30 AM", "price": 40000, "space": "14 ton", "rating": 4.9, "empty": True},
]

def find_trucks(to_filter):
    if not to_filter:
        return TRUCKS[:8]
    tf = to_filter.strip().lower()
    out = [t for t in TRUCKS if tf in t["to"].lower() or tf in t["from"].lower()]
    return out if out else TRUCKS[:6]

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1"/>
<title>Mzigo - Find empty trucks</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
:root{--yellow:#FFCC00;--black:#111111;--white:#FFFFFF;--gray:#F5F5F5;--gray2:#E8E8E8;--green:#22C55E;--text:#111111;--text2:#6B7280;}
*{margin:0;padding:0;box-sizing:border-box;font-family:Inter,system-ui,-apple-system,sans-serif;}
body{background:var(--white);color:var(--black);-webkit-font-smoothing:antialiased;}
.header{position:sticky;top:0;z-index:20;background:var(--yellow);padding:14px 16px 12px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid rgba(0,0,0,0.08);}
.logo{font-weight:800;font-size:22px;letter-spacing:-0.5px;display:flex;align-items:center;gap:8px;}
.logo span{width:32px;height:32px;background:var(--black);color:var(--yellow);border-radius:9px;display:flex;align-items:center;justify-content:center;font-size:18px;}
.menu{display:flex;gap:8px;}
.menu div{width:36px;height:36px;background:rgba(0,0,0,0.08);border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:18px;}
.search-wrap{background:var(--yellow);padding:0 16px 18px;}
.search-pill{background:var(--white);border-radius:24px;padding:6px 6px 6px 16px;display:flex;align-items:center;gap:10px;box-shadow:0 4px 20px rgba(0,0,0,0.12);}
.search-pill input{flex:1;border:none;outline:none;font-size:16px;font-weight:500;background:transparent;padding:10px 0;}
.search-pill button{background:var(--black);color:var(--white);border:none;border-radius:18px;padding:10px 18px;font-weight:600;font-size:14px;}
.chips{display:flex;gap:8px;margin-top:12px;overflow-x:auto;scrollbar-width:none;}
.chips::-webkit-scrollbar{display:none;}
.chip{background:rgba(0,0,0,0.08);border:none;border-radius:20px;padding:8px 14px;font-size:13px;font-weight:600;white-space:nowrap;}
.chip.active{background:var(--black);color:var(--white);}
.map{background:var(--gray);height:132px;position:relative;overflow:hidden;display:flex;align-items:center;justify-content:center;}
.map-line{position:absolute;top:50%;left:16%;right:16%;height:3px;background:repeating-linear-gradient(90deg,var(--black) 0 8px,transparent 8px 14px);border-radius:2px;opacity:0.25;}
.map-dots{display:flex;gap:80px;position:relative;z-index:1;}
.map-dot{width:48px;height:48px;background:var(--white);border-radius:16px;display:flex;align-items:center;justify-content:center;box-shadow:0 4px 16px rgba(0,0,0,0.12);font-weight:700;font-size:12px;flex-direction:column;gap:2px;}
.map-dot b{font-size:11px;}
.sheet{background:var(--white);border-radius:32px 32px 0 0;margin-top:-20px;position:relative;z-index:2;min-height:520px;box-shadow:0 -8px 30px rgba(0,0,0,0.08);padding:16px 16px 120px;}
.handle{width:36px;height:4px;background:var(--gray2);border-radius:2px;margin:0 auto 14px;}
.sheet-title{display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;}
.sheet-title h2{font-size:18px;font-weight:700;letter-spacing:-0.3px;}
.sheet-title span{font-size:13px;color:var(--text2);font-weight:500;}
.card{background:var(--white);border:1px solid var(--gray2);border-radius:20px;padding:14px 14px 12px;margin-bottom:12px;transition:transform 0.15s;}
.card:active{transform:scale(0.99);}
.row1{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;}
.row1 .route{font-weight:700;font-size:15px;display:flex;align-items:center;gap:6px;}
.row1 .km{font-size:12px;color:var(--text2);background:var(--gray);padding:4px 8px;border-radius:10px;font-weight:600;}
.row2{display:flex;gap:8px;align-items:center;margin-bottom:10px;flex-wrap:wrap;}
.row2 .pill{background:var(--gray);padding:5px 10px;border-radius:12px;font-size:12px;font-weight:600;color:var(--black);}
.row2 .pill.green{background:#DCFCE7;color:#166534;}
.row3{display:flex;justify-content:space-between;align-items:center;}
.price{font-weight:800;font-size:18px;letter-spacing:-0.5px;}
.actions{display:flex;gap:8px;}
.btn{border:none;border-radius:14px;padding:10px 16px;font-weight:700;font-size:13px;cursor:pointer;}
.btn-yellow{background:var(--yellow);color:var(--black);}
.btn-white{background:var(--white);border:1.5px solid var(--gray2);color:var(--black);}
.bottom{position:fixed;bottom:0;left:0;right:0;background:var(--white);border-top:1px solid var(--gray2);display:flex;justify-content:space-around;padding:8px 0 18px;z-index:30;}
.bottom div{display:flex;flex-direction:column;align-items:center;gap:3px;font-size:11px;font-weight:600;color:var(--text2);}
.bottom div.active{color:var(--black);}
.bottom div.active i{background:var(--yellow);}
.bottom i{width:28px;height:28px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:16px;background:transparent;}
.simple-form{display:none;background:var(--white);padding:16px;border-radius:20px;border:1px solid var(--gray2);margin-bottom:12px;}
.simple-form input{width:100%;padding:14px 14px;border:1.5px solid var(--gray2);border-radius:14px;font-size:15px;font-weight:500;margin-bottom:10px;outline:none;}
.simple-form input:focus{border-color:var(--black);}
</style>
</head>
<body>
<div class="header">
<div class="logo"><span>M</span> Mzigo</div>
<div class="menu"><div>≡</div></div>
</div>
<div class="search-wrap">
<div class="search-pill">
<span style="font-size:18px;">🔍</span>
<input id="toInput" placeholder="Where to? e.g. Lusaka" value=""/>
<button onclick="search()">Search</button>
</div>
<div class="chips">
<button class="chip active" onclick="quick('Lusaka')">Lusaka</button>
<button class="chip" onclick="quick('Ndola')">Ndola</button>
<button class="chip" onclick="quick('Kitwe')">Kitwe</button>
<button class="chip" onclick="quick('Solwezi')">Solwezi</button>
<button class="chip" onclick="quick('Chipata')">Chipata</button>
<button class="chip" onclick="quick('Livingstone')">Livingstone</button>
</div>
</div>
<div class="map">
<div class="map-line"></div>
<div class="map-dots">
<div class="map-dot">📍<b>Kitwe</b></div>
<div class="map-dot">→ 362 KM</div>
<div class="map-dot">📍<b>Lusaka</b></div>
</div>
</div>
<div class="sheet">
<div class="handle"></div>
<div class="sheet-title"><h2>Empty trucks going your way</h2><span id="count">8 available</span></div>
<div id="list"></div>
<div class="simple-form" id="driverForm">
<h3 style="font-size:16px;margin-bottom:10px;">Post empty truck</h3>
<input placeholder="From e.g. Kitwe"/>
<input placeholder="To e.g. Lusaka"/>
<input placeholder="Truck type e.g. 10 Ton"/>
<input placeholder="When? e.g. Today 6 PM"/>
<input placeholder="Price e.g. 22000"/>
<button class="btn btn-yellow" style="width:100%;margin-top:6px;">Post truck</button>
</div>
</div>
<div class="bottom">
<div class="active"><i>🏠</i>Home</div>
<div onclick="toggleDriver()"><i>🚚</i>Post</div>
<div><i>📦</i>Orders</div>
<div><i>👤</i>Profile</div>
</div>
<script>
const TRUCKS = __TRUCKS__;
function render(list){
  const c = document.getElementById('list');
  document.getElementById('count').innerText = list.length + ' available';
  c.innerHTML = list.map(t=>`
    <div class="card">
      <div class="row1"><div class="route">🚚 ${t.from} → ${t.to}</div><div class="km">${t.km || 362} km • ${t.type}</div></div>
      <div class="row2"><div class="pill">${t.depart}</div><div class="pill">${t.space} available</div><div class="pill">⭐ ${t.rating}</div>${t.empty ? '<div class="pill green">Empty return</div>' : ''}</div>
      <div class="row3"><div class="price">K${t.price.toLocaleString()}</div><div class="actions"><button class="btn btn-white">Chat</button><button class="btn btn-yellow">Book</button></div></div>
    </div>
  `).join('');
}
function search(){
  const v = document.getElementById('toInput').value.trim();
  fetch('/api/trucks?to=' + encodeURIComponent(v)).then(r=>r.json()).then(d=>render(d));
}
function quick(city){
  document.getElementById('toInput').value = city;
  document.querySelectorAll('.chip').forEach(ch=>ch.classList.remove('active'));
  event.target.classList.add('active');
  search();
}
function toggleDriver(){
  const f = document.getElementById('driverForm');
  f.style.display = f.style.display === 'block' ? 'none' : 'block';
  window.scrollTo({top: 200, behavior: 'smooth'});
}
render(TRUCKS);
</script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def home():
    trucks_json = str(TRUCKS).replace("'", '"')
    # inject km
    enriched = []
    for t in TRUCKS:
        km = calc_distance_km(t["from"], t["to"]) or 362
        nt = dict(t)
        nt["km"] = km
        enriched.append(nt)
    html = HTML_PAGE.replace("__TRUCKS__", str(enriched))
    return html

@app.get("/api/trucks")
def api_trucks(to: str = Query(default="")):
    res = find_trucks(to)
    out = []
    for t in res:
        km = calc_distance_km(t["from"], t["to"]) or 362
        nt = dict(t)
        nt["km"] = km
        out.append(nt)
    return out

@app.get("/health")
def health():
    return {"ok": True, "trucks": len(TRUCKS), "towns": len(ZAMBIA_TOWNS)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
