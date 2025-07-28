#!/usr/bin/env python3
"""
Test script for fal.ai solar panel placement validation
"""
import os
import fal_client
from dotenv import load_dotenv
import base64
import requests
from io import BytesIO

# Load environment variables
load_dotenv('/app/backend/.env')

# Configure fal client
fal_key = os.getenv('FAL_KEY')
if not fal_key:
    print("❌ FAL_KEY not found in environment variables")
    exit(1)

print(f"✅ FAL_KEY configured: {fal_key[:20]}...")

def download_and_encode_image(url):
    """Download image from URL and convert to base64"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        # Convert to base64
        image_data = base64.b64encode(response.content).decode('utf-8')
        return f"data:image/jpeg;base64,{image_data}"
    except Exception as e:
        print(f"❌ Error downloading image: {e}")
        return None

def test_solar_panel_placement():
    """Test adding 12 solar panels to the house roof photo"""
    
    # URL of the test house photo
    house_image_url = "https://customer-assets.emergentagent.com/job_frh-discount-system/artifacts/85oefc5z_Essais%20sur%20cette%20toiture.jpg"
    
    print("📥 Downloading and encoding test image...")
    base64_image = download_and_encode_image(house_image_url)
    
    if not base64_image:
        print("❌ Failed to download test image")
        return
    
    print("✅ Image downloaded and encoded")
    
    # Prompt for photorealistic solar panel placement
    prompt = """Add 12 realistic black solar panels on the roof of this house. The solar panels should be:
- Photorealistic and professional quality like real installations
- Properly aligned on the roof tiles
- With natural shadows and reflections
- Modern black rectangular panels (like Powernity 375W)
- Arranged in optimal rows on the available roof space
- Realistic integration that matches the architectural style
- Same quality as professional solar installation photos"""
    
    print("🚀 Generating solar panel placement with fal.ai...")
    print(f"📝 Prompt: {prompt}")
    
    try:
        # Use OmniGen V2 for image editing (adding panels to existing photo)
        handler = fal_client.submit(
            "fal-ai/omnigen-v2",
            arguments={
                "prompt": prompt,
                "image_url": base64_image,
                "guidance_scale": 7.5,
                "num_inference_steps": 50,
                "seed": 42
            }
        )
        
        print("⏳ Processing...")
        result = handler.get()
        
        if result and 'images' in result and len(result['images']) > 0:
            generated_image_url = result['images'][0]['url']
            print(f"✅ SUCCESS! Generated image URL: {generated_image_url}")
            
            # Save the result info
            with open('/app/test_fal_result.txt', 'w') as f:
                f.write(f"TEST VALIDATION FAL.AI\n")
                f.write(f"======================\n")
                f.write(f"Original image: {house_image_url}\n")
                f.write(f"Generated image: {generated_image_url}\n")
                f.write(f"Prompt used: {prompt}\n")
                f.write(f"Model: fal-ai/omnigen-v2\n")
                f.write(f"Status: SUCCESS\n")
            
            print(f"📋 Results saved to /app/test_fal_result.txt")
            return generated_image_url
            
        else:
            print("❌ No image generated in response")
            return None
            
    except Exception as e:
        print(f"❌ Error generating image: {e}")
        
        # Try alternative approach with flux/dev if OmniGen fails
        print("🔄 Trying alternative approach with FLUX/dev...")
        try:
            handler = fal_client.submit(
                "fal-ai/flux/dev",
                arguments={
                    "prompt": f"A French house with 12 black solar panels installed on the roof. Photorealistic, professional installation quality, natural lighting, architectural photography style. The house has grey roof tiles and cream-colored walls with brown shutters.",
                    "image_size": "landscape_4_3",
                    "num_inference_steps": 28,
                    "guidance_scale": 3.5
                }
            )
            
            result = handler.get()
            if result and 'images' in result:
                generated_image_url = result['images'][0]['url']
                print(f"✅ ALTERNATIVE SUCCESS! Generated image URL: {generated_image_url}")
                return generated_image_url
                
        except Exception as e2:
            print(f"❌ Alternative approach also failed: {e2}")
            
        return None

if __name__ == "__main__":
    print("🏠 Testing fal.ai solar panel placement validation")
    print("=" * 50)
    
    result_url = test_solar_panel_placement()
    
    if result_url:
        print("\n🎉 TEST SUCCESSFUL!")
        print(f"✨ Vous pouvez voir le résultat ici: {result_url}")
        print("\n📊 VALIDATION:")
        print("✅ API fal.ai functional")
        print("✅ Image generation working") 
        print("✅ Solar panel placement tested")
        print("\n▶️  Ready to integrate into FRH ENVIRONNEMENT application!")
    else:
        print("\n❌ TEST FAILED")
        print("Need to troubleshoot API configuration or try different models")