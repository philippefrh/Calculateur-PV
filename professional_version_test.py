#!/usr/bin/env python3
"""
Professional Version Testing - Focused on core functionality
Tests the Professional Version implementation without relying on geocoding
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

    def get_existing_clients(self):
        """Get existing clients from database to use for testing"""
        try:
            response = self.session.get(f"{self.base_url}/clients")
            if response.status_code == 200:
                clients = response.json()
                # Filter for professional clients
                professional_clients = [c for c in clients if c.get('client_mode') == 'professionnels']
                particuliers_clients = [c for c in clients if c.get('client_mode') == 'particuliers']
                
                self.log_test("Get Existing Clients", True, 
                            f"Found {len(clients)} total clients: {len(professional_clients)} professional, {len(particuliers_clients)} particuliers")
                
                return {
                    'all': clients,
                    'professional': professional_clients,
                    'particuliers': particuliers_clients
                }
            else:
                self.log_test("Get Existing Clients", False, f"HTTP {response.status_code}: {response.text}")
                return None
        except Exception as e:
            self.log_test("Get Existing Clients", False, f"Error: {str(e)}")
            return None

    def test_professional_kits_structure(self):
        """Test that professional kits have the correct structure"""
        try:
            response = self.session.get(f"{self.base_url}/solar-kits/professionnels")
            if response.status_code == 200:
                kits = response.json()
                
                # Check if we have both small (3-9kW) and large (10-36kW) kits
                available_sizes = [int(k) for k in kits.keys()]
                small_kits = [s for s in available_sizes if 3 <= s <= 9]
                large_kits = [s for s in available_sizes if 10 <= s <= 36]
                
                issues = []
                
                # Check for small kits (3-9kW)
                expected_small = [3, 4, 5, 6, 7, 8, 9]
                missing_small = [s for s in expected_small if s not in small_kits]
                if missing_small:
                    issues.append(f"Missing small kits: {missing_small}")
                
                # Check for some large kits
                expected_large_samples = [12, 15, 20]
                missing_large = [s for s in expected_large_samples if s not in large_kits]
                if missing_large:
                    issues.append(f"Missing large kits: {missing_large}")
                
                # Check structure of a sample kit (6kW)
                if "6" in kits:
                    kit_6 = kits["6"]
                    required_fields = ["tarif_base_ht", "tarif_remise_ht", "tarif_remise_max_ht", "prime", "panels"]
                    missing_fields = [f for f in required_fields if f not in kit_6]
                    if missing_fields:
                        issues.append(f"6kW kit missing fields: {missing_fields}")
                
                # Check structure of a large kit (15kW)
                if "15" in kits:
                    kit_15 = kits["15"]
                    required_fields = ["tarif_base_ht", "tarif_remise_ht", "tarif_remise_max_ht", "prime", "panels"]
                    missing_fields = [f for f in required_fields if f not in kit_15]
                    if missing_fields:
                        issues.append(f"15kW kit missing fields: {missing_fields}")
                
                if issues:
                    self.log_test("Professional Kits Structure", False, f"Structure issues: {'; '.join(issues)}")
                else:
                    kit_6 = kits.get("6", {})
                    kit_15 = kits.get("15", {})
                    self.log_test("Professional Kits Structure", True, 
                                f"✅ Professional kits structure correct. Small kits: {len(small_kits)}, Large kits: {len(large_kits)}. "
                                f"6kW: base {kit_6.get('tarif_base_ht')}€, prime {kit_6.get('prime')}€. "
                                f"15kW: base {kit_15.get('tarif_base_ht')}€, prime {kit_15.get('prime')}€")
                    
                    return kits
            else:
                self.log_test("Professional Kits Structure", False, f"HTTP {response.status_code}: {response.text}")
                return None
        except Exception as e:
            self.log_test("Professional Kits Structure", False, f"Error: {str(e)}")
            return None

    def test_professional_calculation_endpoint(self, client_id: str):
        """Test the professional calculation endpoint with all price levels"""
        try:
            price_levels = ["base", "remise", "remise_max"]
            results = {}
            
            for price_level in price_levels:
                response = self.session.post(f"{self.base_url}/calculate-professional/{client_id}", 
                                           params={"price_level": price_level})
                
                if response.status_code == 200:
                    calculation = response.json()
                    results[price_level] = calculation
                else:
                    self.log_test("Professional Calculation Endpoint", False, 
                                f"Failed for price level {price_level}: HTTP {response.status_code}")
                    return None
            
            # Verify all calculations succeeded
            issues = []
            
            # Check required fields
            for price_level, calc in results.items():
                required_fields = ["kit_power", "kit_price", "leasing_options", "monthly_savings", 
                                 "commission", "price_level", "client_mode", "aids_config"]
                missing_fields = [f for f in required_fields if f not in calc]
                if missing_fields:
                    issues.append(f"{price_level}: missing {missing_fields}")
                
                # Check client mode is professional
                if calc.get("client_mode") != "professionnels":
                    issues.append(f"{price_level}: client_mode should be 'professionnels'")
                
                # Check price level matches
                if calc.get("price_level") != price_level:
                    issues.append(f"{price_level}: price_level mismatch")
            
            # Check price progression: base > remise > remise_max
            if len(results) == 3:
                base_price = results["base"].get("kit_price", 0)
                remise_price = results["remise"].get("kit_price", 0)
                remise_max_price = results["remise_max"].get("kit_price", 0)
                
                if not (base_price > remise_price > remise_max_price):
                    issues.append(f"Price progression incorrect: {base_price} > {remise_price} > {remise_max_price}")
            
            # Check professional rates (80% autoconsumption, 0.26€/kWh EDF)
            base_calc = results.get("base", {})
            aids_config = base_calc.get("aids_config", {})
            
            if aids_config.get("autoconsumption_rate") != 0.80:
                issues.append(f"Autoconsumption rate should be 80%, got {aids_config.get('autoconsumption_rate', 0)*100}%")
            
            if abs(aids_config.get("edf_rate", 0) - 0.26) > 0.001:
                issues.append(f"EDF rate should be 0.26€/kWh, got {aids_config.get('edf_rate')}€/kWh")
            
            if issues:
                self.log_test("Professional Calculation Endpoint", False, f"Issues: {'; '.join(issues)}")
                return None
            else:
                base_calc = results["base"]
                self.log_test("Professional Calculation Endpoint", True, 
                            f"✅ All 3 price levels working. Kit: {base_calc.get('kit_power')}kW, "
                            f"Prices: {base_price}€ > {remise_price}€ > {remise_max_price}€, "
                            f"80% autoconsumption, 0.26€/kWh EDF rate")
                return results
                
        except Exception as e:
            self.log_test("Professional Calculation Endpoint", False, f"Error: {str(e)}")
            return None

    def test_leasing_matrix_functionality(self, calculation_results: dict):
        """Test leasing matrix functionality from calculation results"""
        try:
            if not calculation_results:
                self.log_test("Leasing Matrix Functionality", False, "No calculation results provided")
                return
            
            base_calc = calculation_results.get("base", {})
            leasing_options = base_calc.get("leasing_options", [])
            
            if not leasing_options:
                self.log_test("Leasing Matrix Functionality", False, "No leasing options found")
                return
            
            issues = []
            
            # Check that we have multiple duration options
            durations = [opt.get("duration_months") for opt in leasing_options]
            expected_durations = [60, 72, 84, 96]
            available_durations = [d for d in expected_durations if d in durations]
            
            if len(available_durations) < 2:
                issues.append(f"Too few duration options: {available_durations}")
            
            # Check rate ranges (should be 1-3%)
            for option in leasing_options:
                rate = option.get("rate", 0)
                if not (1.0 <= rate <= 3.0):
                    issues.append(f"Rate {rate}% outside expected range 1-3%")
                
                # Check monthly payment calculation
                monthly_payment = option.get("monthly_payment", 0)
                kit_price = base_calc.get("kit_price", 0)
                expected_payment = kit_price * (rate / 100)
                
                if abs(monthly_payment - expected_payment) > 10:  # 10€ tolerance
                    issues.append(f"Payment calculation error: {monthly_payment}€ vs expected {expected_payment:.2f}€")
            
            # Test specific examples from review request
            # 25,000€/72 months should be around 1.77% rate
            kit_price = base_calc.get("kit_price", 0)
            if 20000 <= kit_price <= 30000:
                option_72 = next((opt for opt in leasing_options if opt.get("duration_months") == 72), None)
                if option_72:
                    rate_72 = option_72.get("rate", 0)
                    if not (1.7 <= rate_72 <= 1.8):
                        issues.append(f"72-month rate {rate_72}% not in expected range 1.7-1.8% for ~25k€")
            
            if issues:
                self.log_test("Leasing Matrix Functionality", False, f"Matrix issues: {'; '.join(issues)}")
            else:
                rate_range = f"{min(opt['rate'] for opt in leasing_options):.2f}%-{max(opt['rate'] for opt in leasing_options):.2f}%"
                duration_range = f"{min(durations)}-{max(durations)} months"
                
                self.log_test("Leasing Matrix Functionality", True, 
                            f"✅ Leasing matrix working: {len(leasing_options)} options, "
                            f"rates {rate_range}, durations {duration_range}")
                
        except Exception as e:
            self.log_test("Leasing Matrix Functionality", False, f"Error: {str(e)}")

    def test_optimal_kit_algorithm(self, calculation_results: dict):
        """Test the optimal kit finding algorithm"""
        try:
            if not calculation_results:
                self.log_test("Optimal Kit Algorithm", False, "No calculation results provided")
                return
            
            optimal_results = {}
            
            for price_level, calc in calculation_results.items():
                optimal_kit = calc.get("optimal_kit")
                monthly_savings = calc.get("monthly_savings", 0)
                
                if optimal_kit:
                    monthly_payment = optimal_kit.get("monthly_payment", 0)
                    monthly_benefit = optimal_kit.get("monthly_benefit", 0)
                    kit_power = optimal_kit.get("kit_power", 0)
                    
                    optimal_results[price_level] = {
                        "found": True,
                        "kit_power": kit_power,
                        "monthly_payment": monthly_payment,
                        "monthly_savings": monthly_savings,
                        "monthly_benefit": monthly_benefit,
                        "is_profitable": monthly_payment <= monthly_savings and monthly_benefit >= 0
                    }
                else:
                    optimal_results[price_level] = {
                        "found": False,
                        "monthly_savings": monthly_savings
                    }
            
            # Analyze results
            issues = []
            found_count = sum(1 for r in optimal_results.values() if r.get("found", False))
            profitable_count = sum(1 for r in optimal_results.values() if r.get("is_profitable", False))
            
            if found_count == 0:
                issues.append("No optimal kits found for any price level")
            
            # Check that better price levels give better results
            if optimal_results.get("base", {}).get("found") and optimal_results.get("remise_max", {}).get("found"):
                base_benefit = optimal_results["base"].get("monthly_benefit", 0)
                remise_max_benefit = optimal_results["remise_max"].get("monthly_benefit", 0)
                
                if remise_max_benefit <= base_benefit:
                    issues.append(f"Remise_max benefit {remise_max_benefit}€ should be > base benefit {base_benefit}€")
            
            if issues:
                self.log_test("Optimal Kit Algorithm", False, f"Algorithm issues: {'; '.join(issues)}")
            else:
                summary_parts = []
                for price_level, result in optimal_results.items():
                    if result.get("found"):
                        summary_parts.append(f"{price_level}: {result['kit_power']}kW, {result['monthly_benefit']:.0f}€ benefit")
                    else:
                        summary_parts.append(f"{price_level}: no optimal kit")
                
                self.log_test("Optimal Kit Algorithm", True, 
                            f"✅ Algorithm working: {found_count}/3 optimal kits found, {profitable_count} profitable. {'; '.join(summary_parts)}")
                
        except Exception as e:
            self.log_test("Optimal Kit Algorithm", False, f"Error: {str(e)}")

    def test_professional_vs_particuliers_rates(self, professional_client_id: str, particuliers_client_id: str):
        """Test rate differences between professional and particuliers modes"""
        try:
            # Get professional calculation
            prof_response = self.session.post(f"{self.base_url}/calculate-professional/{professional_client_id}")
            if prof_response.status_code != 200:
                self.log_test("Professional vs Particuliers Rates", False, "Failed to get professional calculation")
                return
            
            # Get particuliers calculation
            part_response = self.session.post(f"{self.base_url}/calculate/{particuliers_client_id}")
            if part_response.status_code != 200:
                self.log_test("Professional vs Particuliers Rates", False, "Failed to get particuliers calculation")
                return
            
            prof_calc = prof_response.json()
            part_calc = part_response.json()
            
            # Compare aids configurations
            prof_aids = prof_calc.get("aids_config", {})
            part_aids = part_calc.get("aids_config", {})
            
            issues = []
            
            # Check autoconsumption rates
            prof_auto_rate = prof_aids.get("autoconsumption_rate", 0)
            part_auto_rate = part_aids.get("autoconsumption_rate", 0)
            
            if prof_auto_rate != 0.80:
                issues.append(f"Professional autoconsumption should be 80%, got {prof_auto_rate*100}%")
            if part_auto_rate != 0.95:
                issues.append(f"Particuliers autoconsumption should be 95%, got {part_auto_rate*100}%")
            
            # Check EDF rates
            prof_edf_rate = prof_aids.get("edf_rate", 0)
            part_edf_rate = part_aids.get("edf_rate", 0)
            
            if abs(prof_edf_rate - 0.26) > 0.001:
                issues.append(f"Professional EDF rate should be 0.26€/kWh, got {prof_edf_rate}€/kWh")
            if abs(part_edf_rate - 0.2516) > 0.001:
                issues.append(f"Particuliers EDF rate should be 0.2516€/kWh, got {part_edf_rate}€/kWh")
            
            # Check aid rates
            prof_aid_rate = prof_aids.get("autoconsumption_aid_rate", 0)
            part_aid_rate = part_aids.get("autoconsumption_aid_rate", 0)
            
            if prof_aid_rate != 190:
                issues.append(f"Professional aid rate should be 190€/kW, got {prof_aid_rate}€/kW")
            if part_aid_rate != 80:
                issues.append(f"Particuliers aid rate should be 80€/kW, got {part_aid_rate}€/kW")
            
            # Check financing types
            prof_has_leasing = "leasing_options" in prof_calc
            part_has_financing = "financing_with_aids" in part_calc
            
            if not prof_has_leasing:
                issues.append("Professional should have leasing_options")
            if not part_has_financing:
                issues.append("Particuliers should have financing_with_aids")
            
            if issues:
                self.log_test("Professional vs Particuliers Rates", False, f"Rate comparison issues: {'; '.join(issues)}")
            else:
                self.log_test("Professional vs Particuliers Rates", True, 
                            f"✅ Rate differences correct: "
                            f"Autoconsumption: Prof {prof_auto_rate*100:.0f}% vs Part {part_auto_rate*100:.0f}%. "
                            f"EDF rates: Prof {prof_edf_rate}€/kWh vs Part {part_edf_rate}€/kWh. "
                            f"Aid rates: Prof {prof_aid_rate}€/kW vs Part {part_aid_rate}€/kW. "
                            f"Financing: Prof leasing vs Part credit")
                
        except Exception as e:
            self.log_test("Professional vs Particuliers Rates", False, f"Error: {str(e)}")

    def run_professional_tests(self):
        """Run all professional version tests"""
        print("🏢 PROFESSIONAL VERSION COMPREHENSIVE TESTING")
        print("=" * 60)
        
        # Get existing clients to work with
        clients_data = self.get_existing_clients()
        if not clients_data:
            print("❌ Cannot proceed without existing clients")
            return
        
        professional_clients = clients_data['professional']
        particuliers_clients = clients_data['particuliers']
        
        if not professional_clients:
            print("❌ No professional clients found in database")
            return
        
        if not particuliers_clients:
            print("❌ No particuliers clients found in database")
            return
        
        # Test 1: Professional kits structure
        professional_kits = self.test_professional_kits_structure()
        
        # Test 2: Professional calculation endpoint with first professional client
        prof_client_id = professional_clients[0]['id']
        calculation_results = self.test_professional_calculation_endpoint(prof_client_id)
        
        # Test 3: Leasing matrix functionality
        if calculation_results:
            self.test_leasing_matrix_functionality(calculation_results)
            
            # Test 4: Optimal kit algorithm
            self.test_optimal_kit_algorithm(calculation_results)
        
        # Test 5: Professional vs Particuliers rate comparison
        part_client_id = particuliers_clients[0]['id']
        self.test_professional_vs_particuliers_rates(prof_client_id, part_client_id)
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 PROFESSIONAL VERSION TEST SUMMARY")
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
    tester = ProfessionalVersionTester()
    results = tester.run_professional_tests()
    
    # Save results
    with open("/app/professional_test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to /app/professional_test_results.json")