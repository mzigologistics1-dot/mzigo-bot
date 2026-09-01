import os, glob
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, FileResponse
from supabase import create_client, Client

app = FastAPI()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except:
        pass

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
    if supabase:
        try:
            supabase.table("trucks").delete().eq("id", tid).execute()
        except:
            pass
    return HTMLResponse('<script>window.location.href="/";</script>')

@app.get("/", response_class=HTMLResponse)
def home():
    trucks = []
    if supabase:
        try:
            trucks = supabase.table("trucks").select("*").order("created_at", desc=True).limit(30).execute().data or []
        except:
            pass
    html_cards = ""
    for t in trucks:
        msg = f"Hello, I saw your truck on Mzigo Bot from {t.get('from_town','')} to {t.get('to_town','')}. Is it still available?"
        wa = zm_wa(t.get("phone",""), msg)
        html_cards += f"""<div style="background:#fcfbf9; border:1.5px solid #f0ece5; border-radius:18px; padding:14px; margin-bottom:12px"><div style="font-weight:800; font-size:17px">{t.get('from_town','')} <span style="color:#ff6a00">→</span> {t.get('to_town','')}</div><div style="margin-top:8px; display:flex; gap:8px"><span style="background:#121212; color:white; padding:6px 10px; border-radius:100px; font-size:11px; font-weight:700">🚚 {t.get('truck_type','30 Ton')}</span><span style="font-size:12px; color:#888">{t.get('phone','')}</span></div><div style="display:flex; gap:8px; margin-top:12px"><a href="{wa}" target="_blank" style="flex:1; background:#25D366; color:white; text-align:center; padding:11px; border-radius:12px; text-decoration:none; font-weight:800">WhatsApp</a><a href="tel:{t.get('phone','')}" style="background:white; border:1.5px solid #e8e5df; padding:11px 16px; border-radius:12px; text-decoration:none; color:#121212; font-weight:800">Call</a><a href="/delete-truck/{t.get('id','')}" style="background:#fff1f0; color:#ff3b30; padding:11px 14px; border-radius:12px; text-decoration:none" onclick="return confirm('Are you sure you want to delete this truck?')">✕</a></div></div>"""
    if not html_cards:
        html_cards = '<div style="text-align:center; padding:40px 20px; color:#9a9a9a"><div style="font-size:44px">🚚</div><b style="color:#121212; font-size:16px">No trucks available yet</b><p style="font-size:13px; max-width:280px; margin:8px auto 0">Be the first to post your truck from the Copperbelt to Lusaka. Drivers check this platform every hour.</p></div>'
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Mzigo Bot - No Truck Returns Empty</title></head><body style="margin:0; font-family:sans-serif; background:#f6f5f2"><div style="background:#0f0f0f; padding:18px 20px; border-radius:0 0 28px 28px; color:white"><div style="display:flex; gap:14px; max-width:680px; margin:0 auto; align-items:center"><img src="/logo.png" style="width:52px; height:52px; background:white; border-radius:14px; padding:6px" onerror="this.style.display='none'"><div><div style="font-weight:800; font-size:20px">Mzigo Logistics ZM</div><div style="font-size:12px; color:#ff6a00; font-weight:700">NO TRUCK RETURNS EMPTY</div></div></div><div style="max-width:680px; margin:14px auto 0; background:#1e1e1e; border-radius:100px; padding:8px 14px; font-size:11px; color:#9a9a9a">Lusaka ↔ Copperbelt • {len(trucks)} trucks available • Zambia</div></div><div style="max-width:680px; margin:0 auto; padding:18px"><div style="background:white; border-radius:24px; padding:20px; border:1px solid #eee; margin-bottom:18px"><h2 style="margin:0 0 14px">Post Your Truck</h2><form action="/add-truck" method="post"><div style="display:flex; gap:10px"><input name="from_town" placeholder="From • e.g., Kitwe" required style="flex:1; background:#f6f5f2; border:1.5px solid #ece9e3; border-radius:14px; padding:13px"><input name="to_town" placeholder="To • e.g., Lusaka" required style="flex:1; background:#f6f5f2; border-radius:14px; padding:13px"></div><div style="display:flex; gap:10px; margin-top:10px"><input name="truck_type" placeholder="Truck Type • e.g., 30 Ton" style="flex:1; background:#f6f5f2; border-radius:14px; padding:13px"><input name="phone" placeholder="WhatsApp Number • e.g., 097..." required style="flex:1; background:#f6f5f2; border-radius:14px; padding:13px"></div><button type="submit" style="margin-top:12px; width:100%; background:#121212; color:white; border:none; border-radius:14px; padding:15px; font-weight:800">Post Truck – Find Loads</button></form></div><div style="background:white; border-radius:24px; padding:18px; border:1px solid #eee"><h3 style="margin:0 0 14px">Available Trucks</h3>{html_cards}</div></div></body></html>"""

@app.post("/add-truck")
def add_truck(from_town: str = Form(...), to_town: str = Form(...), truck_type: str = Form(""), phone: str = Form(...)):
    if supabase:
        try:
            supabase.table("trucks").insert({"from_town": from_town, "to_town": to_town, "truck_type": truck_type, "phone": phone}).execute()
        except:
            pass
    return HTMLResponse('<script>window.location.href="/";</script>')
