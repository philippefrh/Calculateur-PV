#!/usr/bin/env python3
"""
Comprehensive Professional Version Testing for Solar Calculator
Tests all professional features with real data from the professional table
"""

import requests
import json
import time
from typing import Dict, Any, Optional

# Backend URL from frontend environment
BACKEND_URL = "https://b3e4f691-e66b-445a-8707-3eb34141dcd9.preview.emergentagent.com/api"

class ProfessionalVersionTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.professional_client_id = None
        self.particuliers_client_id = None
        
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

    def test_professional_kits_real_data(self):
        """Test professional kits endpoint with real data from the professional table"""
        try:
            response = self.session.get(f"{self.base_url}/solar-kits/professionnels")
            if response.status_code == 200:
                kits = response.json()
                
                # Test specific kits mentioned in the review request
                test_cases = [
                    {"power": 10, "expected_panels": 24, "expected_prime": 1900},
                    {"power": 15, "expected_panels": 36, "expected_prime": 2850},
                    {"power": 20, "expected_panels": 48, "expected_prime": 3800},
                    {"power": 36, "expected_panels": 86, "expected_prime": 6840}
                ]
                
                issues = []
                verified_kits = []
                
                for test_case in test_cases:
                    power = test_case["power"]
                    kit = kits.get(str(power))
                    
                    if not kit:
                        issues.append(f"Missing {power}kW kit")
                        continue
                    
                    # Check structure
                    required_fields = ["panels", "surface", "prime", "tarif_rachat_surplus", 
                                     "tarif_base_ht", "tarif_remise_ht", "tarif_remise_max_ht",
                                     "commission_normale", "commission_remise_max"]
                    
                    missing_fields = [field for field in required_fields if field not in kit]
                    if missing_fields:
                        issues.append(f"{power}kW kit missing fields: {missing_fields}")
                        continue
                    
                    # Verify specific values
                    if kit["panels"] != test_case["expected_panels"]:
                        issues.append(f"{power}kW kit has {kit['panels']} panels, expected {test_case['expected_panels']}")
                    
                    if kit["prime"] != test_case["expected_prime"]:
                        issues.append(f"{power}kW kit has {kit['prime']}€ prime, expected {test_case['expected_prime']}€")
                    
                    # Check tarif_rachat_surplus (should be 0.0761€/kWh for all)
                    if kit["tarif_rachat_surplus"] != 0.0761:
                        issues.append(f"{power}kW kit has {kit['tarif_rachat_surplus']}€/kWh surplus rate, expected 0.0761€/kWh")
                    
                    # Verify pricing structure (remise < base, remise_max < remise)
                    if kit["tarif_remise_ht"] >= kit["tarif_base_ht"]:
                        issues.append(f"{power}kW kit: remise price {kit['tarif_remise_ht']}€ should be < base price {kit['tarif_base_ht']}€")
                    
                    if kit["tarif_remise_max_ht"] >= kit["tarif_remise_ht"]:
                        issues.append(f"{power}kW kit: remise_max price {kit['tarif_remise_max_ht']}€ should be < remise price {kit['tarif_remise_ht']}€")
                    
                    verified_kits.append({
                        "power": power,
                        "panels": kit["panels"],
                        "prime": kit["prime"],
                        "tarif_base_ht": kit["tarif_base_ht"],
                        "tarif_remise_ht": kit["tarif_remise_ht"],
                        "tarif_remise_max_ht": kit["tarif_remise_max_ht"]
                    })
                
                # Check range (10kW to 36kW)
                available_powers = [int(k) for k in kits.keys()]
                min_power = min(available_powers)
                max_power = max(available_powers)
                
                if min_power != 10:
                    issues.append(f"Minimum power should be 10kW, got {min_power}kW")
                if max_power != 36:
                    issues.append(f"Maximum power should be 36kW, got {max_power}kW")
                
                if issues:
                    self.log_test("Professional Kits Real Data", False, f"Issues: {'; '.join(issues)}", verified_kits)
                else:
                    self.log_test("Professional Kits Real Data", True, 
                                f"✅ Professional kits verified: 10-36kW range, 15kW has {verified_kits[1]['panels']} panels and {verified_kits[1]['prime']}€ prime as expected", 
                                verified_kits)
            else:
                self.log_test("Professional Kits Real Data", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Professional Kits Real Data", False, f"Error: {str(e)}")

    def test_professional_calculation_endpoint_base(self):
        """Test professional calculation endpoint with base price level"""
        # First create a professional client
        try:
            client_data = {
                "first_name": "Entreprise",
                "last_name": "Test",
                "address": "10 Avenue des Champs-Élysées, 75008 Paris",
                "roof_surface": 150.0,
                "roof_orientation": "Sud",
                "velux_count": 0,
                "heating_system": "Pompe à chaleur",
                "water_heating_system": "Solaire thermique",
                "water_heating_capacity": 500,
                "annual_consumption_kwh": 15000.0,
                "monthly_edf_payment": 450.0,
                "annual_edf_payment": 5400.0,
                "client_mode": "professionnels"
            }
            
            client_response = self.session.post(f"{self.base_url}/clients", json=client_data)
            if client_response.status_code != 200:
                self.log_test("Professional Calculation Base", False, f"Failed to create client: {client_response.status_code}")
                return
            
            client = client_response.json()
            self.professional_client_id = client["id"]
            
            # Test calculation with base price level
            response = self.session.post(f"{self.base_url}/calculate-professional/{self.professional_client_id}?price_level=base")
            if response.status_code == 200:
                calculation = response.json()
                
                # Check required fields
                required_fields = [
                    "client_id", "client_mode", "price_level", "kit_power", "panel_count",
                    "estimated_production", "estimated_savings", "autonomy_percentage",
                    "monthly_savings", "kit_price", "commission", "autoconsumption_kwh",
                    "surplus_kwh", "autoconsumption_aid", "total_aids", "pricing_options"
                ]
                
                missing_fields = [field for field in required_fields if field not in calculation]
                if missing_fields:
                    self.log_test("Professional Calculation Base", False, f"Missing fields: {missing_fields}", calculation)
                    return
                
                # Verify professional-specific values
                issues = []
                
                if calculation["client_mode"] != "professionnels":
                    issues.append(f"Client mode should be 'professionnels', got '{calculation['client_mode']}'")
                
                if calculation["price_level"] != "base":
                    issues.append(f"Price level should be 'base', got '{calculation['price_level']}'")
                
                # Check professional rates (80% autoconsumption, 0.26€/kWh EDF, 0.0761€/kWh surplus)
                autoconsumption_kwh = calculation["autoconsumption_kwh"]
                surplus_kwh = calculation["surplus_kwh"]
                estimated_production = calculation["estimated_production"]
                
                expected_autoconsumption = estimated_production * 0.80
                expected_surplus = estimated_production * 0.20
                
                if abs(autoconsumption_kwh - expected_autoconsumption) > 10:
                    issues.append(f"Autoconsumption {autoconsumption_kwh:.0f} kWh != 80% of {estimated_production:.0f} kWh = {expected_autoconsumption:.0f} kWh")
                
                if abs(surplus_kwh - expected_surplus) > 10:
                    issues.append(f"Surplus {surplus_kwh:.0f} kWh != 20% of {estimated_production:.0f} kWh = {expected_surplus:.0f} kWh")
                
                # Check pricing options structure
                pricing_options = calculation["pricing_options"]
                required_pricing_fields = ["tarif_base_ht", "tarif_remise_ht", "tarif_remise_max_ht", 
                                         "commission_normale", "commission_remise_max"]
                
                missing_pricing_fields = [field for field in required_pricing_fields if field not in pricing_options]
                if missing_pricing_fields:
                    issues.append(f"Missing pricing options fields: {missing_pricing_fields}")
                
                # Verify kit_price matches tarif_base_ht
                if abs(calculation["kit_price"] - pricing_options["tarif_base_ht"]) > 1:
                    issues.append(f"Kit price {calculation['kit_price']}€ != tarif_base_ht {pricing_options['tarif_base_ht']}€")
                
                if issues:
                    self.log_test("Professional Calculation Base", False, f"Issues: {'; '.join(issues)}", calculation)
                else:
                    self.log_test("Professional Calculation Base", True, 
                                f"✅ Professional calculation (base) working: {calculation['kit_power']}kW, 80% autoconsumption ({autoconsumption_kwh:.0f} kWh), price {calculation['kit_price']}€ HT", 
                                calculation)
            else:
                self.log_test("Professional Calculation Base", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Professional Calculation Base", False, f"Error: {str(e)}")

    def test_professional_calculation_price_levels(self):
        """Test professional calculation with different price levels"""
        if not self.professional_client_id:
            self.log_test("Professional Price Levels", False, "No professional client ID available")
            return
        
        try:
            price_levels = ["base", "remise", "remise_max"]
            calculations = {}
            
            for price_level in price_levels:
                response = self.session.post(f"{self.base_url}/calculate-professional/{self.professional_client_id}?price_level={price_level}")
                if response.status_code == 200:
                    calculations[price_level] = response.json()
                else:
                    self.log_test("Professional Price Levels", False, f"Failed to get {price_level} calculation: {response.status_code}")
                    return
            
            # Verify price differences
            issues = []
            
            base_price = calculations["base"]["kit_price"]
            remise_price = calculations["remise"]["kit_price"]
            remise_max_price = calculations["remise_max"]["kit_price"]
            
            base_commission = calculations["base"]["commission"]
            remise_commission = calculations["remise"]["commission"]
            remise_max_commission = calculations["remise_max"]["commission"]
            
            # Check price order: remise_max < remise < base
            if remise_price >= base_price:
                issues.append(f"Remise price {remise_price}€ should be < base price {base_price}€")
            
            if remise_max_price >= remise_price:
                issues.append(f"Remise max price {remise_max_price}€ should be < remise price {remise_price}€")
            
            # Check commission differences
            if remise_max_commission >= base_commission:
                issues.append(f"Remise max commission {remise_max_commission}€ should be < base commission {base_commission}€")
            
            # Verify all calculations have same technical specs but different pricing
            for field in ["kit_power", "panel_count", "estimated_production", "estimated_savings"]:
                values = [calculations[level][field] for level in price_levels]
                if not all(abs(v - values[0]) < 1 for v in values):
                    issues.append(f"Technical field {field} should be same across price levels: {values}")
            
            if issues:
                self.log_test("Professional Price Levels", False, f"Issues: {'; '.join(issues)}", calculations)
            else:
                price_savings = base_price - remise_max_price
                commission_reduction = base_commission - remise_max_commission
                self.log_test("Professional Price Levels", True, 
                            f"✅ Price levels working: Base {base_price}€ > Remise {remise_price}€ > Remise Max {remise_max_price}€ (saves {price_savings}€). Commission: {base_commission}€ > {remise_max_commission}€ (reduces {commission_reduction}€)", 
                            {level: {"price": calculations[level]["kit_price"], "commission": calculations[level]["commission"]} for level in price_levels})
            
        except Exception as e:
            self.log_test("Professional Price Levels", False, f"Error: {str(e)}")

    def test_professional_vs_particuliers_rates(self):
        """Test comparison of professional vs particuliers calculation rates"""
        # Create a particuliers client with similar profile
        try:
            particuliers_data = {
                "first_name": "Particulier",
                "last_name": "Test",
                "address": "15 Rue de Rivoli, 75001 Paris",
                "roof_surface": 150.0,
                "roof_orientation": "Sud",
                "velux_count": 0,
                "heating_system": "Pompe à chaleur",
                "water_heating_system": "Solaire thermique",
                "water_heating_capacity": 500,
                "annual_consumption_kwh": 15000.0,
                "monthly_edf_payment": 450.0,
                "annual_edf_payment": 5400.0,
                "client_mode": "particuliers"
            }
            
            client_response = self.session.post(f"{self.base_url}/clients", json=particuliers_data)
            if client_response.status_code != 200:
                self.log_test("Professional vs Particuliers Rates", False, f"Failed to create particuliers client: {client_response.status_code}")
                return
            
            particuliers_client = client_response.json()
            self.particuliers_client_id = particuliers_client["id"]
            
            # Get calculations for both
            part_response = self.session.post(f"{self.base_url}/calculate/{self.particuliers_client_id}")
            prof_response = self.session.post(f"{self.base_url}/calculate/{self.professional_client_id}")
            
            if part_response.status_code != 200 or prof_response.status_code != 200:
                self.log_test("Professional vs Particuliers Rates", False, f"Failed to get calculations: Part {part_response.status_code}, Prof {prof_response.status_code}")
                return
            
            part_calc = part_response.json()
            prof_calc = prof_response.json()
            
            # Compare rates
            issues = []
            
            # Autoconsumption rates
            part_aids = part_calc.get("aids_config", {})
            prof_aids = prof_calc.get("aids_config", {})
            
            part_autoconsumption_rate = part_aids.get("autoconsumption_rate", 0)
            prof_autoconsumption_rate = prof_aids.get("autoconsumption_rate", 0)
            
            if part_autoconsumption_rate != 0.95:
                issues.append(f"Particuliers autoconsumption rate should be 95%, got {part_autoconsumption_rate*100:.0f}%")
            
            if prof_autoconsumption_rate != 0.80:
                issues.append(f"Professionnels autoconsumption rate should be 80%, got {prof_autoconsumption_rate*100:.0f}%")
            
            # EDF rates
            part_edf_rate = part_aids.get("edf_rate", 0)
            prof_edf_rate = prof_aids.get("edf_rate", 0)
            
            if part_edf_rate != 0.2516:
                issues.append(f"Particuliers EDF rate should be 0.2516€/kWh, got {part_edf_rate}€/kWh")
            
            if prof_edf_rate != 0.26:
                issues.append(f"Professionnels EDF rate should be 0.26€/kWh, got {prof_edf_rate}€/kWh")
            
            # Surplus rates
            part_surplus_rate = part_aids.get("surplus_sale_rate", 0)
            prof_surplus_rate = prof_aids.get("surplus_sale_rate", 0)
            
            if part_surplus_rate != 0.076:
                issues.append(f"Particuliers surplus rate should be 0.076€/kWh, got {part_surplus_rate}€/kWh")
            
            if prof_surplus_rate != 0.0761:
                issues.append(f"Professionnels surplus rate should be 0.0761€/kWh, got {prof_surplus_rate}€/kWh")
            
            # Aid rates (prime calculation)
            part_aid_rate = part_aids.get("autoconsumption_aid_rate", 0)
            prof_aid_rate = prof_aids.get("autoconsumption_aid_rate", 0)
            
            if part_aid_rate != 80:
                issues.append(f"Particuliers aid rate should be 80€/kW, got {part_aid_rate}€/kW")
            
            if prof_aid_rate != 190:  # Professional aid rate from backend
                issues.append(f"Professionnels aid rate should be 190€/kW, got {prof_aid_rate}€/kW")
            
            if issues:
                self.log_test("Professional vs Particuliers Rates", False, f"Rate comparison issues: {'; '.join(issues)}")
            else:
                self.log_test("Professional vs Particuliers Rates", True, 
                            f"✅ Rate comparison verified: Autoconsumption (Part: 95% vs Prof: 80%), EDF (Part: 0.2516€ vs Prof: 0.26€), Surplus (Part: 0.076€ vs Prof: 0.0761€), Aid (Part: 80€/kW vs Prof: 190€/kW)", 
                            {
                                "particuliers": {
                                    "autoconsumption_rate": part_autoconsumption_rate,
                                    "edf_rate": part_edf_rate,
                                    "surplus_rate": part_surplus_rate,
                                    "aid_rate": part_aid_rate
                                },
                                "professionnels": {
                                    "autoconsumption_rate": prof_autoconsumption_rate,
                                    "edf_rate": prof_edf_rate,
                                    "surplus_rate": prof_surplus_rate,
                                    "aid_rate": prof_aid_rate
                                }
                            })
            
        except Exception as e:
            self.log_test("Professional vs Particuliers Rates", False, f"Error: {str(e)}")

    def test_professional_prime_calculation(self):
        """Test that professional prime comes directly from the table (not calculated)"""
        if not self.professional_client_id:
            self.log_test("Professional Prime Calculation", False, "No professional client ID available")
            return
        
        try:
            # Test with different price levels to ensure prime is consistent
            response = self.session.post(f"{self.base_url}/calculate-professional/{self.professional_client_id}?price_level=base")
            if response.status_code != 200:
                self.log_test("Professional Prime Calculation", False, f"Failed to get calculation: {response.status_code}")
                return
            
            calculation = response.json()
            kit_power = calculation["kit_power"]
            autoconsumption_aid = calculation["autoconsumption_aid"]
            
            # Get the kit data to verify prime
            kits_response = self.session.get(f"{self.base_url}/solar-kits/professionnels")
            if kits_response.status_code != 200:
                self.log_test("Professional Prime Calculation", False, f"Failed to get kits: {kits_response.status_code}")
                return
            
            kits = kits_response.json()
            kit_info = kits.get(str(kit_power))
            
            if not kit_info:
                self.log_test("Professional Prime Calculation", False, f"Kit {kit_power}kW not found in professional kits")
                return
            
            expected_prime = kit_info["prime"]
            
            # Verify that autoconsumption_aid matches the prime from the table (not calculated)
            if abs(autoconsumption_aid - expected_prime) > 1:
                self.log_test("Professional Prime Calculation", False, 
                            f"Autoconsumption aid {autoconsumption_aid}€ != table prime {expected_prime}€ for {kit_power}kW kit")
                return
            
            # Verify it's NOT calculated as kit_power * rate
            calculated_aid = kit_power * 190  # 190€/kW rate
            if abs(autoconsumption_aid - calculated_aid) < 10:  # If it's close to calculated value
                self.log_test("Professional Prime Calculation", False, 
                            f"Prime appears to be calculated ({autoconsumption_aid}€ ≈ {kit_power}kW × 190€/kW = {calculated_aid}€) instead of using table value {expected_prime}€")
                return
            
            self.log_test("Professional Prime Calculation", True, 
                        f"✅ Professional prime correctly uses table value: {kit_power}kW kit gets {autoconsumption_aid}€ prime (from table, not {calculated_aid}€ calculated)", 
                        {
                            "kit_power": kit_power,
                            "table_prime": expected_prime,
                            "actual_aid": autoconsumption_aid,
                            "calculated_would_be": calculated_aid
                        })
            
        except Exception as e:
            self.log_test("Professional Prime Calculation", False, f"Error: {str(e)}")

    def test_20kw_kit_example(self):
        """Test specific 20kW kit example as mentioned in review request"""
        try:
            # Get 20kW kit data
            response = self.session.get(f"{self.base_url}/solar-kits/professionnels")
            if response.status_code != 200:
                self.log_test("20kW Kit Example", False, f"Failed to get kits: {response.status_code}")
                return
            
            kits = response.json()
            kit_20 = kits.get("20")
            
            if not kit_20:
                self.log_test("20kW Kit Example", False, "20kW kit not found in professional kits")
                return
            
            # Verify 20kW kit specifications
            issues = []
            
            expected_values = {
                "panels": 48,
                "surface": 90,
                "prime": 3800,
                "tarif_rachat_surplus": 0.0761,
                "tarif_base_ht": 35600,
                "tarif_remise_ht": 34600,
                "tarif_remise_max_ht": 33600,
                "commission_normale": 3560,
                "commission_remise_max": 3060
            }
            
            for field, expected_value in expected_values.items():
                actual_value = kit_20.get(field)
                if actual_value != expected_value:
                    issues.append(f"{field}: got {actual_value}, expected {expected_value}")
            
            # Test commercial logic - price differences
            price_base = kit_20["tarif_base_ht"]
            price_remise = kit_20["tarif_remise_ht"]
            price_remise_max = kit_20["tarif_remise_max_ht"]
            
            remise_discount = price_base - price_remise
            remise_max_discount = price_base - price_remise_max
            
            if remise_discount <= 0:
                issues.append(f"Remise should provide discount: {price_base}€ - {price_remise}€ = {remise_discount}€")
            
            if remise_max_discount <= remise_discount:
                issues.append(f"Remise max should provide bigger discount: {remise_max_discount}€ <= {remise_discount}€")
            
            # Test commission logic
            commission_normal = kit_20["commission_normale"]
            commission_remise_max = kit_20["commission_remise_max"]
            
            commission_reduction = commission_normal - commission_remise_max
            if commission_reduction <= 0:
                issues.append(f"Commission should reduce with remise max: {commission_normal}€ - {commission_remise_max}€ = {commission_reduction}€")
            
            if issues:
                self.log_test("20kW Kit Example", False, f"20kW kit issues: {'; '.join(issues)}", kit_20)
            else:
                self.log_test("20kW Kit Example", True, 
                            f"✅ 20kW kit verified: {kit_20['panels']} panels, {kit_20['prime']}€ prime, pricing {price_base}€/{price_remise}€/{price_remise_max}€ (saves up to {remise_max_discount}€), commission {commission_normal}€/{commission_remise_max}€ (reduces {commission_reduction}€)", 
                            kit_20)
            
        except Exception as e:
            self.log_test("20kW Kit Example", False, f"Error: {str(e)}")

    def run_professional_tests(self):
        """Run all professional version tests"""
        print("🚀 Starting Professional Version Tests")
        print(f"Backend URL: {self.base_url}")
        print("=" * 80)
        
        # Test professional kits with real data
        self.test_professional_kits_real_data()
        
        # Test professional calculation endpoints
        self.test_professional_calculation_endpoint_base()
        self.test_professional_calculation_price_levels()
        
        # Test rate comparisons
        self.test_professional_vs_particuliers_rates()
        
        # Test prime calculation logic
        self.test_professional_prime_calculation()
        
        # Test specific examples
        self.test_20kw_kit_example()
        
        # Print summary
        print("\n" + "=" * 80)
        print("📊 PROFESSIONAL VERSION TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  • {result['test']}: {result['details']}")
        
        print("\n✅ PASSED TESTS:")
        for result in self.test_results:
            if result["success"]:
                print(f"  • {result['test']}")
        
        return passed_tests, failed_tests

if __name__ == "__main__":
    tester = ProfessionalVersionTester()
    passed, failed = tester.run_professional_tests()
    
    if failed == 0:
        print("\n🎉 ALL PROFESSIONAL VERSION TESTS PASSED!")
    else:
        print(f"\n⚠️  {failed} tests failed. Please check the issues above.")