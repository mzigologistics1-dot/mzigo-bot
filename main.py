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
    print("Supabase not ready:", e)

app = FastAPI()
trucks_memory = []
loads_memory = []

HTML_TOP = """
<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mzigo ZM</title><style>
*{box-sizing:border-box}body{margin:0;font-family:sans-serif;background:#f8fafc}
header{background:#0f172a;color:#fff;padding:18px;text-align:center}
.container{max-width:750px;margin:0 auto;padding:16px}
.tabs{display:flex;gap:8px;background:#e2e8f0;padding:5px;border-radius:14px;margin:16px 0}
.tab{flex:1;padding:12px;border:none;border-radius:10px;font-weight:800}
.tab.active{background:#0f172a;color:#fff}
.card{background:#fff;border-radius:16px;padding:16px;margin-bottom:12px;border:1px solid #e2e8f0}
.btn{width:100%;background:#0f172a;color:#fff;padding:14px;border:none;border-radius:12px;font-weight:800;margin-top:10px}
.btn2{background:#22c55e;color:#000}
input{width:100%;padding:12px;border-radius:10px;border:1.5px solid #e2e8f0;margin-top:8px}
.wa{display:block;margin-top:10px;background:#22c55e;color:#000;text-align:center;padding:10px;border-radius:10px;text-decoration:none;font-weight:800}
.hidden{display:none}
</style></head><body>
<header><b>MZIGO.ZM</b> - NO TRUCK RETURNS EMPTY</header>
<div class="container">
<div class="tabs">
<button class="tab active" id="t1" onclick="showTab('trucks')">Trucks (CT)</button>
<button class="tab" id="t2" onclick="showTab('loads')">Loads (CL)</button>
</div>
<div id="pt">
<h3>Post Empty Truck</h3>
<form action="/add-truck" method="post">
<input name="from_city" placeholder="From Kitwe" required>
<input name="to_city" placeholder="To Lusaka" required>
<input name="truck_type" placeholder="30 Ton" required>
<input name="whatsapp" placeholder="097..." required>
<button class="btn" type="submit">Post Truck</button>
</form>
<div style="margin-top:20px">HTRUCKS</div>
</div>
<div id="pl" class="hidden">
<h3>Post Load / Goods</h3>
<form action="/add-load" method="post">
<input name="from_city" placeholder="From Lusaka" required>
<input name="to_city" placeholder="To Ndola" required>
<input name="goods_type" placeholder="Copper, Maize" required>
<input name="weight" placeholder="20 Ton" required>
<input name="whatsapp" placeholder="097..." required>
<button class="btn btn2" type="submit">Post Load</button>
</form>
<div style="margin-top:20px">HLOADS</div>
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
    if not trucks: th = "<p>No trucks yet</p>"
    else:
        for tr in trucks:
            th += f"<div class=card><b>{tr.get('from_city','')} > {tr.get('to_city','')}</b><br>{tr.get('truck_type','')} | {tr.get('whatsapp','')}<br><a class=wa href='https://wa.me/{tr.get('whatsapp','')}' target=_blank>WhatsApp</a> <a href='/delete/truck/{tr.get('id','')}'>Delete</a></div>"
    lh = ""
    if not loads: lh = "<p>No loads yet - Post your goods!</p>"
    else:
        for ld in loads:
            lh += f"<div class=card><b>{ld.get('from_city','')} > {ld.get('to_city','')}</b><br>{ld.get('goods_type','')} {ld.get('weight','')}<br>{ld.get('whatsapp','')}<br><a class=wa href='https://wa.me/{ld.get('whatsapp','')}' target=_blank>WhatsApp</a> <a href='/delete/load/{ld.get('id','')}'>Delete</a></div>"
    page = HTML_TOP.replace("CT", str(len(trucks))).replace("CL", str(len(loads))).replace("HTRUCKS", th).replace("HLOADS", lh)
    return HTMLResponse(page)

@app.post("/add-truck")
async def add_truck(from_city: str = Form(...), to_city: str = Form(...), truck_type: str = Form(...), whatsapp: str = Form(...)):
    data = {"from_city": from_city.strip(), "to_city": to_city.strip(), "truck_type": truck_type.strip(), "whatsapp": whatsapp.strip()}
    if supabase:
        try: supabase.table("trucks").insert(data).execute()
        except Exception as e: print(e)
    else: trucks_memory.append(data)
    return RedirectResponse("/", status_code=303)

@app.post("/add-load")
async def add_load(from_city: str = Form(...), to_city: str = Form(...), goods_type: str = Form(...), weight: str = Form(...), whatsapp: str = Form(...)):
    data = {"from_city": from_city.strip(), "to_city": to_city.strip(), "goods_type": goods_type.strip(), "weight": weight.strip(), "whatsapp": whatsapp.strip()}
    if supabase:
        try: supabase.table("loads").insert(data).execute()
        except Exception as e: print(e)
    else: loads_memory.append(data)
    return RedirectResponse("/", status_code=303)

@app.get("/delete/truck/{tid}")
async def del_t(tid: str):
    if supabase:
        try: supabase.table("trucks").delete().eq("id", tid).execute()
        except: pass
    return RedirectResponse("/", status_code=303)

@app.get("/delete/load/{lid}")
async def del_l(lid: str):
    if supabase:
        try: supabase.table("loads").delete().eq("id", lid).execute()
        except: pass
    return RedirectResponse("/", status_code=303)

@app.get("/health")
async def h(): return {"ok": True}
