#!/usr/bin/env python3
"""
Test the R1/R2/R3 Discount System
Verify that discounts are properly applied in calculations
"""

import requests
import json

# Backend URL from frontend environment
BACKEND_URL = "https://9e1efce5-d20a-4c8f-a111-3bf11f62fddb.preview.emergentagent.com/api"

def test_discount_system():
    """Test the R1/R2/R3 discount system with different discount amounts"""
    print("🔍 TESTING R1/R2/R3 DISCOUNT SYSTEM")
    print("=" * 80)
    
    session = requests.Session()
    results = []
    
    # First create a test client
    print("\n1️⃣ Creating test client...")
    client_data = {
        "first_name": "Marie",
        "last_name": "Martin", 
        "address": "Lyon, France",
        "phone": "0123456789",
        "email": "marie.martin@example.com",
        "roof_surface": 80.0,
        "roof_orientation": "Sud",
        "velux_count": 1,
        "heating_system": "Radiateurs électriques",
        "water_heating_system": "Ballon électrique",
        "water_heating_capacity": 200,
        "annual_consumption_kwh": 6000.0,
        "monthly_edf_payment": 180.0,
        "annual_edf_payment": 2160.0
    }
    
    try:
        response = session.post(f"{BACKEND_URL}/clients", json=client_data)
        if response.status_code == 200:
            client = response.json()
            client_id = client.get("id")
            print(f"✅ Client created: {client_id}")
        else:
            print(f"❌ Failed to create client: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Client creation error: {str(e)}")
        return []
    
    # Test different discount scenarios
    discount_tests = [
        {"name": "No Discount (Baseline)", "discount_amount": 0, "expected_reduction": 0},
        {"name": "R1 Discount", "discount_amount": 1000, "expected_reduction": 1000},
        {"name": "R2 Discount", "discount_amount": 2000, "expected_reduction": 2000},
        {"name": "R3 Discount", "discount_amount": 3000, "expected_reduction": 3000}
    ]
    
    baseline_kit_price = None
    baseline_monthly_payment = None
    
    for i, test in enumerate(discount_tests, 2):
        print(f"\n{i}️⃣ Testing {test['name']} ({test['discount_amount']}€)...")
        
        try:
            # Make calculation request with discount
            params = {
                "region": "france",
                "calculation_mode": "realistic"
            }
            if test['discount_amount'] > 0:
                params["discount_amount"] = test['discount_amount']
            
            response = session.post(f"{BACKEND_URL}/calculate/{client_id}", params=params)
            
            if response.status_code == 200:
                calculation = response.json()
                
                # Extract key values
                kit_price_original = calculation.get("kit_price_original", 0)
                kit_price_final = calculation.get("kit_price_final", 0)
                discount_applied = calculation.get("discount_applied", 0)
                financing_with_aids = calculation.get("financing_with_aids", {})
                monthly_payment = financing_with_aids.get("monthly_payment", 0)
                
                # Store baseline for comparison
                if test['discount_amount'] == 0:
                    baseline_kit_price = kit_price_original
                    baseline_monthly_payment = monthly_payment
                
                # Verify discount application
                expected_final_price = kit_price_original - test['discount_amount']
                actual_discount = kit_price_original - kit_price_final
                
                print(f"   - Original kit price: {kit_price_original}€")
                print(f"   - Discount applied: {discount_applied}€")
                print(f"   - Final kit price: {kit_price_final}€")
                print(f"   - Monthly payment with aids: {monthly_payment:.2f}€")
                
                # Validation
                issues = []
                
                # Check discount_applied field
                if discount_applied != test['discount_amount']:
                    issues.append(f"discount_applied {discount_applied}€ != expected {test['discount_amount']}€")
                
                # Check final price calculation
                if abs(kit_price_final - expected_final_price) > 1:
                    issues.append(f"kit_price_final {kit_price_final}€ != expected {expected_final_price}€")
                
                # Check actual discount
                if abs(actual_discount - test['discount_amount']) > 1:
                    issues.append(f"actual discount {actual_discount}€ != expected {test['discount_amount']}€")
                
                # Compare with baseline (if not baseline)
                if baseline_monthly_payment and test['discount_amount'] > 0:
                    expected_payment_reduction = baseline_monthly_payment - monthly_payment
                    if expected_payment_reduction <= 0:
                        issues.append(f"monthly payment should be reduced from baseline {baseline_monthly_payment:.2f}€")
                    else:
                        print(f"   - Payment reduction vs baseline: {expected_payment_reduction:.2f}€/month")
                
                if issues:
                    print(f"❌ Issues found: {'; '.join(issues)}")
                    results.append((test['name'], False, f"Issues: {'; '.join(issues)}"))
                else:
                    print(f"✅ Discount system working correctly")
                    if test['discount_amount'] > 0:
                        payment_reduction = baseline_monthly_payment - monthly_payment if baseline_monthly_payment else 0
                        results.append((test['name'], True, f"{test['discount_amount']}€ discount → {kit_price_final}€ final price, {payment_reduction:.2f}€/month reduction"))
                    else:
                        results.append((test['name'], True, f"Baseline: {kit_price_original}€ price, {monthly_payment:.2f}€/month"))
                        
            else:
                print(f"❌ Calculation failed: HTTP {response.status_code}")
                print(f"   Response: {response.text}")
                results.append((test['name'], False, f"HTTP {response.status_code}: {response.text}"))
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            results.append((test['name'], False, f"Error: {str(e)}"))
    
    return results

def main():
    """Main test execution"""
    print("🚀 R1/R2/R3 DISCOUNT SYSTEM TEST")
    print("Testing that discounts (1000€, 2000€, 3000€) are properly applied in calculations")
    
    results = test_discount_system()
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 DISCOUNT SYSTEM TEST SUMMARY")
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
        print("🎉 DISCOUNT SYSTEM WORKING PERFECTLY!")
        print("✅ R1 (1000€), R2 (2000€), R3 (3000€) discounts properly applied")
        print("✅ Kit prices reduced correctly")
        print("✅ Monthly payments adjusted accordingly")
    else:
        print("⚠️  DISCOUNT SYSTEM HAS ISSUES")
        print("❌ Check the failed tests above for details")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)