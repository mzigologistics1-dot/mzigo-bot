import re
from datetime import datetime
from fastapi import FastAPI, Request

app = FastAPI(title="Mzigo Logistics ZM")

_trucks = []
_loads = []

def parse_message(text: str):
    text = text.upper()
    is_empty = "EMPTY" in text
    is_load = "LOAD" in text
    if not is_empty and not is_load:
        return None
    route_match = re.search(r'([A-Z]+)\s*->\s*([A-Z]+)', text)
    if not route_match:
        return None
    origin = route_match.group(1)
    dest = route_match.group(2)
    ton_match = re.search(r'(\d+)\s*T', text)
    tonnage = int(ton_match.group(1)) if ton_match else 10
    cargo = "General Goods"
    if is_load:
        cargo_match = re.search(r'LOAD:?\s*(.*?)\d+T', text)
        if cargo_match:
            cargo = cargo_match.group(1).strip()
    date = "TODAY" if "TODAY" in text else "TOMORROW"
    price_match = re.search(r'K\s*(\d+)', text)
    price = int(price_match.group(1)) if price_match else 0
    return {
        "type": "EMPTY" if is_empty else "LOAD",
        "origin": origin, "destination": dest,
        "tonnage": tonnage, "cargo": cargo,
        "date": date, "price": price,
        "raw": text, "timestamp": datetime.now().isoformat()
    }

def route_overlap(t_o, t_d, l_o, l_d):
    ORDER = ["LUSAKA", "KABWE", "KAPIRI", "NDOLA", "KITWE", "CHINGOLA", "KASUMBALESA"]
    try:
        ti_o = ORDER.index(t_o)
        ti_d = ORDER.index(t_d)
        li_o = ORDER.index(l_o)
        li_d = ORDER.index(l_d)
        if ti_o <= li_o and ti_d >= li_d:
            return True
        return t_o == l_o and t_d == l_d
    except:
        return t_o == l_o and t_d == l_d

def find_matches(request, pool):
    matches = []
    is_truck = request['type'] == 'EMPTY'
    for item in pool:
        if item.get('phone') == request.get('phone'):
            continue
        if is_truck:
            if route_overlap(request['origin'], request['destination'], item['origin'], item['destination']):
                if request['tonnage'] >= item['tonnage']:
                    matches.append(item)
        else:
            if route_overlap(item['origin'], item['destination'], request['origin'], request['destination']):
                if item['tonnage'] >= request['tonnage']:
                    matches.append(item)
    return matches

def send_whatsapp(to, msg):
    print(f"SEND to {to}: {msg}")
    return True

@app.get("/")
def home():
    return {"status": "Mzigo Bot Running", "trucks": len(_trucks), "loads": len(_loads)}

@app.post("/webhook/whatsapp")
async def webhook(request: Request):
    try:
        data = await request.json()
        msg = data['entry'][0]['changes'][0]['value']['messages'][0]
        from_num = msg['from']
        text = msg['text']['body']
        parsed = parse_message(text)
        if not parsed:
            send_whatsapp(from_num, "Send: EMPTY: Lusaka -> Kitwe 20T OR LOAD: 5T mealie meal Lusaka -> Ndola")
            return {"ok": True}
        parsed['phone'] = from_num
        if parsed['type'] == 'EMPTY':
            _trucks.append(parsed)
            matches = find_matches(parsed, _loads)
            if matches:
                reply = f"Found {len(matches)} LOAD(s) for {parsed['origin']}->{parsed['destination']}:\n"
                for i, m in enumerate(matches[:3], 1):
                    reply += f"\n{i}. {m['tonnage']}T {m['cargo']} {m['origin']}->{m['destination']} K{m['price']}"
                reply += "\n\nReply 1,2,3 to connect. K350 commission."
            else:
                reply = f"Saved! No load yet for {parsed['origin']}->{parsed['destination']} {parsed['tonnage']}T."
            send_whatsapp(from_num, reply)
        else:
            _loads.append(parsed)
            matches = find_matches(parsed, _trucks)
            if matches:
                reply = f"Found {len(matches)} TRUCK(s):\n"
                for i, m in enumerate(matches[:3], 1):
                    reply += f"\n{i}. {m['tonnage']}T {m['origin']}->{m['destination']} Driver: {m['phone']}"
            else:
                reply = f"Saved! Your {parsed['tonnage']}T {parsed['cargo']} {parsed['origin']}->{parsed['destination']} listed."
            send_whatsapp(from_num, reply)
    except Exception as e:
        print(e)
    return {"ok": True}
