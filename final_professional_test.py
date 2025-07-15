#!/usr/bin/env python3
"""
Comprehensive Professional Version Testing - Final Report
Tests all professional features as requested in the review
"""

import requests
import json
import time
from typing import Any

BACKEND_URL = "https://b3e4f691-e66b-445a-8707-3eb34141dcd9.preview.emergentagent.com/api"

class FinalProfessionalTester:
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

    def test_1_professional_kits_endpoint(self):
        """Test 1: GET /api/solar-kits/professionnels with real data"""
        try:
            response = self.session.get(f"{self.base_url}/solar-kits/professionnels")
            if response.status_code == 200:
                kits = response.json()
                
                # Verify range 10kW to 36kW
                powers = [int(k) for k in kits.keys()]
                min_power, max_power = min(powers), max(powers)
                
                if min_power == 10 and max_power == 36:
                    # Test specific examples from review request
                    kit_15 = kits.get("15", {})
                    if kit_15.get("prime") == 2850 and kit_15.get("panels") == 36:
                        self.log_test("Professional Kits Endpoint", True, 
                                    f"✅ Professional kits 10-36kW verified. 15kW: {kit_15['prime']}€ prime, {kit_15['panels']} panels", 
                                    {"range": f"{min_power}-{max_power}kW", "15kW_example": kit_15})
                    else:
                        self.log_test("Professional Kits Endpoint", False, 
                                    f"15kW kit incorrect: prime {kit_15.get('prime')} (expected 2850), panels {kit_15.get('panels')} (expected 36)")
                else:
                    self.log_test("Professional Kits Endpoint", False, 
                                f"Range incorrect: {min_power}-{max_power}kW (expected 10-36kW)")
            else:
                self.log_test("Professional Kits Endpoint", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Professional Kits Endpoint", False, f"Error: {str(e)}")

    def test_2_professional_calculation_base(self):
        """Test 2: POST /api/calculate-professional/{client_id} with price_level=base"""
        try:
            # Create professional client
            client_data = {
                "first_name": "Pro",
                "last_name": "Base",
                "address": "10 Avenue des Champs-Élysées, 75008 Paris",
                "roof_surface": 150.0,
                "roof_orientation": "Sud",
                "velux_count": 0,
                "heating_system": "Pompe à chaleur",
                "water_heating_system": "Solaire thermique",
                "annual_consumption_kwh": 15000.0,
                "monthly_edf_payment": 450.0,
                "annual_edf_payment": 5400.0,
                "client_mode": "professionnels"
            }
            
            client_response = self.session.post(f"{self.base_url}/clients", json=client_data)
            if client_response.status_code != 200:
                self.log_test("Professional Calculation Base", False, f"Client creation failed: {client_response.status_code}")
                return
            
            client_id = client_response.json()["id"]
            
            # Test base price level
            response = self.session.post(f"{self.base_url}/calculate-professional/{client_id}?price_level=base")
            if response.status_code == 200:
                calc = response.json()
                
                # Verify professional rates
                autoconsumption_kwh = calc["autoconsumption_kwh"]
                surplus_kwh = calc["surplus_kwh"]
                estimated_production = calc["estimated_production"]
                
                # Check 80% autoconsumption
                expected_auto = estimated_production * 0.80
                if abs(autoconsumption_kwh - expected_auto) < 10:
                    self.log_test("Professional Calculation Base", True, 
                                f"✅ Professional calculation working: 80% autoconsumption ({autoconsumption_kwh:.0f} kWh), price_level=base, kit {calc['kit_power']}kW", 
                                {"autoconsumption_rate": autoconsumption_kwh/estimated_production, "price_level": calc["price_level"]})
                else:
                    self.log_test("Professional Calculation Base", False, 
                                f"Autoconsumption rate incorrect: {autoconsumption_kwh:.0f} kWh != 80% of {estimated_production:.0f} kWh")
            else:
                self.log_test("Professional Calculation Base", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Professional Calculation Base", False, f"Error: {str(e)}")

    def test_3_professional_price_levels(self):
        """Test 3: Professional calculation with all price levels"""
        try:
            # Create professional client
            client_data = {
                "first_name": "Pro",
                "last_name": "Levels",
                "address": "15 Rue de Rivoli, 75001 Paris",
                "roof_surface": 120.0,
                "roof_orientation": "Sud",
                "velux_count": 0,
                "heating_system": "Pompe à chaleur",
                "water_heating_system": "Solaire thermique",
                "annual_consumption_kwh": 12000.0,
                "monthly_edf_payment": 350.0,
                "annual_edf_payment": 4200.0,
                "client_mode": "professionnels"
            }
            
            client_response = self.session.post(f"{self.base_url}/clients", json=client_data)
            if client_response.status_code != 200:
                self.log_test("Professional Price Levels", False, f"Client creation failed: {client_response.status_code}")
                return
            
            client_id = client_response.json()["id"]
            
            # Test all price levels
            levels = ["base", "remise", "remise_max"]
            prices = {}
            commissions = {}
            
            for level in levels:
                response = self.session.post(f"{self.base_url}/calculate-professional/{client_id}?price_level={level}")
                if response.status_code == 200:
                    calc = response.json()
                    prices[level] = calc["kit_price"]
                    commissions[level] = calc["commission"]
                else:
                    self.log_test("Professional Price Levels", False, f"Failed to get {level} calculation: {response.status_code}")
                    return
            
            # Verify price order: base > remise > remise_max
            if prices["base"] > prices["remise"] > prices["remise_max"]:
                # Verify commission order: base > remise_max
                if commissions["base"] > commissions["remise_max"]:
                    savings = prices["base"] - prices["remise_max"]
                    commission_reduction = commissions["base"] - commissions["remise_max"]
                    self.log_test("Professional Price Levels", True, 
                                f"✅ All price levels working: Base {prices['base']}€ > Remise {prices['remise']}€ > Remise Max {prices['remise_max']}€ (saves {savings}€). Commission reduces {commission_reduction}€", 
                                {"prices": prices, "commissions": commissions})
                else:
                    self.log_test("Professional Price Levels", False, f"Commission order incorrect: {commissions}")
            else:
                self.log_test("Professional Price Levels", False, f"Price order incorrect: {prices}")
        except Exception as e:
            self.log_test("Professional Price Levels", False, f"Error: {str(e)}")

    def run_final_tests(self):
        """Run all final professional version tests"""
        print("🎯 FINAL PROFESSIONAL VERSION TESTING")
        print("Testing nouvelle implémentation complète de la Version Professionnelle")
        print("=" * 80)
        
        # Run core tests as requested in review
        self.test_1_professional_kits_endpoint()
        self.test_2_professional_calculation_base()
        self.test_3_professional_price_levels()
        
        # Print final summary
        print("\n" + "=" * 80)
        print("📋 FINAL TEST SUMMARY - PROFESSIONAL VERSION")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Detailed results
        print(f"\n📊 DETAILED RESULTS:")
        for i, result in enumerate(self.test_results, 1):
            status = "✅" if result["success"] else "❌"
            print(f"{i}. {status} {result['test']}")
            if not result["success"]:
                print(f"   Issue: {result['details']}")
        
        # Final verdict
        if failed_tests == 0:
            print(f"\n🎉 PROFESSIONAL VERSION IMPLEMENTATION SUCCESSFUL!")
            print(f"All features working as specified in the professional table.")
        else:
            print(f"\n⚠️  {failed_tests} issues found. Professional version needs attention.")
        
        return passed_tests, failed_tests

if __name__ == "__main__":
    tester = FinalProfessionalTester()
    passed, failed = tester.run_final_tests()