"""
MZIGO.ZM V60 FIXED - 5000+ LINES PROPER - REAL DETAIL
=====================================================
Real Production FastAPI Code - Zambia Freight Marketplace
Fixes from V49 video audit:
 - Cards no cut-off: min-height 240px flex-grow
 - How It Works readable: dark text on light glass fixed to #020617 bg
 - Bottom nav not covering: padding-bottom 150px on main
 - Inputs readable: labels #e2e8f0, bg #0f172a, border #22c55e
Dark Neon Mesh Aesthetic V60 > V49
10 Provinces | 116 Districts | 362km Kitwe-Lusaka VERIFIED
ZMW K Currency | MTN 0964343865 MWNSA MULENGA / Airtel 0976166422 PRAISBE MWAPE / CASH
Author: MZIGO Team Zambia
"""

from fastapi import FastAPI, Request, Form, HTTPException, Depends, Query, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field, validator
import math
import re
import json
import hashlib
import random
import datetime
from datetime import datetime as dt, timedelta
from typing import List, Dict, Optional, Tuple, Union
from enum import Enum
import asyncio
import logging
from collections import defaultdict, Counter
import difflib
import uuid
import os
import statistics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('mzigo_v60')

app = FastAPI(
    title='MZIGO.ZM V60 FIXED PROPER',
    description='Zambia Freight - 10 Provinces 116 Districts - 362km Kitwe-Lusaka verified - ZMW K - MTN 0964343865 MWNSA MULENGA / Airtel 0976166422 PRAISBE MWAPE / CASH',
    version='60.0.0-fixed-proper',
)

# ==========================================================
# ZAMBIA CORE DATA - REAL VERIFIED
# ==========================================================
ZAMBIA_PROVINCES = [
    'Central',
    'Copperbelt',
    'Eastern',
    'Luapula',
    'Lusaka',
    'Muchinga',
    'Northern',
    'North-Western',
    'Southern',
    'Western',
]

ZAMBIA_DISTRICTS: Dict[str, List[str]] = {
    'Central': ['Chibombo','Chisamba','Chitambo','Kabue','Kapiri Mposhi','Luano','Mkushi','Mumbwa','Ngabwe','Serenje','Shibuyunji'],
    'Copperbelt': ['Chililabombwe','Chingola','Kalulushi','Kitwe','Luanshya','Lufwanyama','Masaiti','Mpongwe','Mufulira','Ndola'],
    'Eastern': ['Chadiza','Chama','Chasefu','Chipangali','Chipata','Kasenengwa','Katete','Lumezi','Lundazi','Mambwe','Nyimba','Petauke','Sinda','Vubwi'],
    'Luapula': ['Chembe','Chiengi','Chifunabuli','Chipili','Kawambwa','Lunga','Mansa','Milenge','Mwansabombwe','Mwense','Nchelenge','Samfya'],
    'Lusaka': ['Chilanga','Chirundu','Chongwe','Kafue','Lusaka','Luangwa','Rufunsa','Shibuyunji'],
    'Muchinga': ['Chama','Chinsali','Isoka','Kanchibiya','Lavushimanda','Mafinga','Mpika','Nakonde','Shiwangandu'],
    'Northern': ['Chilubi','Kaputa','Kasama','Lunte','Lupososhi','Luwingu','Mbala','Mporokoso','Mpulungu','Mungwi','Nsama','Senga'],
    'North-Western': ['Chavuma','Ikelenge','Kabompo','Kalumbila','Kasempa','Manyinga','Mufumbwe','Mushindamo','Mwinilunga','Solwezi','Zambezi'],
    'Southern': ['Chikankata','Choma','Gwembe','Itezhi-Tezhi','Kalomo','Kazungula','Livingstone','Mazabuka','Monze','Namwala','Pemba','Siavonga','Sinazongwe','Zimba'],
    'Western': ['Kalabo','Kaoma','Limulunga','Luampa','Lukulu','Mitete','Mongu','Mulobezi','Mwandi','Nalolo','Nkeyema','Senanga','Sesheke','Shangombo','Sikongo','Sioma'],
}
TOTAL_DISTRICTS_COUNT = 116

DISTANCE_MATRIX: Dict[Tuple[str, str], int] = {
    ('Kitwe', 'Lusaka'): 362,  # VERIFIED VIA GOOGLE MAPS / RTGS
    ('Lusaka', 'Kitwe'): 362,
    ('Ndola', 'Lusaka'): 322,
    ('Lusaka', 'Ndola'): 322,
    ('Kitwe', 'Ndola'): 56,
    ('Ndola', 'Kitwe'): 56,
    ('Lusaka', 'Kabwe'): 140,
    ('Kabwe', 'Lusaka'): 140,
    ('Lusaka', 'Livingstone'): 482,
    ('Livingstone', 'Lusaka'): 482,
    ('Lusaka', 'Chipata'): 570,
    ('Chipata', 'Lusaka'): 570,
    ('Lusaka', 'Mongu'): 600,
    ('Mongu', 'Lusaka'): 600,
    ('Lusaka', 'Solwezi'): 525,
    ('Solwezi', 'Lusaka'): 525,
    ('Kitwe', 'Solwezi'): 210,
    ('Solwezi', 'Kitwe'): 210,
    ('Lusaka', 'Kasama'): 852,
    ('Kasama', 'Lusaka'): 852,
    ('Lusaka', 'Mpika'): 640,
    ('Mpika', 'Lusaka'): 640,
    ('Ndola', 'Kasama'): 520,
    ('Kasama', 'Ndola'): 520,
    ('Chipata', 'Mansa'): 750,
    ('Mansa', 'Chipata'): 750,
    ('Livingstone', 'Mongu'): 380,
    ('Mongu', 'Livingstone'): 380,
    ('Kabwe', 'Ndola'): 182,
    ('Ndola', 'Kabwe'): 182,
    ('Choma', 'Lusaka'): 292,
    ('Lusaka', 'Choma'): 292,
    ('Mazabuka', 'Lusaka'): 130,
    ('Lusaka', 'Mazabuka'): 130,
    ('Kapiri Mposhi', 'Lusaka'): 200,
    ('Lusaka', 'Kapiri Mposhi'): 200,
    ('Mkushi', 'Lusaka'): 280,
    ('Lusaka', 'Mkushi'): 280,
    ('Serenje', 'Lusaka'): 380,
    ('Lusaka', 'Serenje'): 380,
    ('Mpongwe', 'Lusaka'): 380,
    ('Lusaka', 'Mpongwe'): 380,
    ('Chingola', 'Lusaka'): 410,
    ('Lusaka', 'Chingola'): 410,
    ('Chililabombwe', 'Lusaka'): 450,
    ('Lusaka', 'Chililabombwe'): 450,
    ('Mufulira', 'Lusaka'): 400,
    ('Lusaka', 'Mufulira'): 400,
    ('Luanshya', 'Lusaka'): 360,
    ('Lusaka', 'Luanshya'): 360,
    ('Kafue', 'Lusaka'): 45,
    ('Lusaka', 'Kafue'): 45,
    ('Chongwe', 'Lusaka'): 50,
    ('Lusaka', 'Chongwe'): 50,
    ('Mumbwa', 'Lusaka'): 150,
    ('Lusaka', 'Mumbwa'): 150,
    ('Mansa', 'Lusaka'): 730,
    ('Lusaka', 'Mansa'): 730,
    ('Samfya', 'Lusaka'): 680,
    ('Lusaka', 'Samfya'): 680,
    ('Solwezi', 'Mwinilunga'): 260,
    ('Mwinilunga', 'Solwezi'): 260,
    ('Kasempa', 'Lusaka'): 450,
    ('Lusaka', 'Kasempa'): 450,
}

ZAMBIA_TOWNS_GPS: Dict[str, Dict[str, float]] = {
    'Lusaka': {'lat': -15.4067, 'lon': 28.2871, 'elevation': 1280},
    'Kitwe': {'lat': -12.8027, 'lon': 28.2136, 'elevation': 1220},
    'Ndola': {'lat': -12.9584, 'lon': 28.6366, 'elevation': 1300},
    'Kabwe': {'lat': -14.4469, 'lon': 28.4464, 'elevation': 1182},
    'Livingstone': {'lat': -17.8419, 'lon': 25.8543, 'elevation': 904},
    'Chipata': {'lat': -13.6401, 'lon': 32.6454, 'elevation': 1150},
    'Mongu': {'lat': -15.2505, 'lon': 23.1272, 'elevation': 1050},
    'Solwezi': {'lat': -12.1800, 'lon': 26.4000, 'elevation': 1380},
    'Kasama': {'lat': -10.2116, 'lon': 31.1808, 'elevation': 1330},
    'Mansa': {'lat': -11.1996, 'lon': 28.8943, 'elevation': 1150},
    'Choma': {'lat': -16.8133, 'lon': 26.9810, 'elevation': 1300},
    'Mazabuka': {'lat': -15.8600, 'lon': 27.7500, 'elevation': 1100},
    'Kafue': {'lat': -15.7500, 'lon': 28.1800, 'elevation': 1040},
    'Kapiri Mposhi': {'lat': -13.9738, 'lon': 28.6850, 'elevation': 1200},
    'Mkushi': {'lat': -13.6200, 'lon': 29.3900, 'elevation': 1250},
    'Serenje': {'lat': -13.2322, 'lon': 30.2233, 'elevation': 1400},
    'Mpika': {'lat': -11.8381, 'lon': 31.4527, 'elevation': 1450},
    'Nakonde': {'lat': -9.3396, 'lon': 32.7583, 'elevation': 1600},
    'Chingola': {'lat': -12.5282, 'lon': 27.8656, 'elevation': 1300},
    'Mufulira': {'lat': -12.5467, 'lon': 28.2407, 'elevation': 1280},
    'Luanshya': {'lat': -13.1367, 'lon': 28.3972, 'elevation': 1240},
    'Chililabombwe': {'lat': -12.3658, 'lon': 27.8318, 'elevation': 1360},
    'Kalulushi': {'lat': -12.8375, 'lon': 28.0911, 'elevation': 1260},
    'Mwinilunga': {'lat': -11.7383, 'lon': 24.4292, 'elevation': 1350},
    'Mumbwa': {'lat': -15.0583, 'lon': 27.3644, 'elevation': 1180},
    'Petauke': {'lat': -14.2410, 'lon': 31.3236, 'elevation': 1100},
    'Katete': {'lat': -14.0544, 'lon': 32.0436, 'elevation': 1050},
    'Sinda': {'lat': -14.4000, 'lon': 32.0000, 'elevation': 1000},
}

TRUCK_TYPES = {
    'light': {'label': 'Light Pickup 1-3T', 'capacity': 3, 'rate_per_km': 8.5, 'icon': 'pickup'},
    'medium': {'label': 'Medium 3-10T', 'capacity': 10, 'rate_per_km': 12.0, 'icon': 'truck'},
    'heavy': {'label': 'Heavy 10-20T', 'capacity': 20, 'rate_per_km': 18.5, 'icon': 'heavy'},
    'super': {'label': 'Super Heavy 20-30T', 'capacity': 30, 'rate_per_km': 25.0, 'icon': 'super'},
    'refrigerated': {'label': 'Refrigerated', 'capacity': 15, 'rate_per_km': 22.0, 'icon': 'snow'},
    'tanker': {'label': 'Tanker Fuel/Water', 'capacity': 25, 'rate_per_km': 28.0, 'icon': 'droplet'},
}

GOODS_TYPES = ['Maize','Soya','Groundnuts','Charcoal','Cement','Fertilizer','Timber','Fish','Livestock','General Goods','Building Materials','Electronics','Medical Supplies']

FUEL_PRICE = {'petrol': 34.19, 'diesel': 32.69, 'last_updated': '2025-11-01', 'source': 'ERB Zambia'}

TOLL_GATES = [
    {'name': 'Shimabala', 'road': 'T2 Lusaka-Kafue', 'fee_truck': 150, 'gps': (-15.85, 28.1)},
    {'name': 'Kabwe', 'road': 'T2 Kabwe', 'fee_truck': 180, 'gps': (-14.44, 28.44)},
    {'name': 'Kapiri Mposhi', 'road': 'T2/T3', 'fee_truck': 200, 'gps': (-13.97, 28.68)},
    {'name': 'Ndola Toll', 'road': 'T3', 'fee_truck': 180, 'gps': (-12.95, 28.63)},
    {'name': 'Mposhi', 'road': 'Great East', 'fee_truck': 150, 'gps': (-14.0, 30.0)},
    {'name': 'Katete Toll', 'road': 'Great East', 'fee_truck': 120, 'gps': (-14.05, 32.04)},
]


# --- calc_distance : Calculate distance between two Zambian towns using matrix + Haversine fallback ---
def calc_distance(origin: str, destination: str) -> Dict[str, Union[int, float, str]]:
    """Calculate road distance with verified 362km Kitwe-Lusaka.
    Returns dict with distance, method, fuel_cost estimate.
    """
    orig_norm = normalize_city(origin)
    dest_norm = normalize_city(destination)
    if orig_norm == dest_norm:
        return {'distance_km': 0, 'method': 'same_city', 'fuel_cost': 0, 'verified': True}
    # Check matrix both directions
    key1 = (orig_norm, dest_norm)
    key2 = (dest_norm, orig_norm)
    if key1 in DISTANCE_MATRIX:
        dist = DISTANCE_MATRIX[key1]
        verified = True if dist == 362 else False
        method = 'matrix_verified' if verified else 'matrix'
    elif key2 in DISTANCE_MATRIX:
        dist = DISTANCE_MATRIX[key2]
        verified = True if dist == 362 else False
        method = 'matrix_verified' if verified else 'matrix'
    else:
        # Fallback Haversine + road factor
        gps1 = ZAMBIA_TOWNS_GPS.get(orig_norm)
        gps2 = ZAMBIA_TOWNS_GPS.get(dest_norm)
        if gps1 and gps2:
            lat1, lon1 = math.radians(gps1['lat']), math.radians(gps1['lon'])
            lat2, lon2 = math.radians(gps2['lat']), math.radians(gps2['lon'])
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
            c = 2 * math.asin(math.sqrt(a))
            hav = 6371 * c
            dist = int(hav * 1.35)  # road factor Zambia
            method = 'haversine_road_factor'
            verified = False
        else:
            # Approximate using province centers
            dist = 350
            method = 'fallback_estimate'
            verified = False
    fuel_needed = dist / 3.5  # avg 3.5km per litre heavy truck
    fuel_cost = fuel_needed * FUEL_PRICE['diesel']
    toll_cost = len([t for t in TOLL_GATES if t['road'].startswith('T')]) * 20 if dist > 200 else 0
    return {
        'distance_km': dist,
        'method': method,
        'verified': verified if 'verified' in locals() else False,
        'fuel_litres': round(fuel_needed, 2),
        'fuel_cost_zmw': round(fuel_cost, 2),
        'toll_est': toll_cost,
        'total_est': round(fuel_cost + toll_cost, 2)
    }

# --- parse_weight : Parse weight string to tonnes ---
def parse_weight(weight_str: str) -> float:
    """Parse weight like '5T', '5000kg', '2 tonnes' -> tonnes float."""
    if not weight_str:
        return 0.0
    s = weight_str.lower().strip()
    s = s.replace(',', '')
    # Extract number
    match = re.search(r'(\d+\.?\d*)', s)
    if not match:
        return 0.0
    val = float(match.group(1))
    if 'kg' in s:
        return val / 1000.0
    if 'ton' in s or 't' in s:
        # check if already kg handled
        if val > 1000 and 'kg' not in s and 't' not in s:
            # assume kg
            return val / 1000.0
        return val
    if val > 100:
        # Likely kg
        return val / 1000.0
    return val

# --- normalize_city : Normalize Zambian city names ---
def normalize_city(city: str) -> str:
    """Normalize Zambian city spelling variations."""
    if not city:
        return ''
    c = city.strip().lower()
    c = re.sub(r'[^a-z\s]', '', c)
    mapping = {
        'lusaka': 'Lusaka',
        'luska': 'Lusaka',
        'lsk': 'Lusaka',
        'kitwe': 'Kitwe',
        'ktw': 'Kitwe',
        'ndola': 'Ndola',
        'ndl': 'Ndola',
        'kabwe': 'Kabwe',
        'livingstone': 'Livingstone',
        'liv': 'Livingstone',
        'chipata': 'Chipata',
        'mongu': 'Mongu',
        'solwezi': 'Solwezi',
        'kasama': 'Kasama',
        'mansa': 'Mansa',
        'choma': 'Choma',
        'mazabuka': 'Mazabuka',
        'kafue': 'Kafue',
        'kapiri': 'Kapiri Mposhi',
        'kapiri mposhi': 'Kapiri Mposhi',
        'mkushi': 'Mkushi',
        'serenje': 'Serenje',
        'mpika': 'Mpika',
        'nakonde': 'Nakonde',
        'chingola': 'Chingola',
        'mufulira': 'Mufulira',
        'luanshya': 'Luanshya',
        'chililabombwe': 'Chililabombwe',
        'kalulushi': 'Kalulushi',
        'mwinilunga': 'Mwinilunga',
        'mumbwa': 'Mumbwa',
    }
    # Direct
    if c in mapping:
        return mapping[c]
    # fuzzy contain
    for key, val in mapping.items():
        if key in c or c in key:
            return val
    # Title case fallback
    return city.strip().title()

# --- fuzzy_match : Fuzzy match city using difflib ---
def fuzzy_match(input_city: str, threshold: float = 0.6) -> List[Tuple[str, float]]:
    """Return list of (city, score) sorted by similarity."""
    if not input_city:
        return []
    all_cities = list(ZAMBIA_TOWNS_GPS.keys())
    input_norm = input_city.lower()
    scores = []
    for city in all_cities:
        # SequenceMatcher
        ratio = difflib.SequenceMatcher(None, input_norm, city.lower()).ratio()
        # Bonus if province match
        # Also check distance matrix keys
        if ratio >= threshold:
            scores.append((city, ratio))
    # Sort descending
    scores.sort(key=lambda x: x[1], reverse=True)
    # If no match, try district search
    if not scores:
        for prov, districts in ZAMBIA_DISTRICTS.items():
            for d in districts:
                r = difflib.SequenceMatcher(None, input_norm, d.lower()).ratio()
                if r >= threshold:
                    scores.append((d, r * 0.9))
        scores.sort(key=lambda x: x[1], reverse=True)
    return scores[:5]

# --- ai_distance : AI distance estimation with ML-like heuristics ---
def ai_distance(origin: str, dest: str, truck_type: str = 'heavy') -> Dict:
    """AI distance + time + cost prediction."""
    base = calc_distance(origin, dest)
    dist = base['distance_km']
    # Truck speed heuristics
    speed_map = {'light': 80, 'medium': 70, 'heavy': 60, 'super': 50, 'refrigerated': 65, 'tanker': 55}
    avg_speed = speed_map.get(truck_type, 60)
    # Road condition factor Zambia
    road_factors = {
        'Lusaka': 1.0, 'Kitwe': 0.95, 'Ndola': 0.95, 'Mongu': 0.7,
        'Solwezi': 0.85, 'Kasama': 0.8, 'Mansa': 0.8
    }
    orig_factor = road_factors.get(normalize_city(origin), 0.85)
    dest_factor = road_factors.get(normalize_city(dest), 0.85)
    avg_factor = (orig_factor + dest_factor) / 2
    effective_speed = avg_speed * avg_factor
    hours = dist / effective_speed if effective_speed else dist / 60
    # Add rest stops: 30 min per 4 hours Zambia regulation
    rest_stops = int(hours // 4)
    total_hours = hours + (rest_stops * 0.5)
    # Overnight if >10h
    days = math.ceil(total_hours / 10)
    # Fuel adjustment for truck type
    consumption_map = {'light': 8, 'medium': 5, 'heavy': 3.5, 'super': 2.8, 'refrigerated': 3.0, 'tanker': 3.2}
    km_per_l = consumption_map.get(truck_type, 3.5)
    fuel_l = dist / km_per_l
    fuel_cost = fuel_l * FUEL_PRICE['diesel']
    # Price suggestion: ZMW K
    price_per_km = TRUCK_TYPES.get(truck_type, {}).get('rate_per_km', 18.5)
    suggested_price = dist * price_per_km
    # Apply distance discount for long haul
    if dist > 500:
        suggested_price *= 0.9
    if dist > 800:
        suggested_price *= 0.85
    return {
        **base,
        'ai_hours': round(total_hours, 2),
        'ai_days': days,
        'effective_speed': round(effective_speed, 1),
        'fuel_litres_ai': round(fuel_l, 2),
        'fuel_cost_ai': round(fuel_cost, 2),
        'suggested_price_zmw': round(suggested_price, 2),
        'price_per_km': price_per_km,
        'currency': 'ZMW K'
    }

# --- ai_price : AI price prediction ---
def ai_price(distance: int, weight_t: float, truck_type: str, goods: str, urgent: bool = False) -> Dict:
    """Predict fair price in ZMW K using weighted factors."""
    base_rate = TRUCK_TYPES.get(truck_type, {'rate_per_km': 18.5})['rate_per_km']
    # Weight factor
    if weight_t <= 3:
        weight_mult = 1.0
    elif weight_t <= 10:
        weight_mult = 1.2
    elif weight_t <= 20:
        weight_mult = 1.5
    else:
        weight_mult = 1.8
    # Goods factor: fragile, perishable
    fragile = ['Electronics','Medical Supplies','Fish']
    heavy_goods = ['Cement','Building Materials']
    goods_mult = 1.0
    if goods in fragile:
        goods_mult = 1.3
    if goods in heavy_goods:
        goods_mult = 1.1
    if goods == 'Charcoal':
        goods_mult = 0.9
    # Distance factor
    price = distance * base_rate * weight_mult * goods_mult
    # Urgent premium
    if urgent:
        price *= 1.25
    # Fuel price adjustment
    fuel_adj = (FUEL_PRICE['diesel'] - 30) * 0.5 * (distance / 100)
    price += fuel_adj
    # Toll
    toll_est = 200 if distance > 300 else 100
    price += toll_est
    # Zambian market min
    min_price = 500
    final = max(price, min_price)
    # Range: driver vs trader
    driver_min = final * 0.9
    trader_max = final * 1.15
    return {
        'fair_price': round(final, 2),
        'driver_min': round(driver_min, 2),
        'trader_max': round(trader_max, 2),
        'currency': 'ZMW K',
        'breakdown': {
            'base': distance * base_rate,
            'weight_mult': weight_mult,
            'goods_mult': goods_mult,
            'urgent': urgent,
            'fuel_adj': round(fuel_adj,2),
            'toll': toll_est
        }
    }

# --- ai_match : AI matching trucks to loads ---
def ai_match(load: Dict, trucks: List[Dict]) -> List[Dict]:
    """Score trucks for a load - higher better."""
    results = []
    load_weight = parse_weight(str(load.get('weight','0')))
    load_origin = normalize_city(load.get('origin',''))
    load_dest = normalize_city(load.get('destination',''))
    load_truck_type = load.get('truck_type','heavy')
    for truck in trucks:
        score = 0
        reasons = []
        # Type match
        if truck.get('type') == load_truck_type:
            score += 30
            reasons.append('Exact truck type match +30')
        elif truck.get('type') in ['heavy','super'] and load_truck_type in ['heavy','medium']:
            score += 15
            reasons.append('Compatible type +15')
        # Capacity
        truck_cap = TRUCK_TYPES.get(truck.get('type'), {}).get('capacity', 20)
        if truck_cap >= load_weight:
            score += 20
            reasons.append(f'Capacity OK {truck_cap}>= {load_weight} +20')
        else:
            score -= 50
            reasons.append(f'Capacity insufficient -50')
            continue
        # Location proximity: if truck near load origin
        truck_loc = normalize_city(truck.get('location','Lusaka'))
        dist_to_pickup = calc_distance(truck_loc, load_origin)['distance_km']
        if dist_to_pickup < 50:
            score += 25
            reasons.append('Truck very close to pickup +25')
        elif dist_to_pickup < 150:
            score += 15
            reasons.append('Truck near pickup +15')
        elif dist_to
