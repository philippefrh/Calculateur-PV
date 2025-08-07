#!/usr/bin/env python3
"""
Test script for Martinique region fixes:
1. Panel count calculation for Martinique (1kW = 2 panels of 500W each)
2. PDF generation using correct region from client data
"""

import requests
import json
import time
from typing import Dict, Any, Optional

# Backend URL from frontend environment
BACKEND_URL = "https://33eb4c24-76ce-4e41-b0e5-e571dcb4df97.preview.emergentagent.com/api"

class MartiniqueFixes:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.france_client_id = None
        self.martinique_client_id = None
        
    def log_test(self, test_name: str, success: bool, details: str, response_data: Any = None):
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

    def create_test_clients(self):
        """Create test clients for France and Martinique"""
        # Create France client
        france_client_data = {
            "first_name": "Pierre",
            "last_name": "Martin",
            "address": "15 Rue de Rivoli, 75001 Paris",
            "roof_surface": 80.0,
            "roof_orientation": "Sud",
            "velux_count": 1,
            "heating_system": "Radiateurs électriques",
            "water_heating_system": "Ballon électrique",
            "water_heating_capacity": 200,
            "annual_consumption_kwh": 7000.0,
            "monthly_edf_payment": 200.0,
            "annual_edf_payment": 2400.0
        }
        
        # Create Martinique client
        martinique_client_data = {
            "first_name": "Marie",
            "last_name": "Dubois",
            "address": "Fort-de-France, Martinique",
            "roof_surface": 60.0,
            "roof_orientation": "Sud",
            "velux_count": 0,
            "heating_system": "Climatisation",
            "water_heating_system": "Chauffe-eau solaire",
            "water_heating_capacity": 150,
            "annual_consumption_kwh": 5500.0,
            "monthly_edf_payment": 180.0,
            "annual_edf_payment": 2160.0
        }
        
        try:
            # Create France client
            response = self.session.post(f"{self.base_url}/clients", json=france_client_data)
            if response.status_code == 200:
                client = response.json()
                self.france_client_id = client["id"]
                self.log_test("Create France Client", True, f"France client created: {self.france_client_id}")
            else:
                self.log_test("Create France Client", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            # Create Martinique client
            response = self.session.post(f"{self.base_url}/clients", json=martinique_client_data)
            if response.status_code == 200:
                client = response.json()
                self.martinique_client_id = client["id"]
                self.log_test("Create Martinique Client", True, f"Martinique client created: {self.martinique_client_id}")
            else:
                self.log_test("Create Martinique Client", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
            return True
            
        except Exception as e:
            self.log_test("Create Test Clients", False, f"Error: {str(e)}")
            return False

    def test_martinique_panel_count_calculation(self):
        """Test that Martinique panel count is calculated correctly (1kW = 2 panels of 500W each)"""
        if not self.martinique_client_id:
            self.log_test("Martinique Panel Count", False, "No Martinique client ID available")
            return
            
        try:
            response = self.session.post(f"{self.base_url}/calculate/{self.martinique_client_id}?region=martinique")
            if response.status_code == 200:
                calculation = response.json()
                
                kit_power = calculation.get("kit_power", 0)
                panel_count = calculation.get("panel_count", 0)
                
                # Expected panel count: 1kW = 2 panels of 500W each
                expected_panel_count = kit_power * 2
                
                if panel_count == expected_panel_count:
                    self.log_test("Martinique Panel Count", True, 
                                f"✅ Panel count correct for {kit_power}kW kit: {panel_count} panels (1kW = 2 panels of 500W each)", 
                                {"kit_power": kit_power, "panel_count": panel_count, "expected": expected_panel_count})
                else:
                    self.log_test("Martinique Panel Count", False, 
                                f"Panel count incorrect for {kit_power}kW kit: got {panel_count} panels, expected {expected_panel_count} (1kW = 2 panels)", 
                                {"kit_power": kit_power, "panel_count": panel_count, "expected": expected_panel_count})
                    
            else:
                self.log_test("Martinique Panel Count", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Martinique Panel Count", False, f"Error: {str(e)}")

    def test_martinique_kit_calculations(self):
        """Test all Martinique kit calculations with expected panel counts"""
        if not self.martinique_client_id:
            self.log_test("Martinique Kit Calculations", False, "No Martinique client ID available")
            return
            
        try:
            response = self.session.post(f"{self.base_url}/calculate/{self.martinique_client_id}?region=martinique")
            if response.status_code == 200:
                calculation = response.json()
                
                kit_power = calculation.get("kit_power", 0)
                panel_count = calculation.get("panel_count", 0)
                kit_price = calculation.get("kit_price", 0)
                total_aids = calculation.get("total_aids", 0)
                
                # Expected values for Martinique kits
                expected_data = {
                    3: {"panels": 6, "price": 9900, "aid": 5340},
                    6: {"panels": 12, "price": 13900, "aid": 6480},
                    9: {"panels": 18, "price": 16900, "aid": 9720}
                }
                
                if kit_power in expected_data:
                    expected = expected_data[kit_power]
                    issues = []
                    
                    if panel_count != expected["panels"]:
                        issues.append(f"panel_count: got {panel_count}, expected {expected['panels']}")
                    
                    if kit_price != expected["price"]:
                        issues.append(f"kit_price: got {kit_price}€, expected {expected['price']}€")
                    
                    if total_aids != expected["aid"]:
                        issues.append(f"total_aids: got {total_aids}€, expected {expected['aid']}€")
                    
                    if issues:
                        self.log_test("Martinique Kit Calculations", False, 
                                    f"Issues with {kit_power}kW kit: {'; '.join(issues)}", 
                                    calculation)
                    else:
                        self.log_test("Martinique Kit Calculations", True, 
                                    f"✅ {kit_power}kW kit calculation correct: {panel_count} panels, {kit_price}€ TTC, {total_aids}€ aid", 
                                    {"kit_power": kit_power, "panel_count": panel_count, "kit_price": kit_price, "total_aids": total_aids})
                else:
                    self.log_test("Martinique Kit Calculations", False, 
                                f"Unexpected kit power {kit_power}kW (expected 3, 6, or 9)", 
                                calculation)
                    
            else:
                self.log_test("Martinique Kit Calculations", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Martinique Kit Calculations", False, f"Error: {str(e)}")

    def test_france_region_still_works(self):
        """Test that France region calculations still work correctly"""
        if not self.france_client_id:
            self.log_test("France Region Still Works", False, "No France client ID available")
            return
            
        try:
            response = self.session.post(f"{self.base_url}/calculate/{self.france_client_id}")
            if response.status_code == 200:
                calculation = response.json()
                
                # Check that it's using France region
                region = calculation.get("region", "")
                if region != "france":
                    self.log_test("France Region Still Works", False, f"Expected region 'france', got '{region}'")
                    return
                
                kit_power = calculation.get("kit_power", 0)
                panel_count = calculation.get("panel_count", 0)
                kit_price = calculation.get("kit_price", 0)
                
                # France should use SOLAR_KITS data structure
                expected_france_kits = {3: 6, 4: 8, 5: 10, 6: 12, 7: 14, 8: 16, 9: 18}
                
                if kit_power in expected_france_kits:
                    expected_panels = expected_france_kits[kit_power]
                    if panel_count == expected_panels:
                        self.log_test("France Region Still Works", True, 
                                    f"✅ France calculation working: {kit_power}kW kit, {panel_count} panels, {kit_price}€", 
                                    {"region": region, "kit_power": kit_power, "panel_count": panel_count, "kit_price": kit_price})
                    else:
                        self.log_test("France Region Still Works", False, 
                                    f"France panel count incorrect: {kit_power}kW kit should have {expected_panels} panels, got {panel_count}", 
                                    calculation)
                else:
                    self.log_test("France Region Still Works", False, 
                                f"Unexpected France kit power {kit_power}kW", 
                                calculation)
                    
            else:
                self.log_test("France Region Still Works", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("France Region Still Works", False, f"Error: {str(e)}")

    def test_pdf_generation_martinique_region(self):
        """Test PDF generation uses correct Martinique region data"""
        if not self.martinique_client_id:
            self.log_test("PDF Generation Martinique", False, "No Martinique client ID available")
            return
            
        try:
            # First, perform calculation with Martinique region to store region in client
            calc_response = self.session.post(f"{self.base_url}/calculate/{self.martinique_client_id}?region=martinique")
            if calc_response.status_code != 200:
                self.log_test("PDF Generation Martinique", False, f"Failed to calculate for Martinique: {calc_response.status_code}")
                return
            
            calculation = calc_response.json()
            
            # Generate PDF
            pdf_response = self.session.get(f"{self.base_url}/generate-pdf/{self.martinique_client_id}")
            if pdf_response.status_code != 200:
                self.log_test("PDF Generation Martinique", False, f"PDF generation failed: HTTP {pdf_response.status_code}: {pdf_response.text}")
                return
            
            # Check if response is actually a PDF
            if not pdf_response.headers.get('content-type', '').startswith('application/pdf'):
                self.log_test("PDF Generation Martinique", False, f"Response is not a PDF. Content-Type: {pdf_response.headers.get('content-type')}")
                return
            
            # Check PDF size
            pdf_size = len(pdf_response.content)
            if pdf_size < 10000:
                self.log_test("PDF Generation Martinique", False, f"PDF size {pdf_size} bytes seems too small")
                return
            
            # Verify that the calculation data used Martinique values
            kit_power = calculation.get("kit_power", 0)
            kit_price = calculation.get("kit_price", 0)
            total_aids = calculation.get("total_aids", 0)
            region = calculation.get("region", "")
            
            # Expected Martinique values
            expected_martinique = {
                3: {"price": 9900, "aid": 5340},
                6: {"price": 13900, "aid": 6480},
                9: {"price": 16900, "aid": 9720}
            }
            
            if region != "martinique":
                self.log_test("PDF Generation Martinique", False, f"PDF should use Martinique region, got '{region}'")
                return
            
            if kit_power in expected_martinique:
                expected = expected_martinique[kit_power]
                if kit_price == expected["price"] and total_aids == expected["aid"]:
                    self.log_test("PDF Generation Martinique", True, 
                                f"✅ PDF generated with correct Martinique data: {kit_power}kW kit, {kit_price}€ TTC, {total_aids}€ aid (PDF size: {pdf_size:,} bytes)", 
                                {"region": region, "kit_power": kit_power, "kit_price": kit_price, "total_aids": total_aids, "pdf_size": pdf_size})
                else:
                    self.log_test("PDF Generation Martinique", False, 
                                f"PDF uses incorrect Martinique data: {kit_power}kW kit should be {expected['price']}€/{expected['aid']}€ aid, got {kit_price}€/{total_aids}€ aid")
            else:
                self.log_test("PDF Generation Martinique", False, f"Unexpected Martinique kit power {kit_power}kW")
                
        except Exception as e:
            self.log_test("PDF Generation Martinique", False, f"Error: {str(e)}")

    def test_pdf_generation_france_region(self):
        """Test PDF generation uses correct France region data"""
        if not self.france_client_id:
            self.log_test("PDF Generation France", False, "No France client ID available")
            return
            
        try:
            # First, perform calculation with France region (default)
            calc_response = self.session.post(f"{self.base_url}/calculate/{self.france_client_id}")
            if calc_response.status_code != 200:
                self.log_test("PDF Generation France", False, f"Failed to calculate for France: {calc_response.status_code}")
                return
            
            calculation = calc_response.json()
            
            # Generate PDF
            pdf_response = self.session.get(f"{self.base_url}/generate-pdf/{self.france_client_id}")
            if pdf_response.status_code != 200:
                self.log_test("PDF Generation France", False, f"PDF generation failed: HTTP {pdf_response.status_code}: {pdf_response.text}")
                return
            
            # Check if response is actually a PDF
            if not pdf_response.headers.get('content-type', '').startswith('application/pdf'):
                self.log_test("PDF Generation France", False, f"Response is not a PDF. Content-Type: {pdf_response.headers.get('content-type')}")
                return
            
            # Check PDF size
            pdf_size = len(pdf_response.content)
            if pdf_size < 10000:
                self.log_test("PDF Generation France", False, f"PDF size {pdf_size} bytes seems too small")
                return
            
            # Verify that the calculation data used France values
            kit_power = calculation.get("kit_power", 0)
            kit_price = calculation.get("kit_price", 0)
            region = calculation.get("region", "")
            
            # France should use SOLAR_KITS pricing
            france_kits = {3: 14900, 4: 20900, 5: 21900, 6: 22900, 7: 24900, 8: 26900, 9: 29900}
            
            if region != "france":
                self.log_test("PDF Generation France", False, f"PDF should use France region, got '{region}'")
                return
            
            if kit_power in france_kits:
                expected_price = france_kits[kit_power]
                if kit_price == expected_price:
                    self.log_test("PDF Generation France", True, 
                                f"✅ PDF generated with correct France data: {kit_power}kW kit, {kit_price}€ (PDF size: {pdf_size:,} bytes)", 
                                {"region": region, "kit_power": kit_power, "kit_price": kit_price, "pdf_size": pdf_size})
                else:
                    self.log_test("PDF Generation France", False, 
                                f"PDF uses incorrect France data: {kit_power}kW kit should be {expected_price}€, got {kit_price}€")
            else:
                self.log_test("PDF Generation France", False, f"Unexpected France kit power {kit_power}kW")
                
        except Exception as e:
            self.log_test("PDF Generation France", False, f"Error: {str(e)}")

    def test_calculation_response_structure(self):
        """Test that calculation response includes panel_count for both regions"""
        if not self.france_client_id or not self.martinique_client_id:
            self.log_test("Calculation Response Structure", False, "Missing client IDs")
            return
            
        try:
            # Test France response structure
            france_response = self.session.post(f"{self.base_url}/calculate/{self.france_client_id}")
            if france_response.status_code != 200:
                self.log_test("Calculation Response Structure", False, f"France calculation failed: {france_response.status_code}")
                return
            
            france_calc = france_response.json()
            
            # Test Martinique response structure
            martinique_response = self.session.post(f"{self.base_url}/calculate/{self.martinique_client_id}?region=martinique")
            if martinique_response.status_code != 200:
                self.log_test("Calculation Response Structure", False, f"Martinique calculation failed: {martinique_response.status_code}")
                return
            
            martinique_calc = martinique_response.json()
            
            # Check required fields in both responses
            required_fields = ["kit_power", "panel_count", "kit_price", "total_aids", "region"]
            
            issues = []
            
            # Check France response
            for field in required_fields:
                if field not in france_calc:
                    issues.append(f"France missing field: {field}")
            
            # Check Martinique response
            for field in required_fields:
                if field not in martinique_calc:
                    issues.append(f"Martinique missing field: {field}")
            
            # Verify panel_count is present and correct
            france_kit_power = france_calc.get("kit_power", 0)
            france_panel_count = france_calc.get("panel_count", 0)
            martinique_kit_power = martinique_calc.get("kit_power", 0)
            martinique_panel_count = martinique_calc.get("panel_count", 0)
            
            # France: use SOLAR_KITS data
            france_expected_panels = {3: 6, 4: 8, 5: 10, 6: 12, 7: 14, 8: 16, 9: 18}
            if france_kit_power in france_expected_panels:
                if france_panel_count != france_expected_panels[france_kit_power]:
                    issues.append(f"France panel_count: expected {france_expected_panels[france_kit_power]}, got {france_panel_count}")
            
            # Martinique: 1kW = 2 panels
            martinique_expected_panels = martinique_kit_power * 2
            if martinique_panel_count != martinique_expected_panels:
                issues.append(f"Martinique panel_count: expected {martinique_expected_panels}, got {martinique_panel_count}")
            
            # Check region-specific pricing
            france_kit_price = france_calc.get("kit_price", 0)
            martinique_kit_price = martinique_calc.get("kit_price", 0)
            
            # Verify different pricing between regions
            if france_kit_power == martinique_kit_power and france_kit_price == martinique_kit_price:
                issues.append(f"Same kit power ({france_kit_power}kW) should have different prices between regions, both got {france_kit_price}€")
            
            if issues:
                self.log_test("Calculation Response Structure", False, f"Structure issues: {'; '.join(issues)}")
            else:
                self.log_test("Calculation Response Structure", True, 
                            f"✅ Response structure correct. France: {france_kit_power}kW/{france_panel_count} panels/{france_kit_price}€, Martinique: {martinique_kit_power}kW/{martinique_panel_count} panels/{martinique_kit_price}€", 
                            {
                                "france": {"kit_power": france_kit_power, "panel_count": france_panel_count, "kit_price": france_kit_price},
                                "martinique": {"kit_power": martinique_kit_power, "panel_count": martinique_panel_count, "kit_price": martinique_kit_price}
                            })
                
        except Exception as e:
            self.log_test("Calculation Response Structure", False, f"Error: {str(e)}")

    def run_all_tests(self):
        """Run all Martinique fixes tests"""
        print("🧪 TESTING MARTINIQUE REGION FIXES")
        print("=" * 50)
        
        # Create test clients
        if not self.create_test_clients():
            print("❌ Failed to create test clients, aborting tests")
            return
        
        # Run all tests
        self.test_martinique_panel_count_calculation()
        self.test_martinique_kit_calculations()
        self.test_france_region_still_works()
        self.test_pdf_generation_martinique_region()
        self.test_pdf_generation_france_region()
        self.test_calculation_response_structure()
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
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
            print("\n✅ ALL TESTS PASSED!")
        
        return passed == total

if __name__ == "__main__":
    tester = MartiniqueFixes()
    success = tester.run_all_tests()
    exit(0 if success else 1)