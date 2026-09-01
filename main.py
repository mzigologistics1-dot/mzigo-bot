import os
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, FileResponse
from supabase import create_client, Client

app = FastAPI()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except:
        pass

def zm_whatsapp_link(phone: str, text: str):
    p = "".join(filter(str.isdigit, phone))
    if p.startswith("0"):
        p = "260" + p[1:]
    if not p.startswith("260"):
        p = "260" + p
    from urllib.parse import quote
    return f"https://wa.me/{p}?text={quote(text)}"

@app.get("/logo.png")
def get_logo():
    import glob
    if os.path.exists("logo.png"):
        return FileResponse("logo.png")
    # Auto-find your uploaded logo even if named 778... or mzigo_real_logo...
    for pat in ["mzigo_real_logo*", "778816711*", "*logo*.png", "*.png", "*.jpg", "*.jpeg"]:
        for f in glob.glob(pat):
            if os.path.exists(f) and f.lower().endswith(('.png','.jpg','.jpeg')):
                return FileResponse(f)
    return HTMLResponse("Logo not found", status_code=404)

@app.get("/delete-truck/{truck_id}")
def delete_truck(truck_id: str):
    if supabase:
        try: supabase.table("trucks").delete().eq("id", truck_id).execute()
        except: pass
    return HTMLResponse('<script>window.location.href="/";</script>')

@app.get("/delete-load/{load_id}")
def delete_load(load_id: str):
    if supabase:
        try: supabase.table("loads").delete().eq("id", load_id).execute()
        except: pass
    return HTMLResponse('<script>window.location.href="/";</script>')

@app.get("/", response_class=HTMLResponse)
def home():
    trucks = []
    loads = []
    if supabase:
        try:
            trucks = supabase.table("trucks").select("*").order("created_at", desc=True).limit(30).execute().data or []
            loads = supabase.table("loads").select("*").order("created_at", desc=True).limit(30).execute().data or []
        except:
            pass

    trucks_html = ""
    for t in trucks:
        msg = f"Hi! I saw your truck on MZIGO BOT from {t.get('from_town','')} to {t.get('to_town','')}. Still available?"
        wa = zm_whatsapp_link(t.get("phone",""), msg)
        trucks_html += f"""
        <div class="card">
            <div class="route"><span>{t.get('from_town','')}</span><span class="arrow">→</span><span>{t.get('to_town','')}</span></div>
            <div class="meta"><span class="pill">🚚 {t.get('truck_type
