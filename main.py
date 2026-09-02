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

PAGE = '''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mzigo ZM - Marketplace</title>
<style>
*{box-sizing:border-box}body{margin:0;font-family:sans-serif;background:#f8fafc;color:#0f172a}
header{background:#0f172a;color:#fff;padding:18px 16px;position:sticky;top:0;z-index:10}
.header-inner{max-width:750px;margin:0 auto;display:flex;justify-content:space-between;align-items:center}
.logo{font-weight:900;font-size:20px}.logo span{color:#22c55e}
.live{font-size:11px;background:#22c55e;color:#000;padding:4px 10px;border-radius:20px;font-weight:800}
.container{max-width:750px;margin:0 auto;padding:16px}
.tabs{display:flex;gap:8px;margin:16px 0;background:#e2e8f0;padding:5px;border-radius:14px}
.tab{flex:1;padding:12px;text-align:center;border-radius:10px;font-weight:800;cursor:pointer;border:none;background:transparent}
.tab.active{background:#0f172a;color:#fff}
.post-card{background:#fff;border-radius:20px;padding:20px;box-shadow:0 8px 30px rgba(0,0,0,.06);border:1px solid #e2e8f0;margin-bottom:16px}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:10px}
@media(max-width:500px){.grid2{grid-template-columns:1fr}}
input{width:100%;padding:14px;border-radius:12px;border:1.5px solid #e2e8f0;font-size:15px;background:#f8fafc}
.btn{width:100%;background:#0f172a;color:#fff;padding:15px;border:none;border-radius:12px;font-weight:800;margin-top:12px;cursor:pointer}
.btn-green{background:#22c55e;color:#000}
.count{background:#0f172a;color:#fff;padding:4px 10px;border-radius:20px;font-size:12px;font-weight:800}
.card{background:#fff;border-radius:18px;padding:16px;margin-bottom:12px;border:1px solid #e2e8f0;overflow:hidden;position:relative}
.route{display:flex;align-items:center;flex-wrap:wrap;gap:6px;font-weight:900;font-size:16px;padding-right:30px}
.route .city{background:#f1f5f9;padding:4px 10px;border-radius:8px;max-width:100%;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.meta{margin-top:12px;display:flex;flex-wrap:wrap;gap:8px}
.tag{padding:6px 12px;border-radius:20px;font-size:12.5px;border:1px solid #e2e8f0;background:#f8fafc;max-width:100%}
.tag.green{background:#dcfce7;color:#14532d}
.tag.dark{background:#0f172a;color:#fff}
.tag.orange{background:#ffedd5;color:#9a3412}
.wa{display:block;margin-top:14px;background:#22c55e;color:#000;text-align:center;padding:12px;border-radius:12px;text-decoration:none;font-weight:900}
.wa-blue{background
