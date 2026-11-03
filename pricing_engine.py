"""
MZIGO LOGISTICS - AUTOMATED PRICING & CORRIDOR INTELLIGENCE ENGINE
"""

import math

# Corridor Distance Matrix (in Kilometers)
CORRIDOR_DISTANCES = {
    ("kitwe", "lusaka"): 362,
    ("ndola", "lusaka"): 321,
    ("kitwe", "chipata"): 666,
    ("lusaka", "solwezi"): 490,
    ("lusaka", "livingstone"): 485,
    ("ndola", "solwezi"): 395
}

# Base rates per kilometer in ZMW based on truck capacity/type
TONNAGE_MULTIPLIERS = {
    "10 ton": 55.0,
    "15 ton": 75.0,
    "20 ton": 95.0,
    "30 ton": 125.0,
    "default": 60.0
}

def calculate_corridor_estimate(origin: str, destination: str, truck_type: str) -> dict:
    orig = origin.strip().lower()
    dest = destination.strip().lower()
    
    # Lookup distance or default to an AI estimation formula if route is custom
    distance = CORRIDOR_DISTANCES.get((orig, dest)) or CORRIDOR_DISTANCES.get((dest, orig))
    
    if not distance:
        # Fallback pseudo-random calculation for custom unlisted routes
        distance = abs(len(orig) - len(dest)) * 45 + 280

    # Determine rate multiplier
    t_key = "default"
    for key in TONNAGE_MULTIPLIERS:
        if key in truck_type.lower():
            t_key = key
            break
    
    rate_per_km = TONNAGE_MULTIPLIERS[t_key]
    
    # Automated Pricing Formula: (Distance * Rate) + Toll/Fuel Overhead
    base_price = (distance * rate_per_km) + 3500
    
    # Estimated Travel Time (Assuming average truck speed of 65 km/h with mandatory rest stops)
    travel_hours = distance / 65.0
    estimated_time_str = f"{int(travel_hours)} hours ({round(travel_hours / 24, 1)} days)"

    return {
        "origin": origin.title(),
        "destination": destination.title(),
        "distance_km": distance,
        "estimated_price_zmw": round(base_price, -2), # Rounded to nearest 100
        "estimated_travel_time": estimated_time_str,
        "suggested_fuel_allocation_zmw": round(distance * 14.5, 2) # Estimated fuel cost metric
    }
