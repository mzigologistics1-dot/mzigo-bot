from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse
import uuid, os

app = FastAPI()
trucks = []
loads = []

MTN="0964343865"
AIRTEL="0976166422"
MTN_NAME="MWNSA MULENGA"
AIRTEL_NAME="PRAISBE MWAPE"

@app.get("/", response_class=HTMLResponse)
async def home():
    return f"""
<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>MZIGO.ZM</title>
<style>
*{{box-sizing:border-box}}
body{{margin:0;font-family:-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif;background:#f1f5f9;color:#0f172a}}
header{{background:#0f172a;color:#fff;padding:22px 16px;text-align:center;position:sticky;top:0;z-index:10}}
.logo{{font-size:34px;font-weight:900;letter-spacing:-1px}}.logo span{{color:#22c55e}}
.sub{{font-size:13px;opacity:.8;margin-top:4px}}
.badge{{background:#22c55e;color:#000;padding:6px 16px;border-radius:999px;font-weight:900;font-size:12px;margin:12px auto;display:inline-block}}
.provinces{{display:flex;flex-wrap:wrap;justify-content:center;gap:5px;margin-top:10px}}
.provinces span{{background:#1e293b;color:#cbd5e1;padding:4px 10px;border-radius:999px;font-size:10px;border:1px solid #334155}}
.container{{max-width:720px;margin:0 auto;padding:16px}}
.card{{background:#fff;border-radius:20px;padding:22px;margin:14px 0;border:1px solid #e2e8f0;box-shadow:0 4px 20px rgba(0,0,0,.04)}}
.card-dark{{background:#0f172a;color:#fff;border:none}}
.card-orange{{border:2px solid #f97316}}
.card-green{{background:#f0fdf4;border:2px solid #22c55e}}
.btn{{width:100%;padding:14px;border:none;border-radius:12px;font-weight:900;font-size:15px;margin-top:12px;display:block;text-align:center;text-decoration:none;cursor:pointer;transition:.2s}}
.btn-green{{background:#22c55e;color:#000}}.btn-green:hover{{background:#16a34a}}
.btn-dark{{background:#0f172a;color:#fff}}.btn-dark:hover{{background:#1e293b}}
h2{{margin:0 0 6px 0;font-size:20px}}p{{margin:0;color:#64748b;font-size:13px;line-height:1.4}}
.pay-row{{display:flex;gap:10px;margin-top:10px}}
.pay-box{{flex:1;background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:10px;text-align:center;font-size:12px}}
.pay-box b{{display:block;color:#0f172a;font-size:13px}}
.footer{{background:#0f172a;color:#94a3b8;padding:16px;text-align
