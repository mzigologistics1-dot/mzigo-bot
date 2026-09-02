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
        print("✅ Supabase connected")
except Exception as e:
    print(f"❌ Supabase failed: {e}")

app = FastAPI()
trucks_memory = []

PAGE_HEAD = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mzigo Logistics ZM</title>
<style>
*{box-sizing:border-box}
body{margin:0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#f8fafc;color:#0f172a}
header{background:#0f172a;color:#fff;padding:18px 16px;position:sticky;top:0;z-index:10}
.header-inner{max-width:700px;margin:0 auto;display:flex;justify-content:space-between;align-items:center}
.logo{font-weight:900;font-size:20px}.logo span{color:#22c55e}
.tagline{font-size:11px;letter-spacing:2px;opacity:.6;margin-top:2px}
.live{font-size:11px;background:#22c55e;color:#000;padding:4px 10px;border-radius:20px;font-weight:800}
.container{max-width:700px;margin:0 auto;padding:16px}
.post-card{background:#fff;border-radius:20px;padding:20px;box-shadow:0 8px 30px rgba(0,0,0,.06);border:1px solid #e2e8f0}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:10px}
@media(max-width:500px){.grid2{grid-template-columns:1fr}}
input{width:100%;padding:14px;border-radius:12px;border:1.5px solid #e2e8f0;font-size:15px;background:#f8fafc}
.btn{width:100%;background:#0f172a;color:#fff;padding:15px;border:none;border-radius:12px;font-weight:800;margin-top:12px;cursor:pointer}
.count{background:#0f172a;color:#fff;padding:4px 10px;border-radius:20px;font-size:12px;font-weight:800}
.truck-card{background:#fff;border-radius:18px;padding:
