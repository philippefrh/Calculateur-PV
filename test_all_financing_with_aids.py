#!/usr/bin/env python3
"""
Specific test for the new all_financing_with_aids functionality
Tests the new field that contains financing options for all durations (6-15 years) with aids deducted
"""

import requests
import json
import time
from typing import Dict, Any, List

# Backend URL from frontend environment
BACKEND_URL = "https://2132cfb7-d464-4ed0-bcc9-9d58b8782476.preview.emergentagent.com/api"

class AllFinancingWithAidsTest:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.client_id = None
        
    def log_result(self, test_name: str, success: bool, details: str):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        
    def create_test_client(self):
        """Create a new test client for financing tests"""
        print("🔧 Creating test client...")
        
        client_data = {
            "first_name": "Marie",
            "last_name": "Martin",
            "address": "15 Rue de Rivoli, 75001 Paris",
            "roof_surface": 80.0,
            "roof_orientation": "Sud",
            "velux_count": 3,
            "heating_system": "Pompe à chaleur",
            "water_heating_system": "Ballon thermodynamique",
            "water_heating_capacity": 250,
            "annual_consumption_kwh": 7200.0,
            "monthly_edf_payment": 200.0,
            "annual_edf_payment": 2400.0
        }
        
        try:
            response = self.session.post(f"{self.base_url}/clients", json=client_data)
            if response.status_code == 200:
                client = response.json()
                self.client_id = client.get("id")
                self.log_result("Create Test Client", True, f"Client created: {client['first_name']} {client['last_name']} (ID: {self.client_id})")
                return True
            else:
                self.log_result("Create Test Client", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_result("Create Test Client", False, f"Error: {str(e)}")
            return False
    
    def test_all_financing_with_aids_field(self):
        """Test that all_financing_with_aids field exists and has correct structure"""
        if not self.client_id:
            self.log_result("All Financing Field Test", False, "No client ID available")
            return None
            
        try:
            response = self.session.post(f"{self.base_url}/calculate/{self.client_id}")
            if response.status_code == 200:
                calculation = response.json()
                
                # Check if all_financing_with_aids field exists
                if "all_financing_with_aids" not in calculation:
                    self.log_result("All Financing Field Test", False, "Missing 'all_financing_with_aids' field in response")
                    return None
                
                all_financing = calculation["all_financing_with_aids"]
                
                # Check if it's a list
                if not isinstance(all_financing, list):
                    self.log_result("All Financing Field Test", False, f"all_financing_with_aids should be a list, got {type(all_financing)}")
                    return None
                
                # Check if it has options for 6-15 years (10 options)
                if len(all_financing) != 10:
                    self.log_result("All Financing Field Test", False, f"Expected 10 financing options (6-15 years), got {len(all_financing)}")
                    return None
                
                self.log_result("All Financing Field Test", True, f"Found all_financing_with_aids field with {len(all_financing)} options")
                return calculation
                
            else:
                self.log_result("All Financing Field Test", False, f"HTTP {response.status_code}: {response.text}")
                return None
        except Exception as e:
            self.log_result("All Financing Field Test", False, f"Error: {str(e)}")
            return None
    
    def test_financing_option_structure(self, calculation: Dict[str, Any]):
        """Test that each financing option has the required fields"""
        all_financing = calculation["all_financing_with_aids"]
        
        required_fields = ["duration_years", "monthly_payment", "difference_vs_savings"]
        
        for i, option in enumerate(all_financing):
            missing_fields = [field for field in required_fields if field not in option]
            if missing_fields:
                self.log_result("Financing Option Structure", False, f"Option {i+1} missing fields: {missing_fields}")
                return False
        
        self.log_result("Financing Option Structure", True, "All financing options have required fields: duration_years, monthly_payment, difference_vs_savings")
        return True
    
    def test_duration_years_sequence(self, calculation: Dict[str, Any]):
        """Test that duration_years goes from 6 to 15 years"""
        all_financing = calculation["all_financing_with_aids"]
        
        expected_durations = list(range(6, 16))  # 6 to 15 years
        actual_durations = [option["duration_years"] for option in all_financing]
        
        if actual_durations == expected_durations:
            self.log_result("Duration Years Sequence", True, "Duration years correctly range from 6 to 15 years")
            return True
        else:
            self.log_result("Duration Years Sequence", False, f"Expected {expected_durations}, got {actual_durations}")
            return False
    
    def test_monthly_payment_with_interests(self, calculation: Dict[str, Any]):
        """Test that monthly payments include 4.96% TAEG interest and are consistent"""
        all_financing = calculation["all_financing_with_aids"]
        kit_price = calculation.get("kit_price", 0)
        total_aids = calculation.get("total_aids", 0)
        financed_amount = kit_price - total_aids
        
        print(f"📊 Kit price: {kit_price}€, Total aids: {total_aids}€, Financed amount: {financed_amount}€")
        
        # Test that monthly payments decrease as duration increases
        monthly_payments = [option["monthly_payment"] for option in all_financing]
        
        # Check if payments are decreasing (longer duration = lower monthly payment)
        is_decreasing = all(monthly_payments[i] >= monthly_payments[i+1] for i in range(len(monthly_payments)-1))
        
        if not is_decreasing:
            self.log_result("Monthly Payment Consistency", False, "Monthly payments should decrease as duration increases")
            return False
        
        # Test that payments include interest (should be higher than simple division)
        taeg = 0.0496  # 4.96% TAEG
        monthly_rate = taeg / 12
        
        issues = []
        
        for option in all_financing:
            duration_years = option["duration_years"]
            monthly_payment = option["monthly_payment"]
            months = duration_years * 12
            
            # Simple division (without interest)
            simple_payment = financed_amount / months
            
            # Expected payment with interest
            if monthly_rate > 0:
                expected_payment = financed_amount * (monthly_rate * (1 + monthly_rate)**months) / ((1 + monthly_rate)**months - 1)
            else:
                expected_payment = simple_payment
            
            # Check if actual payment is close to expected (with interest)
            if abs(monthly_payment - expected_payment) > 1:  # Allow 1€ tolerance
                issues.append(f"{duration_years} years: {monthly_payment:.2f}€ vs expected {expected_payment:.2f}€")
            
            # Check if payment is higher than simple division (proving interest is included)
            if monthly_payment <= simple_payment:
                issues.append(f"{duration_years} years: {monthly_payment:.2f}€ should be > simple division {simple_payment:.2f}€")
        
        if issues:
            self.log_result("Monthly Payment with Interests", False, f"Interest calculation issues: {'; '.join(issues[:3])}")  # Show first 3 issues
            return False
        else:
            self.log_result("Monthly Payment with Interests", True, f"All monthly payments correctly include 4.96% TAEG interest. Range: {monthly_payments[-1]:.2f}€ (15 years) to {monthly_payments[0]:.2f}€ (6 years)")
            return True
    
    def test_difference_vs_savings(self, calculation: Dict[str, Any]):
        """Test that difference_vs_savings is correctly calculated"""
        all_financing = calculation["all_financing_with_aids"]
        monthly_savings = calculation.get("monthly_savings", 0)
        
        print(f"📊 Monthly EDF savings: {monthly_savings:.2f}€")
        
        for option in all_financing:
            duration_years = option["duration_years"]
            monthly_payment = option["monthly_payment"]
            difference = option["difference_vs_savings"]
            
            expected_difference = monthly_payment - monthly_savings
            
            if abs(difference - expected_difference) > 0.01:  # Allow 1 cent tolerance
                self.log_result("Difference vs Savings", False, f"{duration_years} years: difference {difference:.2f}€ != {monthly_payment:.2f}€ - {monthly_savings:.2f}€ = {expected_difference:.2f}€")
                return False
        
        # Show some examples
        examples = []
        for i in [0, 4, 9]:  # 6 years, 10 years, 15 years
            option = all_financing[i]
            examples.append(f"{option['duration_years']}y: {option['monthly_payment']:.2f}€ - {monthly_savings:.2f}€ = {option['difference_vs_savings']:.2f}€")
        
        self.log_result("Difference vs Savings", True, f"All differences correctly calculated. Examples: {'; '.join(examples)}")
        return True
    
    def test_financing_comparison(self, calculation: Dict[str, Any]):
        """Compare normal financing vs financing with aids"""
        normal_financing = calculation.get("financing_options", [])
        aids_financing = calculation.get("all_financing_with_aids", [])
        
        if not normal_financing or not aids_financing:
            self.log_result("Financing Comparison", False, "Missing normal financing or aids financing data")
            return False
        
        # Find 15-year options in both
        normal_15y = next((opt for opt in normal_financing if opt.get("duration_years") == 15), None)
        aids_15y = next((opt for opt in aids_financing if opt.get("duration_years") == 15), None)
        
        if not normal_15y or not aids_15y:
            self.log_result("Financing Comparison", False, "Could not find 15-year options in both financing types")
            return False
        
        normal_payment = normal_15y["monthly_payment"]
        aids_payment = aids_15y["monthly_payment"]
        
        # Aids financing should have lower monthly payment
        if aids_payment >= normal_payment:
            self.log_result("Financing Comparison", False, f"Aids financing payment {aids_payment:.2f}€ should be < normal financing {normal_payment:.2f}€")
            return False
        
        savings_amount = normal_payment - aids_payment
        savings_percentage = (savings_amount / normal_payment) * 100
        
        self.log_result("Financing Comparison", True, f"Aids financing saves {savings_amount:.2f}€/month ({savings_percentage:.1f}%) vs normal financing: {aids_payment:.2f}€ vs {normal_payment:.2f}€")
        return True
    
    def run_all_tests(self):
        """Run all tests for all_financing_with_aids functionality"""
        print("🚀 Testing all_financing_with_aids Functionality")
        print("=" * 60)
        
        # Step 1: Create test client
        if not self.create_test_client():
            print("❌ Cannot proceed without test client")
            return
        
        # Step 2: Get calculation with all_financing_with_aids
        calculation = self.test_all_financing_with_aids_field()
        if not calculation:
            print("❌ Cannot proceed without calculation data")
            return
        
        print("\n📋 Testing all_financing_with_aids structure and data...")
        
        # Step 3: Test structure
        self.test_financing_option_structure(calculation)
        
        # Step 4: Test duration sequence
        self.test_duration_years_sequence(calculation)
        
        # Step 5: Test monthly payments with interest
        self.test_monthly_payment_with_interests(calculation)
        
        # Step 6: Test difference calculations
        self.test_difference_vs_savings(calculation)
        
        # Step 7: Compare with normal financing
        self.test_financing_comparison(calculation)
        
        print("\n" + "=" * 60)
        print("✅ all_financing_with_aids Testing Complete")
        print("=" * 60)
        
        # Show sample data
        all_financing = calculation["all_financing_with_aids"]
        print("\n📊 Sample all_financing_with_aids data:")
        for i in [0, 4, 9]:  # Show 6, 10, and 15 years
            option = all_financing[i]
            print(f"  {option['duration_years']} years: {option['monthly_payment']:.2f}€/month, difference: {option['difference_vs_savings']:+.2f}€")

if __name__ == "__main__":
    tester = AllFinancingWithAidsTest()
    tester.run_all_tests()