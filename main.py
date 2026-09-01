import os, glob
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
    for pat in ["mzigo_real_logo*", "778816711*", "*logo*.png", "*.png", "*.jpg"]:
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

@app.get("/", response_class=HTMLResponse)
def home():
    trucks = []
    if supabase:
        try:
            trucks = supabase.table("trucks").select("*").order("created_at", desc=True).limit(30).execute().data or []
        except:
            pass

    trucks_html = ""
    for t in trucks:
        msg = f"Hello, I saw your truck on Mzigo Bot from {t.get('from_town','')} to {t.get('to_town','')}. Is it still available?"
        wa = zm_whatsapp_link(t.get("phone",""), msg)
        trucks_html += f"""
        <div class="card">
            <div class="route"><span>{t.get('from_town','')}</span><span class="arrow">→</span><span>{t.get('to_town','')}</span></div>
            <div class="meta"><span class="pill">🚚 {t.get('truck_type','30 Ton Truck')}</span><span class="phone">{t.get('phone','')}</span></div>
            <div class="actions">
                <a href="{wa}" target="_blank" class="btn-wa">WhatsApp</a>
                <a href="tel:{t.get('phone','')}" class="btn-call">Call</a>
                <a href="/delete-truck/{t.get('id','')}" class="btn-del" onclick="return confirm('Are you sure you want to delete this truck?')">✕</a>
            </div>
        </div>"""

    if not trucks_html:
        trucks_html = '<div class="empty"><div class="empty-icon">🚚</div><b>No trucks available yet</b><p>Be the first to post your truck from the Copperbelt to Lusaka. Drivers check this platform every hour.</p></div>'

    return f"""
<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mzigo Bot – No Truck Returns Empty</title>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@600;700;800&display=swap" rel="stylesheet">
<style>
*{{box-sizing:border-box}} body{{margin:0; font-family:'Plus Jakarta Sans',-apple-system,sans-serif; background:#f6f5f2; color:#121212}}
.header{{background:#0f0f0f; padding:18px 20px 22px; border-radius:0 0 28px 28px; color:white; position:sticky; top:0; z-index:10}}
.h-top{{display:flex; align-items:center; gap:14px; max-width:680px; margin:0 auto}}
.h-top img{{width:52px; height:52px; background:white; border-radius:14px; padding:6px; object-fit:contain}}
.h-title{{line-height:1.1}} .h-title b{{font-size:20px; font-weight:800}} .h-title span{{display:block; font-size:12px; color:#ff6a00; font-weight:700; margin-top:3px; letter-spacing:0.8px}}
.badge{{max-width:680px; margin:14px auto 0; background:#1e1e1e; border:1px solid #2a2a2a; border-radius:100px; padding:8px 14px; display:flex; gap:8px; font-size:11px; color:#9a9a9a; align-items:center}}
.badge b{{color:#fff}} .dot{{width:6px; height:6px; background:#25D366; border-radius:50%}}
.wrap{{max-width:680px; margin:0 auto; padding:18px}}
.post-card{{background:white; border-radius:24px; padding:20px; box-shadow:0 8px 24px rgba(0,0,0,0.06); border:1px solid #eee; margin-bottom:18px}}
.post-card h2{{margin:0 0 14px; font-size:18px; font-weight:800;}}
.input-row{{display:flex; gap:10px}} .field{{flex:1; background:#f6f5f2; border:1.5px solid #ece9e3; border-radius:14px; padding:13px 14px; font-size:14px; font-weight:600; outline:none; width:100%}} .field:focus{{border-color:#ff6a00; background:white}}
.btn-post{{margin-top:12px; width:100%; background:#121212; color:white; border:none; border-radius:14px; padding:15px; font-size:15px; font-weight:800; cursor:pointer}}
.section{{background:white; border-radius:24px; padding:18px; border:1px solid #eee}}
.section-head{{display:flex; justify-content:space-between; align-items:center; margin-bottom:14px}} .section-head h3{{margin:0; font-size:16px; font-weight:800}} .count{{background:#f6f5f2; padding:6px 10px; border-radius:100px; font-size:12px; font-weight:700; color:#666}}
.card{{background:#fcfbf9; border:1.5px solid #f0ece5; border-radius:18px; padding:14px; margin-bottom:12px}} 
.route{{font-size:17px; font-weight:800; display:flex; align-items:center; gap:8px}} .arrow{{color:#ff6a00}}
.meta{{display:flex; gap:8px; margin-top:10px; align-items:center}} .pill{{background:#121212; color:white; padding:6px 10px; border-radius:100px; font-size:11px; font-weight:700}} .phone{{font-size:12px; color:#888; font-weight:600}}
.actions{{display:flex; gap:8px; margin-top:12px}} .btn-wa{{flex:1; background:#25D366; color:white; text-align:center; padding:11px; border-radius:12px; text-decoration:none; font-weight:800; font-size:13px}} .btn-call{{background:white; border:1.5px solid #e8e5df; padding:11px 16px; border-radius:12px; text-decoration:none; color:#121212; font-weight:800; font-size:13px}} .btn-del{{background:#fff1f0; border:1px solid #fee2e2; color:#ff3b30; padding:11px 14px; border-radius:12px; text-decoration:none; font-weight:800}}
.empty{{text-align:center; padding:36px 20px; color:#9a9a9a}} .empty-icon{{font-size:44px; margin-bottom:12px}} .empty b{{color:#121212; font-size:16px; display:block}} .empty p{{font-size:13px; line-height:1.5; max-width:280px; margin:8px auto 0}}
.footer{{text-align:center; padding:30px; color:#b8b5b0; font-size:11px; font-weight:600}}
</style></head>
<body>
<div class="header">
  <div class="h-top">
    <img src="/logo.png" onerror="this.style.display='none'">
    <div class="h-title"><b>Mzigo Logistics ZM</b><span>NO TRUCK RETURNS EMPTY</span></div>
  </div>
  <div class="badge"><span class="dot"></span><b>Lusaka ↔ Copperbelt</b> • {len(trucks)} trucks available • WhatsApp Bot • Zambia</div>
</div>
<div class="wrap">
  <div class="post-card">
    <h2>Post Your Truck</h2>
    <form action="/add-truck" method="post">
      <div class="input-row">
        <input class="field" name="from_town" placeholder="From • e.g., Kitwe" required>
       
