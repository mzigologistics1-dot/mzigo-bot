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
.bm{background:#ffeb3b;color:#000}
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
else{document.getElementById('pl').classList.remove('hidden
