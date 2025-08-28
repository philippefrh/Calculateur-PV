#!/usr/bin/env python3
"""
Test rapide du backend pour vérifier que les données PVGIS sont correctement renvoyées 
avec les données mensuelles (pvgis_monthly_data) pour le nouveau graphique de production mensuelle.

Test l'endpoint /api/calculate avec des données de test (région france, surface 50m², 
consommation 8000kWh/an) et vérifie que les données mensuelles sont présentes dans le 
format attendu avec les valeurs E_m pour chaque mois de 1 à 12.
"""

import requests
import json
import time
from typing import Dict, Any, Optional

# Backend URL from frontend environment
BACKEND_URL = "https://solar-quote-builder.preview.emergentagent.com/api"

class PVGISMonthlyDataTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.client_id = None
        
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
        
    def test_api_connectivity(self):
        """Test basic API connectivity"""
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "Solar Calculator" in data["message"]:
                    self.log_test("API Connectivity", True, f"API accessible: {data['message']}")
                else:
                    self.log_test("API Connectivity", False, f"Unexpected response: {data}")
            else:
                self.log_test("API Connectivity", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("API Connectivity", False, f"Connection error: {str(e)}")
    
    def create_test_client(self):
        """Create test client with specified data: région france, surface 50m², consommation 8000kWh/an"""
        try:
            client_data = {
                "first_name": "Test",
                "last_name": "PVGIS",
                "address": "75001 Paris, France",
                "phone": "0123456789",
                "email": "test.pvgis@example.com",
                "roof_surface": 50.0,  # 50m² comme demandé
                "roof_orientation": "Sud",
                "velux_count": 0,
                "heating_system": "Radiateurs électriques",
                "water_heating_system": "Ballon électrique standard",
                "water_heating_capacity": 200,
                "annual_consumption_kwh": 8000.0,  # 8000kWh/an comme demandé
                "monthly_edf_payment": 300.0,
                "annual_edf_payment": 3600.0
            }
            
            response = self.session.post(f"{self.base_url}/clients", json=client_data)
            if response.status_code == 200:
                client = response.json()
                
                if "id" in client and "latitude" in client and "longitude" in client:
                    self.client_id = client["id"]
                    lat, lon = client["latitude"], client["longitude"]
                    
                    # Vérifier que les coordonnées sont en France
                    if 42.0 <= lat <= 51.0 and -5.0 <= lon <= 8.0:
                        self.log_test("Create Test Client", True, 
                                    f"Client créé avec succès. ID: {self.client_id}, Coords: {lat:.4f}, {lon:.4f}, Consommation: 8000kWh/an, Surface: 50m²", 
                                    client)
                    else:
                        self.log_test("Create Test Client", False, 
                                    f"Coordonnées incorrectes pour la France: {lat}, {lon}", client)
                else:
                    self.log_test("Create Test Client", False, "Données manquantes dans la réponse", client)
            else:
                self.log_test("Create Test Client", False, f"HTTP {response.status_code}: {response.text}")
                # Try to use existing client as fallback
                self.use_existing_client()
        except Exception as e:
            self.log_test("Create Test Client", False, f"Erreur: {str(e)}")
            self.use_existing_client()
    
    def use_existing_client(self):
        """Use existing client as fallback"""
        try:
            response = self.session.get(f"{self.base_url}/clients")
            if response.status_code == 200:
                clients = response.json()
                if isinstance(clients, list) and len(clients) > 0:
                    client = clients[0]
                    self.client_id = client.get("id")
                    if self.client_id:
                        self.log_test("Use Existing Client", True, 
                                    f"Utilisation client existant: {client.get('first_name')} {client.get('last_name')} (ID: {self.client_id})")
                    else:
                        self.log_test("Use Existing Client", False, "Pas d'ID trouvé dans le client existant")
                else:
                    self.log_test("Use Existing Client", False, "Aucun client existant trouvé")
            else:
                self.log_test("Use Existing Client", False, f"Échec récupération clients: {response.status_code}")
        except Exception as e:
            self.log_test("Use Existing Client", False, f"Erreur: {str(e)}")
    
    def test_pvgis_monthly_data(self):
        """Test principal: vérifier les données mensuelles PVGIS pour le graphique"""
        if not self.client_id:
            self.log_test("PVGIS Monthly Data", False, "Pas de client ID disponible")
            return
            
        try:
            # Test avec région france comme demandé
            response = self.session.post(f"{self.base_url}/calculate/{self.client_id}?region=france")
            
            if response.status_code == 200:
                calculation = response.json()
                
                # Vérifier que pvgis_monthly_data est présent
                if "pvgis_monthly_data" not in calculation:
                    self.log_test("PVGIS Monthly Data", False, "Champ 'pvgis_monthly_data' manquant dans la réponse", calculation)
                    return
                
                monthly_data = calculation["pvgis_monthly_data"]
                
                # Vérifier que c'est une liste
                if not isinstance(monthly_data, list):
                    self.log_test("PVGIS Monthly Data", False, f"pvgis_monthly_data devrait être une liste, reçu: {type(monthly_data)}", monthly_data)
                    return
                
                # Vérifier qu'on a 12 mois de données
                if len(monthly_data) != 12:
                    self.log_test("PVGIS Monthly Data", False, f"Attendu 12 mois de données, reçu: {len(monthly_data)}", monthly_data)
                    return
                
                # Vérifier le format des données mensuelles
                issues = []
                e_m_values = []
                
                for i, month_data in enumerate(monthly_data):
                    month_num = i + 1
                    
                    # Vérifier que chaque mois a les champs requis
                    if not isinstance(month_data, dict):
                        issues.append(f"Mois {month_num}: devrait être un dict, reçu {type(month_data)}")
                        continue
                    
                    # Vérifier la présence de E_m (production mensuelle)
                    if "E_m" not in month_data:
                        issues.append(f"Mois {month_num}: champ 'E_m' manquant")
                        continue
                    
                    e_m = month_data["E_m"]
                    
                    # Vérifier que E_m est un nombre positif
                    if not isinstance(e_m, (int, float)) or e_m <= 0:
                        issues.append(f"Mois {month_num}: E_m devrait être un nombre positif, reçu {e_m}")
                        continue
                    
                    # Vérifier que E_m est dans une plage raisonnable (50-1000 kWh/mois pour la France)
                    if not (50 <= e_m <= 1000):
                        issues.append(f"Mois {month_num}: E_m={e_m} kWh semble incorrect (attendu 50-1000 kWh)")
                        continue
                    
                    e_m_values.append(e_m)
                
                # Vérifier qu'on a des valeurs E_m pour tous les mois
                if len(e_m_values) != 12:
                    issues.append(f"Seulement {len(e_m_values)}/12 mois ont des valeurs E_m valides")
                
                # Vérifier la variation saisonnière (été > hiver en France)
                if len(e_m_values) == 12:
                    # Mois d'été (juin, juillet, août = indices 5, 6, 7)
                    summer_avg = (e_m_values[5] + e_m_values[6] + e_m_values[7]) / 3
                    # Mois d'hiver (décembre, janvier, février = indices 11, 0, 1)
                    winter_avg = (e_m_values[11] + e_m_values[0] + e_m_values[1]) / 3
                    
                    if summer_avg <= winter_avg:
                        issues.append(f"Production été ({summer_avg:.1f} kWh) devrait être > hiver ({winter_avg:.1f} kWh)")
                
                # Vérifier la production annuelle totale
                total_annual = sum(e_m_values) if e_m_values else 0
                if total_annual < 3000 or total_annual > 12000:
                    issues.append(f"Production annuelle totale {total_annual:.0f} kWh semble incorrecte (attendu 3000-12000 kWh)")
                
                # Vérifier les autres champs utiles pour le graphique
                additional_info = {}
                if "kit_power" in calculation:
                    additional_info["kit_power"] = calculation["kit_power"]
                if "estimated_production" in calculation:
                    additional_info["estimated_production"] = calculation["estimated_production"]
                    # Vérifier cohérence avec la somme mensuelle
                    if abs(calculation["estimated_production"] - total_annual) > 50:
                        issues.append(f"Production estimée {calculation['estimated_production']:.0f} != somme mensuelle {total_annual:.0f}")
                
                if issues:
                    self.log_test("PVGIS Monthly Data", False, f"Problèmes détectés: {'; '.join(issues)}", {
                        "monthly_data": monthly_data,
                        "e_m_values": e_m_values,
                        "additional_info": additional_info
                    })
                else:
                    # Test réussi - données prêtes pour le graphique
                    summer_avg = (e_m_values[5] + e_m_values[6] + e_m_values[7]) / 3
                    winter_avg = (e_m_values[11] + e_m_values[0] + e_m_values[1]) / 3
                    
                    self.log_test("PVGIS Monthly Data", True, 
                                f"✅ DONNÉES MENSUELLES PVGIS CORRECTES: 12 mois avec valeurs E_m de {min(e_m_values):.0f} à {max(e_m_values):.0f} kWh. Production annuelle: {total_annual:.0f} kWh. Variation saisonnière: été {summer_avg:.0f} kWh/mois > hiver {winter_avg:.0f} kWh/mois. Kit: {additional_info.get('kit_power', 'N/A')}kW. PRÊT POUR GRAPHIQUE AVEC BARRES JAUNES.", 
                                {
                                    "monthly_data_count": len(monthly_data),
                                    "e_m_values": e_m_values,
                                    "total_annual_production": total_annual,
                                    "summer_avg": summer_avg,
                                    "winter_avg": winter_avg,
                                    "kit_info": additional_info
                                })
                
            else:
                self.log_test("PVGIS Monthly Data", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("PVGIS Monthly Data", False, f"Erreur: {str(e)}")
    
    def test_chart_data_format(self):
        """Test que les données sont dans le bon format pour le graphique"""
        if not self.client_id:
            self.log_test("Chart Data Format", False, "Pas de client ID disponible")
            return
            
        try:
            response = self.session.post(f"{self.base_url}/calculate/{self.client_id}?region=france")
            
            if response.status_code == 200:
                calculation = response.json()
                monthly_data = calculation.get("pvgis_monthly_data", [])
                
                if not monthly_data:
                    self.log_test("Chart Data Format", False, "Pas de données mensuelles disponibles")
                    return
                
                # Simuler la création du graphique
                chart_data = []
                months_fr = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
                
                issues = []
                
                for i, month_data in enumerate(monthly_data):
                    if "E_m" not in month_data:
                        issues.append(f"Mois {i+1}: E_m manquant")
                        continue
                    
                    chart_point = {
                        "month": months_fr[i],
                        "production": month_data["E_m"],
                        "color": "#FFD700"  # Couleur jaune pour les barres
                    }
                    chart_data.append(chart_point)
                
                if issues:
                    self.log_test("Chart Data Format", False, f"Problèmes format graphique: {'; '.join(issues)}")
                else:
                    # Vérifier qu'on peut créer un graphique complet
                    if len(chart_data) == 12:
                        max_production = max(point["production"] for point in chart_data)
                        min_production = min(point["production"] for point in chart_data)
                        
                        self.log_test("Chart Data Format", True, 
                                    f"✅ FORMAT GRAPHIQUE CORRECT: 12 points de données prêts pour barres jaunes. Production min: {min_production:.0f} kWh, max: {max_production:.0f} kWh. Données compatibles avec nouveau graphique de production mensuelle.", 
                                    {
                                        "chart_data_sample": chart_data[:3],  # Montrer les 3 premiers mois
                                        "total_points": len(chart_data),
                                        "production_range": f"{min_production:.0f}-{max_production:.0f} kWh"
                                    })
                    else:
                        self.log_test("Chart Data Format", False, f"Données incomplètes pour graphique: {len(chart_data)}/12 points")
                        
            else:
                self.log_test("Chart Data Format", False, f"Impossible de récupérer les données: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Chart Data Format", False, f"Erreur: {str(e)}")
    
    def run_all_tests(self):
        """Exécuter tous les tests"""
        print("🔍 TEST RAPIDE BACKEND - DONNÉES PVGIS MENSUELLES")
        print("=" * 70)
        print("Test endpoint /api/calculate avec données de test:")
        print("- Région: France")
        print("- Surface: 50m²") 
        print("- Consommation: 8000kWh/an")
        print("- Vérification: données mensuelles E_m pour graphique")
        print("=" * 70)
        
        # Exécuter les tests
        self.test_api_connectivity()
        self.create_test_client()
        self.test_pvgis_monthly_data()  # Test principal
        self.test_chart_data_format()
        
        # Résumé
        print("\n" + "=" * 70)
        print("📊 RÉSUMÉ DES TESTS")
        print("=" * 70)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"Tests totaux: {total}")
        print(f"Réussis: {passed}")
        print(f"Échoués: {total - passed}")
        print(f"Taux de réussite: {(passed/total)*100:.1f}%")
        
        # Afficher les tests échoués
        failed_tests = [result for result in self.test_results if not result["success"]]
        if failed_tests:
            print(f"\n❌ TESTS ÉCHOUÉS ({len(failed_tests)}):")
            for result in failed_tests:
                print(f"  - {result['test']}: {result['details']}")
        else:
            print(f"\n✅ TOUS LES TESTS RÉUSSIS!")
            print("🎯 Les données PVGIS mensuelles sont correctement renvoyées")
            print("📊 Format compatible avec le nouveau graphique de production mensuelle")
            print("🟡 Prêt pour génération des barres jaunes")
        
        return passed == total

if __name__ == "__main__":
    tester = PVGISMonthlyDataTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)