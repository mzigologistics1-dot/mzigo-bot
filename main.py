from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Mzigo")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

TRUCKS = [
    {"id":1,"from":"Kitwe","to":"Lusaka","type":"10 Ton","km":362,"depart":"Today 5:30 PM","price":22000,"space":"8 ton","rating":4.8,"empty":True,"driver":"J M","trips":127},
]
ORDERS = [
    {"id":"MZ-1023","from":"Kitwe","to":"Lusaka","type":"10 Ton","price":22000,"status":"In Transit","progress":60},
]
# Full App: AUTH + ORDERS + PROFILE + DRAWER - 409 LINES - YELLOW WHITE
