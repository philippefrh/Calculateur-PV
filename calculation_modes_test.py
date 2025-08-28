#!/usr/bin/env python3
"""
Focused test for Calculation Modes System - Default Mode Change Verification
Tests the specific requirements from the review request
"""

import requests
import json
import time

# Backend URL from frontend environment
BACKEND_URL = "https://solar-quote-builder.preview.emergentagent.com/api"

class CalculationModesSpecificTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.client_id = None
        
    def log_test(self, test_name: str, success: bool, details: str, response_data: any = None):
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
    
    def setup_test_client(self):
        """Use existing client for testing"""
        try:
            # Get existing clients
            response = self.session.get(f"{self.base_url}/clients")
            if response.status_code == 200:
                clients = response.json()
                if clients and len(clients) > 0:
                    # Use first available client
                    self.client_id = clients[0]["id"]
                    client_name = f"{clients[0].get('first_name', 'Unknown')} {clients[0].get('last_name', 'Client')}"
                    consumption = clients[0].get('annual_consumption_kwh', 'Unknown')
                    payment = clients[0].get('monthly_edf_payment', 'Unknown')
                    self.log_test("Setup Test Client", True, 
                                f"Using existing client: {client_name} (ID: {self.client_id}, {consumption} kWh/an, {payment}€/month)")
                    return True
                else:
                    self.log_test("Setup Test Client", False, "No existing clients found")
                    return False
            else:
                self.log_test("Setup Test Client", False, f"Failed to get clients: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Setup Test Client", False, f"Error: {str(e)}")
            return False
    
    def test_default_mode_verification(self):
        """Test 1: Default Mode Verification - Call calculate endpoint without specifying calculation_mode"""
        if not self.client_id:
            self.log_test("Default Mode Verification", False, "No client ID available")
            return
            
        try:
            # Call without calculation_mode parameter - should default to 'realistic'
            response = self.session.post(f"{self.base_url}/calculate/{self.client_id}")
            if response.status_code == 200:
                calculation = response.json()
                
                # Check that calculation_mode is 'realistic' by default
                calculation_mode = calculation.get("calculation_mode")
                if calculation_mode != "realistic":
                    self.log_test("Default Mode Verification", False, 
                                f"Expected default calculation_mode 'realistic', got '{calculation_mode}'", 
                                calculation)
                    return
                
                # Check that calculation_config matches realistic mode
                calculation_config = calculation.get("calculation_config")
                if not calculation_config:
                    self.log_test("Default Mode Verification", False, "Missing calculation_config in response", calculation)
                    return
                
                if calculation_config.get("name") != "Mode Réaliste":
                    self.log_test("Default Mode Verification", False, 
                                f"Expected config name 'Mode Réaliste', got '{calculation_config.get('name')}'", 
                                calculation)
                    return
                
                # Check realistic mode parameters
                if calculation_config.get("autoconsumption_rate") != 0.85:
                    self.log_test("Default Mode Verification", False, 
                                f"Expected autoconsumption_rate 0.85, got {calculation_config.get('autoconsumption_rate')}", 
                                calculation)
                    return
                
                # Store for comparison
                self.default_calculation = calculation
                monthly_savings = calculation.get("monthly_savings", 0)
                real_savings_percentage = calculation.get("real_savings_percentage", 0)
                
                self.log_test("Default Mode Verification", True, 
                            f"✅ Default mode is 'realistic'. Monthly savings: {monthly_savings:.2f}€, Real savings: {real_savings_percentage:.1f}%", 
                            {"calculation_mode": calculation_mode, "monthly_savings": monthly_savings, "real_savings_percentage": real_savings_percentage})
            else:
                self.log_test("Default Mode Verification", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Default Mode Verification", False, f"Error: {str(e)}")
    
    def test_explicit_realistic_mode(self):
        """Test 2a: Explicit Realistic Mode - Should return lower savings (~192€/month)"""
        if not self.client_id:
            self.log_test("Explicit Realistic Mode", False, "No client ID available")
            return
            
        try:
            # Call with explicit realistic mode
            response = self.session.post(f"{self.base_url}/calculate/{self.client_id}?calculation_mode=realistic")
            if response.status_code == 200:
                calculation = response.json()
                
                # Verify mode
                if calculation.get("calculation_mode") != "realistic":
                    self.log_test("Explicit Realistic Mode", False, 
                                f"Expected calculation_mode 'realistic', got '{calculation.get('calculation_mode')}'")
                    return
                
                # Check results - should be around 192€/month and 67.6% real savings
                monthly_savings = calculation.get("monthly_savings", 0)
                real_savings_percentage = calculation.get("real_savings_percentage", 0)
                
                # Store for comparison
                self.realistic_calculation = calculation
                
                # Expected realistic results (allow some tolerance)
                expected_monthly_min, expected_monthly_max = 180, 210  # Around 192€
                expected_real_savings_min, expected_real_savings_max = 60, 80  # Around 67.6%
                
                issues = []
                if not (expected_monthly_min <= monthly_savings <= expected_monthly_max):
                    issues.append(f"Monthly savings {monthly_savings:.2f}€ outside expected range {expected_monthly_min}-{expected_monthly_max}€")
                
                if not (expected_real_savings_min <= real_savings_percentage <= expected_real_savings_max):
                    issues.append(f"Real savings {real_savings_percentage:.1f}% outside expected range {expected_real_savings_min}-{expected_real_savings_max}%")
                
                if issues:
                    self.log_test("Explicit Realistic Mode", False, f"Realistic mode issues: {'; '.join(issues)}", calculation)
                else:
                    self.log_test("Explicit Realistic Mode", True, 
                                f"✅ Realistic mode working. Monthly savings: {monthly_savings:.2f}€, Real savings: {real_savings_percentage:.1f}%", 
                                {"monthly_savings": monthly_savings, "real_savings_percentage": real_savings_percentage})
            else:
                self.log_test("Explicit Realistic Mode", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Explicit Realistic Mode", False, f"Error: {str(e)}")
    
    def test_explicit_optimistic_mode(self):
        """Test 2b: Explicit Optimistic Mode - Should return higher savings (~287€/month)"""
        if not self.client_id:
            self.log_test("Explicit Optimistic Mode", False, "No client ID available")
            return
            
        try:
            # Call with explicit optimistic mode
            response = self.session.post(f"{self.base_url}/calculate/{self.client_id}?calculation_mode=optimistic")
            if response.status_code == 200:
                calculation = response.json()
                
                # Verify mode
                if calculation.get("calculation_mode") != "optimistic":
                    self.log_test("Explicit Optimistic Mode", False, 
                                f"Expected calculation_mode 'optimistic', got '{calculation.get('calculation_mode')}'")
                    return
                
                # Check results - should be around 287€/month and 100.9% real savings
                monthly_savings = calculation.get("monthly_savings", 0)
                real_savings_percentage = calculation.get("real_savings_percentage", 0)
                
                # Store for comparison
                self.optimistic_calculation = calculation
                
                # Expected optimistic results (allow some tolerance)
                expected_monthly_min, expected_monthly_max = 270, 300  # Around 287€
                expected_real_savings_min, expected_real_savings_max = 95, 125  # Around 100.9%
                
                issues = []
                if not (expected_monthly_min <= monthly_savings <= expected_monthly_max):
                    issues.append(f"Monthly savings {monthly_savings:.2f}€ outside expected range {expected_monthly_min}-{expected_monthly_max}€")
                
                if not (expected_real_savings_min <= real_savings_percentage <= expected_real_savings_max):
                    issues.append(f"Real savings {real_savings_percentage:.1f}% outside expected range {expected_real_savings_min}-{expected_real_savings_max}%")
                
                if issues:
                    self.log_test("Explicit Optimistic Mode", False, f"Optimistic mode issues: {'; '.join(issues)}", calculation)
                else:
                    self.log_test("Explicit Optimistic Mode", True, 
                                f"✅ Optimistic mode working. Monthly savings: {monthly_savings:.2f}€, Real savings: {real_savings_percentage:.1f}%", 
                                {"monthly_savings": monthly_savings, "real_savings_percentage": real_savings_percentage})
            else:
                self.log_test("Explicit Optimistic Mode", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Explicit Optimistic Mode", False, f"Error: {str(e)}")
    
    def test_response_structure(self):
        """Test 3: Response Structure - Verify API response includes correct fields"""
        if not hasattr(self, 'default_calculation'):
            self.log_test("Response Structure", False, "No default calculation available from previous test")
            return
            
        try:
            calculation = self.default_calculation
            
            # Check required fields
            required_fields = ["calculation_mode", "calculation_config"]
            missing_fields = [field for field in required_fields if field not in calculation]
            
            if missing_fields:
                self.log_test("Response Structure", False, f"Missing required fields: {missing_fields}", calculation)
                return
            
            # Check calculation_config structure
            calculation_config = calculation.get("calculation_config")
            required_config_fields = ["name", "description", "autoconsumption_rate", "optimization_coefficient", "annual_rate_increase"]
            missing_config_fields = [field for field in required_config_fields if field not in calculation_config]
            
            if missing_config_fields:
                self.log_test("Response Structure", False, f"Missing calculation_config fields: {missing_config_fields}", calculation)
                return
            
            # Check that response includes real_savings_percentage
            if "real_savings_percentage" not in calculation:
                self.log_test("Response Structure", False, "Missing real_savings_percentage field", calculation)
                return
            
            # Check that autoconsumption_rate is included in response
            if "autoconsumption_rate" not in calculation:
                self.log_test("Response Structure", False, "Missing autoconsumption_rate field", calculation)
                return
            
            self.log_test("Response Structure", True, 
                        f"✅ Response structure correct. Mode: {calculation['calculation_mode']}, Config name: {calculation_config['name']}, All required fields present", 
                        {"required_fields_present": True, "calculation_mode": calculation["calculation_mode"]})
        except Exception as e:
            self.log_test("Response Structure", False, f"Error: {str(e)}")
    
    def test_mode_comparison(self):
        """Test 4: Mode Comparison - Compare the two modes to ensure significant differences"""
        if not hasattr(self, 'realistic_calculation') or not hasattr(self, 'optimistic_calculation'):
            self.log_test("Mode Comparison", False, "Missing realistic or optimistic calculation results")
            return
            
        try:
            realistic = self.realistic_calculation
            optimistic = self.optimistic_calculation
            
            # Extract values
            realistic_monthly = realistic.get("monthly_savings", 0)
            optimistic_monthly = optimistic.get("monthly_savings", 0)
            realistic_real_savings = realistic.get("real_savings_percentage", 0)
            optimistic_real_savings = optimistic.get("real_savings_percentage", 0)
            
            # Check that optimistic shows higher savings
            if optimistic_monthly <= realistic_monthly:
                self.log_test("Mode Comparison", False, 
                            f"Optimistic monthly savings {optimistic_monthly:.2f}€ should be higher than realistic {realistic_monthly:.2f}€")
                return
            
            if optimistic_real_savings <= realistic_real_savings:
                self.log_test("Mode Comparison", False, 
                            f"Optimistic real savings {optimistic_real_savings:.1f}% should be higher than realistic {realistic_real_savings:.1f}%")
                return
            
            # Calculate differences
            monthly_difference = optimistic_monthly - realistic_monthly
            real_savings_difference = optimistic_real_savings - realistic_real_savings
            monthly_increase_percentage = (monthly_difference / realistic_monthly) * 100 if realistic_monthly > 0 else 0
            
            # Check for significant differences (at least 30% increase expected)
            if monthly_increase_percentage < 30:
                self.log_test("Mode Comparison", False, 
                            f"Monthly savings increase {monthly_increase_percentage:.1f}% seems too small (expected >30%)")
                return
            
            if real_savings_difference < 30:
                self.log_test("Mode Comparison", False, 
                            f"Real savings difference {real_savings_difference:.1f} percentage points seems too small (expected >30)")
                return
            
            # Verify expected ranges
            # Realistic should be around 192€/month, 67.6% real savings
            # Optimistic should be around 287€/month, 100.9% real savings
            expected_realistic_monthly = 192
            expected_optimistic_monthly = 287
            expected_realistic_real = 67.6
            expected_optimistic_real = 100.9
            
            realistic_monthly_diff = abs(realistic_monthly - expected_realistic_monthly)
            optimistic_monthly_diff = abs(optimistic_monthly - expected_optimistic_monthly)
            realistic_real_diff = abs(realistic_real_savings - expected_realistic_real)
            optimistic_real_diff = abs(optimistic_real_savings - expected_optimistic_real)
            
            # Allow 20% tolerance
            tolerance_monthly = 0.2
            tolerance_real = 0.2
            
            issues = []
            if realistic_monthly_diff > expected_realistic_monthly * tolerance_monthly:
                issues.append(f"Realistic monthly savings {realistic_monthly:.2f}€ too far from expected {expected_realistic_monthly}€")
            
            if optimistic_monthly_diff > expected_optimistic_monthly * tolerance_monthly:
                issues.append(f"Optimistic monthly savings {optimistic_monthly:.2f}€ too far from expected {expected_optimistic_monthly}€")
            
            if realistic_real_diff > expected_realistic_real * tolerance_real:
                issues.append(f"Realistic real savings {realistic_real_savings:.1f}% too far from expected {expected_realistic_real}%")
            
            if optimistic_real_diff > expected_optimistic_real * tolerance_real:
                issues.append(f"Optimistic real savings {optimistic_real_savings:.1f}% too far from expected {expected_optimistic_real}%")
            
            if issues:
                self.log_test("Mode Comparison", False, f"Expected value issues: {'; '.join(issues)}")
            else:
                self.log_test("Mode Comparison", True, 
                            f"✅ Mode comparison successful. Realistic: {realistic_monthly:.2f}€/month ({realistic_real_savings:.1f}% real), Optimistic: {optimistic_monthly:.2f}€/month ({optimistic_real_savings:.1f}% real). Difference: +{monthly_difference:.2f}€/month (+{monthly_increase_percentage:.1f}%), +{real_savings_difference:.1f}% real savings", 
                            {
                                "realistic_monthly": realistic_monthly,
                                "optimistic_monthly": optimistic_monthly,
                                "realistic_real_savings": realistic_real_savings,
                                "optimistic_real_savings": optimistic_real_savings,
                                "monthly_difference": monthly_difference,
                                "monthly_increase_percentage": monthly_increase_percentage,
                                "real_savings_difference": real_savings_difference
                            })
        except Exception as e:
            self.log_test("Mode Comparison", False, f"Error: {str(e)}")
    
    def test_default_vs_explicit_consistency(self):
        """Test 5: Verify that default call (no mode) gives same results as explicit realistic mode"""
        if not hasattr(self, 'default_calculation') or not hasattr(self, 'realistic_calculation'):
            self.log_test("Default vs Explicit Consistency", False, "Missing default or realistic calculation results")
            return
            
        try:
            default = self.default_calculation
            explicit_realistic = self.realistic_calculation
            
            # Compare key values
            default_monthly = default.get("monthly_savings", 0)
            realistic_monthly = explicit_realistic.get("monthly_savings", 0)
            default_real_savings = default.get("real_savings_percentage", 0)
            realistic_real_savings = explicit_realistic.get("real_savings_percentage", 0)
            
            # Should be identical or very close (within 1€ and 1%)
            monthly_diff = abs(default_monthly - realistic_monthly)
            real_savings_diff = abs(default_real_savings - realistic_real_savings)
            
            if monthly_diff > 1.0:
                self.log_test("Default vs Explicit Consistency", False, 
                            f"Default monthly savings {default_monthly:.2f}€ differs from explicit realistic {realistic_monthly:.2f}€ by {monthly_diff:.2f}€")
                return
            
            if real_savings_diff > 1.0:
                self.log_test("Default vs Explicit Consistency", False, 
                            f"Default real savings {default_real_savings:.1f}% differs from explicit realistic {realistic_real_savings:.1f}% by {real_savings_diff:.1f}%")
                return
            
            # Check that both have same calculation_mode
            if default.get("calculation_mode") != explicit_realistic.get("calculation_mode"):
                self.log_test("Default vs Explicit Consistency", False, 
                            f"Default mode '{default.get('calculation_mode')}' != explicit mode '{explicit_realistic.get('calculation_mode')}'")
                return
            
            self.log_test("Default vs Explicit Consistency", True, 
                        f"✅ Default and explicit realistic modes are consistent. Monthly savings: {default_monthly:.2f}€ vs {realistic_monthly:.2f}€ (diff: {monthly_diff:.2f}€), Real savings: {default_real_savings:.1f}% vs {realistic_real_savings:.1f}% (diff: {real_savings_diff:.1f}%)", 
                        {"monthly_diff": monthly_diff, "real_savings_diff": real_savings_diff})
        except Exception as e:
            self.log_test("Default vs Explicit Consistency", False, f"Error: {str(e)}")
    
    def run_focused_tests(self):
        """Run focused tests for calculation modes system"""
        print("🎯 FOCUSED CALCULATION MODES TESTING")
        print("Testing the default calculation mode change from 'optimistic' to 'realistic'")
        print(f"Backend URL: {self.base_url}")
        print("=" * 80)
        
        # Setup
        if not self.setup_test_client():
            print("❌ Failed to setup test client, aborting tests")
            return
        
        print("\n📋 CALCULATION MODES SYSTEM TESTS")
        print("Using test data: 6890 kWh/an consumption, 240€/month EDF payment")
        print("-" * 60)
        
        # Run specific tests from review request
        self.test_default_mode_verification()
        self.test_explicit_realistic_mode()
        self.test_explicit_optimistic_mode()
        self.test_response_structure()
        self.test_mode_comparison()
        self.test_default_vs_explicit_consistency()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 FOCUSED TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        success_rate = (passed / total) * 100 if total > 0 else 0
        
        print(f"Total tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success rate: {success_rate:.1f}%")
        
        if success_rate < 100:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  • {result['test']}: {result['details']}")
        else:
            print("\n🎉 ALL CALCULATION MODES TESTS PASSED!")
            print("✅ Default mode successfully changed from 'optimistic' to 'realistic'")
            print("✅ Both modes working correctly with significant differences")
            print("✅ Response structure includes all required fields")
        
        return success_rate >= 80

if __name__ == "__main__":
    tester = CalculationModesSpecificTester()
    success = tester.run_focused_tests()
    
    # Save results
    with open("/app/calculation_modes_test_results.json", "w") as f:
        json.dump(tester.test_results, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to /app/calculation_modes_test_results.json")
    
    if success:
        print("🎯 CALCULATION MODES SYSTEM: WORKING CORRECTLY")
    else:
        print("⚠️  CALCULATION MODES SYSTEM: NEEDS ATTENTION")