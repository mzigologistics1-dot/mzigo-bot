from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, PlainTextResponse
import uuid
import os

app = FastAPI()
trucks_memory = []
loads_memory = []

MTN = "0964343865"
AIRTEL = "0976166422"

# ... (STYLE + JS + all routes same as V19 - clean, no changelog) ...

@app.get("/health")
async def health():
    return {"ok": True}

# CRITICAL FIX FOR RENDER - AUTO PORT BINDING
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
