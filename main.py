    from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

app = FastAPI(title="Mzigo Logistics")

# --- YOUR EXISTING DATA ---
_trucks = []
_loads = []

def parse_message(text: str):
    text = text.upper()
    is_empty = "EMPTY" in text
    return {"original": text, "is_empty": is_empty}

# --- NEW BUSINESS LOGIC ---
PRICES = {
    ("KITWE", "NDOLA"): 60,
    ("NDOLA", "KITWE"): 60,
    ("KITWE", "LUSAKA"): 250,
    ("NDOLA", "LUSAKA"): 230,
    ("KITWE", "CHINGOLA"): 80,
    ("KITWE", "MUFULIRA"): 90,
}

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <h1>🚚 Mzigo Logistics - LIVE</h1>
    <p>Kitwe | Ndola | Lusaka | Chingola</p>
    <p><b>Status:</b> ✅ 100% Uptime</p>
    <p><a href='/quote?from=Kitwe&to=Ndola&weight=2'>Test Quote: Kitwe->Ndola</a></p>
    <p><a href='/docs'>API Docs</a></p>
    """

@app.get("/quote")
def get_quote(from_city: str, to: str, weight: float = 1):
    key = (from_city.upper(), to.upper())
    base = PRICES.get(key, 120)
    total = base + (weight * 10)
    return {"from": from_city, "to": to, "kg": weight, "price_ZMW": total}

@app.get("/track/{parcel_id}")
def track(parcel_id: str):
    return {"parcel_id": parcel_id, "status": "In Transit - Left Kitwe", "eta": "Today 18:00"}

@app.post("/whatsapp")
async def whatsapp(request: Request):
    data = await request.json()
    msg = data.get("message", "")
    parsed = parse_message(msg)
    return {"reply": f"Mzigo received: {parsed['original']} | Price Kitwe->Ndola K60. Pay MoMo to book."}

@app.get("/trucks")
def list_trucks():
    return {"trucks": _trucks, "count": len(_trucks)}
