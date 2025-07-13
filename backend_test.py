#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Solar Calculator with PVGIS Integration
Tests all endpoints with realistic French solar installation data
"""

import requests
import json
import time
from typing import Dict, Any, Optional

# Backend URL from frontend environment
BACKEND_URL = "https://6bdc03cb-2281-45cf-b416-4f00be56fcd6.preview.emergentagent.com/api"

class SolarCalculatorTester:
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
        
    def test_api_root(self):
        """Test basic API connectivity"""
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "Solar Calculator" in data["message"]:
                    self.log_test("API Root", True, f"API accessible, message: {data['message']}", data)
                else:
                    self.log_test("API Root", False, f"Unexpected response format: {data}", data)
            else:
                self.log_test("API Root", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("API Root", False, f"Connection error: {str(e)}")
    
    def test_solar_kits(self):
        """Test solar kits endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/solar-kits")
            if response.status_code == 200:
                kits = response.json()
                if isinstance(kits, dict) and len(kits) > 0:
                    # Check if we have expected kit sizes
                    expected_sizes = [3, 4, 5, 6, 7, 8, 9]
                    available_sizes = list(kits.keys())
                    available_sizes = [int(k) for k in available_sizes]
                    
                    if all(size in available_sizes for size in expected_sizes):
                        # Check pricing structure
                        kit_6 = kits.get("6", {})
                        if "price" in kit_6 and "panels" in kit_6:
                            self.log_test("Solar Kits", True, 
                                        f"All kits available. 6kW kit: {kit_6['price']}€, {kit_6['panels']} panels", 
                                        kits)
                        else:
                            self.log_test("Solar Kits", False, "Missing price/panels info in kit data", kits)
                    else:
                        self.log_test("Solar Kits", False, f"Missing expected kit sizes. Available: {available_sizes}", kits)
                else:
                    self.log_test("Solar Kits", False, f"Invalid kits format: {kits}", kits)
            else:
                self.log_test("Solar Kits", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Solar Kits", False, f"Error: {str(e)}")
    
    def test_pvgis_direct(self):
        """Test direct PVGIS endpoint with Paris coordinates"""
        try:
            # Paris coordinates: 48.8566, 2.3522
            url = f"{self.base_url}/test-pvgis/48.8566/2.3522"
            params = {"orientation": "Sud", "power": 6}
            
            response = self.session.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                if "pvgis_data" in data and "coordinates" in data:
                    pvgis_data = data["pvgis_data"]
                    annual_production = pvgis_data.get("annual_production", 0)
                    
                    # Expected production for 6kW in Paris should be around 6800 kWh
                    if 6000 <= annual_production <= 8000:
                        self.log_test("PVGIS Direct", True, 
                                    f"PVGIS working. Annual production: {annual_production} kWh for 6kW in Paris", 
                                    data)
                    else:
                        self.log_test("PVGIS Direct", False, 
                                    f"Unexpected production value: {annual_production} kWh (expected 6000-8000)", 
                                    data)
                else:
                    self.log_test("PVGIS Direct", False, "Missing pvgis_data or coordinates in response", data)
            else:
                self.log_test("PVGIS Direct", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("PVGIS Direct", False, f"Error: {str(e)}")
    
    def test_create_client(self):
        """Test client creation with realistic French data"""
        try:
            client_data = {
                "first_name": "Jean",
                "last_name": "Dupont",
                "address": "10 Avenue des Champs-Élysées, 75008 Paris",
                "roof_surface": 60.0,
                "roof_orientation": "Sud",
                "velux_count": 2,
                "heating_system": "Radiateurs électriques",
                "water_heating_system": "Ballon électrique",
                "water_heating_capacity": 200,
                "annual_consumption_kwh": 6500.0,
                "monthly_edf_payment": 180.0,
                "annual_edf_payment": 2160.0
            }
            
            response = self.session.post(f"{self.base_url}/clients", json=client_data)
            if response.status_code == 200:
                client = response.json()
                
                # Check if geocoding worked
                if "latitude" in client and "longitude" in client and "id" in client:
                    lat, lon = client["latitude"], client["longitude"]
                    self.client_id = client["id"]  # Store for next test
                    
                    # Paris coordinates should be around 48.8566, 2.3522
                    if 48.5 <= lat <= 49.0 and 2.0 <= lon <= 2.7:
                        self.log_test("Create Client", True, 
                                    f"Client created successfully. ID: {self.client_id}, Coords: {lat:.4f}, {lon:.4f}", 
                                    client)
                    else:
                        self.log_test("Create Client", False, 
                                    f"Geocoding seems incorrect. Coords: {lat}, {lon} (expected Paris area)", 
                                    client)
                else:
                    self.log_test("Create Client", False, "Missing latitude, longitude, or id in response", client)
            else:
                self.log_test("Create Client", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Create Client", False, f"Error: {str(e)}")
    
    def test_get_clients(self):
        """Test getting all clients"""
        try:
            response = self.session.get(f"{self.base_url}/clients")
            if response.status_code == 200:
                clients = response.json()
                if isinstance(clients, list):
                    if len(clients) > 0:
                        # Check if our test client is in the list
                        if self.client_id:
                            client_found = any(c.get("id") == self.client_id for c in clients)
                            if client_found:
                                self.log_test("Get Clients", True, f"Retrieved {len(clients)} clients, test client found", clients)
                            else:
                                self.log_test("Get Clients", False, f"Test client {self.client_id} not found in list", clients)
                        else:
                            self.log_test("Get Clients", True, f"Retrieved {len(clients)} clients", clients)
                    else:
                        self.log_test("Get Clients", True, "No clients in database (empty list)", clients)
                else:
                    self.log_test("Get Clients", False, f"Expected list, got: {type(clients)}", clients)
            else:
                self.log_test("Get Clients", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Get Clients", False, f"Error: {str(e)}")
    
    def test_get_client_by_id(self):
        """Test getting specific client by ID"""
        if not self.client_id:
            self.log_test("Get Client by ID", False, "No client ID available from previous test")
            return
            
        try:
            response = self.session.get(f"{self.base_url}/clients/{self.client_id}")
            if response.status_code == 200:
                client = response.json()
                if client.get("id") == self.client_id:
                    self.log_test("Get Client by ID", True, 
                                f"Retrieved client: {client.get('first_name')} {client.get('last_name')}", 
                                client)
                else:
                    self.log_test("Get Client by ID", False, f"ID mismatch: expected {self.client_id}, got {client.get('id')}", client)
            elif response.status_code == 404:
                self.log_test("Get Client by ID", False, "Client not found (404)")
            else:
                self.log_test("Get Client by ID", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Get Client by ID", False, f"Error: {str(e)}")
    
    def test_solar_calculation(self):
        """Test complete solar calculation with PVGIS integration"""
        if not self.client_id:
            self.log_test("Solar Calculation", False, "No client ID available from previous test")
            return
            
        try:
            response = self.session.post(f"{self.base_url}/calculate/{self.client_id}")
            if response.status_code == 200:
                calculation = response.json()
                
                # Check key calculation results
                required_fields = [
                    "kit_power", "panel_count", "estimated_production", 
                    "estimated_savings", "autonomy_percentage", "monthly_savings",
                    "financing_options", "kit_price"
                ]
                
                missing_fields = [field for field in required_fields if field not in calculation]
                if missing_fields:
                    self.log_test("Solar Calculation", False, f"Missing fields: {missing_fields}", calculation)
                    return
                
                # Validate calculation results
                kit_power = calculation.get("kit_power", 0)
                estimated_production = calculation.get("estimated_production", 0)
                estimated_savings = calculation.get("estimated_savings", 0)
                autonomy_percentage = calculation.get("autonomy_percentage", 0)
                financing_options = calculation.get("financing_options", [])
                
                issues = []
                
                # Check production (should be around 6800 kWh for 6kW in Paris)
                if not (6000 <= estimated_production <= 8000):
                    issues.append(f"Production {estimated_production} kWh outside expected range 6000-8000")
                
                # Check autonomy (should be 95%+ for 6500 kWh consumption)
                if autonomy_percentage < 90:
                    issues.append(f"Low autonomy: {autonomy_percentage}% (expected >90%)")
                
                # Check savings (should be 1300-1400€/year)
                if not (1200 <= estimated_savings <= 1600):
                    issues.append(f"Savings {estimated_savings}€ outside expected range 1200-1600€")
                
                # Check financing options
                if len(financing_options) < 5:
                    issues.append(f"Too few financing options: {len(financing_options)} (expected 6-15 years)")
                
                if issues:
                    self.log_test("Solar Calculation", False, f"Calculation issues: {'; '.join(issues)}", calculation)
                else:
                    self.log_test("Solar Calculation", True, 
                                f"Calculation successful: {kit_power}kW, {estimated_production:.0f} kWh/year, {autonomy_percentage:.1f}% autonomy, {estimated_savings:.0f}€/year savings", 
                                calculation)
            else:
                self.log_test("Solar Calculation", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Solar Calculation", False, f"Error: {str(e)}")
    
    def test_error_cases(self):
        """Test error handling"""
        # Test invalid address
        try:
            invalid_client_data = {
                "first_name": "Test",
                "last_name": "User",
                "address": "Invalid Address That Does Not Exist 99999",
                "roof_surface": 60.0,
                "roof_orientation": "Sud",
                "velux_count": 2,
                "heating_system": "Radiateurs électriques",
                "water_heating_system": "Ballon électrique",
                "annual_consumption_kwh": 6500.0,
                "monthly_edf_payment": 180.0,
                "annual_edf_payment": 2160.0
            }
            
            response = self.session.post(f"{self.base_url}/clients", json=invalid_client_data)
            if response.status_code == 400:
                self.log_test("Error Handling - Invalid Address", True, "Correctly rejected invalid address with 400 error")
            else:
                self.log_test("Error Handling - Invalid Address", False, f"Expected 400 error, got {response.status_code}")
        except Exception as e:
            self.log_test("Error Handling - Invalid Address", False, f"Error: {str(e)}")
        
        # Test non-existent client calculation
        try:
            fake_id = "non-existent-client-id"
            response = self.session.post(f"{self.base_url}/calculate/{fake_id}")
            if response.status_code == 404:
                self.log_test("Error Handling - Non-existent Client", True, "Correctly returned 404 for non-existent client")
            else:
                self.log_test("Error Handling - Non-existent Client", False, f"Expected 404 error, got {response.status_code}")
        except Exception as e:
            self.log_test("Error Handling - Non-existent Client", False, f"Error: {str(e)}")
    
    def run_all_tests(self):
        """Run all tests in order"""
        print("🚀 Starting Solar Calculator Backend Tests")
        print(f"Backend URL: {self.base_url}")
        print("=" * 60)
        
        # Priority 1 tests
        print("\n📋 PRIORITY 1 - Main Endpoints")
        self.test_api_root()
        self.test_solar_kits()
        self.test_pvgis_direct()
        
        # Priority 2 tests - Complete workflow
        print("\n📋 PRIORITY 2 - Complete Client Workflow")
        self.test_create_client()
        self.test_get_clients()
        self.test_get_client_by_id()
        self.test_solar_calculation()
        
        # Error handling tests
        print("\n📋 ERROR HANDLING TESTS")
        self.test_error_cases()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if total - passed > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
        
        return self.test_results

if __name__ == "__main__":
    tester = SolarCalculatorTester()
    results = tester.run_all_tests()
    
    # Save detailed results to file
    with open("/app/test_results_detailed.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Detailed results saved to /app/test_results_detailed.json")