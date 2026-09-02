from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse
import uuid

app = FastAPI()
trucks_memory = []
loads_memory = []

MTN = "0964343865"
AIRTEL = "0976166422"

STYLE = """<style>
*{box-sizing:border-box}body{margin:0;font-family:sans-serif;background:#f8fafc;color:#0f172a}
header{background:#0f172a;color:#fff;padding:18px 16px;text-align:center}
.logo{font-size:28px;font-weight:900}.logo span{color:#22c55e}
.badge-across{background:#22c55e;color:#000;padding:6px 16px;border-radius:20px;font-weight:900;font-size:12px;display:inline-block;margin:8px 0}
.provinces{font-size:10px;opacity:.8;line-height:1.6;max-width:650px;margin:8px auto 0}
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
.delete-btn{position:absolute;top:10px;right:10px;background:#ef4444;color:#fff;border:none;border-radius:50%;width:28px;height:28px;font-weight:900;cursor:pointer}
.footer-contact{background:#0f172a;color:#fff;padding:14px;text-align:center;margin-top:20px}
.footer-contact b{color:#22c55e}
</style>"""

JS = """<script>
const towns={"lusaka":[-15.4067,28.2871],"kitwe":[-12.8024,28.2132],"ndola":[-12.9587,28.6365],"kabwe":[-14.4439,28.4506],"livingstone":[-17.8528,25.8553],"chipata":[-13.6296,32.6467],"kasama":[-10.2107,31.1749],"mansa":[-11.1998,28.8934],"mongu":[-15.2667,23.1167],"solwezi":[-12.1735,26.3865],"chingola":[-12.5256,27.8824],"choma":[-16.8112,26.9979],"mwinilunga":[-11.7357,24.4298],"nakonde":[-9.3359,32.7537]};
function haversine(lat1,lon1,lat2,lon2){const R=6371;const dLat=(lat2-lat1)*3.14159/180;const dLon=(lon2-lon1)*3.14159/180;const a=Math.sin(dLat/2)*Math.sin(dLat/2)+Math.cos(lat1*3.14159/180)*Math.cos(lat2*3.14159/180)*Math.sin(dLon/2)*Math.sin(dLon/2);return R*2*Math.atan2(Math.sqrt(a),Math.sqrt(1-a));}
async function calcDist(){const fromEl=document.getElementById('from_city');const toEl=document.getElementById('to_city');const distEl=document.getElementById('distance_km');const labelEl=document.getElementById('dist_label');const boxEl=document.getElementById('auto_box');if(!fromEl||!toEl||!distEl)return;const from=fromEl.value.toLowerCase();const to=toEl.value.toLowerCase();let fromKey=null,toKey=null;for(let k in towns){if(from.includes(k)){fromKey=k;break;}}for(let k in towns){if(to.includes(k)){toKey=k;break;}}if(!fromKey||!toKey){if(labelEl)labelEl.innerHTML="Type Zambian town to calc driving distance";return;}if(labelEl)labelEl.innerHTML="Calculating "+fromKey+" to "+toKey+"...";const lat1=towns[fromKey][0],lon1=towns[fromKey][1],lat2=towns[toKey][0],lon2=towns[toKey][1];const straight=Math.round(haversine(lat1,lon1,lat2,lon2));try{const url="https://router.project-osrm.org/route/v1/driving/"+lon1+","+lat1+";"+lon2+","+lat2+"?overview=false";const res=await fetch(url);const data=await res.json();if(data.routes&&data.routes[0]&&data.routes[0].distance){let km=Math.round(data.routes[0].distance/1000);let h=Math.round(data.routes[0].duration/3600*10)/10;distEl.value=km+" km";if(labelEl)labelEl.innerHTML="Driving: "+km+" km";if(boxEl)boxEl.innerHTML="Road: "+km+" km | Straight: "+straight+" km | "+h+" hrs";if(typeof calcWeightPrice==="function")calcWeightPrice();return;}}catch(e){}let est=Math.round(straight*1.38);if((fromKey=="lusaka"&&toKey=="kitwe")||(fromKey=="kitwe"&&toKey=="lusaka"))est=363;distEl.value=est+" km";if(labelEl)labelEl.innerHTML="Driving (est): "+est+" km";if(boxEl)boxEl.innerHTML="Est road: "+est+" km | Straight: "+straight+" km";if(typeof calcWeightPrice==="function")calcWeightPrice();}
function parseWeightKg(text){if(!text)return 0;let t=text.toLowerCase();let num=parseFloat(t.replace(/[^0-9.]/g,''));if(isNaN(num))return 0;if(t.includes("ton"))return num*1000;return num;}
function calcWeightPrice(){const weightEl=document.getElementById('weight');const rateEl=document.getElementById('rate_per_kg');const priceEl=document.getElementById('price');const priceBox=document.getElementById('price_calc_box');if(!weightEl||!rateEl||!priceEl)return;let kg=parseWeightKg(weightEl.value);let rate=parseFloat(rateEl.value)||30;if(kg>0){let total=Math.round(kg*rate);if(priceBox){priceBox.innerHTML="Weight: "+kg+" kg x K"+rate+" = <b>K"+total+"</b>";priceBox.style.display="block";}if(!priceEl.value||priceEl.dataset.auto=="1"){priceEl.value=total;priceEl.dataset.auto="1";}}}
function onWeightInput(){const p=document.getElementById('price');if(p)p.dataset.auto="1";calcWeightPrice();}
function onPriceManual(){const p=document.getElementById('price');if(p)p.dataset.auto="0";}
function confirmDelete(id){if(confirm('Delete this? Permanently!')){window.location.href='/delete-item/'+id;}}
</script>"""

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTMLResponse("""<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Mzigo</title>""" + STYLE + """</head><body>
<header><div class="logo">MZIGO<span>.ZM</span></div><div style="font-size:12px;opacity:.8">Zambia smart logistics - No truck empty - Weight K25-35/kg Platinum - Real driving distance</div><div class="badge-across">ACROSS ZAMBIA</div><div class="provinces"><span>Central</span><span>Copperbelt</span><span>Eastern</span><span>Luapula</span><span>Lusaka</span><span>Muchinga</span><span>Northern</span><span>North-Western</span><span>Southern</span><span>Western</span><br>10 Provinces - No numbers on top as requested</div></header>
<div class="container"><div class="card" style="background:#0f172a;color:#fff"><h2 style="margin:0">🚛 Driver</h2><a href="/driver" class="btn btn-green">Enter as Driver →</a></div><div class="card" style="border:2px solid #f97316"><h2 style="margin:0">📦 Trader - Weight Based</h2><p class="small">K25-35 per kg like Platinum</p><a href="/trader" class="btn btn-dark">Enter as Trader →</a></div></div><div class="footer-contact"><b>MTN:</b> 0964343865 | <b>Airtel:</b> 0976166422<br><span style="font-size:11px;opacity:.7">Bottom only, not top - Corrected Airtel 0976166422</span></div></body></html>""")

@app.get("/driver", response_class=HTMLResponse)
async def driver_screen():
    th = '<div class="card">No trucks yet - Be first!</div>' if not trucks_memory else ""
    for tr in trucks_memory:
        from_c = tr.get("from_city","")
        to_c = tr.get("to_city","")
        dist = tr.get("distance_km","")
        tm = str(tr.get("departure_time",""))[:16]
        loc = tr.get("current_location","")
        typ = tr.get("truck_type","")
        price = tr.get("price","")
        lid = tr.get("local_id","")
        th += '<div class="card"><button class="delete-btn" onclick="confirmDelete(\'' + lid + '\')">X</button><b>' + from_c + ' → ' + to_c + '</b><br><span class="badge bp">' + typ + '</span><span class="badge bp">K' + str(price) + '</span><br><div class="small">📍 ' + loc + ' | 📏 ' + dist + ' | 🕒 ' + tm + '</div><a class="wa" href="https://wa.me/260964343865?text=Truck ' + from_c + ' to ' + to_c + '" target="_blank">MTN: 0964343865</a><a class="wa wa-airtel" href="https://wa.me/260976166422?text=Truck" target="_blank">Airtel: 0976166422</a><br><button class="btn-red" onclick="confirmDelete(\'' + lid + '\')">🗑 Delete - Now Works!</button></div>'
    return HTMLResponse("""<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Driver</title>""" + STYLE + """</head><body>
<header><div class="logo">MZIGO<span>.ZM</span> DRIVER</div><div class="badge-across">ACROSS ZAMBIA</div><div class="provinces"><span>Central</span><span>Copperbelt</span><span>Eastern</span><span>Luapula</span><span>Lusaka</span><span>Muchinga</span><span>Northern</span><span>North-Western</span><span>Southern</span><span>Western</span></div></header>
<div class="container"><a href="/" class="back">← Home</a> <a href="/trader" class="back" style="float:right">Trader →</a>
<div class="card" style="background:#0f172a;color:#fff"><h3>🚛 Post Empty Truck - V16 GREEN + Delete Fixed + Provinces Back</h3><form action="/add-truck" method="post">
<label>From</label><input id="from_city" name="from_city" placeholder="e.g. Kitwe" required oninput="calcDist()">
<label>To</label><input id="to_city" name="to_city" placeholder="e.g. Lusaka" required oninput="calcDist()">
<label id="dist_label">Distance auto (driving)</label><input id="distance_km" name="distance_km" placeholder="Auto driving" readonly style="background:#dcfce7;font-weight:800"><div class="auto-box" id="auto_box">Real driving distance - 362km Kitwe→Lusaka</div>
<label>Truck Type</label><input name="truck_type" placeholder="e.g. 50 ton" required>
<label>Current Location</label><input name="current_location" placeholder="e.g. Total Sports">
<label>Set Departure Date & Time</label><input name="departure_time" type="datetime-local" required>
<label>Price</label><input name="price" placeholder="e.g. 10000" required>
<label>WhatsApp</label><input name="whatsapp" placeholder="e.g. 0964343865" required>
<button class="btn btn-green" type="submit">Post Truck - Will Save & Show!</button>
</form></div><h3>🚛 Trucks (""" + str(len(trucks_memory)) + """) - Delete FIXED!</h3>""" + th + """</div><div class="footer-contact"><b>MTN:</b> 0964343865 | <b>Airtel:</b> 0976166422 - Bottom only</div>""" + JS + """</body></html>""")

@app.get("/trader", response_class=HTMLResponse)
async def trader_screen():
    lh = '<div class="card">No loads yet</div>' if not loads_memory else ""
    for tr in loads_memory:
        from_c = tr.get("from_city","")
        to_c = tr.get("to_city","")
        goods = tr.get("goods_type","")
        w = tr.get("weight","")
        dist = tr.get("distance_km","")
        price = tr.get("price","")
        rate = tr.get("rate_per_kg","30")
        lid = tr.get("local_id","")
        lh += '<div class="card"><button class="delete-btn" onclick="confirmDelete(\'' + lid + '\')">X</button><b>' + from_c + ' → ' + to_c + '</b><br><span class="badge">' + goods + ' ' + w + '</span> <span class="badge" style="background:#dcfce7">📏 ' + dist + '</span><br><span class="badge bp">K' + str(price) + ' (K' + str(rate) + '/kg)</span><br><a class="wa" href="https://wa.me/260964343865?text=Load" target="_blank">MTN: 0964343865</a><a class="wa wa-airtel" href="https://wa.me/260976166422?text=Load" target="_blank">Airtel: 0976166422</a><br><button class="btn-red" onclick="confirmDelete(\'' + lid + '\')">🗑 Delete</button></div>'
    return HTMLResponse("""<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Trader</title>""" + STYLE + """</head><body>
<header><div class="logo">MZIGO<span>.ZM</span> TRADER</div><div class="badge-across">ACROSS ZAMBIA</div><div class="provinces"><span>Central</span><span>Copperbelt</span><span>Eastern</span><span>Luapula</span><span>Lusaka</span><span>Muchinga</span><span>Northern</span><span>North-Western</span><span>Southern</span><span>Western</span></div></header>
<div class="container"><a href="/" class="back">← Home</a> <a href="/driver" class="back" style="float:right">Driver →</a>
<div class="card" style="border:2px solid #f97316"><h3>📦 Post Load - Weight K25-35/kg Platinum</h3><form action="/add-load" method="post">
<label>From</label><input id="from_city" name="from_city" placeholder="e.g. Lusaka" required oninput="calcDist()">
<label>To</label><input id="to_city" name="to_city" placeholder="e.g. Ndola" required oninput="calcDist()">
<label id="dist_label">Distance auto</label><input id="distance_km" name="distance_km" placeholder="Auto" readonly style="background:#dcfce7;font-weight:800"><div class="auto-box" id="auto_box">Real road distance</div>
<label>Goods Type</label><input name="goods_type" placeholder="e.g. Maize" required>
<label>Weight (kg or tons)</label><input id="weight" name="weight" placeholder="e.g. 1000 kg or 1.5 tons" required oninput="onWeightInput()">
<label>Rate per kg</label><select id="rate_per_kg" name="rate_per_kg" onchange="calcWeightPrice()"><option value="25">K25/kg Budget</option><option value="30" selected>K30/kg Standard</option><option value="35">K35/kg Express</option><option value="50">K50/kg Urgent</option></select><div id="price_calc_box" class="price-box" style="display:none">Enter weight</div>
<label>Set Date & Time</label><input name="departure_time" type="datetime-local" required>
<label>Total Budget (Auto from weight)</label><input id="price" name="price" placeholder="Auto from weight" required oninput="onPriceManual()" data-auto="1">
<label>WhatsApp</label><input name="whatsapp" placeholder="e.g. 0964343865" required>
<button class="btn btn-orange" type="submit">Post Load - Weight Based</button>
</form></div><h3>📦 Loads (""" + str(len(loads_memory)) + """)</h3>""" + lh + """</div><div class="footer-contact"><b>MTN:</b> 0964343865 | <b>Airtel:</b> 0976166422</div>""" + JS + """</body></html>""")

@app.get("/delete-item/{item_id}")
async def delete_item(item_id: str):
    global trucks_memory, loads_memory
    trucks_memory = [t for t in trucks_memory if str(t.get('local_id'))!= str(item_id)]
    loads_memory = [l for l in loads_memory if str(l.get('local_id'))!= str(item_id)]
    return RedirectResponse("/driver", status_code=303)

@app.post("/add-truck")
async def add_truck(from_city: str = Form(...), to_city: str = Form(...), truck_type: str = Form(...), current_location: str = Form(""), departure_time: str = Form(""), price: str = Form(...), whatsapp: str = Form(...), distance_km: str = Form("")):
    data = {"local_id": str(uuid.uuid4())[:8], "from_city": from_city.strip(), "to_city": to_city.strip(), "truck_type": truck_type.strip(), "current_location": current_location.strip(), "departure_time": departure_time.strip(), "price": price.strip(), "whatsapp": whatsapp.strip(), "distance_km": distance_km.strip()}
    trucks_memory.insert(0, data)
    return RedirectResponse("/driver", status_code=303)

@app.post("/add-load")
async def add_load(from_city: str = Form(...), to_city: str = Form(...), goods_type: str = Form(...), weight: str = Form(...), distance_km: str = Form(""), departure_time: str = Form(""), price: str = Form(...), whatsapp: str = Form(...), rate_per_kg: str = Form("30")):
    data = {"local_id": str(uuid.uuid4())[:8], "from_city": from_city.strip(), "to_city": to_city.strip(), "goods_type": goods_type.strip(), "weight": weight.strip(), "distance_km": distance_km.strip(), "departure_time": departure_time.strip(), "price": price.strip(), "whatsapp": whatsapp.strip(), "rate_per_kg": rate_per_kg.strip()}
    loads_memory.insert(0, data)
    return RedirectResponse("/trader", status_code=303)

@app.get("/health")
async def health():
    return {"ok": True, "mtn": MTN, "airtel": AIRTEL, "trucks": len(trucks_memory)}
