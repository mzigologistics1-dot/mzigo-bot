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
loads_memory = []
MTN = "0970000000"
PCT = 30
def calc(s):
    try:
        b = int("".join([c for c in str(s) if c.isdigit()]) or 0)
        return b, b*PCT//100, b + b*PCT//100
    except:
        return 0,0,s

HTML = """<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"><title>Mzigo ACROSS ZAMBIA</title><style>body{margin:0;font-family:sans-serif;background:#f8fafc}header{background:#0f172a;color:#fff;padding:20px;text-align:center}.across{background:#22c55e;color:#000;padding:4px 12px;border-radius:20px;font-weight:900;font-size:12px;display:inline-block;margin-top:8px}.container{max-width:800px;margin:0 auto;padding:14px}.card{background:#fff;border-radius:16px;padding:14px;margin-bottom:10px;border:1px solid #e2e8f0}.badge{font-size:11px;padding:4px 8px;border-radius:20px;font-weight:800;display:inline-block;margin:2px}.bp{background:#0f172a;color:#fff}.bf{background:#fef3c7}.btn{width:100%;background:#0f172a;color:#fff;padding:12px;border:none;border-radius:10px;font-weight:800;margin-top:8px}.wa{display:block;margin-top:8px;background:#22c55e;text-align:center;padding:10px;border-radius:8px;text-decoration:none;color:#000;font-weight:800}</style></head><body><header><div style="font-size:26px;font-weight:900">MZIGO<span style="color:#22c55e">.ZM</span></div><div class="across">ACROSS ZAMBIA • FIXED 30%</div><div style="font-size:10px;opacity:.6;margin-top:4px">Kitwe Lusaka Ndola Solwezi Mwinilunga Nakonde Livingstone</div></header><div class="container"><h3>🚛 Post Truck ACROSS ZAMBIA</h3><form action="/add-truck" method="post"><input name="from_city" placeholder="From - Across Zambia" required style="width:100%;padding:10px;margin-top:6px"><input name="to_city" placeholder="To - Across Zambia" required style="width:100%;padding:10px;margin-top:6px"><input name="truck_type" placeholder="30 Ton" required style="width:100%;padding:10px;margin-top:6px"><input name="price" placeholder="Your Price K 15000" required style="width:100%;padding:10px;margin-top:6px"><input name="whatsapp" placeholder="WhatsApp" required style="width:100%;padding:10px;margin-top:6px"><button class="btn" type="submit">Post ACROSS ZAMBIA</button></form><div style="margin-top:14px">HTRUCKS</div><h3>📦 Post Load ACROSS ZAMBIA</h3><form action="/add-load" method="post"><input name="from_city" placeholder="From" required style="width:100%;padding:10px;margin-top:6px"><input name="to_city" placeholder="To" required style="width:100%;padding:10px;margin-top:6px"><input name="goods_type" placeholder="Maize" required style="width:100%;padding:10px;margin-top:6px"><input name="weight" placeholder="15 Tons" required style="width:100%;padding:10px;margin-top:6px"><input name="price" placeholder="Budget K" required style="width:100%;padding:10px;margin-top:6px"><input name="whatsapp" placeholder="WhatsApp" required style="width:100%;padding:10px;margin-top:6px"><button class="btn" style="background:#f97316" type="submit">Post Load</button></form><div style="margin-top:14px">HLOADS</div></div></body></html>"""

def get_trucks():
    if supabase:
        try: return supabase.table("trucks").select("*").order("created_at", desc=True).execute().data
        except: return trucks_memory
    return trucks_memory
def get_loads():
    if supabase:
        try: return supabase.table("loads").select("*").order("created_at", desc=True).execute().data
        except: return loads_memory
    return loads_memory

@app.get("/", response_class=HTMLResponse)
async def home():
    trucks = get_trucks()
    loads = get_loads()
    th = "" if trucks else '<div class="card">No trucks ACROSS ZAMBIA yet</div>'
    for tr in trucks:
        b,f,t = calc(tr.get("price","0"))
        th += f'<div class="card"><b>{tr.get("from_city","")} → {tr.get("to_city","")}</b> <span class="badge" style="background:#22c55e">ACROSS ZAMBIA</span><br><span class="badge bp">Driver K{b}</span><span class="badge bf">30% K{f}</span><span class="badge bp">Pays K{t}</span><br><div style="background:#ffeb3b;padding:6px;border-radius:6px;margin-top:6px;font-weight:800">MTN MoMo K{t} → {MTN} | Profit K{f}</div><a class="wa" href="https://wa.me/260970000000">Contact via Bot</a></div>'
    lh = "" if loads else '<div class="card">No loads ACROSS ZAMBIA</div>'
    for ld in loads:
        lh += f'<div class="card"><b>{ld.get("from_city","")} → {ld.get("to_city","")}</b><br>{ld.get("goods_type","")} {ld.get("weight","")} K{ld.get("price","")}<br><a class="wa" style="background:#0f172a;color:#fff" href="https://wa.me/260970000000">I Have Truck ACROSS ZAMBIA</a></div>'
    return HTMLResponse(HTML.replace("HTRUCKS", th).replace("HLOADS", lh))

@app.post("/add-truck")
async def add_truck(from_city: str = Form(...), to_city: str = Form(...), truck_type: str = Form(...), price: str = Form(...), whatsapp: str = Form(...)):
    data = {"from_city": from_city.strip(), "to_city": to_city.strip(), "truck_type": truck_type.strip(), "price": price.strip(), "whatsapp": whatsapp.strip()}
    if supabase:
        try: supabase.table("trucks").insert(data).execute()
        except: pass
    else: trucks_memory.append(data)
    return RedirectResponse("/", status_code=303)

@app.post("/add-load")
async def add_load(from_city: str = Form(...), to_city: str = Form(...), goods_type: str = Form(...), weight: str = Form(...), price: str = Form(...), whatsapp: str = Form(...)):
    data = {"from_city": from_city.strip(), "to_city": to_city.strip(), "goods_type": goods_type.strip(), "weight": weight.strip(), "price": price.strip(), "whatsapp": whatsapp.strip()}
    if supabase:
        try: supabase.table("loads").insert(data).execute()
        except: pass
    else: loads_memory.append(data)
    return RedirectResponse("/", status_code=303)
