import os
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse

supabase = None
try:
    from supabase import create_client
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if url and key:
        supabase = create_client(url, key)
except Exception as e:
    print("Supabase off:", e)

app = FastAPI()
trucks_memory = []
loads_memory = []
MTN = "0964343865"
AIRTEL = "0976166422"
PCT = 30

def calc(s):
    try:
        digits = "".join([c for c in str(s) if c.isdigit()])
        b = int(digits) if digits else 0
        fee = b * PCT // 100
        total = b + fee
        return b, fee, total
    except:
        return 0,0,s

STYLE = """
<style>
*{box-sizing:border-box}body{margin:0;font-family:sans-serif;background:#f8fafc;color:#0f172a}
header{background:#0f172a;color:#fff;padding:20px 16px;text-align:center}
.logo{font-size:28px;font-weight:900}.logo span{color:#22c55e}
.desc{font-size:13px;line-height:1.4;opacity:.85;max-width:600px;margin:8px auto;color:#cbd5e1}
.badge-across{background:#22c55e;color:#000;padding:6px 16px;border-radius:20px;font-weight:900;font-size:12px;display:inline-block;margin:10px 0 6px;letter-spacing:2px}
.provinces{font-size:10px;opacity:.6;line-height:1.6;max-width:650px;margin:0 auto}
.provinces span{background:#1e293b;padding:3px 8px;border-radius:12px;margin:2px;display:inline-block;border:1px solid #334155}
.container{max-width:700px;margin:0 auto;padding:14px}
.card{background:#fff;border-radius:18px;padding:18px;margin-bottom:14px;border:1px solid #e2e8f0;box-shadow:0 4px 12px rgba(0,0,0,.04)}
.btn{width:100%;padding:14px;border:none;border-radius:12px;font-weight:900;margin-top:10px;cursor:pointer;display:block;text-align:center;text-decoration:none}
.btn-green{background:#22c55e;color:#000}
.btn-dark{background:#0f172a;color:#fff}
.btn-orange{background:#f97316;color:#fff}
input{width:100%;padding:12px;border-radius:10px;border:1.5px solid #e2e8f0;margin-top:6px;background:#f8fafc;font-size:14px}
label{font-size:11px;font-weight:800;color:#334155;margin-top:10px;display:block;letter-spacing:.5px;text-transform:uppercase}
.badge{font-size:11px;padding:4px 10px;border-radius:20px;font-weight:800;display:inline-block;margin:2px}
.bp{background:#0f172a;color:#fff}
.bf{background:#fef3c7;color:#92400e}
.wa{display:block;margin-top:10px;background:#22c55e;color:#000;text-align:center;padding:12px;border-radius:10px;text-decoration:none;font-weight:900}
.back{display:inline-block;margin-bottom:12px;background:#e2e8f0;padding:8px 14px;border-radius:20px;text-decoration:none;color:#000;font-weight:800;font-size:12px}
.small{font-size:12px;color:#64748b;margin-top:4px}
.auto-box{background:#dcfce7;border:1px dashed #22c55e;padding:10px;border-radius:10px;margin-top:8px;font-size:12px;font-weight:700;color:#14532d}
</style>
"""

JS = """
<script>
const towns = {
"lusaka": [-15.4067,28.2871], "kitwe": [-12.8024,28.2132], "ndola": [-12.9587,28.6365],
"kabwe": [-14.4439,28.4506], "livingstone": [-17.8528,25.8553], "chipata": [-13.6296,32.6467],
"kasama": [-10.2107,31.1749], "mansa": [-11.1998,28.8934], "mongu": [-15.2667,23.1167],
"solwezi": [-12.1735,26.3865], "chingola": [-12.5256,27.8824], "choma": [-16.8112,26.9979],
"mwinilunga": [-11.7357,24.4298], "nakonde": [-9.3359,32.7537]
};
function haversine(lat1,lon1,lat2,lon2){
  const R=6371; const dLat=(lat2-lat1)*Math.PI/180; const dLon=(lon2-lon1)*Math.PI/180;
  const a=Math.sin(dLat/2)**2 + Math.cos(lat1*Math.PI/180)*Math.cos(lat2*Math.PI/180)*Math.sin(dLon/2)**2;
  return R*2*Math.atan2(Math.sqrt(a),Math.sqrt(1-a));
}
async function calcDist(){
  const fromEl=document.getElementById('from_city');
  const toEl=document.getElementById('to_city');
  const distEl=document.getElementById('distance_km');
  const labelEl=document.getElementById('dist_label');
  const boxEl=document.getElementById('auto_box');
  if(!fromEl||!toEl||!distEl) return;
  const from=fromEl.value.toLowerCase(); const to=toEl.value.toLowerCase();
  let fromKey=Object.keys(towns).find(k=>from.includes(k));
  let toKey=Object.keys(towns).find(k=>to.includes(k));
  if(!fromKey||!toKey){ if(labelEl) labelEl.innerHTML="⌛ Type Zambian town to auto-calculate driving distance"; return; }
  if(labelEl) labelEl.innerHTML="🔄 Calculating driving distance "+fromKey+" → "+toKey+"...";
  const lat1=towns[fromKey][0], lon1=towns[fromKey][1], lat2=towns[toKey][0], lon2=towns[toKey][1];
  const straight=Math.round(haversine(lat1,lon1,lat2,lon2));
  try{
    const url=`https://router.project-osrm.org/route/v1/driving/${lon1},${lat1};${lon2},${lat2}?overview=false`;
    const res=await fetch(url); const data=await res.json();
    if(data.routes && data.routes[0] && data.routes[0].distance){
      let km=Math.round(data.routes[0].distance/1000);
      let h=Math.round(data.routes[0].duration/3600*10)/10;
      distEl.value=km+" km";
      if(labelEl) labelEl.innerHTML="✅ Driving distance: "+km+" km";
      if(boxEl) boxEl.innerHTML=`✅ Real road: ${km} km | Straight: ${straight} km | Time: ${h} hrs`;
      return;
    }
  }catch(e){}
  let est=Math.round(straight*1.38);
  if((fromKey=="lusaka"&&toKey=="kitwe")||(fromKey=="kitwe"&&toKey=="lusaka")) est=363;
  if((fromKey=="lusaka"&&toKey=="ndola")||(fromKey=="ndola"&&toKey=="lusaka")) est=316;
  if((fromKey=="lusaka"&&toKey=="livingstone")||(fromKey=="livingstone"&&toKey=="lusaka")) est=485;
  distEl.value=est+" km";
  if(labelEl) labelEl.innerHTML="✅ Driving distance (est): "+est+" km";
  if(boxEl) boxEl.innerHTML=`✅ Est. road: ${est} km | Straight: ${straight} km`;
}
</script>
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    html = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Mzigo - Across Zambia</title>{STYLE}</head><body>
<header>
<div class="logo">MZIGO<span>.ZM</span></div>
<div class="desc">Zambia's smart logistics platform. No truck returns empty. We connect empty trucks with loads, GPS tracked, secure payments via Mobile Money. Like Kargo, built for Zambia.</div>
<div class="badge-across">ACROSS ZAMBIA</div>
<div class="provinces">
<span>Central</span><span>Copperbelt</span><span>Eastern</span><span>Luapula</span><span>Lusaka</span><span>Muchinga</span><span>Northern</span><span>North-Western</span><span>Southern</span><span>Western</span><br>10 Provinces Covered
</div>
</header>
<div class="container">
<div class="card" style="background:#0f172a;color:#fff">
<h2 style="margin:0">🚛 I'm a Driver</h2>
<p style="opacity:.85;font-size:13px">Have empty truck going anywhere in Zambia? Post it, set your price.</p>
<a href="/driver" class="btn btn-green">Enter as Driver →</a>
</div>
<div class="card" style="border:2px solid #f97316">
<h2 style="margin:0">📦 I'm a Trader</h2>
<p class="small">Need truck for your goods? Post load, we find truck ACROSS ZAMBIA, GPS tracking included.</p>
<a href="/trader" class="btn btn-dark">Enter as Trader →</a>
</div>
</div></body></html>"""
    return HTMLResponse(html)

@app.get("/driver", response_class=HTMLResponse)
async def driver_screen():
    trucks = []
    if supabase:
        try: trucks = supabase.table("trucks").select("*").order("created_at", desc=True).execute().data
        except: trucks = trucks_memory
    else: trucks = trucks_memory
    th = '<div class="card">No trucks yet - Be first across Zambia!</div>' if not trucks else ""
    for tr in trucks:
        b, fee, total = calc(tr.get("price","0"))
        th += f'<div class="card"><b>{tr.get("from_city","")} → {tr.get("to_city","")}</b><br><span class="badge bp">Driver K{b}</span><span class="badge bf">Trader K{total}</span><br><div class="small">📏 {tr.get("distance_km","")} driving | 🕒 {str(tr.get("departure_time",""))[:16]}</div></div>'
    html = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Driver - Mzigo</title>{STYLE}</head><body>
<header><div class="logo">MZIGO<span>.ZM</span> DRIVER</div><div class="badge-across">ACROSS ZAMBIA</div>
<div class="provinces"><span>Central</span><span>Copperbelt</span><span>Eastern</span><span>Luapula</span><span>Lusaka</span><span>Muchinga</span><span>Northern</span><span>North-Western</span><span>Southern</span><span>Western</span></div>
</header>
<div class="container">
<a href="/" class="back">← Home</a> <a href="/trader" class="back" style="float:right">Trader →</a>
<div class="card" style="background:#0f172a;color:#fff">
<h3>🚛 Post Empty Truck</h3>
<form action="/add-truck" method="post">
<label>From (Departure City)</label>
<input id="from_city" name="from_city" placeholder="e.g. Lusaka, Kitwe" required oninput="calcDist()">
<label>To (Destination City)</label>
<input id="to_city" name="to_city" placeholder="e.g. Livingstone, Ndola" required oninput="calcDist()">
<label id="dist_label">Distance will auto-calculate (driving road distance)</label>
<input id="distance_km" name="distance_km" placeholder="Auto driving distance (road)" readonly style="background:#dcfce7;font-weight:800">
<div class="auto-box" id="auto_box">✅ Real driving distance</div>
<label>Truck Type</label><input name="truck_type" placeholder="e.g. 30 Ton" required>
<label>Current Location (GPS)</label><input name="current_location" placeholder="e.g. Parked at station">
<label>Set Departure Date & Time</label><input name="departure_time" type="datetime-local" required>
<label>Your Price (ZMW)</label><input name="price" placeholder="e.g. 10000" required>
<label>Your WhatsApp</label><input name="whatsapp" placeholder="e.g. 097..." required>
<button class="btn btn-green" type="submit">Post Truck Across Zambia</button>
</form>
</div><h3>🚛 Trucks ({len(trucks)})</h3>{th}
</div>{JS}</body></html>"""
    return HTMLResponse(html)

@app.get("/trader", response_class=HTMLResponse)
async def trader_screen():
    loads = []
    if supabase:
        try: loads = supabase.table("loads").select("*").order("created_at", desc=True).execute().data
        except: loads = loads_memory
    else: loads = loads_memory
    lh = '<div class="card">No loads yet</div>' if not loads else ""
    for ld in loads:
        lh += f'<div class="card"><b>{ld.get("from_city","")} → {ld.get("to_city","")}</b><br><span class="badge">{ld.get("goods_type","")} {ld.get("weight","")}</span> <span class="badge" style="background:#dcfce7">📏 {ld.get("distance_km","")} driving</span></div>'
    html = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Trader - Mzigo</title>{STYLE}</head><body>
<header><div class="logo">MZIGO<span>.ZM</span> TRADER</div><div class="badge-across">ACROSS ZAMBIA</div>
<div class="provinces"><span>Central</span><span>Copperbelt</span><span>Eastern</span><span>Luapula</span><span>Lusaka</span><span>Muchinga</span><span>Northern</span><span>North-Western</span><span>Southern</span><span>Western</span></div>
</header>
<div class="container">
<a href="/" class="back">← Home</a> <a href="/driver" class="back" style="float:right">Driver →</a>
<div class="card" style="border:2px solid #f97316">
<h3>📦 Post Load</h3>
<form action="/add-load" method="post">
<label>From</label><input id="from_city" name="from_city" placeholder="e.g. Lusaka" required oninput="calcDist()">
<label>To</label><input id="to_city" name="to_city" placeholder="e.g. Ndola" required oninput="calcDist()">
<label id="dist_label">Distance auto-calculates (road)</label>
<input id="distance_km" name="distance_km" placeholder="Auto driving distance" readonly style="background:#dcfce7;font-weight:800">
<div class="auto-box" id="auto_box">✅ Real road distance</div>
<label>Goods Type</label><input name="goods_type" placeholder="e.g. Maize" required>
<label>Weight</label><input name="weight" placeholder="e.g. 15 Tons" required>
<label>Set Needed Date & Time</label><input name="departure_time" type="datetime-local" required>
<label>Budget</label><input name="price" placeholder="e.g. 13000" required>
<label>WhatsApp</label><input name="whatsapp" placeholder="e.g. 097..." required>
<button class="btn btn-orange" type="submit">Post Load Across Zambia</button>
</form>
</div><h3>📦 Loads ({len(loads)})</h3>{lh}
</div>{JS}</body></html>"""
    return HTMLResponse(html)

@app.post("/add-truck")
async def add_truck(from_city: str = Form(...), to_city: str = Form(...), truck_type: str = Form(...), current_location: str = Form(""), departure_time: str = Form(""), price: str = Form(...), whatsapp: str = Form(...), distance_km: str = Form("")):
    data = {"from_city": from_city.strip(), "to_city": to_city.strip(), "truck_type": truck_type.strip(), "current_location": current_location.strip(), "departure_time": departure_time.strip(), "price": price.strip(), "whatsapp": whatsapp.strip(), "distance_km": distance_km.strip()}
    if supabase:
        try: supabase.table("trucks").insert(data).execute()
        except Exception as e: print(e)
    else: trucks_memory.append(data)
    return RedirectResponse("/driver", status_code=303)

@app.post("/add-load")
async def add_load(from_city: str = Form(...), to_city: str = Form(...), goods_type: str = Form(...), weight: str = Form(...), distance_km: str = Form(""), departure_time: str = Form(""), price: str = Form(...), whatsapp: str = Form(...)):
    data = {"from_city": from_city.strip(), "to_city": to_city.strip(), "goods_type": goods_type.strip(), "weight": weight.strip(), "distance_km": distance_km.strip(), "departure_time": departure_time.strip(), "price": price.strip(), "whatsapp": whatsapp.strip()}
    if supabase:
        try: supabase.table("loads").insert(data).execute()
        except Exception as e: print(e)
    else: loads_memory.append(data)
    return RedirectResponse("/trader", status_code=303)

@app.get("/health")
async def health():
    return {"ok": True, "home_30": "removed", "distance": "driving"}
