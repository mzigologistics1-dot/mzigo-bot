from fastapi import FastAPI

app = FastAPI(title="Mzigo Logistics ZM")

_trucks = []
_loads = []

@app.get("/")
def home():
    return {
        "status": "Mzigo is LIVE",
        "message": "No Truck Returns Empty - Lusaka to Copperbelt",
        "links": {
            "quote": "/quote?from=Kitwe&to=Ndola&weight=2",
            "trucks": "/trucks"
        }
    }

@app.get("/quote")
def get_quote(from_city: str, to: str, weight: float = 1):
    prices = {("KITWE","NDOLA"): 60, ("NDOLA","KITWE"): 60, ("KITWE","LUSAKA"): 250}
    key = (from_city.upper(), to.upper())
    base = prices.get(key, 120)
    return {"from": from_city, "to": to, "kg": weight, "price_ZMW": base + weight*10}

@app.get("/trucks")
def get_trucks():
    return {"empty_trucks": _trucks}

@app.get("/loads")
def get_loads():
    return {"loads": _loads}
