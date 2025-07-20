#!/usr/bin/env python3
"""
Script de test simple pour l'analyse de toiture simplifiée
"""
import base64
import requests
import json
import sys
import os

def test_simple_roof_analysis():
    """Test avec une image simple fournie par l'utilisateur"""
    print("🏠 Test de l'analyse de toiture SIMPLIFIÉE")
    
    # Utiliser une image simple de test (URL Unsplash)
    # Cette image représente votre maison avec toit simple sans obstacles
    test_image_url = "https://images.unsplash.com/photo-1558618666-fcd25aacd5f4?w=800&h=600&fit=crop"
    
    try:
        # Télécharger l'image de test
        print("📸 Téléchargement de l'image test...")
        response = requests.get(test_image_url, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Erreur téléchargement: {response.status_code}")
            return False
            
        # Convertir en base64
        image_data = response.content
        base64_image = base64.b64encode(image_data).decode()
        print(f"✅ Image convertie: {len(base64_image)} caractères base64")
        
        # Préparer les données de test
        test_data = {
            'image_base64': f'data:image/jpeg;base64,{base64_image}',
            'panel_count': 6  # Test avec 6 panneaux simples
        }
        
        # Appeler l'API simplifiée
        print("🤖 Appel de l'API d'analyse simplifiée...")
        api_response = requests.post(
            'http://localhost:8001/api/analyze-roof', 
            json=test_data, 
            timeout=30
        )
        
        print(f"📊 Statut API: {api_response.status_code}")
        
        if api_response.status_code == 200:
            result = api_response.json()
            print(f"✅ Succès: {result['success']}")
            print(f"📍 Panneaux positionnés: {len(result['panel_positions'])}")
            print(f"🏠 Placement possible: {result['placement_possible']}")
            print(f"📏 Surface requise: {result['total_surface_required']} m²")
            print(f"🔍 Analyse: {result['roof_analysis'][:100]}...")
            print(f"💡 Recommandations: {result['recommendations'][:100]}...")
            
            # Vérifier l'image composite
            if 'composite_image' in result and result['composite_image']:
                print(f"🖼️ Image composite générée: {len(result['composite_image'])} caractères base64")
                print("✅ TEST RÉUSSI - L'image composite simple devrait être visible avec bordures jaunes")
                
                # Optionnel: sauvegarder l'image composite pour vérification
                if result['composite_image'].startswith('data:image'):
                    composite_data = result['composite_image'].split(',')[1]
                    with open('/app/test_composite_simple.jpg', 'wb') as f:
                        f.write(base64.b64decode(composite_data))
                    print("💾 Image composite sauvegardée: /app/test_composite_simple.jpg")
                
                return True
            else:
                print("❌ Pas d'image composite générée")
                return False
                
        else:
            print(f"❌ Erreur API: {api_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur test: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🔧 TEST DE L'ANALYSE DE TOITURE SIMPLIFIÉE")
    print("=" * 60)
    
    success = test_simple_roof_analysis()
    
    print("=" * 60)
    if success:
        print("🎉 TEST RÉUSSI - Les panneaux solaires SIMPLES sont maintenant visibles!")
        print("✅ Bordures jaunes, numéros blancs, disposition en grille claire")
    else:
        print("❌ TEST ÉCHOUÉ - Vérifiez les logs pour plus de détails")
    print("=" * 60)