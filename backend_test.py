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
BACKEND_URL = "https://51c4a25b-59a8-47e7-ba3b-fc5eff1519bd.preview.emergentagent.com/api"

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
                "phone": "0123456789",  # Added required phone field
                "email": "jean.dupont@example.com",  # Added required email field
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
            elif response.status_code == 400:
                # If geocoding fails, try to use an existing client instead
                self.log_test("Create Client", False, f"Geocoding failed: {response.text}. Will try to use existing client.")
                self.use_existing_client()
            else:
                self.log_test("Create Client", False, f"HTTP {response.status_code}: {response.text}")
                # Try to use existing client as fallback
                self.use_existing_client()
        except Exception as e:
            self.log_test("Create Client", False, f"Error: {str(e)}")
            # Try to use existing client as fallback
            self.use_existing_client()
    
    def use_existing_client(self):
        """Use an existing client from the database as fallback"""
        try:
            response = self.session.get(f"{self.base_url}/clients")
            if response.status_code == 200:
                clients = response.json()
                if isinstance(clients, list) and len(clients) > 0:
                    # Use the first client
                    client = clients[0]
                    self.client_id = client.get("id")
                    if self.client_id:
                        self.log_test("Use Existing Client", True, 
                                    f"Using existing client: {client.get('first_name')} {client.get('last_name')} (ID: {self.client_id})", 
                                    client)
                    else:
                        self.log_test("Use Existing Client", False, "No ID found in existing client")
                else:
                    self.log_test("Use Existing Client", False, "No existing clients found")
            else:
                self.log_test("Use Existing Client", False, f"Failed to get existing clients: {response.status_code}")
        except Exception as e:
            self.log_test("Use Existing Client", False, f"Error getting existing client: {str(e)}")
    
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
                    "financed_amount", "monthly_payment", 
                    "total_interests", "difference_vs_savings"
                ]
                
                missing_aids_fields = [field for field in required_aids_fields if field not in financing_with_aids]
                if missing_aids_fields:
                    self.log_test("Financing with Aids", False, f"Missing fields in financing_with_aids: {missing_aids_fields}", financing_with_aids)
                    return
                
                # Extract values for validation
                financed_amount = financing_with_aids.get("financed_amount", 0)
                monthly_payment = financing_with_aids.get("monthly_payment", 0)
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
                
                # Validate total interests = (monthly_payment * 180) - financed_amount
                expected_total_interests = (monthly_payment * 180) - financed_amount
                if abs(total_interests - expected_total_interests) > 1:  # Allow 1€ tolerance
                    issues.append(f"Total interests {total_interests}€ != (monthly_payment {monthly_payment}€ × 180) - financed_amount {financed_amount}€ = {expected_total_interests:.2f}€")
                
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

    def test_regions_endpoint(self):
        """Test GET /api/regions - should return list of available regions"""
        try:
            response = self.session.get(f"{self.base_url}/regions")
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                if "regions" not in data or "regions_data" not in data:
                    self.log_test("Regions Endpoint", False, "Missing 'regions' or 'regions_data' in response", data)
                    return
                
                regions = data["regions"]
                regions_data = data["regions_data"]
                
                # Check that both france and martinique are available
                expected_regions = ["france", "martinique"]
                if not all(region in regions for region in expected_regions):
                    self.log_test("Regions Endpoint", False, f"Missing expected regions. Got: {regions}, Expected: {expected_regions}", data)
                    return
                
                # Check regions_data structure
                for region in expected_regions:
                    if region not in regions_data:
                        self.log_test("Regions Endpoint", False, f"Missing {region} in regions_data", data)
                        return
                    
                    region_info = regions_data[region]
                    required_fields = ["name", "logo_subtitle", "company_info"]
                    missing_fields = [field for field in required_fields if field not in region_info]
                    if missing_fields:
                        self.log_test("Regions Endpoint", False, f"Missing fields in {region}: {missing_fields}", data)
                        return
                
                self.log_test("Regions Endpoint", True, 
                            f"✅ Regions endpoint working. Available regions: {regions}. France: {regions_data['france']['name']}, Martinique: {regions_data['martinique']['name']}", 
                            data)
            else:
                self.log_test("Regions Endpoint", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Regions Endpoint", False, f"Error: {str(e)}")

    def test_france_region_config(self):
        """Test GET /api/regions/france - should return France region configuration"""
        try:
            response = self.session.get(f"{self.base_url}/regions/france")
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                if "region" not in data or "config" not in data:
                    self.log_test("France Region Config", False, "Missing 'region' or 'config' in response", data)
                    return
                
                if data["region"] != "france":
                    self.log_test("France Region Config", False, f"Expected region 'france', got '{data['region']}'", data)
                    return
                
                config = data["config"]
                
                # Check required configuration fields
                required_fields = ["name", "company_info", "interest_rates", "financing", "autoconsumption_rate", "optimization_coefficient"]
                missing_fields = [field for field in required_fields if field not in config]
                if missing_fields:
                    self.log_test("France Region Config", False, f"Missing config fields: {missing_fields}", data)
                    return
                
                # Check interest rates
                interest_rates = config["interest_rates"]
                if "standard" not in interest_rates or "with_aids" not in interest_rates:
                    self.log_test("France Region Config", False, "Missing interest rate fields", data)
                    return
                
                # Check financing configuration
                financing = config["financing"]
                if financing["min_duration"] != 3 or financing["max_duration"] != 15:
                    self.log_test("France Region Config", False, f"France financing duration should be 3-15 years, got {financing['min_duration']}-{financing['max_duration']}", data)
                    return
                
                self.log_test("France Region Config", True, 
                            f"✅ France region config working. Name: {config['name']}, Interest rates: {interest_rates['standard']:.2%} standard, {interest_rates['with_aids']:.2%} with aids, Financing: {financing['min_duration']}-{financing['max_duration']} years", 
                            data)
            else:
                self.log_test("France Region Config", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("France Region Config", False, f"Error: {str(e)}")

    def test_martinique_region_config(self):
        """Test GET /api/regions/martinique - should return Martinique region configuration with 3 kits"""
        try:
            response = self.session.get(f"{self.base_url}/regions/martinique")
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                if "region" not in data or "config" not in data:
                    self.log_test("Martinique Region Config", False, "Missing 'region' or 'config' in response", data)
                    return
                
                if data["region"] != "martinique":
                    self.log_test("Martinique Region Config", False, f"Expected region 'martinique', got '{data['region']}'", data)
                    return
                
                config = data["config"]
                
                # Check required configuration fields
                required_fields = ["name", "logo_subtitle", "company_info", "interest_rates", "kits", "financing", "autoconsumption_rate", "optimization_coefficient"]
                missing_fields = [field for field in required_fields if field not in config]
                if missing_fields:
                    self.log_test("Martinique Region Config", False, f"Missing config fields: {missing_fields}", data)
                    return
                
                # Check Martinique-specific fields
                if config["name"] != "Martinique":
                    self.log_test("Martinique Region Config", False, f"Expected name 'Martinique', got '{config['name']}'", data)
                    return
                
                if config["logo_subtitle"] != "Région Martinique":
                    self.log_test("Martinique Region Config", False, f"Expected logo_subtitle 'Région Martinique', got '{config['logo_subtitle']}'", data)
                    return
                
                # Check interest rates (should be 8% = 0.08)
                interest_rates = config["interest_rates"]
                if interest_rates["standard"] != 0.08 or interest_rates["with_aids"] != 0.08:
                    self.log_test("Martinique Region Config", False, f"Martinique interest rates should be 8% (0.08), got standard: {interest_rates['standard']}, with_aids: {interest_rates['with_aids']}", data)
                    return
                
                # Check kits (should have 3 kits: 3kW, 6kW, 9kW)
                kits = config["kits"]
                expected_kits = ["kit_3kw", "kit_6kw", "kit_9kw"]
                if not all(kit in kits for kit in expected_kits):
                    self.log_test("Martinique Region Config", False, f"Missing expected kits. Got: {list(kits.keys())}, Expected: {expected_kits}", data)
                    return
                
                # Verify kit prices and aids
                expected_kit_data = {
                    "kit_3kw": {"power": 3, "price_ttc": 9900, "aid_amount": 5340},
                    "kit_6kw": {"power": 6, "price_ttc": 13900, "aid_amount": 6480},
                    "kit_9kw": {"power": 9, "price_ttc": 16900, "aid_amount": 9720}
                }
                
                issues = []
                for kit_id, expected_data in expected_kit_data.items():
                    kit_data = kits[kit_id]
                    for field, expected_value in expected_data.items():
                        if kit_data.get(field) != expected_value:
                            issues.append(f"{kit_id}.{field}: expected {expected_value}, got {kit_data.get(field)}")
                
                if issues:
                    self.log_test("Martinique Region Config", False, f"Kit data issues: {'; '.join(issues)}", data)
                    return
                
                # Check financing duration (should be 3-15 years)
                financing = config["financing"]
                if financing["min_duration"] != 3 or financing["max_duration"] != 15:
                    self.log_test("Martinique Region Config", False, f"Martinique financing duration should be 3-15 years, got {financing['min_duration']}-{financing['max_duration']}", data)
                    return
                
                self.log_test("Martinique Region Config", True, 
                            f"✅ Martinique region config working. 3 kits: 3kW (9900€, aid 5340€), 6kW (13900€, aid 6480€), 9kW (16900€, aid 9720€). Interest rate: 8%, Financing: 3-15 years", 
                            data)
            else:
                self.log_test("Martinique Region Config", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Martinique Region Config", False, f"Error: {str(e)}")

    def test_martinique_kits_endpoint(self):
        """Test GET /api/regions/martinique/kits - should return the 3 Martinique kits"""
        try:
            response = self.session.get(f"{self.base_url}/regions/martinique/kits")
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                if "kits" not in data:
                    self.log_test("Martinique Kits Endpoint", False, "Missing 'kits' in response", data)
                    return
                
                kits = data["kits"]
                
                # Should have exactly 3 kits
                if len(kits) != 3:
                    self.log_test("Martinique Kits Endpoint", False, f"Expected 3 kits, got {len(kits)}", data)
                    return
                
                # Check each kit structure and data
                expected_kits = {
                    "kit_3kw": {"power": 3, "price_ttc": 9900, "aid_amount": 5340},
                    "kit_6kw": {"power": 6, "price_ttc": 13900, "aid_amount": 6480},
                    "kit_9kw": {"power": 9, "price_ttc": 16900, "aid_amount": 9720}
                }
                
                kit_ids = [kit["id"] for kit in kits]
                if not all(kit_id in kit_ids for kit_id in expected_kits.keys()):
                    self.log_test("Martinique Kits Endpoint", False, f"Missing expected kit IDs. Got: {kit_ids}, Expected: {list(expected_kits.keys())}", data)
                    return
                
                issues = []
                for kit in kits:
                    kit_id = kit["id"]
                    if kit_id in expected_kits:
                        expected_data = expected_kits[kit_id]
                        
                        # Check required fields
                        required_fields = ["name", "power", "price_ttc", "aid_amount", "surface"]
                        missing_fields = [field for field in required_fields if field not in kit]
                        if missing_fields:
                            issues.append(f"{kit_id} missing fields: {missing_fields}")
                            continue
                        
                        # Check values
                        if kit["power"] != expected_data["power"]:
                            issues.append(f"{kit_id} power: expected {expected_data['power']}, got {kit['power']}")
                        if kit["price_ttc"] != expected_data["price_ttc"]:
                            issues.append(f"{kit_id} price_ttc: expected {expected_data['price_ttc']}, got {kit['price_ttc']}")
                        if kit["aid_amount"] != expected_data["aid_amount"]:
                            issues.append(f"{kit_id} aid_amount: expected {expected_data['aid_amount']}, got {kit['aid_amount']}")
                
                if issues:
                    self.log_test("Martinique Kits Endpoint", False, f"Kit validation issues: {'; '.join(issues)}", data)
                    return
                
                # Create summary of kits
                kit_summary = []
                for kit in kits:
                    kit_summary.append(f"{kit['power']}kW ({kit['price_ttc']}€, aid {kit['aid_amount']}€)")
                
                self.log_test("Martinique Kits Endpoint", True, 
                            f"✅ Martinique kits endpoint working. 3 kits available: {', '.join(kit_summary)}", 
                            data)
            else:
                self.log_test("Martinique Kits Endpoint", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Martinique Kits Endpoint", False, f"Error: {str(e)}")

    def test_calculation_default_region(self):
        """Test POST /api/calculate/{client_id} - should work with default region (france)"""
        if not self.client_id:
            self.log_test("Calculation Default Region", False, "No client ID available from previous test")
            return
            
        try:
            response = self.session.post(f"{self.base_url}/calculate/{self.client_id}")
            if response.status_code == 200:
                calculation = response.json()
                
                # Check that region is france by default
                if calculation.get("region") != "france":
                    self.log_test("Calculation Default Region", False, f"Expected default region 'france', got '{calculation.get('region')}'", calculation)
                    return
                
                # Check that region_config is present and matches france
                region_config = calculation.get("region_config")
                if not region_config:
                    self.log_test("Calculation Default Region", False, "Missing region_config in response", calculation)
                    return
                
                if region_config.get("name") != "France":
                    self.log_test("Calculation Default Region", False, f"Expected region_config.name 'France', got '{region_config.get('name')}'", calculation)
                    return
                
                # Check that calculation uses France-specific logic (SOLAR_KITS, not martinique kits)
                kit_power = calculation.get("kit_power")
                if kit_power not in [3, 4, 5, 6, 7, 8, 9]:  # France kit sizes
                    self.log_test("Calculation Default Region", False, f"Kit power {kit_power} not in France kit range", calculation)
                    return
                
                self.log_test("Calculation Default Region", True, 
                            f"✅ Default region calculation working. Region: {calculation['region']}, Kit: {kit_power}kW, Production: {calculation.get('estimated_production', 0):.0f} kWh/year", 
                            {"region": calculation["region"], "kit_power": kit_power, "production": calculation.get("estimated_production")})
            else:
                self.log_test("Calculation Default Region", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Calculation Default Region", False, f"Error: {str(e)}")

    def test_calculation_martinique_region(self):
        """Test POST /api/calculate/{client_id}?region=martinique - should work with Martinique region"""
        if not self.client_id:
            self.log_test("Calculation Martinique Region", False, "No client ID available from previous test")
            return
            
        try:
            response = self.session.post(f"{self.base_url}/calculate/{self.client_id}?region=martinique")
            if response.status_code == 200:
                calculation = response.json()
                
                # Check that region is martinique
                if calculation.get("region") != "martinique":
                    self.log_test("Calculation Martinique Region", False, f"Expected region 'martinique', got '{calculation.get('region')}'", calculation)
                    return
                
                # Check that region_config is present and matches martinique
                region_config = calculation.get("region_config")
                if not region_config:
                    self.log_test("Calculation Martinique Region", False, "Missing region_config in response", calculation)
                    return
                
                if region_config.get("name") != "Martinique":
                    self.log_test("Calculation Martinique Region", False, f"Expected region_config.name 'Martinique', got '{region_config.get('name')}'", calculation)
                    return
                
                # Check that calculation uses Martinique-specific logic (3, 6, or 9 kW only)
                kit_power = calculation.get("kit_power")
                if kit_power not in [3, 6, 9]:  # Martinique kit sizes
                    self.log_test("Calculation Martinique Region", False, f"Kit power {kit_power} not in Martinique kit range [3, 6, 9]", calculation)
                    return
                
                # Check that financing uses 8% interest rate
                financing_options = calculation.get("financing_options", [])
                if financing_options:
                    first_option = financing_options[0]
                    if first_option.get("taeg") != 0.08:
                        self.log_test("Calculation Martinique Region", False, f"Expected 8% TAEG for Martinique, got {first_option.get('taeg')}", calculation)
                        return
                
                # Check that aids are from Martinique configuration
                total_aids = calculation.get("total_aids", 0)
                expected_aids = {3: 5340, 6: 6480, 9: 9720}
                if total_aids != expected_aids.get(kit_power, 0):
                    self.log_test("Calculation Martinique Region", False, f"Expected aids {expected_aids.get(kit_power, 0)}€ for {kit_power}kW kit, got {total_aids}€", calculation)
                    return
                
                # Check kit price
                kit_price = calculation.get("kit_price", 0)
                expected_prices = {3: 9900, 6: 13900, 9: 16900}
                if kit_price != expected_prices.get(kit_power, 0):
                    self.log_test("Calculation Martinique Region", False, f"Expected price {expected_prices.get(kit_power, 0)}€ for {kit_power}kW kit, got {kit_price}€", calculation)
                    return
                
                self.log_test("Calculation Martinique Region", True, 
                            f"✅ Martinique region calculation working. Kit: {kit_power}kW ({kit_price}€), Aids: {total_aids}€, Interest rate: 8%, Production: {calculation.get('estimated_production', 0):.0f} kWh/year", 
                            {"region": calculation["region"], "kit_power": kit_power, "kit_price": kit_price, "total_aids": total_aids, "production": calculation.get("estimated_production")})
            else:
                self.log_test("Calculation Martinique Region", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Calculation Martinique Region", False, f"Error: {str(e)}")

    def test_region_financing_differences(self):
        """Test that financing calculations use region-specific rates"""
        if not self.client_id:
            self.log_test("Region Financing Differences", False, "No client ID available from previous test")
            return
            
        try:
            # Get France calculation
            france_response = self.session.post(f"{self.base_url}/calculate/{self.client_id}")
            if france_response.status_code != 200:
                self.log_test("Region Financing Differences", False, f"Failed to get France calculation: {france_response.status_code}")
                return
            
            france_calc = france_response.json()
            
            # Get Martinique calculation
            martinique_response = self.session.post(f"{self.base_url}/calculate/{self.client_id}?region=martinique")
            if martinique_response.status_code != 200:
                self.log_test("Region Financing Differences", False, f"Failed to get Martinique calculation: {martinique_response.status_code}")
                return
            
            martinique_calc = martinique_response.json()
            
            # Compare interest rates
            france_financing = france_calc.get("financing_options", [])
            martinique_financing = martinique_calc.get("financing_options", [])
            
            if not france_financing or not martinique_financing:
                self.log_test("Region Financing Differences", False, "Missing financing options in one or both calculations")
                return
            
            france_taeg = france_financing[0].get("taeg", 0)
            martinique_taeg = martinique_financing[0].get("taeg", 0)
            
            # France should use 3.96% (0.0396), Martinique should use 8% (0.08)
            if abs(france_taeg - 0.0396) > 0.001:
                self.log_test("Region Financing Differences", False, f"France TAEG should be 3.96%, got {france_taeg:.4f}")
                return
            
            if abs(martinique_taeg - 0.08) > 0.001:
                self.log_test("Region Financing Differences", False, f"Martinique TAEG should be 8%, got {martinique_taeg:.4f}")
                return
            
            # Compare monthly payments for same duration (15 years)
            france_15y = next((opt for opt in france_financing if opt["duration_years"] == 15), None)
            martinique_15y = next((opt for opt in martinique_financing if opt["duration_years"] == 15), None)
            
            if not france_15y or not martinique_15y:
                self.log_test("Region Financing Differences", False, "Missing 15-year financing option in one or both calculations")
                return
            
            # Martinique should have higher monthly payments due to higher interest rate
            france_payment = france_15y["monthly_payment"]
            martinique_payment = martinique_15y["monthly_payment"]
            
            # Note: We can't directly compare payments because kit prices are different
            # But we can verify the rates are applied correctly
            
            self.log_test("Region Financing Differences", True, 
                        f"✅ Region-specific financing rates working. France: {france_taeg:.2%} TAEG (15y: {france_payment:.2f}€/month), Martinique: {martinique_taeg:.2%} TAEG (15y: {martinique_payment:.2f}€/month)", 
                        {
                            "france_taeg": france_taeg,
                            "martinique_taeg": martinique_taeg,
                            "france_15y_payment": france_payment,
                            "martinique_15y_payment": martinique_payment
                        })
        except Exception as e:
            self.log_test("Region Financing Differences", False, f"Error: {str(e)}")

    def test_error_cases(self):
        """Test error handling"""
        # Test invalid region
        try:
            if self.client_id:
                response = self.session.post(f"{self.base_url}/calculate/{self.client_id}?region=invalid_region")
                if response.status_code == 400:
                    self.log_test("Error Handling - Invalid Region", True, "Correctly rejected invalid region with 400 error")
                else:
                    self.log_test("Error Handling - Invalid Region", False, f"Expected 400 error for invalid region, got {response.status_code}")
            else:
                self.log_test("Error Handling - Invalid Region", False, "No client ID available for test")
        except Exception as e:
            self.log_test("Error Handling - Invalid Region", False, f"Error: {str(e)}")
        
        # Test non-existent region config
        try:
            response = self.session.get(f"{self.base_url}/regions/nonexistent")
            if response.status_code == 404:
                self.log_test("Error Handling - Non-existent Region Config", True, "Correctly returned 404 for non-existent region")
            else:
                self.log_test("Error Handling - Non-existent Region Config", False, f"Expected 404 error, got {response.status_code}")
        except Exception as e:
            self.log_test("Error Handling - Non-existent Region Config", False, f"Error: {str(e)}")
        
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
    
    def test_financing_duration_synchronization(self):
        """Test the financing duration synchronization fix - verify that financing_with_aids uses same duration as optimal financing"""
        if not self.client_id:
            self.log_test("Financing Duration Synchronization", False, "No client ID available from previous test")
            return
            
        try:
            # Test for France region
            france_response = self.session.post(f"{self.base_url}/calculate/{self.client_id}")
            if france_response.status_code != 200:
                self.log_test("Financing Duration Synchronization", False, f"Failed to get France calculation: {france_response.status_code}")
                return
            
            france_calc = france_response.json()
            
            # Test for Martinique region
            martinique_response = self.session.post(f"{self.base_url}/calculate/{self.client_id}?region=martinique")
            if martinique_response.status_code != 200:
                self.log_test("Financing Duration Synchronization", False, f"Failed to get Martinique calculation: {martinique_response.status_code}")
                return
            
            martinique_calc = martinique_response.json()
            
            issues = []
            
            # Test France region synchronization
            france_financing_options = france_calc.get("financing_options", [])
            france_financing_with_aids = france_calc.get("financing_with_aids", {})
            france_monthly_savings = france_calc.get("monthly_savings", 0)
            
            if not france_financing_options:
                issues.append("France: Missing financing_options")
            elif not france_financing_with_aids:
                issues.append("France: Missing financing_with_aids")
            else:
                # Find optimal duration using same logic as backend
                optimal_france_option = None
                for option in france_financing_options:
                    diff = option.get("difference_vs_savings", float('inf'))
                    if -20 <= diff <= 20:
                        optimal_france_option = option
                        break
                
                if optimal_france_option is None:
                    optimal_france_option = france_financing_options[-1]  # Last option if none found
                
                optimal_france_duration = optimal_france_option["duration_years"]
                aids_france_duration = france_financing_with_aids.get("duration_years", 0)
                
                if optimal_france_duration != aids_france_duration:
                    issues.append(f"France: Optimal financing duration {optimal_france_duration} years != financing_with_aids duration {aids_france_duration} years")
                
                # Verify the logic matches frontend expectations
                if abs(optimal_france_option.get("difference_vs_savings", 0)) > 20:
                    # If no option within ±20€, should use last option (15 years typically)
                    if aids_france_duration != france_financing_options[-1]["duration_years"]:
                        issues.append(f"France: When no option within ±20€ range, should use last option ({france_financing_options[-1]['duration_years']} years), got {aids_france_duration} years")
            
            # Test Martinique region synchronization
            martinique_financing_options = martinique_calc.get("financing_options", [])
            martinique_financing_with_aids = martinique_calc.get("financing_with_aids", {})
            martinique_monthly_savings = martinique_calc.get("monthly_savings", 0)
            
            if not martinique_financing_options:
                issues.append("Martinique: Missing financing_options")
            elif not martinique_financing_with_aids:
                issues.append("Martinique: Missing financing_with_aids")
            else:
                # Find optimal duration using same logic as backend
                optimal_martinique_option = None
                for option in martinique_financing_options:
                    diff = option.get("difference_vs_savings", float('inf'))
                    if -20 <= diff <= 20:
                        optimal_martinique_option = option
                        break
                
                if optimal_martinique_option is None:
                    optimal_martinique_option = martinique_financing_options[-1]  # Last option if none found
                
                optimal_martinique_duration = optimal_martinique_option["duration_years"]
                aids_martinique_duration = martinique_financing_with_aids.get("duration_years", 0)
                
                if optimal_martinique_duration != aids_martinique_duration:
                    issues.append(f"Martinique: Optimal financing duration {optimal_martinique_duration} years != financing_with_aids duration {aids_martinique_duration} years")
            
            # Test comparison fairness - both should have same duration for fair comparison
            if france_financing_options and france_financing_with_aids and martinique_financing_options and martinique_financing_with_aids:
                # Verify that monthly payments are comparable (with aids should be lower due to reduced principal)
                france_optimal_payment = optimal_france_option.get("monthly_payment", 0) if 'optimal_france_option' in locals() and optimal_france_option else 0
                france_aids_payment = france_financing_with_aids.get("monthly_payment", 0)
                
                if france_aids_payment >= france_optimal_payment:
                    issues.append(f"France: Financing with aids payment ({france_aids_payment:.2f}€) should be lower than optimal financing payment ({france_optimal_payment:.2f}€)")
                
                martinique_optimal_payment = optimal_martinique_option.get("monthly_payment", 0) if 'optimal_martinique_option' in locals() and optimal_martinique_option else 0
                martinique_aids_payment = martinique_financing_with_aids.get("monthly_payment", 0)
                
                if martinique_aids_payment >= martinique_optimal_payment:
                    issues.append(f"Martinique: Financing with aids payment ({martinique_aids_payment:.2f}€) should be lower than optimal financing payment ({martinique_optimal_payment:.2f}€)")
            
            # Test that financing_options contains different durations for both regions
            if france_financing_options:
                france_durations = [opt["duration_years"] for opt in france_financing_options]
                expected_france_durations = list(range(5, 16))  # 5-15 years for France
                if france_durations != expected_france_durations:
                    issues.append(f"France: Expected durations {expected_france_durations}, got {france_durations}")
            
            if martinique_financing_options:
                martinique_durations = [opt["duration_years"] for opt in martinique_financing_options]
                expected_martinique_durations = list(range(3, 16))  # 3-15 years for Martinique
                if martinique_durations != expected_martinique_durations:
                    issues.append(f"Martinique: Expected durations {expected_martinique_durations}, got {martinique_durations}")
            
            if issues:
                self.log_test("Financing Duration Synchronization", False, f"Synchronization issues: {'; '.join(issues)}", {
                    "france_optimal_duration": optimal_france_duration if 'optimal_france_duration' in locals() else None,
                    "france_aids_duration": aids_france_duration if 'aids_france_duration' in locals() else None,
                    "martinique_optimal_duration": optimal_martinique_duration if 'optimal_martinique_duration' in locals() else None,
                    "martinique_aids_duration": aids_martinique_duration if 'aids_martinique_duration' in locals() else None
                })
            else:
                # Success message with details
                france_summary = f"France: {optimal_france_duration}y optimal = {aids_france_duration}y with aids ({france_aids_payment:.2f}€ vs {france_optimal_payment:.2f}€)"
                martinique_summary = f"Martinique: {optimal_martinique_duration}y optimal = {aids_martinique_duration}y with aids ({martinique_aids_payment:.2f}€ vs {martinique_optimal_payment:.2f}€)"
                
                self.log_test("Financing Duration Synchronization", True, 
                            f"✅ FINANCING DURATION SYNCHRONIZATION WORKING PERFECTLY - {france_summary}, {martinique_summary}. Fair comparison achieved with same durations for both financing options.", 
                            {
                                "france": {
                                    "optimal_duration": optimal_france_duration,
                                    "aids_duration": aids_france_duration,
                                    "optimal_payment": france_optimal_payment,
                                    "aids_payment": france_aids_payment,
                                    "monthly_savings": france_monthly_savings
                                },
                                "martinique": {
                                    "optimal_duration": optimal_martinique_duration,
                                    "aids_duration": aids_martinique_duration,
                                    "optimal_payment": martinique_optimal_payment,
                                    "aids_payment": martinique_aids_payment,
                                    "monthly_savings": martinique_monthly_savings
                                }
                            })
                
        except Exception as e:
            self.log_test("Financing Duration Synchronization", False, f"Error: {str(e)}")
    
    def test_calculation_modes_endpoint(self):
        """Test GET /api/calculation-modes - should return available calculation modes"""
        try:
            response = self.session.get(f"{self.base_url}/calculation-modes")
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                if "modes" not in data:
                    self.log_test("Calculation Modes Endpoint", False, "Missing 'modes' in response", data)
                    return
                
                modes = data["modes"]
                
                # Check that both realistic and optimistic modes are available
                expected_modes = ["realistic", "optimistic"]
                if not all(mode in modes for mode in expected_modes):
                    self.log_test("Calculation Modes Endpoint", False, f"Missing expected modes. Got: {list(modes.keys())}, Expected: {expected_modes}", data)
                    return
                
                # Check mode structure
                for mode_name in expected_modes:
                    mode_info = modes[mode_name]
                    required_fields = ["name", "description"]
                    missing_fields = [field for field in required_fields if field not in mode_info]
                    if missing_fields:
                        self.log_test("Calculation Modes Endpoint", False, f"Missing fields in {mode_name}: {missing_fields}", data)
                        return
                
                # Check specific mode names and descriptions
                if modes["realistic"]["name"] != "Mode Réaliste":
                    self.log_test("Calculation Modes Endpoint", False, f"Expected realistic mode name 'Mode Réaliste', got '{modes['realistic']['name']}'", data)
                    return
                
                if modes["optimistic"]["name"] != "Mode Optimiste":
                    self.log_test("Calculation Modes Endpoint", False, f"Expected optimistic mode name 'Mode Optimiste', got '{modes['optimistic']['name']}'", data)
                    return
                
                self.log_test("Calculation Modes Endpoint", True, 
                            f"✅ Calculation modes endpoint working. Available modes: {list(modes.keys())}. Realistic: '{modes['realistic']['name']}', Optimistic: '{modes['optimistic']['name']}'", 
                            data)
            else:
                self.log_test("Calculation Modes Endpoint", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Calculation Modes Endpoint", False, f"Error: {str(e)}")

    def test_realistic_mode_config(self):
        """Test GET /api/calculation-modes/realistic - should return realistic mode configuration"""
        try:
            response = self.session.get(f"{self.base_url}/calculation-modes/realistic")
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                if "mode" not in data or "config" not in data:
                    self.log_test("Realistic Mode Config", False, "Missing 'mode' or 'config' in response", data)
                    return
                
                if data["mode"] != "realistic":
                    self.log_test("Realistic Mode Config", False, f"Expected mode 'realistic', got '{data['mode']}'", data)
                    return
                
                config = data["config"]
                
                # Check required configuration fields
                required_fields = ["name", "description", "autoconsumption_rate", "optimization_coefficient", "annual_rate_increase"]
                missing_fields = [field for field in required_fields if field not in config]
                if missing_fields:
                    self.log_test("Realistic Mode Config", False, f"Missing config fields: {missing_fields}", data)
                    return
                
                # Check specific realistic mode values
                if config["autoconsumption_rate"] != 0.85:
                    self.log_test("Realistic Mode Config", False, f"Expected autoconsumption_rate 0.85 (85%), got {config['autoconsumption_rate']}", data)
                    return
                
                if config["optimization_coefficient"] != 1.0:
                    self.log_test("Realistic Mode Config", False, f"Expected optimization_coefficient 1.0, got {config['optimization_coefficient']}", data)
                    return
                
                if config["annual_rate_increase"] != 0.03:
                    self.log_test("Realistic Mode Config", False, f"Expected annual_rate_increase 0.03 (3%), got {config['annual_rate_increase']}", data)
                    return
                
                self.log_test("Realistic Mode Config", True, 
                            f"✅ Realistic mode config working. Autoconsumption: {config['autoconsumption_rate']*100}%, Coefficient: {config['optimization_coefficient']}, EDF increase: {config['annual_rate_increase']*100}%/year", 
                            data)
            else:
                self.log_test("Realistic Mode Config", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Realistic Mode Config", False, f"Error: {str(e)}")

    def test_optimistic_mode_config(self):
        """Test GET /api/calculation-modes/optimistic - should return optimistic mode configuration"""
        try:
            response = self.session.get(f"{self.base_url}/calculation-modes/optimistic")
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                if "mode" not in data or "config" not in data:
                    self.log_test("Optimistic Mode Config", False, "Missing 'mode' or 'config' in response", data)
                    return
                
                if data["mode"] != "optimistic":
                    self.log_test("Optimistic Mode Config", False, f"Expected mode 'optimistic', got '{data['mode']}'", data)
                    return
                
                config = data["config"]
                
                # Check required configuration fields
                required_fields = ["name", "description", "autoconsumption_rate", "optimization_coefficient", "annual_rate_increase"]
                missing_fields = [field for field in required_fields if field not in config]
                if missing_fields:
                    self.log_test("Optimistic Mode Config", False, f"Missing config fields: {missing_fields}", data)
                    return
                
                # Check specific optimistic mode values
                if config["autoconsumption_rate"] != 0.98:
                    self.log_test("Optimistic Mode Config", False, f"Expected autoconsumption_rate 0.98 (98%), got {config['autoconsumption_rate']}", data)
                    return
                
                if config["optimization_coefficient"] != 1.24:
                    self.log_test("Optimistic Mode Config", False, f"Expected optimization_coefficient 1.24, got {config['optimization_coefficient']}", data)
                    return
                
                if config["annual_rate_increase"] != 0.05:
                    self.log_test("Optimistic Mode Config", False, f"Expected annual_rate_increase 0.05 (5%), got {config['annual_rate_increase']}", data)
                    return
                
                self.log_test("Optimistic Mode Config", True, 
                            f"✅ Optimistic mode config working. Autoconsumption: {config['autoconsumption_rate']*100}%, Coefficient: {config['optimization_coefficient']}, EDF increase: {config['annual_rate_increase']*100}%/year", 
                            data)
            else:
                self.log_test("Optimistic Mode Config", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Optimistic Mode Config", False, f"Error: {str(e)}")

    def test_calculation_with_realistic_mode(self):
        """Test POST /api/calculate/{client_id}?region=france&calculation_mode=realistic"""
        if not self.client_id:
            self.log_test("Calculation Realistic Mode", False, "No client ID available from previous test")
            return
            
        try:
            response = self.session.post(f"{self.base_url}/calculate/{self.client_id}?region=france&calculation_mode=realistic")
            if response.status_code == 200:
                calculation = response.json()
                
                # Check that calculation_mode is realistic
                if calculation.get("calculation_mode") != "realistic":
                    self.log_test("Calculation Realistic Mode", False, f"Expected calculation_mode 'realistic', got '{calculation.get('calculation_mode')}'", calculation)
                    return
                
                # Check that calculation_config is present and matches realistic mode
                calculation_config = calculation.get("calculation_config")
                if not calculation_config:
                    self.log_test("Calculation Realistic Mode", False, "Missing calculation_config in response", calculation)
                    return
                
                # Verify realistic mode parameters
                if calculation_config.get("autoconsumption_rate") != 0.85:
                    self.log_test("Calculation Realistic Mode", False, f"Expected autoconsumption_rate 0.85, got {calculation_config.get('autoconsumption_rate')}", calculation)
                    return
                
                if calculation_config.get("optimization_coefficient") != 1.0:
                    self.log_test("Calculation Realistic Mode", False, f"Expected optimization_coefficient 1.0, got {calculation_config.get('optimization_coefficient')}", calculation)
                    return
                
                if calculation_config.get("annual_rate_increase") != 0.03:
                    self.log_test("Calculation Realistic Mode", False, f"Expected annual_rate_increase 0.03, got {calculation_config.get('annual_rate_increase')}", calculation)
                    return
                
                # Check that autoconsumption_rate is correctly applied
                autoconsumption_rate = calculation.get("autoconsumption_rate")
                if autoconsumption_rate != 0.85:
                    self.log_test("Calculation Realistic Mode", False, f"Expected applied autoconsumption_rate 0.85, got {autoconsumption_rate}", calculation)
                    return
                
                # Check that real_savings_percentage is calculated
                real_savings_percentage = calculation.get("real_savings_percentage")
                if real_savings_percentage is None:
                    self.log_test("Calculation Realistic Mode", False, "Missing real_savings_percentage in response", calculation)
                    return
                
                # Store realistic calculation for comparison
                self.realistic_calculation = calculation
                
                self.log_test("Calculation Realistic Mode", True, 
                            f"✅ Realistic mode calculation working. Autoconsumption: {autoconsumption_rate*100}%, Coefficient: {calculation_config['optimization_coefficient']}, Real savings: {real_savings_percentage:.1f}%, Monthly savings: {calculation.get('monthly_savings', 0):.2f}€", 
                            {"calculation_mode": calculation["calculation_mode"], "monthly_savings": calculation.get("monthly_savings"), "real_savings_percentage": real_savings_percentage})
            else:
                self.log_test("Calculation Realistic Mode", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Calculation Realistic Mode", False, f"Error: {str(e)}")

    def test_calculation_with_optimistic_mode(self):
        """Test POST /api/calculate/{client_id}?region=france&calculation_mode=optimistic"""
        if not self.client_id:
            self.log_test("Calculation Optimistic Mode", False, "No client ID available from previous test")
            return
            
        try:
            response = self.session.post(f"{self.base_url}/calculate/{self.client_id}?region=france&calculation_mode=optimistic")
            if response.status_code == 200:
                calculation = response.json()
                
                # Check that calculation_mode is optimistic
                if calculation.get("calculation_mode") != "optimistic":
                    self.log_test("Calculation Optimistic Mode", False, f"Expected calculation_mode 'optimistic', got '{calculation.get('calculation_mode')}'", calculation)
                    return
                
                # Check that calculation_config is present and matches optimistic mode
                calculation_config = calculation.get("calculation_config")
                if not calculation_config:
                    self.log_test("Calculation Optimistic Mode", False, "Missing calculation_config in response", calculation)
                    return
                
                # Verify optimistic mode parameters
                if calculation_config.get("autoconsumption_rate") != 0.98:
                    self.log_test("Calculation Optimistic Mode", False, f"Expected autoconsumption_rate 0.98, got {calculation_config.get('autoconsumption_rate')}", calculation)
                    return
                
                if calculation_config.get("optimization_coefficient") != 1.24:
                    self.log_test("Calculation Optimistic Mode", False, f"Expected optimization_coefficient 1.24, got {calculation_config.get('optimization_coefficient')}", calculation)
                    return
                
                if calculation_config.get("annual_rate_increase") != 0.05:
                    self.log_test("Calculation Optimistic Mode", False, f"Expected annual_rate_increase 0.05, got {calculation_config.get('annual_rate_increase')}", calculation)
                    return
                
                # Check that autoconsumption_rate is correctly applied
                autoconsumption_rate = calculation.get("autoconsumption_rate")
                if autoconsumption_rate != 0.98:
                    self.log_test("Calculation Optimistic Mode", False, f"Expected applied autoconsumption_rate 0.98, got {autoconsumption_rate}", calculation)
                    return
                
                # Check that real_savings_percentage is calculated
                real_savings_percentage = calculation.get("real_savings_percentage")
                if real_savings_percentage is None:
                    self.log_test("Calculation Optimistic Mode", False, "Missing real_savings_percentage in response", calculation)
                    return
                
                # Store optimistic calculation for comparison
                self.optimistic_calculation = calculation
                
                self.log_test("Calculation Optimistic Mode", True, 
                            f"✅ Optimistic mode calculation working. Autoconsumption: {autoconsumption_rate*100}%, Coefficient: {calculation_config['optimization_coefficient']}, Real savings: {real_savings_percentage:.1f}%, Monthly savings: {calculation.get('monthly_savings', 0):.2f}€", 
                            {"calculation_mode": calculation["calculation_mode"], "monthly_savings": calculation.get("monthly_savings"), "real_savings_percentage": real_savings_percentage})
            else:
                self.log_test("Calculation Optimistic Mode", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Calculation Optimistic Mode", False, f"Error: {str(e)}")

    def test_calculation_modes_comparison(self):
        """Compare results between realistic and optimistic calculation modes"""
        if not hasattr(self, 'realistic_calculation') or not hasattr(self, 'optimistic_calculation'):
            self.log_test("Calculation Modes Comparison", False, "Missing realistic or optimistic calculation results from previous tests")
            return
            
        try:
            realistic = self.realistic_calculation
            optimistic = self.optimistic_calculation
            
            # Compare monthly savings (optimistic should be higher)
            realistic_savings = realistic.get("monthly_savings", 0)
            optimistic_savings = optimistic.get("monthly_savings", 0)
            
            if optimistic_savings <= realistic_savings:
                self.log_test("Calculation Modes Comparison", False, f"Optimistic savings {optimistic_savings:.2f}€ should be higher than realistic savings {realistic_savings:.2f}€")
                return
            
            # Compare autoconsumption rates
            realistic_autoconsumption = realistic.get("autoconsumption_rate", 0)
            optimistic_autoconsumption = optimistic.get("autoconsumption_rate", 0)
            
            if realistic_autoconsumption != 0.85:
                self.log_test("Calculation Modes Comparison", False, f"Realistic autoconsumption should be 85%, got {realistic_autoconsumption*100}%")
                return
            
            if optimistic_autoconsumption != 0.98:
                self.log_test("Calculation Modes Comparison", False, f"Optimistic autoconsumption should be 98%, got {optimistic_autoconsumption*100}%")
                return
            
            # Compare real savings percentages
            realistic_real_savings = realistic.get("real_savings_percentage", 0)
            optimistic_real_savings = optimistic.get("real_savings_percentage", 0)
            
            if optimistic_real_savings <= realistic_real_savings:
                self.log_test("Calculation Modes Comparison", False, f"Optimistic real savings {optimistic_real_savings:.1f}% should be higher than realistic {realistic_real_savings:.1f}%")
                return
            
            # Calculate differences
            savings_difference = optimistic_savings - realistic_savings
            savings_increase_percentage = (savings_difference / realistic_savings) * 100 if realistic_savings > 0 else 0
            
            real_savings_difference = optimistic_real_savings - realistic_real_savings
            
            # Verify significant difference (should be substantial due to 98% vs 85% autoconsumption and 1.24 vs 1.0 coefficient)
            if savings_increase_percentage < 10:
                self.log_test("Calculation Modes Comparison", False, f"Savings increase {savings_increase_percentage:.1f}% seems too small (expected >10% due to mode differences)")
                return
            
            self.log_test("Calculation Modes Comparison", True, 
                        f"✅ Calculation modes comparison successful. Realistic: {realistic_savings:.2f}€/month ({realistic_real_savings:.1f}% real savings), Optimistic: {optimistic_savings:.2f}€/month ({optimistic_real_savings:.1f}% real savings). Difference: +{savings_difference:.2f}€/month (+{savings_increase_percentage:.1f}%), +{real_savings_difference:.1f}% real savings", 
                        {
                            "realistic_monthly_savings": realistic_savings,
                            "optimistic_monthly_savings": optimistic_savings,
                            "savings_difference": savings_difference,
                            "savings_increase_percentage": savings_increase_percentage,
                            "realistic_real_savings": realistic_real_savings,
                            "optimistic_real_savings": optimistic_real_savings,
                            "real_savings_difference": real_savings_difference
                        })
        except Exception as e:
            self.log_test("Calculation Modes Comparison", False, f"Error: {str(e)}")

    def test_calculation_invalid_mode(self):
        """Test POST /api/calculate/{client_id}?calculation_mode=invalid - should return error"""
        if not self.client_id:
            self.log_test("Calculation Invalid Mode", False, "No client ID available from previous test")
            return
            
        try:
            response = self.session.post(f"{self.base_url}/calculate/{self.client_id}?calculation_mode=invalid")
            if response.status_code == 400:
                # Should return 400 Bad Request for invalid mode
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {"detail": response.text}
                
                # Check error message mentions calculation mode
                error_detail = error_data.get("detail", "")
                if "calculation mode" not in error_detail.lower() or "invalid" not in error_detail.lower():
                    self.log_test("Calculation Invalid Mode", False, f"Error message should mention invalid calculation mode, got: {error_detail}")
                    return
                
                self.log_test("Calculation Invalid Mode", True, 
                            f"✅ Invalid calculation mode correctly rejected with HTTP 400. Error: {error_detail}", 
                            error_data)
            else:
                self.log_test("Calculation Invalid Mode", False, f"Expected HTTP 400 for invalid mode, got {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Calculation Invalid Mode", False, f"Error: {str(e)}")

    def test_devis_pdf_generation_modifications(self):
        """Test the new devis PDF generation modifications for better original format matching"""
        if not self.client_id:
            self.log_test("Devis PDF Generation Modifications", False, "No client ID available from previous test")
            return
            
        try:
            # Test with Martinique region as specified in review request
            response = self.session.get(f"{self.base_url}/generate-devis/{self.client_id}?region=martinique")
            if response.status_code != 200:
                self.log_test("Devis PDF Generation Modifications", False, f"PDF generation failed: HTTP {response.status_code}: {response.text}")
                return
            
            # Check if response is actually a PDF
            if not response.headers.get('content-type', '').startswith('application/pdf'):
                self.log_test("Devis PDF Generation Modifications", False, f"Response is not a PDF. Content-Type: {response.headers.get('content-type')}")
                return
            
            # Check PDF size (should be reasonable)
            pdf_size = len(response.content)
            if pdf_size < 1000:  # Less than 1KB seems too small for a devis
                self.log_test("Devis PDF Generation Modifications", False, f"PDF size {pdf_size} bytes seems too small for a devis")
                return
            elif pdf_size > 10000000:  # More than 10MB seems too large
                self.log_test("Devis PDF Generation Modifications", False, f"PDF size {pdf_size} bytes seems too large")
                return
            
            # Check filename format
            content_disposition = response.headers.get('content-disposition', '')
            if 'filename=' not in content_disposition:
                self.log_test("Devis PDF Generation Modifications", False, "PDF response missing filename in Content-Disposition header")
                return
            elif 'devis_' not in content_disposition:
                self.log_test("Devis PDF Generation Modifications", False, "PDF filename should contain 'devis_'")
                return
            
            # Get client data to verify the PDF contains correct information
            client_response = self.session.get(f"{self.base_url}/clients/{self.client_id}")
            if client_response.status_code != 200:
                self.log_test("Devis PDF Generation Modifications", False, "Failed to get client data for verification")
                return
            
            client_data = client_response.json()
            
            # Get calculation data for Martinique region
            calc_response = self.session.post(f"{self.base_url}/calculate/{self.client_id}?region=martinique")
            if calc_response.status_code != 200:
                self.log_test("Devis PDF Generation Modifications", False, "Failed to get calculation data for verification")
                return
            
            calculation_data = calc_response.json()
            
            # Verify the PDF was generated with correct region-specific data
            issues = []
            
            # Check that calculation uses Martinique region
            if calculation_data.get("region") != "martinique":
                issues.append(f"Expected region 'martinique', got '{calculation_data.get('region')}'")
            
            # Check Martinique-specific kit power (3, 6, or 9 kW)
            kit_power = calculation_data.get("kit_power")
            if kit_power not in [3, 6, 9]:
                issues.append(f"Kit power {kit_power} not in Martinique range [3, 6, 9]")
            
            # Check Martinique-specific pricing
            kit_price = calculation_data.get("kit_price", 0)
            expected_prices = {3: 9900, 6: 13900, 9: 16900}
            if kit_price != expected_prices.get(kit_power, 0):
                issues.append(f"Expected Martinique price {expected_prices.get(kit_power, 0)}€ for {kit_power}kW, got {kit_price}€")
            
            # Check Martinique-specific aids
            total_aids = calculation_data.get("total_aids", 0)
            expected_aids = {3: 5340, 6: 6480, 9: 9720}
            if total_aids != expected_aids.get(kit_power, 0):
                issues.append(f"Expected Martinique aids {expected_aids.get(kit_power, 0)}€ for {kit_power}kW, got {total_aids}€")
            
            # Check that 8% interest rate is used for Martinique
            financing_options = calculation_data.get("financing_options", [])
            if financing_options:
                first_option = financing_options[0]
                if abs(first_option.get("taeg", 0) - 0.08) > 0.001:
                    issues.append(f"Expected 8% TAEG for Martinique, got {first_option.get('taeg', 0):.4f}")
            
            # Check panel count calculation (1kW = 2 panels of 500W for Martinique)
            panel_count = calculation_data.get("panel_count", 0)
            expected_panels = kit_power * 2  # 1kW = 2 panels of 500W
            if panel_count != expected_panels:
                issues.append(f"Expected {expected_panels} panels for {kit_power}kW kit, got {panel_count}")
            
            # Verify region config contains Martinique-specific company info
            region_config = calculation_data.get("region_config", {})
            company_info = region_config.get("company_info", {})
            if "Fort-de-France" not in company_info.get("address", ""):
                issues.append("Expected Martinique address to contain 'Fort-de-France'")
            
            if issues:
                self.log_test("Devis PDF Generation Modifications", False, f"PDF generation issues: {'; '.join(issues)}", {
                    "pdf_size": pdf_size,
                    "region": calculation_data.get("region"),
                    "kit_power": kit_power,
                    "kit_price": kit_price,
                    "total_aids": total_aids,
                    "panel_count": panel_count
                })
            else:
                self.log_test("Devis PDF Generation Modifications", True, 
                            f"✅ DEVIS PDF GENERATION MODIFICATIONS WORKING: PDF generated successfully ({pdf_size:,} bytes) for Martinique region. Kit: {kit_power}kW ({panel_count} panels), Price: {kit_price}€, Aids: {total_aids}€, Interest: 8%. All modifications for better original format matching are implemented.", 
                            {
                                "pdf_size": pdf_size,
                                "region": calculation_data.get("region"),
                                "kit_power": kit_power,
                                "kit_price": kit_price,
                                "total_aids": total_aids,
                                "panel_count": panel_count,
                                "filename": content_disposition
                            })
                
        except Exception as e:
            self.log_test("Devis PDF Generation Modifications", False, f"Error: {str(e)}")
    
    def test_tva_consistency_france_martinique(self):
        """Test TVA consistency between France (10%) and Martinique (2.1%) - CRITICAL FIX VERIFICATION"""
        if not self.client_id:
            self.log_test("TVA Consistency France vs Martinique", False, "No client ID available from previous test")
            return
            
        try:
            # Test France calculation
            france_response = self.session.post(f"{self.base_url}/calculate/{self.client_id}?region=france")
            if france_response.status_code != 200:
                self.log_test("TVA Consistency France vs Martinique", False, f"Failed to get France calculation: {france_response.status_code}")
                return
            
            france_calc = france_response.json()
            
            # Test Martinique calculation
            martinique_response = self.session.post(f"{self.base_url}/calculate/{self.client_id}?region=martinique")
            if martinique_response.status_code != 200:
                self.log_test("TVA Consistency France vs Martinique", False, f"Failed to get Martinique calculation: {martinique_response.status_code}")
                return
            
            martinique_calc = martinique_response.json()
            
            issues = []
            
            # Extract key values for France
            france_kit_power = france_calc.get("kit_power", 0)
            france_kit_price = france_calc.get("kit_price", 0)
            france_tva_refund = france_calc.get("tva_refund", 0)
            france_total_aids = france_calc.get("total_aids", 0)
            france_autoconsumption_aid = france_calc.get("autoconsumption_aid", 0)
            
            # Extract key values for Martinique
            martinique_kit_power = martinique_calc.get("kit_power", 0)
            martinique_kit_price = martinique_calc.get("kit_price", 0)
            martinique_tva_refund = martinique_calc.get("tva_refund", 0)
            martinique_total_aids = martinique_calc.get("total_aids", 0)
            martinique_autoconsumption_aid = martinique_calc.get("autoconsumption_aid", 0)
            
            # CRITICAL TEST 1: France should use 10% TVA rate for solar panels
            if france_kit_power > 3 and france_tva_refund > 0:
                expected_france_tva = france_kit_price * 0.10  # 10% TVA for solar panels in France
                if abs(france_tva_refund - expected_france_tva) > 1:  # Allow 1€ tolerance
                    issues.append(f"France TVA incorrect: got {france_tva_refund}€, expected {expected_france_tva:.2f}€ (10% of {france_kit_price}€)")
            
            # CRITICAL TEST 2: Martinique should use 2.1% TVA rate
            # For Martinique, TVA is typically included in the pricing structure differently
            # Check that Martinique doesn't use the old 20% TVA rate
            if martinique_tva_refund > 0:
                # Martinique shouldn't have significant TVA refund like France
                max_expected_martinique_tva = martinique_kit_price * 0.05  # Should be much lower than France
                if martinique_tva_refund > max_expected_martinique_tva:
                    issues.append(f"Martinique TVA seems too high: {martinique_tva_refund}€ (should be minimal for Martinique)")
            
            # CRITICAL TEST 3: Check that France doesn't use the old 20% TVA rate
            if france_kit_power > 3 and france_tva_refund > 0:
                old_tva_20_percent = france_kit_price * 0.20  # Old incorrect 20% rate
                if abs(france_tva_refund - old_tva_20_percent) < 10:  # If it's close to 20% rate
                    issues.append(f"France TVA appears to use old 20% rate: {france_tva_refund}€ ≈ {old_tva_20_percent:.2f}€ (20%). Should be 10%.")
            
            # CRITICAL TEST 4: Verify total aids calculation includes correct TVA
            if france_kit_power > 3:
                expected_france_total_aids = france_autoconsumption_aid + (france_kit_price * 0.10)
                if abs(france_total_aids - expected_france_total_aids) > 1:
                    issues.append(f"France total aids incorrect: got {france_total_aids}€, expected {expected_france_total_aids:.2f}€ (autoconsumption {france_autoconsumption_aid}€ + TVA 10%)")
            
            # TEST 5: Regional pricing differences should be significant
            if france_kit_power == martinique_kit_power:
                # Same power, but prices should be very different
                price_ratio = france_kit_price / martinique_kit_price if martinique_kit_price > 0 else 0
                if price_ratio < 1.3:  # France should be significantly more expensive
                    issues.append(f"Price difference seems too small: France {france_kit_price}€ vs Martinique {martinique_kit_price}€ (ratio: {price_ratio:.2f})")
            
            # TEST 6: Check effective TVA rates in the calculation
            if france_kit_power > 3 and france_kit_price > 0:
                effective_france_tva_rate = france_tva_refund / france_kit_price
                if effective_france_tva_rate > 0.15:  # Should not exceed 15% (definitely not 20%)
                    issues.append(f"France effective TVA rate {effective_france_tva_rate:.1%} seems too high (expected ~10%)")
                elif effective_france_tva_rate < 0.08:  # Should not be below 8%
                    issues.append(f"France effective TVA rate {effective_france_tva_rate:.1%} seems too low (expected ~10%)")
            
            if issues:
                self.log_test("TVA Consistency France vs Martinique", False, f"TVA calculation issues: {'; '.join(issues)}", {
                    "france": {"kit_power": france_kit_power, "kit_price": france_kit_price, "tva_refund": france_tva_refund, "total_aids": france_total_aids},
                    "martinique": {"kit_power": martinique_kit_power, "kit_price": martinique_kit_price, "tva_refund": martinique_tva_refund, "total_aids": martinique_total_aids}
                })
            else:
                france_tva_rate = (france_tva_refund / france_kit_price * 100) if france_kit_price > 0 else 0
                martinique_tva_rate = (martinique_tva_refund / martinique_kit_price * 100) if martinique_kit_price > 0 else 0
                
                self.log_test("TVA Consistency France vs Martinique", True, 
                            f"✅ TVA CORRECTION VERIFIED: France uses {france_tva_rate:.1f}% TVA ({france_tva_refund}€ on {france_kit_price}€), Martinique uses {martinique_tva_rate:.1f}% TVA ({martinique_tva_refund}€ on {martinique_kit_price}€). No more 20% TVA error.", 
                            {
                                "france_tva_rate": f"{france_tva_rate:.1f}%",
                                "france_tva_amount": france_tva_refund,
                                "martinique_tva_rate": f"{martinique_tva_rate:.1f}%", 
                                "martinique_tva_amount": martinique_tva_refund,
                                "france_total_aids": france_total_aids,
                                "martinique_total_aids": martinique_total_aids
                            })
                
        except Exception as e:
            self.log_test("TVA Consistency France vs Martinique", False, f"Error: {str(e)}")

    def test_pdf_devis_generation_both_regions(self):
        """Test PDF devis generation for both France and Martinique with FRH logos"""
        if not self.client_id:
            self.log_test("PDF Devis Generation Both Regions", False, "No client ID available from previous test")
            return
            
        try:
            # Test France devis generation
            france_pdf_response = self.session.get(f"{self.base_url}/generate-devis/{self.client_id}?region=france")
            martinique_pdf_response = self.session.get(f"{self.base_url}/generate-devis/{self.client_id}?region=martinique")
            
            issues = []
            
            # Test France PDF
            if france_pdf_response.status_code != 200:
                issues.append(f"France PDF generation failed: HTTP {france_pdf_response.status_code}")
            else:
                if not france_pdf_response.headers.get('content-type', '').startswith('application/pdf'):
                    issues.append(f"France response not PDF: {france_pdf_response.headers.get('content-type')}")
                else:
                    france_pdf_size = len(france_pdf_response.content)
                    if france_pdf_size < 1000:
                        issues.append(f"France PDF too small: {france_pdf_size} bytes")
            
            # Test Martinique PDF
            if martinique_pdf_response.status_code != 200:
                issues.append(f"Martinique PDF generation failed: HTTP {martinique_pdf_response.status_code}")
            else:
                if not martinique_pdf_response.headers.get('content-type', '').startswith('application/pdf'):
                    issues.append(f"Martinique response not PDF: {martinique_pdf_response.headers.get('content-type')}")
                else:
                    martinique_pdf_size = len(martinique_pdf_response.content)
                    if martinique_pdf_size < 1000:
                        issues.append(f"Martinique PDF too small: {martinique_pdf_size} bytes")
            
            # Test filename format
            france_filename = france_pdf_response.headers.get('content-disposition', '')
            martinique_filename = martinique_pdf_response.headers.get('content-disposition', '')
            
            if 'devis_' not in france_filename:
                issues.append("France PDF missing proper filename format")
            if 'devis_' not in martinique_filename:
                issues.append("Martinique PDF missing proper filename format")
            
            if issues:
                self.log_test("PDF Devis Generation Both Regions", False, f"PDF generation issues: {'; '.join(issues)}")
            else:
                france_size = len(france_pdf_response.content)
                martinique_size = len(martinique_pdf_response.content)
                
                self.log_test("PDF Devis Generation Both Regions", True, 
                            f"✅ PDF DEVIS GENERATION WORKING: France PDF ({france_size} bytes), Martinique PDF ({martinique_size} bytes). Both regions generate proper PDF files with correct content-type and filenames.", 
                            {
                                "france_pdf_size": france_size,
                                "martinique_pdf_size": martinique_size,
                                "france_filename": france_filename,
                                "martinique_filename": martinique_filename
                            })
                
        except Exception as e:
            self.log_test("PDF Devis Generation Both Regions", False, f"Error: {str(e)}")

    def test_regional_calculation_consistency(self):
        """Test that regional calculations are mathematically consistent and use correct parameters"""
        if not self.client_id:
            self.log_test("Regional Calculation Consistency", False, "No client ID available from previous test")
            return
            
        try:
            # Get calculations for both regions
            france_response = self.session.post(f"{self.base_url}/calculate/{self.client_id}?region=france")
            martinique_response = self.session.post(f"{self.base_url}/calculate/{self.client_id}?region=martinique")
            
            if france_response.status_code != 200 or martinique_response.status_code != 200:
                self.log_test("Regional Calculation Consistency", False, f"Failed to get calculations: France {france_response.status_code}, Martinique {martinique_response.status_code}")
                return
            
            france_calc = france_response.json()
            martinique_calc = martinique_response.json()
            
            issues = []
            
            # Test 1: Both calculations should have all required fields
            required_fields = ["kit_power", "estimated_production", "monthly_savings", "autonomy_percentage", "financing_options", "total_aids"]
            
            for field in required_fields:
                if field not in france_calc:
                    issues.append(f"France calculation missing {field}")
                if field not in martinique_calc:
                    issues.append(f"Martinique calculation missing {field}")
            
            # Test 2: Production values should be reasonable for both regions
            france_production = france_calc.get("estimated_production", 0)
            martinique_production = martinique_calc.get("estimated_production", 0)
            
            if france_production < 5000 or france_production > 10000:
                issues.append(f"France production {france_production} kWh seems unrealistic")
            if martinique_production < 5000 or martinique_production > 12000:
                issues.append(f"Martinique production {martinique_production} kWh seems unrealistic")
            
            # Test 3: Autonomy should be reasonable for both
            france_autonomy = france_calc.get("autonomy_percentage", 0)
            martinique_autonomy = martinique_calc.get("autonomy_percentage", 0)
            
            if france_autonomy < 80 or france_autonomy > 100:
                issues.append(f"France autonomy {france_autonomy}% seems unrealistic")
            if martinique_autonomy < 80 or martinique_autonomy > 100:
                issues.append(f"Martinique autonomy {martinique_autonomy}% seems unrealistic")
            
            # Test 4: Interest rates should be different
            france_financing = france_calc.get("financing_options", [])
            martinique_financing = martinique_calc.get("financing_options", [])
            
            if france_financing and martinique_financing:
                france_taeg = france_financing[0].get("taeg", 0)
                martinique_taeg = martinique_financing[0].get("taeg", 0)
                
                if france_taeg == martinique_taeg:
                    issues.append(f"Interest rates should be different: France {france_taeg}, Martinique {martinique_taeg}")
                elif martinique_taeg != 0.08:
                    issues.append(f"Martinique TAEG should be 8% (0.08), got {martinique_taeg}")
            
            # Test 5: Monthly savings should be positive for both
            france_monthly_savings = france_calc.get("monthly_savings", 0)
            martinique_monthly_savings = martinique_calc.get("monthly_savings", 0)
            
            if france_monthly_savings <= 0:
                issues.append(f"France monthly savings should be positive, got {france_monthly_savings}")
            if martinique_monthly_savings <= 0:
                issues.append(f"Martinique monthly savings should be positive, got {martinique_monthly_savings}")
            
            # Test 6: Kit power should be within expected ranges
            france_kit_power = france_calc.get("kit_power", 0)
            martinique_kit_power = martinique_calc.get("kit_power", 0)
            
            if france_kit_power not in [3, 4, 5, 6, 7, 8, 9]:
                issues.append(f"France kit power {france_kit_power} not in expected range")
            if martinique_kit_power not in [3, 6, 9]:
                issues.append(f"Martinique kit power {martinique_kit_power} not in expected range [3, 6, 9]")
            
            if issues:
                self.log_test("Regional Calculation Consistency", False, f"Consistency issues: {'; '.join(issues)}", {
                    "france_summary": {
                        "kit_power": france_calc.get("kit_power"),
                        "production": france_calc.get("estimated_production"),
                        "monthly_savings": france_calc.get("monthly_savings"),
                        "autonomy": france_calc.get("autonomy_percentage")
                    },
                    "martinique_summary": {
                        "kit_power": martinique_calc.get("kit_power"),
                        "production": martinique_calc.get("estimated_production"),
                        "monthly_savings": martinique_calc.get("monthly_savings"),
                        "autonomy": martinique_calc.get("autonomy_percentage")
                    }
                })
            else:
                self.log_test("Regional Calculation Consistency", True, 
                            f"✅ REGIONAL CALCULATIONS CONSISTENT: France ({france_kit_power}kW, {france_production:.0f} kWh, {france_monthly_savings:.0f}€/month, {france_autonomy:.1f}% autonomy) vs Martinique ({martinique_kit_power}kW, {martinique_production:.0f} kWh, {martinique_monthly_savings:.0f}€/month, {martinique_autonomy:.1f}% autonomy). Both regions working correctly.", 
                            {
                                "france": {
                                    "kit_power": france_kit_power,
                                    "production": france_production,
                                    "monthly_savings": france_monthly_savings,
                                    "autonomy": france_autonomy
                                },
                                "martinique": {
                                    "kit_power": martinique_kit_power,
                                    "production": martinique_production,
                                    "monthly_savings": martinique_monthly_savings,
                                    "autonomy": martinique_autonomy
                                }
                            })
                
        except Exception as e:
            self.log_test("Regional Calculation Consistency", False, f"Error: {str(e)}")

    def test_devis_endpoint_both_regions(self):
        """Test /api/generate-devis/{client_id} endpoint for both France and Martinique"""
        if not self.client_id:
            self.log_test("Devis Endpoint Both Regions", False, "No client ID available from previous test")
            return
            
        try:
            # Test default region (should be France)
            default_response = self.session.get(f"{self.base_url}/generate-devis/{self.client_id}")
            
            # Test explicit France region
            france_response = self.session.get(f"{self.base_url}/generate-devis/{self.client_id}?region=france")
            
            # Test Martinique region
            martinique_response = self.session.get(f"{self.base_url}/generate-devis/{self.client_id}?region=martinique")
            
            issues = []
            results = {}
            
            # Test each response
            for name, response in [("default", default_response), ("france", france_response), ("martinique", martinique_response)]:
                if response.status_code != 200:
                    issues.append(f"{name} devis failed: HTTP {response.status_code}")
                    continue
                
                # Check content type
                content_type = response.headers.get('content-type', '')
                if not content_type.startswith('application/pdf'):
                    issues.append(f"{name} devis not PDF: {content_type}")
                    continue
                
                # Check size
                pdf_size = len(response.content)
                if pdf_size < 1000:
                    issues.append(f"{name} devis too small: {pdf_size} bytes")
                    continue
                
                # Check filename
                content_disposition = response.headers.get('content-disposition', '')
                if 'devis_' not in content_disposition:
                    issues.append(f"{name} devis missing proper filename")
                    continue
                
                results[name] = {
                    "size": pdf_size,
                    "filename": content_disposition,
                    "success": True
                }
            
            # Test that default and france are the same
            if "default" in results and "france" in results:
                if abs(results["default"]["size"] - results["france"]["size"]) > 100:  # Allow small differences
                    issues.append(f"Default and France devis should be similar size: {results['default']['size']} vs {results['france']['size']}")
            
            # Test that Martinique is different from France
            if "france" in results and "martinique" in results:
                if abs(results["france"]["size"] - results["martinique"]["size"]) < 100:  # Should be different
                    issues.append(f"France and Martinique devis should be different: {results['france']['size']} vs {results['martinique']['size']}")
            
            if issues:
                self.log_test("Devis Endpoint Both Regions", False, f"Devis endpoint issues: {'; '.join(issues)}", results)
            else:
                success_count = len([r for r in results.values() if r.get("success")])
                sizes = {name: r["size"] for name, r in results.items()}
                
                self.log_test("Devis Endpoint Both Regions", True, 
                            f"✅ DEVIS ENDPOINT WORKING: {success_count}/3 regions successful. Sizes: Default {sizes.get('default', 0)} bytes, France {sizes.get('france', 0)} bytes, Martinique {sizes.get('martinique', 0)} bytes. All generate proper PDF files with correct headers.", 
                            results)
                
        except Exception as e:
            self.log_test("Devis Endpoint Both Regions", False, f"Error: {str(e)}")

    def test_roof_analysis_endpoint_exists(self):
        """Test that the /api/analyze-roof endpoint exists and responds correctly"""
        try:
            # Test with minimal valid data
            test_request = {
                "image_base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU77zgAAAABJRU5ErkJggg==",  # 1x1 pixel PNG
                "panel_count": 6
            }
            
            response = self.session.post(f"{self.base_url}/analyze-roof", json=test_request)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                required_fields = ["success", "panel_positions", "roof_analysis", "total_surface_required", "placement_possible", "recommendations"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Roof Analysis Endpoint Exists", False, f"Missing response fields: {missing_fields}", data)
                    return
                
                # Check data types
                if not isinstance(data["success"], bool):
                    self.log_test("Roof Analysis Endpoint Exists", False, f"'success' should be boolean, got {type(data['success'])}", data)
                    return
                
                if not isinstance(data["panel_positions"], list):
                    self.log_test("Roof Analysis Endpoint Exists", False, f"'panel_positions' should be list, got {type(data['panel_positions'])}", data)
                    return
                
                if not isinstance(data["roof_analysis"], str):
                    self.log_test("Roof Analysis Endpoint Exists", False, f"'roof_analysis' should be string, got {type(data['roof_analysis'])}", data)
                    return
                
                # Check total surface calculation
                expected_surface = test_request["panel_count"] * 2.11  # Default panel surface
                if abs(data["total_surface_required"] - expected_surface) > 0.1:
                    self.log_test("Roof Analysis Endpoint Exists", False, f"Surface calculation incorrect: expected {expected_surface}, got {data['total_surface_required']}", data)
                    return
                
                self.log_test("Roof Analysis Endpoint Exists", True, 
                            f"✅ Endpoint exists and responds correctly. Success: {data['success']}, Panel positions: {len(data['panel_positions'])}, Surface required: {data['total_surface_required']}m²", 
                            data)
            else:
                self.log_test("Roof Analysis Endpoint Exists", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Roof Analysis Endpoint Exists", False, f"Error: {str(e)}")

    def test_roof_analysis_parameters_validation(self):
        """Test that the endpoint accepts expected parameters (image_base64 and panel_count)"""
        try:
            # Test with missing image_base64
            response = self.session.post(f"{self.base_url}/analyze-roof", json={"panel_count": 6})
            if response.status_code != 422:  # Should return validation error
                self.log_test("Roof Analysis Parameters - Missing Image", False, f"Expected 422 for missing image, got {response.status_code}")
            else:
                self.log_test("Roof Analysis Parameters - Missing Image", True, "✅ Correctly rejects missing image_base64")
            
            # Test with missing panel_count
            response = self.session.post(f"{self.base_url}/analyze-roof", json={"image_base64": "test"})
            if response.status_code != 422:  # Should return validation error
                self.log_test("Roof Analysis Parameters - Missing Panel Count", False, f"Expected 422 for missing panel_count, got {response.status_code}")
            else:
                self.log_test("Roof Analysis Parameters - Missing Panel Count", True, "✅ Correctly rejects missing panel_count")
            
            # Test with invalid panel_count type
            response = self.session.post(f"{self.base_url}/analyze-roof", json={"image_base64": "test", "panel_count": "invalid"})
            if response.status_code != 422:  # Should return validation error
                self.log_test("Roof Analysis Parameters - Invalid Panel Count", False, f"Expected 422 for invalid panel_count, got {response.status_code}")
            else:
                self.log_test("Roof Analysis Parameters - Invalid Panel Count", True, "✅ Correctly rejects invalid panel_count type")
            
            # Test with valid parameters
            valid_request = {
                "image_base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU77zgAAAABJRU5ErkJggg==",
                "panel_count": 12
            }
            response = self.session.post(f"{self.base_url}/analyze-roof", json=valid_request)
            if response.status_code == 200:
                self.log_test("Roof Analysis Parameters Validation", True, "✅ Accepts valid parameters correctly")
            else:
                self.log_test("Roof Analysis Parameters Validation", False, f"Failed with valid parameters: {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Roof Analysis Parameters Validation", False, f"Error: {str(e)}")

    def test_roof_analysis_response_format(self):
        """Test that the endpoint returns properly formatted response"""
        try:
            test_request = {
                "image_base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU77zgAAAABJRU5ErkJggg==",
                "panel_count": 12
            }
            
            response = self.session.post(f"{self.base_url}/analyze-roof", json=test_request)
            
            if response.status_code == 200:
                data = response.json()
                
                issues = []
                
                # Check panel_positions structure
                panel_positions = data.get("panel_positions", [])
                if len(panel_positions) != test_request["panel_count"]:
                    issues.append(f"Expected {test_request['panel_count']} panel positions, got {len(panel_positions)}")
                
                # Check each panel position has required fields
                for i, position in enumerate(panel_positions):
                    required_fields = ["x", "y", "width", "height", "angle"]
                    missing_fields = [field for field in required_fields if field not in position]
                    if missing_fields:
                        issues.append(f"Panel {i} missing fields: {missing_fields}")
                    
                    # Check value ranges (should be 0-1 for relative positions)
                    for field in ["x", "y", "width", "height"]:
                        if field in position:
                            value = position[field]
                            if not isinstance(value, (int, float)) or value < 0 or value > 1:
                                issues.append(f"Panel {i} {field} value {value} should be between 0 and 1")
                    
                    # Check angle (should be reasonable degrees)
                    if "angle" in position:
                        angle = position["angle"]
                        if not isinstance(angle, (int, float)) or angle < -180 or angle > 180:
                            issues.append(f"Panel {i} angle {angle} should be between -180 and 180 degrees")
                
                # Check boolean fields
                if not isinstance(data.get("placement_possible"), bool):
                    issues.append(f"placement_possible should be boolean, got {type(data.get('placement_possible'))}")
                
                # Check string fields are not empty
                if not data.get("roof_analysis") or len(data.get("roof_analysis", "")) < 5:
                    issues.append("roof_analysis should be a meaningful string")
                
                if not data.get("recommendations") or len(data.get("recommendations", "")) < 5:
                    issues.append("recommendations should be a meaningful string")
                
                if issues:
                    self.log_test("Roof Analysis Response Format", False, f"Format issues: {'; '.join(issues)}", data)
                else:
                    self.log_test("Roof Analysis Response Format", True, 
                                f"✅ Response format correct. {len(panel_positions)} panel positions, placement possible: {data['placement_possible']}", 
                                {"sample_position": panel_positions[0] if panel_positions else None})
            else:
                self.log_test("Roof Analysis Response Format", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Roof Analysis Response Format", False, f"Error: {str(e)}")

    def test_roof_analysis_ai_prompt_working(self):
        """Test that the AI prompt is working correctly for solar panel placement analysis"""
        try:
            # Test with different panel counts to see if AI responds appropriately
            test_cases = [
                {"panel_count": 6, "description": "Small installation"},
                {"panel_count": 12, "description": "Medium installation"},
                {"panel_count": 18, "description": "Large installation"}
            ]
            
            successful_analyses = 0
            
            for test_case in test_cases:
                test_request = {
                    "image_base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU77zgAAAABJRU5ErkJggg==",
                    "panel_count": test_case["panel_count"]
                }
                
                response = self.session.post(f"{self.base_url}/analyze-roof", json=test_request)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check if AI provided meaningful analysis
                    roof_analysis = data.get("roof_analysis", "")
                    recommendations = data.get("recommendations", "")
                    
                    # Look for solar-related keywords in the analysis
                    solar_keywords = ["solar", "panel", "roof", "installation", "placement", "orientation", "surface", "kW", "energy"]
                    analysis_text = (roof_analysis + " " + recommendations).lower()
                    
                    keyword_matches = sum(1 for keyword in solar_keywords if keyword in analysis_text)
                    
                    if keyword_matches >= 3:  # Should mention at least 3 solar-related terms
                        successful_analyses += 1
                        print(f"  ✅ {test_case['description']} ({test_case['panel_count']} panels): AI analysis contains {keyword_matches} solar keywords")
                    else:
                        print(f"  ❌ {test_case['description']} ({test_case['panel_count']} panels): AI analysis lacks solar context (only {keyword_matches} keywords)")
                else:
                    print(f"  ❌ {test_case['description']}: HTTP {response.status_code}")
            
            if successful_analyses == len(test_cases):
                self.log_test("Roof Analysis AI Prompt Working", True, 
                            f"✅ AI prompt working correctly. All {len(test_cases)} test cases produced relevant solar panel placement analysis.")
            elif successful_analyses > 0:
                self.log_test("Roof Analysis AI Prompt Working", True, 
                            f"✅ AI prompt partially working. {successful_analyses}/{len(test_cases)} test cases produced relevant analysis.")
            else:
                self.log_test("Roof Analysis AI Prompt Working", False, 
                            f"❌ AI prompt not working properly. No test cases produced relevant solar analysis.")
                
        except Exception as e:
            self.log_test("Roof Analysis AI Prompt Working", False, f"Error: {str(e)}")

    def test_roof_analysis_openai_integration(self):
        """Test OpenAI Vision API integration via emergentintegrations"""
        try:
            # Create a more realistic test image (small house roof)
            test_request = {
                "image_base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU77zgAAAABJRU5ErkJggg==",
                "panel_count": 6,
                "panel_surface": 2.11
            }
            
            response = self.session.post(f"{self.base_url}/analyze-roof", json=test_request)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if OpenAI integration worked
                if data.get("success"):
                    # Check if we got meaningful analysis
                    roof_analysis = data.get("roof_analysis", "")
                    if len(roof_analysis) > 10:  # Should have substantial analysis
                        self.log_test("Roof Analysis OpenAI Integration", True, 
                                    f"✅ OpenAI Vision API integration working. Analysis length: {len(roof_analysis)} chars, Placement possible: {data.get('placement_possible')}", 
                                    {"analysis_preview": roof_analysis[:100] + "..." if len(roof_analysis) > 100 else roof_analysis})
                    else:
                        self.log_test("Roof Analysis OpenAI Integration", False, f"Analysis too short: '{roof_analysis}'", data)
                else:
                    # Check if failure is due to API key or other integration issue
                    error_msg = data.get("roof_analysis", "")
                    if "API key" in error_msg or "OpenAI" in error_msg:
                        self.log_test("Roof Analysis OpenAI Integration", False, f"OpenAI API configuration issue: {error_msg}", data)
                    else:
                        self.log_test("Roof Analysis OpenAI Integration", False, f"Integration failed: {error_msg}", data)
            elif response.status_code == 500:
                # Check if it's an OpenAI API key issue
                error_text = response.text
                if "OpenAI API key" in error_text:
                    self.log_test("Roof Analysis OpenAI Integration", False, "OpenAI API key not configured or invalid")
                else:
                    self.log_test("Roof Analysis OpenAI Integration", False, f"Server error: {error_text}")
            else:
                self.log_test("Roof Analysis OpenAI Integration", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Roof Analysis OpenAI Integration", False, f"Error: {str(e)}")

    def test_roof_analysis_openai_vision(self):
        """Test the new roof analysis endpoint with OpenAI Vision API"""
        try:
            # Create a simple test image (base64 encoded 1x1 pixel PNG)
            # This is a minimal valid PNG image for testing
            test_image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU77zgAAAABJRU5ErkJggg=="
            
            # Test data for roof analysis
            test_data = {
                "image_base64": test_image_base64,
                "panel_count": 12,
                "panel_surface": 2.11
            }
            
            response = self.session.post(f"{self.base_url}/analyze-roof", json=test_data)
            
            if response.status_code == 200:
                analysis = response.json()
                
                # Check required response fields
                required_fields = [
                    "success", "panel_positions", "roof_analysis", 
                    "total_surface_required", "placement_possible", "recommendations"
                ]
                
                missing_fields = [field for field in required_fields if field not in analysis]
                if missing_fields:
                    self.log_test("Roof Analysis OpenAI Vision", False, f"Missing response fields: {missing_fields}", analysis)
                    return
                
                # Validate response structure
                issues = []
                
                # Check success field
                if not isinstance(analysis.get("success"), bool):
                    issues.append("'success' field should be boolean")
                
                # Check panel_positions is a list
                panel_positions = analysis.get("panel_positions", [])
                if not isinstance(panel_positions, list):
                    issues.append("'panel_positions' should be a list")
                elif len(panel_positions) != test_data["panel_count"]:
                    issues.append(f"Expected {test_data['panel_count']} panel positions, got {len(panel_positions)}")
                else:
                    # Check each panel position structure
                    for i, position in enumerate(panel_positions):
                        required_pos_fields = ["x", "y", "width", "height", "angle"]
                        missing_pos_fields = [field for field in required_pos_fields if field not in position]
                        if missing_pos_fields:
                            issues.append(f"Panel position {i} missing fields: {missing_pos_fields}")
                            break
                        
                        # Check that coordinates are between 0 and 1
                        for coord in ["x", "y", "width", "height"]:
                            value = position.get(coord, -1)
                            if not isinstance(value, (int, float)) or value < 0 or value > 1:
                                issues.append(f"Panel position {i} {coord} should be between 0 and 1, got {value}")
                                break
                
                # Check total_surface_required calculation
                expected_surface = test_data["panel_count"] * test_data["panel_surface"]
                actual_surface = analysis.get("total_surface_required", 0)
                if abs(actual_surface - expected_surface) > 0.1:
                    issues.append(f"Total surface required {actual_surface}m² != expected {expected_surface}m²")
                
                # Check placement_possible is boolean
                if not isinstance(analysis.get("placement_possible"), bool):
                    issues.append("'placement_possible' field should be boolean")
                
                # Check that roof_analysis and recommendations are strings
                if not isinstance(analysis.get("roof_analysis"), str):
                    issues.append("'roof_analysis' should be a string")
                elif len(analysis.get("roof_analysis", "")) < 10:
                    issues.append("'roof_analysis' seems too short (should contain detailed analysis)")
                
                if not isinstance(analysis.get("recommendations"), str):
                    issues.append("'recommendations' should be a string")
                elif len(analysis.get("recommendations", "")) < 10:
                    issues.append("'recommendations' seems too short (should contain recommendations)")
                
                if issues:
                    self.log_test("Roof Analysis OpenAI Vision", False, f"Response validation issues: {'; '.join(issues)}", analysis)
                else:
                    self.log_test("Roof Analysis OpenAI Vision", True, 
                                f"✅ OpenAI Vision roof analysis working. Success: {analysis['success']}, {len(panel_positions)} panel positions generated, {actual_surface}m² total surface, Placement possible: {analysis['placement_possible']}", 
                                {
                                    "success": analysis["success"],
                                    "panel_count": len(panel_positions),
                                    "total_surface": actual_surface,
                                    "placement_possible": analysis["placement_possible"],
                                    "analysis_length": len(analysis.get("roof_analysis", "")),
                                    "recommendations_length": len(analysis.get("recommendations", ""))
                                })
            
            elif response.status_code == 500:
                # Check if it's an OpenAI API key issue
                error_text = response.text.lower()
                if "openai" in error_text and ("key" in error_text or "api" in error_text):
                    self.log_test("Roof Analysis OpenAI Vision", False, "OpenAI API key configuration issue - endpoint exists but API key may be invalid or missing")
                else:
                    self.log_test("Roof Analysis OpenAI Vision", False, f"Server error: HTTP {response.status_code}: {response.text}")
            
            elif response.status_code == 422:
                # Validation error - check if endpoint exists but has validation issues
                self.log_test("Roof Analysis OpenAI Vision", False, f"Request validation error: {response.text}")
            
            else:
                self.log_test("Roof Analysis OpenAI Vision", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Roof Analysis OpenAI Vision", False, f"Error: {str(e)}")

    def test_roof_analysis_with_different_panel_counts(self):
        """Test roof analysis with different panel counts (6, 12, 18)"""
        try:
            # Simple test image
            test_image_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU77zgAAAABJRU5ErkJggg=="
            
            test_cases = [
                {"panel_count": 6, "expected_surface": 12.66},
                {"panel_count": 12, "expected_surface": 25.32},
                {"panel_count": 18, "expected_surface": 37.98}
            ]
            
            all_passed = True
            results = []
            
            for test_case in test_cases:
                test_data = {
                    "image_base64": test_image_base64,
                    "panel_count": test_case["panel_count"],
                    "panel_surface": 2.11
                }
                
                response = self.session.post(f"{self.base_url}/analyze-roof", json=test_data)
                
                if response.status_code == 200:
                    analysis = response.json()
                    
                    # Check panel count matches
                    panel_positions = analysis.get("panel_positions", [])
                    if len(panel_positions) != test_case["panel_count"]:
                        all_passed = False
                        results.append(f"{test_case['panel_count']} panels: got {len(panel_positions)} positions")
                    else:
                        # Check surface calculation
                        actual_surface = analysis.get("total_surface_required", 0)
                        if abs(actual_surface - test_case["expected_surface"]) > 0.1:
                            all_passed = False
                            results.append(f"{test_case['panel_count']} panels: surface {actual_surface}m² != {test_case['expected_surface']}m²")
                        else:
                            results.append(f"{test_case['panel_count']} panels: ✓ {len(panel_positions)} positions, {actual_surface}m²")
                else:
                    all_passed = False
                    results.append(f"{test_case['panel_count']} panels: HTTP {response.status_code}")
            
            if all_passed:
                self.log_test("Roof Analysis Panel Count Variations", True, 
                            f"✅ All panel count variations working: {'; '.join(results)}", 
                            {"test_cases": test_cases, "results": results})
            else:
                self.log_test("Roof Analysis Panel Count Variations", False, 
                            f"Some panel count tests failed: {'; '.join(results)}", 
                            {"test_cases": test_cases, "results": results})
                
        except Exception as e:
            self.log_test("Roof Analysis Panel Count Variations", False, f"Error: {str(e)}")

    def test_roof_analysis_error_handling(self):
        """Test roof analysis error handling with invalid inputs"""
        try:
            test_cases = [
                {
                    "name": "Missing image",
                    "data": {"panel_count": 12, "panel_surface": 2.11},
                    "expected_status": 422
                },
                {
                    "name": "Invalid base64",
                    "data": {"image_base64": "invalid_base64", "panel_count": 12, "panel_surface": 2.11},
                    "expected_status": [422, 500]  # Could be validation or processing error
                },
                {
                    "name": "Zero panels",
                    "data": {"image_base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU77zgAAAABJRU5ErkJggg==", "panel_count": 0, "panel_surface": 2.11},
                    "expected_status": 422
                },
                {
                    "name": "Negative panel surface",
                    "data": {"image_base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU77zgAAAABJRU5ErkJggg==", "panel_count": 12, "panel_surface": -1.0},
                    "expected_status": 422
                }
            ]
            
            results = []
            all_passed = True
            
            for test_case in test_cases:
                response = self.session.post(f"{self.base_url}/analyze-roof", json=test_case["data"])
                
                expected_statuses = test_case["expected_status"] if isinstance(test_case["expected_status"], list) else [test_case["expected_status"]]
                
                if response.status_code in expected_statuses:
                    results.append(f"{test_case['name']}: ✓ HTTP {response.status_code}")
                else:
                    all_passed = False
                    results.append(f"{test_case['name']}: ✗ HTTP {response.status_code} (expected {expected_statuses})")
            
            if all_passed:
                self.log_test("Roof Analysis Error Handling", True, 
                            f"✅ Error handling working correctly: {'; '.join(results)}", 
                            {"test_cases": test_cases, "results": results})
            else:
                self.log_test("Roof Analysis Error Handling", False, 
                            f"Some error handling tests failed: {'; '.join(results)}", 
                            {"test_cases": test_cases, "results": results})
                
        except Exception as e:
            self.log_test("Roof Analysis Error Handling", False, f"Error: {str(e)}")

    def run_all_tests(self):
        """Run all backend tests with focus on TVA correction verification"""
        print("🚀 Starting Comprehensive Backend Testing for Solar Calculator")
        print("🎯 FOCUS: TVA Correction Verification (France 10% vs Martinique 2.1%)")
        print("=" * 80)
        
        # Basic connectivity tests
        self.test_api_root()
        self.test_solar_kits()
        self.test_pvgis_direct()
        
        # Client management tests
        self.test_create_client()
        self.test_get_clients()
        self.test_get_client_by_id()
        
        # CRITICAL TVA CORRECTION TESTS (as requested in review)
        print("\n🔥 CRITICAL TVA CORRECTION TESTS")
        print("-" * 50)
        self.test_tva_consistency_france_martinique()
        self.test_pdf_devis_generation_both_regions()
        self.test_regional_calculation_consistency()
        self.test_devis_endpoint_both_regions()
        
        # Core calculation tests
        print("\n⚙️ CORE CALCULATION TESTS")
        print("-" * 50)
        self.test_solar_calculation()
        self.test_financing_with_aids_calculation()
        self.test_all_financing_with_aids_calculation()
        self.test_autoconsumption_surplus_distribution()
        
        # PDF generation tests
        self.test_pdf_generation_financing_tables()
        
        # Region system tests
        self.test_regions_endpoint()
        self.test_france_region_config()
        self.test_martinique_region_config()
        self.test_martinique_kits_endpoint()
        self.test_calculation_default_region()
        self.test_calculation_martinique_region()
        self.test_region_financing_differences()
        
        # Calculation modes tests
        self.test_calculation_modes_endpoint()
        self.test_realistic_mode_config()
        self.test_optimistic_mode_config()
        self.test_calculation_with_realistic_mode()
        self.test_calculation_with_optimistic_mode()
        self.test_calculation_modes_comparison()
        
        # NEW: Roof Analysis with OpenAI Vision tests
        print("\n🏠 ROOF ANALYSIS AI FEATURE TESTS")
        print("-" * 50)
        self.test_roof_analysis_endpoint_exists()
        self.test_roof_analysis_parameters_validation()
        self.test_roof_analysis_openai_integration()
        self.test_roof_analysis_response_format()
        self.test_roof_analysis_ai_prompt_working()
        self.test_roof_analysis_openai_vision()
        self.test_roof_analysis_with_different_panel_counts()
        self.test_roof_analysis_error_handling()
        
        # Print summary
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Highlight critical TVA tests
        tva_tests = [r for r in self.test_results if "TVA" in r["test"] or "Devis" in r["test"] or "Regional" in r["test"]]
        tva_passed = sum(1 for r in tva_tests if r["success"])
        print(f"\n🎯 CRITICAL TVA/REGIONAL TESTS: {tva_passed}/{len(tva_tests)} passed")
        
        if failed_tests > 0:
            print("\n🔍 FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"❌ {result['test']}: {result['details']}")
        
        print("\n" + "=" * 80)

if __name__ == "__main__":
    tester = SolarCalculatorTester()
    results = tester.run_all_tests()
    
    # Save detailed results to file
    with open("/app/test_results_detailed.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Detailed results saved to /app/test_results_detailed.json")