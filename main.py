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

PAGE = '''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mzigo ZM</title>
<style>
*{box-sizing:border-box}body{margin:0;font-family:sans-serif;background:#f8fafc;color:#0f172a}
header{background:#0f172a;color:#fff;padding:18px 16px;position:sticky;top:0;z-index:10}
.header-inner{max-width:700px;margin:0 auto;display:flex;justify-content:space-between;align-items:center}
.logo{font-weight:900;font-size:20px}.logo span{color:#22c55e}
.live{font-size:11px;background:#22c55e;color:#000;padding:4px 10px;border-radius:20px;font-weight:800}
.container{max-width:700px;margin:0 auto;padding:16px}
.post-card{background:#fff;border-radius:20px;padding:20px;box-shadow:0 8px 30px rgba(0,0,0,.06);border:1px solid #e2e8f0}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:10px}
@media(max-width:500px){.grid2{grid-template-columns:1fr}}
input{width:100%;padding:14px;border-radius:12px;border:1.5px solid #e2e8f0;font-size:15px;background:#f8fafc}
.btn{width:100%;background:#0f172a;color:#fff;padding:15px;border:none;border-radius:12px;font-weight:800;margin-top:12px;cursor:pointer}
.count{background:#0f172a;color:#fff;padding:4px 10px;border-radius:20px;font-size:12px;font-weight:800}
.truck-card{background:#fff;border-radius:18px;padding:16px;margin-bottom:12px;border:1px solid #e2e8f0;overflow:hidden;position:relative}
.route{display:flex;align-items:center;flex-wrap:wrap;gap:6px;font-weight:900;font-size:16px;padding-right:30px}
.route .city{background:#f1f5f9;padding:4px 10px;border-radius:8px;max-width:100%;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.meta{margin-top:12px;display:flex;flex-wrap:wrap;gap:8px}
.tag{padding:6px 12px;border-radius:20px;font-size:12.5px;border:1px solid #e2e8f0;background:#f8fafc;max-width:100%}
.tag.green{background:#dcfce7;color:#14532d}
.tag.dark{background:#0f172a;color:#fff}
.wa{display:block;margin-top:14px;background:#22c55e;color:#000;text-align:center;padding:12px;border-radius:12px;text-decoration:none;font-weight:900}
.del{position:absolute;top:10px;right:10px;background:#fee2e2;color:#dc2626;width:28px;height:28px;border-radius:50%;display:flex;align-items:center;justify-content:center;text-decoration:none;font-weight:900;font-size:16px;border:1px solid #fecaca}
.time{font-size:11px;color:#94a3b8;margin-top:10px}
.empty{background:#fff;border-radius:20px;padding:36px 20px;text-align:center;border:1.5px dashed #cbd5e1;color:#64748b}
.section{margin:28px 0 12px;display:flex;justify-content:space-between;align-items:center}
.clear{font-size:11px;color:#94a3b8;text-decoration:none}
</style></head><body>
<header><div class="header-inner"><div><div class="logo">MZIGO<span>.ZM</span></div><div style="font-size:11px;letter-spacing:2px;opacity:.6;margin-top:2px">NO TRUCK RETURNS EMPTY</div></div><div class="live">LIVE</div></div></header>
<div class="container"><div class="post-card"><h3>Truck Post</h3><form action="/add-truck" method="post">
<div class="grid2"><input name="from_city" placeholder="From Kitwe" required><input name="to_city" placeholder="To Lusaka" required></div>
<div class="grid2" style="margin-top:10px"><input name="truck_type" placeholder="30 Ton" required><input name="whatsapp" placeholder="097..." required></div>
<button class="btn" type="submit">Post Truck</button></form></div>
<div class="section"><h3>Available Trucks</h3><div style="display:flex;gap:8px;align-items:center"><div class="count">COUNT trucks</div><a class="clear" href="/clear-duplicates">Clear dupes</a></div></div>
TRUCKS
</div></body></html>'''

def get_trucks():
    if supabase:
        try:
            res = supabase.table("trucks").select("*").order("created_at", desc=True).execute()
            return res.data
        except Exception as e:
            print(e)
            return trucks_memory
    return trucks_memory

def save_truck(f,t,typ,wa):
    if supabase:
        try:
            supabase.table("trucks").insert({"from_city":f,"to_city":t,"truck_type":typ,"whatsapp":wa}).execute()
            return
        except Exception as e:
            print(e)
    trucks_memory.append({"from_city":f,"to_city":t,"truck_type":typ,"whatsapp":wa,"created_at":"Just now","id": str(len(trucks_memory))})

@app.get("/", response_class=HTMLResponse)
async def home():
    trucks = get_trucks()
    if not trucks:
        trucks_html = '<div class="empty"><b>No trucks yet</b>Be first to post</div>'
    else:
        out=""
        for tr in trucks:
            tid = str(tr.get('id',''))
            wa = str(tr.get('whatsapp','')).strip()
            wa_digits = ''.join(filter(str.isdigit, wa))[-10:]
            wa_link = f"https://wa.me/260{wa_digits}" if len(wa_digits)>=9 else f"https://wa.me/{wa}"
            out+=f'<div class="truck-card"><a class="del" href="/delete/{tid}" onclick="return confirm(\'Delete?\')">x</a><div class="route"><span class="city">{tr.get("from_city","")}</span> > <span class="city">{tr.get("to_city","")}</span></div><div class="meta"><span class="tag dark">{tr.get("truck_type","")}</span><span class="tag green">{tr.get("whatsapp","")}</span></div><a class="wa" href="{wa_link}" target="_blank">WhatsApp</a><div class="time">{str(tr.get("created_at",""))[:19]}</div></div>'
        trucks_html = out
    page = PAGE.replace("COUNT", str(len(trucks))).replace("TRUCKS", trucks_html)
    return HTMLResponse(content=page)

@app.post("/add-truck")
async def add_truck(from_city: str = Form(...), to_city: str = Form(...), truck_type: str = Form(...), whatsapp: str = Form(...)):
    save_truck(from_city.strip(), to_city.strip(), truck_type.strip(), whatsapp.strip())
    return RedirectResponse("/", status_code=303)

@app.get("/delete/{truck_id}")
async def delete_truck(truck_id: str):
    if supabase and truck_id:
        try:
            supabase.table("trucks").delete().eq("id", truck_id).execute()
        except Exception as e:
            print(e)
    else:
        global trucks_memory
        trucks_memory = [t for t in trucks_memory if str(t.get('id','')) != truck_id]
    return RedirectResponse("/", status_code=303)

@app.get("/clear-duplicates")
async def clear_dupes():
    if supabase:
        try:
            res = supabase.table("trucks").select("*").execute()
            seen=set()
            for tr in res.data:
                key=(tr.get('from_city'), tr.get('to_city'), tr.get('whatsapp'))
                if key in seen:
                    supabase.table("trucks").delete().eq("id", tr.get('id')).execute()
                else:
                    seen.add(key)
        except Exception as e:
            print(e)
    return RedirectResponse("/", status_code=303)

@app.get("/health")
async def health():
    return {"supabase": supabase is not None, "status": "ok"}
