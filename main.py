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
    print(e)

app = FastAPI()
trucks_memory = []
loads_memory = []

# === YOUR MTN MONEY NUMBER - CHANGE THIS ===
MTN_MOMO_NUMBER = "0964343865"  # Put your MTN number here
AIRTEL_MONEY_NUMBER = "0976166422"  # Put your Airtel number here

def get_commission_pct(from_c, to_c, price_str):
    combo = (from_c + " " + to_c).lower()
    if "mwinilunga" in combo or "mwilunga" in combo or "nakonde" in combo or "tanzania" in combo or "mwinilunga" in combo:
        return 35
    try:
        digits = int(''.join(filter(str.isdigit, str(price_str)))) if price_str else 0
        if digits < 5000:
            return 20
        elif digits <= 15000:
            return 25
        else:
            return 20
    except:
        return 25

def calc_prices(driver_price_str, from_c, to_c):
    try:
        clean = ''.join(filter(str.isdigit, str(driver_price_str)))
        base = int(clean) if clean else 0
        pct = get_commission_pct(from_c, to_c, driver_price_str)
        fee = base * pct // 100
        total = base + fee
        return base, pct, fee, total
    except:
        return 0, 25, 0, driver_price_str

HTML = """
<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mzigo ZM - Bot Marketplace</title>
<style>
*{box-sizing:border-box}body{margin:0;font-family:system-ui,sans-serif;background:#f8fafc;color:#0f172a}
header{background:#0f172a;color:#fff;padding:20px;text-align:center}
.logo{font-weight:900;font-size:24px;letter-spacing:1px}.logo span{color:#22c55e}
.container{max-width:800px;margin:0 auto;padding:14px}
.hero{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:18px 0}
@media(max-width:600px){.hero{grid-template-columns:1fr}}
.role{border-radius:20px;padding:22px;cursor:pointer;border:2px solid transparent;transition:.2s}
.role-driver{background:#0f172a;color:#fff}
.role-trader{background:#fff;border-color:#f97316;color:#0f172a;box-shadow:0 8px 30px rgba(0,0,0,.06)}
.role h2{margin:0 0 6px;font-size:20px}
.role p{margin:0 0 12px;opacity:.8;font-size:14px}
.role button{width:100%;padding:12px;border:none;border-radius:12px;font-weight:800;cursor:pointer}
.role-driver button{background:#22c55e;color:#000}
.role-trader button{background:#0f172a;color:#fff}
.tabs{display:flex;gap:6px;background:#e2e8f0;padding:5px;border-radius:14px;margin:14px 0}
.tab{flex:1;padding:12px;border:none;border-radius:10px;font-weight:800;background:transparent}
.tab.active{background:#0f172a;color:#fff}
.card{background:#fff;border-radius:16px;padding:16px;margin-bottom:12px;border:1px solid #e2e8f0;position:relative;overflow:hidden}
.card.trader{border-color:#fed7aa}
.badge{font-size:11px;padding:4px 10px;border-radius:20px;font-weight:800;display:inline-block;margin:2px}
.badge-bot{background:#fef3c7;color:#92400e}
.badge-remote{background:#fee2e2;color:#991b1b}
.badge-time{background:#dbeafe;color:#1e40af}
.badge-gps{background:#dcfce7;color:#14532d}
.badge-price{background:#0f172a;color:#fff}
.route{font-weight:900;font-size:16px;display:flex;gap:6px;flex-wrap:wrap;align-items:center}
.city{background:#f1f5f9;padding:4px 10px;border-radius:8px}
.meta{margin-top:10px;display:flex;flex-wrap:wrap;gap:6px}
input,select{width:100%;padding:12px;border-radius:10px;border:1.5px solid #e2e8f0;margin-top:8px;background:#f8fafc;font-size:14px}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:8px}
@media(max-width:500px){.grid2{grid-template-columns:1fr}}
.btn{width:100%;background:#0f172a;color:#fff;padding:14px;border:none;border-radius:12px;font-weight:800;margin-top:10px;cursor:pointer}
.btn2{background:#f97316;color:#fff}
.wa{display:block;margin-top:12px;background:#22c55e;color:#000;text-align:center;padding:12px;border-radius:10px;text-decoration:none;font-weight:900}
.wa2{background:#0f172a;color:#fff}
.hidden{display:none}
.small{font-size:12px;color:#64748b;margin-top:6px}
.price-box{background:#f8fafc;border:1px dashed #cbd5e1;border-radius:10px;padding:10px;margin-top:8px;font-size:13px}
</style></head><body>
<header><div class="logo">MZIGO<span>.ZM</span></div><div style="font-size:11px;letter-spacing:2px;opacity:.6;margin-top:4px">BOT MATCHES • WE HANDLE PAYMENT • NO BYPASS</div></header>
<div class="container">

<div class="hero">
<div class="role role-driver" onclick="showTab('trucks')">
<h2>🚛 I'm a Driver</h2>
<p>Empty from Mwinilunga to Nakonde? Post truck + your price. Bot finds trader, handles cash.</p>
<button>Enter as Driver →</button>
<div class="small" style="color:#22c55e;margin-top:8px">You set price: K15,000 → You get K15,000</div>
</div>
<div class="role role-trader" onclick="showTab('loads')">
<h2>📦 I'm a Trader</h2>
<p>Need 15 tons maize Mwinilunga → Border? Bot tracks truck at ShopRite, payment secured.</p>
<button>Enter as Trader →</button>
<div class="small">GPS + Escrow + No empty trucks</div>
</div>
</div>

<div class="tabs">
<button class="tab active" id="t1" onclick="showTab('trucks')">🚛 Drivers (CT)</button>
<button class="tab" id="t2" onclick="showTab('loads')">📦 Traders (CL)</button>
</div>

<div id="pt">
<div style="background:#fff;border-radius:16px;padding:16px;border:1px solid #e2e8f0">
<h3 style="margin:0">🚛 Post Empty Truck</h3>
<p class="small">You set your price. Bot adds commission and talks to trader. You get full price.</p>
<form action="/add-truck" method="post">
<div class="grid2">
<input name="from_city" placeholder="From - Mwinilunga" required>
<input name="to_city" placeholder="To - Nakonde / Tanzania Border" required>
</div>
<div class="grid2">
<input name="truck_type" placeholder="30 Ton, Horse" required>
<input name="current_location" placeholder="Current GPS - Parked at ShopRite Solwezi">
</div>
<div class="grid2">
<input name="departure_time" type="datetime-local" required>
<input name="price" placeholder="Your Price K - 15000" required>
</div>
<input name="whatsapp" placeholder="Your WhatsApp 097..." required>
<button class="btn" type="submit">Post via Mzigo Bot → Earn Full Price</button>
</form>
</div>
<div style="margin-top:16px">HTRUCKS</div>
</div>

<div id="pl" class="hidden">
<div style="background:#fff;border-radius:16px;padding:16px;border:1.5px solid #f97316">
<h3 style="margin:0">📦 Post Load - Traders / Wholesalers</h3>
<p class="small">Bot finds truck, tracks GPS, holds payment until delivery.</p>
<form action="/add-load" method="post">
<div class="grid2">
<input name="from_city" placeholder="From - Mwinilunga" required>
<input name="to_city" placeholder="To - Nakonde Border" required>
</div>
<div class="grid2">
<input name="goods_type" placeholder="15 Tons Maize / Copper" required>
<input name="weight" placeholder="15 Tons" required>
</div>
<div class="grid2">
<input name="distance_km" placeholder="Distance km - 1200">
<input name="departure_time" type="datetime-local" required>
</div>
<input name="price" placeholder="Your Budget K - 20250" required>
<input name="whatsapp" placeholder="Your WhatsApp 097..." required>
<button class="btn btn2" type="submit">Post Load via Bot → Get Truck</button>
</form>
</div>
<div style="margin-top:16px">HLOADS</div>
</div>

<div style="margin-top:24px;background:#0f172a;color:#fff;border-radius:16px;padding:16px">
<b>How Mzigo Bot Works (No Bypass):</b>
<div class="small" style="color:#94a3b8;margin-top:6px">
1. Driver posts K15,000 Mwinilunga→Nakonde • 2. Bot adds 35% remote fee = K20,250 for trader • 3. Trader pays Mzigo (MTN Money) • 4. Driver delivers, we pay driver K15,000 • 5. We keep K5,250 profit. No direct contact!
</div>
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
localStorage.setItem('mzigo_tab',n);
window.scrollTo({top:400,behavior:'smooth'});
}
var s=localStorage.getItem('mzigo_tab');if(s)showTab(s);
</script></body></html>
"""

def get_trucks():
    if supabase:
        try: return supabase.table("trucks").select("*").order("created_at", desc=True).execute().data
        except: return trucks_memory
    return trucks_memory

def get_loads():
    if supabase:
        try: return supabase.table("loads").select("*").order("created_at", desc=True).execute().data
        except: return loads_memory
    return loads_memory

@app.get("/", response_class=HTMLResponse)
async def home():
    trucks = get_trucks()
    loads = get_loads()
    th = ""
    if not trucks:
        th = '<div class="card">No trucks yet. Be first from Mwinilunga!</div>'
    else:
        for tr in trucks:
            base, pct, fee, total = calc_prices(tr.get('price','0'), tr.get('from_city',''), tr.get('to_city',''))
            remote = pct==35
            badge_remote = '<span class="badge badge-remote">REMOTE 35% - Mwinilunga/Nakonde</span>' if remote else f'<span class="badge badge-bot">BOT FEE {pct}% = K{fee}</span>'
            th += f"""<div class="card">
<div class="route"><span class="city">{tr.get('from_city','')}</span> → <span class="city">{tr.get('to_city','')}</span></div>
<div class="meta">
<span class="badge badge-price">Driver: K{base}</span>
{badge_remote}
<span class="badge badge-price">Trader Pays: K{total}</span>
<span class="badge badge-gps">📍 {tr.get('current_location','No GPS')}</span>
<span class="badge badge-time">🕒 {str(tr.get('departure_time',''))[:16]}</span>
</div>
<div class="price-box" style="background:#f8fafc;border:1px dashed #cbd5e1;border-radius:10px;padding:10px;margin-top:8px;font-size:13px">
Driver gets: <b>K{base}</b> | Mzigo fee {pct}%: <b>K{fee}</b> | Trader total: <b>K{total}</b><br>
<span class="small">Profit for you: K{fee} - Bot prevents bypass</span><br>
<div style="margin-top:8px;background:#ffeb3b;padding:8px;border-radius:8px;color:#000;font-weight:800">
💰 MTN MoMo: K{total} → {MTN_MOMO_NUMBER} | Dial *303#<br>
<span style="font-size:11px">Trader pays YOU, you pay driver K{base}</span>
</div>
</div>
<div class="small">{tr.get('truck_type','')} | {tr.get('whatsapp','')}</div>
<a class="wa" href="https://wa.me/260970000000?text=Hi%20Mzigo%20Bot%20-%20Match%20Truck%20{tr.get('id','')}%20K{total}" target="_blank">Contact via Mzigo Bot - Pay via MoMo</a>
</div>"""
    lh = ""
    if not loads:
        lh = '<div class="card trader">No loads yet. Traders waiting for Mwinilunga trucks!</div>'
    else:
        for ld in loads:
            lh += f"""<div class="card trader">
<div class="route"><span class="city">{ld.get('from_city','')}</span> → <span class="city">{ld.get('to_city','')}</span></div>
<div class="meta">
<span class="badge" style="background:#ffedd5;color:#9a3412">{ld.get('goods_type','')} - {ld.get('weight','')}</span>
<span class="badge badge-price">Budget K{ld.get('price','')}</span>
<span class="badge badge-time">🕒 {str(ld.get('departure_time',''))[:16]}</span>
<span class="badge badge-gps">📏 {ld.get('distance_km','')} km</span>
</div>
<a class="wa wa2" href="https://wa.me/260970000000?text=Hi%20Mzigo%20Bot%20-%20I%20have%20truck%20for%20Load%20{ld.get('id','')}" target="_blank">I Have Truck - Contact via Bot</a>
</div>"""
    page = HTML.replace("CT", str(len(trucks))).replace("CL", str(len(loads))).replace("HTRUCKS", th).replace("HLOADS", lh)
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
async def h(): return {"ok": True}
