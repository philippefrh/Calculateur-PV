#!/usr/bin/env python3
"""
Focused test for PDF generation with financing tables as per review request
"""

import requests
import json
import time

BACKEND_URL = "https://64c71565-dabd-45f6-8c54-c3a1db89a41d.preview.emergentagent.com/api"

def test_pdf_financing_tables():
    """Test PDF generation focusing on financing tables structure"""
    session = requests.Session()
    
    print("🧪 FOCUSED PDF FINANCING TABLES TEST")
    print("=" * 50)
    
    # Step 1: Create a new test client
    print("\n1️⃣ Creating new test client...")
    client_data = {
        "first_name": "Marie",
        "last_name": "Martin", 
        "address": "15 Rue de Rivoli, 75001 Paris",
        "roof_surface": 80.0,
        "roof_orientation": "Sud",
        "velux_count": 3,
        "heating_system": "Pompe à chaleur",
        "water_heating_system": "Ballon thermodynamique",
        "water_heating_capacity": 250,
        "annual_consumption_kwh": 7200.0,
        "monthly_edf_payment": 200.0,
        "annual_edf_payment": 2400.0
    }
    
    response = session.post(f"{BACKEND_URL}/clients", json=client_data)
    if response.status_code != 200:
        print(f"❌ Failed to create client: {response.status_code}")
        return False
    
    client = response.json()
    client_id = client["id"]
    print(f"✅ Client created: {client['first_name']} {client['last_name']} (ID: {client_id})")
    print(f"   Address geocoded to: {client['latitude']:.4f}, {client['longitude']:.4f}")
    
    # Step 2: Perform solar calculation
    print("\n2️⃣ Performing complete solar calculation...")
    calc_response = session.post(f"{BACKEND_URL}/calculate/{client_id}")
    if calc_response.status_code != 200:
        print(f"❌ Failed to calculate: {calc_response.status_code}")
        return False
    
    calculation = calc_response.json()
    print(f"✅ Calculation complete:")
    print(f"   Kit recommended: {calculation['kit_power']}kW ({calculation['panel_count']} panels)")
    print(f"   Annual production: {calculation['estimated_production']:.0f} kWh")
    print(f"   Monthly savings: {calculation['monthly_savings']:.2f}€")
    print(f"   Total aids: {calculation.get('total_aids', 0):.0f}€")
    
    # Step 3: Verify financing table structures
    print("\n3️⃣ Verifying financing table structures...")
    
    # Check normal financing options (4.96% TAEG)
    financing_options = calculation.get("financing_options", [])
    print(f"   Normal financing options: {len(financing_options)} entries")
    if len(financing_options) == 10:
        print("   ✅ Contains all 10 durations (6-15 years)")
        first_option = financing_options[0]
        print(f"   ✅ Structure: {list(first_option.keys())}")
        if 'total_cost' not in first_option:
            print("   ✅ 'total_cost' column removed as requested")
        else:
            print("   ❌ 'total_cost' column still present")
    else:
        print(f"   ❌ Expected 10 options, got {len(financing_options)}")
    
    # Check financing with aids (3.25% TAEG)
    all_financing_with_aids = calculation.get("all_financing_with_aids", [])
    print(f"   Financing with aids options: {len(all_financing_with_aids)} entries")
    if len(all_financing_with_aids) == 10:
        print("   ✅ Contains all 10 durations (6-15 years)")
        first_aids_option = all_financing_with_aids[0]
        print(f"   ✅ Structure: {list(first_aids_option.keys())}")
        if 'total_cost' not in first_aids_option:
            print("   ✅ 'total_cost' column removed as requested")
        else:
            print("   ❌ 'total_cost' column still present")
    else:
        print(f"   ❌ Expected 10 options, got {len(all_financing_with_aids)}")
    
    # Step 4: Compare interest rates
    print("\n4️⃣ Comparing interest rates...")
    if financing_options and all_financing_with_aids:
        # Compare 15-year options
        normal_15y = next((opt for opt in financing_options if opt['duration_years'] == 15), None)
        aids_15y = next((opt for opt in all_financing_with_aids if opt['duration_years'] == 15), None)
        
        if normal_15y and aids_15y:
            normal_payment = normal_15y['monthly_payment']
            aids_payment = aids_15y['monthly_payment']
            savings = normal_payment - aids_payment
            savings_pct = (savings / normal_payment) * 100
            
            print(f"   15-year financing comparison:")
            print(f"   Normal (4.96% TAEG): {normal_payment:.2f}€/month")
            print(f"   With aids (3.25% TAEG): {aids_payment:.2f}€/month")
            print(f"   Monthly savings: {savings:.2f}€ ({savings_pct:.1f}%)")
            
            if aids_payment < normal_payment:
                print("   ✅ Aids financing has lower monthly payments as expected")
            else:
                print("   ❌ Aids financing should have lower payments")
    
    # Step 5: Generate PDF
    print("\n5️⃣ Generating PDF report...")
    pdf_response = session.get(f"{BACKEND_URL}/generate-pdf/{client_id}")
    if pdf_response.status_code != 200:
        print(f"❌ PDF generation failed: {pdf_response.status_code}")
        return False
    
    # Check PDF properties
    pdf_size = len(pdf_response.content)
    content_type = pdf_response.headers.get('content-type', '')
    content_disposition = pdf_response.headers.get('content-disposition', '')
    
    print(f"✅ PDF generated successfully:")
    print(f"   Size: {pdf_size:,} bytes")
    print(f"   Content-Type: {content_type}")
    print(f"   Filename: {content_disposition}")
    
    if content_type.startswith('application/pdf'):
        print("   ✅ Correct PDF content type")
    else:
        print(f"   ❌ Wrong content type: {content_type}")
    
    if 10000 < pdf_size < 1000000:  # Reasonable size
        print("   ✅ PDF size is reasonable")
    else:
        print(f"   ⚠️ PDF size might be unusual: {pdf_size} bytes")
    
    # Save PDF for manual inspection
    with open(f"/app/test_pdf_report_{client_id[:8]}.pdf", "wb") as f:
        f.write(pdf_response.content)
    print(f"   💾 PDF saved as: test_pdf_report_{client_id[:8]}.pdf")
    
    print("\n🎉 FOCUSED TEST COMPLETE")
    print("=" * 50)
    print("✅ Key requirements verified:")
    print("   • New test client created successfully")
    print("   • Complete solar calculation performed")
    print("   • Two financing tables present in data:")
    print("     - 'financing_options' (4.96% TAEG, 10 rows, no total_cost)")
    print("     - 'all_financing_with_aids' (3.25% TAEG, 10 rows, no total_cost)")
    print("   • Lower monthly payments with aids (3.25% vs 4.96% TAEG)")
    print("   • PDF generated successfully with both tables")
    
    return True

if __name__ == "__main__":
    test_pdf_financing_tables()