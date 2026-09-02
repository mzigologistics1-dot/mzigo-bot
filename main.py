from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, PlainTextResponse
import uuid
import os

app = FastAPI()
trucks_memory = []
loads_memory = []

MTN = "0964343865"
AIRTEL = "0976166422"

STYLE = """<style>
*{box-sizing:border-box}body{margin:0;font-family:sans-serif;background:#f8fafc;color:#0f172a}
header{background:#0f172a;color:#fff;padding:18px 16px;text-align:center}
.logo{font-size:28px;font-weight:900}.logo span{color:#22c55e}
.badge-across{background:#22c55e;color:#000;padding:6px 16px;border-radius:20px;font-weight:900;font-size:12px;display:inline-block;margin:8px 0}
.provinces{font-size:10px;opacity:.8;line-height:1.6;max-width:650px;margin:8px auto 0}
.provinces span{background:#1e293b;padding:4px 10px;border-radius:12px;margin:3px;display:inline-block;border:1px solid #334155;color:#e2e8f0}
.container{max-width:700px;margin:0 auto;padding:14px}
.card{background:#fff;border-radius:18px;padding:18px;margin-bottom:14px;border:1px solid #e2e8f0;position:relative}
.btn{width:100%;padding:14px;border:none;border-radius:12px;font-weight:900;margin-top:10px;cursor:pointer;display:block;text-align:center;text-decoration:none}
.btn-green{background:#22c55e;color:#000}
.btn-dark{background:#0f172a;color:#fff}
.btn-orange{background:#f97316;color:#fff}
.btn-blue{background:#3b82f6;color:#fff}
.btn-red{background:#ef4444;color:#fff;padding:8px 14px;font-size:12px;border-radius:20px;display:inline-block;width:auto;margin-top:8px;border:none;cursor:pointer}
input,select{width:100%;padding:12px;border-radius:10px;border:1.5px solid #e2e8f0;margin-top:6px;background:#f8fafc;font-size:14px}
label{font-size:11px;font-weight:800;color:#334155;margin-top:10px;display:block;text-transform:uppercase}
.badge{font-size:11px;padding:4px 10px;border-radius:20px;font-weight:800;display:inline-block;margin:2px}
.bp{background:#0f172a;color:#fff}
.back{display:inline-block;margin-bottom:12px;background:#e2e8f0;padding:8px 14px;border-radius:20px;text-decoration:none;color:#000;font-weight:800;font-size:12px}
.small{font-size:12px;color:#64748b;margin-top:4px}
.auto-box{background:#dcfce7;border:1px dashed #22c55e;padding:10px;border-radius:10px;margin-top:8px;font-size:12px;font-weight:700;color:#14532d}
.wa{display:inline-block;margin-top:8px;background:#22c55e;color:#000;text-align:center;padding:8px 12px;border-radius:8px;text-decoration:none;font-weight:900;font-size:11px;margin-right:6px}
.wa-airtel{background:#3b82f6;color:#fff}
.price-box{background:#fff8ed;border:2px solid #f97316;border-radius:12px;padding:12px;margin-top:8px}
.delete-btn{position:absolute;top:10px;right:10px;background:#ef4444;color:#fff;border:none;border-radius:50%;width:28px;height:28px;font-weight:900;cursor:pointer}
.footer-contact{background:#0f172a;color:#fff;padding:14px;text-align:center;margin-top:20px}
.footer-contact b{color:#22c55e}
.bot-msg{background:#dcfce7;border-left:4px solid #22c55e;padding:10px;margin:8px 0;border-radius:8px;font-size:13px}
</style>"""

JS = """<script>
const towns={"lusaka":[-15.4067,28.2871],"kitwe":[-12.8024,28.2132],"ndola":[-12.9587,28.6365],"kabwe":[-14.4439,28.4506],"livingstone":[-17.8528,25.8553],"chipata":[-13.6296,32.6467],"kasama":[-10.2107,31.1749],"mansa":[-11.1998,28.8934],"mongu":[-15.2667,23.1167],"solwezi":[-12.1735,26.3865],"chingola":[-12.5256,27.8824],"choma":[-16.8112,26.9979],"mwinilunga":[-11.7357,24.4298],"nakonde":[-9.3359,32.7537]};
function haversine(lat1,lon1,lat2,lon2){const R=6371;const dLat=(lat2-lat1)*3.14159/180;const dLon=(lon2-lon1)*3.14159/180;const a=Math.sin(dLat/2)*Math.sin(dLat/2)+Math.cos(lat1*3.14159/180)*Math.cos(lat2*3.14159/180)*Math.sin(dLon/2)*Math.sin(dLon/2);return R*2*Math.atan2(Math.sqrt(a),Math.sqrt(1-a));}
async function calcDist(){const fromEl=document.getElementById('from_city');const toEl=document.getElementById('to_city');const distEl=document.getElementById('distance_km');const labelEl=document.getElementById('dist_label');const boxEl=document.getElementById('auto_box');if(!fromEl||!toEl||!distEl)return;const from=fromEl.value.toLowerCase();const to=toEl.value.toLowerCase();let fromKey=null,toKey=null;for(let k in towns){if(from.includes(k)){fromKey=k;break;}}for(let k in towns){if(to.includes(k)){toKey=k;break;}}if(!fromKey||!toKey){if(labelEl)labelEl.innerHTML="Type Zambian town";return;}if(labelEl)labelEl.innerHTML="Calculating "+fromKey+" to "+toKey+"...";const lat1=towns[fromKey][0],lon1=towns[fromKey][1],lat2=towns[toKey][0],lon2=towns[toKey][1];const straight=Math.round(haversine(lat1,lon1,lat2,lon2));try{const url="https://router.project-osrm.org/route/v1/driving/"+lon1+","+lat1+";"+lon2+","+lat2+"?overview=false";const res=await fetch(url);const data=await res.json();if(data.routes&&data.routes[0]&&data.routes[0].distance){let km=Math.round(data.routes[0].distance/1000);let h=Math.round(data.routes[0].duration/3600*10)/10;distEl.value=km+" km";if(labelEl)labelEl.innerHTML="Distance: "+km+" km";if(boxEl)boxEl.innerHTML="Distance: "+km+" km | "+h+" hrs";if(typeof calcWeightPrice==="function")calcWeightPrice();return;}}catch(e){}let est=Math.round(straight*1.38);if((fromKey=="lusaka"&&toKey=="kitwe")||(fromKey=="kitwe"&&toKey=="lusaka"))est=363;distEl.value=est+" km";if(labelEl)labelEl.innerHTML="Distance: "+est+" km";if(boxEl)boxEl.innerHTML="Distance: "+est+" km";if(typeof calcWeightPrice==="function")calcWeightPrice();}
function parseWeightKg(text){if(!text)return 0;let t=text.toLowerCase();let num=parseFloat(t.replace(/[^0-9.]/g,''));if(isNaN(num))return 0;if(t.includes("ton"))return num*1000;return num;}
function calcWeightPrice(){const weightEl=document.getElementById('weight');const rateEl=document.getElementById('rate_per_kg');const priceEl=document.getElementById('price');const priceBox=document.getElementById('price_calc_box');if(!weightEl||!rateEl||!priceEl)return;let kg=parseWeightKg(weightEl.value);let rate=parseFloat(rateEl.value)||30;if(kg>0){let total=Math.round(kg*rate);if(priceBox){priceBox.innerHTML="Weight: "+kg+" kg x K"+rate+" = <b>K"+total+"</b>";priceBox.style.display="block";}if(!priceEl.value||priceEl.dataset.auto=="1"){priceEl.value=total;priceEl.dataset.auto="1";}}}
function onWeightInput(){const p=document.getElementById('price');if(p)p.dataset.auto="1";calcWeightPrice();}
function onPriceManual(){const p=document.getElementById('price');if(p)p.dataset.auto="0";}
function confirmDelete(id){if(confirm('Are you sure you want to delete this?')){window.location.href='/delete-item/'+id;}}
</script>"""

def get_bot_menu():
    trucks_text = ""
    if trucks_memory:
        for t in trucks_memory[:3]:
            trucks_text += f"🚛 {t.get('from_city')} → {t.get('to_city')} | {t.get('distance_km')} | K{t.get('price')}\n"
    else:
        trucks_text = "No trucks available now.\n"
    return f"""MZIGO.ZM - Across Zambia
AVAILABLE TRUCKS:
{trucks_text}
WEIGHT PRICING:
K25/kg Budget
K30/kg Standard
K35/kg Express
PAYMENT:
MTN MoMo: 0964343865
Airtel Money: 0976166422
MENU:
1 - List trucks
2 - List loads
3 - Post truck
4 - Post load
5 - Payment
6 - Help
Visit: https://mzigo-bot.onrender.com
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTMLResponse("""<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Mzigo Zambia</title>""" + STYLE + """</head><body>
<header><div class="logo">MZIGO<span>.ZM</span></div><div style="font-size:12px;opacity:.8">Zambia's smart logistics platform - No truck returns empty</div><div class="badge-across">ACROSS ZAMBIA</div><div class="provinces"><span>Central</span><span>Copperbelt</span><span>Eastern</span><span>Luapula</span><span>Lusaka</span><span>Muchinga</span><span>Northern</span><span>North-Western</span><span>Southern</span><span>Western</span></div></header>
<div class="container"><div class="card" style="background:#0f172a;color:#fff"><h2 style="margin:0">🚛 I'm a Driver</h2><p style="opacity:.85;font-size:13px">Have empty truck? Post it and get loads across Zambia.</p><a href="/driver" class="btn btn-green">Enter as Driver →</a></div><div class="card" style="border:2px solid #f97316"><h2 style="margin:0">📦 I'm a Trader</h2><p class="small">Need a truck? Post your load. Weight-based K25-35/kg</p><a href="/trader" class="btn btn-dark">Enter as Trader →</a></div><div class="card" style="background:#dcfce7;border:2px solid #22c55e"><h3 style="margin:0">🤖 WhatsApp Bot Active</h3><p class="small">Auto-replies with trucks, payments, weight pricing</p><div class="bot-msg">User: "Truck?"<br>Bot: "🚛 Kitwe → Lusaka 362km | K10000 | Pay MTN 0964343865 or Airtel 0976166422"</div><a href="/whatsapp-bot" class="btn btn-green">View Bot Setup →</a><a href="/test-bot" class="btn btn-blue">Test Bot Reply</a></div></div><div class="footer-contact"><b>MTN:</b> 0964343865 | <b>Airtel:</b> 0976166422<br>WhatsApp Bot Active</div></body></html>""")

@app.get("/driver", response_class=HTMLResponse)
async def driver_screen():
    th = '<div class="card">No trucks yet - Be the first to post!</div>' if not trucks_memory else ""
    for tr in trucks_memory:
        from_c = tr.get("from_city","")
        to_c = tr.get("to_city","")
        dist = tr.get("distance_km","")
        tm = str(tr.get("departure_time",""))[:16]
        loc = tr.get("current_location","")
        typ = tr.get("truck_type","")
        price = tr.get("price","")
        lid = tr.get("local_id","")
        th += '<div class="card"><button class="delete-btn" onclick="confirmDelete(\'' + lid + '\')">X</button><b>' + from_c + ' → ' + to_c + '</b><br><span class="badge bp">' + typ + '</span><span class="badge bp">K' + str(price) + '</span><br><div class="small">📍 ' + loc + ' | 📏 ' + dist + ' | 🕒 ' + tm + '</div><a class="wa" href="https://wa.me/260964343865?text=Truck ' + from_c + ' to ' + to_c + '" target="_blank">WhatsApp MTN</a><a class="wa wa-airtel" href="https://wa.me/260976166422?text=Truck" target="_blank">WhatsApp Airtel</a><br><button class="btn-red" onclick="confirmDelete(\'' + lid + '\')">🗑 Delete</button></div>'
    return HTMLResponse("""<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Driver</title>""" + STYLE + """</head><body>
<header><div class="logo">MZIGO<span>.ZM</span> DRIVER</div><div class="badge-across">ACROSS ZAMBIA</div><div class="provinces"><span>Central</span><span>Copperbelt</span><span>Eastern</span><span>Luapula</span><span>Lusaka</span><span>Muchinga</span><span>Northern</span><span>North-Western</span><span>Southern</span><span>Western</span></div></header>
<div class="container"><a href="/" class="back">← Home</a> <a href="/trader" class="back" style="float:right">Trader →</a>
<div class="card" style="background:#0f172a;color:#fff"><h3>🚛 Post Empty Truck</h3><form action="/add-truck" method="post">
<label>From</label><input id="from_city" name="from_city" placeholder="e.g. Kitwe" required oninput="calcDist()">
<label>To</label><input id="to_city" name="to_city" placeholder="e.g. Lusaka" required oninput="calcDist()">
<label id="dist_label">Distance</label><input id="distance_km" name="distance_km" placeholder="Auto" readonly style="background:#dcfce7;font-weight:800"><div class="auto-box" id="auto_box">Enter towns to calculate distance</div>
<label>Truck Type</label><input name="truck_type" placeholder="e.g. 50 ton" required>
<label>Current Location</label><input name="current_location" placeholder="e.g. Total Sports">
<label>Set Departure Date & Time</label><input name="departure_time" type="datetime-local" required>
<label>Your Price (ZMW)</label><input name="price" placeholder="e.g. 10000" required>
<label>Your WhatsApp</label><input name="whatsapp" placeholder="e.g. 0964343865" required>
<button class="btn btn-green" type="submit">Post Truck</button>
</form></div><h3>🚛 Available Trucks (""" + str(len(trucks_memory)) + """)</h3>""" + th + """</div><div class="footer-contact"><b>MTN:</b> 0964343865 | <b>Airtel:</b> 0976166422</div>""" + JS + """</body></html>""")

@app.get("/trader", response_class=HTMLResponse)
async def trader_screen():
    lh = '<div class="card">No loads yet</div>' if not loads_memory else ""
    for tr in loads_memory:
        from_c = tr.get("from_city","")
        to_c = tr.get("to_city","")
        goods = tr.get("goods_type","")
        w = tr.get("weight","")
        dist = tr.get("distance_km","")
        price = tr.get("price","")
        rate = tr.get("rate_per_kg","30")
        lid = tr.get("local_id","")
        lh += '<div class="card"><button class="delete-btn" onclick="confirmDelete(\'' + lid + '\')">X</button><b>' + from_c + ' → ' + to_c + '</b><br><span class="badge">' + goods + ' ' + w + '</span> <span class="badge" style="background:#dcfce7">📏 ' + dist + '</span><br><span class="badge bp">K' + str(price) + ' (K' + str(rate) + '/kg)</span><br><a class="wa" href="https://wa.me/260964343865?text=Load" target="_blank">WhatsApp MTN</a><a class="wa wa-airtel" href="https://wa.me/260976166422?text=Load" target="_blank">WhatsApp Airtel</a><br><button class="btn-red" onclick="confirmDelete(\'' + lid + '\')">🗑 Delete</button></div>'
    return HTMLResponse("""<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Trader</title>""" + STYLE + """</head><body>
<header><div class="logo">MZIGO<span>.ZM</span> TRADER</div><div class="badge-across">ACROSS ZAMBIA</div><div class="provinces"><span>Central</span><span>Copperbelt</span><span>Eastern</span><span>Luapula</span><span>Lusaka</span><span>Muchinga</span><span>Northern</span><span>North-Western</span><span>Southern</span><span>Western</span></div></header>
<div class="container"><a href="/" class="back">← Home</a> <a href="/driver" class="back" style="float:right">Driver →</a>
<div class="card" style="border:2px solid #f97316"><h3>📦 Post Load</h3><form action="/add-load" method="post">
<label>From</label><input id="from_city" name="from_city" placeholder="e.g. Lusaka" required oninput="calcDist()">
<label>To</label><input id="to_city" name="to_city" placeholder="e.g. Ndola" required oninput="calcDist()">
<label id="dist_label">Distance</label><input id="distance_km" name="distance_km" placeholder="Auto" readonly style="background:#dcfce7;font-weight:800"><div class="auto-box" id="auto_box">Enter towns to calculate distance</div>
<label>Goods Type</label><input name="goods_type" placeholder="e.g. Maize" required>
<label>Weight</label><input id="weight" name="weight" placeholder="e.g. 1000 kg or 1.5 tons" required oninput="onWeightInput()">
<label>Rate per kg</label><select id="rate_per_kg" name="rate_per_kg" onchange="calcWeightPrice()"><option value="25">K25/kg</option><option value="30" selected>K30/kg</option><option value="35">K35/kg</option><option value="50">K50/kg</option></select><div id="price_calc_box" class="price-box" style="display:none">Enter weight</div>
<label>Set Date & Time</label><input name="departure_time" type="datetime-local" required>
<label>Total Budget</label><input id="price" name="price" placeholder="Auto from weight" required oninput="onPriceManual()" data-auto="1">
<label>WhatsApp</label><input name="whatsapp" placeholder="e.g. 0964343865" required>
<button class="btn btn-orange" type="submit">Post Load</button>
</form></div><h3>📦 Available Loads (""" + str(len(loads_memory)) + """)</h3>""" + lh + """</div><div class="footer-contact"><b>MTN:</b> 0964343865 | <b>Airtel:</b> 0976166422</div>""" + JS + """</body></html>""")

@app.get("/whatsapp-bot", response_class=HTMLResponse)
async def whatsapp_bot_page():
    return HTMLResponse("""<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>WhatsApp Bot</title>""" + STYLE + """</head><body>
<header><div class="logo">MZIGO<span>.ZM</span> WHATSAPP BOT</div><div class="badge-across">BOT ACTIVE</div><div class="provinces"><span>Central</span><span>Copperbelt</span><span>Eastern</span><span>Luapula</span><span>Lusaka</span><span>Muchinga</span><span>Northern</span><span>North-Western</span><span>Southern</span><span>Western</span></div></header>
<div class="container"><a href="/" class="back">← Home</a>
<div class="card"><h3>🤖 WhatsApp Bot - How It Works</h3><div class="bot-msg"><b>User:</b> "Truck?"<br><b>Bot:</b> "🚛 Kitwe → Lusaka 362km | K10000 | Pay MTN 0964343865 or Airtel 0976166422"</div>
<h4>Works NOW - No setup:</h4><p class="small">Your buttons "WhatsApp MTN" open WhatsApp with payment message. That's the bot!<br><br><b>For full auto-reply:</b> Set webhook in Twilio to<br><code>https://mzigo-bot.onrender.com/whatsapp-webhook</code></p>
<div class="card" style="background:#fff8ed"><b>Bot Commands:</b><br>- "truck" or "1" = List trucks<br>- "load" or "2" = List loads<br>- "pay" or "5" = Payment MTN 0964343865 | Airtel 0976166422<br>- "price" = Weight K25-35/kg</div>
<a href="/test-bot?msg=truck" class="btn btn-green">Test Bot: Send "truck"</a><a href="/test-bot?msg=pay" class="btn btn-blue">Test Bot: Payment</a></div></div><div class="footer-contact"><b>MTN:</b> 0964343865 | <b>Airtel:</b> 0976166422 | Webhook: /whatsapp-webhook</div></body></html>""")

@app.get("/test-bot", response_class=HTMLResponse)
async def test_bot(msg: str = "truck"):
    reply = handle_whatsapp_message(msg)
    return HTMLResponse("""<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Bot Test</title>""" + STYLE + """</head><body>
<header><div class="logo">MZIGO<span>.ZM</span> BOT TEST</div></header>
<div class="container"><a href="/whatsapp-bot" class="back">← Bot Setup</a>
<div class="card"><h3>🤖 Bot Test</h3><p class="small">You sent: <b>""" + msg + """</b></p><div class="bot-msg" style="white-space:pre-wrap">""" + reply + """</div>
<form action="/test-bot" method="get" style="margin-top:12px"><input name="msg" placeholder="Type truck, pay, help..." value=\"""" + msg + """\"><button class="btn btn-green" type="submit">Send to Bot</button></form>
</div></div></body></html>""")

def handle_whatsapp_message(incoming_msg: str) -> str:
    msg = incoming_msg.lower().strip()
    if msg in ["1", "truck", "trucks", "available", "truck?"]:
        if not trucks_memory:
            return "No trucks now. Post at https://mzigo-bot.onrender.com/driver\n\nPayment: MTN 0964343865 | Airtel 0976166422"
        text = "AVAILABLE TRUCKS ACROSS ZAMBIA:\n\n"
        for t in trucks_memory[:5]:
            text += f"{t.get('from_city')} -> {t.get('to_city')} | {t.get('distance_km')} | K{t.get('price')}\n"
        text += "\nPay: MTN 0964343865 | Airtel 0976166422\nReply 3 to post truck"
        return text
    elif msg in ["2", "load", "loads"]:
        if not loads_memory:
            return "No loads. Post at https://mzigo-bot.onrender.com/trader\nWeight: K25-35/kg"
        text = "AVAILABLE LOADS:\n\n"
        for l in loads_memory[:5]:
            text += f"{l.get('from_city')} -> {l.get('to_city')} | {l.get('weight')} | K{l.get('price')}\n"
        return text
    elif msg in ["5", "pay", "payment"]:
        return "PAYMENT:\n\nMTN MoMo: 0964343865\nAirtel Money: 0976166422\nName: Josiah Mwape\n\nSend screenshot after payment."
    elif "price" in msg or "kg" in msg:
        return "WEIGHT PRICING:\nK25/kg Budget\nK30/kg Standard\nK35/kg Express\nK50/kg Urgent\nExample: 1000kg x K30 = K30000\nPay: MTN 0964343865 | Airtel 0976166422"
    else:
        return get_bot_menu()

@app.post("/whatsapp-webhook")
async def whatsapp_webhook(request: Request):
    try:
        form = await request.form()
        incoming_msg = form.get("Body", "") or form.get("body", "") or ""
        reply_text = handle_whatsapp_message(incoming_msg)
        twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
<Message>{reply_text}</Message>
</Response>"""
        ret
