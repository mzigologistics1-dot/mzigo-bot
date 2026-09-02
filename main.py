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
MTN_MOMO = "0970000000"  # YOUR NUMBER
COMMISSION = 30

def calc(base_str):
    try:
        b = int(''.join(filter(str.isdigit, str(base_str))) or 0)
        fee = b * COMMISSION // 100
        total = b + fee
        return b, fee, total
    except:
        return 0, 0, base_str

HTML = """
<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mzigo ZM - Across Zambia</title>
<style>
*{box-sizing:border-box}body{margin:0;font-family:sans-serif;background:#f8fafc;color:#0f172a}
header{background:#0f172a;color:#fff;padding:22px;text-align:center}
.logo{font-weight:900;font-size:28px}.logo span{color:#22c55e}
.across{font-size:13px;letter-spacing:3px;background:#22c55e;color:#000;padding:4px 12px;border-radius:20px;font-weight:900;margin-top:8px;display:inline-block}
.container{max-width:800px;margin:0 auto;padding:14px}
.hero{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:18px 0}
@media(max-width:600px){.hero{grid-template-columns:1fr}}
.role{border-radius:20px;padding:22px;cursor:pointer}
.role-driver{background:#0f172a;color:#fff}
.role-trader{background:#fff;border:2px solid #f97316}
.role button{width:100%;padding:12px;border:none;border-radius:12px;font-weight:800;margin-top:8px}
.role-driver button{background:#22c55e}
.role-trader button{background:#0f172a;color:#fff}
.tabs{display:flex;gap:6px;background:#e2e8f0;padding:5px;border-radius:14px;margin:14px 0}
.tab{flex:1;padding:12px;border:none;border-radius:10px;font-weight:800}
.tab.active{background:#0f172a;color:#fff}
.card{background:#fff;border-radius:16px;padding:16px;margin-bottom:12px;border:1px solid #e2e8f0}
.badge{font-size:11px;padding:4px 10px;border-radius:20px;font-weight:800;display:inline-block;margin:2px}
.badge-price{background:#0f172a;color:#fff}
.badge-fee{background:#fef3c7;color:#92400e}
.route{font-weight:900;display:flex;gap:6px;flex-wrap:wrap}
.city{background:#f1f5f9;padding:4px 10px;border-radius:8px}
input{width:100%;padding:12px;border-radius:10px;border:1.5px solid #e2e8f0;margin-top:8px;background:#f8fafc}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:8px}
.btn{width:100%;background:#0f172a;color:#fff;padding:14px;border:none;border-radius:12px;font-weight:800;margin-top:10px}
.btn2{background:#f97316;color:#fff}
.wa{display:block;margin-top:12px;background:#22c55e;color:#000;text-align:center;padding:12px;border-radius:10px;text-decoration:none;font-weight:900}
.hidden{display:none}
.small{font-size:12px;color:#64748b}
.box{background:#ffeb3b;padding:10px;border-radius:10px;margin-top:8px;color:#000;font-weight:800}
</style></head><body>
<header>
<div class="logo">MZIGO<span>.ZM</span></div>
<div class="across">ACROSS ZAMBIA • FROM MWINILUNGA TO NAKONDE</div>
<div style="font-size:11px;opacity:.7;margin-top:8px">Kitwe • Lusaka • Ndola • Solwezi • Livingstone • Chipata • Kasama • Mansa</div>
</header>
<div class="container">
<div class="hero">
<div class="role role-driver" onclick="showTab('trucks')"><h2>🚛 Driver</h2><p>Empty truck ACROSS ZAMBIA? Post + your price. You get full price.</p><button>Enter →</button></div>
<div class="role role-trader" onclick="showTab('loads')"><h2>📦 Trader</h2><p>Need truck ACROSS ZAMBIA? Bot finds + GPS</p><button>Enter →</button></div>
</div>
<div class="tabs">
<button class="tab active" id="t1" onclick="showTab('trucks')">🚛 Drivers ACROSS ZM (CT)</button>
<button class="tab" id="t2" onclick="showTab('loads')">📦 Loads ACROSS ZM (CL)</button>
</div>
<div id="pt">
<div style="background:#fff;border-radius:16px;padding:16px;border:1px solid #e2e8f0">
<h3>🚛 Post Empty Truck - ACROSS ZAMBIA</h3>
<form action="/add-truck" method="post">
<div class="grid2"><input list="zm" name="from_city" placeholder="From - Kitwe, Lusaka, Mwinilunga..." required><input list="zm" name="to_city" placeholder="To - Nakonde, Solwezi, Livingstone..." required></div>
<div class="grid2"><input name="truck_type" placeholder="30 Ton" required><input name="current_location" placeholder="GPS - ShopRite"></div>
<div class="grid2"><input name="departure_time" type
