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
MTN = "0970000000"  # CHANGE TO YOUR NUMBER
PCT = 30

def calc(s):
    try:
        digits = "".join([c for c in str(s) if c.isdigit()])
        b = int(digits) if digits else 0
        fee = b * PCT // 100
        total = b + fee
        return b, fee, total
    except:
        return 0, 0, s

HTML_BASE = """
<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mzigo ZM - Across Zambia</title>
<style>
*{box-sizing:border-box}body{margin:0;font-family:sans-serif;background:#f8fafc}
header{background:#0f172a;color:#fff;padding:22px;text-align:center}
.logo{font-size:28px;font-weight:900}.logo span{color:#22c55e}
.badge-across{background:#22c55e;color:#000;padding:4px 14px;border-radius:20px;font-weight:900;font-size:12px;display:inline-block;margin-top:8px;letter-spacing:2px}
.container{max-width:800px;margin:0 auto;padding:14px}
.hero{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:16px 0}
@media(max-width:600px){.hero{grid-template-columns:1fr}}
.role{border-radius:20px;padding:20px;cursor:pointer}
.driver{background:#0f172a;color:#fff}
.trader{background:#fff;border:2px solid #f97316}
.role button{width:100%;padding:12px;border:none;border-radius:12px;font-weight:800;margin-top:8px}
.driver button{background:#22c55e}
.trader button{background:#0f172a;color:#fff}
.tabs{display:flex;gap:6px;background:#e2e8f0;padding:5px;border-radius:14px;margin:14px 0}
.tab{flex:1;padding:12px;border:none;border-radius:10px;font-weight:800}
.tab.active{background:#0f172a;color:#fff}
.card{background:#fff;border-radius:16px;padding:16px;margin-bottom:12px;border:1px solid #e2e8f0}
.badge{font-size:11px;padding:4px 10px;border-radius:20px;font-weight:800;display:inline-block;margin:2px}
.bp{background:#0f172a;color:#fff}
.bf{background:#fef3c7;color:#92400e}
input{width:100%;padding:12px;border-radius:10px;border:1.5px solid #e2e8f0;margin-top:8px}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:8px}
.btn{width:100%;background:#0f172a;color:#fff;padding:14px;border:none;border-radius:12px;font-weight:800;margin-top:10px}
.btn2{background:#f97316;color:#fff}
.wa{display:block;margin-top:10px;background:#22c55e;color:#000;text-align:center;padding:12px;border-radius:10px;text-decoration:none;font-weight:900}
.hidden{display:none}
.small{font-size:12px;color:#64748b}
</style></head><body>
<header>
<div class="logo">MZIGO<span>.ZM</span></div>
<div class="badge-across">ACROSS ZAMBIA • MWINILUNGA TO NAKONDE • KITWE TO LIVINGSTONE</div>
<div style="font-size:10px;opacity:.6;margin-top:6px">Kitwe • Lusaka • Ndola • Solwezi • Chipata • Kasama • Mansa • Kabwe</div>
</header>
<div class="container">
<div class="hero">
<div class="role driver" onclick="showTab('trucks')"><h2>🚛 Driver</h2><p>Empty ACROSS ZAMBIA? Post price, get full.</p><button>Enter →</button></div>
<div class="role trader" onclick="showTab('loads')"><h2>📦 Trader</h2><p>Need truck ACROSS ZAMBIA? Bot + GPS.</p><button>Enter →</button></div>
</div>
<div class="tabs">
<button class="tab active" id="t1" onclick="showTab('trucks')">🚛 Drivers (CT)</button>
<button class="tab" id="t2" onclick="showTab('loads')">📦 Loads (CL)</button>
</div>
<div id="pt">
<div style="background:#fff;border-radius:16px;padding:16px;border:1px solid #e2e8f0">
<h3>🚛 Post Truck - ACROSS ZAMBIA</h3>
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
<input name="whatsapp" placeholder="WhatsApp 097..." required>
<button class="btn" type="submit">Post ACROSS ZAMBIA</button>
</form>
</div>
<div style="margin-top:16px">HTRUCKS</div>
</div>
<div id="pl" class="hidden">
<div style="background:#fff;border-radius:16px;padding:16px;border:1.5px solid #f97316">
<h3>📦 Post Load - ACROSS ZAMBIA</h3>
<form action="/add-load" method="post">
<div class="grid2">
<input name="from_city" placeholder="From - Across Zambia" required>
<input name="to_city" placeholder="To - Across Zambia" required>
</div>
<div class="grid2">
<input name="goods_type" placeholder="Maize / Copper" required>
<input name="weight" placeholder="15 Tons" required>
</div>
<div class="grid2">
<input name="distance_km" placeholder="Distance km">
<input name="departure_time" type="datetime-local" required>
</div>
<input name="price" placeholder="Budget K" required>
<input name="whatsapp" placeholder="WhatsApp 097..." required>
<button class="btn btn2" type="submit">Post Load ACROSS ZAMBIA</button>
</form>
</div>
<div style="margin-top:16px">HLOADS</div>
</div>
</div>
<script>
function showTab(n){
document.getElementById('pt').classList.add('hidden');
document.getElementById('pl').classList.add('hidden');
document.getElementById('t1').classList.remove('active');
document.getElementById('t2').classList.remove('active');
if(n=='trucks'){document.getElementById('pt').classList.remove('hidden');document.getElementById('t1').classList.add('active');}
else{document.getElementById('pl').classList.remove('hidden');document.getElementById('t2').classList.add('active');}
localStorage.setItem('tab',n);
}
var s=localStorage.getItem('tab');if(s)showTab(s);
</script></body></html>
"""

def get_trucks():
    if supabase:
        try:
            return supabase.table("trucks").select("*").order("created_at", desc=True).execute().data
        except:
            return trucks_memory
    return trucks_memory

def get_loads():
    if supabase:
        try:
            return supabase.table("loads").select("*").order("created_at", desc=True).execute().data
        except:
            return loads_memory
    return loads_memory

@app.get("/", response_class=HTMLResponse)
async def home():
    trucks = get_trucks()
    loads = get_loads()
    t_html = ""
    if not trucks:
        t_html = '<div class="card">No trucks yet ACROSS ZAMBIA - Be first!</div>'
    else:
        for tr in trucks:
            b, fee, total = calc(tr.get("price", "0"))
            from_c = tr.get("from_city", "")
            to_c = tr.get("to_city", "")
            loc = tr.get("current_location", "")
            tm = str(tr.get("departure_time", ""))[:16]
            typ = tr.get("truck_type", "")
            tid = tr.get("id", "")
            t_html += f'<div class="card"><b>{from_c} → {to_c}</b> <span class="badge" style="background:#22c55e;color:#000">ACROSS ZAMBIA</span><br><span class="badge bp">Driver K{b}</span><span class="badge bf">30% K{fee}</span><span class="badge bp">Pays K{total}</span><br><div class="small">📍 {loc} | 🕒 {tm} | {typ}</div><div style="background:#ffeb3b;padding:8px;border-radius:8px;margin-top:8px;font-weight:800">💰 MTN MoMo K{total} → {MTN} | You keep K{fee}</div><a class="wa" href="https://wa.me/260970000000?text=Truck{tid}K{total}" target="_blank">Contact via Bot</a></div>'
    l_html = ""
    if not loads:
        l_html = '<div class="card">No loads ACROSS ZAMBIA yet</div>'
    else:
        for ld in loads:
            from_c = ld.get("from_city", "")
            to_c = ld.get("to_city", "")
            goods = ld.get("goods_type", "")
            w = ld.get("weight", "")
            lid = ld.get("id", "")
            pr = ld.get("price", "")
            l_html += f'<div class="card"><b>{from_c} → {to_c}</b><br><span class="badge">{goods} {w}</span><span class="badge bp">K{pr}</span><br><a class="wa" style="background:#0f172a;color:#fff" href="https://wa.me/260970000000?text=Load{lid}" target="_blank">I Have Truck - ACROSS ZAMBIA</a></div>'
    page = HTML_BASE.replace("CT", str(len(trucks))).replace("CL", str(len(loads))).replace("HTRUCKS", t_html).replace("HLOADS", l_html)
    return HTMLResponse(page)

@app.post("/add-truck")
async def add_truck(from_city: str = Form(...), to_city: str = Form(...), truck_type: str = Form(...), current_location: str = Form(""), departure_time: str = Form(""), price: str = Form(...), whatsapp: str = Form(...)):
    data = {"from_city": from_city.strip(), "to_city": to_city.strip(), "truck_type": truck_type.strip(), "current_location": current_location.strip(), "departure_time": departure_time.strip(), "price": price.strip(), "whatsapp": whatsapp.strip()}
    if supabase:
        try: supabase.table("trucks").insert(data).execute()
        except Exception as e: print(e)
    else: trucks_memory.append(data)
    return RedirectResponse("/", status_code=303)

@app.post("/add-load")
async def add_load(from_city: str = Form(...), to_city: str = Form(...), goods_type: str = Form(...), weight: str = Form(...), distance_km: str = Form(""), departure_time: str = Form(""), price: str = Form(...), whatsapp: str = Form(...)):
    data = {"from_city": from_city.strip(), "to_city": to_city.strip(), "goods_type": goods_type.strip(), "weight": weight.strip(), "distance_km": distance_km.strip(), "departure_time": departure_time.strip(), "price": price.strip(), "whatsapp": whatsapp.strip()}
    if supabase:
        try: supabase.table("loads").insert(data).execute()
        except Exception as e: print(e)
    else: loads_memory.append(data)
    return RedirectResponse("/", status_code=303)

@app.get("/health")
async def health():
    return {"ok": True, "across": "Zambia", "commission": "30%"}
