import os
import time
import uuid
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse

app = FastAPI()
trucks_memory = []
loads_memory = []

MTN = "0964343865"
AIRTEL = "0976166422"

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
header{background:#0f172a;color:#fff;padding:18px 16px;text-align:center}
.logo{font-size:28px;font-weight:900}.logo span{color:#22c55e}
.desc{font-size:12px;line-height:1.4;opacity:.8;max-width:600px;margin:8px auto;color:#cbd5e1}
.badge-across{background:#22c55e;color:#000;padding:6px 16px;border-radius:20px;font-weight:900;font-size:12px;display:inline-block;margin:8px 0}
.provinces{font-size:10px;opacity:.7;line-height:1.6;max-width:650px;margin:8px auto 0}
.provinces span{background:#1e293b;padding:4px 10px;border-radius:12px;margin:3px;display:inline-block;border:1px solid #334155;color:#e2e8f0}
.container{max-width:700px;margin:0 auto;padding:14px}
.card{background:#fff;border-radius:18px;padding:18px;margin-bottom:14px;border:1px solid #e2e8f0;position:relative}
.btn{width:100%;padding:14px;border:none;border-radius:12px;font-weight:900;margin-top:10px;cursor:pointer;display:block;text-align:center;text-decoration:none}
.btn-green{background:#22c55e;color:#000}
.btn-dark{background:#0f172a;color:#fff}
.btn-orange{background:#f97316;color:#fff}
.btn-red{background:#ef4444;color:#fff;padding:8px 14px;font-size:12px;border-radius:20px;display:inline-block;width:auto;margin-top:8px;border:none;cursor:pointer}
input,select{width:100%;padding:12px;border-radius:10px;border:1.5px solid #e2e8f0;margin-top:6px;background:#f8fafc;font-size:14px}
label{font-size:11px;font-weight:800;color:#334155;margin-top:10px;display:block;text-transform:uppercase}
.badge{font-size:11px;padding:4px 10px;border-radius:20px;font-weight:800;display:inline-block;margin:2px}
.bp{background:#0f172a;color:#fff}
.back{display:inline-block;margin-bottom:12px;background:#e2e8f0;padding:8px 14px;border-radius:20px;text-decoration:none;color:#000;font-weight:800;font-size:12px}
.small{font-size:12px;color:#64748b;margin-top:4px}
.auto-box{background:#dcfce7;border:1px dashed #22c55e;padding:10px;border-radius:10px;margin-top:8px;font-size:12px;font-weight:700;color:#14532d}
.wa{display:inline-block;margin-top:8px;background:#22c55e;color:#000;text-align:center;padding:8px 12px;border-radius:8px;text-decoration:none;font-weight:900;font-size:11px;margin-right:6px}
.wa-airtel{background:#3b82f6;color:#fff}
.price-box{background:#fff8ed;border:2px solid #f97316;border-radius:12px;padding:12px;margin-top:8px}
.delete-btn{position:absolute;top:10px;right:10px;background:#ef4444;color:#fff;border:none;border-radius:50%;width:28px;height:28px;font-weight:900;cursor:pointer;font-size:14px}
.footer-contact{background:#0f172a;color:#fff;padding:14px;text-align:center;margin-top:20px;border-radius:16px 16px 0 0}
.footer-contact b{color:#22c55e}
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
      if(typeof calcWeightPrice==="function") calcWeightPrice();
      return;
    }
  }catch(e){}
  let est=Math.round(straight*1.38);
  if((fromKey=="lusaka"&&toKey=="kitwe")||(fromKey=="kitwe"&&toKey=="lusaka")) est=363;
  distEl.value=est+" km";
  if(labelEl) labelEl.innerHTML="Driving distance (est): "+est+" km";
  if(boxEl) boxEl.innerHTML="Est road: "+est+" km | Straight: "+straight+" km";
  if(typeof calcWeightPrice==="function") calcWeightPrice();
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
function confirmDelete(id){
  if(confirm('Delete this? This will remove it permanently!')){
    window.location.href='/delete-item/'+id;
  }
}
</script>
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    html = """<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Mzigo - Across Zambia</title>""" + STYLE + """</head><body>
<header>
<div class="logo">MZIGO<span>.ZM</span></div>
<div class="desc">Zambia's smart logistics - No truck returns empty. Weight-based pricing K25-35/kg like Platinum. Real driving distance.</div>
<div class="badge-across">ACROSS ZAMBIA</div>
<div class="provinces">
<span>Central</span><span>Copperbelt</span><span>Eastern</span><span>Luapula</span><span>Lusaka</span><span>Muchinga</span><span>Northern</span><span>North-Western</span><span>Southern</span><span>Western</span><br>10 Provinces Covered - No numbers on top as requested
</div>
</header>
<div class="container">
<div class="card" style="background:#0f172a;color:#fff">
<h2 style="margin:0">🚛 I'm a Driver</h2>
<p style="opacity:.85;font-size:13px">Post empty truck anywhere in Zambia.</p>
<a href="/driver" class="btn btn-green">Enter as Driver →</a>
</div>
<div class="card" style="border:2px solid #f97316">
<h2 style="margin:0">📦 I'm a Trader - Weight Based</h2>
<p class="small">K25-35 per kg like Platinum. Auto calculates.</p>
<a href="/trader" class="btn btn-dark">Enter as Trader →</a>
</div>
</div>
<div class="footer-contact">
<b>MTN:</b> 0964343865 | <b>Airtel:</b> 0976166422<br>
<span style="font-size:11px;opacity:.7">WhatsApp Bot + Payments - Bottom only, not top</span>
</div>
</body></html>"""
    return HTMLResponse(html)

def get_trucks_combined():
    trucks = list(trucks_memory)
    if supabase:
        try:
            res = supabase.table("trucks").select("*").order("created_at", desc=True).execute()
            if res.data:
                for db_truck in res.data:
                    exists = False
                    for mem in trucks_memory:
                        if mem.get('from_city')==db_truck.get('from_city') and mem.get('to_city')==db_truck.get('to_city') and str(mem.get('price'))==str(db_truck.get('price')):
                            exists = True
                            break
                    if not exists:
                        if 'local_id' not in db_truck:
                            db_truck['local_id'] = str(db_truck.get('id'))
                        trucks.append(db_truck)
        except Exception as e:
            print("get trucks error", e)
    return trucks

def get_loads_combined():
    loads = list(loads_memory)
    if supabase:
        try:
            res = supabase.table("loads").select("*").order("created_at", desc=True).execute()
            if res.data:
                for db_load in res.data:
                    exists = False
                    for mem in loads_memory:
                        if mem.get('from_city')==db_load.get('from_city') and mem.get('to_city')==db_load.get('to_city') and str(mem.get('price'))==str(db_load.get('price')):
                            exists = True
                            break
                    if not exists:
                        if 'local_id' not in db_load:
                            db_load['local_id'] = str(db_load.get('id'))
                        loads.append(db_load)
        except:
            pass
    return loads

@app.get("/driver", response_class=HTMLResponse)
async def driver_screen():
    trucks = get_trucks_combined()
    th = '<div class="card">No trucks yet - Be first across Zambia!</div>' if not trucks else ""
    for tr in trucks:
        from_c = tr.get("from_city","")
        to_c = tr.get("to_city","")
        dist = tr.get("distance_km","")
        tm = str(tr.get("departure_time",""))[:16]
        loc = tr.get("current_location","")
        typ = tr.get("truck_type","")
        price = tr.get("price","")
        local_id = tr.get("local_id") or tr.get("id") or str(id(tr))
        local_id_str = str(local_id).replace(" ","_")
        th += '<div class="card"><button class="delete-btn" onclick="confirmDelete(\'' + local_id_str + '\')">X</button><b>' + from_c + ' → ' + to_c + '</b><br><span class="badge bp">' + typ + '</span><span class="badge bp">K' + str(price) + '</span><br><div class="small">📍 ' + loc + ' | 📏 ' + dist + ' driving | 🕒 ' + tm + '</div><a class="wa" href="https://wa.me/260964343865?text=Truck%20' + from_c + '%20to%20' + to_c + '%20' + dist + '" target="_blank">MTN: 0964343865</a><a class="wa wa-airtel" href="https://wa.me/260976166422?text=Truck%20' + from_c + '%20to%20' + to_c + '" target="_blank">Airtel: 0976166422</a><br><button class="btn-red" onclick="confirmDelete(\'' + local_id_str + '\')">🗑 Delete</button></div>'
    html = """<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Driver - Mzigo</title>""" + STYLE + """</head><body>
<header>
<div class="logo">MZIGO<span>.ZM</span> DRIVER</div>
<div class="badge-across">ACROSS ZAMBIA</div>
<div class="provinces">
<span>Central</span><span>Copperbelt</span><span>Eastern</span><span>Luapula</span><span>Lusaka</span><span>Muchinga</span><span>Northern</span><span>North-Western</span><span>Southern</span><span>Western</span>
</div>
</header>
<div class="container">
<a href="/" class="back">← Home</a> <a href="/trader" class="back" style="float:right">Trader →</a>
<div class="card" style="background:#0f172a;color:#fff">
<h3>🚛 Post Empty Truck - Fixed Delete + Provinces Back</h3>
<form action="/add-truck" method="post">
<label>From (Departure City)</label>
<input id="from_city" name="from_city" placeholder="e.g. Kitwe" required oninput="calcDist()">
<label>To (Destination City)</label>
<input id="to_city" name="to_city" placeholder="e.g. Lusaka" required oninput="calcDist()">
<label id="dist_label">Distance will auto-calculate (driving road)</label>
<input id="distance_km" name="distance_km" placeholder="Auto driving distance" readonly style="background:#dcfce7;font-weight:800">
<div class="auto-box" id="auto_box">Real driving distance - 362km Kitwe→Lusaka road</div>
<label>Truck Type</label><input name="truck_type" placeholder="e.g. 50 ton" required>
<label>Current Location (GPS)</label><input name="current_location" placeholder="e.g. Total Sports">
<label>Set Departure Date & Time</label><input name="departure_time" type="datetime-local" required>
<label>Your Price (ZMW)</label><input name="price" placeholder="e.g. 10000" required>
<label>Your WhatsApp</label><input name="whatsapp" placeholder="e.g. 0964343865" required>
<button class="btn btn-green" type="submit">Post Truck Across Zambia</button>
</form>
</div><h3>🚛 Trucks (""" + str(len(trucks)) + """) - Delete Fixed!</h3>""" + th + """</div>
<div class="footer-contact">
<b>MTN:</b> 0964343865 | <b>Airtel:</b> 0976166422 (Corrected!)<br>
<span style="font-size:11px">Numbers only at bottom, not top as requested</span>
</div>
""" + JS + """</body></html>"""
    return HTMLResponse(html)

@app.get("/trader", response_class=HTMLResponse)
async def trader_screen():
    loads = get_loads_combined()
    lh = '<div class="card">No loads yet</div>' if not loads else ""
    for tr in loads:
        from_c = tr.get("from_city","")
        to_c = tr.get("to_city","")
        goods = tr.get("goods_type","")
        w = tr.get("weight","")
        dist = tr.get("distance_km","")
        price = tr.get("price","")
        rate = tr.get("rate_per_kg","30")
        local_id = tr.get("local_id") or tr.get("id") or str(id(tr))
        local_id_str = str(local_id).replace(" ","_")
        lh += '<div class="card"><button class="delete-btn" onclick="confirmDelete(\'' + local_id_str + '\')">X</button><b>' + from_c + ' → ' + to_c + '</b><br><span class="badge">' + goods + ' ' + w + '</span> <span class="badge" style="background:#dcfce7">📏 ' + dist + '</span><br><span class="badge bp">K' + str(price) + ' (K' + str(rate) + '/kg)</span><br><a class="wa" href="https://wa.me/260964343865?text=Load%20' + from_c + '" target="_blank">MTN: 0964343865</a><a class="wa wa-airtel" href="https://wa.me/260976166422?text=Load" target="_blank">Airtel: 0976166422</a><br><button class="btn-red" onclick="confirmDelete(\'' + local_id_str + '\')">🗑 Delete Load</button></div>'
    html = """<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Trader - Mzigo</title>""" + STYLE + """</head><body>
<header>
<div class="logo">MZIGO<span>.ZM</span> TRADER</div>
<div class="badge-across">ACROSS ZAMBIA</div>
<div class="provinces">
<span>Central</span><span>Copperbelt</span><span>Eastern</span><span>Luapula</span><span>Lusaka</span><span>Muchinga</span><span>Northern</span><span>North-Western</span><span>Southern</span><span>Western</span>
</div>
</header>
<div class="container">
<a href="/" class="back">← Home</a> <a href="/driver" class="back" style="float:right">Driver →</a>
<div class="card" style="border:2px solid #f97316">
<h3>📦 Post Load - Weight-Based (K25-35/kg Platinum)</h3>
<form action="/add-load" method="post">
<label>From</label><input id="from_city" name="from_city" placeholder="e.g. Lusaka" required oninput="calcDist()">
<label>To</label><input id="to_city" name="to_city" placeholder="e.g. Ndola" required oninput="calcDist()">
<label id="dist_label">Distance auto</label>
<input id="distance_km" name="distance_km" placeholder="Auto" readonly style="background:#dcfce7;font-weight:800">
<div class="auto-box" id="auto_box">Real road distance</div>
<label>Goods Type</label><input name="goods_type" placeholder="e.g. Maize" required>
<label>Weight (kg or tons)</label><input id="weight" name="weight" placeholder="e.g. 1000 kg or 1.5 tons" required oninput="onWeightInput()">
<label>Rate per kg</label>
<select id="rate_per_kg" name="rate_per_kg" onchange="calcWeightPrice()">
<option value="25">K25/kg Budget</option>
<option value="30" selected>K30/kg Standard (Platinum)</option>
<option value="35">K35/kg Express</option>
<option value="50">K50/kg Urgent</option>
</select>
<div id="price_calc_box" class="price-box" style="display:none">Enter weight</div>
<label>Set Date & Time</label><input name="departure_time" type="datetime-local" required>
<label>Total Budget (Auto from weight)</label><input id="price" name="price" placeholder="Auto from weight" required oninput="onPriceManual()" data-auto="1">
<label>WhatsApp</label><input name="whatsapp" placeholder="e.g. 0964343865" required>
<button class="btn btn-orange" type="submit">Post Load - Weight Based</button>
</form>
</div><h3>📦 Loads (""" + str(len(loads)) + """)</h3>""" + lh + """</div>
<div class="footer-contact">
<b>MTN:</b> 0964343865 | <b>Airtel:</b> 0976166422<br>
Numbers only at bottom
</div>
""" + JS + """</body></html>"""
    return HTMLResponse(html)

@app.get("/delete-item/{item_id}")
async def delete_item(item_id: str):
    global trucks_memory, loads_memory
    new_trucks = []
    for t in trucks_memory:
        tid = str(t.get('local_id') or t.get('id') or '')
        if tid!= item_id and str(id(t))!= item_id:
            new_trucks.append(t)
    trucks_memory = new_trucks
    new_loads = []
    for l in loads_memory:
        lid = str(l.get('local_id') or l.get('id') or '')
        if lid!= item_id and str(id(l))!= item_id:
            new_loads.append(l)
    loads_memory = new_loads
    if supabase:
        try:
            try:
                int_id = int(item_id)
                supabase.table("trucks").delete().eq("id", int_id).execute()
                supabase.table("loads").delete().eq("id", int_id).execute()
            except:
                pass
            supabase.table("trucks").delete().eq("local_id", item_id).execute()
            supabase.table("loads").delete().eq("local_id", item_id).execute()
        except Exception as e:
            print("supabase delete error", e)
    return RedirectResponse("/driver", status_code=303)

@app.get("/delete-truck/{idx}")
async def delete_truck_legacy(idx: str):
    return RedirectResponse(f"/delete-item/{idx}", status_code=303)

@app.get("/delete-load/{idx}")
async def delete_load_legacy(idx: str):
    return RedirectResponse(f"/delete-item/{idx}", status_code=303)

@app.post("/add-truck")
async def add_truck(from_city: str = Form(...), to_city: str = Form(...), truck_type: str = Form(...), current_location: str = Form(""), departure_time: str = Form(""), price: str = Form(...), whatsapp: str = Form(...), distance_km: str = Form("")):
    local_id = str(uuid.uuid4())[:
