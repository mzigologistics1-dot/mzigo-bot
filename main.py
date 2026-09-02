from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import os

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
<!DOCTYPE html>
<html><head><meta name="viewport" content="width=device-width, initial-scale=1">
<title>MZIGO.ZM</title>
<style>
body{margin:0;font-family:sans-serif;background:#f8fafc;text-align:center}
header{background:#0f172a;color:#fff;padding:20px}
.logo{font-size:32px;font-weight:900}.logo span{color:#22c55e}
.badge{background:#22c55e;color:#000;padding:6px 16px;border-radius:20px;font-weight:900;display:inline-block;margin:10px}
.container{max-width:700px;margin:0 auto;padding:20px}
.card{background:#fff;border-radius:16px;padding:20px;margin:15px;border:1px solid #e2e8f0}
.btn{padding:14px 20px;border-radius:12px;font-weight:900;text-decoration:none;display:inline-block;margin:5px}
.btn-green{background:#22c55e;color:#000}
.btn-dark{background:#0f172a;color:#fff}
</style>
</head><body>
<header>
<div class="logo">MZIGO<span>.ZM</span></div>
<div>Zambia smart logistics - No truck empty</div>
<div class="badge">ACROSS ZAMBIA</div>
<div style="font-size:12px">Central Copperbelt Eastern Luapula Lusaka Muchinga Northern North-Western Southern Western</div>
</header>
<div class="container">
<div class="card"><h2>🚛 I'm a Driver</h2><a href="/driver" class="btn btn-green">Enter Driver</a></div>
<div class="card"><h2>📦 I'm a Trader</h2><a href="/trader" class="btn btn-dark">Enter Trader</a></div>
<div class="card" style="background:#dcfce7"><h3>🤖 WhatsApp Bot Active</h3><p>MTN 0964343865 | Airtel 0976166422</p><a href="/test-bot" class="btn btn-green">Test Bot</a></div>
</div>
<div style="background:#0f172a;color:#fff;padding:15px"><b>MTN:</b> 0964343865 | <b>Airtel:</b> 0976166422</div>
</body></html>
"""

@app.get("/driver", response_class=HTMLResponse)
async def driver():
    return "<html><body><a href='/'>← Home</a><h1>Driver - Post Truck</h1><p>Form coming - V22 minimal works!</p><a href='/'>Home</a></body></html>"

@app.get("/trader", response_class=HTMLResponse)
async def trader():
    return "<html><body><a href='/'>← Home</a><h1>Trader - Post Load K30/kg</h1><p>Form coming - V22 minimal works!</p><a href='/'>Home</a></body></html>"

@app.get("/health")
async def health():
    return {"ok": True, "mtn": "0964343865", "airtel": "0976166422"}

@app.get("/whatsapp-webhook")
async def webhook_get():
    return {"status": "active", "mtn": "0964343865", "airtel": "0976166422"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
