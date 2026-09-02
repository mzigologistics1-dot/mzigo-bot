import os
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse

app = FastAPI()
trucks_memory = []
loads_memory = []

# YOUR EXACT NUMBERS
MTN = "0964343865"
AIRTEL = "0977166422"
MTN_FULL = "260964343865"
AIRTEL_FULL = "260977166422"

supabase = None
try:
    from supabase import create_client
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if url and key:
        supabase = create_client(url, key)
except:
    supabase = None

STYLE = """
<style>
*{box-sizing:border-box}body{margin:0;font-family:sans-serif;background:#f8fafc;color:#0f172a}
header{background:#0f172a;color:#fff;padding:20px 16px;text-align:center}
.logo{font-size:28px;font-weight:900}.logo span{color:#22c55e}
.desc{font-size:13px;line-height:1.4;opacity:.85;max-width:600px;margin:8px auto;color:#cbd5e1}
.badge-across{background:#22c55e;color:#000;padding:6px 16px;border-radius:20px;font-weight:900;font-size:12px;display:inline-block;margin:10px 0 6px;letter-spacing:2px}
.provinces{font-size:10px;opacity:.6;line-height:1.6;max-width:650px;margin:0 auto}
.provinces span{background:#1e293b;padding:3px 8px;border-radius:12px;margin:2px;display:inline-block;border:1px solid #334155}
.contact-bar{background:#1e293b;border:1px solid #334155;border-radius:12px;padding:10px;margin:10px auto;max-width:600px;display:flex;justify-content:center;gap:12px;flex-wrap:wrap}
.contact-bar span{font-size:12px;font-weight:800}
.contact-bar.mtn{color:#ffeb3b}
.contact-bar.airtel{color:#ff6b6b}
.container{max-width:700px;margin:0 auto;padding:14px}
.card{background:#fff;border-radius:18px;padding:18px;margin-bottom:14px;border:1px solid #e2e8f0}
.btn{width:100%;padding:14px;border:none;border-radius:12px;font-weight:900;margin-top:10px;cursor:pointer;display:block;text-align:center;text-decoration:none}
.btn-green{background:#22c55e;color:#000}
.btn-dark{background:#0f172a;color:#fff}
.btn-orange{background:#f97316;color:#fff}
input{width:100%;padding:12px;border-radius:10px;border:1.5px solid #e2e8f0;margin-top:6px;background:#f8fafc;font-size:14px}
label{font-size:11px;font-weight:800;color:#334155;margin-top:10px;display:block;text-transform:uppercase}
.badge{font-size:11px;padding:4px 10px;border-radius:20px;font-weight:800;display:inline-block;margin:2px}
.bp{background:#0f172a;color:#fff}
.back{display:inline-block;margin-bottom:12px;background:#e2e8f0;padding:8px 14px;border-radius:20px;text-decoration:none;color:#000;font-weight:800;font-size:12px}
.small{font-size:12px;color:#64748b;margin-top:4px}
.auto-box{background:#dcfce7;border:1px dashed #22c55e;padding:10px;border-radius:10px;margin-top:8px;font-size:12px;font-weight:700;color:#14532d}
.wa{display:block;margin-top:10px;background:#22c55e;color:#000;text-align:center;padding:12px;border-radius:10px;text-decoration:none;font-weight:900}
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
  const R=6371;
  const dLat=(lat2-lat1)*3.141592653589793/180;
  const dLon=(lon2-lon1)*3.141592653589793/180;
  const a=Math.sin(dLat/2)*Math.sin(dLat/2) + Math.cos(lat1*3.141592653589793/180)*Math.cos(lat2*3.141592653589793/180)*Math.sin(dLon/2)*Math.sin(dLon/2);
  const c=2*Math.atan2(Math.sqrt(a),Math.sqrt(1-a));
  return R*c;
}
async function calcDist(){
  const fromEl=document.getElementById('from_city');
  const toEl=document.getElementById('to_city');
  const distEl=document.getElementById('distance_km');
  const labelEl=document.getElementById('dist_label');
  const boxEl=document.getElementById('auto_box');
  if(!fromEl||!toEl||!distEl) return;
  const from=fromEl.value.toLowerCase();
  const to=toEl.value.toLowerCase();
  let fromKey=null, toKey=null;
  for(let k in towns){ if(from.includes(k)){ fromKey=k; break; } }
  for(let k in towns){ if(to.includes(k)){ toKey=k; break; } }
  if(!fromKey||!toKey){
    if(labelEl) labelEl.innerHTML="Type Zambian town to auto-calculate driving distance";
    return;
  }
  if(labelEl) labelEl.innerHTML="Calculating driving distance "+fromKey+" to "+toKey+"...";
  const lat1=towns[fromKey][0], lon1=towns[fromKey][1], lat2=towns[toKey][0], lon2=towns[toKey][1];
  const straight=Math.round(haversine(lat1,lon1,lat2,lon2));
  try{
    const url="https://router.project-osrm.org/route/v1/driving/"+lon1+","+lat1+";"+lon2+","+lat2+"?overview=false";
    const res=await fetch(url);
    const data=await res.json();
    if(data.routes && data.routes[0] && data.routes[0].distance){
      let km=Math.round(data.routes[0].distance/1000);
      let h=Math.round(data.routes[0].duration/3600*10)/10;
      distEl.value=km+" km";
      if(labelEl) labelEl.innerHTML="Driving distance: "+km+" km";
      if(boxEl) boxEl.innerHTML="Real road: "+km+" km | Straight: "+straight+" km | Time: "+h+" hrs";
      return;
    }
  }catch(e){}
  let est=Math.round(straight*1.38);
  if((fromKey=="lusaka"&&toKey=="kitwe")||(fromKey=="kitwe"&&toKey=="lusaka")) est=363;
  if((fromKey=="lusaka"&&toKey=="ndola")||(fromKey=="ndola"&&toKey=="lusaka")) est=316;
  if((fromKey=="lusaka"&&toKey=="livingstone")||(fromKey=="livingstone"&&toKey=="lusaka")) est=485;
  distEl.value=est+" km";
  if(labelEl) labelEl.innerHTML="Driving distance (est): "+est+" km";
  if(boxEl) boxEl.innerHTML="Est road: "+est+" km | Straight: "+straight+" km";
}
</script>
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    html = """<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Mzigo - Across Zambia</title>""" + STYLE + """</head><body>
<header>
<div class="logo">MZIGO<span>.ZM</span></div>
<div class="desc">Zambia's smart logistics platform. No truck returns empty. We connect empty trucks with loads, GPS tracked, secure payments via Mobile Money.</div>
<div class="badge-across">ACROSS ZAMBIA</div>
<div class="contact-bar">
<span class="mtn">📱 MTN: 0964343865</span>
<span class="airtel">📱 Airtel: 0977166422</span>
</div>
<div class="provinces">
<span>Central</span><span>Copperbelt</span><span>Eastern</span><span>Luapula</span><span>Lusaka</span><span>Muchinga</span><span>Northern</span><span>North-Western</span><span>Southern</span><span>Western</span><br>10 Provinces Covered
</div>
</header>
<div class="container">
<div class="card" style="background:#0f172a;color:#fff">
<h2 style="margin:0">🚛 I'm a Driver</h2>
<p style="opacity:.85;font-size:13px">Have empty truck anywhere in Zambia? Post it, set your price.</p>
<a href="/driver" class="btn btn-green">Enter as Driver →</a>
</div>
<div class="card" style="border:2px solid #f97316">
<h2 style="margin:0">📦 I'm a Trader</h2>
<p class="small">Need truck for your goods? Post load, we find truck ACROSS ZAMBIA.</p>
<a href="/trader" class="btn btn-dark">Enter as Trader →</a>
</div>
<div class="card" style="background:#fff8ed;text-align:center">
<b>Contact: MTN 0964343865 | Airtel 0977166422</b><br>
<span class="small">WhatsApp / Calls - Across Zambia</span>
</div>
</div></body></html>"""
    return HTMLResponse(html)

@app.get("/driver", response_class=HTMLResponse)
async def driver_screen():
    trucks = trucks_memory
    if supabase:
        try:
            res = supabase.table("trucks").select("*").order("created_at", desc=True).execute()
            if res.data:
                all_trucks = trucks_memory + res.data
                seen = set()
                uniq = []
                for t in all_trucks:
                    k = str(t.get('from_city')) + str(t.get('to_city')) + str(t.get('price')) + str(t.get('whatsapp'))
                    if k not in seen:
                        seen.add(k)
                        uniq.append(t)
                trucks = uniq
        except:
            pass
    th = '<div class="card">No trucks yet - Be first across Zambia!</div>' if not trucks else ""
    for tr in trucks:
        from_c = tr.get("from_city","")
        to_c = tr.get("to_city","")
        dist = tr.get("distance_km","")
        tm = str(tr.get("departure_time",""))[:16]
        loc = tr.get("current_location","")
        typ = tr.get("truck_type","")
        price = tr.get("price","")
        th += '<div class="card"><b>' + from_c + ' → ' + to_c + '</b> <span class="badge" style="background:#22c55e">ACROSS ZAMBIA</span><br><span class="badge bp">' + typ + '</span><span class="badge bp">K' + str(price) + '</span><br><div class="small">📍 ' + loc + ' | 📏 ' + dist + ' driving | 🕒 ' + tm + '</div><div style="background:#dcfce7;padding:6px;border-radius:6px;margin-top:6px;font-weight:800">✅ SAVED!</div><a class="wa" href="https://wa.me/260964343865?text=Truck ' + from_c + ' to ' + to_c + '" target="_blank">📱 MTN WhatsApp: 0964343865</a><a class="wa" style="background:#ff4444;color:#fff" href="https://wa.me/260977166422?text=Truck ' + from_c + ' to ' + to_c + '" target="_blank">📱 Airtel WhatsApp: 0977166422</a></div>'
    html = """<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Driver - Mzigo</title>""" + STYLE + """</head><body>
<header>
<div class="logo">MZIGO<span>.ZM</span> DRIVER</div>
<div class="badge-across">ACROSS ZAMBIA</div>
<div class="contact-bar"><span class="mtn">📱 MTN: 0964343865</span><span class="airtel">📱 Airtel: 0977166422</span></div>
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
<label id="dist_label">Distance will auto-calculate (driving road)</label>
<input id="distance_km" name="distance_km" placeholder="Auto driving distance" readonly style="background:#dcfce7;font-weight:800">
<div class="auto-box" id="auto_box">Enter Zambian towns - real driving distance</div>
<label>Truck Type</label><input name="truck_type" placeholder="e.g. 30 Ton" required>
<label>Current Location (GPS)</label><input name="current_location" placeholder="e.g. Total Sports">
<label>Set Departure Date & Time</label><input name="departure_time" type="datetime-local" required>
<label>Your Price (ZMW)</label><input name="price" placeholder="e.g. 10000" required>
<label>Your WhatsApp</label><input name="whatsapp" placeholder="e.g. 097..." required>
<button class="btn btn-green" type="submit">Post Truck Across Zambia</button>
</form>
</div><h3>🚛 Trucks (""" + str(len(trucks)) + """) - Now Saving!</h3>""" + th + """</div>""" + JS + """</body></html>"""
    return HTMLResponse(html)

@app.get("/trader", response_class=HTMLResponse)
async def trader_screen():
    loads = loads_memory
    if supabase:
        try:
            res = supabase.table("loads").select("*").order("created_at", desc=True).execute()
            if res.data:
                all_loads = loads_memory + res.data
                seen = set()
                uniq = []
                for l in all_loads:
                    k = str(l.get('from_city')) + str(l.get('to_city')) + str(l.get('price'))
                    if k not in seen:
                        seen.add(k)
                        uniq.append(l)
                loads = uniq
        except:
            pass
    lh = '<div class="card">No loads yet</div>' if not loads else ""
    for ld in loads:
        from_c = ld.get("from_city","")
        to_c = ld.get("to_city","")
        goods = ld.get("goods_type","")
        w = ld.get("weight","")
        dist = ld.get("distance_km","")
        lh += '<div class="card"><b>' + from_c + ' → ' + to_c + '</b><br><span class="badge">' + goods + ' ' + w + '</span> <span class="badge" style="background:#dcfce7">📏 ' + dist + ' driving</span><br><a class="wa" href="https://wa.me/260964343865?text=Load ' + from_c + ' to ' + to_c + '" target="_blank">📱 MTN: 0964343865</a><a class="wa" style="background:#ff4444;color:#fff" href="https://wa.me/260977166422?text=Load ' + from_c + ' to ' + to_c + '" target="_blank">📱 Airtel: 0977166422</a></div>'
    html = """<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Trader - Mzigo</title>""" + STYLE + """</head><body>
<header><div class="logo">MZIGO<span>.ZM</span> TRADER</div><div class="badge-across">ACROSS ZAMBIA</div>
<div class="contact-bar"><span class="mtn">📱 MTN: 0964343865</span><span class="airtel">📱 Airtel: 0977166422</span></div>
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
<div class="auto-box" id="auto_box">Real road distance</div>
<label>Goods Type</label><input name="goods_type" placeholder="e.g. Maize" required>
<label>Weight</label><input name="weight" placeholder="e.g. 15 Tons" required>
<label>Set Needed Date & Time</label><input name="departure_time" type="datetime-local" required>
<label>Budget</label><input name="price" placeholder="e.g. 13000" required>
<label>WhatsApp</label><input name="whatsapp" placeholder="e.g. 097..." required>
<button class="btn btn-orange" type="submit">Post Load Across Zambia</button>
</form>
</div><h3>📦 Loads (""" + str(len(loads)) + """)</h3>""" + lh + """</div>""" + JS + """</body></html>"""
    return HTMLResponse(html)

@app.post("/add-truck")
async def add_truck(from_city: str = Form(...), to_city: str = Form(...), truck_type: str = Form(...), current_location: str = Form(""), departure_time: str = Form(""), price: str = Form(...), whatsapp: str = Form(...), distance_km: str = Form("")):
    data = {"from_city": from_city.strip(), "to_city": to_city.strip(), "truck_type": truck_type.strip(), "current_location": current_location.strip(), "departure_time": departure_time.strip(), "price": price.strip(), "whatsapp": whatsapp.strip(), "distance_km": distance_km.strip()}
    trucks_memory.insert(0, data)
    if supabase:
        try:
            supabase.table("trucks").insert(data).execute()
        except:
            try:
                minimal = {"from_city": data["from_city"], "to_city": data["to_city"], "truck_type": data["truck_type"], "price": data["price"], "whatsapp": data["whatsapp"]}
                supabase.table("trucks").insert(minimal).execute()
            except:
                pass
    return RedirectResponse("/driver", status_code=303)

@app.post("/add-load")
async def add_load(from_city: str = Form(...), to_city: str = Form(...), goods_type: str = Form(...), weight: str = Form(...), distance_km: str = Form(""), departure_time: str = Form(""), price: str = Form(...), whatsapp: str = Form(...)):
    data = {"from_city": from_city.strip(), "to_city": to_city.strip(), "goods_type": goods_type.strip(), "weight": weight.strip(), "distance_km": distance_km.strip(), "departure_time": departure_time.strip(), "price": price.strip(), "whatsapp": whatsapp.strip()}
    loads_memory.insert(0, data)
    if supabase:
        try:
            supabase.table("loads").insert(data).execute()
        except:
            try:
                minimal = {"from_city": data["from_city"], "to_city": data["to_city"], "goods_type": data["goods_type"], "weight": data["weight"], "price": data["price"], "whatsapp": data["whatsapp"]}
                supabase.table("loads").insert(minimal).execute()
            except:
                pass
    return RedirectResponse("/trader", status_code=303)

@app.get("/health")
async def health():
    return {"ok": True, "mtn": "0964343865", "airtel": "0977166422"}
