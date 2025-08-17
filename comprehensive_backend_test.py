#!/usr/bin/env python3
"""
Comprehensive Backend Testing for 20-Year Visual Support
Tests all critical backend functionality needed for the new 20-year financial visual
"""

import requests
import json
import time
from typing import Dict, Any, Optional

# Backend URL from frontend environment
BACKEND_URL = "https://pdf-solar-quote.preview.emergentagent.com/api"

class TwentyYearVisualTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.client_id = None
        
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
        
    def test_api_connectivity(self):
        """Test basic API connectivity"""
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "Solar Calculator" in data["message"]:
                    self.log_test("API Connectivity", True, f"Backend API accessible: {data['message']}")
                    return True
                else:
                    self.log_test("API Connectivity", False, f"Unexpected response: {data}")
                    return False
            else:
                self.log_test("API Connectivity", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("API Connectivity", False, f"Connection error: {str(e)}")
            return False
    
    def test_solar_kits_data(self):
        """Test solar kits data availability"""
        try:
            response = self.session.get(f"{self.base_url}/solar-kits")
            if response.status_code == 200:
                kits = response.json()
                if isinstance(kits, dict) and len(kits) > 0:
                    # Check if we have key kit sizes needed for 20-year calculations
                    key_sizes = [6, 9]  # Most common sizes
                    available_sizes = [int(k) for k in kits.keys()]
                    
                    missing_sizes = [size for size in key_sizes if size not in available_sizes]
                    if missing_sizes:
                        self.log_test("Solar Kits Data", False, f"Missing key kit sizes: {missing_sizes}")
                        return False
                    
                    # Check 6kW kit structure (most common)
                    kit_6 = kits.get("6", {})
                    if "price" in kit_6 and "panels" in kit_6:
                        self.log_test("Solar Kits Data", True, 
                                    f"Solar kits available. 6kW kit: {kit_6['price']}€, {kit_6['panels']} panels")
                        return True
                    else:
                        self.log_test("Solar Kits Data", False, "Missing price/panels in kit data")
                        return False
                else:
                    self.log_test("Solar Kits Data", False, f"Invalid kits format: {kits}")
                    return False
            else:
                self.log_test("Solar Kits Data", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Solar Kits Data", False, f"Error: {str(e)}")
            return False
    
    def create_test_client(self):
        """Create a test client for calculations"""
        try:
            client_data = {
                "first_name": "Test",
                "last_name": "Client",
                "address": "75008 Paris",
                "phone": "0659597690",
                "email": "test@example.com",
                "roof_surface": 80.0,
                "roof_orientation": "Sud",
                "velux_count": 0,
                "heating_system": "Radiateurs électriques",
                "water_heating_system": "Ballon électrique standard",
                "water_heating_capacity": 200,
                "annual_consumption_kwh": 7200.0,
                "monthly_edf_payment": 220.0,
                "annual_edf_payment": 2640.0
            }
            
            response = self.session.post(f"{self.base_url}/clients", json=client_data)
            if response.status_code == 200:
                client = response.json()
                if "id" in client:
                    self.client_id = client["id"]
                    self.log_test("Create Test Client", True, f"Test client created: ID {self.client_id}")
                    return True
                else:
                    self.log_test("Create Test Client", False, "Missing ID in response")
                    return False
            else:
                # Try to use existing client
                self.log_test("Create Test Client", False, f"Failed to create client: {response.status_code}. Trying existing client...")
                return self.use_existing_client()
        except Exception as e:
            self.log_test("Create Test Client", False, f"Error: {str(e)}")
            return self.use_existing_client()
    
    def use_existing_client(self):
        """Use an existing client as fallback"""
        try:
            response = self.session.get(f"{self.base_url}/clients")
            if response.status_code == 200:
                clients = response.json()
                if isinstance(clients, list) and len(clients) > 0:
                    client = clients[0]
                    self.client_id = client.get("id")
                    if self.client_id:
                        self.log_test("Use Existing Client", True, f"Using existing client: ID {self.client_id}")
                        return True
                    else:
                        self.log_test("Use Existing Client", False, "No ID in existing client")
                        return False
                else:
                    self.log_test("Use Existing Client", False, "No existing clients found")
                    return False
            else:
                self.log_test("Use Existing Client", False, f"Failed to get clients: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Use Existing Client", False, f"Error: {str(e)}")
            return False
    
    def test_solar_calculation_data(self):
        """Test solar calculation and verify all data needed for 20-year visual"""
        if not self.client_id:
            self.log_test("Solar Calculation Data", False, "No client ID available")
            return False
            
        try:
            response = self.session.post(f"{self.base_url}/calculate/{self.client_id}")
            if response.status_code == 200:
                calculation = response.json()
                
                # Check all fields needed for 20-year visual
                required_fields = [
                    "kit_power",           # For surplus calculation
                    "monthly_savings",     # For 20-year savings calculation
                    "estimated_production", # For production calculations
                    "kit_price",          # For investment calculations
                    "monthly_edf_payment", # For EDF payment calculations (from client)
                    "autonomy_percentage", # For remaining EDF percentage
                    "surplus_kwh",        # For surplus resale calculation
                    "autoconsumption_kwh" # For autoconsumption calculation
                ]
                
                missing_fields = []
                for field in required_fields:
                    if field not in calculation:
                        missing_fields.append(field)
                
                if missing_fields:
                    self.log_test("Solar Calculation Data", False, f"Missing required fields: {missing_fields}")
                    return False
                
                # Validate data ranges for 20-year calculations
                kit_power = calculation.get("kit_power", 0)
                monthly_savings = calculation.get("monthly_savings", 0)
                estimated_production = calculation.get("estimated_production", 0)
                kit_price = calculation.get("kit_price", 0)
                autonomy_percentage = calculation.get("autonomy_percentage", 0)
                surplus_kwh = calculation.get("surplus_kwh", 0)
                
                issues = []
                
                # Validate reasonable values for 20-year calculations
                if kit_power < 3 or kit_power > 15:
                    issues.append(f"Kit power {kit_power}kW outside reasonable range")
                
                if monthly_savings < 50 or monthly_savings > 500:
                    issues.append(f"Monthly savings {monthly_savings}€ outside reasonable range")
                
                if estimated_production < 3000 or estimated_production > 15000:
                    issues.append(f"Production {estimated_production} kWh outside reasonable range")
                
                if kit_price < 10000 or kit_price > 50000:
                    issues.append(f"Kit price {kit_price}€ outside reasonable range")
                
                if autonomy_percentage < 50 or autonomy_percentage > 100:
                    issues.append(f"Autonomy {autonomy_percentage}% outside reasonable range")
                
                if surplus_kwh < 0 or surplus_kwh > estimated_production:
                    issues.append(f"Surplus {surplus_kwh} kWh invalid")
                
                if issues:
                    self.log_test("Solar Calculation Data", False, f"Data validation issues: {'; '.join(issues)}")
                    return False
                
                # Calculate 20-year values to verify they make sense
                annual_savings = monthly_savings * 12
                savings_20_years = annual_savings * 20
                
                # EDF payment without PV (with 5% annual increase)
                monthly_edf = 220  # From test client
                edf_20_years_without_pv = 0
                for year in range(20):
                    yearly_payment = monthly_edf * 12 * (1.05 ** year)
                    edf_20_years_without_pv += yearly_payment
                
                # EDF payment with PV (18% remaining)
                remaining_percentage = (100 - autonomy_percentage) / 100
                edf_20_years_with_pv = 0
                for year in range(20):
                    yearly_payment = monthly_edf * 12 * remaining_percentage * (1.05 ** year)
                    edf_20_years_with_pv += yearly_payment
                
                # Surplus resale (based on kit power)
                surplus_monthly_resale = (surplus_kwh / 12) * 0.076  # €/kWh resale rate
                surplus_20_years = surplus_monthly_resale * 12 * 20
                
                self.log_test("Solar Calculation Data", True, 
                            f"✅ ALL 20-YEAR VISUAL DATA AVAILABLE: Kit {kit_power}kW, Monthly savings {monthly_savings}€, "
                            f"20-year savings {savings_20_years:,.0f}€, EDF without PV {edf_20_years_without_pv:,.0f}€, "
                            f"EDF with PV {edf_20_years_with_pv:,.0f}€, Surplus resale {surplus_20_years:,.0f}€")
                return True
                
            else:
                self.log_test("Solar Calculation Data", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Solar Calculation Data", False, f"Error: {str(e)}")
            return False
    
    def test_battery_functionality(self):
        """Test battery functionality for 20-year calculations"""
        if not self.client_id:
            self.log_test("Battery Functionality", False, "No client ID available")
            return False
            
        try:
            # Test without battery
            response_no_battery = self.session.post(f"{self.base_url}/calculate/{self.client_id}?battery_selected=false")
            if response_no_battery.status_code != 200:
                self.log_test("Battery Functionality", False, f"Failed to get calculation without battery: {response_no_battery.status_code}")
                return False
            
            calc_no_battery = response_no_battery.json()
            
            # Test with battery
            response_with_battery = self.session.post(f"{self.base_url}/calculate/{self.client_id}?battery_selected=true")
            if response_with_battery.status_code != 200:
                self.log_test("Battery Functionality", False, f"Failed to get calculation with battery: {response_with_battery.status_code}")
                return False
            
            calc_with_battery = response_with_battery.json()
            
            # Verify battery fields
            required_battery_fields = ["battery_selected", "battery_cost", "kit_price_final"]
            missing_fields = [field for field in required_battery_fields if field not in calc_with_battery]
            if missing_fields:
                self.log_test("Battery Functionality", False, f"Missing battery fields: {missing_fields}")
                return False
            
            # Verify battery cost is added correctly
            battery_cost = calc_with_battery.get("battery_cost", 0)
            if battery_cost != 5000:
                self.log_test("Battery Functionality", False, f"Expected battery cost 5000€, got {battery_cost}€")
                return False
            
            # Verify price difference
            price_no_battery = calc_no_battery.get("kit_price_final", calc_no_battery.get("kit_price", 0))
            price_with_battery = calc_with_battery.get("kit_price_final", 0)
            price_difference = price_with_battery - price_no_battery
            
            if abs(price_difference - 5000) > 1:  # Allow 1€ tolerance
                self.log_test("Battery Functionality", False, f"Price difference {price_difference}€ != 5000€")
                return False
            
            self.log_test("Battery Functionality", True, 
                        f"✅ BATTERY FUNCTIONALITY WORKING: Without battery: {price_no_battery}€, "
                        f"With battery: {price_with_battery}€ (+{price_difference}€)")
            return True
            
        except Exception as e:
            self.log_test("Battery Functionality", False, f"Error: {str(e)}")
            return False
    
    def test_martinique_region_support(self):
        """Test Martinique region support for 20-year calculations"""
        if not self.client_id:
            self.log_test("Martinique Region Support", False, "No client ID available")
            return False
            
        try:
            # Test Martinique calculation
            response = self.session.post(f"{self.base_url}/calculate/{self.client_id}?region=martinique")
            if response.status_code == 200:
                calculation = response.json()
                
                # Verify region-specific data
                if calculation.get("region") != "martinique":
                    self.log_test("Martinique Region Support", False, f"Expected region 'martinique', got '{calculation.get('region')}'")
                    return False
                
                # Check Martinique-specific kit sizes and pricing
                kit_power = calculation.get("kit_power", 0)
                if kit_power not in [3, 6, 9, 12, 15, 18, 21, 24, 27]:  # Updated Martinique kit sizes
                    self.log_test("Martinique Region Support", False, f"Kit power {kit_power} not in Martinique range")
                    return False
                
                # Check that all 20-year calculation fields are present
                required_fields = ["monthly_savings", "kit_price", "autonomy_percentage", "surplus_kwh"]
                missing_fields = [field for field in required_fields if field not in calculation]
                if missing_fields:
                    self.log_test("Martinique Region Support", False, f"Missing Martinique fields: {missing_fields}")
                    return False
                
                self.log_test("Martinique Region Support", True, 
                            f"✅ MARTINIQUE REGION WORKING: Kit {kit_power}kW, Monthly savings {calculation.get('monthly_savings', 0)}€")
                return True
                
            else:
                self.log_test("Martinique Region Support", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Martinique Region Support", False, f"Error: {str(e)}")
            return False
    
    def test_financing_calculations(self):
        """Test financing calculations needed for 20-year visual"""
        if not self.client_id:
            self.log_test("Financing Calculations", False, "No client ID available")
            return False
            
        try:
            response = self.session.post(f"{self.base_url}/calculate/{self.client_id}")
            if response.status_code == 200:
                calculation = response.json()
                
                # Check financing options
                financing_options = calculation.get("financing_options", [])
                if not financing_options:
                    self.log_test("Financing Calculations", False, "Missing financing_options")
                    return False
                
                # Check financing with aids
                financing_with_aids = calculation.get("financing_with_aids", {})
                if not financing_with_aids:
                    self.log_test("Financing Calculations", False, "Missing financing_with_aids")
                    return False
                
                # Verify financing data structure
                required_financing_fields = ["monthly_payment", "financed_amount"]
                missing_fields = [field for field in required_financing_fields if field not in financing_with_aids]
                if missing_fields:
                    self.log_test("Financing Calculations", False, f"Missing financing fields: {missing_fields}")
                    return False
                
                monthly_payment = financing_with_aids.get("monthly_payment", 0)
                financed_amount = financing_with_aids.get("financed_amount", 0)
                
                # Validate reasonable financing values
                if monthly_payment < 50 or monthly_payment > 1000:
                    self.log_test("Financing Calculations", False, f"Monthly payment {monthly_payment}€ outside reasonable range")
                    return False
                
                if financed_amount < 5000 or financed_amount > 50000:
                    self.log_test("Financing Calculations", False, f"Financed amount {financed_amount}€ outside reasonable range")
                    return False
                
                self.log_test("Financing Calculations", True, 
                            f"✅ FINANCING CALCULATIONS WORKING: Monthly payment {monthly_payment}€, "
                            f"Financed amount {financed_amount}€")
                return True
                
            else:
                self.log_test("Financing Calculations", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Financing Calculations", False, f"Error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all tests for 20-year visual support"""
        print("🎯 TESTING BACKEND SUPPORT FOR 20-YEAR VISUAL COMPONENT")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print("=" * 80)
        print()
        
        tests = [
            ("API Connectivity", self.test_api_connectivity),
            ("Solar Kits Data", self.test_solar_kits_data),
            ("Create Test Client", self.create_test_client),
            ("Solar Calculation Data", self.test_solar_calculation_data),
            ("Battery Functionality", self.test_battery_functionality),
            ("Martinique Region Support", self.test_martinique_region_support),
            ("Financing Calculations", self.test_financing_calculations)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
            except Exception as e:
                self.log_test(test_name, False, f"Test execution error: {str(e)}")
        
        print()
        print("=" * 80)
        print("📊 20-YEAR VISUAL BACKEND TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        print()
        
        if passed == total:
            print("🎉 ALL TESTS PASSED - Backend is ready for 20-year visual!")
        else:
            print("⚠️  Some tests failed - Check issues above")
            failed_tests = [result for result in self.test_results if not result["success"]]
            if failed_tests:
                print("\n🔍 FAILED TESTS:")
                for test in failed_tests:
                    print(f"❌ {test['test']}: {test['details']}")
        
        return passed == total

if __name__ == "__main__":
    tester = TwentyYearVisualTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)