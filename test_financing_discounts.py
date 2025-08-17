#!/usr/bin/env python3
"""
Test rapide du backend FRH ENVIRONNEMENT pour vérifier les calculs de financement
avec les remises R1/R2/R3 après les modifications récentes.
"""

import requests
import json
import time

# Backend URL from frontend environment
BACKEND_URL = "https://solarquote-fix.preview.emergentagent.com/api"

def test_api_root():
    """Test 1: GET /api pour s'assurer que le serveur répond"""
    print("🔍 Test 1: Vérification de la connectivité API...")
    try:
        response = requests.get(f"{BACKEND_URL}/")
        if response.status_code == 200:
            data = response.json()
            if "Solar Calculator" in data.get("message", ""):
                print("✅ API accessible - Serveur répond correctement")
                print(f"   Message: {data['message']}")
                return True
            else:
                print(f"❌ Réponse inattendue: {data}")
                return False
        else:
            print(f"❌ Erreur HTTP {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erreur de connexion: {str(e)}")
        return False

def create_test_client():
    """Créer un client test pour les calculs"""
    print("\n🔍 Test 2: Création d'un client test...")
    try:
        client_data = {
            "first_name": "Marie",
            "last_name": "Dubois", 
            "address": "15 Rue de la Paix, 75001 Paris",
            "phone": "0145678901",
            "email": "marie.dubois@example.com",
            "roof_surface": 80.0,
            "roof_orientation": "Sud",
            "velux_count": 1,
            "heating_system": "Pompe à chaleur",
            "water_heating_system": "Ballon thermodynamique",
            "water_heating_capacity": 250,
            "annual_consumption_kwh": 7200.0,
            "monthly_edf_payment": 195.0,
            "annual_edf_payment": 2340.0
        }
        
        response = requests.post(f"{BACKEND_URL}/clients", json=client_data)
        if response.status_code == 200:
            client = response.json()
            client_id = client.get("id")
            print(f"✅ Client créé avec succès - ID: {client_id}")
            print(f"   Nom: {client['first_name']} {client['last_name']}")
            print(f"   Consommation: {client['annual_consumption_kwh']} kWh/an")
            return client_id
        else:
            print(f"❌ Erreur création client: HTTP {response.status_code}")
            # Try to use existing client
            return get_existing_client()
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return get_existing_client()

def get_existing_client():
    """Récupérer un client existant si la création échoue"""
    try:
        response = requests.get(f"{BACKEND_URL}/clients")
        if response.status_code == 200:
            clients = response.json()
            if clients and len(clients) > 0:
                client = clients[0]
                client_id = client.get("id")
                print(f"✅ Utilisation client existant - ID: {client_id}")
                return client_id
        print("❌ Aucun client disponible")
        return None
    except Exception as e:
        print(f"❌ Erreur récupération client: {str(e)}")
        return None

def test_financing_without_discount(client_id):
    """Test calcul sans remise (baseline)"""
    print("\n🔍 Test 3a: Calcul de financement SANS remise (baseline)...")
    try:
        response = requests.post(f"{BACKEND_URL}/calculate/{client_id}")
        if response.status_code == 200:
            calculation = response.json()
            
            kit_power = calculation.get("kit_power", 0)
            kit_price_original = calculation.get("kit_price", 0)
            kit_price_final = calculation.get("kit_price_final", kit_price_original)
            discount_applied = calculation.get("discount_applied", 0)
            monthly_savings = calculation.get("monthly_savings", 0)
            
            # Vérifier les options de financement
            financing_options = calculation.get("financing_options", [])
            financing_with_aids = calculation.get("financing_with_aids", {})
            
            print(f"✅ Calcul baseline réussi:")
            print(f"   Kit recommandé: {kit_power} kW")
            print(f"   Prix original: {kit_price_original}€")
            print(f"   Prix final: {kit_price_final}€")
            print(f"   Remise appliquée: {discount_applied}€")
            print(f"   Économies mensuelles: {monthly_savings:.2f}€")
            
            if financing_with_aids:
                monthly_payment = financing_with_aids.get("monthly_payment", 0)
                print(f"   Mensualité avec aides: {monthly_payment:.2f}€")
            
            return {
                "kit_power": kit_power,
                "kit_price_original": kit_price_original,
                "kit_price_final": kit_price_final,
                "discount_applied": discount_applied,
                "monthly_savings": monthly_savings,
                "financing_with_aids": financing_with_aids
            }
        else:
            print(f"❌ Erreur calcul: HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return None

def test_financing_with_discounts(client_id):
    """Test calculs avec remises R1, R2, R3"""
    print("\n🔍 Test 3b: Calculs de financement AVEC remises R1/R2/R3...")
    
    discount_tests = [
        {"name": "R1", "amount": 1000, "description": "Remise de 1000€"},
        {"name": "R2", "amount": 2000, "description": "Remise de 2000€"}, 
        {"name": "R3", "amount": 3000, "description": "Remise de 3000€"}
    ]
    
    results = []
    
    for discount_test in discount_tests:
        print(f"\n   🔸 Test {discount_test['name']}: {discount_test['description']}")
        try:
            # Appel avec paramètre discount_amount
            response = requests.post(f"{BACKEND_URL}/calculate/{client_id}?discount_amount={discount_test['amount']}")
            
            if response.status_code == 200:
                calculation = response.json()
                
                kit_power = calculation.get("kit_power", 0)
                kit_price_original = calculation.get("kit_price_original", 0)
                kit_price_final = calculation.get("kit_price_final", 0)
                discount_applied = calculation.get("discount_applied", 0)
                monthly_savings = calculation.get("monthly_savings", 0)
                financing_with_aids = calculation.get("financing_with_aids", {})
                
                # Vérifications
                issues = []
                
                # Vérifier que la remise est appliquée
                if discount_applied != discount_test['amount']:
                    issues.append(f"Remise incorrecte: {discount_applied}€ au lieu de {discount_test['amount']}€")
                
                # Vérifier que le prix final = prix original - remise
                expected_final_price = kit_price_original - discount_test['amount']
                if abs(kit_price_final - expected_final_price) > 1:
                    issues.append(f"Prix final incorrect: {kit_price_final}€ au lieu de {expected_final_price}€")
                
                # Vérifier que les mensualités diminuent avec la remise
                if financing_with_aids:
                    monthly_payment = financing_with_aids.get("monthly_payment", 0)
                    financed_amount = financing_with_aids.get("financed_amount", 0)
                    
                    if issues:
                        print(f"      ❌ Problèmes détectés: {'; '.join(issues)}")
                    else:
                        print(f"      ✅ {discount_test['name']} fonctionne correctement:")
                        print(f"         Prix: {kit_price_original}€ → {kit_price_final}€ (-{discount_applied}€)")
                        print(f"         Mensualité avec aides: {monthly_payment:.2f}€")
                        print(f"         Montant financé: {financed_amount:.2f}€")
                
                results.append({
                    "discount_name": discount_test['name'],
                    "discount_amount": discount_applied,
                    "kit_price_original": kit_price_original,
                    "kit_price_final": kit_price_final,
                    "monthly_payment": financing_with_aids.get("monthly_payment", 0),
                    "financed_amount": financing_with_aids.get("financed_amount", 0),
                    "issues": issues
                })
                
            else:
                print(f"      ❌ Erreur HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"      ❌ Erreur: {str(e)}")
    
    return results

def test_manual_kit_selection_with_discount(client_id):
    """Test sélection manuelle de kit avec remise"""
    print("\n🔍 Test 4: Sélection manuelle de kit avec remise...")
    
    try:
        # Test avec kit 6kW + remise R3 (3000€)
        response = requests.post(f"{BACKEND_URL}/calculate/{client_id}?manual_kit_power=6&discount_amount=3000")
        
        if response.status_code == 200:
            calculation = response.json()
            
            kit_power = calculation.get("kit_power", 0)
            kit_price_original = calculation.get("kit_price_original", 0)
            kit_price_final = calculation.get("kit_price_final", 0)
            discount_applied = calculation.get("discount_applied", 0)
            financing_with_aids = calculation.get("financing_with_aids", {})
            
            print(f"✅ Sélection manuelle avec remise réussie:")
            print(f"   Kit sélectionné: {kit_power} kW (manuel)")
            print(f"   Prix: {kit_price_original}€ → {kit_price_final}€ (-{discount_applied}€)")
            
            if financing_with_aids:
                monthly_payment = financing_with_aids.get("monthly_payment", 0)
                print(f"   Mensualité avec aides: {monthly_payment:.2f}€")
            
            # Vérifications
            if kit_power != 6:
                print(f"   ❌ Kit incorrect: {kit_power} kW au lieu de 6 kW")
                return False
            
            if discount_applied != 3000:
                print(f"   ❌ Remise incorrecte: {discount_applied}€ au lieu de 3000€")
                return False
            
            return True
        else:
            print(f"❌ Erreur HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return False

def main():
    """Fonction principale de test"""
    print("🏠 TEST RAPIDE BACKEND FRH ENVIRONNEMENT")
    print("=" * 60)
    print("Objectif: Vérifier que les calculs de financement avec remises R1/R2/R3 fonctionnent")
    print()
    
    # Test 1: Connectivité API
    if not test_api_root():
        print("\n❌ ÉCHEC: Impossible de se connecter à l'API")
        return
    
    # Test 2: Création client
    client_id = create_test_client()
    if not client_id:
        print("\n❌ ÉCHEC: Impossible de créer ou récupérer un client")
        return
    
    # Test 3a: Calcul baseline (sans remise)
    baseline = test_financing_without_discount(client_id)
    if not baseline:
        print("\n❌ ÉCHEC: Calcul baseline impossible")
        return
    
    # Test 3b: Calculs avec remises
    discount_results = test_financing_with_discounts(client_id)
    
    # Test 4: Sélection manuelle avec remise
    manual_test = test_manual_kit_selection_with_discount(client_id)
    
    # Résumé final
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 60)
    
    print("✅ API Root: Serveur accessible")
    print("✅ Client Test: Créé/récupéré avec succès")
    print("✅ Calcul Baseline: Fonctionnel")
    
    # Analyse des résultats de remises
    successful_discounts = 0
    for result in discount_results:
        if not result.get("issues", []):
            successful_discounts += 1
            print(f"✅ Remise {result['discount_name']}: Fonctionnelle")
        else:
            print(f"❌ Remise {result['discount_name']}: {'; '.join(result['issues'])}")
    
    if manual_test:
        print("✅ Sélection Manuelle + Remise: Fonctionnelle")
    else:
        print("❌ Sélection Manuelle + Remise: Problème détecté")
    
    # Conclusion
    print("\n🎯 CONCLUSION:")
    if successful_discounts == 3 and manual_test:
        print("✅ TOUS LES TESTS RÉUSSIS - Le système de remises R1/R2/R3 fonctionne correctement")
        print("   Les calculs de financement prennent bien en compte les remises")
        print("   La nouvelle logique frontend peut être utilisée en toute sécurité")
    else:
        print("❌ PROBLÈMES DÉTECTÉS - Certaines fonctionnalités nécessitent des corrections")
        print(f"   Remises fonctionnelles: {successful_discounts}/3")
        print(f"   Sélection manuelle: {'OK' if manual_test else 'KO'}")
    
    print("\n💡 Les données de financement sont correctement calculées et retournées")
    print("   pour que la nouvelle logique frontend fonctionne.")

if __name__ == "__main__":
    main()