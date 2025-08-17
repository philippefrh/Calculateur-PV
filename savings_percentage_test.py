#!/usr/bin/env python3
"""
Specific test to identify the 71% savings percentage field in API response
Testing with client having 11990 kWh/an consumption and 6kW recommended
"""

import requests
import json
import time
from typing import Dict, Any, Optional

# Backend URL from frontend environment
BACKEND_URL = "https://solarquote-fix.preview.emergentagent.com/api"

class SavingsPercentageTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.client_id = None
        
    def log_result(self, message: str, data: Any = None):
        """Log test results"""
        print(f"🔍 {message}")
        if data:
            print(f"   Data: {json.dumps(data, indent=2)}")
        print()
    
    def create_test_client(self):
        """Create a test client with 11990 kWh/an consumption"""
        try:
            client_data = {
                "first_name": "Test",
                "last_name": "Client",
                "address": "Fort-de-France, Martinique",
                "phone": "0596123456",
                "email": "test@martinique.com",
                "roof_surface": 100.0,
                "roof_orientation": "Sud",
                "velux_count": 0,
                "heating_system": "Climatisation",
                "water_heating_system": "Ballon électrique",
                "water_heating_capacity": 200,
                "annual_consumption_kwh": 11990.0,  # Specific consumption requested
                "monthly_edf_payment": 450.0,
                "annual_edf_payment": 5400.0
            }
            
            response = self.session.post(f"{self.base_url}/clients", json=client_data)
            if response.status_code == 200:
                client = response.json()
                self.client_id = client["id"]
                self.log_result(f"✅ Client created successfully with 11990 kWh/an consumption", {
                    "client_id": self.client_id,
                    "annual_consumption": client_data["annual_consumption_kwh"]
                })
                return True
            else:
                self.log_result(f"❌ Failed to create client: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.log_result(f"❌ Error creating client: {str(e)}")
            return False
    
    def test_calculate_api_for_savings_percentage(self):
        """Test calculate API to find the 71% savings percentage field"""
        if not self.client_id:
            self.log_result("❌ No client ID available")
            return
        
        try:
            # Test with Martinique region and manual 6kW selection
            response = self.session.post(
                f"{self.base_url}/calculate/{self.client_id}",
                params={
                    "region": "martinique",
                    "manual_kit_power": 6
                }
            )
            
            if response.status_code == 200:
                calculation = response.json()
                
                self.log_result("✅ Calculate API response received")
                
                # Extract all percentage fields from the response
                percentage_fields = {}
                
                # Look for any field containing percentage values
                for key, value in calculation.items():
                    if isinstance(value, (int, float)):
                        # Check if value could be a percentage (0-100 range)
                        if 0 <= value <= 100:
                            percentage_fields[key] = value
                
                self.log_result("🔍 All percentage fields found (0-100 range):", percentage_fields)
                
                # Specifically look for fields that might contain 71%
                fields_around_71 = {}
                for key, value in percentage_fields.items():
                    if isinstance(value, (int, float)) and 69 <= value <= 73:
                        fields_around_71[key] = value
                
                self.log_result("🎯 Fields with values around 71% (69-73 range):", fields_around_71)
                
                # Look for autonomy_percentage (should be around 74%)
                autonomy_percentage = calculation.get("autonomy_percentage")
                self.log_result(f"📊 autonomy_percentage (autoconsumption): {autonomy_percentage}%")
                
                # Look for real_savings_percentage (this might be the 71% field)
                real_savings_percentage = calculation.get("real_savings_percentage")
                if real_savings_percentage:
                    self.log_result(f"💰 real_savings_percentage: {real_savings_percentage}%")
                
                # Search for any field with "savings", "economic", "economy" in the name
                savings_related_fields = {}
                for key, value in calculation.items():
                    if any(term in key.lower() for term in ["savings", "economic", "economy", "save"]):
                        savings_related_fields[key] = value
                
                self.log_result("💡 All savings/economy related fields:", savings_related_fields)
                
                # Calculate potential savings percentage manually
                annual_edf_bill = calculation.get("annual_edf_bill", 0)
                estimated_savings = calculation.get("estimated_savings", 0)
                
                if annual_edf_bill > 0 and estimated_savings > 0:
                    calculated_savings_percentage = (estimated_savings / annual_edf_bill) * 100
                    self.log_result(f"🧮 Manually calculated savings percentage: {calculated_savings_percentage:.1f}%")
                    self.log_result(f"   Based on: {estimated_savings}€ savings / {annual_edf_bill}€ annual bill")
                
                # Look for any field that equals exactly 71 or close to it
                exact_71_fields = {}
                for key, value in calculation.items():
                    if isinstance(value, (int, float)) and abs(value - 71) < 1:
                        exact_71_fields[key] = value
                
                if exact_71_fields:
                    self.log_result("🎯 FOUND FIELDS WITH VALUE ~71:", exact_71_fields)
                else:
                    self.log_result("⚠️ No fields found with value exactly around 71")
                
                # Print key calculation details
                key_details = {
                    "kit_power": calculation.get("kit_power"),
                    "estimated_production": calculation.get("estimated_production"),
                    "annual_consumption": 11990,  # From our test client
                    "autonomy_percentage": calculation.get("autonomy_percentage"),
                    "real_savings_percentage": calculation.get("real_savings_percentage"),
                    "estimated_savings": calculation.get("estimated_savings"),
                    "annual_edf_bill": calculation.get("annual_edf_bill"),
                    "monthly_savings": calculation.get("monthly_savings")
                }
                
                self.log_result("📋 Key calculation details:", key_details)
                
                # Save full response for analysis
                with open("/app/full_calculate_response.json", "w") as f:
                    json.dump(calculation, f, indent=2)
                
                self.log_result("💾 Full API response saved to /app/full_calculate_response.json")
                
                return calculation
                
            else:
                self.log_result(f"❌ Calculate API failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.log_result(f"❌ Error testing calculate API: {str(e)}")
            return None
    
    def search_for_71_percent_field(self, calculation_data):
        """Deep search for the 71% field in the calculation data"""
        if not calculation_data:
            return
        
        self.log_result("🔍 DEEP SEARCH FOR 71% FIELD:")
        
        # Function to recursively search through nested data
        def search_nested(data, path=""):
            results = []
            if isinstance(data, dict):
                for key, value in data.items():
                    current_path = f"{path}.{key}" if path else key
                    if isinstance(value, (int, float)):
                        if 70 <= value <= 72:  # Looking for values around 71
                            results.append((current_path, value))
                    elif isinstance(value, (dict, list)):
                        results.extend(search_nested(value, current_path))
            elif isinstance(data, list):
                for i, item in enumerate(data):
                    current_path = f"{path}[{i}]"
                    results.extend(search_nested(item, current_path))
            return results
        
        # Search for values around 71
        results_71 = search_nested(calculation_data)
        
        if results_71:
            self.log_result("🎯 FOUND VALUES AROUND 71%:")
            for path, value in results_71:
                self.log_result(f"   {path}: {value}")
        else:
            self.log_result("⚠️ No values found around 71%")
        
        # Also search for common field names that might contain savings percentage
        potential_field_names = [
            "savings_percentage", "economic_percentage", "economy_rate", 
            "real_savings_percentage", "effective_savings_percentage",
            "savings_rate", "economy_percentage", "financial_savings_percentage"
        ]
        
        found_fields = {}
        for field_name in potential_field_names:
            if field_name in calculation_data:
                found_fields[field_name] = calculation_data[field_name]
        
        if found_fields:
            self.log_result("💡 Found potential savings percentage fields:", found_fields)
        else:
            self.log_result("⚠️ None of the expected field names found")
    
    def run_test(self):
        """Run the complete test to identify the 71% savings field"""
        self.log_result("🚀 Starting test to identify 71% savings percentage field")
        self.log_result("📋 Test parameters: 11990 kWh/an consumption, 6kW recommended, Martinique region")
        
        # Step 1: Create test client
        if not self.create_test_client():
            return
        
        # Step 2: Test calculate API
        calculation_data = self.test_calculate_api_for_savings_percentage()
        
        # Step 3: Deep search for 71% field
        self.search_for_71_percent_field(calculation_data)
        
        self.log_result("✅ Test completed. Check the results above to identify the 71% savings field.")

if __name__ == "__main__":
    tester = SavingsPercentageTester()
    tester.run_test()