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

PAGE = '''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mzigo ZM - Marketplace</title>
<style>
*{box-sizing:border-box}body{margin:0;font-family:sans-serif;background:#f8fafc;color:#0f172a}
header{background:#0f172a;color:#fff;padding:18px 16px;position:sticky;top:0;z-index:10}
.header-inner{max-width:750px;margin:0 auto;display:flex;justify-content:space-between;align-items:center}
.logo{font-weight:900;font-size:20px}.logo span{color:#22c55e}
.live{font-size:11px;background:#22c55e;color:#000;padding:4px 10px;border-radius:20px;font-weight:800}
.container{max-width:750px;margin:0 auto;padding:16px}
.tabs{display:flex;gap:8px;margin:16px 0;background:#e2e8f0;padding:5px;border-radius:14px}
.tab{flex:1;padding:12px;text-align:center;border-radius:10px;font-weight:800;cursor:pointer;border:none;background:transparent}
.tab.active{background:#0f172a;color:#fff}
.post-card{background:#fff;border-radius:20px;padding:20px;box-shadow:0 8px 30px rgba(0,0,0,.06);border:1px solid #e2e8f0;margin-bottom:16px}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:10px}
@media(max-width:500px){.grid2{grid-template-columns:1fr}}
input{width:100%;padding:14px;border-radius:12px;border:1.5px solid #e2e8f0;font-size:15px;background:#f8fafc}
.btn{width:100%;background:#0f172a;color:#fff;padding:15px;border:none;border-radius:12px;font-weight:800;margin-top:12px;cursor:pointer}
.btn-green{background:#22c55e;color:#000}
.count{background:#0f172a;color:#fff;padding:4px 10px;border-radius:20px;font-size:12px;font-weight:800}
.card{background:#fff;border-radius:18px;padding:16px;margin-bottom:12px;border:1px solid #e2e8f0;overflow:hidden;position:relative}
.route{display:flex;align-items:center;flex-wrap:wrap;gap:6px;font-weight:900;font-size:16px;padding-right:30px}
.route .city{background:#f1f5f9;padding:4px 10px;border-radius:8px;max-width:100%;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.meta{margin-top:12px;display:flex;flex-wrap:wrap;gap:8px}
.tag{padding:6px 12px;border-radius:20px;font-size:12.5px;border:1px solid #e2e8f0;background:#f8fafc;max-width:100%}
.tag.green{background:#dcfce7;color:#14532d}
.tag.dark{background:#0f172a;color:#fff}
.tag.orange{background:#ffedd5;color:#9a3412}
.wa{display:block;margin-top:14px;background:#22c55e;color:#000;text-align:center;padding:12px;border-radius:12px;text-decoration:none;font-weight:900}
.wa-blue{background:#0ea5e9;color:#fff}
.del{position:absolute;top:10px;right:10px;background:#fee2e2;color:#dc2626;width:28px;height:28px;border-radius:50%;display:flex;align-items:center;justify-content:center;text-decoration:none;font-weight:900;font-size:16px;border:1px solid #fecaca}
.time{font-size:11px;color:#94a3b8;margin-top:10px}
.empty{background:#fff;border-radius:20px;padding:36px 20px;text-align:center;border:1.5px dashed #cbd5e1;color:#64748b}
.section{margin:20px 0 12px;display:flex;justify-content:space-between;align-items:center}
.hidden{display:none}
</style></head><body>
<header><div class="header-inner"><div><div class="logo">MZIGO<span>.ZM</span></div><div style="font-size:11px;letter-spacing:2px;opacity:.6;margin-top:2px">NO TRUCK RETURNS EMPTY</div></div><div class="live">LIVE</div></div></header>
<div class="container">
<div class="tabs">
<button class="tab active" onclick="showTab('trucks')" id="tab-trucks">🚛 Trucks (COUNT_TRUCK)</button>
<button class="tab" onclick="showTab('loads')" id="tab-loads">📦 Loads (COUNT_LOAD)</button>
</div>

<div id="panel-trucks">
<div class="post-card"><h3>🚛 Post Your Empty Truck</h3><p>Find back-load - Don't return empty!</p>
<form action="/add-truck" method="post">
<div class="grid2"><input name="from_city" placeholder="From - Kitwe" required><input name="to_city" placeholder="To - Lusaka" required></div>
<div class="grid2" style="margin-top:10px"><input name="truck_type" placeholder="30 Ton, Semi" required><input name="whatsapp" placeholder="WhatsApp 097..." required></div>
<button class="btn" type="submit">Post Truck → Find Loads</button>
</form></div>
<div class="section"><h3>Available Trucks</h3><div class="count">COUNT_TRUCK trucks</div></div>
TRUCKS_HTML
</div>

<div id="panel-loads" class="hidden">
<div class="post-card" style="border:1.5px solid #f97316"><h3>📦 Post Your Load / Goods</h3><p>Need a truck? Post your goods!</p>
<form action="/add-load" method="post">
<div class="grid2"><input name="from_city" placeholder="From - Lusaka" required><input name="to_city" placeholder="To - Ndola" required></div>
<div class="grid2" style="margin-top:10px"><input name="goods_type" placeholder="Copper, Maize, Cement" required><input name="weight" placeholder="20 Ton" required></div>
<input name="whatsapp" placeholder="WhatsApp 097..." required style="margin-top:10px">
<button class="btn btn-green" type="submit">Post Load → Find Trucks</button>
</form></div>
<div class="section"><h3>Available Loads</h3><div class="count" style="background:#f97316">COUNT_LOAD loads</div></div>
LOADS_HTML
</div>

</div>
<script>
function showTab(name){
document.getElementById('panel-trucks').classList.add('hidden');
document.getElementById('panel-loads').classList.add('hidden');
document.getElementById('tab-trucks').classList.remove('active');
document.getElementById('tab-loads').classList.remove('active');
document.getElementById('panel-'+name).classList.remove('hidden');
document.getElementById('tab-'+name).classList.add('active');
localStorage.setItem('mzigo_tab', name);
}
var saved = localStorage.getItem('mzigo_tab');
if(saved){ showTab(saved); }
</script>
</body></html>'''

def get_trucks():
    if supabase:
        try:
            return supabase.table("trucks").select("*").order("created_at", desc=True).execute().data
        except: return trucks_memory
    return trucks_memory

def get_loads():
    if supabase:
        try:
            return supabase.table("loads").select("*").order("created_at", desc=True).execute().data
        except: return loads_memory
    return loads_memory

@app.get("/", response_class=HTMLResponse)
async def home():
    trucks = get_trucks()
    loads = get_loads()
    if not trucks:
        trucks_html = '<div class="empty">No trucks yet. Be first!</div>'
    else:
        out=""
        for tr in trucks:
            tid=str(tr.get('id',''))
            wa=str(tr.get('whatsapp','')).strip()
            dig=''.join(filter(str.isdigit, wa))[-10:]
            link=f"https://wa.me/260{dig}" if len(dig)>=9 else f"https://wa.me/{wa}"
            out+=f'<div class="card"><a class="del" href="/delete/truck/{tid}" onclick="return confirm(\\'Delete?\\')">x</a><div class="route"><span class="city">{tr.get("from_city","")}</span> > <span class="city">{tr.get("to_city","")}</span></div><div class="meta"><span class="tag dark">{tr.get("truck_type","")}</span><span class="tag green">{tr.get("whatsapp","")}</span></div><a class="wa" href="{link}" target="_blank">WhatsApp Driver</a><div class="time">{str(tr.get("created_at",""))[:19]}</div></div>'
        trucks_html=out
    if not loads:
        loads_html = '<div class="empty">No loads yet. Post your goods - truckers are waiting!</div>'
    else:
        out=""
        for ld in loads:
            lid=str(ld.get('id',''))
            wa=str(ld.get('whatsapp','')).strip()
            dig=''.join(filter(str.isdigit, wa))[-10:]
            link=f"https://wa.me/260{dig}" if len(dig)>=9 else f"https://wa.me/{wa}"
            out+=f'<div class="card" style="border-color:#fed7aa"><a class="del" href="/delete/load/{lid}" onclick="return confirm(\\'Delete?\\')">x</a><div class="route"><span class="city">{ld.get("from_city","")}</span> > <span class="city">{ld.get("to_city","")}</span></div><div class="meta"><span class="tag orange">{ld.get("goods_type","")} - {ld.get("weight","")}</span><span class="tag green">{ld.get("whatsapp","")}</span></div><a class="wa wa-blue" href="{link}" target="_blank">I Have Truck - WhatsApp</a><div class="time">{str(ld.get("created_at",""))[:19]}</div></div>'
        loads_html=out
    page = PAGE.replace("COUNT_TRUCK", str(len(trucks))).replace("COUNT_LOAD", str(len(loads))).replace("TRUCKS_HTML", trucks_html).replace("LOADS_HTML", loads_html)
    return HTMLResponse(page)

@app.post("/add-truck")
async def add_truck(from_city: str = Form(...), to_city: str = Form(...), truck_type: str = Form(...), whatsapp: str = Form(...)):
    if supabase:
        try:
            supabase.table("trucks").insert({"from_city":from_city.strip(),"to_city":to_city.strip(),"truck_type":truck_type.strip(),"whatsapp":whatsapp.strip()}).execute()
        except Exception as e: print(e)
    else:
        trucks_memory.append({"from_city":from_city,"to_city":to_city,"truck_type":truck_type,"whatsapp":whatsapp,"created_at":"Just now","id":str(len(trucks_memory))})
    return RedirectResponse("/", status_code=303)

@app.post("/add-load")
async def add_load(from_city: str = Form(...), to_city: str = Form(...), goods_type: str = Form(...), weight: str = Form(...), whatsapp: str = Form(...)):
    if supabase:
        try:
            supabase.table("loads").insert({"from_city":from_city.strip(),"to_city":to_city.strip(),"goods_type":goods_type.strip(),"weight":weight.strip(),"whatsapp":whatsapp.strip()}).execute()
        except Exception as e: print(e)
    else:
        loads_memory.append({"from_city":from_city,"to_city":to_city,"goods_type":goods_type,"weight":weight,"whatsapp":whatsapp,"created_at":"Just now","id":str(len(loads_memory))})
    return RedirectResponse("/", status_code=303)

@app.get("/delete/truck/{tid}")
async def del_truck(tid: str):
    if supabase:
        try: supabase.table("trucks").delete().eq("id", tid).execute()
        except: pass
    return RedirectResponse("/", status_code=303)

@app.get("/delete/load/{lid}")
async def del_load(lid: str):
    if supabase:
        try: supabase.table("loads").delete().eq("id", lid).execute()
        except: pass
    return RedirectResponse("/", status_code=303)

@app.get("/delete/{tid}")
async def del_legacy(tid: str):
    if supabase:
        try: supabase.table("trucks").delete().eq("id", tid).execute()
        except: pass
        try: supabase.table("loads").delete().eq("id", tid).execute()
        except: pass
    return RedirectResponse("/", status_code=303)

@app.get("/health")
async def health(): return {"ok": True, "supabase": supabase is not None}
