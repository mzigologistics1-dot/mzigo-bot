from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, PlainTextResponse
import uuid, os

app = FastAPI()
trucks = []
loads = []

MTN = "0964343865"
AIRTEL = "0976166422"

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>MZIGO.ZM</title>
<style>
body{margin:0;font-family:sans-serif;background:#f8fafc}
header{background:#0f172a;color:#fff;padding:18px;text-align:center}
.logo{font-size:30px;font-weight:900}.logo span{color:#22c55e}
.badge{background:#22c55e;color:#000;padding:5px 14px;border-radius:20px;font-weight:900;font-size:12px;display:inline-block;margin:8px}
.prov{font-size:10px;opacity:.8}
.prov span{background:#1e293b;padding:3px 8px;border-radius:10px;margin:2px;display:inline-block}
.container{max-width:700px;margin:0 auto;padding:14px}
.card{background:#fff;border-radius:16px;padding:18px;margin:12px 0;border:1px solid #e2e8f0}
.btn{width:100%;padding:12px;border:none;border-radius:10px;font-weight:900;margin-top:8px;display:block;text-align:center;text-decoration:none}
.btn-green{background:#22c55e;color:#000}
.btn-dark{background:#0f172a;color:#fff}
.btn-blue{background:#3b82f6;color:#fff}
.footer{background:#0f172a;color:#fff;padding:12px;text-align:center}
.footer b{color:#22c55e}
</style></head><body>
<header>
<div class="logo">MZIGO<span>.ZM</span></div>
<div style="font-size:12px">Zambia's smart logistics - No truck returns empty</div>
<div class="badge">ACROSS ZAMBIA</div>
<div class="prov"><span>Central</span><span>Copperbelt</span><span>Eastern</span><span>Luapula</span><span>Lusaka</span><span>Muchinga</span><span>Northern</span><span>North-Western</span><span>Southern</span><span>Western</span></div>
</header>
<div class="container">
<div class="card" style="background:#0f172a;color:#fff"><h2 style="margin:0">🚛 I'm a Driver</h2><p style="font-size:13px;opacity:.8">Post empty truck across Zambia</p><a href="/driver" class="btn btn-green">Enter as Driver →</a></div>
<div class="card" style="border:2px solid #f97316"><h2 style="margin:0">📦 I'm a Trader</h2><p style="font-size:13px;color:#64748b">Need truck? Weight-based K25-35/kg Platinum</p><a href="/trader" class="btn btn-dark">Enter as Trader →</a></div>
<div class="card" style="background:#dcfce7;border:2px solid #22c55e"><h3 style="margin:0">🤖 WhatsApp Bot Active</h3><p style="font-size:12px">Auto-reply: trucks, pay MTN 0964343865 | Airtel 0976166422, weight pricing</p><a href="/whatsapp-bot" class="btn btn-green">View Bot Setup →</a><a href="/test-bot?msg=truck" class="btn btn-blue">Test Bot Reply</a></div>
</div>
<div class="footer"><b>MTN:</b> 0964343865 | <b>Airtel:</b> 0976166422</div>
</body></html>
"""

@app.get("/driver", response_class=HTMLResponse)
async def driver_get():
    html_trucks = ""
    if not trucks:
        html_trucks = '<div class="card">No trucks yet - Be first to post!</div>'
    else:
        for t in trucks:
            lid = t['id']
            html_trucks += f"""<div class="card"><b>{t['from_city']} → {t['to_city']}</b><br>
<span style="background:#0f172a;color:#fff;padding:4px 8px;border-radius:10px;font-size:11px">{t['truck_type']} K{t['price']}</span><br>
<small>📍 {t['current_location']} | 📏 {t['distance_km']} | 🕒 {t['departure_time']}</small><br>
<a href="https://wa.me/260964343865?text=Truck {t['from_city']} to {t['to_city']} {t['distance_km']}" target="_blank" style="background:#22c55e;color:#000;padding:6px 10px;border-radius:8px;text-decoration:none;font-size:11px;font-weight:900;margin-top:6px;display:inline-block">MTN</a>
<a href="https://wa.me/260976166422?text=Truck" target="_blank" style="background:#3b82f6;color:#fff;padding:6px 10px;border-radius:8px;text-decoration:none;font-size:11px;font-weight:900;margin-top:6px;display:inline-block;margin-left:6px">Airtel</a>
<br><a href="/delete-truck/{lid}" style="background:#ef4444;color:#fff;padding:6px 12px;border-radius:20px;font-size:11px;text-decoration:none;display:inline-block;margin-top:8px" onclick="return confirm('Delete?')">🗑 Delete</a>
</div>"""
    return f"""
<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Driver</title>
<style>
body{{margin:0;font-family:sans-serif;background:#f8fafc}}
header{{background:#0f172a;color:#fff;padding:14px;text-align:center}}
.container{{max-width:700px;margin:0 auto;padding:14px}}
.card{{background:#fff;border-radius:14px;padding:16px;margin:10px 0;border:1px solid #e2e8f0}}
.btn{{width:100%;padding:12px;border:none;border-radius:10px;font-weight:900;margin-top:8px;display:block;text-align:center;text-decoration:none;cursor:pointer}}
.btn-green{{background:#22c55e;color:#000}}
input{{width:100%;padding:10px;border-radius:8px;border:1px solid #ddd;margin-top:4px}}
label{{font-size:11px;font-weight:800;margin-top:8px;display:block}}
</style>
<script>
const towns={{"lusaka":[-15.4067,28.2871],"kitwe":[-12.8024,28.2132],"ndola":[-12.9587,28.6365],"kabwe":[-14.4439,28.4506],"livingstone":[-17.8528,25.8553],"chipata":[-13.6296,32.6467],"kasama":[-10.2107,31.1749],"mansa":[-11.1998,28.8934],"mongu":[-15.2667,23.1167],"solwezi":[-12.1735,26.3865]}};
function haversine(a,b,c,d){{const R=6371;const dLat=(c-a)*Math.PI/180;const dLon=(d-b)*Math.PI/180;const e=Math.sin(dLat/2)*Math.sin(dLat/2)+Math.cos(a*Math.PI/180)*Math.cos(c*Math.PI/180)*Math.sin(dLon/2)*Math.sin(dLon/2);return R*2*Math.atan2(Math.sqrt(e),Math.sqrt(1-e));}}
function calcDist(){{
let from=document.getElementById('from_city').value.toLowerCase();
let to=document.getElementById('to_city').value.toLowerCase();
let fk=null,tk=null;
for(let k in towns){{if(from.includes(k)){{fk=k;break;}}}}
for(let k in towns){{if(to.includes(k)){{tk=k;break;}}}}
if(!fk||!tk){{document.getElementById('dist_label').innerText="Type Zambian town";return;}}
let lat1=towns[fk][0],lon1=towns[fk][1],lat2=towns[tk][0],lon2=towns[tk][1];
let straight=Math.round(haversine(lat1,lon1,lat2,lon2));
let est=Math.round(straight*1.38);
if((fk=="lusaka"&&tk=="kitwe")||(fk=="kitwe"&&tk=="lusaka"))est=363;
document.getElementById('distance_km').value=est+" km";
document.getElementById('dist_label').innerText="Distance: "+est+" km driving (road)";
}}
</script>
</head><body>
<header><div style="font-size:22px;font-weight:900">MZIGO.ZM DRIVER</div><div style="background:#22c55e;color:#000;padding:4px 12px;border-radius:20px;display:inline-block;margin-top:6px;font-weight:900;font-size:11px">ACROSS ZAMBIA</div></header>
<div class="container">
<a href="/" style="background:#e2e8f0;padding:6px 12px;border-radius:20px;text-decoration:none;color:#000;font-size:12px">← Home</a>
<div class="card" style="background:#0f172a;color:#fff">
<h3>🚛 Post Empty Truck</h3>
<form action="/add-truck" method="post">
<label>From</label><input id="from_city" name="from_city" placeholder="e.g. Kitwe" required oninput="calcDist()">
<label>To</label><input id="to_city" name="to_city" placeholder="e.g. Lusaka" required oninput="calcDist()">
<label id="dist_label">Distance</label><input id="distance_km" name="distance_km" placeholder="Auto driving distance" readonly style="background:#dcfce7;font-weight:800">
<label>Truck Type</label><input name="truck_type" placeholder="e.g. 50 ton" required>
<label>Current Location</label><input name="current_location" placeholder="e.g. Total Sports">
<label>Departure Time</label><input name="departure_time" type="datetime-local" required>
<label>Price ZMW</label><input name="price" placeholder="e.g. 10000" required>
<label>WhatsApp</label><input name="whatsapp" placeholder="e.g. 0964343865" required>
<button class="btn btn-green" type="submit">Post Truck</button>
</form>
</div>
<h3>🚛 Trucks ({len(trucks)})</h3>
{html_trucks}
</div>
<div style="background:#0f172a;color:#fff;padding:12px;text-align:center"><b>MTN:</b> 0964343865 | <b>Airtel:</b> 0976166422</div>
</body></html>
"""

@app.post("/add-truck")
async def add_truck(from_city: str = Form(...), to_city: str = Form(...), truck_type: str = Form(...), current_location: str = Form(""), departure_time: str = Form(""), price: str = Form(...), whatsapp: str = Form(...), distance_km: str = Form("")):
    trucks.insert(0, {"id": str(uuid.uuid4())[:8], "from_city": from_city.strip(), "to_city": to_city.strip(), "truck_type": truck_type.strip(), "current_location": current_location.strip(), "departure_time": departure_time.strip(), "price": price.strip(), "whatsapp": whatsapp.strip(), "distance_km": distance_km.strip()})
    return RedirectResponse("/driver", status_code=303)

@app.get("/delete-truck/{tid}")
async def delete_truck(tid: str):
    global trucks
    trucks = [t for t in trucks if t['id']!= tid]
    return RedirectResponse("/driver", status_code=303)

@app.get("/trader", response_class=HTMLResponse)
async def trader_get():
    html_loads = ""
    if not loads:
        html_loads = '<div class="card">No loads yet</div>'
    else:
        for l in loads:
            lid = l['id']
            html_loads += f"""<div class="card"><b>{l['from_city']} → {l['to_city']}</b><br>
<span style="background:#fff8ed;border:1px solid #f97316;padding:4px 8px;border-radius:10px;font-size:11px">{l['goods_type']} {l['weight']} K{l['price']} (K{l['rate_per_kg']}/kg)</span><br>
<small>📏 {l['distance_km']}</small><br>
<a href="/delete-load/{lid}" style="background:#ef4444;color:#fff;padding:6px 12px;border-radius:20px;font-size:11px;text-decoration:none;display:inline-block;margin-top:8px" onclick="return confirm('Delete?')">🗑 Delete</a>
</div>"""
    return f"""
<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Trader</title>
<style>
body{{margin:0;font-family:sans-serif;background:#f8fafc}}
header{{background:#0f172a;color:#fff;padding:14px;text-align:center}}
.container{{max-width:700px;margin:0 auto;padding:14px}}
.card{{background:#fff;border-radius:14px;padding:16px;margin:10px 0;border:1px solid #e2e8f0}}
.btn{{width:100%;padding:12px;border:none;border-radius:10px;font-weight:900;margin-top:8px;display:block;text-align:center;text-decoration:none}}
.btn-orange{{background:#f97316;color:#fff}}
input,select{{width:100%;padding:10px;border-radius:8px;border:1px solid #ddd;margin-top:4px}}
label{{font-size:11px;font-weight:800;margin-top:8px;display:block}}
.calc{{background:#fff8ed;border:2px solid #f97316;padding:10px;border-radius:10px;margin-top:6px;display:none}}
</style>
<script>
function parseKg(t){{if(!t)return 0;let n=parseFloat(t.replace(/[^0-9.]/g,''));if(isNaN(n))return 0;if(t.toLowerCase().includes("ton"))return n*1000;return n;}}
function calcPrice(){{
let w=document.getElementById('weight').value;
let r=document.getElementById('rate_per_kg').value;
let kg=parseKg(w);
let rate=parseFloat(r)||30;
if(kg>0){{
let total=Math.round(kg*rate);
document.getElementById('price').value=total;
let box=document.getElementById('calc_box');
box.innerHTML="Weight: "+kg+"kg x K"+rate+" = <b>K"+total+"</b>";
box.style.display="block";
}}
}}
const towns={{"lusaka":[-15.4067,28.2871],"kitwe":[-12.8024,28.2132],"ndola":[-12.9587,28.6365]}};
function haversine(a,b,c,d){{const R=6371;const dLat=(c-a)*Math.PI/180;const dLon=(d-b)*Math.PI/180;const e=Math.sin(dLat/2)*Math.sin(dLat/2)+Math.cos(a*Math.PI/180)*Math.cos(c*Math.PI/180)*Math.sin(dLon/2)*Math.sin(dLon/2);return R*2*Math.atan2(Math.sqrt(e),Math.sqrt(1-e));}}
function calcDist(){{
let from=document.getElementById('from_city').value.toLowerCase();
let to=document.getElementById('to_city').value.toLowerCase();
let fk=null,tk=null;
for(let k in towns){{if(from.includes(k)){{fk=k;break;}}}}
for(let k in towns){{if(to.includes(k)){{tk=k;break;}}}}
if(!fk||!tk)return;
let lat1=towns[fk][0],lon1=towns[fk][1],lat2=towns[tk][0],lon2=towns[tk][1];
let straight=Math.round(haversine(lat1,lon1,lat2,lon2));
let est=Math.round(straight*1.38);
if((fk=="lusaka"&&tk=="kitwe")||(fk=="kitwe"&&tk=="lusaka"))est=363;
document.getElementById('distance_km').value=est+" km";
}}
</script>
</head><body>
<header><div style="font-size:22px;font-weight:900">MZIGO.ZM TRADER</div><div style="background:#22c55e;color:#000;padding:4px 12px;border-radius:20px;display:inline-block;margin-top:6px;font-weight:900;font-size:11px">WEIGHT PRICING K25-35/kg</div></header>
<div class="container">
<a href="/" style="background:#e2e8f0;padding:6px 12px;border-radius:20px;text-decoration:none;color:#000;font-size:12px">← Home</a>
<div class="card" style="border:2px solid #f97316">
<h3>📦 Post Load - Weight Based (Platinum)</h3>
<form action="/add-load" method="post">
<label>From</label><input id="from_city" name="from_city" placeholder="Lusaka" required oninput="calcDist()">
<label>To</label><input id="to_city" name="to_city" placeholder="Ndola" required oninput="calcDist()">
<label>Distance</label><input id="distance_km" name="distance_km" placeholder="Auto road distance" readonly style="background:#dcfce7">
<label>Goods Type</label><input name="goods_type" placeholder="Maize" required>
<label>Weight</label><input id="weight" name="weight" placeholder="1000 kg or 1.5 tons" required oninput="calcPrice()">
<label>Rate per kg</label><select id="rate_per_kg" name="rate_per_kg" onchange="calcPrice()"><option value="25">K25/kg Budget</option><option value="30" selected>K30/kg Standard ⭐</option><option value="35">K35/kg Express</option><option value="50">K50/kg Urgent</option></select>
<div id="calc_box" class="calc"></div>
<label>Date & Time</label><input name="departure_time" type="datetime-local" required>
<label>Total Budget (auto)</label><input id="price" name="price" placeholder="Auto from weight" required>
<label>WhatsApp</label><input name="whatsapp" placeholder="0964343865" required>
<button class="btn btn-orange" type="submit">Post Load</button>
</form>
</div>
<h3>📦 Loads ({len(loads)})</h3>
{html_loads}
</div>
<div style="background:#0f172a;color:#fff;padding:12px;text-align:center"><b>MTN:</b> 0964343865 | <b>Airtel:</b> 0976166422</div>
</body></html>
"""

@app.post("/add-load")
async def add_load(from_city: str = Form(...), to_city: str = Form(...), goods_type: str = Form(...), weight: str = Form(...), distance_km: str = Form(""), departure_time: str = Form(""), price: str = Form(...), whatsapp: str = Form(...), rate_per_kg: str = Form("30")):
    loads.insert(0, {"id": str(uuid.uuid4())[:8], "from_city": from_city.strip(), "to_city": to_city.strip(), "goods_type": goods_type.strip(), "weight": weight.strip(), "distance_km": distance_km.strip(), "departure_time": departure_time.strip(), "price": price.strip(), "whatsapp": whatsapp.strip(), "rate_per_kg": rate_per_kg.strip()})
    return RedirectResponse("/trader", status_code=303)

@app.get("/delete-load/{lid}")
async def delete_load(lid: str):
    global loads
    loads = [l for l in loads if l['id']!= lid]
    return RedirectResponse("/trader", status_code=303)

@app.get("/whatsapp-bot", response_class=HTMLResponse)
async def bot_page():
    return """
<html><head><meta name="viewport" content="width=device-width, initial-scale=1"><style>
body{font-family:sans-serif;background:#f8fafc;margin:0}header{background:#0f172a;color:#fff;padding:14px;text-align:center}
.container{max-width:700px;margin:0 auto;padding:14px}.card{background:#fff;border-radius:14px;padding:16px;margin:10px 0;border:1px solid #e2e8f0}
.bot{background:#dcfce7;border-left:4px solid #22c55e;padding:10px;border-radius:8px;margin:8px 0;font-size:13px}
.btn{padding:12px;border:none;border-radius:10px;font-weight:900;text-decoration:none;display:block;text-align:center;margin-top:8px}
.btn-green{background:#22c55e;color:#000}.btn-blue{background:#3b82f6;color:#fff}
</style></head><body>
<header><div style="font-size:22px;font-weight:900">MZIGO WHATSAPP BOT</div></header>
<div class="container"><a href="/" style="background:#e2e8f0;padding:6px 12px;border-radius:20px;text-decoration:none;color:#000;font-size:12px">← Home</a>
<div class="card"><h3>🤖 Bot Active</h3>
<div class="bot">User: "truck"<br>Bot: "🚛 Kitwe → Lusaka 362km driving | K10000 | Pay MTN 0964343865 | Airtel 0976166422"</div>
<p style="font-size:12px">Webhook: <code>/whatsapp-webhook</code> - Set in Twilio to auto-reply<br>Commands: truck/1, load/2, pay/5, price/kg, help/6</p>
<p><b>MTN:</b> 0964343865<br><b>Airtel:</b> 0976166422</p>
<a href="/test-bot?msg=truck" class="btn btn-green">Test Bot: truck</a>
<a href="/test-bot?msg=pay" class="btn btn-blue">Test Bot: pay</a>
</div></div></body></html>
"""

@app.get("/test-bot", response_class=HTMLResponse)
async def test_bot(msg: str = "truck"):
    trucks_text = "No trucks now. Be first at /driver"
    if trucks:
        trucks_text = ""
        for t in trucks[:3]:
            trucks_text += f"{t['from_city']}→{t['to_city']} {t['distance_km']} K{t['price']}\n"
    m = msg.lower()
    if "pay" in m or m=="5":
        reply = f"PAYMENT:\nMTN MoMo: {MTN}\nAirtel Money: {AIRTEL}\nName: Josiah Mwape\nSend screenshot after payment"
    elif "truck" in m or m=="1":
        reply = f"TRUCKS ACROSS ZAMBIA:\n{trucks_text}\nPay: MTN {MTN} | Airtel {AIRTEL}"
    elif "price" in m or "kg" in m:
        reply = f"WEIGHT PRICING:\nK25/kg Budget\nK30/kg Standard\nK35/kg Express\nK50/kg Urgent\nExample: 1000kg x K30=K30000\nPay MTN {MTN} | Airtel {AIRTEL}"
    else:
        reply = f"MZIGO.ZM\n{trucks_text}\nPay MTN {MTN} | Airtel {AIRTEL}\nMenu: 1=trucks 2=loads 5=pay 6=help"
    return f"""
<html><head><meta name="viewport" content="width=device-width, initial-scale=1"><style>
body{{font-family:sans-serif;background:#f8fafc;margin:0}}.container{{max-width:700px;margin:0 auto;padding:14px}}
.card{{background:#fff;border-radius:14px;padding:16px;margin:10px 0;border:1px solid #e2e8f0}}
.bot{{background:#dcfce7;border-left:4px solid #22c55e;padding:10px;border-radius:8px;white-space:pre-wrap;font-size:13px}}
</style></head><body><div class="container">
<a href="/whatsapp-bot" style="background:#e2e8f0;padding:6px 12px;border-radius:20px;text-decoration:none;color:#000;font-size:12px">← Bot</a>
<div class="card"><h3>Bot Test: {msg}</h3><div class="bot">{reply}</div>
<form action="/test-bot" method="get" style="margin-top:10px"><input name="msg" placeholder="truck, pay..." value="{msg}" style="width:65%;padding:8px;border-radius:8px;border:1px solid #ddd"><button type="submit" style="padding:8px 12px;background:#22c55e;border:none;border-radius:8px;font-weight:900">Send</button></form>
</div></div></body></html>
"""

@app.post("/whatsapp-webhook")
async def webhook(request: Request):
    try:
        form = await request.form()
        body = (form.get("Body") or "").lower()
        trucks_text = "No trucks now"
        if trucks:
            trucks_text = ""
            for t in trucks[:3]:
                trucks_text += f"{t['from_city']}->{t['to_city']} {t['distance_km']} K{t['price']}\n"
        if "truck" in body or body=="1":
            txt = f"TRUCKS:\n{trucks_text}\nPay MTN {MTN} | Airtel {AIRTEL}"
        elif "pay" in body or body=="5":
            txt = f"MTN: {MTN}\nAirtel: {AIRTEL}"
        else:
            txt = f"MZIGO.ZM\n{trucks_text}\nMTN {MTN} | Airtel {AIRTEL}\n1=trucks 5=pay"
        twiml = f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{txt}</Message></Response>'
        return PlainTextResponse(twiml, media_type="application/xml")
    except:
        return PlainTextResponse(f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>MTN {MTN} | Airtel {AIRTEL}</Message></Response>', media_type="application/xml")

@app.get("/whatsapp-webhook")
async def webhook_get():
    return {"status":"active","mtn":MTN,"airtel":AIRTEL}

@app.get("/health")
async def health():
    return {"ok": True}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
