from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse
import uuid, os
app = FastAPI(title="MZIGO.ZM FULL UI", version="43.0")
trucks=[]; loads=[]

ZAMBIA_PROVINCES = ["Central","Copperbelt","Eastern","Luapula","Lusaka","Muchinga","Northern","North-Western","Southern","Western"]
TOWNS_KM = {("kitwe","lusaka"):362, ("lusaka","kitwe"):362, ("lusaka","ndola"):321, ("ndola","lusaka"):321, ("kitwe","ndola"):62, ("ndola","kitwe"):62, ("lusaka","kabwe"):138, ("lusaka","livingstone"):485, ("lusaka","chipata"):575, ("kitwe","solwezi"):220}

def get_dist(f,t):
 f=f.lower(); t=t.lower()
 for (a,b),km in TOWNS_KM.items():
  if a in f and b in t: return km
 return 150 if f and t else 0

STYLE="""
<style>
*{box-sizing:border-box}body{margin:0;font-family:-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif;background:#f1f5f9;color:#0f172a}
.phone{max-width:440px;margin:0 auto;background:#f1f5f9;min-height:100vh;box-shadow:0 0 40px rgba(0,0,0,.15);position:relative;padding-bottom:80px}
.hero-dark{background:#0f172a;color:#fff;padding:22px 18px 18px;border-radius:0 0 28px 28px;position:relative}
.logo{font-size:32px;font-weight:900;letter-spacing:-1px;display:flex;align-items:center;gap:8px}
.logo span{color:#22c55e}.badge{background:#22c55e;color:#000;padding:6px 14px;border-radius:999px;font
