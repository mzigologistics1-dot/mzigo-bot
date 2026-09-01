from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse
import os
from supabase import create_client, Client

app = FastAPI()

# --- SUPABASE ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("SUPABASE CONNECTED")
    except Exception as e:
        print(f"Supabase error: {e}")

def get_trucks():
    if not supabase: return []
    try:
        res = supabase.table("trucks").select("*").order("created_at", desc=True).limit(50).execute()
        return res.data or []
    except: return []

def get_loads():
    if not supabase: return []
    try:
        res = supabase.table("loads").select("*").order("created_at", desc=True).limit(50).execute()
        return res.data or []
    except: return []

HTML = """
<html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Mzigo - Zambia Truck Link</title>
<style>
body{font-family:Arial;background:#0f172a;color:white;margin:0;padding:0}
.header{background:#16a34a;padding:20px;text-align:center}
.card{background:#1e293b;margin:15px;padding:15px;border-radius:12px}
input,select,button{width:100%;padding:12px;margin:6px 0;border-radius:8px;border:none}
button{background:#16a34a;color:white;font-weight:bold;font-size:16px}
.truck{background:#334155;padding:10px;margin:8px 0;border-radius:8px;border-left:4px solid #22c55e}
a{color:#4ade80}
</style></head><body>
<div class="header"><h1>🚛 MZIGO</h1><p>Move Anything, Anywhere in Zambia</p><p style="font-size:12px">{db_status}</p></div>

<div class="card"><h3>🔍 Find Transport</h3>
<form action="/" method="get">
<input name="from_city" placeholder="From (e.g. Kitwe)" value="{from_f}">
<input name="to_city" placeholder="To (e.g. Lusaka)" value="{to_f}">
<button>Search</button></form></div>

<div class="card"><h3>🚚 I Have a Truck (Empty)</h3>
<form action="/trucks/add-form" method="post">
<input name="from_city" placeholder="From" required>
<input name="to_city" placeholder="To" required>
<input name="phone" placeholder="Phone 097..." required>
<button>Add My Truck</button></form></div>

<div class="card"><h3>📦 I Have Goods to Move</h3>
<form action="/loads/add-form" method="post">
<input name="from_city" placeholder="From" required>
<input name="to_city" placeholder="To" required>
<input name="weight" placeholder="Weight in tonnes (e.g. 30)" type="number" step="0.1">
<input name="phone" placeholder="Phone" required>
<button>Post My Load</button></form></div>

<div class="card"><h3>Available Trucks ({truck_count})</h3>{trucks_html}</div>
<div class="card"><h3>Loads Needing Trucks ({load_count})</h3>{loads_html}</div>

<div class="card" style="text-align:center;font-size:12px;color:#94a3b8">
Mzigo Logistics | Kitwe - Lusaka - Ndola - Livingstone<br>
API: <a href="/trucks">/trucks</a> | <a href="/loads">/loads</a>
</div></body></html>
"""

def render_home(from_f="", to_f=""):
    trucks = get_trucks()
    loads = get_loads()
    
    # filter
    if from_f: trucks = [t for t in trucks if from_f.lower() in (t.get('from_city','') or '').lower()]
    if to_f: trucks = [t for t in trucks if to_f.lower() in (t.get('to_city','') or '').lower()]
    
    trucks_html = ""
    for t in trucks[:20]:
        trucks_html += f"<div class='truck'>🚛 {t.get('from_city')} → {t.get('to_city')}<br>📞 {t.get('phone')} <a href='tel:{t.get('phone')}'><button style='width:auto;padding:5px 10px'>Call</button></a></div>"
    if not trucks_html: trucks_html = "<p>No trucks yet - be the first!</p>"

    loads_html = ""
    for l in loads[:20]:
        loads_html += f"<div class='truck' style='border-left-color:#f59e0b'>📦 {l.get('from_city')} → {l.get('to_city')} {l.get('weight','')}T<br>📞 {l.get('phone')}</div>"
    if not loads_html: loads_html = "<p>No loads yet.</p>"

    db_status = "🟢 SUPABASE CONNECTED - Forever" if supabase else "🔴 MEMORY MODE - Add keys in Render"
    
    return HTML.format(
        db_status=db_status, from_f=from_f, to_f=to_f,
        truck_count=len(trucks), load_count=len(loads),
        trucks_html=trucks_html, loads_html=loads_html
    )

@app.get("/", response_class=HTMLResponse)
def home(from_city: str = "", to_city: str = ""):
    return render_home(from_city, to_city)

@app.post("/trucks/add-form")
def add_truck_form(from_city: str = Form(...), to_city: str = Form(...), phone: str = Form(...)):
    if supabase:
        supabase.table("trucks").insert({"from_city": from_city, "to_city": to_city, "phone": phone}).execute()
    return RedirectResponse("/", status_code=303)

@app.post("/loads/add-form")
def add_load_form(from_city: str = Form(...), to_city: str = Form(...), weight: float = Form(0), phone: str = Form(...)):
    if supabase:
        supabase.table("loads").insert({"from_city": from_city, "to_city": to_city, "weight": weight, "phone": phone}).execute()
    return RedirectResponse("/", status_code=303)

# Keep old API links working
@app.get("/trucks/add")
def add_truck_api(from_city: str, to: str = "", to_city: str = "", phone: str = ""):
    dest = to or to_city
    if supabase:
        supabase.table("trucks").insert({"from_city": from_city, "to_city": dest, "phone": phone}).execute()
        return {"status": "saved FOREVER in Supabase", "truck": {"from": from_city, "to": dest}}
    return {"status": "saved in memory"}

@app.get("/trucks")
def list_trucks():
    return {"trucks": get_trucks(), "count": len(get_trucks()), "database": "supabase" if supabase else "memory"}

@app.get("/loads")
def list_loads():
    return {"loads": get_loads(), "count": len(get_loads())}
