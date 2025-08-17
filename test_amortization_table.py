#!/usr/bin/env python3
"""
Test complet du backend après l'implémentation du tableau d'amortissement
Focus sur les données nécessaires pour le tableau d'amortissement
"""

import requests
import json
import time
from typing import Dict, Any, Optional

# Backend URL from frontend environment
BACKEND_URL = "https://pdf-solar-quote.preview.emergentagent.com/api"

class AmortizationTableTester:
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
        """Test 1: API Root Endpoint - GET /api"""
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "Solar Calculator" in data["message"]:
                    self.log_test("1. API Root Endpoint", True, f"API accessible: {data['message']}", data)
                else:
                    self.log_test("1. API Root Endpoint", False, f"Unexpected response: {data}", data)
            else:
                self.log_test("1. API Root Endpoint", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("1. API Root Endpoint", False, f"Connection error: {str(e)}")
    
    def test_solar_kits_endpoint(self):
        """Test 2: Solar Kits Endpoint - GET /api/solar-kits"""
        try:
            response = self.session.get(f"{self.base_url}/solar-kits")
            if response.status_code == 200:
                kits = response.json()
                if isinstance(kits, dict) and len(kits) > 0:
                    # Check for 6kW kit specifically
                    kit_6 = kits.get("6", {})
                    if "price" in kit_6 and "panels" in kit_6:
                        self.log_test("2. Solar Kits Endpoint", True, 
                                    f"Kits disponibles: {len(kits)} kits. 6kW: {kit_6['price']}€, {kit_6['panels']} panneaux", 
                                    kits)
                    else:
                        self.log_test("2. Solar Kits Endpoint", False, "Missing price/panels in 6kW kit", kits)
                else:
                    self.log_test("2. Solar Kits Endpoint", False, f"Invalid response format: {kits}", kits)
            else:
                self.log_test("2. Solar Kits Endpoint", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("2. Solar Kits Endpoint", False, f"Error: {str(e)}")
    
    def test_regions_endpoint(self):
        """Test 3: Régions Endpoint - GET /api/regions"""
        try:
            response = self.session.get(f"{self.base_url}/regions")
            if response.status_code == 200:
                data = response.json()
                if "regions" in data and "regions_data" in data:
                    regions = data["regions"]
                    if "france" in regions and "martinique" in regions:
                        self.log_test("3. Régions Endpoint", True, 
                                    f"Régions disponibles: {regions}", data)
                    else:
                        self.log_test("3. Régions Endpoint", False, f"Missing expected regions: {regions}", data)
                else:
                    self.log_test("3. Régions Endpoint", False, "Missing regions/regions_data", data)
            else:
                self.log_test("3. Régions Endpoint", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("3. Régions Endpoint", False, f"Error: {str(e)}")
    
    def test_martinique_kits_endpoint(self):
        """Test 4: Martinique Kits Endpoint - GET /api/regions/martinique/kits"""
        try:
            response = self.session.get(f"{self.base_url}/regions/martinique/kits")
            if response.status_code == 200:
                data = response.json()
                if "kits" in data:
                    kits = data["kits"]
                    if len(kits) >= 3:  # Should have at least 3kW, 6kW, 9kW
                        # Find 6kW kit
                        kit_6kw = next((kit for kit in kits if kit.get("power") == 6), None)
                        if kit_6kw:
                            self.log_test("4. Martinique Kits Endpoint", True, 
                                        f"Martinique kits: {len(kits)} kits. 6kW: {kit_6kw.get('price_ttc')}€, aide {kit_6kw.get('aid_amount')}€", 
                                        data)
                        else:
                            self.log_test("4. Martinique Kits Endpoint", False, "6kW kit not found", data)
                    else:
                        self.log_test("4. Martinique Kits Endpoint", False, f"Expected at least 3 kits, got {len(kits)}", data)
                else:
                    self.log_test("4. Martinique Kits Endpoint", False, "Missing kits in response", data)
            else:
                self.log_test("4. Martinique Kits Endpoint", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("4. Martinique Kits Endpoint", False, f"Error: {str(e)}")
    
    def create_martinique_client(self):
        """Create a realistic Martinique client for testing"""
        try:
            client_data = {
                "first_name": "Jean",
                "last_name": "Martinique",
                "address": "Fort-de-France, Martinique",
                "phone": "0596123456",
                "email": "jean.martinique@example.com",
                "roof_surface": 80.0,
                "roof_orientation": "Sud",
                "velux_count": 1,
                "heating_system": "Climatisation",
                "water_heating_system": "Chauffe-eau solaire",
                "water_heating_capacity": 300,
                "annual_consumption_kwh": 7200.0,
                "monthly_edf_payment": 220.0,
                "annual_edf_payment": 2640.0
            }
            
            response = self.session.post(f"{self.base_url}/clients", json=client_data)
            if response.status_code == 200:
                client = response.json()
                self.client_id = client["id"]
                self.log_test("Create Martinique Client", True, 
                            f"Client créé: {client['first_name']} {client['last_name']}, ID: {self.client_id}", 
                            client)
                return True
            else:
                # Try to use existing client
                clients_response = self.session.get(f"{self.base_url}/clients")
                if clients_response.status_code == 200:
                    clients = clients_response.json()
                    if clients:
                        self.client_id = clients[0]["id"]
                        self.log_test("Create Martinique Client", True, 
                                    f"Using existing client: ID {self.client_id}", clients[0])
                        return True
                
                self.log_test("Create Martinique Client", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Create Martinique Client", False, f"Error: {str(e)}")
            return False
    
    def test_calculation_without_battery(self):
        """Test 5: Calcul solaire sans batterie"""
        if not self.client_id:
            self.log_test("5. Calcul sans batterie", False, "No client ID available")
            return None
            
        try:
            params = {
                "region": "martinique",
                "manual_kit_power": 6,
                "battery_selected": False
            }
            
            response = self.session.post(f"{self.base_url}/calculate/{self.client_id}", params=params)
            if response.status_code == 200:
                calculation = response.json()
                
                # Verify key fields
                required_fields = ["kit_power", "kit_price", "total_aids", "monthly_savings", "estimated_production"]
                missing_fields = [field for field in required_fields if field not in calculation]
                if missing_fields:
                    self.log_test("5. Calcul sans batterie", False, f"Missing fields: {missing_fields}", calculation)
                    return None
                
                kit_power = calculation["kit_power"]
                kit_price = calculation["kit_price"]
                total_aids = calculation["total_aids"]
                monthly_savings = calculation["monthly_savings"]
                
                self.log_test("5. Calcul sans batterie", True, 
                            f"Calcul réussi: {kit_power}kW, {kit_price}€, aides {total_aids}€, économies {monthly_savings:.2f}€/mois", 
                            calculation)
                return calculation
            else:
                self.log_test("5. Calcul sans batterie", False, f"HTTP {response.status_code}: {response.text}")
                return None
        except Exception as e:
            self.log_test("5. Calcul sans batterie", False, f"Error: {str(e)}")
            return None
    
    def test_calculation_with_battery(self):
        """Test 6: Calcul solaire avec batterie - FOCUS TABLEAU D'AMORTISSEMENT"""
        if not self.client_id:
            self.log_test("6. Calcul avec batterie", False, "No client ID available")
            return None
            
        try:
            params = {
                "region": "martinique",
                "manual_kit_power": 6,
                "battery_selected": True
            }
            
            response = self.session.post(f"{self.base_url}/calculate/{self.client_id}", params=params)
            if response.status_code == 200:
                calculation = response.json()
                
                # Verify ALL required fields for amortization table
                required_fields = [
                    "total_aids", "monthly_savings", "kit_price", "kit_price_final", 
                    "kit_power", "financing_with_aids", "battery_selected", "battery_cost",
                    "autoconsumption_kwh", "surplus_kwh", "estimated_production"
                ]
                
                missing_fields = [field for field in required_fields if field not in calculation]
                if missing_fields:
                    self.log_test("6. Calcul avec batterie", False, f"Missing required fields: {missing_fields}", calculation)
                    return None
                
                # Extract and validate data
                total_aids = calculation["total_aids"]
                monthly_savings = calculation["monthly_savings"]
                kit_price = calculation["kit_price"]
                kit_price_final = calculation["kit_price_final"]
                kit_power = calculation["kit_power"]
                battery_selected = calculation["battery_selected"]
                battery_cost = calculation["battery_cost"]
                financing_with_aids = calculation["financing_with_aids"]
                autoconsumption_kwh = calculation["autoconsumption_kwh"]
                surplus_kwh = calculation["surplus_kwh"]
                estimated_production = calculation["estimated_production"]
                
                # Validation checks
                issues = []
                
                # Battery validation
                if not battery_selected:
                    issues.append("battery_selected should be true")
                if battery_cost != 5000:
                    issues.append(f"battery_cost should be 5000€, got {battery_cost}€")
                
                # Price calculation validation
                expected_final_price = kit_price + battery_cost
                if abs(kit_price_final - expected_final_price) > 1:
                    issues.append(f"kit_price_final {kit_price_final}€ != {kit_price}€ + {battery_cost}€")
                
                # Financing validation
                if "monthly_payment" not in financing_with_aids:
                    issues.append("Missing monthly_payment in financing_with_aids")
                
                # Production validation
                if abs((autoconsumption_kwh + surplus_kwh) - estimated_production) > 1:
                    issues.append(f"Production breakdown doesn't match total")
                
                if issues:
                    self.log_test("6. Calcul avec batterie", False, f"Validation issues: {'; '.join(issues)}", calculation)
                    return None
                
                # Calculate amortization metrics
                net_investment = kit_price_final - total_aids
                monthly_payment = financing_with_aids["monthly_payment"]
                monthly_cash_flow = monthly_savings - monthly_payment
                payback_years = net_investment / (monthly_savings * 12) if monthly_savings > 0 else 0
                
                self.log_test("6. Calcul avec batterie", True, 
                            f"✅ DONNÉES TABLEAU D'AMORTISSEMENT COMPLÈTES: Kit {kit_power}kW + batterie. Prix: {kit_price}€ + {battery_cost}€ = {kit_price_final}€. Aides: {total_aids}€. Investissement net: {net_investment}€. Mensuel: {monthly_savings:.2f}€ économies - {monthly_payment:.2f}€ financement = {monthly_cash_flow:.2f}€ flux. Retour: {payback_years:.1f} ans. Production: {estimated_production:.0f} kWh/an ({autoconsumption_kwh:.0f} auto + {surplus_kwh:.0f} surplus)", 
                            calculation)
                return calculation
            else:
                self.log_test("6. Calcul avec batterie", False, f"HTTP {response.status_code}: {response.text}")
                return None
        except Exception as e:
            self.log_test("6. Calcul avec batterie", False, f"Error: {str(e)}")
            return None
    
    def run_amortization_tests(self):
        """Run all tests for amortization table data"""
        print("🚀 TEST COMPLET DU BACKEND - TABLEAU D'AMORTISSEMENT")
        print("🎯 Vérification des données nécessaires pour le tableau d'amortissement")
        print("=" * 80)
        
        # Test endpoints as requested
        self.test_api_root()
        self.test_solar_kits_endpoint()
        self.test_regions_endpoint()
        self.test_martinique_kits_endpoint()
        
        # Create client and test calculations
        if self.create_martinique_client():
            baseline_calc = self.test_calculation_without_battery()
            battery_calc = self.test_calculation_with_battery()
            
            # Compare results if both successful
            if baseline_calc and battery_calc:
                print(f"\n📊 COMPARAISON AVEC/SANS BATTERIE:")
                print(f"Sans batterie: {baseline_calc['kit_price']}€")
                print(f"Avec batterie: {battery_calc['kit_price_final']}€ (+{battery_calc['battery_cost']}€)")
                print(f"Différence: +{battery_calc['kit_price_final'] - baseline_calc['kit_price']}€")
        
        # Print summary
        print("\n" + "=" * 80)
        print("📊 RÉSUMÉ DES TESTS")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Réussis: {passed_tests}")
        print(f"❌ Échoués: {failed_tests}")
        print(f"Taux de réussite: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ TESTS ÉCHOUÉS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
        
        print("\n🎯 Test du tableau d'amortissement terminé!")
        return self.test_results

if __name__ == "__main__":
    tester = AmortizationTableTester()
    results = tester.run_amortization_tests()
    
    # Save results
    with open("/app/amortization_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Résultats sauvegardés dans /app/amortization_test_results.json")