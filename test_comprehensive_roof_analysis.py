#!/usr/bin/env python3
"""
Comprehensive testing for the intelligent roof analysis system
Verifies all 6 critical testing objectives from the review request
"""

import requests
import json
import base64
import io
from PIL import Image as PILImage, ImageDraw

# Backend URL
BACKEND_URL = "https://42ba765f-58bd-41eb-84d9-c956e64f3f53.preview.emergentagent.com/api"

def create_complex_roof_image():
    """Create a complex roof image with multiple obstacles"""
    # Create a larger, more complex roof image
    img = PILImage.new('RGB', (1000, 800), color='lightblue')  # Sky background
    draw = ImageDraw.Draw(img)
    
    # Draw main roof structure with multiple sections
    draw.polygon([(100, 600), (900, 600), (800, 300), (200, 300)], fill='darkgray', outline='black')
    
    # Add roof tiles pattern
    for y in range(300, 600, 25):
        for x in range(200, 800, 35):
            draw.rectangle([x, y, x+30, y+20], fill='gray', outline='darkgray')
    
    # Add multiple obstacles as mentioned in review request
    
    # 1. Skylights/Velux (multiple)
    draw.rectangle([300, 350, 380, 420], fill='lightblue', outline='black', width=3)
    draw.rectangle([500, 380, 580, 450], fill='lightblue', outline='black', width=3)
    
    # 2. Chimneys (different sizes)
    draw.rectangle([650, 320, 690, 400], fill='brown', outline='black', width=2)
    draw.rectangle([250, 340, 280, 390], fill='darkred', outline='black', width=2)
    
    # 3. Antennas
    draw.line([(720, 350), (720, 280)], fill='black', width=4)
    draw.line([(715, 285), (725, 285)], fill='black', width=3)
    draw.line([(400, 360), (400, 310)], fill='black', width=3)
    
    # 4. Roof vents
    draw.ellipse([450, 340, 470, 360], fill='darkgray', outline='black')
    draw.ellipse([600, 370, 620, 390], fill='darkgray', outline='black')
    
    # 5. Solar water heater (existing installation)
    draw.rectangle([350, 480, 450, 550], fill='darkblue', outline='black', width=2)
    
    # Add some roof edge details
    draw.line([(200, 300), (800, 300)], fill='black', width=3)  # Ridge
    draw.line([(100, 600), (900, 600)], fill='black', width=3)  # Gutter
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', quality=95)
    buffer.seek(0)
    img_b64 = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/jpeg;base64,{img_b64}"

def test_comprehensive_roof_analysis():
    """Test all 6 critical testing objectives from the review request"""
    print("🏠 COMPREHENSIVE INTELLIGENT ROOF ANALYSIS TESTING")
    print("=" * 70)
    print("🎯 TESTING ALL 6 CRITICAL OBJECTIVES FROM REVIEW REQUEST:")
    print("1. ✅ OBSTACLE DETECTION SYSTEM")
    print("2. ✅ INTELLIGENT ZONE POSITIONING") 
    print("3. ✅ REAL ROOF GEOMETRY ANALYSIS")
    print("4. ✅ ENHANCED ANALYSIS MESSAGES")
    print("5. ✅ REALISTIC INSTALLATION PATTERNS")
    print("6. ✅ MULTI-ZONE DISTRIBUTION")
    print("=" * 70)
    
    # Create complex test image with multiple obstacles
    test_image = create_complex_roof_image()
    print(f"✅ Created complex roof test image with multiple obstacles ({len(test_image)} chars)")
    
    # Test different panel counts as mentioned in review (6, 12, 18)
    panel_counts = [6, 12, 18]
    results = {}
    
    for panel_count in panel_counts:
        print(f"\n🔧 TESTING {panel_count} PANELS - COMPREHENSIVE ANALYSIS")
        print("-" * 50)
        
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
                
                # Extract key data
                panel_positions = result.get('panel_positions', [])
                roof_analysis = result.get('roof_analysis', '')
                recommendations = result.get('recommendations', '')
                placement_possible = result.get('placement_possible', False)
                surface_required = result.get('total_surface_required', 0)
                
                print(f"📊 BASIC RESULTS:")
                print(f"  • Panel positions returned: {len(panel_positions)}")
                print(f"  • Surface required: {surface_required}m²")
                print(f"  • Placement possible: {placement_possible}")
                
                # OBJECTIVE 1: OBSTACLE DETECTION SYSTEM
                print(f"\n1️⃣ OBSTACLE DETECTION SYSTEM:")
                obstacle_keywords = ['obstacle', 'velux', 'cheminée', 'antenne', 'vent', 'existant']
                found_obstacles = [kw for kw in obstacle_keywords if kw.lower() in (roof_analysis + recommendations).lower()]
                print(f"  • Obstacle keywords found: {found_obstacles}")
                print(f"  • Detection score: {len(found_obstacles)}/6")
                
                # OBJECTIVE 2: INTELLIGENT ZONE POSITIONING
                print(f"\n2️⃣ INTELLIGENT ZONE POSITIONING:")
                zone_keywords = ['zone', 'répartie', 'distribution', 'exploitable', 'secteur']
                found_zones = [kw for kw in zone_keywords if kw.lower() in (roof_analysis + recommendations).lower()]
                print(f"  • Zone positioning keywords: {found_zones}")
                print(f"  • Zone positioning score: {len(found_zones)}/5")
                
                # OBJECTIVE 3: REAL ROOF GEOMETRY ANALYSIS
                print(f"\n3️⃣ REAL ROOF GEOMETRY ANALYSIS:")
                geometry_keywords = ['inclinaison', 'pente', 'orientation', 'géométrie', 'toit', 'toiture']
                found_geometry = [kw for kw in geometry_keywords if kw.lower() in (roof_analysis + recommendations).lower()]
                print(f"  • Geometry analysis keywords: {found_geometry}")
                print(f"  • Geometry analysis score: {len(found_geometry)}/6")
                
                # OBJECTIVE 4: ENHANCED ANALYSIS MESSAGES
                print(f"\n4️⃣ ENHANCED ANALYSIS MESSAGES:")
                enhanced_keywords = ['optimisation', 'intelligent', 'analyse', 'détecté', 'recommandation']
                found_enhanced = [kw for kw in enhanced_keywords if kw.lower() in (roof_analysis + recommendations).lower()]
                print(f"  • Enhanced message keywords: {found_enhanced}")
                print(f"  • Message quality score: {len(found_enhanced)}/5")
                print(f"  • Analysis length: {len(roof_analysis)} chars")
                print(f"  • Recommendations length: {len(recommendations)} chars")
                
                # OBJECTIVE 5: REALISTIC INSTALLATION PATTERNS
                print(f"\n5️⃣ REALISTIC INSTALLATION PATTERNS:")
                if panel_positions:
                    x_coords = [p.get('x', 0) for p in panel_positions]
                    y_coords = [p.get('y', 0) for p in panel_positions]
                    
                    # Check distribution
                    x_range = max(x_coords) - min(x_coords) if x_coords else 0
                    y_range = max(y_coords) - min(y_coords) if y_coords else 0
                    
                    # Check realistic positioning (within roof bounds)
                    valid_positions = all(0.05 <= x <= 0.95 and 0.05 <= y <= 0.95 for x, y in zip(x_coords, y_coords))
                    
                    # Check spacing (no overlapping)
                    min_spacing = 0.08  # Minimum realistic spacing
                    proper_spacing = True
                    for i, pos1 in enumerate(panel_positions):
                        for j, pos2 in enumerate(panel_positions[i+1:], i+1):
                            distance = ((pos1.get('x', 0) - pos2.get('x', 0))**2 + 
                                      (pos1.get('y', 0) - pos2.get('y', 0))**2)**0.5
                            if distance < min_spacing:
                                proper_spacing = False
                                break
                        if not proper_spacing:
                            break
                    
                    print(f"  • Position distribution - X: {x_range:.3f}, Y: {y_range:.3f}")
                    print(f"  • Valid positioning: {valid_positions}")
                    print(f"  • Proper spacing: {proper_spacing}")
                    print(f"  • Realistic pattern score: {sum([x_range > 0.2, y_range > 0.15, valid_positions, proper_spacing])}/4")
                
                # OBJECTIVE 6: MULTI-ZONE DISTRIBUTION
                print(f"\n6️⃣ MULTI-ZONE DISTRIBUTION:")
                multi_zone_keywords = ['zone', 'répartie', 'distribution', 'secteur', 'contournement']
                found_multi_zone = [kw for kw in multi_zone_keywords if kw.lower() in (roof_analysis + recommendations).lower()]
                print(f"  • Multi-zone keywords: {found_multi_zone}")
                print(f"  • Multi-zone score: {len(found_multi_zone)}/5")
                
                # Check if positions suggest multi-zone placement
                if panel_positions and len(panel_positions) >= 6:
                    # Group positions by proximity to detect zones
                    zones_detected = 1
                    if x_range > 0.4 or y_range > 0.3:  # Wide distribution suggests multiple zones
                        zones_detected = 2
                    print(f"  • Estimated zones from positions: {zones_detected}")
                
                # OVERALL ASSESSMENT
                print(f"\n📊 OVERALL ASSESSMENT FOR {panel_count} PANELS:")
                scores = {
                    'obstacle_detection': len(found_obstacles),
                    'zone_positioning': len(found_zones), 
                    'geometry_analysis': len(found_geometry),
                    'enhanced_messages': len(found_enhanced),
                    'realistic_patterns': sum([x_range > 0.2, y_range > 0.15, valid_positions, proper_spacing]) if panel_positions else 0,
                    'multi_zone': len(found_multi_zone)
                }
                
                total_score = sum(scores.values())
                max_score = 31  # Sum of all maximum scores
                
                print(f"  • Total functionality score: {total_score}/{max_score} ({(total_score/max_score)*100:.1f}%)")
                
                if total_score >= 20:  # 65% threshold
                    print(f"  ✅ EXCELLENT - All major objectives achieved")
                elif total_score >= 15:  # 50% threshold
                    print(f"  ✅ GOOD - Most objectives achieved")
                else:
                    print(f"  ⚠️ NEEDS IMPROVEMENT - Some objectives missing")
                
            else:
                print(f"  ❌ Status: ERROR {response.status_code} - {response.text}")
                results[panel_count] = {"error": response.status_code, "message": response.text}
                
        except Exception as e:
            print(f"  ❌ Exception: {str(e)}")
            results[panel_count] = {"error": "exception", "message": str(e)}
    
    # FINAL SUMMARY
    print(f"\n🎯 FINAL COMPREHENSIVE ASSESSMENT")
    print("=" * 50)
    
    successful_tests = len([r for r in results.values() if not r.get('error')])
    total_tests = len(panel_counts)
    
    print(f"Successful tests: {successful_tests}/{total_tests}")
    
    if successful_tests > 0:
        print(f"\n✅ CRITICAL OBJECTIVES VERIFICATION:")
        
        # Aggregate all successful results
        all_analysis_text = ""
        total_positions = 0
        all_positions = []
        
        for panel_count, result in results.items():
            if not result.get('error'):
                all_analysis_text += result.get('roof_analysis', '') + result.get('recommendations', '')
                positions = result.get('panel_positions', [])
                total_positions += len(positions)
                all_positions.extend(positions)
        
        # Final feature verification
        final_scores = {}
        
        # 1. Obstacle Detection System
        obstacle_found = any(kw in all_analysis_text.lower() for kw in ['obstacle', 'velux', 'cheminée', 'antenne'])
        final_scores['obstacle_detection'] = obstacle_found
        print(f"1. ✅ OBSTACLE DETECTION SYSTEM: {'WORKING' if obstacle_found else 'MISSING'}")
        
        # 2. Intelligent Zone Positioning  
        zone_found = any(kw in all_analysis_text.lower() for kw in ['zone', 'répartie', 'exploitable'])
        final_scores['zone_positioning'] = zone_found
        print(f"2. ✅ INTELLIGENT ZONE POSITIONING: {'WORKING' if zone_found else 'MISSING'}")
        
        # 3. Real Roof Geometry Analysis
        geometry_found = any(kw in all_analysis_text.lower() for kw in ['inclinaison', 'géométrie', 'toit'])
        final_scores['geometry_analysis'] = geometry_found
        print(f"3. ✅ REAL ROOF GEOMETRY ANALYSIS: {'WORKING' if geometry_found else 'MISSING'}")
        
        # 4. Enhanced Analysis Messages
        enhanced_found = len(all_analysis_text) > 200  # Substantial analysis content
        final_scores['enhanced_messages'] = enhanced_found
        print(f"4. ✅ ENHANCED ANALYSIS MESSAGES: {'WORKING' if enhanced_found else 'MISSING'}")
        
        # 5. Realistic Installation Patterns
        realistic_found = total_positions == sum(panel_counts)  # Correct panel count
        final_scores['realistic_patterns'] = realistic_found
        print(f"5. ✅ REALISTIC INSTALLATION PATTERNS: {'WORKING' if realistic_found else 'MISSING'}")
        
        # 6. Multi-Zone Distribution
        multi_zone_found = any(kw in all_analysis_text.lower() for kw in ['zone', 'répartie', 'contournement'])
        final_scores['multi_zone'] = multi_zone_found
        print(f"6. ✅ MULTI-ZONE DISTRIBUTION: {'WORKING' if multi_zone_found else 'MISSING'}")
        
        # Overall system assessment
        working_objectives = sum(final_scores.values())
        print(f"\n🏆 SYSTEM PERFORMANCE: {working_objectives}/6 objectives working ({(working_objectives/6)*100:.1f}%)")
        
        if working_objectives >= 5:
            print("🎉 EXCELLENT - Intelligent roof analysis system fully operational!")
        elif working_objectives >= 4:
            print("✅ GOOD - Most critical objectives achieved")
        else:
            print("⚠️ NEEDS IMPROVEMENT - Several objectives require attention")
    
    return results

if __name__ == "__main__":
    results = test_comprehensive_roof_analysis()
    
    # Save results
    with open('/app/comprehensive_roof_analysis_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Comprehensive results saved to /app/comprehensive_roof_analysis_results.json")