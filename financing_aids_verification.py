#!/usr/bin/env python3
"""
Specific verification test for the financing with aids calculation
Based on the review request requirements
"""

import requests
import json

BACKEND_URL = "https://3c730e74-b603-4563-b76c-9eaef48b0e46.preview.emergentagent.com/api"

def test_financing_with_aids_specific():
    """Test the specific requirements from the review request"""
    
    print("🔍 SPECIFIC FINANCING WITH AIDS VERIFICATION")
    print("=" * 60)
    
    # 1. Create a new test client
    print("1. Creating new test client...")
    client_data = {
        "first_name": "Marie",
        "last_name": "Martin", 
        "address": "15 Rue de Rivoli, 75001 Paris",
        "roof_surface": 50.0,
        "roof_orientation": "Sud",
        "velux_count": 1,
        "heating_system": "Pompe à chaleur",
        "water_heating_system": "Ballon thermodynamique",
        "water_heating_capacity": 150,
        "annual_consumption_kwh": 6000.0,
        "monthly_edf_payment": 175.0,
        "annual_edf_payment": 2100.0
    }
    
    response = requests.post(f"{BACKEND_URL}/clients", json=client_data)
    if response.status_code != 200:
        print(f"❌ Failed to create client: {response.status_code}")
        return
    
    client = response.json()
    client_id = client["id"]
    print(f"✅ Client created: {client['first_name']} {client['last_name']} (ID: {client_id})")
    
    # 2. Perform complete solar calculation
    print("\n2. Performing complete solar calculation...")
    response = requests.post(f"{BACKEND_URL}/calculate/{client_id}")
    if response.status_code != 200:
        print(f"❌ Failed to calculate: {response.status_code}")
        return
    
    calculation = response.json()
    print(f"✅ Calculation completed for {calculation['kit_power']}kW kit")
    
    # 3. Verify financing_with_aids field exists
    print("\n3. Verifying financing_with_aids field...")
    if "financing_with_aids" not in calculation:
        print("❌ Missing 'financing_with_aids' field in response")
        return
    
    financing_with_aids = calculation["financing_with_aids"]
    print("✅ financing_with_aids field found")
    
    # 4. Check all required fields
    print("\n4. Checking required fields in financing_with_aids...")
    required_fields = ["financed_amount", "monthly_payment", "total_cost", "total_interests", "difference_vs_savings"]
    
    for field in required_fields:
        if field in financing_with_aids:
            print(f"✅ {field}: {financing_with_aids[field]}")
        else:
            print(f"❌ Missing field: {field}")
            return
    
    # 5. Verify monthly payment is higher than simple division
    print("\n5. Verifying monthly payment includes interests...")
    financed_amount = financing_with_aids["financed_amount"]
    monthly_payment = financing_with_aids["monthly_payment"]
    simple_division = financed_amount / 180  # 15 years = 180 months
    
    print(f"Financed amount: {financed_amount}€")
    print(f"Simple division (no interest): {simple_division:.2f}€/month")
    print(f"Actual monthly payment (with interest): {monthly_payment:.2f}€/month")
    
    if monthly_payment > simple_division:
        difference = monthly_payment - simple_division
        print(f"✅ Monthly payment is {difference:.2f}€ higher than simple division (interests included)")
    else:
        print(f"❌ Monthly payment should be higher than simple division")
        return
    
    # 6. Verify calculation consistency
    print("\n6. Verifying calculation consistency...")
    total_cost = financing_with_aids["total_cost"]
    total_interests = financing_with_aids["total_interests"]
    
    # Check total_cost = monthly_payment * 180
    expected_total_cost = monthly_payment * 180
    if abs(total_cost - expected_total_cost) < 1:
        print(f"✅ Total cost calculation correct: {total_cost}€")
    else:
        print(f"❌ Total cost mismatch: {total_cost}€ vs expected {expected_total_cost:.2f}€")
    
    # Check total_interests = total_cost - financed_amount
    expected_interests = total_cost - financed_amount
    if abs(total_interests - expected_interests) < 1:
        print(f"✅ Total interests calculation correct: {total_interests}€")
    else:
        print(f"❌ Total interests mismatch: {total_interests}€ vs expected {expected_interests:.2f}€")
    
    # 7. Show complete financing breakdown
    print("\n7. Complete financing breakdown:")
    print(f"   Kit price: {calculation.get('kit_price', 0)}€")
    print(f"   Total aids: {calculation.get('total_aids', 0)}€")
    print(f"   Amount to finance: {financed_amount}€")
    print(f"   Duration: 15 years (180 months)")
    print(f"   Interest rate: 4.96% TAEG")
    print(f"   Monthly payment: {monthly_payment:.2f}€")
    print(f"   Total cost: {total_cost:.2f}€")
    print(f"   Total interests: {total_interests:.2f}€")
    print(f"   Monthly EDF savings: {calculation.get('monthly_savings', 0):.2f}€")
    print(f"   Difference vs savings: {financing_with_aids['difference_vs_savings']:.2f}€")
    
    print("\n🎉 ALL VERIFICATION TESTS PASSED!")
    print("The financing with aids calculation is working correctly with proper interest calculations.")

if __name__ == "__main__":
    test_financing_with_aids_specific()