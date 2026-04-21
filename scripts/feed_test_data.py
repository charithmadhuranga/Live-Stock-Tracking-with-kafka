#!/usr/bin/env python3
import requests
import json
import time
import random
from datetime import datetime

API_URL = "http://localhost:8000"

def create_paddocks():
    paddocks = [
        {
            "id": "paddock-1",
            "name": "North Paddock",
            "geometry": "POLYGON((144.94 -36.59, 144.95 -36.59, 144.95 -36.60, 144.94 -36.60, 144.94 -36.59))",
            "area_hectares": 50.5
        },
        {
            "id": "paddock-2",
            "name": "South Paddock",
            "geometry": "POLYGON((144.94 -36.60, 144.95 -36.60, 144.95 -36.61, 144.94 -36.61, 144.94 -36.60))",
            "area_hectares": 75.2
        },
        {
            "id": "paddock-3",
            "name": "East Paddock",
            "geometry": "POLYGON((144.95 -36.60, 144.96 -36.60, 144.96 -36.61, 144.95 -36.61, 144.95 -36.60))",
            "area_hectares": 60.0
        }
    ]
    
    for p in paddocks:
        try:
            res = requests.post(f"{API_URL}/api/paddocks", json=p)
            print(f"Created paddock: {p['name']} - {res.status_code}")
        except Exception as e:
            print(f"Error creating paddock: {e}")

def create_animals():
    animals = [
        {"id": "animal-001", "name": "Bessie", "species": "cattle", "belt_id": "BELT-001", "current_paddock_id": "paddock-1"},
        {"id": "animal-002", "name": "Maggie", "species": "cattle", "belt_id": "BELT-002", "current_paddock_id": "paddock-1"},
        {"id": "animal-003", "name": "Daisy", "species": "cattle", "belt_id": "BELT-003", "current_paddock_id": "paddock-2"},
        {"id": "animal-004", "name": "Bull", "species": "cattle", "belt_id": "BELT-004", "current_paddock_id": "paddock-2"},
        {"id": "animal-005", "name": "Calf", "species": "cattle", "belt_id": "BELT-005", "current_paddock_id": "paddock-3"},
    ]
    
    for a in animals:
        try:
            res = requests.post(f"{API_URL}/api/animals", json=a)
            print(f"Created animal: {a['name']} - {res.status_code}")
        except Exception as e:
            print(f"Error creating animal: {e}")

def send_telemetry():
    belt_ids = ["BELT-001", "BELT-002", "BELT-003", "BELT-004", "BELT-005"]
    base_coords = {
        "BELT-001": (-36.595, 144.945),
        "BELT-002": (-36.596, 144.946),
        "BELT-003": (-36.605, 144.945),
        "BELT-004": (-36.606, 144.946),
        "BELT-005": (-36.605, 144.955),
    }
    
    print("Sending telemetry data for 30 seconds...")
    for i in range(30):
        for belt_id in belt_ids:
            lat, lng = base_coords[belt_id]
            lat += random.uniform(-0.001, 0.001)
            lng += random.uniform(-0.001, 0.001)
            
            payload = {
                "belt_id": belt_id,
                "latitude": round(lat, 6),
                "longitude": round(lng, 6),
                "temperature": round(random.uniform(37.5, 39.5), 1),
                "activity_level": round(random.uniform(0.5, 10.0), 1),
                "timestamp": int(time.time())
            }
            
            try:
                res = requests.post(f"{API_URL}/api/telemetry", json=payload)
                if res.status_code == 200:
                    print(f"Telemetry {belt_id}: {payload['temperature']}°C, {payload['activity_level']}")
            except Exception as e:
                print(f"Error sending telemetry: {e}")
        
        time.sleep(1)
    
    print("Telemetry sending complete!")

def main():
    print("=== Feeding Test Data ===")
    print("Creating paddocks...")
    create_paddocks()
    
    print("\nCreating animals...")
    create_animals()
    
    print("\nSending telemetry data...")
    send_telemetry()
    
    print("\n=== Test Data Loaded ===")
    print(f"API: {API_URL}")
    print("Frontend: http://localhost:3000")

if __name__ == "__main__":
    main()