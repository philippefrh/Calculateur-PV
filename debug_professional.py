#!/usr/bin/env python3
"""
Focused Professional Version Testing - Debug Issues
"""

import requests
import json

BACKEND_URL = "https://b3e4f691-e66b-445a-8707-3eb34141dcd9.preview.emergentagent.com/api"

def test_professional_prime_issue():
    """Debug the professional prime calculation issue"""
    session = requests.Session()
    
    # Create professional client
    client_data = {
        "first_name": "Debug",
        "last_name": "Test",
        "address": "10 Avenue des Champs-Élysées, 75008 Paris",
        "roof_surface": 150.0,
        "roof_orientation": "Sud",
        "velux_count": 0,
        "heating_system": "Pompe à chaleur",
        "water_heating_system": "Solaire thermique",
        "water_heating_capacity": 500,
        "annual_consumption_kwh": 15000.0,
        "monthly_edf_payment": 450.0,
        "annual_edf_payment": 5400.0,
        "client_mode": "professionnels"
    }
    
    client_response = session.post(f"{BACKEND_URL}/clients", json=client_data)
    if client_response.status_code != 200:
        print(f"❌ Failed to create client: {client_response.status_code}")
        print(client_response.text)
        return
    
    client = client_response.json()
    client_id = client["id"]
    print(f"✅ Created professional client: {client_id}")
    
    # Test professional calculation
    prof_response = session.post(f"{BACKEND_URL}/calculate-professional/{client_id}?price_level=base")
    if prof_response.status_code != 200:
        print(f"❌ Professional calculation failed: {prof_response.status_code}")
        print(prof_response.text)
        return
    
    prof_calc = prof_response.json()
    kit_power = prof_calc["kit_power"]
    autoconsumption_aid = prof_calc["autoconsumption_aid"]
    
    print(f"✅ Professional calculation successful:")
    print(f"   Kit power: {kit_power}kW")
    print(f"   Autoconsumption aid: {autoconsumption_aid}€")
    
    # Get kit data to check prime
    kits_response = session.get(f"{BACKEND_URL}/solar-kits/professionnels")
    kits = kits_response.json()
    kit_info = kits.get(str(kit_power))
    
    if kit_info:
        table_prime = kit_info["prime"]
        print(f"   Table prime: {table_prime}€")
        
        # Check if it matches
        if abs(autoconsumption_aid - table_prime) < 1:
            print(f"✅ Prime correctly uses table value")
        else:
            print(f"❌ Prime mismatch: aid {autoconsumption_aid}€ != table {table_prime}€")
            
        # Check if it's calculated
        calculated_aid = kit_power * 190
        if abs(autoconsumption_aid - calculated_aid) < 10:
            print(f"⚠️  Prime appears calculated: {autoconsumption_aid}€ ≈ {kit_power}kW × 190€/kW = {calculated_aid}€")
        else:
            print(f"✅ Prime is NOT calculated (would be {calculated_aid}€)")
    
    # Test regular calculation for comparison
    regular_response = session.post(f"{BACKEND_URL}/calculate/{client_id}")
    if regular_response.status_code == 200:
        regular_calc = regular_response.json()
        regular_aid = regular_calc["autoconsumption_aid"]
        print(f"   Regular calculation aid: {regular_aid}€")
        
        if abs(regular_aid - autoconsumption_aid) < 1:
            print(f"✅ Both calculations give same aid")
        else:
            print(f"❌ Different aids: professional {autoconsumption_aid}€ vs regular {regular_aid}€")
    else:
        print(f"❌ Regular calculation failed: {regular_response.status_code}")
        print(regular_response.text)

def test_particuliers_calculation():
    """Test particuliers calculation to debug the comparison issue"""
    session = requests.Session()
    
    # Create particuliers client
    client_data = {
        "first_name": "Particulier",
        "last_name": "Debug",
        "address": "15 Rue de Rivoli, 75001 Paris",
        "roof_surface": 150.0,
        "roof_orientation": "Sud",
        "velux_count": 0,
        "heating_system": "Pompe à chaleur",
        "water_heating_system": "Solaire thermique",
        "water_heating_capacity": 500,
        "annual_consumption_kwh": 15000.0,
        "monthly_edf_payment": 450.0,
        "annual_edf_payment": 5400.0,
        "client_mode": "particuliers"
    }
    
    client_response = session.post(f"{BACKEND_URL}/clients", json=client_data)
    if client_response.status_code != 200:
        print(f"❌ Failed to create particuliers client: {client_response.status_code}")
        print(client_response.text)
        return
    
    client = client_response.json()
    client_id = client["id"]
    print(f"✅ Created particuliers client: {client_id}")
    
    # Test calculation
    calc_response = session.post(f"{BACKEND_URL}/calculate/{client_id}")
    if calc_response.status_code != 200:
        print(f"❌ Particuliers calculation failed: {calc_response.status_code}")
        print(calc_response.text)
        return
    
    calc = calc_response.json()
    print(f"✅ Particuliers calculation successful:")
    print(f"   Kit power: {calc['kit_power']}kW")
    print(f"   Autoconsumption aid: {calc['autoconsumption_aid']}€")
    print(f"   Client mode: {calc['client_mode']}")
    
    aids_config = calc.get("aids_config", {})
    print(f"   Aids config: {aids_config}")

if __name__ == "__main__":
    print("🔍 Debugging Professional Version Issues")
    print("=" * 50)
    
    print("\n1. Testing Professional Prime Calculation:")
    test_professional_prime_issue()
    
    print("\n2. Testing Particuliers Calculation:")
    test_particuliers_calculation()