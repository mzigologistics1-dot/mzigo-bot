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
MTN = "0970000000"
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
*{box-sizing:border-box}body{margin:0;font-family:sans-serif;background:#f8fafc}
header{background:#0f172a;color:#fff;padding:18px;text-align:center;position:sticky;top:0;z-index:10}
.logo{font-size:26px;font-weight:900}.logo span{color:#22c55e}
.badge-across{background:#22c55e;color:#000;padding:4px 12px;border-radius:20px;font-weight:900;font-size:11px;display:inline-block;margin-top:6px;letter-spacing:1px}
.container{max-width:700px;margin:0 auto;padding:14px}
.card{background:#fff;border-radius:18px;padding:18px;margin-bottom:14px;border:1px solid #e2e8f0;box-shadow:0 4px 12px rgba(0,0,0,.04)}
.btn{width:100%;padding:14px;border:none;border-radius:12px;font-weight:900;margin-top:10px;cursor:pointer;display:block;text-align:center;text-decoration:none}
.btn-green{background:#22c55e;color:#000}
.btn-dark{background:#0f172a;color:#fff}
.btn-orange{background:#f97316;color:#fff}
input{width:100%;padding:12px;border-radius:10px;border:1.5px solid #e2e8f0;margin-top:8px;background:#f8fafc}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:8px}
.badge{font-size:11px;padding:4px 10px;border-radius:20px;font-weight:800;display:inline-block;margin:2px}
.bp{background:#0f172a;color:#fff}
.bf{background:#fef3c7;color:#92400e}
.wa{display:block;margin-top:10px;background:#22c55e;color:#000;text-align:center;padding:12px;border-radius:10px;text-decoration:none;font-weight:900}
.back{display:inline-block;margin-bottom:12px;background:#e2e8f0;padding:8px 14px;border-radius:20px;text-decoration:none;color:#000;font-weight:800;font-size:12px}
.small{font-size:12px;color:#64748b;margin-top:6px}
</style>
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    html = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Mzigo - Across Zambia</title>{STYLE}</head><body>
<header>
<div class="logo">MZIGO<span>.ZM</span></div>
<div class="badge-across">ACROSS ZAMBIA • MWINILUNGA TO NAKONDE</div>
</header>
<div class="container">
<h2 style="text-align:center;margin:20px 0 6px">Choose Your Role</h2>
<p style="text-align:center" class="small">Separate screens - Driver & Trader connected</p>

<div class="card" style="background:#0f172a;color:#fff">
<h2 style="margin:0">🚛 I'm a Driver</h2>
<p style="opacity:.8">Empty ACROSS ZAMBIA? Post your truck, set your price K15,000, you get full K15,000. Bot adds 30% for trader.</p>
<a href="/driver" class="btn btn-green">Enter as Driver → Post Truck</a>
</div>

<div class="card" style="border:2px solid #f97316">
<h2 style="margin:0">📦 I'm a Trader / Wholesaler</h2>
<p class="small">Need truck ACROSS ZAMBIA? Bot finds empty truck, GPS tracking, payment via MTN MoMo.</p>
<a href="/trader" class="btn btn-dark">Enter as Trader → Post Load</a>
</div>

<div class="card" style="background:#fff8ed;text-align:center">
<b>FIXED 30% Commission ACROSS ZAMBIA</b><br>
<span class="small">Driver: K15,000 → Trader Pays: K19,500 → You keep K4,500</span><br>
<span class="small">No bypass - Bot handles payment</span>
</div>
</div></body></html>"""
    return HTMLResponse(html)

@app.get("/driver", response_class=HTMLResponse)
async def driver_screen():
    trucks = []
    if supabase:
        try:
            trucks = supabase.table("trucks").select("*").order("created_at", desc=True).execute().data
        except:
            trucks = trucks_memory
    else:
        trucks = trucks_memory
    
    th = '<div class="card">No trucks yet ACROSS ZAMBIA - Be first driver!</div>' if not trucks else ""
    for tr in trucks:
        b, fee, total = calc(tr.get("price","0"))
        from_c = tr.get("from_city","")
        to_c = tr.get("to_city","")
        loc = tr.get("current_location","")
        tm = str(tr.get("departure_time",""))[:16]
        th += f'<div class="card"><b>{from_c} → {to_c}</b> <span class="badge" style="background:#22c55e">ACROSS ZAMBIA</span><br><span class="badge bp">You get K{b}</span><span class="badge bf">Trader pays K{total} (30% K{fee})</span><br><div class="small">📍 {loc} | 🕒 {tm}</div><div style="background:#ffeb3b;padding:8px;border-radius:8px;margin-top:6px;font-weight:800">MTN MoMo → {MTN} | Profit K{fee}</div><a class="wa" href="https://wa.me/260970000000?text=Truck{tr.get("id","")}" target="_blank">Contact via Bot</a></div>'

    html = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Driver - Mzigo</title>{STYLE}</head><body>
<header><div class="logo">MZIGO<span>.ZM</span> DRIVER</div><div class="badge-across">ACROSS ZAMBIA • DRIVER SCREEN ONLY</div></header>
<div class="container">
<a href="/" class="back">← Back Home</a> <a href="/trader" class="back" style="float:right">Go to Trader →</a>
<div class="card" style="background:#0f172a;color:#fff">
<h3 style="margin:0">🚛 Post Empty Truck - Driver Only Screen</h3>
<p style="opacity:.7;font-size:12px">This screen ONLY shows Post Truck - as you asked!</p>
<form action="/add-truck" method="post">
<div class="grid2">
<input name="from_city" placeholder="From - Kitwe, Mwinilunga" required>
<input name="to_city" placeholder="To - Nakonde, Lusaka" required>
</div>
<div class="grid2">
<input name="truck_type" placeholder="30 Ton" required>
<input name="current_location" placeholder="GPS - ShopRite">
</div>
<div class="grid2">
<input name="departure_time" type="datetime-local" required>
<input name="price" placeholder="Your Price K - 15000" required>
</div>
<input name="whatsapp" placeholder="Your WhatsApp 097..." required>
<button class="btn btn-green" type="submit">Post Truck ACROSS ZAMBIA</button>
</form>
</div>
<h3>🚛 Trucks ACROSS ZAMBIA ({len(trucks)})</h3>
{th}
</div></body></html>"""
    return HTMLResponse(html)

@app.get("/trader", response_class=HTMLResponse)
async def trader_screen():
    loads = []
    if supabase:
        try:
            loads = supabase.table("loads").select("*").order("created_at", desc=True).execute().data
        except:
            loads = loads_memory
    else:
        loads = loads_memory
    
    lh = '<div class="card">No loads yet ACROSS ZAMBIA - Traders waiting!</div>' if not loads else ""
    for ld in loads:
        from_c = ld.get("from_city","")
        to_c = ld.get("to_city","")
        goods = ld.get("goods_type","")
        w = ld.get("weight","")
        pr = ld.get("price","")
        lh += f'<div class="card"><b>{from_c} → {to_c}</b> ACROSS ZAMBIA<br><span class="badge">{goods} {w}</span> <span class="badge bp">K{pr}</span><br><a class="wa" style="background:#0f172a;color:#fff" href="https://wa.me/260970000000?text=Load{ld.get("id","")}" target="_blank">I Have Truck - Contact Bot</a></div>'

    html = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Trader - Mzigo</title>{STYLE}</head><body>
<header><div class="logo">MZIGO<span>.ZM</span> TRADER</div><div class="badge-across">ACROSS ZAMBIA • TRADER SCREEN ONLY</div></header>
<div class="container">
<a href="/" class="back">← Back Home</a> <a href="/driver" class="back" style="float:right">Go to Driver →</a>
<div class="card" style="border:2px solid #f97316">
<h3 style="margin:0">📦 Post Load - Trader Only Screen</h3>
<p class="small">This screen ONLY shows Post Load - as you asked!</p>
<form action="/add-load" method="post">
<div class="grid2">
<input name="from_city" placeholder="From - Mwinilunga" required>
<input name="to_city" placeholder="To - Nakonde" required>
</div>
<div class="grid2">
<input name="goods_type" placeholder="15 Tons Maize" required>
<input name="weight" placeholder="15 Tons" required>
</div>
<div class="grid2">
<input name="distance_km" placeholder="Distance km">
<input name="departure_time" type="datetime-local" required>
</div>
<input name="price" placeholder="Budget K - 19500" required>
<input name="whatsapp" placeholder="Your WhatsApp 097..." required>
<button class="btn btn-orange" type="submit">Post Load ACROSS ZAMBIA</button>
</form>
</div>
<h3>📦 Loads ACROSS ZAMBIA ({len(loads)})</h3>
{lh}
</div></body></html>"""
    return HTMLResponse(html)

@app.post("/add-truck")
async def add_truck(from_city: str = Form(...), to_city: str = Form(...), truck_type: str = Form(...), current_location: str = Form(""), departure_time: str = Form(""), price: str = Form(...), whatsapp: str = Form(...)):
    data = {"from_city": from_city.strip(), "to_city": to_city.strip(), "truck_type": truck_type.strip(), "current_location": current_location.strip(), "departure_time": departure_time.strip(), "price": price.strip(), "whatsapp": whatsapp.strip()}
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
    return {"ok": True, "across": "Zambia", "commission": "30%", "screens": "separate"}
