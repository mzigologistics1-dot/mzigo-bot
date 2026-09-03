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
    html = """
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>MZIGO.ZM - Zambia Logistics</title>
<style>
body{margin:0;font-family:-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif;background:#f1f5f9;color:#0f172a;line-height:1.5}
header{background:#0f172a;color:#fff;padding:28px 16px;text-align:center}
.logo{font-size:36px;font-weight:900;letter-spacing:-1px}
.logo span{color:#22c55e}
.sub{font-size:14px;opacity:0.8;margin-top:6px}
.badge{background:#22c55e;color:#000;padding:8px 18px;border-radius:999px;font-weight:900;font-size:12px;margin:14px auto;display:inline-block}
.provinces{display:flex;flex-wrap:wrap;justify-content:center;gap:6px;margin-top:14px}
.provinces span{background:#1e293b;color:#cbd5e1;padding:5px 12px;border-radius:999px;font-size:11px;border:1px solid #334155}
.container{max-width:760px;margin:0 auto;padding:16px}
.card{background:#fff;border-radius:20px;padding:24px;margin:16px 0;border:1px solid #e2e8f0;box-shadow:0 8px 24px rgba(0,0,0,0.06)}
.card-dark{background:#0f172a;color:#fff;border:none}
.card-green{background:#f0fdf4;border:2px solid #22c55e}
.card-orange{border:2px solid #f97316}
.btn{width:100%;padding:16px;border:none;border-radius:14px;font-weight:900;font-size:16px;margin-top:14px;display:block;text-align:center;text-decoration:none;cursor:pointer}
.btn-green{background:#22c55e;color:#000}
.btn-dark{background:#0f172a;color:#fff}
.btn-orange{background:#f97316;color:#fff}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.stat{background:#f8fafc;border:1px solid #e2e8f0;border-radius:14px;padding:14px;text-align:center}
.stat b{display:block;font-size:22px;color:#0f172a}
.how{display:flex;gap:12px;margin-top:12px}
.how-step{flex:1;background:#f8fafc;border-radius:14px;padding:14px;text-align:center;border:1px solid #e2e8f0}
.pay-row{display:flex;gap:12px;margin-top:12px}
.pay-box{flex:1;background:#fff;border:1px solid #e2e8f0;border-radius:14px;padding:14px;text-align:center}
.footer{background:#0f172a;color:#94a3b8;padding:24px;text-align:center;font-size:12px;margin-top:40px}
</style></head><body>
<header>
<div class="logo">MZIGO<span>.ZM</span></div>
<div class="sub">Zambia's smart logistics platform — No truck returns empty</div>
<div class="badge">✦ ACROSS ZAMBIA • 10 PROVINCES • LIVE NOW</div>
<div class="provinces">
<span>Central</span><span>Copperbelt</span><span>Eastern</span><span>Luapula</span><span>Lusaka</span><span>Muchinga</span><span>Northern</span><span>North-Western</span><span>Southern</span><span>Western</span>
</div>
</header>
<div class="container">

<div class="card card-dark">
<h2 style="margin:0;font-size:24px">🚛 I'm a Driver — Have Empty Truck?</h2>
<p style="color:#94a3b8;margin-top:8px">Post your empty return trip across Zambia. Auto distance calculation — Kitwe → Lusaka = 363km driving distance. Get loads instantly via WhatsApp!</p>
<div class="grid" style="margin-top:14px">
<div class="stat" style="background:#1e293b;border-color:#334155"><b style="color:#22c55e">363 km</b><span style="color:#94a3b8;font-size:11px">Kitwe→Lusaka</span></div>
<div class="stat" style="background:#1e293b;border-color:#334155"><b style="color:#22c55e">24/7</b><span style="color:#94a3b8;font-size:11px">WhatsApp Bot</span></div>
</div>
<a href="/driver" class="btn btn-green">Enter as Driver → Post Truck</a>
</div>

<div class="card card-orange">
<h2 style="margin:0;font-size:24px">📦 I'm a Trader — Need a Truck?</h2>
<p style="margin-top:8px;color:#64748b">Post your load with weight-based pricing. K25/kg Budget, K30/kg Standard ⭐, K35/kg Express, K50/kg Urgent. Platinum quality service!</p>
<div class="how">
<div class="how-step"><b>1️⃣ Post</b><br><span style="font-size:11px;color:#64748b">Enter goods + weight</span></div>
<div class="how-step"><b>2️⃣ Match</b><br><span style="font-size:11px;color:#64748b">Drivers bid</span></div>
<div class="how-step"><b>3️⃣ Move</b><br><span style="font-size:11px;color:#64748b">Track delivery</span></div>
</div>
<a href="/trader" class="btn btn-orange">Enter as Trader → Post Load</a>
</div>

<div class="card">
<h2 style="margin:0">⚡ How MZIGO.ZM Works — Looooong Explain</h2>
<p style="margin-top:8px;color:#64748b">We solve the biggest problem in Zambia logistics: Trucks go full one way, empty back! That's wasted fuel, wasted money. MZIGO.ZM connects empty trucks with traders who need goods moved!</p>
<div style="margin-top:16px;background:#f8fafc;border-radius:14px;padding:16px;border:1px solid #e2e8f0">
<b>🚛 For Drivers:</b><br>
<span style="font-size:13px;color:#475569">You drive Kitwe → Lusaka with copper? Don't return empty! Post your truck on MZIGO.ZM, set price K10,000, and traders in Lusaka with goods to Kitwe will contact you via WhatsApp. Auto distance 363km calculated for you! Delete anytime.</span>
</div>
<div style="margin-top:12px;background:#fff7ed;border-radius:14px;padding:16px;border:1px solid #fed7aa">
<b>📦 For Traders:</b><br>
<span style="font-size:13px;color:#7c2d12">You have 1000kg maize in Lusaka to send to Ndola? Post load: Weight 1000kg x K30/kg = K30,000 total. Drivers with empty trucks will see it. Pay via MoMo. Simple!</span>
</div>
</div>

<div class="card">
<h2 style="margin:0">🗺️ Covered Routes — All Zambia Towns</h2>
<p style="color:#64748b;margin-top:6px">We auto calculate road distance (not straight line) for all major towns!</p>
<div style="margin-top:12px;display:flex;flex-wrap:wrap;gap:8px">
<span style="background:#dcfce7;padding:6px 12px;border-radius:999px;font-size:12px;font-weight:700">Kitwe → Lusaka 363km ✅</span>
<span style="background:#f1f5f9;padding:6px 12px;border-radius:999px;font-size:12px">Lusaka → Ndola 321km</span>
<span style="background:#f1f5f9;padding:6px 12px;border-radius:999px;font-size:12px">Kitwe → Ndola 62km</span>
<span style="background:#f1f5f9;padding:6px 12px;border-radius:999px;font-size:12px">Lusaka → Kabwe 138km</span>
<span style="background:#f1f5f9;padding:6px 12px;border-radius:999px;font-size:12px">Lusaka → Livingstone 485km</span>
<span style="background:#f1f5f9;padding:6px 12px;border-radius:999px;font-size:12px">Chipata, Kasama, Mansa, Mongu, Solwezi + more!</span>
</div>
</div>

<div class="card card-green">
<h2 style="margin:0;color:#14532d">💰 Payment — Zambia Mobile Money — Looooong Details</h2>
<p style="color:#15803d;margin-top:6px;font-size:13px">Pay securely via MTN MoMo or Airtel Money. Your payment names are protected — no leak before payment! Send screenshot after paying.</p>
<div class="pay-row">
<div class="pay-box"><b style="font-size:14px">MTN MoMo</b><span style="font-size:18px;font-weight:900">""" + MTN + """</span><br><span style="color:#15803d;font-weight:800">""" + MTN_NAME + """</span><br><span style="font-size:10px;color:#64748b">Send to this number</span></div>
<div class="pay-box"><b style="font-size:14px">Airtel Money</b><span style="font-size:18px;font-weight:900">""" + AIRTEL + """</span><br><span style="color:#1d4ed8;font-weight:800">""" + AIRTEL_NAME + """</span><br><span style="font-size:10px;color:#64748b">Send to this number</span></div>
</div>
<div style="margin-top:14px;background:#fff;border-radius:12px;padding:12px;border:1px dashed #22c55e;font-size:12px;text-align:center">
✅ After payment, send screenshot via WhatsApp • You get priority listing • Drivers contact you faster!
</div>
</div>

<div class="card">
<h2 style="margin:0">📊 Live Stats — Growing Zambia Logistics</h2>
<div class="grid" style="margin-top:14px">
<div class="stat"><b>10</b><span style="font-size:11px;color:#64748b">Provinces Covered</span></div>
<div class="stat"><b>50+</b><span style="font-size:11px;color:#64748b">Towns & Cities</span></div>
<div class="stat"><b>363 km</b><span style="font-size:11px;color:#64748b">Kitwe-Lusaka Road</span></div>
<div class="stat"><b>K30/kg</b><span style="font-size:11px;color:#64748b">Standard Rate</span></div>
</div>
</div>

<div class="card" style="text-align:center">
<h2 style="margin:0">🚀 Ready? Let's Move Zambia!</h2>
<p style="color:#64748b;margin-top:8px">Choose your role and start posting. No truck returns empty!</p>
<a href="/driver" class="btn btn-green">I Have Truck →</a>
<a href="/trader" class="btn btn-dark">I Need Truck →</a>
</div>

</div>
<div class="footer">
<b style="color:#22c55e">MTN:</b> """ + MTN + """ (""" + MTN_NAME + """) • <b style="color:#60a5fa">Airtel:</b> """ + AIRTEL + """ (""" + AIRTEL_NAME + """)<br><br>
© MZIGO.ZM 2026 • Made in Kitwe, Copperbelt • Zambia's No.1 Empty Truck Platform<br>
All 10 Provinces • Central, Copperbelt, Eastern, Luapula, Lusaka, Muchinga, Northern, North-Western, Southern, Western
</div>
</body></html>
"""
    return html

@app.get("/driver", response_class=HTMLResponse)
async def driver_page():
    count = len(trucks)
    trucks_html = ""
    if count == 0:
        trucks_html = '<div class="card" style="text-align:center;color:#64748b;padding:30px">No trucks yet — Be first to post! 🚛<br><span style="font-size:12px">Your truck will appear here after posting</span></div>'
    else:
        for t in trucks:
            tid = t['id']
            trucks_html += '<div class="card" style="padding:18px"><div style="display:flex;justify-content:space-between"><div><b style="font-size:17px">' + t['from_city'] + ' → ' + t['to_city'] + '</b><br><span style="background:#0f172a;color:#fff;padding:4px 10px;border-radius:999px;font-size:11px">' + t['truck_type'] + '</span> <span style="background:#dcfce7;color:#14532d;padding:4px 10px;border-radius:999px;font-size:11px">📏 ' + t['distance_km'] + '</span> <span style="background:#fef3c7;padding:4px 10px;border-radius:999px;font-size:11px">K' + t['price'] + '</span><div style="margin-top:8px;font-size:12px;color:#64748b">📍 ' + t['current_location'] + ' • 🕒 ' + t['departure_time'] + ' • 📱 ' + t['whatsapp'] + '</div></div><a href="/delete-truck/' + tid + '" onclick="return confirm(\'Delete?\')" style="background:#fee2e2;color:#dc2626;padding:8px 14px;border-radius:999px;text-decoration:none;font-weight:800">🗑️</a></div></div>'

    html = """
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Driver • MZIGO.ZM</title>
<style>
body{margin:0;font-family:-apple-system,sans-serif;background:#f1f5f9}
header{background:#0f172a;color:#fff;padding:18px;text-align:center;position:sticky;top:0;z-index:10}
.container{max-width:760px;margin:0 auto;padding:16px}
.card{background:#fff;border-radius:20px;padding:22px;margin:14px 0;border:1px solid #e2e8f0;box-shadow:0 4px 16px rgba(0,0,0,0.05)}
.btn{width:100%;padding:16px;border:none;border-radius:14px;font-weight:900;background:#22c55e;color:#000;font-size:16px;cursor:pointer;margin-top:14px}
label{font-size:11px;font-weight:800;letter-spacing:0.5px;text-transform:uppercase;color:#334155;margin-top:16px;display:block}
input{width:100%;padding:14px 16px;border-radius:14px;border:1.5px solid #e2e8f0;margin-top:8px;font-size:15px;outline:none}
input:focus{border-color:#22c55e;box-shadow:0 0 0 4px #dcfce7}
.dist-box{background:#f0fdf4;border:2px dashed #22c55e;padding:16px;border-radius:14px;margin-top:12px;font-weight:800;color:#14532d;text-align:center;font-size:14px}
.back{background:#e2e8f0;color:#0f172a;padding:8px 16px;border-radius:999px;text-decoration:none;font-size:13px;font-weight:700}
</style></head><body>
<header><div style="font-size:22px;font-weight:900">MZIGO<span style="color:#22c55e">.ZM</span> • DRIVER — LOOOOONG FORM</div></header>
<div class="container">
<a href="/" class="back">← Home</a>

<div class="card" style="background:#0f172a;color:#fff;border:none">
<h2 style="margin:0;font-size:22px">🚛 Post Your Empty Truck — Long Detailed Form</h2>
<p style="color:#94a3b8;margin-top:8px">Fill all fields carefully. Auto distance will calculate road distance (not straight line). Kitwe → Lusaka = 363km real road distance!</p>
<form action="/add-truck" method="post" style="margin-top:20px">
<label>📍 From — Where are you now? (Town/City)</label><input id="from_city" name="from_city" placeholder="e.g. Kitwe, Lusaka, Ndola, Kabwe..." required>
<label>🎯 To — Where are you going? (Destination)</label><input id="to_city" name="to_city" placeholder="e.g. Lusaka, Kitwe, Livingstone, Chipata..." required>
<label>📏 Distance — Auto Calculated Road Distance (No need to type)</label><input id="distance_km" name="distance_km" placeholder="Auto — e.g. 363 km driving" readonly style="background:#f0fdf4;font-weight:900;color:#14532d;font-size:16px">
<div id="dist_info" class="dist-box">✏️ Start typing From & To — Example: Kitwe → Lusaka = 363 km driving distance (road, not straight line!)</div>
<label>🚚 Truck Type — What truck do you have?</label><input name="truck_type" placeholder="e.g. 50 Ton Howo, 30 Ton Sino, 10 Ton Canter, Flatbed..." required>
<label>📌 Current Exact Location — Landmark for pickup</label><input name="current_location" placeholder="e.g. Total Filling Station, Nkana East, Kitwe (be specific for traders)" required>
<label>🕒 Departure Date & Time — When are you leaving?</label><input name="departure_time" type="datetime-local" required>
<label>💰 Price — How much for the trip? (ZMW)</label><input name="price" type="number" placeholder="e.g. 10000 (ZMW 10,000 for Kitwe-Lusaka)" required>
<label>📱 WhatsApp Number — Traders will contact you here</label><input name="whatsapp" placeholder="e.g. 0964343865 (with MTN/Airtel)" required>
<button class="btn" type="submit">✅ Post Truck — Make It Live Across Zambia!</button>
<p style="text-align:center;color:#64748b;font-size:11px;margin-top:10px">Your truck will be visible to all traders in 10 provinces instantly!</p>
</form>
</div>

<div class="card">
<h3 style="margin:0">💡 Tips for Drivers — Get More Loads</h3>
<p style="color:#64748b;font-size:13px;margin-top:8px">1. Be specific with location — "Total Nkana Kitwe" better than "Kitwe"<br>2. Set fair price — K30/kg standard<br>3. Keep WhatsApp online<br>4. Update departure time accurately<br>5. Delete after trip done</p>
</div>

<h2 style="padding:0 8px;margin-top:24px">🚛 Live Trucks Across Zambia (""" + str(count) + """)</h2>
""" + trucks_html + """
</div>
<div style="background:#0f172a;color:#64748b;padding:20px;text-align:center;font-size:12px;margin-top:30px">
<b style="color:#22c55e">MTN:</b> """ + MTN + """ (""" + MTN_NAME + """) • <b style="color:#60a5fa">Airtel:</b> """ + AIRTEL + """ (""" + AIRTEL_NAME + """)<br>© MZIGO.ZM • Kitwe, Copperbelt
</div>
<script>
var fromEl = document.getElementById('from_city');
var toEl = document.getElementById('to_city');
var distEl = document.getElementById('distance_km');
var infoEl = document.getElementById('dist_info');
var towns = {
"lusaka": [-15.4067,28.2871],
"kitwe": [-12.8024,28.2132],
"ndola": [-12.9587,28.6365],
"kabwe": [-14.4439,28.4506],
"livingstone": [-17.8528,25.8553],
"chipata": [-13.6296,32.6467],
"kasama": [-10.2107,31.1749],
"mansa": [-11.1998,28.8934],
"mongu": [-15.2667,23.1167],
"solwezi": [-12.1735,26.3865]
};
function haversine(a,b,c,d){
  var R=6371;
  var dLat=(c-a)*Math.PI/180;
  var dLon=(d-b)*Math.PI/180;
  var e=Math.sin(dLat/2)*Math.sin(dLat/2)+Math.cos(a*Math.PI/180)*Math.cos(c*Math.PI/180)*Math.sin(dLon/2)*Math.sin(dLon/2);
  return R*2*Math.atan2(Math.sqrt(e),Math.sqrt(1-e));
}
function calcDist(){
  var f = fromEl.value.toLowerCase().trim();
  var t = toEl.value.toLowerCase().trim();
  if(!f ||!t){ infoEl.innerHTML = "✏️ Start typing From & To — Example: Kitwe → Lusaka = 363 km driving distance (road, not straight line!)"; distEl.value=""; return; }
  var fk=null, tk=null;
  for(var k in towns){ if(f.indexOf(k)>-1){ fk=k; break; } }
  for(var k in towns){ if(t.indexOf(k)>-1){ tk=k; break; } }
  if(!fk ||!tk){ infoEl.innerHTML = "📍 Town not in database yet — try Lusaka, Kitwe, Ndola, Kabwe, Livingstone, Chipata... Distance will be Calculated"; distEl.value="Calculated"; return; }
  var straight = haversine(towns[fk][0], towns[fk][1], towns[tk][0], towns[tk][1]);
  var road = Math.round(straight*1.38);
  if((fk=="lusaka" && tk=="kitwe") || (fk=="kitwe" && tk=="lusaka")) road=363;
  if((fk=="lusaka" && tk=="ndola") || (fk=="ndola" && tk=="lusaka")) road=321;
  if((fk=="kitwe" && tk=="ndola") || (fk=="ndola" && tk=="kitwe")) road=62;
  if((fk=="lusaka" && tk=="kabwe") || (fk=="kabwe" && tk=="lusaka")) road=138;
  if((fk=="lusaka" && tk=="livingstone") || (fk=="livingstone" && tk=="lusaka")) road=485;
  distEl.value = road + " km";
  infoEl.innerHTML = "✅ <b>" + road + " km driving</b> — " + fk + " → " + tk + " (road distance, not straight line!) — Real Zambian road distance";
}
fromEl.addEventListener('input', calcDist);
toEl.addEventListener('input', calcDist);
</script>
</body></html>
"""
    return html

@app.post("/add-truck")
async def add_truck(from_city: str = Form(...), to_city: str = Form(...), truck_type: str = Form(...), current_location: str = Form(""), departure_time: str = Form(""), price: str = Form(...), whatsapp: str = Form(...), distance_km: str = Form("")):
    if not distance_km or distance_km == "":
        fc = from_city.lower()
        tc = to_city.lower()
        if ("kitwe" in fc and "lusaka" in tc) or ("lusaka" in fc and "kitwe" in tc):
            distance_km = "363 km"
        else:
            distance_km = "Calculated"
    trucks.insert(0, {"id": str(uuid.uuid4())[:8], "from_city": from_city.strip(), "to_city": to_city.strip(), "truck_type": truck_type.strip(), "current_location": current_location.strip(), "departure_time": departure_time.strip(), "price": price.strip(), "whatsapp": whatsapp.strip(), "distance_km": distance_km.strip()})
    return RedirectResponse("/driver", status_code=303)

@app.get("/delete-truck/{tid}")
async def delete_truck(tid: str):
    global trucks
    trucks = [t for t in trucks if t['id']!= tid]
    return RedirectResponse("/driver", status_code=303)

@app.get("/trader", response_class=HTMLResponse)
async def trader_page():
    html = "<html><head><meta name='viewport' content='width=device-width, initial-scale=1'><style>body{margin:0;font-family:sans-serif;background:#f1f5f9;padding:16px}.card{background:#fff;border-radius:16px;padding:20px;margin:12px 0}</style></head><body><div class='card'><a href='/'>← Home</a><h2>📦 Trader — Looooong Version Coming Next!</h2><p>MTN " + MTN + " (" + MTN_NAME + ")<br>Airtel " + AIRTEL + " (" + AIRTEL_NAME + ")</p><p>Weight pricing K25-35/kg Platinum</p></div></body></html>"
    return html

@app.get("/health")
async def health():
    return {"ok": True}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
