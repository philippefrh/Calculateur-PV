#!/usr/bin/env python3
"""
Test Martinique Region Functionality
Verify new pricing, 375W panels, and 8.63% interest rate
"""

import requests
import json

# Backend URL from frontend environment
BACKEND_URL = "https://solar-quote-genius.preview.emergentagent.com/api"

def test_martinique_region():
    """Test Martinique region with new pricing and configurations"""
    print("🔍 TESTING MARTINIQUE REGION FUNCTIONALITY")
    print("=" * 80)
    
    session = requests.Session()
    results = []
    
    # Test 1: Martinique Kits Endpoint
    print("\n1️⃣ Testing Martinique Kits Endpoint...")
    try:
        response = session.get(f"{BACKEND_URL}/regions/martinique/kits")
        if response.status_code == 200:
            data = response.json()
            kits = data.get("kits", [])
            
            if len(kits) == 9:  # Should have 9 kits now
                print(f"✅ Found {len(kits)} Martinique kits")
                
                # Check specific kit pricing
                expected_kits = {
                    "kit_3kw": {"power": 3, "price_ttc": 10900, "aid_amount": 5340, "panels": 8},
                    "kit_6kw": {"power": 6, "price_ttc": 15900, "aid_amount": 6480, "panels": 16},
                    "kit_9kw": {"power": 9, "price_ttc": 18900, "aid_amount": 9720, "panels": 24},
                    "kit_12kw": {"power": 12, "price_ttc": 22900, "aid_amount": 9720, "panels": 32},
                    "kit_15kw": {"power": 15, "price_ttc": 25900, "aid_amount": 12150, "panels": 40},
                    "kit_18kw": {"power": 18, "price_ttc": 28900, "aid_amount": 14580, "panels": 48},
                    "kit_21kw": {"power": 21, "price_ttc": 30900, "aid_amount": 17010, "panels": 56},
                    "kit_24kw": {"power": 24, "price_ttc": 32900, "aid_amount": 19440, "panels": 64},
                    "kit_27kw": {"power": 27, "price_ttc": 34900, "aid_amount": 21870, "panels": 72}
                }
                
                # Verify each kit
                kit_dict = {kit["id"]: kit for kit in kits}
                issues = []
                
                for kit_id, expected in expected_kits.items():
                    if kit_id in kit_dict:
                        kit = kit_dict[kit_id]
                        for field, expected_value in expected.items():
                            if kit.get(field) != expected_value:
                                issues.append(f"{kit_id}.{field}: expected {expected_value}, got {kit.get(field)}")
                    else:
                        issues.append(f"Missing kit: {kit_id}")
                
                if issues:
                    print(f"❌ Kit validation issues: {'; '.join(issues[:3])}...")  # Show first 3 issues
                    results.append(("Martinique Kits", False, f"Validation issues: {len(issues)} found"))
                else:
                    print("✅ All 9 kits have correct pricing and panel counts")
                    results.append(("Martinique Kits", True, "9 kits with correct NEW pricing (10900€-34900€) and 375W panel counts"))
            else:
                print(f"❌ Expected 9 kits, found {len(kits)}")
                results.append(("Martinique Kits", False, f"Expected 9 kits, found {len(kits)}"))
        else:
            print(f"❌ Failed to get kits: HTTP {response.status_code}")
            results.append(("Martinique Kits", False, f"HTTP {response.status_code}"))
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        results.append(("Martinique Kits", False, f"Error: {str(e)}"))
    
    # Test 2: Create Martinique Client
    print("\n2️⃣ Creating Martinique test client...")
    client_data = {
        "first_name": "Marcel",
        "last_name": "RETAILLEAU", 
        "address": "Fort-de-France, Martinique",
        "phone": "0596123456",
        "email": "marcel.retailleau@example.com",
        "roof_surface": 50.0,
        "roof_orientation": "Sud",
        "velux_count": 1,
        "heating_system": "Climatisation",
        "water_heating_system": "Chauffe-eau solaire",
        "water_heating_capacity": 200,
        "annual_consumption_kwh": 4500.0,
        "monthly_edf_payment": 120.0,
        "annual_edf_payment": 1440.0
    }
    
    client_id = None
    try:
        response = session.post(f"{BACKEND_URL}/clients", json=client_data)
        if response.status_code == 200:
            client = response.json()
            client_id = client.get("id")
            print(f"✅ Martinique client created: {client_id}")
            results.append(("Martinique Client Creation", True, f"Client ID: {client_id}"))
        else:
            print(f"❌ Failed to create client: {response.status_code}")
            results.append(("Martinique Client Creation", False, f"HTTP {response.status_code}"))
            return results
    except Exception as e:
        print(f"❌ Client creation error: {str(e)}")
        results.append(("Martinique Client Creation", False, f"Error: {str(e)}"))
        return results
    
    # Test 3: Martinique Calculation with New Pricing
    print("\n3️⃣ Testing Martinique calculation with new pricing...")
    try:
        response = session.post(f"{BACKEND_URL}/calculate/{client_id}?region=martinique&calculation_mode=realistic")
        if response.status_code == 200:
            calculation = response.json()
            
            # Extract key values
            region = calculation.get("region")
            kit_power = calculation.get("kit_power", 0)
            panel_count = calculation.get("panel_count", 0)
            kit_price = calculation.get("kit_price", 0)
            total_aids = calculation.get("total_aids", 0)
            estimated_production = calculation.get("estimated_production", 0)
            financing_options = calculation.get("financing_options", [])
            
            print(f"   - Region: {region}")
            print(f"   - Recommended kit: {kit_power} kW")
            print(f"   - Panel count: {panel_count} panels")
            print(f"   - Kit price: {kit_price}€")
            print(f"   - Total aids: {total_aids}€")
            print(f"   - Annual production: {estimated_production:.0f} kWh")
            
            # Validation
            issues = []
            
            # Check region
            if region != "martinique":
                issues.append(f"Expected region 'martinique', got '{region}'")
            
            # Check 375W panel calculation (1kW = 2.67 panels)
            expected_panels = round(kit_power * 2.67)  # 375W panels
            if abs(panel_count - expected_panels) > 1:
                issues.append(f"Panel count {panel_count} != expected {expected_panels} for {kit_power}kW (375W panels)")
            
            # Check if kit power is valid for Martinique (3, 6, 9, 12, 15, 18, 21, 24, 27)
            valid_powers = [3, 6, 9, 12, 15, 18, 21, 24, 27]
            if kit_power not in valid_powers:
                issues.append(f"Kit power {kit_power} not in valid Martinique range {valid_powers}")
            
            # Check pricing matches new structure
            expected_prices = {3: 10900, 6: 15900, 9: 18900, 12: 22900, 15: 25900, 18: 28900, 21: 30900, 24: 32900, 27: 34900}
            if kit_price != expected_prices.get(kit_power, 0):
                issues.append(f"Kit price {kit_price}€ != expected {expected_prices.get(kit_power, 0)}€ for {kit_power}kW")
            
            # Check aids
            expected_aids = {3: 5340, 6: 6480, 9: 9720, 12: 9720, 15: 12150, 18: 14580, 21: 17010, 24: 19440, 27: 21870}
            if total_aids != expected_aids.get(kit_power, 0):
                issues.append(f"Total aids {total_aids}€ != expected {expected_aids.get(kit_power, 0)}€ for {kit_power}kW")
            
            # Check 8.63% interest rate
            if financing_options:
                first_option = financing_options[0]
                taeg = first_option.get("taeg", 0)
                if abs(taeg - 0.0863) > 0.001:  # Allow small floating point difference
                    issues.append(f"TAEG {taeg:.4f} != expected 0.0863 (8.63%)")
            
            if issues:
                print(f"❌ Calculation issues: {'; '.join(issues)}")
                results.append(("Martinique Calculation", False, f"Issues: {'; '.join(issues[:2])}..."))
            else:
                print(f"✅ Martinique calculation working with new pricing")
                results.append(("Martinique Calculation", True, f"{kit_power}kW kit, {panel_count} panels (375W), {kit_price}€ price, {total_aids}€ aids, 8.63% TAEG"))
                
        else:
            print(f"❌ Calculation failed: HTTP {response.status_code}")
            results.append(("Martinique Calculation", False, f"HTTP {response.status_code}"))
    except Exception as e:
        print(f"❌ Calculation error: {str(e)}")
        results.append(("Martinique Calculation", False, f"Error: {str(e)}"))
    
    return results

def main():
    """Main test execution"""
    print("🚀 MARTINIQUE REGION TEST")
    print("Testing new pricing structure, 375W panels, and 8.63% interest rate")
    
    results = test_martinique_region()
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 MARTINIQUE REGION TEST SUMMARY")
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
        print("🎉 MARTINIQUE REGION WORKING PERFECTLY!")
        print("✅ 9 new kits with updated pricing (10900€-34900€)")
        print("✅ 375W panels calculation (1kW = 2.67 panels)")
        print("✅ 8.63% interest rate applied")
        print("✅ Correct aid amounts per kit")
    else:
        print("⚠️  MARTINIQUE REGION HAS ISSUES")
        print("❌ Check the failed tests above for details")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)