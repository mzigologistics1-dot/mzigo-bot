            from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from urllib.parse import quote
import os

# Supabase - safe import
try:
    from supabase import create_client
except:
    create_client = None

def zm_whatsapp_link(phone: str, from_town="", to_town=""):
    try:
        clean = phone.replace(" ", "").replace("+", "").replace("-", "")
        if clean.startswith("0"):
            clean = "260" + clean[1:]
        if not clean.startswith("260"):
            clean = "260" + clean
        msg = f"Hi, I saw your post on MZIGO from {from_town} to {to_town}. Is it still available?"
        return f"https://wa.me/{clean}?text={quote(msg)}"
    except:
        return f"https://wa.me/{phone}"

app = FastAPI()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = None
if SUPABASE_URL and SUPABASE_KEY and create_client:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"Supabase failed: {e}")
        supabase = None

memory_trucks = []
memory_loads = []

@app.get("/", response_class=HTMLResponse)
def home():
    trucks = []
    loads = []
    if supabase:
        try:
            trucks = supabase.table("trucks").select("*").order("created_at", desc=True).execute().data
        except: pass
        try:
            loads = supabase.table("loads").select("*").order("created_at", desc=True).execute().data
        except: pass
    else:
        trucks = memory_trucks
        loads = memory_loads

    banner = '<div style="background:#16a34a; color:white; padding:10px; text-align:center; font-weight:bold;">🟢 SUPABASE CONNECTED - Forever</div>' if supabase else '<div style="background:#ef4444; color:white; padding:10px; text-align:center;">🔴 MEMORY MODE</div>'

    trucks_html = ""
    for t in trucks:
        wa = zm_whatsapp_link(t.get('phone',''), t.get('from_town',''), t.get('to_town',''))
        trucks_html += f'<div style="background:white; margin:12px; padding:15px; border-radius:12px; border-left:5px solid #16a34a;"><b>{t.get("from_town","")} → {t.get("to_town","")}</b><br><small>📦 {t.get("capacity","")} | 📞 {t.get("phone","")}</small><br><div style="display:flex; gap:8px; margin-top:10px;"><a href="tel:{t.get("phone","")}" style="flex:1; background:#f3f4f6; text-align:center; padding:10px; border-radius:8px; text-decoration:none; color:black;">📞 Call</a><a href="{wa}" target="_blank" style="flex:1; background:#25D366; text-align:center; padding:10px; border-radius:8px; text-decoration:none; color:white; font-weight:bold;">💬 WhatsApp</a></div></div>'

    loads_html = ""
    for l in loads:
        wa = zm_whatsapp_link(l.get('phone',''), l.get('from_town',''), l.get('to_town',''))
        loads_html += f'<div style="background:white; margin:12px; padding:15px; border-radius:12px; border-left:5px solid #f59e0b;"><b>{l.get("from_town","")} → {l.get("to_town","")}</b><br><small>📦 {l.get("goods","")} | 📞 {l.get("phone","")}</small><br><div style="display:flex; gap:8px; margin-top:10px;"><a href="tel:{l.get("phone","")}" style="flex:1; background:#f3f4f6; text-align:center; padding:10px; border-radius:8px; text-decoration:none; color:black;">📞 Call</a><a href="{wa}" target="_blank" style="flex:1; background:#25D366; text-align:center; padding:10px; border-radius:8px; text-decoration:none; color:white; font-weight:bold;">💬 WhatsApp</a></div></div>'

    return f'<html><head><meta name="viewport" content="width=device-width, initial-scale=1"><title>MZIGO</title></head><body style="font-family:sans-serif; background:#f0fdf4; margin:0;"><div style="background:#16a34a; color:white; padding:20px; text-align:center; font-size:22px; font-weight:bold;">🚚 MZIGO - Move Anything, Zambia</div>{banner}<div style="padding:15px;"><h3>Post Your Truck</h3><form action="/add-truck" method="post" style="background:white; padding:15px; border-radius:12px;"><input name="from_town" placeholder="From e.g. Kitwe" required style="width:100%; padding:10px; margin:5px 0; border-radius:8px; border:1px solid #ccc;"><input name="to_town" placeholder="To e.g. Lusaka" required style="width:100%; padding:10px; margin:5px 0; border-radius:8px; border:1px solid #ccc;"><input name="phone" placeholder="Phone 097..." required style="width:100%; padding:10px; margin:5px 0; border-radius:8px; border:1px solid #ccc;"><input name="capacity" placeholder="Capacity e.g. 10 Ton" style="width:100%; padding:10px; margin:5px 0; border-radius:8px; border:1px solid #ccc;"><button style="width:100%; background:#16a34a; color:white; padding:12px; border:none; border-radius:8px; font-weight:bold;">🚚 POST TRUCK</button></form><h3 style="margin-top:25px;">Post Your Load</h3><form action="/add-load" method="post" style="background:white; padding:15px; border-radius:12px;"><input name="from_town" placeholder="From" required style="width:100%; padding:10px; margin:5px 0; border-radius:8px; border:1px solid #ccc;"><input name="to_town" placeholder="To" required style="width:100%; padding:10px; margin:5px 0; border-radius:8px; border:1px solid #ccc;"><input name="phone" placeholder="Phone" required style="width:100%; padding:10px; margin:5px 0; border-radius:8px; border:1px solid #ccc;"><input name="goods" placeholder="Goods e.g. Maize" style="width:100%; padding:10px; margin:5px 0; border-radius:8px; border:1px solid #ccc;"><button style="width:100%; background:#f59e0b; color:white; padding:12px; border:none; border-radius:8px; font-weight:bold;">📦 POST LOAD</button></form></div><h3 style="padding-left:15px;">Available Trucks</h3>{trucks_html if trucks_html else "<p style=\"padding:0 15px; color:gray;\">No trucks yet. Be first!</p>"}<h3 style="padding-left:15px;">Available Loads</h3>{loads_html if loads_html else "<p style=\"padding:0 15px; color:gray;\">No loads yet. Be first!</p>"}</body></html>'

@app.post("/add-truck")
def add_truck(from_town: str = Form(...), to_town: str = Form(...), phone: str = Form(...), capacity: str = Form("")):
    data = {"from_town": from_town, "to_town": to_town, "phone": phone, "capacity": capacity}
    if supabase:
        try: supabase.table("trucks").insert(data).execute()
        except: memory_trucks.insert(0, data)
    else: memory_trucks.insert(0, data)
    return HTMLResponse('<script>window.location="/"</script>')

@app.post("/add-load")
def add_load(from_town: str = Form(...), to_town: str = Form(...), phone: str = Form(...), goods: str = Form("")):
    data = {"from_town": from_town, "to_town": to_town, "phone": phone, "goods": goods}
    if supabase:
        try: supabase.table("loads").insert(data).execute()
        except: memory_loads.insert(0, data)
    else: memory_loads.insert(0, data)
    return HTMLResponse('<script>window.location="/"</script>')
