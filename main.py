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
    cards = ""
    for t in trucks:
        msg = f"Hello, I saw your truck on Mzigo Bot from {t.get('from_town','')} to {t.get('to_town','')}. Is it still available?"
        wa = zm_wa(t.get("phone",""), msg)
        cards += f"""<div class="card"><div class="route">{t.get('from_town','')} <span class="arrow">→</span> {t.get('to_town','')}</div><div class="meta"><span class="pill">🚚 {t.get('truck_type','30 Ton')}</span><span class="phone">{t.get('phone','')}</span></div><div class="actions"><a href="{wa}" target="_blank" class="btn-wa">WhatsApp</a><a href="tel:{t.get('phone','')}" class="btn-call">Call</a><a href="/delete-truck/{t.get('id','')}" class="btn-del" onclick="return confirm('Are you sure you want to delete this truck?')">✕</a></div></div>"""
    if not cards:
        cards = '<div class="empty"><div class="empty-icon">🚚</div><b>No trucks available yet</b><p>Be the first to post your truck from the Copperbelt to Lusaka. Drivers check this platform every hour.</p></div>'
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1"><title>Mzigo Bot - No Truck Returns Empty</title><style>*{{box-sizing:border-box}} body{{margin:0; font-family:sans-serif; background:#f6f5f2; overflow-x:hidden}} .header{{background:#0f0f0f; padding:18px 16px 22px; border-radius:0 0 28px 28px; color:white}} .h-top{{display:flex; gap:12px; max-width:680px; margin:0 auto; align-items:center}} .h-top img{{width:48px; height:48px; background:white; border-radius:14px; padding:6px}} .badge{{max-width:680px; margin:14px auto 0; background:#1e1e1e; border-radius:100px; padding:8px 12px; font-size:11px; color:#9a9a9a}} .wrap{{max-width:680px; margin:0 auto; padding:14px; width:100%}} .post-card{{background:white; border-radius:24px; padding:16px; border:1px solid #eee; margin-bottom:14px}} .grid{{display:grid; grid-template-columns:1fr 1fr; gap:10px}} @media(max-width:480px){{.grid{{grid-template-columns:1fr}}}} .field{{width:100%; background:#f6f5f2; border:1.5px solid #ece9e3; border-radius:14px; padding:13px}} .btn-post{{margin-top:12px; width:100%; background:#121212; color:white; border:none; border-radius:14px; padding:15px; font-weight:800}} .section{{background:white; border-radius:24px; padding:16px; border:1px solid #eee}} .card{{background:#fcfbf9; border:1.5px solid #f0ece5; border-radius:18px; padding:14px; margin-bottom:12px}} .route{{font-weight:800}} .arrow{{color:#ff6a00}} .actions{{display:flex; gap:8px; margin-top:12px}} .btn-wa{{flex:1; background:#25D366; color:white; text-align:center; padding:11px; border-radius:12px; text-decoration:none; font-weight:800}} .btn-call{{background:white; border:1.5px solid #e8e5df; padding:11px 14px; border-radius:12px; text-decoration:none; color:#121212; font-weight:800}} .btn-del{{background:#fff1f0; color:#ff3b30; padding:11px 12px; border-radius:12px; text-decoration:none}} .empty{{text-align:center; padding:32px 16px; color:#9a9a9a}} .footer{{text-align:center; padding:24px; color:#b8b5b0; font-size:11px}}</style></head><body><div class="header"><div class="h-top"><img src="/logo.png" onerror="this.style.display='none'"><div><b>Mzigo Logistics ZM</b><br><span style="font-size:11px; color:#ff6a00">NO TRUCK RETURNS EMPTY</span></div></div><div class="badge">Lusaka ↔ Copperbelt • {len(trucks)} trucks available • Zambia</div></div><div class="wrap"><div class="post-card"><h2>Post Your Truck</h2><form action="/add-truck" method="post"><div class="grid"><input class="field" name="from_town" placeholder="From • e.g., Kitwe" required><input class="field" name="to_town" placeholder="To • e.g., Lusaka" required></div><div class="grid" style="margin-top:10px"><input class="field" name="truck_type" placeholder="Truck Type • e.g., 30 Ton"><input class="field" name="phone" placeholder="WhatsApp Number • e.g., 097..." required></div><button class="btn-post" type="submit">Post Truck – Find Loads</button></form></div><div class="section"><h3 style="margin:0 0 14px">Available Trucks</h3>{cards}</div><div class="footer">Built in Kitwe for Zambian truckers • Mzigo Bot © 2026</div></div></body></html>"""

@app.post("/add-truck")
def add_truck(from_town: str = Form(...), to_town: str = Form(...), truck_type: str = Form(""), phone: str = Form(...)):
    if supabase:
        try:
            supabase.table("trucks").insert({"from_town": from_town, "to_town": to_town, "truck_type": truck_type, "phone": phone}).execute()
        except:
            pass
    return HTMLResponse('<script>window.location.href="/";</script>')
