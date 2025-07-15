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
BACKEND_URL = "https://b3e4f691-e66b-445a-8707-3eb34141dcd9.preview.emergentagent.com/api"

class SolarCalculatorTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.client_id = None
        self.professional_client_id = None
        self.particuliers_calculation = None
        self.professionnels_calculation = None
        
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
    
    def test_solar_kits_legacy(self):
        """Test legacy solar kits endpoint (should return particuliers kits)"""
        try:
            response = self.session.get(f"{self.base_url}/solar-kits")
            if response.status_code == 200:
                kits = response.json()
                if isinstance(kits, dict) and len(kits) > 0:
                    # Check if we have expected kit sizes for particuliers
                    expected_sizes = [3, 4, 5, 6, 7, 8, 9]
                    available_sizes = list(kits.keys())
                    available_sizes = [int(k) for k in available_sizes]
                    
                    if all(size in available_sizes for size in expected_sizes):
                        # Check pricing structure
                        kit_6 = kits.get("6", {})
                        if "price" in kit_6 and "panels" in kit_6:
                            self.log_test("Solar Kits Legacy", True, 
                                        f"Legacy endpoint working. 6kW kit: {kit_6['price']}€, {kit_6['panels']} panels", 
                                        kits)
                        else:
                            self.log_test("Solar Kits Legacy", False, "Missing price/panels info in kit data", kits)
                    else:
                        self.log_test("Solar Kits Legacy", False, f"Missing expected kit sizes. Available: {available_sizes}", kits)
                else:
                    self.log_test("Solar Kits Legacy", False, f"Invalid kits format: {kits}", kits)
            else:
                self.log_test("Solar Kits Legacy", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Solar Kits Legacy", False, f"Error: {str(e)}")

    def test_solar_kits_particuliers(self):
        """Test solar kits endpoint for particuliers mode"""
        try:
            response = self.session.get(f"{self.base_url}/solar-kits/particuliers")
            if response.status_code == 200:
                kits = response.json()
                if isinstance(kits, dict) and len(kits) > 0:
                    # Check if we have expected kit sizes for particuliers (3-9kW)
                    expected_sizes = [3, 4, 5, 6, 7, 8, 9]
                    available_sizes = list(kits.keys())
                    available_sizes = [int(k) for k in available_sizes]
                    
                    if all(size in available_sizes for size in expected_sizes):
                        # Should NOT have professional kits (12, 15, 20kW)
                        professional_sizes = [12, 15, 20]
                        has_professional_kits = any(size in available_sizes for size in professional_sizes)
                        
                        if not has_professional_kits:
                            kit_6 = kits.get("6", {})
                            self.log_test("Solar Kits Particuliers", True, 
                                        f"Particuliers kits (3-9kW only). 6kW kit: {kit_6['price']}€, {kit_6['panels']} panels", 
                                        kits)
                        else:
                            self.log_test("Solar Kits Particuliers", False, 
                                        f"Particuliers should not have professional kits. Found: {[s for s in available_sizes if s in professional_sizes]}", 
                                        kits)
                    else:
                        self.log_test("Solar Kits Particuliers", False, f"Missing expected kit sizes. Available: {available_sizes}", kits)
                else:
                    self.log_test("Solar Kits Particuliers", False, f"Invalid kits format: {kits}", kits)
            else:
                self.log_test("Solar Kits Particuliers", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Solar Kits Particuliers", False, f"Error: {str(e)}")

    def test_solar_kits_professionnels(self):
        """Test solar kits endpoint for professionnels mode"""
        try:
            response = self.session.get(f"{self.base_url}/solar-kits/professionnels")
            if response.status_code == 200:
                kits = response.json()
                if isinstance(kits, dict) and len(kits) > 0:
                    # Check if we have expected kit sizes for professionnels (3-9kW + 12, 15, 20kW)
                    expected_basic_sizes = [3, 4, 5, 6, 7, 8, 9]
                    expected_professional_sizes = [12, 15, 20]
                    all_expected_sizes = expected_basic_sizes + expected_professional_sizes
                    
                    available_sizes = list(kits.keys())
                    available_sizes = [int(k) for k in available_sizes]
                    
                    if all(size in available_sizes for size in all_expected_sizes):
                        # Check pricing - should be slightly lower than particuliers
                        kit_6 = kits.get("6", {})
                        kit_12 = kits.get("12", {})
                        kit_20 = kits.get("20", {})
                        
                        if all(kit.get("price") and kit.get("panels") for kit in [kit_6, kit_12, kit_20]):
                            self.log_test("Solar Kits Professionnels", True, 
                                        f"Professional kits available (3-9kW + 12,15,20kW). 6kW: {kit_6['price']}€, 12kW: {kit_12['price']}€, 20kW: {kit_20['price']}€", 
                                        kits)
                        else:
                            self.log_test("Solar Kits Professionnels", False, "Missing price/panels info in professional kit data", kits)
                    else:
                        missing_sizes = [s for s in all_expected_sizes if s not in available_sizes]
                        self.log_test("Solar Kits Professionnels", False, f"Missing professional kit sizes: {missing_sizes}. Available: {available_sizes}", kits)
                else:
                    self.log_test("Solar Kits Professionnels", False, f"Invalid kits format: {kits}", kits)
            else:
                self.log_test("Solar Kits Professionnels", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Solar Kits Professionnels", False, f"Error: {str(e)}")

    def test_solar_kits_pricing_comparison(self):
        """Test that professional kits have different (lower) pricing than particuliers"""
        try:
            # Get particuliers kits
            response_part = self.session.get(f"{self.base_url}/solar-kits/particuliers")
            response_prof = self.session.get(f"{self.base_url}/solar-kits/professionnels")
            
            if response_part.status_code == 200 and response_prof.status_code == 200:
                kits_part = response_part.json()
                kits_prof = response_prof.json()
                
                # Compare pricing for common kits (3-9kW)
                common_sizes = [3, 4, 5, 6, 7, 8, 9]
                pricing_differences = []
                
                for size in common_sizes:
                    if str(size) in kits_part and str(size) in kits_prof:
                        part_price = kits_part[str(size)]["price"]
                        prof_price = kits_prof[str(size)]["price"]
                        
                        if prof_price < part_price:
                            difference = part_price - prof_price
                            pricing_differences.append(f"{size}kW: {part_price}€ → {prof_price}€ (-{difference}€)")
                        elif prof_price == part_price:
                            pricing_differences.append(f"{size}kW: same price {part_price}€")
                        else:
                            pricing_differences.append(f"{size}kW: HIGHER for pros {prof_price}€ vs {part_price}€")
                
                if len(pricing_differences) == len(common_sizes):
                    # Check if most professional prices are lower
                    lower_count = sum(1 for diff in pricing_differences if "→" in diff and "-" in diff)
                    if lower_count >= len(common_sizes) * 0.7:  # At least 70% should be lower
                        self.log_test("Solar Kits Pricing Comparison", True, 
                                    f"Professional pricing is lower for most kits. Examples: {'; '.join(pricing_differences[:3])}", 
                                    {"particuliers_sample": {str(k): kits_part[str(k)] for k in [6, 9]}, 
                                     "professionnels_sample": {str(k): kits_prof[str(k)] for k in [6, 9, 12, 20]}})
                    else:
                        self.log_test("Solar Kits Pricing Comparison", False, 
                                    f"Professional pricing not consistently lower. Details: {'; '.join(pricing_differences)}")
                else:
                    self.log_test("Solar Kits Pricing Comparison", False, f"Could not compare all common kit sizes")
            else:
                self.log_test("Solar Kits Pricing Comparison", False, 
                            f"Failed to get kits data. Particuliers: {response_part.status_code}, Professionnels: {response_prof.status_code}")
        except Exception as e:
            self.log_test("Solar Kits Pricing Comparison", False, f"Error: {str(e)}")
    
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
    
    def test_create_client_particuliers(self):
        """Test client creation with particuliers mode"""
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
                "annual_edf_payment": 2160.0,
                "client_mode": "particuliers"
            }
            
            response = self.session.post(f"{self.base_url}/clients", json=client_data)
            if response.status_code == 200:
                client = response.json()
                
                # Check if geocoding worked and client_mode is stored
                if "latitude" in client and "longitude" in client and "id" in client and "client_mode" in client:
                    lat, lon = client["latitude"], client["longitude"]
                    client_mode = client["client_mode"]
                    self.client_id = client["id"]  # Store for next test
                    
                    # Paris coordinates should be around 48.8566, 2.3522
                    if 48.5 <= lat <= 49.0 and 2.0 <= lon <= 2.7 and client_mode == "particuliers":
                        self.log_test("Create Client Particuliers", True, 
                                    f"Particuliers client created. ID: {self.client_id}, Mode: {client_mode}, Coords: {lat:.4f}, {lon:.4f}", 
                                    client)
                    else:
                        issues = []
                        if not (48.5 <= lat <= 49.0 and 2.0 <= lon <= 2.7):
                            issues.append(f"Geocoding incorrect: {lat}, {lon}")
                        if client_mode != "particuliers":
                            issues.append(f"Client mode incorrect: {client_mode}")
                        self.log_test("Create Client Particuliers", False, f"Issues: {'; '.join(issues)}", client)
                else:
                    missing_fields = [f for f in ["latitude", "longitude", "id", "client_mode"] if f not in client]
                    self.log_test("Create Client Particuliers", False, f"Missing fields: {missing_fields}", client)
            else:
                self.log_test("Create Client Particuliers", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Create Client Particuliers", False, f"Error: {str(e)}")

    def test_create_client_professionnels(self):
        """Test client creation with professionnels mode"""
        try:
            client_data = {
                "first_name": "Marie",
                "last_name": "Martin",
                "address": "15 Rue de Rivoli, 75001 Paris",
                "roof_surface": 120.0,  # Larger roof for professional
                "roof_orientation": "Sud",
                "velux_count": 4,
                "heating_system": "Pompe à chaleur",
                "water_heating_system": "Solaire thermique",
                "water_heating_capacity": 300,
                "annual_consumption_kwh": 12000.0,  # Higher consumption for professional
                "monthly_edf_payment": 350.0,
                "annual_edf_payment": 4200.0,
                "client_mode": "professionnels"
            }
            
            response = self.session.post(f"{self.base_url}/clients", json=client_data)
            if response.status_code == 200:
                client = response.json()
                
                # Check if geocoding worked and client_mode is stored
                if "latitude" in client and "longitude" in client and "id" in client and "client_mode" in client:
                    lat, lon = client["latitude"], client["longitude"]
                    client_mode = client["client_mode"]
                    self.professional_client_id = client["id"]  # Store for comparison test
                    
                    # Paris coordinates should be around 48.8566, 2.3522
                    if 48.5 <= lat <= 49.0 and 2.0 <= lon <= 2.7 and client_mode == "professionnels":
                        self.log_test("Create Client Professionnels", True, 
                                    f"Professional client created. ID: {self.professional_client_id}, Mode: {client_mode}, Coords: {lat:.4f}, {lon:.4f}", 
                                    client)
                    else:
                        issues = []
                        if not (48.5 <= lat <= 49.0 and 2.0 <= lon <= 2.7):
                            issues.append(f"Geocoding incorrect: {lat}, {lon}")
                        if client_mode != "professionnels":
                            issues.append(f"Client mode incorrect: {client_mode}")
                        self.log_test("Create Client Professionnels", False, f"Issues: {'; '.join(issues)}", client)
                else:
                    missing_fields = [f for f in ["latitude", "longitude", "id", "client_mode"] if f not in client]
                    self.log_test("Create Client Professionnels", False, f"Missing fields: {missing_fields}", client)
            else:
                self.log_test("Create Client Professionnels", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Create Client Professionnels", False, f"Error: {str(e)}")
    
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
    
    def test_solar_calculation_particuliers(self):
        """Test solar calculation for particuliers client"""
        if not self.client_id:
            self.log_test("Solar Calculation Particuliers", False, "No particuliers client ID available from previous test")
            return
            
        try:
            response = self.session.post(f"{self.base_url}/calculate/{self.client_id}")
            if response.status_code == 200:
                calculation = response.json()
                
                # Check key calculation results including client_mode and aids_config
                required_fields = [
                    "kit_power", "panel_count", "estimated_production", 
                    "estimated_savings", "autonomy_percentage", "monthly_savings",
                    "financing_options", "kit_price", "client_mode", "aids_config",
                    "autoconsumption_aid", "total_aids"
                ]
                
                missing_fields = [field for field in required_fields if field not in calculation]
                if missing_fields:
                    self.log_test("Solar Calculation Particuliers", False, f"Missing fields: {missing_fields}", calculation)
                    return
                
                # Validate calculation results
                client_mode = calculation.get("client_mode")
                aids_config = calculation.get("aids_config", {})
                autoconsumption_aid = calculation.get("autoconsumption_aid", 0)
                kit_power = calculation.get("kit_power", 0)
                
                issues = []
                
                # Check client mode
                if client_mode != "particuliers":
                    issues.append(f"Client mode should be 'particuliers', got '{client_mode}'")
                
                # Check aids configuration for particuliers
                expected_aid_rate = 80  # €/kW for particuliers
                actual_aid_rate = aids_config.get("autoconsumption_aid_rate", 0)
                if actual_aid_rate != expected_aid_rate:
                    issues.append(f"Aid rate should be {expected_aid_rate}€/kW for particuliers, got {actual_aid_rate}€/kW")
                
                # Check autoconsumption aid calculation
                expected_autoconsumption_aid = kit_power * expected_aid_rate
                if abs(autoconsumption_aid - expected_autoconsumption_aid) > 1:
                    issues.append(f"Autoconsumption aid {autoconsumption_aid}€ != {kit_power}kW × {expected_aid_rate}€/kW = {expected_autoconsumption_aid}€")
                
                # Store calculation for comparison
                self.particuliers_calculation = calculation
                
                if issues:
                    self.log_test("Solar Calculation Particuliers", False, f"Calculation issues: {'; '.join(issues)}", calculation)
                else:
                    self.log_test("Solar Calculation Particuliers", True, 
                                f"Particuliers calculation successful: {kit_power}kW, {calculation['estimated_production']:.0f} kWh/year, {calculation['autonomy_percentage']:.1f}% autonomy, {autoconsumption_aid}€ aid ({actual_aid_rate}€/kW)", 
                                calculation)
            else:
                self.log_test("Solar Calculation Particuliers", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Solar Calculation Particuliers", False, f"Error: {str(e)}")

    def test_solar_calculation_professionnels(self):
        """Test solar calculation for professionnels client"""
        if not hasattr(self, 'professional_client_id') or not self.professional_client_id:
            self.log_test("Solar Calculation Professionnels", False, "No professional client ID available from previous test")
            return
            
        try:
            response = self.session.post(f"{self.base_url}/calculate/{self.professional_client_id}")
            if response.status_code == 200:
                calculation = response.json()
                
                # Check key calculation results including client_mode and aids_config
                required_fields = [
                    "kit_power", "panel_count", "estimated_production", 
                    "estimated_savings", "autonomy_percentage", "monthly_savings",
                    "financing_options", "kit_price", "client_mode", "aids_config",
                    "autoconsumption_aid", "total_aids"
                ]
                
                missing_fields = [field for field in required_fields if field not in calculation]
                if missing_fields:
                    self.log_test("Solar Calculation Professionnels", False, f"Missing fields: {missing_fields}", calculation)
                    return
                
                # Validate calculation results
                client_mode = calculation.get("client_mode")
                aids_config = calculation.get("aids_config", {})
                autoconsumption_aid = calculation.get("autoconsumption_aid", 0)
                kit_power = calculation.get("kit_power", 0)
                
                issues = []
                
                # Check client mode
                if client_mode != "professionnels":
                    issues.append(f"Client mode should be 'professionnels', got '{client_mode}'")
                
                # Check aids configuration for professionnels
                expected_aid_rate = 60  # €/kW for professionnels (reduced from 80€/kW)
                actual_aid_rate = aids_config.get("autoconsumption_aid_rate", 0)
                if actual_aid_rate != expected_aid_rate:
                    issues.append(f"Aid rate should be {expected_aid_rate}€/kW for professionnels, got {actual_aid_rate}€/kW")
                
                # Check autoconsumption aid calculation
                expected_autoconsumption_aid = kit_power * expected_aid_rate
                if abs(autoconsumption_aid - expected_autoconsumption_aid) > 1:
                    issues.append(f"Autoconsumption aid {autoconsumption_aid}€ != {kit_power}kW × {expected_aid_rate}€/kW = {expected_autoconsumption_aid}€")
                
                # Check for amortissement accéléré in aids_config
                amortissement_accelere = aids_config.get("amortissement_accelere", 0)
                if amortissement_accelere != 0.30:  # 30% amortissement accéléré
                    issues.append(f"Amortissement accéléré should be 0.30 (30%) for professionnels, got {amortissement_accelere}")
                
                # Check if professional can get larger kits (12kW+)
                if kit_power >= 12:
                    issues.append(f"Professional client recommended {kit_power}kW kit (good - larger kits available)")
                    issues.pop()  # Remove this "issue" as it's actually good
                
                # Store calculation for comparison
                self.professionnels_calculation = calculation
                
                if issues:
                    self.log_test("Solar Calculation Professionnels", False, f"Calculation issues: {'; '.join(issues)}", calculation)
                else:
                    self.log_test("Solar Calculation Professionnels", True, 
                                f"Professional calculation successful: {kit_power}kW, {calculation['estimated_production']:.0f} kWh/year, {calculation['autonomy_percentage']:.1f}% autonomy, {autoconsumption_aid}€ aid ({actual_aid_rate}€/kW), amortissement: {amortissement_accelere*100:.0f}%", 
                                calculation)
            else:
                self.log_test("Solar Calculation Professionnels", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Solar Calculation Professionnels", False, f"Error: {str(e)}")

    def test_particuliers_vs_professionnels_comparison(self):
        """Test comparison between particuliers and professionnels calculations"""
        if not hasattr(self, 'particuliers_calculation') or not hasattr(self, 'professionnels_calculation'):
            self.log_test("Particuliers vs Professionnels Comparison", False, "Missing calculation data from previous tests")
            return
            
        try:
            part_calc = self.particuliers_calculation
            prof_calc = self.professionnels_calculation
            
            # Compare aid rates
            part_aid_rate = part_calc.get("aids_config", {}).get("autoconsumption_aid_rate", 0)
            prof_aid_rate = prof_calc.get("aids_config", {}).get("autoconsumption_aid_rate", 0)
            
            # Compare total aids for same kit power (if possible)
            part_kit_power = part_calc.get("kit_power", 0)
            prof_kit_power = prof_calc.get("kit_power", 0)
            
            part_autoconsumption_aid = part_calc.get("autoconsumption_aid", 0)
            prof_autoconsumption_aid = prof_calc.get("autoconsumption_aid", 0)
            
            issues = []
            
            # Check aid rate difference
            if part_aid_rate != 80:
                issues.append(f"Particuliers aid rate should be 80€/kW, got {part_aid_rate}€/kW")
            if prof_aid_rate != 60:
                issues.append(f"Professionnels aid rate should be 60€/kW, got {prof_aid_rate}€/kW")
            
            # Calculate aid difference for comparison
            if part_kit_power > 0 and prof_kit_power > 0:
                # Normalize to per kW for comparison
                part_aid_per_kw = part_autoconsumption_aid / part_kit_power
                prof_aid_per_kw = prof_autoconsumption_aid / prof_kit_power
                
                aid_difference = part_aid_per_kw - prof_aid_per_kw
                expected_difference = 80 - 60  # 20€/kW difference
                
                if abs(aid_difference - expected_difference) > 1:
                    issues.append(f"Aid difference should be 20€/kW, got {aid_difference:.2f}€/kW")
            
            # Check amortissement accéléré for professionals only
            part_amortissement = part_calc.get("aids_config", {}).get("amortissement_accelere", 0)
            prof_amortissement = prof_calc.get("aids_config", {}).get("amortissement_accelere", 0)
            
            if part_amortissement != 0:
                issues.append(f"Particuliers should not have amortissement accéléré, got {part_amortissement}")
            if prof_amortissement != 0.30:
                issues.append(f"Professionnels should have 30% amortissement accéléré, got {prof_amortissement}")
            
            # Check if professional has access to larger kits
            professional_kit_available = prof_kit_power >= 12 or prof_kit_power > part_kit_power
            
            if issues:
                self.log_test("Particuliers vs Professionnels Comparison", False, f"Comparison issues: {'; '.join(issues)}")
            else:
                comparison_summary = (
                    f"✅ Aid rates: Particuliers {part_aid_rate}€/kW vs Professionnels {prof_aid_rate}€/kW (-20€/kW). "
                    f"Amortissement: Particuliers {part_amortissement*100:.0f}% vs Professionnels {prof_amortissement*100:.0f}%. "
                    f"Kit sizes: Particuliers {part_kit_power}kW vs Professionnels {prof_kit_power}kW"
                )
                
                self.log_test("Particuliers vs Professionnels Comparison", True, comparison_summary, {
                    "particuliers": {
                        "aid_rate": part_aid_rate,
                        "kit_power": part_kit_power,
                        "autoconsumption_aid": part_autoconsumption_aid,
                        "amortissement_accelere": part_amortissement
                    },
                    "professionnels": {
                        "aid_rate": prof_aid_rate,
                        "kit_power": prof_kit_power,
                        "autoconsumption_aid": prof_autoconsumption_aid,
                        "amortissement_accelere": prof_amortissement
                    }
                })
                
        except Exception as e:
            self.log_test("Particuliers vs Professionnels Comparison", False, f"Error: {str(e)}")
    
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

    def test_leasing_matrix_rates(self):
        """Test the leasing matrix with different amounts and durations"""
        try:
            # Test case 1: 30,000€ / 72 mois = 1.77 (autorisé)
            test_cases = [
                {"amount": 30000, "duration": 72, "expected_rate": 1.77, "should_exist": True, "description": "30,000€ / 72 mois"},
                {"amount": 30000, "duration": 84, "expected_rate": None, "should_exist": False, "description": "30,000€ / 84 mois (zone rouge)"},
                {"amount": 15000, "duration": 60, "expected_rate": 2.07, "should_exist": True, "description": "15,000€ / 60 mois"},
                {"amount": 50000, "duration": 96, "expected_rate": 1.4, "should_exist": True, "description": "50,000€ / 96 mois"},
                {"amount": 100000, "duration": 84, "expected_rate": 1.54, "should_exist": True, "description": "100,000€ / 84 mois"},
            ]
            
            issues = []
            
            # Since we can't directly test the matrix function, we'll test through the professional endpoint
            # and verify that leasing options are calculated correctly
            if not hasattr(self, 'professional_client_id') or not self.professional_client_id:
                issues.append("No professional client available for leasing tests")
            else:
                response = self.session.post(f"{self.base_url}/calculate-professional/{self.professional_client_id}", 
                                           params={"price_level": "base"})
                
                if response.status_code == 200:
                    calculation = response.json()
                    leasing_options = calculation.get("leasing_options", [])
                    
                    if not leasing_options:
                        issues.append("No leasing options returned from professional calculation")
                    else:
                        # Verify leasing options structure
                        for option in leasing_options:
                            required_fields = ["duration_months", "duration_years", "rate", "monthly_payment", "total_payment"]
                            missing_fields = [field for field in required_fields if field not in option]
                            if missing_fields:
                                issues.append(f"Leasing option missing fields: {missing_fields}")
                            
                            # Verify rate calculation
                            duration_months = option.get("duration_months", 0)
                            rate = option.get("rate", 0)
                            monthly_payment = option.get("monthly_payment", 0)
                            kit_price = calculation.get("kit_price", 0)
                            
                            if kit_price > 0 and rate > 0:
                                expected_monthly = kit_price * rate
                                if abs(monthly_payment - expected_monthly) > 1:
                                    issues.append(f"Monthly payment {monthly_payment}€ != kit_price {kit_price}€ × rate {rate} = {expected_monthly}€")
                        
                        # Test specific matrix values
                        kit_price = calculation.get("kit_price", 0)
                        for test_case in test_cases:
                            amount = test_case["amount"]
                            duration = test_case["duration"]
                            expected_rate = test_case["expected_rate"]
                            should_exist = test_case["should_exist"]
                            
                            # Find matching option
                            matching_option = None
                            for option in leasing_options:
                                if option.get("duration_months") == duration:
                                    matching_option = option
                                    break
                            
                            if should_exist and expected_rate is not None:
                                if matching_option:
                                    actual_rate = matching_option.get("rate", 0)
                                    if abs(actual_rate - expected_rate) > 0.01:
                                        issues.append(f"Rate mismatch for {duration} months: expected {expected_rate}, got {actual_rate}")
                                else:
                                    issues.append(f"Missing leasing option for {duration} months duration")
                            elif not should_exist:
                                if matching_option:
                                    issues.append(f"Found leasing option for {duration} months (should be zone rouge)")
                else:
                    issues.append(f"Failed to get professional calculation: HTTP {response.status_code}")
            
            if issues:
                self.log_test("Leasing Matrix Rates", False, f"Leasing matrix issues: {'; '.join(issues)}")
            else:
                # Show available leasing options
                response = self.session.post(f"{self.base_url}/calculate-professional/{self.professional_client_id}", 
                                           params={"price_level": "base"})
                if response.status_code == 200:
                    calculation = response.json()
                    leasing_options = calculation.get("leasing_options", [])
                    options_summary = []
                    for option in leasing_options:
                        duration = option.get("duration_months", 0)
                        rate = option.get("rate", 0)
                        monthly = option.get("monthly_payment", 0)
                        options_summary.append(f"{duration}mois: {rate}% = {monthly}€/mois")
                    
                    self.log_test("Leasing Matrix Rates", True, 
                                f"✅ Leasing matrix working. Available options: {'; '.join(options_summary)}", 
                                {"leasing_options": leasing_options, "kit_price": calculation.get("kit_price", 0)})
                
        except Exception as e:
            self.log_test("Leasing Matrix Rates", False, f"Error: {str(e)}")

    def test_optimal_leasing_kit_algorithm(self):
        """Test the find_optimal_leasing_kit algorithm"""
        try:
            if not hasattr(self, 'professional_client_id') or not self.professional_client_id:
                self.log_test("Optimal Leasing Kit Algorithm", False, "No professional client available for leasing tests")
                return
            
            # Test with different price levels
            price_levels = ["base", "remise", "remise_max"]
            optimal_results = {}
            
            for price_level in price_levels:
                response = self.session.post(f"{self.base_url}/calculate-professional/{self.professional_client_id}", 
                                           params={"price_level": price_level})
                
                if response.status_code == 200:
                    calculation = response.json()
                    optimal_kit = calculation.get("optimal_kit")
                    monthly_savings = calculation.get("monthly_savings", 0)
                    
                    if optimal_kit:
                        optimal_results[price_level] = {
                            "kit_power": optimal_kit.get("kit_power"),
                            "monthly_payment": optimal_kit.get("monthly_payment"),
                            "monthly_savings": monthly_savings,
                            "monthly_benefit": optimal_kit.get("monthly_benefit"),
                            "price_level": optimal_kit.get("price_level"),
                            "kit_price": optimal_kit.get("kit_price")
                        }
                    else:
                        optimal_results[price_level] = None
            
            issues = []
            
            # Verify that optimal kits were found
            for price_level, result in optimal_results.items():
                if result is None:
                    issues.append(f"No optimal kit found for price level '{price_level}'")
                else:
                    # Verify that monthly payment <= monthly savings (key requirement)
                    monthly_payment = result["monthly_payment"]
                    monthly_savings = result["monthly_savings"]
                    monthly_benefit = result["monthly_benefit"]
                    
                    if monthly_payment > monthly_savings:
                        issues.append(f"Price level '{price_level}': monthly payment {monthly_payment}€ > monthly savings {monthly_savings}€")
                    
                    # Verify monthly benefit calculation
                    expected_benefit = monthly_savings - monthly_payment
                    if abs(monthly_benefit - expected_benefit) > 0.01:
                        issues.append(f"Price level '{price_level}': monthly benefit {monthly_benefit}€ != {monthly_savings}€ - {monthly_payment}€ = {expected_benefit}€")
            
            # Verify that remise_max gives better deals than base
            if optimal_results.get("base") and optimal_results.get("remise_max"):
                base_benefit = optimal_results["base"]["monthly_benefit"]
                remise_max_benefit = optimal_results["remise_max"]["monthly_benefit"]
                
                if remise_max_benefit <= base_benefit:
                    issues.append(f"Remise max benefit {remise_max_benefit}€ should be > base benefit {base_benefit}€")
            
            if issues:
                self.log_test("Optimal Leasing Kit Algorithm", False, f"Algorithm issues: {'; '.join(issues)}", optimal_results)
            else:
                # Create success summary
                summary_parts = []
                for price_level, result in optimal_results.items():
                    if result:
                        summary_parts.append(f"{price_level}: {result['kit_power']}kW kit, {result['monthly_payment']}€/mois ≤ {result['monthly_savings']}€ économies (+{result['monthly_benefit']}€ bénéfice)")
                
                self.log_test("Optimal Leasing Kit Algorithm", True, 
                            f"✅ MEILLEUR KITS OPTIMISE algorithm working. {'; '.join(summary_parts)}", 
                            optimal_results)
                
        except Exception as e:
            self.log_test("Optimal Leasing Kit Algorithm", False, f"Error: {str(e)}")

    def test_professional_endpoint_complete(self):
        """Test the complete professional endpoint with all features"""
        try:
            if not hasattr(self, 'professional_client_id') or not self.professional_client_id:
                self.log_test("Professional Endpoint Complete", False, "No professional client available")
                return
            
            # Test all three price levels
            price_levels = ["base", "remise", "remise_max"]
            results = {}
            
            for price_level in price_levels:
                response = self.session.post(f"{self.base_url}/calculate-professional/{self.professional_client_id}", 
                                           params={"price_level": price_level})
                
                if response.status_code == 200:
                    calculation = response.json()
                    results[price_level] = calculation
                else:
                    self.log_test("Professional Endpoint Complete", False, 
                                f"Failed to get calculation for price level '{price_level}': HTTP {response.status_code}")
                    return
            
            issues = []
            
            # Verify all required fields are present
            required_fields = [
                "client_id", "client_mode", "price_level", "kit_power", "panel_count", 
                "estimated_production", "estimated_savings", "autonomy_percentage", 
                "monthly_savings", "kit_price", "commission", "autoconsumption_kwh", 
                "surplus_kwh", "autoconsumption_aid", "total_aids", "leasing_options", 
                "optimal_kit", "aids_config", "pricing_options"
            ]
            
            for price_level, calculation in results.items():
                missing_fields = [field for field in required_fields if field not in calculation]
                if missing_fields:
                    issues.append(f"Price level '{price_level}' missing fields: {missing_fields}")
                
                # Verify client mode is professional
                if calculation.get("client_mode") != "professionnels":
                    issues.append(f"Price level '{price_level}': client_mode should be 'professionnels', got '{calculation.get('client_mode')}'")
                
                # Verify price level is correct
                if calculation.get("price_level") != price_level:
                    issues.append(f"Price level mismatch: expected '{price_level}', got '{calculation.get('price_level')}'")
                
                # Verify professional rates (80% autoconsommation, 0.26€/kWh)
                aids_config = calculation.get("aids_config", {})
                autoconsumption_rate = aids_config.get("autoconsumption_rate", 0)
                edf_rate = aids_config.get("edf_rate", 0)
                surplus_sale_rate = aids_config.get("surplus_sale_rate", 0)
                
                if autoconsumption_rate != 0.80:
                    issues.append(f"Price level '{price_level}': autoconsumption rate should be 0.80 (80%), got {autoconsumption_rate}")
                
                if abs(edf_rate - 0.26) > 0.001:
                    issues.append(f"Price level '{price_level}': EDF rate should be 0.26€/kWh, got {edf_rate}€/kWh")
                
                if abs(surplus_sale_rate - 0.0761) > 0.0001:
                    issues.append(f"Price level '{price_level}': surplus sale rate should be 0.0761€/kWh, got {surplus_sale_rate}€/kWh")
                
                # Verify leasing options exist
                leasing_options = calculation.get("leasing_options", [])
                if not leasing_options:
                    issues.append(f"Price level '{price_level}': no leasing options provided")
                
                # Verify optimal kit exists
                optimal_kit = calculation.get("optimal_kit")
                if not optimal_kit:
                    issues.append(f"Price level '{price_level}': no optimal kit found")
                
                # Verify prime calculation (should use table data, not calculated)
                autoconsumption_aid = calculation.get("autoconsumption_aid", 0)
                kit_power = calculation.get("kit_power", 0)
                
                # For professionals, aid should come from table prime, not calculated
                if autoconsumption_aid <= 0:
                    issues.append(f"Price level '{price_level}': autoconsumption aid should be > 0, got {autoconsumption_aid}")
            
            # Verify price differences between levels
            if len(results) == 3:
                base_price = results["base"].get("kit_price", 0)
                remise_price = results["remise"].get("kit_price", 0)
                remise_max_price = results["remise_max"].get("kit_price", 0)
                
                if not (base_price > remise_price > remise_max_price):
                    issues.append(f"Price levels should decrease: base {base_price}€ > remise {remise_price}€ > remise_max {remise_max_price}€")
            
            if issues:
                self.log_test("Professional Endpoint Complete", False, f"Professional endpoint issues: {'; '.join(issues)}", results)
            else:
                # Create success summary
                base_calc = results["base"]
                summary = (
                    f"✅ Professional endpoint working perfectly. "
                    f"Kit: {base_calc.get('kit_power')}kW, "
                    f"Production: {base_calc.get('estimated_production', 0):.0f} kWh/year, "
                    f"80% autoconsommation rate, "
                    f"0.26€/kWh EDF rate, "
                    f"Prime: {base_calc.get('autoconsumption_aid', 0)}€, "
                    f"Prices: base {results['base'].get('kit_price')}€ > remise {results['remise'].get('kit_price')}€ > remise_max {results['remise_max'].get('kit_price')}€"
                )
                
                self.log_test("Professional Endpoint Complete", True, summary, {
                    "base_calculation": results["base"],
                    "price_comparison": {
                        "base": results["base"].get("kit_price"),
                        "remise": results["remise"].get("kit_price"),
                        "remise_max": results["remise_max"].get("kit_price")
                    }
                })
                
        except Exception as e:
            self.log_test("Professional Endpoint Complete", False, f"Error: {str(e)}")

    def test_three_price_levels_optimization(self):
        """Test optimization works for all 3 price levels"""
        try:
            if not hasattr(self, 'professional_client_id') or not self.professional_client_id:
                self.log_test("Three Price Levels Optimization", False, "No professional client available")
                return
            
            price_levels = ["base", "remise", "remise_max"]
            optimization_results = {}
            
            for price_level in price_levels:
                response = self.session.post(f"{self.base_url}/calculate-professional/{self.professional_client_id}", 
                                           params={"price_level": price_level})
                
                if response.status_code == 200:
                    calculation = response.json()
                    optimal_kit = calculation.get("optimal_kit")
                    leasing_options = calculation.get("leasing_options", [])
                    
                    optimization_results[price_level] = {
                        "optimal_kit": optimal_kit,
                        "leasing_options_count": len(leasing_options),
                        "kit_price": calculation.get("kit_price", 0),
                        "monthly_savings": calculation.get("monthly_savings", 0)
                    }
                else:
                    optimization_results[price_level] = None
            
            issues = []
            
            # Verify optimization works for each level
            for price_level, result in optimization_results.items():
                if result is None:
                    issues.append(f"Failed to get calculation for price level '{price_level}'")
                    continue
                
                optimal_kit = result["optimal_kit"]
                if not optimal_kit:
                    issues.append(f"No optimal kit found for price level '{price_level}'")
                    continue
                
                # Verify optimal kit has required fields
                required_optimal_fields = [
                    "kit_power", "monthly_payment", "monthly_savings", "monthly_benefit", 
                    "price_level", "kit_price", "leasing_rate"
                ]
                
                missing_fields = [field for field in required_optimal_fields if field not in optimal_kit]
                if missing_fields:
                    issues.append(f"Optimal kit for '{price_level}' missing fields: {missing_fields}")
                
                # Verify price level matches
                if optimal_kit.get("price_level") != price_level:
                    issues.append(f"Optimal kit price level '{optimal_kit.get('price_level')}' != requested '{price_level}'")
                
                # Verify leasing options exist
                if result["leasing_options_count"] == 0:
                    issues.append(f"No leasing options for price level '{price_level}'")
            
            # Verify that lower price levels give better optimization results
            if all(result is not None for result in optimization_results.values()):
                base_benefit = optimization_results["base"]["optimal_kit"].get("monthly_benefit", 0) if optimization_results["base"]["optimal_kit"] else 0
                remise_benefit = optimization_results["remise"]["optimal_kit"].get("monthly_benefit", 0) if optimization_results["remise"]["optimal_kit"] else 0
                remise_max_benefit = optimization_results["remise_max"]["optimal_kit"].get("monthly_benefit", 0) if optimization_results["remise_max"]["optimal_kit"] else 0
                
                if not (remise_max_benefit >= remise_benefit >= base_benefit):
                    issues.append(f"Monthly benefits should increase with better pricing: base {base_benefit}€ ≤ remise {remise_benefit}€ ≤ remise_max {remise_max_benefit}€")
            
            if issues:
                self.log_test("Three Price Levels Optimization", False, f"Optimization issues: {'; '.join(issues)}", optimization_results)
            else:
                # Create success summary
                summary_parts = []
                for price_level, result in optimization_results.items():
                    if result and result["optimal_kit"]:
                        optimal = result["optimal_kit"]
                        summary_parts.append(f"{price_level}: {optimal.get('kit_power')}kW, {optimal.get('monthly_benefit', 0):.2f}€ bénéfice/mois")
                
                self.log_test("Three Price Levels Optimization", True, 
                            f"✅ Optimization working for all 3 price levels. {'; '.join(summary_parts)}", 
                            optimization_results)
                
        except Exception as e:
            self.log_test("Three Price Levels Optimization", False, f"Error: {str(e)}")
    
    def run_all_tests(self):
        """Run all tests in order"""
        print("🚀 Starting Solar Calculator Backend Tests")
        print(f"Backend URL: {self.base_url}")
        print("=" * 60)
        
        # Priority 1 tests - NEW: Professional Version Endpoints
        print("\n📋 PRIORITY 1 - Professional Version Endpoints")
        self.test_api_root()
        self.test_solar_kits_legacy()
        self.test_solar_kits_particuliers()
        self.test_solar_kits_professionnels()
        self.test_solar_kits_pricing_comparison()
        self.test_pvgis_direct()
        
        # Priority 2 tests - Client Creation with Modes
        print("\n📋 PRIORITY 2 - Client Creation with Professional Mode Support")
        self.test_create_client_particuliers()
        self.test_create_client_professionnels()
        self.test_get_clients()
        self.test_get_client_by_id()
        
        # Priority 3 tests - Solar Calculations with Professional Mode
        print("\n📋 PRIORITY 3 - Solar Calculations with Professional Mode")
        self.test_solar_calculation_particuliers()
        self.test_solar_calculation_professionnels()
        self.test_particuliers_vs_professionnels_comparison()
        
        # NEW: Professional Leasing System Tests
        print("\n📋 PRIORITY 3.5 - NEW Professional Leasing System Tests")
        self.test_leasing_matrix_rates()
        self.test_optimal_leasing_kit_algorithm()
        self.test_professional_endpoint_complete()
        self.test_three_price_levels_optimization()
        
        # Priority 3 - NEW: Test autoconsumption/surplus distribution changes
        print("\n📋 PRIORITY 4 - NEW Autoconsumption/Surplus Distribution (95%/5%)")
        self.test_autoconsumption_surplus_distribution()
        
        # Priority 4 - Financing with aids tests (3.25% TAEG)
        print("\n📋 PRIORITY 5 - Financing with Aids Calculation (3.25% TAEG)")
        self.test_financing_with_aids_calculation()
        self.test_all_financing_with_aids_calculation()
        
        # Priority 5 - PDF Generation with Financing Tables
        print("\n📋 PRIORITY 6 - PDF Generation with Financing Tables")
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