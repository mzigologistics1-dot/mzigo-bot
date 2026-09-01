import os, glob
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, FileResponse
from supabase import create_client
app = FastAPI()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except:
        pass
memory_trucks = []
def zm_wa(phone: str, text: str):
    p = "".join(filter(str.isdigit, phone))
    if p.startswith("0"):
        p = "260" + p[1:]
    if not p.startswith("260"):
        p = "260" + p
    from urllib.parse import quote
    return f"https://wa.me/{p}?text={quote(text)}"
@app.get("/logo.png")
def logo():
    if os.path.exists("logo.png"):
        return FileResponse("logo.png")
    for f in glob.glob("*.png") + glob.glob("*.jpg"):
        if os.path.exists(f):
            return FileResponse(f)
    return HTMLResponse("Logo not found", status_code=404)
@app.get("/delete-truck/{tid}")
def del_truck(tid: str):
    global memory_trucks
    if supabase:
        try:
            supabase.table("trucks").delete().eq("id", tid).execute()
        except:
            pass
    memory_trucks = [t for t in memory_trucks if t.get('id') != tid]
    return HTMLResponse('<script>window.location.href="/";</script>')
@app.get("/", response_class=HTMLResponse)
def home():
    trucks = []
    if supabase:
        try:
            trucks = supabase.table("trucks").select("*").order("created_at", desc=True).limit(30).execute().data or []
        except:
            trucks = memory_trucks
    else:
        trucks = memory_trucks
    cards = ""
    for t in trucks:
        msg = f"Hello, I saw your truck on Mzigo Bot from {t.get('from_town','')} to {t.get('to_town','')}. Is it still available?"
        wa = zm_wa(t.get("phone",""), msg)
        cards += f"""<div style="background:#fcfbf9; border:1.5px solid #f0ece5; border-radius:18px; padding:14px; margin-bottom:12px"><div style="font-weight:800">{t.get('from_town','')} → {t.get('to_town','')}</div><div style="display:flex; gap:8px; margin-top:8px"><span style="background:#121212; color:white; padding:6px 10px; border-radius:100px; font-size:11px">🚚 {t.get('truck_type','')}</span><span style="font-size:12px; color:#888">{t.get('phone','')}</span></div><div style="display:flex; gap:8px; margin-top:12px"><a href="{wa}" target="_blank" style="flex:1; background:#25D366; color:white; text-align:center; padding:11px; border-radius:12px; text-decoration:none; font-weight:800">WhatsApp</a><a href="/delete-truck/{t.get('id','')}" style="background:#fff1f0; color:#ff3b30; padding:11px 12px; border-radius:12px; text-decoration:none">✕</a></div></div>"""
    if not cards:
        cards = '<div style="text-align:center; padding:32px; color:#9a9a9a"><b>No trucks available yet</b><p>Be the first to post your truck from the Copperbelt to Lusaka. Drivers check this platform every hour.</p></div>'
    status = f"{len(trucks)} trucks available" if supabase else f"{len(trucks)} trucks (memory mode)"
    return f"""<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"><title>Mzigo Bot</title></head><body style="margin:0; font-family:sans-serif; background:#f6f5f2"><div style="background:#0f0f0f; padding:18px; border-radius:0 0 28px 28px; color:white"><div style="display:flex; gap:12px; max-width:680px; margin:0 auto"><img src="/logo.png" style="width:48px; height:48px; background:white; border-radius:14px; padding:6px"><div><b>Mzigo Logistics ZM</b><br><span style="font-size:11px; color:#ff6a00">NO TRUCK RETURNS EMPTY</span></div></div><div style="max-width:680px; margin:14px auto 0; background:#1e1e1e; border-radius:100px; padding:8px 12px; font-size:11px; color:#9a9a9a">Lusaka ↔ Copperbelt • {status} • Zambia</div></div><div style="max-width:680px; margin:0 auto; padding:14px"><div style="background:white; border-radius:24px; padding:16px; border:1px solid #eee"><h2>Post Your Truck</h2><form action="/add-truck" method="post"><div style="display:grid; grid-template-columns:1fr 1fr; gap:10px"><input name="from_town" placeholder="From • e.g., Kitwe" required style="background:#f6f5f2; border-radius:14px; padding:13px"><input name="to_town" placeholder="To • e.g., Lusaka" required style="background:#f6f5f2; border-radius:14px; padding:13px"></div><div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-top:10px"><input name="truck_type" placeholder="Truck Type • e.g., 30 Ton" style="background:#f6f5f2; border-radius:14px; padding:13px"><input name="phone" placeholder="WhatsApp Number • e.g., 097..." required style="background:#f6f5f2; border-radius:14px; padding:13px"></div><button type="submit" style="margin-top:12px; width:100%; background:#121212; color:white; border:none; border-radius:14px; padding:15px; font-weight:800">Post Truck – Find Loads</button></form></div><div style="background:white; border-radius:24px; padding:16px; border:1px solid #eee; margin-top:14px"><h3>Available Trucks</h3>{cards}</div></div></body></html>"""
@app.post("/add-truck")
def add_truck(from_town: str = Form(...), to_town: str = Form(...), truck_type: str = Form(""), phone: str = Form(...)):
    global memory_trucks
    import uuid, datetime
    new_truck = {"id": str(uuid.uuid4()), "from_town": from_town, "to_town": to_town, "truck_type": truck_type, "phone": phone}
    saved = False
    if supabase:
        try:
            supabase.table("trucks").insert({"from_town": from_town, "to_town": to_town, "truck_type": truck_type, "phone": phone}).execute()
            saved = True
        except:
            pass
    if not saved:
        memory_trucks.insert(0, new_truck)
    return HTMLResponse('<script>window.location.href="/";</script>')
