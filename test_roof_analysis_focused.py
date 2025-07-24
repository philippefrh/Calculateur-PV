#!/usr/bin/env python3
"""
Focused testing for the intelligent roof analysis system
Tests the specific functions mentioned in the review request
"""

import requests
import json
import base64
import io
from PIL import Image as PILImage, ImageDraw

# Backend URL
BACKEND_URL = "https://5410321f-da01-4eb4-b6e7-0d805c152085.preview.emergentagent.com/api"

def create_realistic_roof_image():
    """Create a realistic roof image for testing"""
    # Create a larger, more realistic roof image
    img = PILImage.new('RGB', (800, 600), color='lightblue')  # Sky background
    draw = ImageDraw.Draw(img)
    
    # Draw main roof structure
    draw.polygon([(100, 400), (700, 400), (600, 200), (200, 200)], fill='darkgray', outline='black')
    
    # Add roof tiles pattern
    for y in range(200, 400, 20):
        for x in range(200, 600, 30):
            draw.rectangle([x, y, x+25, y+15], fill='gray', outline='darkgray')
    
    # Add obstacles
    # Velux/skylight
    draw.rectangle([300, 250, 350, 300], fill='lightblue', outline='black', width=3)
    
    # Chimney
    draw.rectangle([450, 220, 480, 280], fill='brown', outline='black', width=2)
    
    # Antenna
    draw.line([(520, 240), (520, 200)], fill='black', width=3)
    draw.line([(515, 205), (525, 205)], fill='black', width=2)
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', quality=95)
    buffer.seek(0)
    img_b64 = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/jpeg;base64,{img_b64}"

def test_roof_analysis_core_functions():
    """Test the core roof analysis functionality"""
    print("🏠 Testing Intelligent Roof Analysis System")
    print("=" * 60)
    
    # Create realistic test image
    test_image = create_realistic_roof_image()
    print(f"✅ Created realistic roof test image ({len(test_image)} chars)")
    
    # Test different panel counts as mentioned in review
    panel_counts = [6, 12, 18]
    results = {}
    
    for panel_count in panel_counts:
        print(f"\n🔧 Testing {panel_count} panels...")
        
        # Prepare request
        analysis_data = {
            "image_base64": test_image,
            "panel_count": panel_count
        }
        
        try:
            response = requests.post(f"{BACKEND_URL}/analyze-roof", json=analysis_data)
            
            if response.status_code == 200:
                result = response.json()
                results[panel_count] = result
                
                # Analyze the response
                print(f"  ✅ Status: SUCCESS")
                print(f"  📊 Panel positions returned: {len(result.get('panel_positions', []))}")
                print(f"  🏠 Roof analysis: {result.get('roof_analysis', '')[:100]}...")
                print(f"  💡 Recommendations: {result.get('recommendations', '')[:100]}...")
                print(f"  📐 Surface required: {result.get('total_surface_required', 0)}m²")
                print(f"  ✅ Placement possible: {result.get('placement_possible', False)}")
                
                # Check for key features mentioned in review
                analysis_text = result.get('roof_analysis', '') + result.get('recommendations', '')
                
                # 1. Obstacle detection keywords
                obstacle_keywords = ['obstacle', 'velux', 'cheminée', 'antenne', 'contournement']
                found_obstacles = [kw for kw in obstacle_keywords if kw.lower() in analysis_text.lower()]
                print(f"  🚧 Obstacle detection keywords found: {found_obstacles}")
                
                # 2. Zone positioning keywords  
                zone_keywords = ['zone', 'répartie', 'distribution', 'exploitable']
                found_zones = [kw for kw in zone_keywords if kw.lower() in analysis_text.lower()]
                print(f"  🗺️  Zone positioning keywords found: {found_zones}")
                
                # 3. Roof geometry keywords
                geometry_keywords = ['inclinaison', 'pente', 'orientation', 'géométrie']
                found_geometry = [kw for kw in geometry_keywords if kw.lower() in analysis_text.lower()]
                print(f"  📐 Roof geometry keywords found: {found_geometry}")
                
                # 4. Check panel position distribution
                positions = result.get('panel_positions', [])
                if positions:
                    x_coords = [p.get('x', 0) for p in positions]
                    y_coords = [p.get('y', 0) for p in positions]
                    x_range = max(x_coords) - min(x_coords) if x_coords else 0
                    y_range = max(y_coords) - min(y_coords) if y_coords else 0
                    print(f"  📍 Position distribution - X range: {x_range:.3f}, Y range: {y_range:.3f}")
                    
                    # Check for realistic positioning (not all clustered)
                    if x_range > 0.2 or y_range > 0.2:
                        print(f"  ✅ Good distribution - panels spread across roof")
                    else:
                        print(f"  ⚠️  Limited distribution - panels may be clustered")
                
            elif response.status_code == 422:
                print(f"  ⚠️  Status: VALIDATION ERROR - {response.text}")
                # This might be expected for certain test conditions
                
            else:
                print(f"  ❌ Status: ERROR {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"  ❌ Exception: {str(e)}")
    
    # Summary analysis
    print(f"\n📊 SUMMARY ANALYSIS")
    print("=" * 40)
    
    successful_tests = len([r for r in results.values() if r.get('success', False)])
    total_tests = len(panel_counts)
    
    print(f"Successful tests: {successful_tests}/{total_tests}")
    
    if successful_tests > 0:
        print("\n🎯 KEY FEATURES VERIFICATION:")
        
        # Check if the system shows signs of the redesigned features
        all_analysis_text = ""
        total_positions = 0
        
        for panel_count, result in results.items():
            all_analysis_text += result.get('roof_analysis', '') + result.get('recommendations', '')
            total_positions += len(result.get('panel_positions', []))
        
        # Feature checks
        features_found = []
        
        if 'obstacle' in all_analysis_text.lower() or 'velux' in all_analysis_text.lower():
            features_found.append("✅ Obstacle Detection System")
        else:
            features_found.append("❌ Obstacle Detection System")
            
        if 'zone' in all_analysis_text.lower() and 'répartie' in all_analysis_text.lower():
            features_found.append("✅ Multi-Zone Distribution")
        else:
            features_found.append("❌ Multi-Zone Distribution")
            
        if 'inclinaison' in all_analysis_text.lower() or 'géométrie' in all_analysis_text.lower():
            features_found.append("✅ Real Roof Geometry Analysis")
        else:
            features_found.append("❌ Real Roof Geometry Analysis")
            
        if total_positions == sum(panel_counts):
            features_found.append("✅ Correct Panel Count Positioning")
        else:
            features_found.append(f"❌ Panel Count Issues ({total_positions} vs {sum(panel_counts)} expected)")
            
        for feature in features_found:
            print(f"  {feature}")
    
    return results

if __name__ == "__main__":
    results = test_roof_analysis_core_functions()
    
    # Save results
    with open('/app/roof_analysis_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to /app/roof_analysis_test_results.json")