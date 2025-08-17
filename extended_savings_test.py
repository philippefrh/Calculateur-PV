#!/usr/bin/env python3
"""
Extended test to find the 71% savings field by testing different calculation modes and parameters
"""

import requests
import json
import time
from typing import Dict, Any, Optional

# Backend URL from frontend environment
BACKEND_URL = "https://pdf-solar-quote.preview.emergentagent.com/api"

class ExtendedSavingsTest:
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
                "last_name": "Client71",
                "address": "Fort-de-France, Martinique",
                "phone": "0596123456",
                "email": "test71@martinique.com",
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
                self.log_result(f"✅ Client created successfully", {"client_id": self.client_id})
                return True
            else:
                self.log_result(f"❌ Failed to create client: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            self.log_result(f"❌ Error creating client: {str(e)}")
            return False
    
    def test_different_calculation_modes(self):
        """Test both realistic and optimistic calculation modes"""
        if not self.client_id:
            return
        
        modes = ["realistic", "optimistic"]
        results = {}
        
        for mode in modes:
            try:
                self.log_result(f"🧪 Testing calculation mode: {mode}")
                
                response = self.session.post(
                    f"{self.base_url}/calculate/{self.client_id}",
                    params={
                        "region": "martinique",
                        "calculation_mode": mode,
                        "manual_kit_power": 6
                    }
                )
                
                if response.status_code == 200:
                    calculation = response.json()
                    
                    # Extract key percentage values
                    key_values = {
                        "autonomy_percentage": calculation.get("autonomy_percentage"),
                        "real_savings_percentage": calculation.get("real_savings_percentage"),
                        "autoconsumption_rate": calculation.get("autoconsumption_rate"),
                        "estimated_savings": calculation.get("estimated_savings"),
                        "monthly_savings": calculation.get("monthly_savings"),
                        "annual_edf_bill": calculation.get("annual_edf_bill")
                    }
                    
                    results[mode] = key_values
                    
                    # Look for any value around 71
                    values_around_71 = {}
                    for key, value in calculation.items():
                        if isinstance(value, (int, float)) and 70 <= value <= 72:
                            values_around_71[key] = value
                    
                    self.log_result(f"📊 {mode.upper()} mode key values:", key_values)
                    if values_around_71:
                        self.log_result(f"🎯 Values around 71% in {mode} mode:", values_around_71)
                    
                    # Calculate different savings percentages
                    if calculation.get("annual_edf_bill") and calculation.get("estimated_savings"):
                        annual_bill = calculation.get("annual_edf_bill")
                        savings = calculation.get("estimated_savings")
                        
                        # Standard savings percentage
                        standard_savings_pct = (savings / annual_bill) * 100
                        
                        # Maybe the 71% is based on monthly values?
                        monthly_bill = calculation.get("monthly_edf_payment", annual_bill / 12)
                        monthly_savings = calculation.get("monthly_savings", 0)
                        monthly_savings_pct = (monthly_savings / monthly_bill) * 100 if monthly_bill > 0 else 0
                        
                        # Or maybe it's based on consumption vs production?
                        production = calculation.get("estimated_production", 0)
                        consumption = 11990  # Our test consumption
                        production_vs_consumption_pct = (production / consumption) * 100 if consumption > 0 else 0
                        
                        # Or autonomy-based savings?
                        autonomy_pct = calculation.get("autonomy_percentage", 0)
                        
                        calculated_percentages = {
                            "standard_savings_percentage": round(standard_savings_pct, 1),
                            "monthly_savings_percentage": round(monthly_savings_pct, 1),
                            "production_vs_consumption_percentage": round(production_vs_consumption_pct, 1),
                            "autonomy_percentage": round(autonomy_pct, 1)
                        }
                        
                        self.log_result(f"🧮 Calculated percentages for {mode}:", calculated_percentages)
                        
                        # Check if any of these equals ~71%
                        for calc_name, calc_value in calculated_percentages.items():
                            if 70 <= calc_value <= 72:
                                self.log_result(f"🎯 POTENTIAL 71% FIELD FOUND: {calc_name} = {calc_value}%")
                
                else:
                    self.log_result(f"❌ Failed to get calculation for {mode}: {response.status_code}")
                    
            except Exception as e:
                self.log_result(f"❌ Error testing {mode} mode: {str(e)}")
        
        return results
    
    def test_with_different_consumption_values(self):
        """Test with different consumption values to see if we can get 71%"""
        consumption_values = [10000, 11000, 11990, 12000, 13000, 14000]
        
        for consumption in consumption_values:
            try:
                # Create client with specific consumption
                client_data = {
                    "first_name": "Test",
                    "last_name": f"Client{consumption}",
                    "address": "Fort-de-France, Martinique",
                    "phone": "0596123456",
                    "email": f"test{consumption}@martinique.com",
                    "roof_surface": 100.0,
                    "roof_orientation": "Sud",
                    "velux_count": 0,
                    "heating_system": "Climatisation",
                    "water_heating_system": "Ballon électrique",
                    "water_heating_capacity": 200,
                    "annual_consumption_kwh": float(consumption),
                    "monthly_edf_payment": consumption * 0.0375,  # Approximate monthly bill
                    "annual_edf_payment": consumption * 0.45  # Approximate annual bill
                }
                
                response = self.session.post(f"{self.base_url}/clients", json=client_data)
                if response.status_code == 200:
                    client = response.json()
                    test_client_id = client["id"]
                    
                    # Calculate with 6kW
                    calc_response = self.session.post(
                        f"{self.base_url}/calculate/{test_client_id}",
                        params={
                            "region": "martinique",
                            "manual_kit_power": 6
                        }
                    )
                    
                    if calc_response.status_code == 200:
                        calculation = calc_response.json()
                        
                        # Check key percentages
                        autonomy_pct = calculation.get("autonomy_percentage", 0)
                        real_savings_pct = calculation.get("real_savings_percentage", 0)
                        
                        # Calculate production vs consumption percentage
                        production = calculation.get("estimated_production", 0)
                        prod_vs_cons_pct = (production / consumption) * 100 if consumption > 0 else 0
                        
                        result_summary = {
                            "consumption": consumption,
                            "autonomy_percentage": round(autonomy_pct, 1),
                            "real_savings_percentage": round(real_savings_pct, 1),
                            "production_vs_consumption": round(prod_vs_cons_pct, 1),
                            "production": round(production, 0)
                        }
                        
                        # Check if any value is around 71%
                        values_around_71 = []
                        for key, value in result_summary.items():
                            if isinstance(value, (int, float)) and 70 <= value <= 72:
                                values_around_71.append(f"{key}={value}%")
                        
                        if values_around_71:
                            self.log_result(f"🎯 FOUND 71% VALUES for {consumption} kWh:", result_summary)
                        else:
                            self.log_result(f"📊 Results for {consumption} kWh:", result_summary)
                
            except Exception as e:
                self.log_result(f"❌ Error testing consumption {consumption}: {str(e)}")
    
    def analyze_calculation_config(self):
        """Analyze the calculation configuration to understand the 71% source"""
        try:
            # Get the calculation with full details
            response = self.session.post(
                f"{self.base_url}/calculate/{self.client_id}",
                params={
                    "region": "martinique",
                    "calculation_mode": "realistic",
                    "manual_kit_power": 6
                }
            )
            
            if response.status_code == 200:
                calculation = response.json()
                
                # Look at calculation_config
                calc_config = calculation.get("calculation_config", {})
                self.log_result("🔧 Calculation configuration:", calc_config)
                
                # Look at region_config
                region_config = calculation.get("region_config", {})
                self.log_result("🌍 Region configuration (partial):", {
                    "name": region_config.get("name"),
                    "interest_rates": region_config.get("interest_rates"),
                    "financing": region_config.get("financing")
                })
                
                # Analyze the calculation breakdown
                production = calculation.get("estimated_production", 0)
                consumption = 11990
                autoconsumption_kwh = calculation.get("autoconsumption_kwh", 0)
                surplus_kwh = calculation.get("surplus_kwh", 0)
                
                breakdown = {
                    "annual_consumption": consumption,
                    "estimated_production": production,
                    "autoconsumption_kwh": autoconsumption_kwh,
                    "surplus_kwh": surplus_kwh,
                    "autonomy_percentage": calculation.get("autonomy_percentage"),
                    "autoconsumption_rate": calculation.get("autoconsumption_rate")
                }
                
                self.log_result("📊 Production/Consumption breakdown:", breakdown)
                
                # Maybe the 71% is related to the optimization coefficient?
                optimization_coeff = calc_config.get("optimization_coefficient", 1.0)
                if optimization_coeff != 1.0:
                    self.log_result(f"🔧 Optimization coefficient: {optimization_coeff}")
                    
                    # Calculate what the savings would be without optimization
                    base_savings = calculation.get("estimated_savings", 0) / optimization_coeff
                    optimized_savings = calculation.get("estimated_savings", 0)
                    optimization_impact = ((optimized_savings - base_savings) / base_savings) * 100 if base_savings > 0 else 0
                    
                    self.log_result(f"🎯 Optimization impact: {optimization_impact:.1f}%")
                    
                    if 70 <= optimization_impact <= 72:
                        self.log_result("🎯 FOUND IT! The 71% might be the optimization impact!")
                
        except Exception as e:
            self.log_result(f"❌ Error analyzing calculation config: {str(e)}")
    
    def run_extended_test(self):
        """Run the complete extended test"""
        self.log_result("🚀 Starting extended test to find 71% savings field")
        
        # Step 1: Create test client
        if not self.create_test_client():
            return
        
        # Step 2: Test different calculation modes
        self.log_result("🧪 Testing different calculation modes...")
        self.test_different_calculation_modes()
        
        # Step 3: Analyze calculation configuration
        self.log_result("🔧 Analyzing calculation configuration...")
        self.analyze_calculation_config()
        
        # Step 4: Test with different consumption values
        self.log_result("📊 Testing with different consumption values...")
        self.test_with_different_consumption_values()
        
        self.log_result("✅ Extended test completed.")

if __name__ == "__main__":
    tester = ExtendedSavingsTest()
    tester.run_extended_test()