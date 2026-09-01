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
    if os.path.exists("logo.png"):
        return FileResponse("logo.png")
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
            trucks = supabase.table("trucks").select("*").order("created_at", desc=True).limit(20).execute().data or []
            loads = supabase.table("loads").select("*").order("created_at", desc=True).limit(20).execute().data or []
        except: pass

    trucks_html = ""
    for t in trucks:
        msg = f"Hi, I saw your truck on Mzigo from {t.get('from_town','')} to {t.get('to_town','')}. Is it still available?"
        wa = zm_whatsapp_link(t.get("phone",""), msg)
        trucks_html += f"""
        <div style="background:white; border:1px solid #e5e7eb; border-radius:12px; padding:12px; margin-bottom:10px;">
            <div style="font-weight:bold;">🚚 {t.get('from_town','')} → {t.get('to_town','')}</div>
            <div style="color:#6b7280; font-size:13px;">Truck: {t.get('truck_type','')}</div>
            <div style="display:flex; gap:8px; margin-top:8px;">
                <a href="{wa}" target="_blank" style="flex:1; background:#25D366; color:white; text-align:center; padding:10px; border-radius:8px; text-decoration:none; font-weight:bold;">💬 WhatsApp</a>
                <a href="tel:{t.get('phone','')}" style="background:#f3f4f6; padding:10px 14px; border-radius:8px; text-decoration:none;">📞</a>
                <a href="/delete-truck/{t.get('id','')}" style="background:#fee2e2; color:#dc2626; padding:10px 12px; border-radius:8px; text-decoration:none;" onclick="return confirm('Delete?')">🗑️</a>
            </div>
        </div>
        """
    if not trucks_html:
        trucks_html = '<div style="text-align:center; color:#9ca3af; padding:20px;">No trucks yet. Be first!</div>'

    return f"""
    <html><head><meta name="viewport" content="width=device-width, initial-scale=1"><title>Mzigo</title></head>
    <body style="margin:0; font-family:sans-serif; background:#f9fafb;">
        <div style="background:white; padding:12px 16px; display:flex; align-items:center; gap:12px; border-bottom:1px solid #e5e7eb; position:sticky; top:0;">
            <img src="/logo.png" style="height:48px; object-fit:contain;" onerror="this.style.display='none'">
            <div><div style="font-weight:800; font-size:18px;">Mzigo Logistics ZM</div><div style="font-size:12px; color:#ea580c; font-weight:600;">No Truck Returns Empty</div></div>
        </div>
        <div style="padding:16px; max-width:600px; margin:0 auto;">
            <div style="background:white; border-radius:16px; padding:16px; margin-bottom:16px;">
                <h3>Post Your Truck</h3>
                <form action="/add-truck" method="post" style="display:grid; gap:8px;">
                    <div style="display:flex; gap:8px;"><input name="from_town" placeholder="From Kitwe" required style="flex:1; padding:10px; border:1px solid #d1d5db; border-radius:8px;"><input name="to_town" placeholder="To Lusaka" required style="flex:1; padding:10px; border:1px solid #d1d5db; border-radius:8px;"></div>
                    <input name="truck_type" placeholder="Truck type" style="padding:10px; border:1px solid #d1d5db; border-radius:8px;">
                    <input name="phone" placeholder="WhatsApp 097..." required style="padding:10px; border:1px solid #d1d5db; border-radius:8px;">
                    <button style="background:#111827; color:white; padding:12px; border:none; border-radius:8px; font-weight:bold;">Post Truck →</button>
                </form>
            </div>
            <div style="background:white; border-radius:16px; padding:16px;">{trucks_html}</div>
        </div>
    </body></html>
    """

@app.post("/add-truck")
def add_truck(from_town: str = Form(...), to_town: str = Form(...), truck_type: str = Form(""), phone: str = Form(...)):
    if supabase:
        try: supabase.table("trucks").insert({"from_town": from_town, "to_town": to_town, "truck_type": truck_type, "phone": phone}).execute()
        except: pass
    return HTMLResponse('<script>window.location.href="/";</script>')
