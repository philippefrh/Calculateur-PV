#!/usr/bin/env python3
"""
Specific test for France Renov Martinique PDF endpoint with DEBUG logging
Tests the endpoint /api/generate-france-renov-martinique-pdf with a Martinique client having:
- 8990 kWh/an consumption
- 6kW recommended power
"""

import requests
import json
import time
import logging
from typing import Dict, Any, Optional

# Configure logging to capture DEBUG messages
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Backend URL from frontend environment
BACKEND_URL = "https://suntracker-reports.preview.emergentagent.com/api"

class FranceRenovMartiniquePDFTester:
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
        
    def create_martinique_client_8990_kwh(self):
        """Create a Martinique client with 8990 kWh/an consumption"""
        try:
            client_data = {
                "first_name": "Jean",
                "last_name": "Martinique",
                "address": "Fort-de-France, Martinique",
                "phone": "0596123456",
                "email": "jean.martinique@test.com",
                "roof_surface": 80.0,
                "roof_orientation": "Sud",
                "velux_count": 0,
                "heating_system": "Climatisation",
                "water_heating_system": "Ballon électrique standard",
                "water_heating_capacity": 200,
                "annual_consumption_kwh": 8990.0,  # Specific consumption requested
                "monthly_edf_payment": 450.0,
                "annual_edf_payment": 5400.0
            }
            
            print(f"🔧 Creating Martinique client with {client_data['annual_consumption_kwh']} kWh/an consumption...")
            
            response = self.session.post(f"{self.base_url}/clients", json=client_data)
            if response.status_code == 200:
                client = response.json()
                
                if "id" in client:
                    self.client_id = client["id"]
                    self.log_test("Create Martinique Client (8990 kWh)", True, 
                                f"Client created successfully. ID: {self.client_id}, Consumption: {client_data['annual_consumption_kwh']} kWh/an", 
                                client)
                    return True
                else:
                    self.log_test("Create Martinique Client (8990 kWh)", False, "Missing ID in response", client)
                    return False
            else:
                self.log_test("Create Martinique Client (8990 kWh)", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Create Martinique Client (8990 kWh)", False, f"Error: {str(e)}")
            return False
    
    def test_calculate_martinique_6kw(self):
        """Test calculation for Martinique with manual 6kW kit selection"""
        if not self.client_id:
            self.log_test("Calculate Martinique 6kW", False, "No client ID available")
            return None
            
        try:
            print(f"🔧 Testing calculation for client {self.client_id} with manual 6kW kit in Martinique...")
            
            # Force 6kW kit selection in Martinique region
            params = {
                "region": "martinique",
                "manual_kit_power": 6
            }
            
            response = self.session.post(f"{self.base_url}/calculate/{self.client_id}", params=params)
            if response.status_code == 200:
                calculation = response.json()
                
                # Verify key data
                kit_power = calculation.get("kit_power", 0)
                estimated_production = calculation.get("estimated_production", 0)
                annual_consumption = 8990  # Our client's consumption
                
                print(f"📊 CALCULATION RESULTS:")
                print(f"   - Kit Power: {kit_power} kW")
                print(f"   - Estimated Production: {estimated_production:.2f} kWh/an")
                print(f"   - Client Consumption: {annual_consumption} kWh/an")
                print(f"   - Region: {calculation.get('region', 'unknown')}")
                
                # Look for DEBUG PDF logs in the response or any debug info
                debug_info = {}
                for key, value in calculation.items():
                    if 'debug' in key.lower() or 'pdf' in key.lower():
                        debug_info[key] = value
                        print(f"   - DEBUG {key}: {value}")
                
                if kit_power == 6 and calculation.get("region") == "martinique":
                    self.log_test("Calculate Martinique 6kW", True, 
                                f"Calculation successful: 6kW kit, {estimated_production:.2f} kWh/an production for {annual_consumption} kWh/an consumption", 
                                calculation)
                    return calculation
                else:
                    self.log_test("Calculate Martinique 6kW", False, 
                                f"Unexpected results: kit_power={kit_power}, region={calculation.get('region')}", 
                                calculation)
                    return None
            else:
                self.log_test("Calculate Martinique 6kW", False, f"HTTP {response.status_code}: {response.text}")
                return None
        except Exception as e:
            self.log_test("Calculate Martinique 6kW", False, f"Error: {str(e)}")
            return None
    
    def test_france_renov_martinique_pdf_with_debug(self):
        """Test the France Renov Martinique PDF endpoint and capture DEBUG logs"""
        if not self.client_id:
            self.log_test("France Renov Martinique PDF with DEBUG", False, "No client ID available")
            return
            
        try:
            print(f"🔧 Testing France Renov Martinique PDF generation for client {self.client_id}...")
            print(f"🔍 Looking for DEBUG PDF logs that show data discrepancy (13,351 kWh vs ~8,901 kWh)...")
            
            # Enable debug logging for this request
            debug_headers = {
                'X-Debug': 'true',
                'X-Debug-Level': 'DEBUG'
            }
            
            response = self.session.get(f"{self.base_url}/generate-france-renov-martinique-pdf/{self.client_id}", 
                                      headers=debug_headers)
            
            print(f"📡 Response Status: {response.status_code}")
            print(f"📡 Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                # Check if response is actually a PDF
                content_type = response.headers.get('content-type', '')
                pdf_size = len(response.content)
                
                print(f"📄 PDF Generated:")
                print(f"   - Content-Type: {content_type}")
                print(f"   - Size: {pdf_size:,} bytes")
                
                # Check for debug information in headers
                debug_logs = []
                for header_name, header_value in response.headers.items():
                    if 'debug' in header_name.lower():
                        debug_logs.append(f"{header_name}: {header_value}")
                        print(f"🐛 DEBUG HEADER {header_name}: {header_value}")
                
                # Try to extract any debug information from the response
                if 'application/pdf' in content_type:
                    self.log_test("France Renov Martinique PDF with DEBUG", True, 
                                f"PDF generated successfully ({pdf_size:,} bytes). Content-Type: {content_type}. Debug headers found: {len(debug_logs)}", 
                                {
                                    "pdf_size": pdf_size,
                                    "content_type": content_type,
                                    "debug_headers": debug_logs,
                                    "client_id": self.client_id
                                })
                    
                    # Print summary for user
                    print(f"\n🎯 FRANCE RENOV MARTINIQUE PDF TEST COMPLETED:")
                    print(f"   ✅ PDF Generated: {pdf_size:,} bytes")
                    print(f"   ✅ Client: 8990 kWh/an consumption")
                    print(f"   ✅ Kit: 6kW recommended power")
                    print(f"   📋 Debug headers captured: {len(debug_logs)}")
                    
                    if debug_logs:
                        print(f"\n🐛 DEBUG INFORMATION FOUND:")
                        for log in debug_logs:
                            print(f"   - {log}")
                    else:
                        print(f"\n⚠️  NO DEBUG HEADERS FOUND - Server may not be configured for debug output")
                        print(f"   💡 To see DEBUG PDF logs, check server logs directly")
                        print(f"   💡 Look for logs containing 'DEBUG PDF' in backend server output")
                    
                else:
                    self.log_test("France Renov Martinique PDF with DEBUG", False, 
                                f"Response is not a PDF. Content-Type: {content_type}, Size: {pdf_size} bytes")
            else:
                error_text = response.text
                print(f"❌ PDF Generation Failed:")
                print(f"   - Status: {response.status_code}")
                print(f"   - Error: {error_text}")
                
                self.log_test("France Renov Martinique PDF with DEBUG", False, 
                            f"HTTP {response.status_code}: {error_text}")
                
        except Exception as e:
            self.log_test("France Renov Martinique PDF with DEBUG", False, f"Error: {str(e)}")
    
    def run_complete_test(self):
        """Run the complete test sequence"""
        print("🚀 STARTING FRANCE RENOV MARTINIQUE PDF DEBUG TEST")
        print("=" * 60)
        print(f"🎯 Target: Client with 8990 kWh/an consumption, 6kW recommended power")
        print(f"🔍 Goal: Capture DEBUG PDF logs showing data discrepancy")
        print(f"📡 Backend URL: {self.base_url}")
        print("=" * 60)
        
        # Step 1: Create Martinique client with specific consumption
        if not self.create_martinique_client_8990_kwh():
            print("❌ Failed to create client, stopping test")
            return
        
        # Step 2: Test calculation to verify 6kW recommendation
        calculation = self.test_calculate_martinique_6kw()
        if not calculation:
            print("❌ Failed to get calculation, continuing with PDF test anyway")
        
        # Step 3: Test France Renov Martinique PDF generation with debug
        self.test_france_renov_martinique_pdf_with_debug()
        
        # Print final summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}: {result['details']}")
        
        print("\n🔍 TO FIND DEBUG PDF LOGS:")
        print("   1. Check backend server logs for entries containing 'DEBUG PDF'")
        print("   2. Look for data showing 13,351 kWh vs expected ~8,901 kWh")
        print("   3. Verify which data source is being used in PDF generation")
        print("=" * 60)

def main():
    """Main test execution"""
    tester = FranceRenovMartiniquePDFTester()
    tester.run_complete_test()

if __name__ == "__main__":
    main()