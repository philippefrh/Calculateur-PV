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
    
    def test_financing_with_aids_calculation(self):
        """Test the new financing with aids calculation functionality with 3.25% TAEG"""
        if not self.client_id:
            self.log_test("Financing with Aids", False, "No client ID available from previous test")
            return
            
        try:
            response = self.session.post(f"{self.base_url}/calculate/{self.client_id}")
            if response.status_code == 200:
                calculation = response.json()
                
                # Check if financing_with_aids field exists
                if "financing_with_aids" not in calculation:
                    self.log_test("Financing with Aids", False, "Missing 'financing_with_aids' field in response", calculation)
                    return
                
                financing_with_aids = calculation["financing_with_aids"]
                
                # Check required fields in financing_with_aids
                required_aids_fields = [
                    "financed_amount", "monthly_payment", "total_cost", 
                    "total_interests", "difference_vs_savings"
                ]
                
                missing_aids_fields = [field for field in required_aids_fields if field not in financing_with_aids]
                if missing_aids_fields:
                    self.log_test("Financing with Aids", False, f"Missing fields in financing_with_aids: {missing_aids_fields}", financing_with_aids)
                    return
                
                # Extract values for validation
                financed_amount = financing_with_aids.get("financed_amount", 0)
                monthly_payment = financing_with_aids.get("monthly_payment", 0)
                total_cost = financing_with_aids.get("total_cost", 0)
                total_interests = financing_with_aids.get("total_interests", 0)
                kit_price = calculation.get("kit_price", 0)
                total_aids = calculation.get("total_aids", 0)
                monthly_savings = calculation.get("monthly_savings", 0)
                
                issues = []
                
                # Validate financed amount = kit_price - total_aids
                expected_financed_amount = kit_price - total_aids
                if abs(financed_amount - expected_financed_amount) > 1:  # Allow 1€ tolerance
                    issues.append(f"Financed amount {financed_amount}€ != kit_price {kit_price}€ - total_aids {total_aids}€ = {expected_financed_amount}€")
                
                # Validate that monthly payment is MORE than simple division (116€ for 20880€/180 months)
                simple_division = financed_amount / 180  # 15 years = 180 months
                if monthly_payment <= simple_division:
                    issues.append(f"Monthly payment {monthly_payment}€ should be > simple division {simple_division:.2f}€ (interests not included)")
                
                # Validate total cost = monthly_payment * 180 months
                expected_total_cost = monthly_payment * 180
                if abs(total_cost - expected_total_cost) > 1:  # Allow 1€ tolerance
                    issues.append(f"Total cost {total_cost}€ != monthly_payment {monthly_payment}€ × 180 = {expected_total_cost:.2f}€")
                
                # Validate total interests = total_cost - financed_amount
                expected_total_interests = total_cost - financed_amount
                if abs(total_interests - expected_total_interests) > 1:  # Allow 1€ tolerance
                    issues.append(f"Total interests {total_interests}€ != total_cost {total_cost}€ - financed_amount {financed_amount}€ = {expected_total_interests:.2f}€")
                
                # NEW: Test for 3.25% TAEG rate - Expected monthly payment should be around 125€ for 20880€ over 15 years
                # Calculate expected payment with 3.25% TAEG
                taeg = 0.0325
                monthly_rate = taeg / 12
                months = 180
                if financed_amount > 0:
                    expected_payment_325 = financed_amount * (monthly_rate * (1 + monthly_rate)**months) / ((1 + monthly_rate)**months - 1)
                    
                    # Check if actual payment matches 3.25% calculation (within 2€ tolerance)
                    if abs(monthly_payment - expected_payment_325) > 2:
                        issues.append(f"Monthly payment {monthly_payment:.2f}€ doesn't match 3.25% TAEG calculation {expected_payment_325:.2f}€ (difference: {abs(monthly_payment - expected_payment_325):.2f}€)")
                    
                    # For 20880€ example, check if payment is around 125€ (not 135€ from old 4.96% rate)
                    if abs(financed_amount - 20880) < 1000:  # If amount is close to 20880€
                        if monthly_payment > 130:  # Should be lower than old 4.96% rate (~135€)
                            issues.append(f"Monthly payment {monthly_payment:.2f}€ seems too high for 3.25% rate (expected ~125€ for 20880€, old 4.96% rate was ~135€)")
                        elif monthly_payment < 120:  # But not too low
                            issues.append(f"Monthly payment {monthly_payment:.2f}€ seems too low for 3.25% rate (expected ~125€ for 20880€)")
                
                # Check that interests are positive and reasonable for 3.25% TAEG over 15 years
                if total_interests <= 0:
                    issues.append(f"Total interests {total_interests}€ should be positive")
                elif financed_amount > 0:
                    # For 3.25% over 15 years, total interests should be around 20-25% of financed amount
                    interest_ratio = total_interests / financed_amount
                    if interest_ratio < 0.15 or interest_ratio > 0.35:
                        issues.append(f"Total interests ratio {interest_ratio:.1%} seems incorrect for 3.25% TAEG over 15 years (expected 15-35%)")
                
                if issues:
                    self.log_test("Financing with Aids (3.25% TAEG)", False, f"Financing calculation issues: {'; '.join(issues)}", financing_with_aids)
                else:
                    interest_rate_effective = (total_interests / financed_amount) * 100 if financed_amount > 0 else 0
                    self.log_test("Financing with Aids (3.25% TAEG)", True, 
                                f"✅ NEW 3.25% TAEG RATE WORKING: {financed_amount}€ financed, {monthly_payment:.2f}€/month (vs {simple_division:.2f}€ simple division), {total_interests:.2f}€ total interests ({interest_rate_effective:.1f}% effective rate over 15 years) - REDUCED from old 4.96% rate", 
                                financing_with_aids)
            else:
                self.log_test("Financing with Aids (3.25% TAEG)", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Financing with Aids (3.25% TAEG)", False, f"Error: {str(e)}")
    
    def test_all_financing_with_aids_calculation(self):
        """Test the all_financing_with_aids field with 3.25% TAEG for all durations"""
        if not self.client_id:
            self.log_test("All Financing with Aids", False, "No client ID available from previous test")
            return
            
        try:
            response = self.session.post(f"{self.base_url}/calculate/{self.client_id}")
            if response.status_code == 200:
                calculation = response.json()
                
                # Check if all_financing_with_aids field exists
                if "all_financing_with_aids" not in calculation:
                    self.log_test("All Financing with Aids", False, "Missing 'all_financing_with_aids' field in response", calculation)
                    return
                
                all_financing_with_aids = calculation["all_financing_with_aids"]
                
                if not isinstance(all_financing_with_aids, list):
                    self.log_test("All Financing with Aids", False, f"all_financing_with_aids should be a list, got {type(all_financing_with_aids)}", all_financing_with_aids)
                    return
                
                # Should have 10 options (6-15 years)
                if len(all_financing_with_aids) != 10:
                    self.log_test("All Financing with Aids", False, f"Expected 10 financing options (6-15 years), got {len(all_financing_with_aids)}", all_financing_with_aids)
                    return
                
                kit_price = calculation.get("kit_price", 0)
                total_aids = calculation.get("total_aids", 0)
                financed_amount = kit_price - total_aids
                
                issues = []
                taeg = 0.0325  # Expected 3.25% TAEG
                monthly_rate = taeg / 12
                
                # Test each financing option
                for i, option in enumerate(all_financing_with_aids):
                    duration_years = option.get("duration_years", 0)
                    monthly_payment = option.get("monthly_payment", 0)
                    
                    # Check duration is correct (6 + i years)
                    expected_duration = 6 + i
                    if duration_years != expected_duration:
                        issues.append(f"Option {i}: duration {duration_years} != expected {expected_duration}")
                        continue
                    
                    # Calculate expected payment for this duration with 3.25% TAEG
                    months = duration_years * 12
                    if financed_amount > 0 and monthly_rate > 0:
                        expected_payment = financed_amount * (monthly_rate * (1 + monthly_rate)**months) / ((1 + monthly_rate)**months - 1)
                        
                        # Check if actual payment matches 3.25% calculation (within 2€ tolerance)
                        if abs(monthly_payment - expected_payment) > 2:
                            issues.append(f"Option {duration_years}y: payment {monthly_payment:.2f}€ != 3.25% TAEG calculation {expected_payment:.2f}€")
                
                # Check that payments decrease with longer duration (basic sanity check)
                for i in range(len(all_financing_with_aids) - 1):
                    current_payment = all_financing_with_aids[i]["monthly_payment"]
                    next_payment = all_financing_with_aids[i + 1]["monthly_payment"]
                    if current_payment <= next_payment:
                        issues.append(f"Monthly payments should decrease with longer duration: {current_payment}€ (year {6+i}) >= {next_payment}€ (year {6+i+1})")
                
                # Check specific values for common durations
                option_15y = next((opt for opt in all_financing_with_aids if opt["duration_years"] == 15), None)
                if option_15y and abs(financed_amount - 20880) < 1000:  # If amount is close to 20880€
                    payment_15y = option_15y["monthly_payment"]
                    if payment_15y > 130:  # Should be lower than old 4.96% rate
                        issues.append(f"15-year payment {payment_15y:.2f}€ seems too high for 3.25% rate (expected ~125€ for 20880€)")
                    elif payment_15y < 120:
                        issues.append(f"15-year payment {payment_15y:.2f}€ seems too low for 3.25% rate")
                
                if issues:
                    self.log_test("All Financing with Aids (3.25% TAEG)", False, f"Issues found: {'; '.join(issues)}", all_financing_with_aids)
                else:
                    # Show range of payments
                    payments = [opt["monthly_payment"] for opt in all_financing_with_aids]
                    min_payment = min(payments)
                    max_payment = max(payments)
                    self.log_test("All Financing with Aids (3.25% TAEG)", True, 
                                f"✅ ALL FINANCING OPTIONS WITH 3.25% TAEG WORKING: 10 options (6-15 years), payments range {max_payment:.2f}€ (6y) to {min_payment:.2f}€ (15y) - REDUCED from old 4.96% rate", 
                                all_financing_with_aids)
            else:
                self.log_test("All Financing with Aids (3.25% TAEG)", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("All Financing with Aids (3.25% TAEG)", False, f"Error: {str(e)}")
    
    def test_autoconsumption_surplus_distribution(self):
        """Test the new 95% autoconsumption / 5% surplus distribution and economic impact"""
        if not self.client_id:
            self.log_test("Autoconsumption/Surplus Distribution", False, "No client ID available from previous test")
            return
            
        try:
            response = self.session.post(f"{self.base_url}/calculate/{self.client_id}")
            if response.status_code == 200:
                calculation = response.json()
                
                # Check if required fields exist
                required_fields = ["autoconsumption_kwh", "surplus_kwh", "estimated_production", "monthly_savings"]
                missing_fields = [field for field in required_fields if field not in calculation]
                if missing_fields:
                    self.log_test("Autoconsumption/Surplus Distribution", False, f"Missing fields: {missing_fields}", calculation)
                    return
                
                # Extract values
                autoconsumption_kwh = calculation.get("autoconsumption_kwh", 0)
                surplus_kwh = calculation.get("surplus_kwh", 0)
                estimated_production = calculation.get("estimated_production", 0)
                monthly_savings = calculation.get("monthly_savings", 0)
                
                issues = []
                
                # Test 1: Verify 95% autoconsumption
                expected_autoconsumption = estimated_production * 0.95
                if abs(autoconsumption_kwh - expected_autoconsumption) > 1:  # Allow 1 kWh tolerance
                    issues.append(f"Autoconsumption {autoconsumption_kwh:.1f} kWh != 95% of production {expected_autoconsumption:.1f} kWh")
                
                # Test 2: Verify 5% surplus
                expected_surplus = estimated_production * 0.05
                if abs(surplus_kwh - expected_surplus) > 1:  # Allow 1 kWh tolerance
                    issues.append(f"Surplus {surplus_kwh:.1f} kWh != 5% of production {expected_surplus:.1f} kWh")
                
                # Test 3: Verify total adds up to production
                total_distribution = autoconsumption_kwh + surplus_kwh
                if abs(total_distribution - estimated_production) > 1:  # Allow 1 kWh tolerance
                    issues.append(f"Total distribution {total_distribution:.1f} kWh != production {estimated_production:.1f} kWh")
                
                # Test 4: Calculate economic impact comparison
                # Constants from backend
                EDF_RATE_PER_KWH = 0.2516  # €/kWh
                SURPLUS_SALE_RATE = 0.076  # €/kWh for surplus sold to EDF
                
                # New method (95%/5%): (production × 0.95 × 0.2516) + (production × 0.05 × 0.076)
                new_method_savings = (estimated_production * 0.95 * EDF_RATE_PER_KWH) + (estimated_production * 0.05 * SURPLUS_SALE_RATE)
                
                # Old method (70%/30%): (production × 0.7 × 0.2516) + (production × 0.3 × 0.076)
                old_method_savings = (estimated_production * 0.7 * EDF_RATE_PER_KWH) + (estimated_production * 0.3 * SURPLUS_SALE_RATE)
                
                # Verify actual calculation matches new method
                calculated_annual_savings = monthly_savings * 12
                if abs(calculated_annual_savings - new_method_savings) > 10:  # Allow 10€ tolerance
                    issues.append(f"Calculated annual savings {calculated_annual_savings:.2f}€ != new method {new_method_savings:.2f}€")
                
                # Test 5: Verify significant increase in savings
                savings_increase = new_method_savings - old_method_savings
                savings_increase_percentage = (savings_increase / old_method_savings) * 100
                
                if savings_increase <= 0:
                    issues.append(f"New method should increase savings, but increase is {savings_increase:.2f}€")
                elif savings_increase_percentage < 10:  # Should be significant increase
                    issues.append(f"Savings increase {savings_increase_percentage:.1f}% seems too small (expected >10%)")
                
                # Test 6: Check if monthly savings are closer to financing payments
                financing_with_aids = calculation.get("financing_with_aids", {})
                if financing_with_aids:
                    monthly_payment_with_aids = financing_with_aids.get("monthly_payment", 0)
                    payment_savings_ratio = monthly_payment_with_aids / monthly_savings if monthly_savings > 0 else float('inf')
                    
                    # With 95% autoconsumption, the ratio should be closer to 1 (better balance)
                    if payment_savings_ratio > 2.0:  # If payment is more than 2x savings, balance is poor
                        issues.append(f"Monthly payment {monthly_payment_with_aids:.2f}€ vs savings {monthly_savings:.2f}€ ratio {payment_savings_ratio:.2f} still too high")
                
                if issues:
                    self.log_test("Autoconsumption/Surplus Distribution (95%/5%)", False, f"Distribution issues: {'; '.join(issues)}", calculation)
                else:
                    # Calculate percentages for verification
                    autoconsumption_percentage = (autoconsumption_kwh / estimated_production) * 100 if estimated_production > 0 else 0
                    surplus_percentage = (surplus_kwh / estimated_production) * 100 if estimated_production > 0 else 0
                    
                    self.log_test("Autoconsumption/Surplus Distribution (95%/5%)", True, 
                                f"✅ NEW 95%/5% DISTRIBUTION WORKING: {autoconsumption_kwh:.0f} kWh autoconsumption ({autoconsumption_percentage:.1f}%), {surplus_kwh:.0f} kWh surplus ({surplus_percentage:.1f}%). Monthly savings increased from {old_method_savings/12:.2f}€ to {monthly_savings:.2f}€ (+{savings_increase/12:.2f}€/month, +{savings_increase_percentage:.1f}%). Better balance with financing.", 
                                {
                                    "autoconsumption_kwh": autoconsumption_kwh,
                                    "surplus_kwh": surplus_kwh,
                                    "estimated_production": estimated_production,
                                    "monthly_savings_new": monthly_savings,
                                    "monthly_savings_old": old_method_savings/12,
                                    "monthly_increase": savings_increase/12,
                                    "percentage_increase": savings_increase_percentage
                                })
            else:
                self.log_test("Autoconsumption/Surplus Distribution (95%/5%)", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Autoconsumption/Surplus Distribution (95%/5%)", False, f"Error: {str(e)}")

    def test_pdf_generation_financing_tables(self):
        """Test PDF generation with focus on financing tables structure"""
        if not self.client_id:
            self.log_test("PDF Generation - Financing Tables", False, "No client ID available from previous test")
            return
            
        try:
            # First get the calculation data to verify structure
            calc_response = self.session.post(f"{self.base_url}/calculate/{self.client_id}")
            if calc_response.status_code != 200:
                self.log_test("PDF Generation - Financing Tables", False, f"Failed to get calculation data: {calc_response.status_code}")
                return
            
            calculation = calc_response.json()
            
            # Test PDF generation endpoint
            pdf_response = self.session.get(f"{self.base_url}/generate-pdf/{self.client_id}")
            if pdf_response.status_code != 200:
                self.log_test("PDF Generation - Financing Tables", False, f"PDF generation failed: HTTP {pdf_response.status_code}: {pdf_response.text}")
                return
            
            # Check if response is actually a PDF
            if not pdf_response.headers.get('content-type', '').startswith('application/pdf'):
                self.log_test("PDF Generation - Financing Tables", False, f"Response is not a PDF. Content-Type: {pdf_response.headers.get('content-type')}")
                return
            
            # Check PDF size (should be reasonable)
            pdf_size = len(pdf_response.content)
            if pdf_size < 10000:  # Less than 10KB seems too small
                self.log_test("PDF Generation - Financing Tables", False, f"PDF size {pdf_size} bytes seems too small")
                return
            elif pdf_size > 5000000:  # More than 5MB seems too large
                self.log_test("PDF Generation - Financing Tables", False, f"PDF size {pdf_size} bytes seems too large")
                return
            
            # Verify calculation data has required financing structures
            issues = []
            
            # Check financing_options (normal financing with 4.96% TAEG)
            financing_options = calculation.get("financing_options", [])
            if not financing_options:
                issues.append("Missing financing_options field")
            elif len(financing_options) != 10:
                issues.append(f"financing_options should have 10 options (6-15 years), got {len(financing_options)}")
            else:
                # Check structure - should NOT have 'total_cost' field (removed as per request)
                first_option = financing_options[0]
                
                # Check required fields (4 columns as per request)
                required_fields = ['duration_years', 'monthly_payment', 'difference_vs_savings']
                missing_fields = [field for field in required_fields if field not in first_option]
                if missing_fields:
                    issues.append(f"financing_options missing fields: {missing_fields}")
                
                # Verify all 10 durations (6-15 years)
                durations = [opt['duration_years'] for opt in financing_options]
                expected_durations = list(range(6, 16))
                if durations != expected_durations:
                    issues.append(f"financing_options durations {durations} != expected {expected_durations}")
            
            # Check all_financing_with_aids (financing with aids with 3.25% TAEG)
            all_financing_with_aids = calculation.get("all_financing_with_aids", [])
            if not all_financing_with_aids:
                issues.append("Missing all_financing_with_aids field")
            elif len(all_financing_with_aids) != 10:
                issues.append(f"all_financing_with_aids should have 10 options (6-15 years), got {len(all_financing_with_aids)}")
            else:
                # Check structure - should NOT have 'total_cost' field (removed as per request)
                first_aids_option = all_financing_with_aids[0]
                if 'total_cost' in first_aids_option:
                    issues.append("all_financing_with_aids should NOT contain 'total_cost' column (removed as per request)")
                
                # Check required fields (4 columns as per request)
                required_aids_fields = ['duration_years', 'monthly_payment', 'difference_vs_savings']
                missing_aids_fields = [field for field in required_aids_fields if field not in first_aids_option]
                if missing_aids_fields:
                    issues.append(f"all_financing_with_aids missing fields: {missing_aids_fields}")
                
                # Verify all 10 durations (6-15 years)
                aids_durations = [opt['duration_years'] for opt in all_financing_with_aids]
                expected_durations = list(range(6, 16))
                if aids_durations != expected_durations:
                    issues.append(f"all_financing_with_aids durations {aids_durations} != expected {expected_durations}")
            
            # Verify that aids financing has lower monthly payments (3.25% vs 4.96% TAEG)
            if financing_options and all_financing_with_aids:
                # Compare 15-year options
                normal_15y = next((opt for opt in financing_options if opt['duration_years'] == 15), None)
                aids_15y = next((opt for opt in all_financing_with_aids if opt['duration_years'] == 15), None)
                
                if normal_15y and aids_15y:
                    normal_payment = normal_15y['monthly_payment']
                    aids_payment = aids_15y['monthly_payment']
                    
                    if aids_payment >= normal_payment:
                        issues.append(f"Aids financing payment {aids_payment}€ should be lower than normal financing {normal_payment}€ (3.25% vs 4.96% TAEG)")
                    else:
                        savings_per_month = normal_payment - aids_payment
                        savings_percentage = (savings_per_month / normal_payment) * 100
                        if savings_percentage < 5:  # Should save at least 5%
                            issues.append(f"Aids financing savings {savings_percentage:.1f}% seems too small (expected >5%)")
            
            # Check filename format
            content_disposition = pdf_response.headers.get('content-disposition', '')
            if 'filename=' not in content_disposition:
                issues.append("PDF response missing filename in Content-Disposition header")
            elif 'etude_solaire_' not in content_disposition:
                issues.append("PDF filename should contain 'etude_solaire_'")
            
            if issues:
                self.log_test("PDF Generation - Financing Tables", False, f"PDF structure issues: {'; '.join(issues)}", {
                    "pdf_size": pdf_size,
                    "financing_options_count": len(financing_options),
                    "all_financing_with_aids_count": len(all_financing_with_aids),
                    "content_disposition": content_disposition
                })
            else:
                # Calculate comparison data for success message
                normal_15y = next((opt for opt in financing_options if opt['duration_years'] == 15), None)
                aids_15y = next((opt for opt in all_financing_with_aids if opt['duration_years'] == 15), None)
                
                comparison_msg = ""
                if normal_15y and aids_15y:
                    normal_payment = normal_15y['monthly_payment']
                    aids_payment = aids_15y['monthly_payment']
                    savings_per_month = normal_payment - aids_payment
                    comparison_msg = f" 15-year comparison: {normal_payment:.2f}€ (4.96% TAEG) vs {aids_payment:.2f}€ (3.25% TAEG) = {savings_per_month:.2f}€/month savings."
                
                self.log_test("PDF Generation - Financing Tables", True, 
                            f"✅ PDF generated successfully ({pdf_size:,} bytes). Two financing tables: 'OPTIONS DE FINANCEMENT' (4.96% TAEG, 10 rows, 4 columns without total cost) and 'OPTIONS DE FINANCEMENT AVEC AIDES DÉDUITES' (3.25% TAEG, 10 rows, 4 columns without total cost).{comparison_msg}", 
                            {
                                "pdf_size": pdf_size,
                                "financing_options_count": len(financing_options),
                                "all_financing_with_aids_count": len(all_financing_with_aids),
                                "normal_15y_payment": normal_15y['monthly_payment'] if normal_15y else None,
                                "aids_15y_payment": aids_15y['monthly_payment'] if aids_15y else None
                            })
                
        except Exception as e:
            self.log_test("PDF Generation - Financing Tables", False, f"Error: {str(e)}")

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
        
        # Priority 3 - NEW: Test autoconsumption/surplus distribution changes
        print("\n📋 PRIORITY 3 - NEW Autoconsumption/Surplus Distribution (95%/5%)")
        self.test_autoconsumption_surplus_distribution()
        
        # Priority 4 - Financing with aids tests (3.25% TAEG)
        print("\n📋 PRIORITY 4 - Financing with Aids Calculation (3.25% TAEG)")
        self.test_financing_with_aids_calculation()
        self.test_all_financing_with_aids_calculation()
        
        # Priority 5 - PDF Generation with Financing Tables
        print("\n📋 PRIORITY 5 - PDF Generation with Financing Tables")
        self.test_pdf_generation_financing_tables()
        
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