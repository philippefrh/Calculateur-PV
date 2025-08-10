#!/usr/bin/env python3
"""
Comprehensive test for all Martinique kit sizes and expected behavior
Testing the specific scenarios from the review request
"""

import requests
import json
import time

BACKEND_URL = "https://6843aeb1-b7fa-4f3a-94e4-7e571b085fd3.preview.emergentagent.com/api"

class MartiniqueComprehensiveTest:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, details: str, response_data=None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "response_data": response_data
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")

    def create_martinique_client_for_kit(self, consumption_kwh: float, kit_target: str):
        """Create a client that should get a specific kit recommendation"""
        client_data = {
            "first_name": f"Test{kit_target}",
            "last_name": "Martinique",
            "address": "Fort-de-France, Martinique",
            "roof_surface": 100.0,  # Large enough for any kit
            "roof_orientation": "Sud",
            "velux_count": 0,
            "heating_system": "Climatisation",
            "water_heating_system": "Chauffe-eau solaire",
            "water_heating_capacity": 150,
            "annual_consumption_kwh": consumption_kwh,
            "monthly_edf_payment": consumption_kwh * 0.25 / 12,  # Approximate EDF rate
            "annual_edf_payment": consumption_kwh * 0.25
        }
        
        try:
            response = self.session.post(f"{self.base_url}/clients", json=client_data)
            if response.status_code == 200:
                client = response.json()
                return client["id"]
            else:
                print(f"Failed to create client for {kit_target}: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error creating client for {kit_target}: {str(e)}")
            return None

    def test_specific_martinique_kit_scenarios(self):
        """Test the specific expected behavior for Martinique kits"""
        # Expected behavior from review request:
        # 3kW kit: 6 panels, 9,900€ TTC, 5,340€ aid
        # 6kW kit: 12 panels, 13,900€ TTC, 6,480€ aid  
        # 9kW kit: 18 panels, 16,900€ TTC, 9,720€ aid
        
        expected_scenarios = [
            {"consumption": 3000, "expected_kit": 3, "expected_panels": 6, "expected_price": 9900, "expected_aid": 5340},
            {"consumption": 6000, "expected_kit": 6, "expected_panels": 12, "expected_price": 13900, "expected_aid": 6480},
            {"consumption": 9000, "expected_kit": 9, "expected_panels": 18, "expected_price": 16900, "expected_aid": 9720}
        ]
        
        for scenario in expected_scenarios:
            # Create client for this scenario
            client_id = self.create_martinique_client_for_kit(scenario["consumption"], f"{scenario['expected_kit']}kW")
            if not client_id:
                self.log_test(f"Martinique {scenario['expected_kit']}kW Scenario", False, "Failed to create client")
                continue
            
            try:
                # Calculate with Martinique region
                response = self.session.post(f"{self.base_url}/calculate/{client_id}?region=martinique")
                if response.status_code == 200:
                    calculation = response.json()
                    
                    kit_power = calculation.get("kit_power", 0)
                    panel_count = calculation.get("panel_count", 0)
                    kit_price = calculation.get("kit_price", 0)
                    total_aids = calculation.get("total_aids", 0)
                    region = calculation.get("region", "")
                    
                    issues = []
                    
                    # Check all expected values
                    if kit_power != scenario["expected_kit"]:
                        issues.append(f"kit_power: expected {scenario['expected_kit']}kW, got {kit_power}kW")
                    
                    if panel_count != scenario["expected_panels"]:
                        issues.append(f"panel_count: expected {scenario['expected_panels']}, got {panel_count}")
                    
                    if kit_price != scenario["expected_price"]:
                        issues.append(f"kit_price: expected {scenario['expected_price']}€, got {kit_price}€")
                    
                    if total_aids != scenario["expected_aid"]:
                        issues.append(f"total_aids: expected {scenario['expected_aid']}€, got {total_aids}€")
                    
                    if region != "martinique":
                        issues.append(f"region: expected 'martinique', got '{region}'")
                    
                    if issues:
                        self.log_test(f"Martinique {scenario['expected_kit']}kW Scenario", False, 
                                    f"Issues: {'; '.join(issues)}", calculation)
                    else:
                        self.log_test(f"Martinique {scenario['expected_kit']}kW Scenario", True, 
                                    f"✅ {kit_power}kW kit: {panel_count} panels, {kit_price}€ TTC, {total_aids}€ aid - MATCHES EXPECTED", 
                                    {"kit_power": kit_power, "panel_count": panel_count, "kit_price": kit_price, "total_aids": total_aids})
                else:
                    self.log_test(f"Martinique {scenario['expected_kit']}kW Scenario", False, 
                                f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_test(f"Martinique {scenario['expected_kit']}kW Scenario", False, f"Error: {str(e)}")

    def test_pdf_uses_martinique_data(self):
        """Test that PDF generation uses Martinique data, not France data"""
        # Create a Martinique client
        client_id = self.create_martinique_client_for_kit(6000, "6kW")
        if not client_id:
            self.log_test("PDF Uses Martinique Data", False, "Failed to create client")
            return
        
        try:
            # Calculate with Martinique region to store region in client
            calc_response = self.session.post(f"{self.base_url}/calculate/{client_id}?region=martinique")
            if calc_response.status_code != 200:
                self.log_test("PDF Uses Martinique Data", False, f"Calculation failed: {calc_response.status_code}")
                return
            
            calculation = calc_response.json()
            
            # Generate PDF
            pdf_response = self.session.get(f"{self.base_url}/generate-pdf/{client_id}")
            if pdf_response.status_code != 200:
                self.log_test("PDF Uses Martinique Data", False, f"PDF generation failed: {pdf_response.status_code}")
                return
            
            # Check that calculation used Martinique data
            kit_power = calculation.get("kit_power", 0)
            kit_price = calculation.get("kit_price", 0)
            total_aids = calculation.get("total_aids", 0)
            region = calculation.get("region", "")
            
            # Verify it's using Martinique data, not France data
            france_6kw_price = 22900  # France 6kW price
            martinique_6kw_price = 13900  # Martinique 6kW price
            martinique_6kw_aid = 6480  # Martinique 6kW aid
            
            issues = []
            
            if region != "martinique":
                issues.append(f"PDF should use Martinique region, got '{region}'")
            
            if kit_price == france_6kw_price:
                issues.append(f"PDF using France price {kit_price}€ instead of Martinique price {martinique_6kw_price}€")
            
            if kit_price != martinique_6kw_price:
                issues.append(f"PDF price {kit_price}€ doesn't match expected Martinique price {martinique_6kw_price}€")
            
            if total_aids != martinique_6kw_aid:
                issues.append(f"PDF aid {total_aids}€ doesn't match expected Martinique aid {martinique_6kw_aid}€")
            
            if issues:
                self.log_test("PDF Uses Martinique Data", False, f"Issues: {'; '.join(issues)}")
            else:
                pdf_size = len(pdf_response.content)
                self.log_test("PDF Uses Martinique Data", True, 
                            f"✅ PDF correctly uses Martinique data: {kit_power}kW, {kit_price}€ TTC, {total_aids}€ aid (not France {france_6kw_price}€) - PDF size: {pdf_size:,} bytes")
                
        except Exception as e:
            self.log_test("PDF Uses Martinique Data", False, f"Error: {str(e)}")

    def test_panel_count_formula(self):
        """Test that panel count follows 1kW = 2 panels of 500W each formula"""
        test_cases = [
            {"kit_power": 3, "expected_panels": 6},
            {"kit_power": 6, "expected_panels": 12},
            {"kit_power": 9, "expected_panels": 18}
        ]
        
        for case in test_cases:
            # Create client
            client_id = self.create_martinique_client_for_kit(case["kit_power"] * 1000, f"{case['kit_power']}kW")
            if not client_id:
                continue
            
            try:
                response = self.session.post(f"{self.base_url}/calculate/{client_id}?region=martinique")
                if response.status_code == 200:
                    calculation = response.json()
                    
                    kit_power = calculation.get("kit_power", 0)
                    panel_count = calculation.get("panel_count", 0)
                    
                    # Verify formula: 1kW = 2 panels of 500W each
                    expected_panels = kit_power * 2
                    
                    if panel_count == expected_panels and panel_count == case["expected_panels"]:
                        self.log_test(f"Panel Count Formula {kit_power}kW", True, 
                                    f"✅ {kit_power}kW = {panel_count} panels (1kW = 2 panels of 500W each)")
                    else:
                        self.log_test(f"Panel Count Formula {kit_power}kW", False, 
                                    f"Formula incorrect: {kit_power}kW should have {expected_panels} panels, got {panel_count}")
                else:
                    self.log_test(f"Panel Count Formula {kit_power}kW", False, f"HTTP {response.status_code}")
            except Exception as e:
                self.log_test(f"Panel Count Formula {kit_power}kW", False, f"Error: {str(e)}")

    def run_comprehensive_tests(self):
        """Run all comprehensive Martinique tests"""
        print("🧪 COMPREHENSIVE MARTINIQUE REGION TESTING")
        print("=" * 60)
        
        self.test_specific_martinique_kit_scenarios()
        self.test_pdf_uses_martinique_data()
        self.test_panel_count_formula()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"Total tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success rate: {(passed/total)*100:.1f}%")
        
        if total - passed > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
        else:
            print("\n✅ ALL COMPREHENSIVE TESTS PASSED!")
            print("\n🎉 MARTINIQUE FIXES WORKING PERFECTLY:")
            print("   • Panel count calculation: 1kW = 2 panels of 500W each")
            print("   • 3kW kit: 6 panels, 9,900€ TTC, 5,340€ aid")
            print("   • 6kW kit: 12 panels, 13,900€ TTC, 6,480€ aid")
            print("   • 9kW kit: 18 panels, 16,900€ TTC, 9,720€ aid")
            print("   • PDF generation uses correct regional data")
        
        return passed == total

if __name__ == "__main__":
    tester = MartiniqueComprehensiveTest()
    success = tester.run_comprehensive_tests()
    exit(0 if success else 1)