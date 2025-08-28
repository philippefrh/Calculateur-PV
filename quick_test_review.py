#!/usr/bin/env python3
"""
Quick Backend Test for Review Request
Test /api/calculate endpoint with specific data:
- région: france
- surface: 50m²
- orientation: Sud
- chauffage: électrique
- consommation: 150kWh/mois
Verify backend responds correctly and battery_selected data is present
"""

import requests
import json
import time

# Backend URL from frontend environment
BACKEND_URL = "https://solar-calculator-ui.preview.emergentagent.com/api"

def test_review_request():
    """Test the specific scenario requested in the review"""
    print("🔍 QUICK BACKEND TEST FOR REVIEW REQUEST")
    print("=" * 60)
    print("Testing /api/calculate with:")
    print("- région: france")
    print("- surface: 50m²")
    print("- orientation: Sud")
    print("- chauffage: électrique")
    print("- consommation: 150kWh/mois")
    print("=" * 60)
    
    session = requests.Session()
    
    # Step 1: Create test client with specified data
    print("\n1️⃣ Creating test client...")
    client_data = {
        "first_name": "Test",
        "last_name": "Review",
        "address": "75001 Paris, France",
        "phone": "0123456789",
        "email": "test.review@example.com",
        "roof_surface": 50.0,  # 50m²
        "roof_orientation": "Sud",  # Sud orientation
        "velux_count": 0,
        "heating_system": "Radiateurs électriques",  # chauffage électrique
        "water_heating_system": "Ballon électrique standard",
        "water_heating_capacity": 200,
        "annual_consumption_kwh": 1800.0,  # 150kWh/mois × 12 = 1800kWh/an
        "monthly_edf_payment": 150.0,  # 150€/mois
        "annual_edf_payment": 1800.0
    }
    
    try:
        response = session.post(f"{BACKEND_URL}/clients", json=client_data)
        if response.status_code == 200:
            client = response.json()
            client_id = client.get("id")
            print(f"✅ Client created successfully: {client_id}")
            print(f"   Coordinates: {client.get('latitude'):.4f}, {client.get('longitude'):.4f}")
        else:
            print(f"❌ Failed to create client: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error creating client: {e}")
        return False
    
    # Step 2: Test /api/calculate endpoint for France region
    print("\n2️⃣ Testing /api/calculate endpoint for France...")
    try:
        response = session.post(f"{BACKEND_URL}/calculate/{client_id}?region=france")
        if response.status_code == 200:
            calculation = response.json()
            print("✅ /api/calculate endpoint working correctly")
            
            # Extract key data
            kit_power = calculation.get("kit_power", 0)
            estimated_production = calculation.get("estimated_production", 0)
            monthly_savings = calculation.get("monthly_savings", 0)
            autonomy_percentage = calculation.get("autonomy_percentage", 0)
            kit_price = calculation.get("kit_price", 0)
            
            print(f"   Kit recommended: {kit_power}kW")
            print(f"   Annual production: {estimated_production:.0f} kWh")
            print(f"   Monthly savings: {monthly_savings:.2f}€")
            print(f"   Autonomy: {autonomy_percentage:.1f}%")
            print(f"   Kit price: {kit_price}€")
            
        else:
            print(f"❌ /api/calculate failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing /api/calculate: {e}")
        return False
    
    # Step 3: Test battery_selected functionality (KEY REQUIREMENT)
    print("\n3️⃣ Testing battery_selected functionality...")
    
    # Test without battery
    try:
        response_no_battery = session.post(f"{BACKEND_URL}/calculate/{client_id}?region=france&battery_selected=false")
        if response_no_battery.status_code == 200:
            calc_no_battery = response_no_battery.json()
            print("✅ Calculation without battery successful")
            
            battery_selected_no = calc_no_battery.get("battery_selected", None)
            battery_cost_no = calc_no_battery.get("battery_cost", None)
            kit_price_final_no = calc_no_battery.get("kit_price_final", None)
            
            print(f"   battery_selected: {battery_selected_no}")
            print(f"   battery_cost: {battery_cost_no}€")
            print(f"   kit_price_final: {kit_price_final_no}€")
            
        else:
            print(f"❌ Calculation without battery failed: {response_no_battery.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing without battery: {e}")
        return False
    
    # Test with battery
    try:
        response_with_battery = session.post(f"{BACKEND_URL}/calculate/{client_id}?region=france&battery_selected=true")
        if response_with_battery.status_code == 200:
            calc_with_battery = response_with_battery.json()
            print("✅ Calculation with battery successful")
            
            battery_selected_yes = calc_with_battery.get("battery_selected", None)
            battery_cost_yes = calc_with_battery.get("battery_cost", None)
            kit_price_final_yes = calc_with_battery.get("kit_price_final", None)
            
            print(f"   battery_selected: {battery_selected_yes}")
            print(f"   battery_cost: {battery_cost_yes}€")
            print(f"   kit_price_final: {kit_price_final_yes}€")
            
            # Verify battery functionality
            if battery_selected_yes == True and battery_cost_yes == 5000:
                print("✅ Battery functionality working correctly")
                print(f"   Price increase: {kit_price_final_yes - kit_price_final_no}€ (+5000€ expected)")
            else:
                print("❌ Battery functionality not working correctly")
                return False
            
        else:
            print(f"❌ Calculation with battery failed: {response_with_battery.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing with battery: {e}")
        return False
    
    # Step 4: Verify all required data fields are present
    print("\n4️⃣ Verifying required data fields for product images...")
    
    required_fields = [
        "battery_selected", "battery_cost", "kit_price_final", 
        "kit_power", "estimated_production", "autonomy_percentage",
        "financing_options", "region"
    ]
    
    missing_fields = []
    for field in required_fields:
        if field not in calc_with_battery:
            missing_fields.append(field)
    
    if missing_fields:
        print(f"❌ Missing required fields: {missing_fields}")
        return False
    else:
        print("✅ All required data fields present for conditional image display")
        print(f"   Total fields returned: {len(calc_with_battery.keys())}")
    
    # Step 5: Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print("✅ Backend API accessible and responding correctly")
    print("✅ /api/calculate endpoint working with test data")
    print("✅ battery_selected functionality working correctly")
    print("✅ All required data present for conditional battery image display")
    print("✅ Application ready for product images integration")
    
    print(f"\n🎯 KEY RESULTS:")
    print(f"   - France region: {kit_power}kW kit recommended")
    print(f"   - Annual production: {estimated_production:.0f} kWh")
    print(f"   - Without battery: {kit_price_final_no}€")
    print(f"   - With battery: {kit_price_final_yes}€ (+{battery_cost_yes}€)")
    print(f"   - battery_selected parameter working correctly")
    
    return True

if __name__ == "__main__":
    success = test_review_request()
    if success:
        print("\n🎉 ALL TESTS PASSED - Backend ready for production!")
    else:
        print("\n❌ SOME TESTS FAILED - Check issues above")
    exit(0 if success else 1)