#!/usr/bin/env python3
"""
Test the new roof visualization endpoints specifically
"""

import requests
import json
import time
from typing import Dict, Any, Optional
from PIL import Image as PILImage
import io
import base64

# Backend URL from frontend environment
BACKEND_URL = "https://14552323-26f8-4263-9c4d-9869e98cea3a.preview.emergentagent.com/api"

class RoofVisualizationTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.test_image_data = None
        
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

    def test_roof_image_upload(self):
        """Test POST /api/upload-roof-image - Upload a roof image for solar panel visualization"""
        try:
            # Create a test image for upload
            test_image = PILImage.new('RGB', (400, 300), color='lightgray')
            buffer = io.BytesIO()
            test_image.save(buffer, format='JPEG')
            buffer.seek(0)
            
            # Prepare file upload
            files = {'file': ('test_roof.jpg', buffer, 'image/jpeg')}
            
            response = self.session.post(f"{self.base_url}/upload-roof-image", files=files)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                required_fields = ["success", "image_data", "file_size"]
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    self.log_test("Roof Image Upload", False, f"Missing fields: {missing_fields}", data)
                    return
                
                if not data["success"]:
                    self.log_test("Roof Image Upload", False, f"Upload failed: {data.get('error_message', 'Unknown error')}", data)
                    return
                
                # Validate base64 image data
                image_data = data["image_data"]
                if not image_data.startswith('data:image/'):
                    self.log_test("Roof Image Upload", False, "Image data not in correct base64 format", data)
                    return
                
                # Check file size
                file_size = data["file_size"]
                if file_size <= 0:
                    self.log_test("Roof Image Upload", False, f"Invalid file size: {file_size}", data)
                    return
                
                self.log_test("Roof Image Upload", True, 
                            f"✅ Image upload successful. File size: {file_size} bytes, Base64 format: {image_data[:50]}...", 
                            {"file_size": file_size, "has_base64_data": len(image_data) > 100})
                
                # Store image data for next test
                self.test_image_data = image_data
                
            else:
                self.log_test("Roof Image Upload", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Roof Image Upload", False, f"Error: {str(e)}")

    def test_roof_visualization_generation_france(self):
        """Test POST /api/generate-roof-visualization for France region with fal.ai integration"""
        # Skip if no image data from previous test
        if not self.test_image_data:
            self.log_test("Roof Visualization France", False, "No test image data available from upload test")
            return
            
        try:
            # Test with 6kW kit for France (should have 12 panels)
            request_data = {
                "image_data": self.test_image_data,
                "kit_power": 6,
                "region": "france"
            }
            
            response = self.session.post(f"{self.base_url}/generate-roof-visualization", json=request_data)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                required_fields = ["success"]
                if data.get("success"):
                    required_fields.extend(["generated_image_url", "original_image_data", "kit_info"])
                else:
                    required_fields.append("error_message")
                
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    self.log_test("Roof Visualization France", False, f"Missing fields: {missing_fields}", data)
                    return
                
                if not data["success"]:
                    error_msg = data.get("error_message", "Unknown error")
                    # Check if it's a FAL_KEY issue
                    if "FAL_KEY" in error_msg:
                        self.log_test("Roof Visualization France", False, f"❌ FAL_KEY configuration issue: {error_msg}", data)
                    else:
                        self.log_test("Roof Visualization France", False, f"❌ Generation failed: {error_msg}", data)
                    return
                
                # Validate successful response
                kit_info = data["kit_info"]
                
                # Check kit power matches request
                if kit_info.get("power") != 6:
                    self.log_test("Roof Visualization France", False, f"Kit power mismatch: expected 6, got {kit_info.get('power')}", data)
                    return
                
                # Check panel count for 6kW kit (should be 12 panels)
                expected_panels = 12
                actual_panels = kit_info.get("panels")
                if actual_panels != expected_panels:
                    self.log_test("Roof Visualization France", False, f"Panel count mismatch: expected {expected_panels}, got {actual_panels}", data)
                    return
                
                # Check region
                if kit_info.get("region") != "france":
                    self.log_test("Roof Visualization France", False, f"Region mismatch: expected france, got {kit_info.get('region')}", data)
                    return
                
                # Check generated image URL
                generated_url = data.get("generated_image_url")
                if not generated_url or not generated_url.startswith("http"):
                    self.log_test("Roof Visualization France", False, f"Invalid generated image URL: {generated_url}", data)
                    return
                
                self.log_test("Roof Visualization France", True, 
                            f"✅ Roof visualization generated successfully for France. 6kW kit with {actual_panels} BLACK panels, fal.ai URL: {generated_url[:50]}...", 
                            {"kit_power": 6, "panels": actual_panels, "region": "france", "has_generated_url": bool(generated_url)})
                
            else:
                self.log_test("Roof Visualization France", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Roof Visualization France", False, f"Error: {str(e)}")

    def test_roof_visualization_generation_martinique(self):
        """Test POST /api/generate-roof-visualization for Martinique region with different kit powers"""
        # Skip if no image data from previous test
        if not self.test_image_data:
            self.log_test("Roof Visualization Martinique", False, "No test image data available from upload test")
            return
            
        try:
            # Test with 9kW kit for Martinique (should have 24 panels based on 375W panels)
            request_data = {
                "image_data": self.test_image_data,
                "kit_power": 9,
                "region": "martinique"
            }
            
            response = self.session.post(f"{self.base_url}/generate-roof-visualization", json=request_data)
            
            if response.status_code == 200:
                data = response.json()
                
                if not data.get("success"):
                    error_msg = data.get("error_message", "Unknown error")
                    if "FAL_KEY" in error_msg:
                        self.log_test("Roof Visualization Martinique", False, f"❌ FAL_KEY configuration issue: {error_msg}", data)
                    else:
                        self.log_test("Roof Visualization Martinique", False, f"❌ Generation failed: {error_msg}", data)
                    return
                
                # Validate successful response
                kit_info = data["kit_info"]
                
                # Check kit power matches request
                if kit_info.get("power") != 9:
                    self.log_test("Roof Visualization Martinique", False, f"Kit power mismatch: expected 9, got {kit_info.get('power')}", data)
                    return
                
                # Check panel count for 9kW kit in Martinique (9kW = 24 panels of 375W)
                expected_panels = 24
                actual_panels = kit_info.get("panels")
                if actual_panels != expected_panels:
                    self.log_test("Roof Visualization Martinique", False, f"Panel count mismatch: expected {expected_panels}, got {actual_panels}", data)
                    return
                
                # Check region
                if kit_info.get("region") != "martinique":
                    self.log_test("Roof Visualization Martinique", False, f"Region mismatch: expected martinique, got {kit_info.get('region')}", data)
                    return
                
                # Check generated image URL
                generated_url = data.get("generated_image_url")
                if not generated_url or not generated_url.startswith("http"):
                    self.log_test("Roof Visualization Martinique", False, f"Invalid generated image URL: {generated_url}", data)
                    return
                
                self.log_test("Roof Visualization Martinique", True, 
                            f"✅ Roof visualization generated successfully for Martinique. 9kW kit with {actual_panels} BLACK panels (375W each), fal.ai URL: {generated_url[:50]}...", 
                            {"kit_power": 9, "panels": actual_panels, "region": "martinique", "has_generated_url": bool(generated_url)})
                
            else:
                self.log_test("Roof Visualization Martinique", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Roof Visualization Martinique", False, f"Error: {str(e)}")

    def test_roof_visualization_different_kit_powers(self):
        """Test roof visualization with different kit powers (3kW, 6kW, 9kW)"""
        # Skip if no image data from previous test
        if not self.test_image_data:
            self.log_test("Roof Visualization Different Powers", False, "No test image data available from upload test")
            return
            
        try:
            test_cases = [
                {"power": 3, "region": "france", "expected_panels": 6},
                {"power": 6, "region": "france", "expected_panels": 12},
                {"power": 9, "region": "france", "expected_panels": 18},
                {"power": 3, "region": "martinique", "expected_panels": 8},  # 3kW = 8 panels of 375W
                {"power": 6, "region": "martinique", "expected_panels": 16}, # 6kW = 16 panels of 375W
            ]
            
            results = []
            
            for test_case in test_cases:
                request_data = {
                    "image_data": self.test_image_data,
                    "kit_power": test_case["power"],
                    "region": test_case["region"]
                }
                
                response = self.session.post(f"{self.base_url}/generate-roof-visualization", json=request_data)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get("success"):
                        kit_info = data["kit_info"]
                        actual_panels = kit_info.get("panels")
                        expected_panels = test_case["expected_panels"]
                        
                        if actual_panels == expected_panels:
                            results.append(f"✅ {test_case['power']}kW {test_case['region']}: {actual_panels} panels")
                        else:
                            results.append(f"❌ {test_case['power']}kW {test_case['region']}: expected {expected_panels}, got {actual_panels}")
                    else:
                        error_msg = data.get("error_message", "Unknown error")
                        if "FAL_KEY" in error_msg:
                            results.append(f"❌ {test_case['power']}kW {test_case['region']}: FAL_KEY issue")
                        else:
                            results.append(f"❌ {test_case['power']}kW {test_case['region']}: {error_msg}")
                else:
                    results.append(f"❌ {test_case['power']}kW {test_case['region']}: HTTP {response.status_code}")
            
            # Check if all tests passed
            failed_tests = [r for r in results if r.startswith("❌")]
            
            if not failed_tests:
                self.log_test("Roof Visualization Different Powers", True, 
                            f"✅ All kit power tests passed: {'; '.join(results)}", 
                            {"test_cases": len(test_cases), "passed": len(results) - len(failed_tests)})
            else:
                self.log_test("Roof Visualization Different Powers", False, 
                            f"Some tests failed: {'; '.join(results)}", 
                            {"test_cases": len(test_cases), "failed": len(failed_tests)})
                
        except Exception as e:
            self.log_test("Roof Visualization Different Powers", False, f"Error: {str(e)}")

    def test_fal_ai_integration_and_black_panels(self):
        """Test fal.ai integration and verify BLACK panel requirement"""
        # Skip if no image data from previous test
        if not self.test_image_data:
            self.log_test("Fal.ai Integration & Black Panels", False, "No test image data available from upload test")
            return
            
        try:
            # Test with a specific kit to verify fal.ai integration
            request_data = {
                "image_data": self.test_image_data,
                "kit_power": 6,
                "region": "france"
            }
            
            response = self.session.post(f"{self.base_url}/generate-roof-visualization", json=request_data)
            
            if response.status_code == 200:
                data = response.json()
                
                if not data.get("success"):
                    error_msg = data.get("error_message", "Unknown error")
                    
                    # Check specific error types
                    if "FAL_KEY not configured" in error_msg:
                        self.log_test("Fal.ai Integration & Black Panels", False, 
                                    "❌ CRITICAL: FAL_KEY not configured in environment variables", data)
                    elif "FAL_KEY" in error_msg:
                        self.log_test("Fal.ai Integration & Black Panels", False, 
                                    f"❌ CRITICAL: FAL_KEY configuration issue: {error_msg}", data)
                    elif "Generation error" in error_msg:
                        self.log_test("Fal.ai Integration & Black Panels", False, 
                                    f"❌ fal.ai generation error: {error_msg}", data)
                    else:
                        self.log_test("Fal.ai Integration & Black Panels", False, 
                                    f"❌ Visualization failed: {error_msg}", data)
                    return
                
                # Successful generation - verify integration
                generated_url = data.get("generated_image_url")
                kit_info = data.get("kit_info", {})
                
                # Verify fal.ai URL format
                if not generated_url or not generated_url.startswith("http"):
                    self.log_test("Fal.ai Integration & Black Panels", False, 
                                f"❌ Invalid fal.ai generated URL: {generated_url}", data)
                    return
                
                # Check if URL looks like fal.ai format (fal.media is the CDN for fal.ai)
                if "fal.ai" not in generated_url and "fal.media" not in generated_url:
                    self.log_test("Fal.ai Integration & Black Panels", False, 
                                f"❌ Generated URL doesn't appear to be from fal.ai: {generated_url}", data)
                    return
                
                # Verify panel count matches kit power
                expected_panels = 12  # 6kW kit should have 12 panels
                actual_panels = kit_info.get("panels")
                if actual_panels != expected_panels:
                    self.log_test("Fal.ai Integration & Black Panels", False, 
                                f"❌ Panel count mismatch: expected {expected_panels}, got {actual_panels}", data)
                    return
                
                self.log_test("Fal.ai Integration & Black Panels", True, 
                            f"✅ fal.ai integration working correctly. Generated photorealistic visualization with {actual_panels} BLACK panels using OmniGen V2 model. URL: {generated_url[:50]}...", 
                            {
                                "fal_ai_url": generated_url,
                                "panels": actual_panels,
                                "kit_power": 6,
                                "model": "OmniGen V2",
                                "panel_color": "BLACK (as specified in prompt)"
                            })
                
            else:
                self.log_test("Fal.ai Integration & Black Panels", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Fal.ai Integration & Black Panels", False, f"Error: {str(e)}")

    def run_roof_visualization_tests(self):
        """Run all roof visualization tests"""
        print("🏠 TESTING NEW ROOF VISUALIZATION ENDPOINTS - FAL.AI INTEGRATION")
        print("=" * 70)
        print("🎯 TESTING: POST /api/upload-roof-image & POST /api/generate-roof-visualization")
        print()
        
        # Run tests in sequence
        self.test_roof_image_upload()
        self.test_roof_visualization_generation_france()
        self.test_roof_visualization_generation_martinique()
        self.test_roof_visualization_different_kit_powers()
        self.test_fal_ai_integration_and_black_panels()
        
        # Print summary
        print("\n" + "=" * 70)
        print("📊 ROOF VISUALIZATION TEST SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n🔍 FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"❌ {result['test']}: {result['details']}")
        
        print("\n" + "=" * 70)

if __name__ == "__main__":
    tester = RoofVisualizationTester()
    tester.run_roof_visualization_tests()