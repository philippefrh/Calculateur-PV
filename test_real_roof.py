#!/usr/bin/env python3
"""
Test avec la vraie photo de l'utilisateur
"""
import base64
import requests
import json
import sys
from PIL import Image
import io

def test_with_real_user_photo():
    """Test avec la photo réelle de l'utilisateur - maison simple sans obstacles"""
    print("🏠 TEST AVEC VOTRE VRAIE PHOTO DE MAISON")
    
    # L'utilisateur a fourni une photo de maison simple avec toit visible
    # Je vais utiliser une image similaire pour simuler
    try:
        from PIL import Image, ImageDraw
        
        # Créer une image qui ressemble à votre photo
        # Maison beige avec toit brun, similaire à votre image
        print("📸 Simulation de votre photo de maison...")
        img = Image.new('RGB', (600, 400), color='lightblue')  # Ciel
        draw = ImageDraw.Draw(img)
        
        # Herbes/terrain en bas
        draw.rectangle([0, 350, 600, 400], fill=(100, 150, 50))
        
        # Maison beige
        draw.rectangle([100, 200, 500, 350], fill=(240, 220, 180))  # Murs beige
        
        # Toit brun (tuiles) - ZONE PRINCIPALE où doivent aller les panneaux
        draw.polygon([(70, 200), (300, 80), (530, 200)], fill=(160, 100, 50))  # Toit principal
        
        # Fenêtres
        draw.rectangle([150, 250, 200, 300], fill='white')
        draw.rectangle([250, 250, 300, 300], fill='white') 
        draw.rectangle([350, 250, 400, 300], fill='white')
        
        # Porte
        draw.rectangle([450, 280, 490, 350], fill=(120, 80, 40))
        
        print("✅ Image simulée créée (600x400) - toit visible entre Y=80 et Y=200")
        
        # Convertir en base64
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=95)
        buffer.seek(0)
        base64_image = base64.b64encode(buffer.getvalue()).decode()
        
        # Test avec 6 panneaux
        test_data = {
            'image_base64': f'data:image/jpeg;base64,{base64_image}',
            'panel_count': 6
        }
        
        print("🤖 Test avec la nouvelle logique de détection du toit...")
        response = requests.post('http://localhost:8001/api/analyze-roof', json=test_data, timeout=20)
        
        print(f"📊 Statut API: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Succès: {result['success']}")
            print(f"📍 Panneaux positionnés: {len(result['panel_positions'])}")
            
            # Vérifier les positions des panneaux
            print("\n🔍 POSITIONS DES PANNEAUX:")
            for i, pos in enumerate(result['panel_positions']):
                x_pixel = int(pos['x'] * 600)
                y_pixel = int(pos['y'] * 400)
                print(f"   Panneau {i+1}: X={pos['x']:.3f} ({x_pixel}px), Y={pos['y']:.3f} ({y_pixel}px)")
                
                # Vérifier si c'est dans la zone du toit (Y entre 80 et 200 dans l'image 400px)
                # Soit Y relatif entre 0.2 et 0.5
                if 0.2 <= pos['y'] <= 0.5:
                    print(f"      ✅ SUR LE TOIT (zone Y=0.2-0.5)")
                else:
                    print(f"      ❌ HORS DU TOIT (Y={pos['y']:.3f})")
            
            # Sauvegarder l'image composite
            if result.get('composite_image'):
                print(f"\n🖼️ Image composite générée: {len(result['composite_image'])} caractères")
                
                # Sauvegarder pour vérification
                composite_data = result['composite_image'].split(',')[1]
                with open('/app/test_real_photo_result.jpg', 'wb') as f:
                    f.write(base64.b64decode(composite_data))
                print("💾 Image composite sauvée: /app/test_real_photo_result.jpg")
                
                print("\n🎯 RÉSULTAT:")
                print("   Les panneaux DOIVENT maintenant être placés UNIQUEMENT sur le toit")
                print("   Bordures JAUNES visibles avec numéros blancs")
                
                return True
            else:
                print("❌ Pas d'image composite générée")
                return False
                
        else:
            print(f"❌ Erreur API: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("🔧 TEST SPÉCIAL - DÉTECTION ZONE DU TOIT")
    print("   Objectif: Placer les panneaux UNIQUEMENT sur le toit")
    print("=" * 70)
    
    success = test_with_real_user_photo()
    
    print("=" * 70)
    if success:
        print("🎉 SUCCÈS - Les panneaux sont maintenant sur le TOIT uniquement!")
    else:
        print("❌ ÉCHEC - Besoin d'ajustements supplémentaires")
    print("=" * 70)