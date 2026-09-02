import os
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse

app = FastAPI()
trucks_memory = []
loads_memory = []

MTN = "0964343865"
AIRTEL = "0977166422"
RATE_PER_KG = 30

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
.container{max-width:700px;margin:0 auto;padding:14px}
.card{background:#fff;border-radius:18px;padding:18px;margin-bottom:14px;border:1px solid #e2e8f0;position:relative}
.btn{width:100%;padding:14px;border:none;border-radius:12px;font-weight:900;margin-top:10px;cursor:pointer;display:block;text-align:center;text-decoration:none}
.btn-green{background:#22c55e;color:#000}
.btn-dark{background:#0f172a;color:#fff}
.btn-orange{background:#f97316;color:#fff}
.btn-red{background:#ef4444;color:#fff;padding:6px 12px;font-size:11px;border-radius:20px;display:inline-block;width:auto;margin-left:6px}
input,select{width:100%;padding:12px;border-radius:10px;border:1.5px solid #e2e8f0;margin-top:6px;background:#f8fafc;font-size:14px}
label{font-size:11px;font-weight:800;color:#334155;margin-top:10px;display:block;text-transform:uppercase}
.badge{font-size:11px;padding:4px 10px;border-radius:20px;font-weight:800;display:inline-block;margin:2px}
.bp{background:#0f172a;color:#fff}
.back{display:inline-block;margin-bottom:12px;background:#e2e8f0;padding:8px 14px;border-radius:20px;text-decoration:none;color:#000;font-weight:800;font-size:12px}
.small{font-size:12px;color:#64748b;margin-top:4px}
.auto-box{background:#dcfce7;border:1px dashed #22c55e;padding:10px;border-radius:10px;margin-top:8px;font-size:12px;font-weight:700;color:#14532d}
.wa{display:inline-block;margin-top:8px;background:#22c55e;color:#000;text-align:center;padding:8px 12px;border-radius:8px;text-decoration:none;font-weight:900;font-size:12px;margin-right:6px}
.wa-airtel{background:#ff4444;color:#fff}
.price-box{background:#fff8ed;border:2px solid #f97316;border-radius:12px;padding:12px;margin-top:8px}
.delete-btn{position:absolute;top:10px;right:10px;background:#ef4444;color:#fff;border:none;border-radius:50%;width:28px;height:28px;font-weight:900;cursor:pointer}
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
      calcWeightPrice();
      return;
    }
  }catch(e){}
  let est=Math.round(straight*1.38);
  if((fromKey=="lusaka"&&toKey=="kitwe")||(fromKey=="kitwe"&&toKey=="lusaka")) est=363;
  distEl.value=est+" km";
  if(labelEl) labelEl.innerHTML="Driving distance (est): "+est+" km";
  if(boxEl) boxEl.innerHTML="Est road: "+est+" km | Straight: "+straight+" km";
  calcWeightPrice();
}
function parseWeightKg(text){
  if(!text) return 0;
  let t=text.toLowerCase();
  let num=parseFloat(t.replace(/[^0-9.]/g,''));
  if(isNaN(num)) return 0;
  if(t.includes("ton")){ return num*1000; }
  return num;
}
function calcWeightPrice(){
  const weightEl=document.getElementById('weight');
  const rateEl=document.getElementById('rate_per_kg');
  const priceEl=document.getElementById('price');
  const priceBox=document.getElementById('price_calc_box');
  if(!weightEl||!rateEl||!priceEl) return;
  let kg=parseWeightKg(weightEl.value);
  let rate=parseFloat(rateEl.value)||30;
  if(kg>0){
    let total=Math.round(kg*rate);
    let perTon=Math.round(rate*1000);
    if(priceBox){
      priceBox.innerHTML="Weight: "+kg+" kg ("+(kg/1000)+" tons) x K"+rate+"/kg = <b>K"+total+"</b><br><span style='font-size:10px'>Platinum style: K"+rate+"/kg | K"+perTon+"/ton</span>";
      priceBox.style.display="block";
    }
    if(!priceEl.value || priceEl.dataset.auto=="1"){
      priceEl.value=total;
      priceEl.dataset.auto="1";
    }
  }
}
function onWeightInput(){
  const priceEl=document.getElementById('price');
  if(priceEl) priceEl.dataset.auto="1";
  calcWeightPrice();
}
function onPriceManual(){
  const priceEl=document.getElementById('price');
  if(priceEl) priceEl.dataset.auto="0";
}
</script>
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    html = """<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Mzigo - Across Zambia</title>""" + STYLE + """</head><body>
<header>
<div class="logo">MZIGO<span>.ZM</span></div>
<div class="desc">Weight-based pricing like Platinum - K25-35/kg. WhatsApp bot included.</div>
<div class="badge-across">ACROSS ZAMBIA</div>
<div class="contact-bar">
<span>📱 MTN: 0964343865</span>
<span>📱 Airtel: 0977166422</span>
</div>
<div class="provinces">
<span>Central</span><span>Copperbelt</span><span>Eastern</span><span>Luapula</span><span>Lusaka</span><span>Muchinga</span><span>Northern</span><span>North-Western</span><span>Southern</span><span>Western</span>
</div>
</header>
<div class="container">
<div class="card" style="background:#0f172a;color:#fff">
<h2 style="margin:0">🚛 Driver</h2>
<a href="/driver" class="btn btn-green">Enter as Driver →</a>
</div>
<div class="card" style="border:2px solid #f97316">
<h2 style="margin:0">📦 Trader - Weight Based</h2>
<a href="/trader" class="btn btn-dark">Enter as Trader →</a>
</div>
<div class="card" style="background:#dcfce7;text-align:center">
<b>🤖 WhatsApp Bot Active</b><br>
<span class="small">MTN 0964343865 | Airtel 0977166422</span><br>
<a href="/whatsapp-bot" class="btn btn-green" style="margin-top:8px">View Bot Setup</a>
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
    th = '<div class="card">No trucks yet</div>' if not trucks else ""
    for idx, tr in enumerate(trucks):
        from_c = tr.get("from_city","")
        to_c = tr.get("to_city","")
        dist = tr.get("distance_km","")
        tm = str(tr.get("departure_time",""))[:16]
        loc = tr.get("current_location","")
        typ = tr.get("truck_type","")
        price = tr.get("price","")
        th += '<div class="card"><button class="delete-btn" onclick="if(confirm(\'Delete?\')) window.location.href=\'/delete-truck/' + str(idx) + '\'">X</button><b>' + from_c + ' → ' + to_c + '</b><br><span class="badge bp">' + typ + '</span><span class="badge bp">K' + str(price) + '</span><br><div class="small">📍 ' + loc + ' | 📏 ' + dist + ' | 🕒 ' + tm + '</div><a class="wa" href="https://wa.me/260964343865?text=Truck%20' + from_c + '%20to%20' + to_c + '" target="_blank">MTN: 0964343865</a><a class="wa wa-airtel" href="https://wa.me/260977166422?text=Truck" target="_blank">Airtel: 0977166422</a><br><a class="btn btn-red" href="/delete-truck/' + str(idx) + '">🗑 Delete</a></div>'
    html = """<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Driver</title>""" + STYLE + """</head><body>
<header><div class="logo">MZIGO<span>.ZM</span> DRIVER</div><div class="badge-across">ACROSS ZAMBIA</div>
<div class="contact-bar"><span>📱 MTN: 0964343865</span><span>📱 Airtel: 0977166422</span></div>
</header>
<div class="container">
<a href="/" class="back">← Home</a> <a href="/trader" class="back" style="float:right">Trader →</a>
<div class="card" style="background:#0f172a;color:#fff">
<h3>🚛 Post Empty Truck</h3>
<form action="/add-truck" method="post">
<label>From</label><input id="from_city" name="from_city" placeholder="e.g. Kitwe" required oninput="calcDist()">
<label>To</label><input id="to_city" name="to_city" placeholder="e.g. Lusaka" required oninput="calcDist()">
<label id="dist_label">Distance auto</label>
<input id="distance_km" name="distance_km" placeholder="Auto" readonly style="background:#dcfce7;font-weight:800">
<div class="auto-box" id="auto_box">Real driving distance</div>
<label>Truck Type</label><input name="truck_type" placeholder="e.g. 50 ton" required>
<label>Current Location</label><input name="current_location" placeholder="e.g. Total Sports">
<label>Set Departure Date & Time</label><input name="departure_time" type="datetime-local" required>
<label>Price</label><input name="price" placeholder="e.g. 10000" required>
<label>WhatsApp</label><input name="whatsapp" placeholder="e.g. 0964343865" required>
<button class="btn btn-green" type="submit">Post Truck</button>
</form>
</div><h3>🚛 Trucks (""" + str(len(trucks)) + """)</h3>""" + th + """</div>""" + JS + """</body></html>"""
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
    for idx, ld in enumerate(loads):
        from_c = ld.get("from_city","")
        to_c = ld.get("to_city","")
        goods = ld.get("goods_type","")
        w = ld.get("weight","")
        dist = ld.get("distance_km","")
        price = ld.get("price","")
        rate = ld.get("rate_per_kg","30")
        lh += '<div class="card"><button class="delete-btn" onclick="if(confirm(\'Delete?\')) window.location.href=\'/delete-load/' + str(idx) + '\'">X</button><b>' + from_c + ' → ' + to_c + '</b><br><span class="badge">' + goods + ' ' + w + '</span> <span class="badge" style="background:#dcfce7">📏 ' + dist + '</span><br><span class="badge bp">K' + str(price) + ' (K' + str(rate) + '/kg)</span><br><a class="wa" href="https://wa.me/260964343865?text=Load" target="_blank">MTN: 0964343865</a><a class="wa wa-airtel" href="https://wa.me/260977166422?text=Load" target="_blank">Airtel: 0977166422</a><br><a class="btn btn-red" href="/delete-load/' + str(idx) + '">🗑 Delete Load</a></div>'
    html = """<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Trader</title>""" + STYLE + """</head><body>
<header><div class="logo">MZIGO<span>.ZM</span> TRADER</div><div class="badge-across">ACROSS ZAMBIA</div>
<div class="contact-bar"><span>📱 MTN: 0964343865</span><span>📱 Airtel: 0977166422</span></div>
</header>
<div class="container">
<a href="/" class="back">← Home</a> <a href="/driver" class="back" style="float:right">Driver →</a>
<div class="card" style="border:2px solid #f97316">
<h3>📦 Post Load - Weight-Based (Platinum)</h3>
<form action="/add-load" method="post">
<label>From</label><input id="from_city" name="from_city" placeholder="e.g. Lusaka" required oninput="calcDist()">
<label>To</label><input id="to_city" name="to_city" placeholder="e.g. Ndola" required oninput="calcDist()">
<label id="dist_label">Distance auto</label>
<input id="distance_km" name="distance_km" placeholder="Auto" readonly style="background:#dcfce7;font-weight:800">
<div class="auto-box" id="auto_box">Real road distance</div>
<label>Goods Type</label><input name="goods_type" placeholder="e.g. Maize" required>
<label>Weight (kg or tons)</label><input id="weight" name="weight" placeholder="e.g. 1000 kg or 1.5 tons" required oninput="onWeightInput()">
<label>Rate per kg (Platinum)</label>
<select id="rate_per_kg" name="rate_per_kg" onchange="calcWeightPrice()">
<option value="25">K25/kg Budget</option>
<option value="30" selected>K30/kg Standard</option>
<option value="35">K35/kg Express</option>
<option value="50">K50/kg Urgent</option>
</select>
<div id="price_calc_box" class="price-box" style="display:none">Enter weight</div>
<label>Set Needed Date & Time</label><input name="departure_time" type="datetime-local" required>
<label>Total Budget (Auto from weight)</label><input id="price" name="price" placeholder="Auto from weight" required oninput="onPriceManual()" data-auto="1">
<label>WhatsApp</label><input name="whatsapp" placeholder="e.g. 0964343865" required>
<button class="btn btn-orange" type="submit">Post Load - Weight Based</button>
</form>
</div><h3>📦 Loads (""" + str(len(loads)) + """)</h3>""" + lh + """</div>""" + JS + """</body></html>"""
    return HTMLResponse(html)

@app.get("/whatsapp-bot", response_class=HTMLResponse)
async def whatsapp_bot():
    html = """<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>WhatsApp Bot</title>""" + STYLE + """</head><body>
<header><div class="logo">MZIGO<span>.ZM</span> BOT</div></header>
<div class="container">
<a href="/" class="back">← Home</a>
<div class="card">
<h3>🤖 WhatsApp Bot Active</h3>
<div style="background:#dcfce7;padding:12px;border-radius:10px">
🚛 TRUCK AVAILABLE!<br>Kitwe → Lusaka 362km<br>Pay: MTN 0964343865 | Airtel 0977166422
</div>
<p class="small">Bot uses wa.me links with your numbers. Click MTN/Airtel buttons to open WhatsApp with payment info.</p>
<a href="/driver" class="btn btn-green">Test Bot</a>
</div></div></body></html>"""
    return HTMLResponse(html)

@app.get("/delete-truck/{idx}")
async def delete_truck(idx: int):
    try:
        if 0 <= idx < len(trucks_memory):
            trucks_memory.pop(idx)
    except:
        pass
    return RedirectResponse("/driver", status_code=303)

@app.get("/delete-load/{idx}")
async def delete_load(idx: int):
    try:
        if 0 <= idx < len(loads_memory):
            loads_memory.pop(idx)
    except:
        pass
    return RedirectResponse("/trader", status_code=303)

@app.post("/add-truck")
async def add_truck(from_city: str = Form(...), to_city: str = Form(...), truck_type: str = Form(...), current_location: str = Form(""), departure_time: str = Form(""), price: str = Form(...), whatsapp: str = Form(...), distance_km: str = Form("")):
    data = {"from_city": from_city.strip(), "to_city": to_city.strip(), "truck_type": truck_type.strip(), "current_location": current_location.strip(), "departure_time": departure_time.strip(), "price": price.strip(), "whatsapp": whatsapp.strip(), "distance_km": distance_km.strip()}
    trucks_memory.insert(0, data)
    if supabase:
        try: supabase.table("trucks").insert(data).execute()
        except:
            try:
                minimal = {"from_city": data["from_city"], "to_city": data["to_city"], "truck_type": data["truck_type"], "price": data["price"], "whatsapp": data["whatsapp"]}
                supabase.table("trucks").insert(minimal).execute()
            except: pass
    return RedirectResponse("/driver", status_code=303)

@app.post("/add-load")
async def add_load(from_city: str = Form(...), to_city: str = Form(...), goods_type: str = Form(...), weight: str = Form(...), distance_km: str = Form(""), departure_time: str = Form(""), price: str = Form(...), whatsapp: str = Form(...), rate_per_kg: str = Form("30")):
    data = {"from_city": from_city.strip(), "to_city": to_city.strip(), "goods_type": goods_type.strip(), "weight": weight.strip(), "distance_km": distance_km.strip(), "departure_time": departure_time.strip(), "price": price.strip(), "whatsapp": whatsapp.strip(), "rate_per_kg": rate_per_kg.strip()}
    loads_memory.insert(0, data)
    if supabase:
        try: supabase.table("loads").insert(data).execute()
        except:
            try:
                minimal = {"from_city": data["from_city"], "to_city": data["to_city"], "goods_type": data["goods_type"], "weight": data["weight"], "price": data["price"], "whatsapp": data["whatsapp"]}
                supabase.table("loads").insert(minimal).execute()
            except: pass
    return RedirectResponse("/trader", status_code=303)
