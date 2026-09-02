from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse
import uuid, os

app = FastAPI()
trucks = []
loads = []

MTN = "0964343865"
AIRTEL = "0976166422"
MTN_NAME = "MWNSA MULENGA"
AIRTEL_NAME = "PRAISBE MWAPE"

@app.get("/", response_class=HTMLResponse)
async def home():
    return f"""
<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>MZIGO.ZM - Zambia Logistics</title>
<style>
body{{margin:0;font-family:sans-serif;background:#f8fafc}}
header{{background:#0f172a;color:#fff;padding:20px;text-align:center}}
.logo{{font-size:32px;font-weight:900}}.logo span{{color:#22c55e}}
.badge{{background:#22c55e;color:#000;padding:6px 16px;border-radius:20px;font-weight:900;display:inline-block;margin:10px}}
.provinces{{font-size:11px;opacity:.8}}.provinces span{{background:#1e293b;padding:4px 8px;border-radius:10px;margin:2px;display:inline-block}}
.container{{max-width:700px;margin:0 auto;padding:15px}}
.card{{background:#fff;border-radius:16px;padding:20px;margin:12px 0;border:1px solid #e2e8f0}}
.btn{{width:100%;padding:14px;border:none;border-radius:12px;font-weight:900;margin-top:10px;display:block;text-align:center;text-decoration:none;cursor:pointer}}
.btn-green{{background:#22c55e;color:#000}}
.btn-dark{{background:#0f172a;color:#fff}}
.footer{{background:#0f172a;color:#fff;padding:15px;text-align:center;margin-top:20px;font-size:12px}}.footer b{{color:#22c55e}}
</style></head><body>
<header>
<div class="logo">MZIGO<span>.ZM</span></div>
<div>Zambia's smart logistics - No truck returns empty</div>
<div class="badge">ACROSS ZAMBIA</div>
<div class="provinces">
<span>Central</span><span>Copperbelt</span><span>Eastern</span><span>Luapula</span><span>Lusaka</span>
<span>Muchinga</span><span>Northern</span><span>North-Western</span><span>Southern</span><span>Western
