from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse
import uuid, os
app = FastAPI()
trucks = []
MTN="0964343865"
AIRTEL="0976166422"
MTN_NAME="MWNSA MULENGA"
AIRTEL_NAME="PRAISBE MWAPE"

@app.get("/", response_class=HTMLResponse)
async def home():
    return f"""
<html><head><meta name="viewport" content="width=device-width, initial-scale=1"><style>
body{{margin:0;font-family:sans-serif;background:#f8fafc;text-align:center}}
header{{background:#0f172a;color:#fff;padding:20px}}.logo{{font-size:30px;font-weight:900}}.logo span{{color:#22c55e}}
.badge{{background:#22c55e;color:#000;padding:5px 14px;border-radius:20px;font-weight:900;display:inline-block;margin:8px}}
.card{{background:#fff;border-radius:16px;padding:18px;margin:12px;border:1px solid #e2e8f0;max-width:600px;margin-left:auto;margin-right:auto}}
.btn{{padding:12px 20px;border-radius:10px;font-weight:900;text-decoration:none;display:inline-block;margin:5px}}
.btn-green{{background:#22c55e;color:#000}}.btn-dark{{background:#0f172a;color:#fff}}
</style></head><body>
<header><div class="logo">MZIGO<span>.ZM</span></div><div class="badge">ACROSS ZAMBIA</div><div style="font-size:10px">All 10 Provinces - Kitwe Lusaka Ndola Kabwe Livingstone etc</div></header>
<div class="card"><h2>🚛 Driver</h2><a href="/driver" class="btn btn-green">Enter Driver</a></div>
<div class="card"><h2>📦 Trader</h2><a href="/trader" class="btn btn-dark">Enter Trader</a></div>
<div class="card" style="background:#dcfce7"><h3>💰 Pay</h3>MTN {MTN} ({MTN_NAME})<br>Airtel {AIRTEL} ({AIRTEL_NAME})</div>
<div style="background:#0f172a;color:#fff;padding:12px"><b>MTN:</b> {MTN} ({MTN_NAME}) | <b>Airtel:</b> {AIRTEL} ({AIRTEL_NAME})</div>
</body></html>
"""

@app.get("/driver", response_class=HTMLResponse)
async def driver_get():
    html=""
    if not trucks: html='<div class="card">No trucks yet</div>'
    for t in trucks:
        html+=f"<div class='card'><b>{t['from_city']}→{t['to_city']}</b> {t['distance_km']} K{t['price']} <a href='/delete-truck/{t['id']}' style='background:#ef4444;color:#fff;padding:4px 10px;border-radius:10px;text-decoration:none'>Delete</a></div>"
    return f"""
<html><head><meta name="viewport" content="width=device-width, initial-scale=1"><style>
body{{margin:0;font-family:sans-serif;background:#f8fafc}}.container{{max-width:600px;margin:0 auto;padding:14px}}
.card{{background:#fff;border-radius:14px;padding:16px;margin:10px 0;border:1px solid #e2e8f0}}
.btn{{width:100%;padding:12px;border:none;border-radius:10px;font-weight:900;background:#22c55e}}
input{{width:100%;padding:10px;border-radius:8px;border:1px solid #ddd;margin-top:4px;box-sizing:border-box}}
label{{font-size:11px;font-weight:800;margin-top:8px;display:block}}
.box{{background:#dcfce7;border:2px dashed #22c55e;padding:8px;border-radius:8px;margin-top:6px;font-weight:800;font-size:12px}}
</style></head><body>
<div class="container"><a href="/" style="text-decoration:none;background:#e2e8f0;padding:6px 12px;border-radius:20px">← Home</a>
<div class="card" style="background:#0f172a;color:#fff"><h3>Post Truck - Auto 363km Kitwe→Lusaka</h3>
<form action="/add-truck" method="post">
<label>From</label><input id="from_city" name="from_city" placeholder="Kitwe" required>
<label>To</label><input id="to_city" name="to_city" placeholder="Lusaka" required>
<label>Distance Auto</label><input id="distance_km" name="distance_km" readonly style="background:#dcfce7;font-weight:900">
<div id="info" class="box">Type Kitwe → Lusaka = 363 km</div>
<label>Truck Type</label><input name="truck_type" placeholder="50 ton" required>
<label>Location</label><input name="current_location" placeholder="Total Sports" required>
<label>Time</label><input name="departure_time" type="datetime-local" required>
<label>Price</label><input name="price" placeholder="10000" required>
<label>WhatsApp</label><input name="whatsapp" placeholder="0964343865" required>
<button class="btn" type="submit">Post</button>
</form></div>
<h3>Trucks ({len(trucks)})</h3>{html}
</div>
<div style="background:#0f172a;color:#fff;padding:10px;text-align:center;font-size:10px"><b>MTN:</b> {MTN} ({MTN_NAME}) | <b>Airtel:</b> {AIRTEL} ({AIRTEL_NAME})</div>
<script>
const towns={{"lusaka":[-15.4,28.2],"kitwe":[-12.8,28.2],"ndola":[-12.9,28.6],"kabwe":[-14.4,28.4],"livingstone":[-17.8,25.8]}};
function hav(a,b,c,d){{const R=6371;const dLat=(c-a)*3.1416/180;const dLon=(d-b)*3.1416/180;const e=Math.sin(dLat/2)**2+Math.cos(a*3.1416/180)*Math.cos(c*3.1416/180)*Math.sin(dLon/2)**2;return R*2*Math.atan2(Math.sqrt(e),Math.sqrt(1-e));}}
function calc(){{let f=document.getElementById('from_city').value.toLowerCase();let t=document.getElementById('to_city').value.toLowerCase();let i=document.getElementById('info');let d=document.getElementById('distance_km');if(!f||!t){{i.innerText="Type Kitwe → Lusaka = 363 km";return;}}let fk=null,tk=null;for(let k in towns)if(f.includes(k))fk=k;for(let k in towns)if(t.includes(k))tk=k;if(!fk||!tk){{i.innerText="Try Kitwe, Lusaka, Ndola...";d.value="";return;}}let lat1=towns[fk][0],lon1=towns[fk][1],lat2=towns[tk][0],lon2=towns[tk][1];let s=hav(lat1,lon1,lat2,lon2);let r=Math.round(s*1.38);if((fk=="lusaka"&&tk=="kitwe")||(fk=="kitwe"&&tk=="lusaka"))r=363;if((fk=="lusaka"&&tk=="ndola")||(fk=="ndola"&&tk=="lusaka"))r=321;d.value=r+" km";i.innerText="✅ "+r+" km driving "+fk+"→"+tk;}}
document.getElementById('from_city').addEventListener('input',calc);document.getElementById('to_city').addEventListener('input',calc);
</script>
</body></html>
"""

@app.post("/add-truck")
async def add_truck(from_city: str = Form(...), to_city: str = Form(...), truck_type: str = Form(...), current_location: str = Form(""), departure_time: str = Form(""), price: str = Form(...), whatsapp: str = Form(...), distance_km: str = Form("")):
    if not distance_km:
        if "kitwe" in from_city.lower() and "lusaka" in to_city.lower() or "lusaka" in from_city.lower() and "kitwe" in to_city.lower():
            distance_km="363 km"
    trucks.insert(0, {"id": str(uuid.uuid4())[:8], "from_city": from_city.strip(), "to_city": to_city.strip(), "truck_type": truck_type.strip(), "current_location": current_location.strip(), "departure_time": departure_time.strip(), "price": price.strip(), "whatsapp": whatsapp.strip(), "distance_km": distance_km.strip()})
    return RedirectResponse("/driver", status_code=303)

@app.get("/delete-truck/{tid}")
async def del_truck(tid: str):
    global trucks
    trucks=[t for t in trucks if t['id']!=tid]
    return RedirectResponse("/driver", status_code=303)

@app.get("/trader", response_class=HTMLResponse)
async def trader_page():
    return f"<html><body><a href='/'>Home</a><h1>Trader - K30/kg</h1><p>MTN {MTN} ({MTN_NAME})<br>Airtel {AIRTEL} ({AIRTEL_NAME})</p><a href='/'>Home</a></body></html>"

@app.get("/health")
async def health():
    return {"ok": True}

if __name__=="__main__":
    import uvicorn
    port=int(os.environ.get("PORT",10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
