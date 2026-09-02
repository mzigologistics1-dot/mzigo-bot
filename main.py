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
        print("✅ Supabase connected")
    else:
        print("❌ SUPABASE NOT SET")
except Exception as e:
    print(f"❌ Supabase failed: {e}")

app = FastAPI()
trucks_memory = []

PAGE_HEAD = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mzigo Logistics ZM</title>
<style>
*{box-sizing:border-box}
body{margin:0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#f8fafc;color:#0f172a;line-height:1.4}
header{background:#0f172a;color:#fff;padding:18px 16px;position:sticky;top:0;z-index:10}
.header-inner{max-width:700px;margin:0 auto;display:flex;justify-content:space-between;align-items:center}
.logo{font-weight:900;font-size:20px}
.logo span{color:#22c55e}
.tagline{font-size:11px;letter-spacing:2px;opacity:.6;margin-top:2px}
.live{font-size:11px;background:#22c55e;color:#000;padding:4px 10px;border-radius:20px;font-weight:800}
.container{max-width:700px;margin:0 auto;padding:16px}
.post-card{background:#fff;border-radius:20px;padding:20px;box-shadow:0 8px 30px rgba(0,0,0,.06);border:1px solid #e2e8f0}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:10px}
@media(max-width:500px){.grid2{grid-template-columns:1fr}}
input{width:100%;padding:14px;border-radius:12px;border:1.5px solid #e2e8f0;font-size:15px;background:#f8fafc}
.btn{width:100%;background:#0f172a;color:#fff;padding:15px;border:none;border-radius:12px;font-weight:800;margin-top:12px}
.count{background:#0f172a;color:#fff;padding:4px 10px;border-radius:20px;font-size:12px;font-weight:800}
.truck-card{background:#fff;border-radius:18px;padding:16px;margin-bottom:12px;border:1px solid #e2e8f0;overflow:hidden}
.truck-card *{min-width:0;overflow-wrap:anywhere;word-break:break-word}
.route{display:flex;align-items:center;flex-wrap:wrap;gap:6px;font-weight:900;font-size:16px}
.route .city{background:#f1f5f9;padding:4px 10px;border-radius:8px;max-width:100%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.meta{margin-top:12px;display:flex;flex-wrap:wrap;gap:8px}
.tag{padding:6px 12px;border-radius:20px;font-size:12.5px;border:1px solid #e2e8f0;background:#f8fafc;max-width:100%}
.tag.green{background:#dcfce7;color:#14532d}
.tag.dark{background:#0f172a;color:#fff}
.wa{display:block;margin-top:14px;background:#22c55e;color:#000;text-align:center;padding:12px;border-radius:12px;text-decoration:none;font-weight:900}
.time{font-size:11px;color:#94a3b8;margin-top:10px}
.empty{background:#fff;border-radius:20px;padding:36px 20px;text-align:center;border:1.5px dashed #cbd5e1;color:#64748b}
.section{margin:28px 0 12px;display:flex;justify-content:space-between;align-items:center}
</style>
</head>
<body>
<header><div class="header-inner"><div><div class="logo">MZIGO<span>.ZM</span></div><div class="tagline">NO TRUCK RETURNS EMPTY</div></div><div class="live">● LIVE</div></div></header>
<div class="container">
<div class="post-card">
<h3>🚛 Post Your Truck</h3>
<p>Find back-loads from Lusaka to Copperbelt</p>
<form action="/add-truck" method="post">
<div class="grid2"><input name="from_city" placeholder="From • e.g. Kitwe" required><input name="to_city" placeholder="To • e.g. Lusaka" required></div>
<div class="grid2" style="margin-top:10px"><input name="truck_type" placeholder="Truck • e.g. 30 Ton" required><input name="whatsapp" placeholder="WhatsApp • 097..." required></div>
<button class="btn" type="submit">Post Truck → Find Loads</button>
</form>
</div>
<div class="section"><h3>Available Trucks</h3><div class="count">COUNT_PLACEHOLDER trucks</div></div>
TRUCKS_PLACEHOLDER
</div>
</body>
</html>
"""

def get_trucks():
    if supabase:
        try:
            res = supabase.table("trucks").select("*").order("created_at", desc=True).execute()
            return res.data
        except Exception as e:
            print(f"SELECT failed: {e}")
            return trucks_memory
    return trucks_memory

def save_truck(f,t,typ,wa):
    if supabase:
        try:
            supabase.table("trucks").insert({"from_city":f,"to_city":t,"truck_type":typ,"whatsapp":wa}).execute()
            print(f"Saved {f}->{t}")
            return
        except Exception as e:
            print(f"INSERT failed: {e}")
    trucks_memory.append({"from_city":f,"to_city":t,"truck_type":typ,"whatsapp":wa,"created_at":"Just now"})

@app.get("/", response_class=HTMLResponse)
async def home():
    trucks = get_trucks()
    if not trucks:
        trucks_html = '<div class="empty"><b>No trucks available yet</b>Be the first to post your truck.</div>'
    else:
        out=""
        for tr in trucks:
            wa = str(tr.get('whatsapp','')).strip()
            wa_digits = ''.join(filter(str.isdigit, wa))[-10:]
            wa_link = f"https://wa.me/260{wa_digits}"
            out+=f'<div class="truck-card"><div class="route"><span class="city">{tr.get("from_city","")}</span> → <span class="city">{tr.get("to_city","")}</span></div><div class="meta"><span class="tag dark">{tr.get("truck_type","")}</span><span class="tag green">📱 {tr.get("whatsapp","")}</span></div><a class="wa" href="{wa_link}" target="_blank">💬 WhatsApp Driver</a><div class="time">{str(tr.get("created_at",""))[:19]}</div></div>'
        trucks_html = out
    page = PAGE_HEAD.replace("COUNT_PLACEHOLDER", str(len(trucks))).replace("TRUCKS_PLACEHOLDER", trucks_html)
    return HTMLResponse(content=page)

@app.post("/add-truck")
async def add_truck(from_city: str = Form(...), to_city: str = Form(...), truck_type: str = Form(...), whatsapp: str = Form(...)):
    save_truck(from_city.strip(), to_city.strip(), truck_type.strip(), whatsapp.strip())
    return RedirectResponse("/", status_code=303)

@app.get("/health")
async def health():
    return {"supabase": supabase is not None, "status": "ok"}
