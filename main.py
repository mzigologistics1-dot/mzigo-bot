from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse
import uuid, os, math

app = FastAPI(title="MZIGO.ZM - Aesthetic 1000", version="40.0")
trucks = []
loads = []

MTN = "0964343865"
AIRTEL = "0976166422"
MTN_NAME = "MWNSA MULENGA"
AIRTEL_NAME = "PRAISBE MWAPE"

def calc_road(a,b):
    a=a.lower(); b=b.lower()
    if "kitwe" in a and "lusaka" in b: return 363
    if "lusaka" in a and "kitwe" in b: return 363
    if "lusaka" in a and "ndola" in b: return 321
    if "kitwe" in a and "ndola" in b: return 62
    return 120

@app.get("/", response_class=HTMLResponse)
async def home():
    return """<html>... (FULL CODE IN FILE ABOVE - USE DOWNLOAD) ...</html>"""
# ... rest of driver/trader in file
