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
    return f"""<html><head><meta name="viewport" content="width=device-width, initial-scale=1"><title>MZIGO.ZM</title>
<style>body{{margin:0;font-family:sans-serif;background:#f8fafc;text-align:center}}header{{background:#0f172a;color:#fff;padding:20px}}.logo{{font-size:32px;font-weight:900}}.logo span{{color:#22c55e}}.card{{background:#fff;border-radius:16px;padding:18px;margin:12px auto;max-width:600px;border:1px solid #e2e8f0}}.btn{{padding:12px 20px;border-radius:10px;font-weight:900;text-decoration:none;display:inline-block;margin:5px}}.btn-green{{background:#22c55e;color:#000}}.btn-dark{{background:#0f172a;color:#fff}}</style>
</head><body><header><div class="logo">MZIGO<span>.ZM</span></div><div>Zambia Logistics - Kitwe→Lusaka 363km</div></header>
<div class="card"><h2>🚛 Driver</h2><a href="/driver" class="btn btn-green">Enter</a></div>
<div class="card"><h2>📦 Trader</h2><a href="/trader" class="btn btn-dark">Enter</a></div>
<div class="card" style="background:#dcfce7">MTN {MTN} ({MTN_NAME})<br>Airtel {AIRTEL} ({AIRTEL_NAME})</div>
</body></html>"""

@app.get("/driver", response_class=HTMLResponse)
async def driver_get():
    html="No trucks" if not trucks else ""
    for t in trucks:
        html+=f"<div class='card'><b>{t['from_city']}→{t['to_city']}</b> {t['distance_km']} K{t['price']} <a href='/delete-truck/{t['id']}'>Delete</a></div>"
    return f"""<html><head><meta name="viewport" content="width=device-width, initial-scale=1"><style>body{{font-family:sans-serif}}.card{{border:1px solid #ddd;padding:10px;margin:8px;border-radius:10px}}input{{width:100%;padding:8px;margin:4px 0;box-sizing:border-box}}</style>
</head><body><a href="/">Home</a><h2>Driver - Auto 363km</h2>
<form action="/add-truck" method="post"><input id="f" name="from_city" placeholder="From Kitwe" required><input id="t" name="to_city" placeholder="To Lusaka" required><input id="d" name="distance_km" readonly placeholder="Auto 363km"><div id="i">Type Kitwe→Lusaka</div><input name="truck_type" placeholder="50 ton" required><input name="current_location" placeholder="Location" required><input name="departure_time" type="datetime-local" required><input name="price" placeholder="10000" required><input name="whatsapp" placeholder="0964343865" required><button type="submit">Post</button></form>
{html}
<script>const towns={{"lusaka":1,"kitwe":1,"ndola":1}};function calc(){{let f=document.getElementById('f').value.toLowerCase();let tt=document.getElementById('t').value.toLowerCase();let dd=document.getElementById('d');let ii=document.getElementById('i');if(!f||!tt)return;if((f.includes("kitwe")&&tt.includes("lusaka"))||(f.includes("lusaka")&&tt.includes("kitwe"))){{dd.value="363 km";ii.innerText="✅ 363 km driving";}}else{{dd.value="Calculated";ii.innerText="Distance calculated";}}}}document.getElementById('f').addEventListener('input',calc);document.getElementById('t').addEventListener('input',calc);</script>
</body></html>"""

@app.post("/add-truck")
async def add_truck(from_city: str = Form(...), to_city: str = Form(...), truck_type: str = Form(...), current_location: str = Form(""), departure_time: str = Form(""), price: str = Form(...), whatsapp: str = Form(...), distance_km: str = Form("")):
    if not distance_km:
        distance_km="363 km" if ("kitwe" in from_city.lower() and "lusaka" in to_city.lower()) or ("lusaka" in from_city.lower() and "kitwe" in to_city.lower()) else "Calculated"
    trucks.insert(0, {"id": str(uuid.uuid4())[:8], "from_city": from_city.strip(), "to_city": to_city.strip(), "truck_type": truck_type.strip(), "current_location": current_location.strip(), "departure_time": departure_time.strip(), "price": price.strip(), "whatsapp": whatsapp.strip(), "distance_km": distance_km.strip()})
    return RedirectResponse("/driver", status_code=303)

@app.get("/delete-truck/{tid}")
async def del_truck(tid: str):
    global trucks
    trucks=[t for t in trucks if t['id']!=tid]
    return RedirectResponse
