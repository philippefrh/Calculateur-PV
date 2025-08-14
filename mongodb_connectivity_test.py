#!/usr/bin/env python3
"""
Quick MongoDB Connectivity Test for Solar Calculator API
Focus on testing client creation and PVGIS calculation as requested
"""

import requests
import json
import time

# Backend URL from frontend environment
BACKEND_URL = "https://eco-quote-solar.preview.emergentagent.com/api"

def test_mongodb_connectivity():
    """Test the specific MongoDB connectivity issue mentioned in the request"""
    print("🔍 TESTING MONGODB CONNECTIVITY - Focus on client creation and PVGIS calculation")
    print("=" * 80)
    
    session = requests.Session()
    results = []
    
    # Test 1: API Root - Basic connectivity
    print("\n1️⃣ Testing API Root Endpoint...")
    try:
        response = session.get(f"{BACKEND_URL}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API accessible: {data.get('message', 'No message')}")
            results.append(("API Root", True, f"Status: {response.status_code}"))
        else:
            print(f"❌ API not accessible: HTTP {response.status_code}")
            results.append(("API Root", False, f"HTTP {response.status_code}"))
            return results
    except Exception as e:
        print(f"❌ API connection failed: {str(e)}")
        results.append(("API Root", False, f"Connection error: {str(e)}"))
        return results
    
    # Test 2: Client Creation - MongoDB Write Test
    print("\n2️⃣ Testing Client Creation (MongoDB Write)...")
    client_data = {
        "first_name": "Jean",
        "last_name": "Dupont", 
        "address": "Paris, France",
        "phone": "0123456789",
        "email": "jean.dupont@example.com",
        "roof_surface": 60.0,
        "roof_orientation": "Sud",
        "velux_count": 2,
        "heating_system": "Radiateurs électriques",
        "water_heating_system": "Ballon électrique",
        "water_heating_capacity": 200,
        "annual_consumption_kwh": 5000.0,
        "monthly_edf_payment": 150.0,
        "annual_edf_payment": 1800.0
    }
    
    try:
        response = session.post(f"{BACKEND_URL}/clients", json=client_data)
        if response.status_code == 200:
            client = response.json()
            client_id = client.get("id")
            if client_id:
                print(f"✅ Client created successfully!")
                print(f"   - Client ID: {client_id}")
                print(f"   - Name: {client.get('first_name')} {client.get('last_name')}")
                print(f"   - Coordinates: {client.get('latitude', 'N/A')}, {client.get('longitude', 'N/A')}")
                results.append(("Client Creation", True, f"Client ID: {client_id}"))
            else:
                print(f"❌ Client created but no ID returned")
                results.append(("Client Creation", False, "No client ID in response"))
                return results
        else:
            print(f"❌ Client creation failed: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            results.append(("Client Creation", False, f"HTTP {response.status_code}: {response.text}"))
            return results
    except Exception as e:
        print(f"❌ Client creation error: {str(e)}")
        results.append(("Client Creation", False, f"Error: {str(e)}"))
        return results
    
    # Test 3: PVGIS Calculation - MongoDB Read + External API
    print("\n3️⃣ Testing PVGIS Calculation (MongoDB Read + PVGIS API)...")
    try:
        # Test with France region and realistic mode as requested
        response = session.post(f"{BACKEND_URL}/calculate/{client_id}?region=france&calculation_mode=realistic")
        if response.status_code == 200:
            calculation = response.json()
            
            # Check key fields
            kit_power = calculation.get("kit_power", 0)
            estimated_production = calculation.get("estimated_production", 0)
            monthly_savings = calculation.get("monthly_savings", 0)
            autonomy_percentage = calculation.get("autonomy_percentage", 0)
            region = calculation.get("region", "unknown")
            calculation_mode = calculation.get("calculation_mode", "unknown")
            
            print(f"✅ PVGIS calculation successful!")
            print(f"   - Region: {region}")
            print(f"   - Calculation mode: {calculation_mode}")
            print(f"   - Recommended kit: {kit_power} kW")
            print(f"   - Annual production: {estimated_production:.0f} kWh")
            print(f"   - Monthly savings: {monthly_savings:.2f} €")
            print(f"   - Autonomy: {autonomy_percentage:.1f}%")
            
            # Verify no 500 errors and reasonable values
            if estimated_production > 0 and monthly_savings > 0:
                results.append(("PVGIS Calculation", True, f"Kit: {kit_power}kW, Production: {estimated_production:.0f} kWh, Savings: {monthly_savings:.2f}€"))
            else:
                results.append(("PVGIS Calculation", False, f"Invalid calculation results: production={estimated_production}, savings={monthly_savings}"))
        else:
            print(f"❌ PVGIS calculation failed: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            results.append(("PVGIS Calculation", False, f"HTTP {response.status_code}: {response.text}"))
    except Exception as e:
        print(f"❌ PVGIS calculation error: {str(e)}")
        results.append(("PVGIS Calculation", False, f"Error: {str(e)}"))
    
    # Test 4: Client Retrieval - MongoDB Read Test
    print("\n4️⃣ Testing Client Retrieval (MongoDB Read)...")
    try:
        response = session.get(f"{BACKEND_URL}/clients/{client_id}")
        if response.status_code == 200:
            client = response.json()
            print(f"✅ Client retrieved successfully!")
            print(f"   - Name: {client.get('first_name')} {client.get('last_name')}")
            print(f"   - Address: {client.get('address')}")
            results.append(("Client Retrieval", True, f"Retrieved client: {client.get('first_name')} {client.get('last_name')}"))
        else:
            print(f"❌ Client retrieval failed: HTTP {response.status_code}")
            results.append(("Client Retrieval", False, f"HTTP {response.status_code}"))
    except Exception as e:
        print(f"❌ Client retrieval error: {str(e)}")
        results.append(("Client Retrieval", False, f"Error: {str(e)}"))
    
    return results

def main():
    """Main test execution"""
    print("🚀 MONGODB CONNECTIVITY TEST - Solar Calculator API")
    print("Testing client creation and PVGIS calculation to verify MongoDB fix")
    print("Previous issue: 500 error due to mongodb:27017 -> Now configured to localhost:27017")
    
    results = test_mongodb_connectivity()
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    
    passed = 0
    failed = 0
    
    for test_name, success, details in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        if success:
            passed += 1
        else:
            failed += 1
    
    print(f"\n🎯 RESULTS: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 ALL TESTS PASSED - MongoDB connectivity issue appears to be RESOLVED!")
        print("✅ Client creation working (MongoDB write)")
        print("✅ PVGIS calculation working (MongoDB read + external API)")
        print("✅ No 500 errors detected")
    else:
        print("⚠️  SOME TESTS FAILED - MongoDB connectivity issue may still exist")
        print("❌ Check the failed tests above for details")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)