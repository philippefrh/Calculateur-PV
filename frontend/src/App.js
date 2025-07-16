import React, { useState, useEffect } from "react";
import './App.css';

const API = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001/api';

// Écran de démarrage avec vrais logos
const StartScreen = ({ onStart }) => {
  
  const handleClick = () => {
    console.log("Button clicked!");
    onStart();
  };
  
  return (
    <div className="start-screen">
      {/* Logo FRH Environnement officiel */}
      <div className="company-header">
        <div className="company-image">
          <img 
            src="https://cdn-dhoin.nitrocdn.com/EuBhgITwlcEgvZudhGdVBYWQskHAaTgE/assets/images/optimized/rev-a144ac5/france-renovhabitat.fr/contenu/2021/uploads/2021/05/FRH2-logo-HORIZONTALE.png" 
            alt="FRH Environnement - Installateur Photovoltaïque"
            className="company-logo-image centered"
          />
        </div>
        <h1 className="company-title">Installateur Photovoltaïque</h1>
        <p className="company-subtitle">FRH ENVIRONNEMENT - Énergie Solaire Professionnel</p>
        <div className="company-stats">
          <div className="stat-item">
            <span className="stat-number">+ de 5000</span>
            <span className="stat-label">Installations réalisées</span>
          </div>
          <div className="stat-item">
            <span className="stat-number">86%</span>
            <span className="stat-label">de clients nous recommandent</span>
          </div>
        </div>
      </div>

      {/* Logos de certifications */}
      <div className="certifications">
        <div className="certification-item">
          <img 
            src="https://france-renovhabitat.fr/contenu/2021/uploads/2021/05/RGE-logo.png" 
            alt="RGE - Reconnu Garant de l'Environnement"
            className="certification-logo"
          />
        </div>
        <div className="certification-item">
          <img 
            src="https://france-renovhabitat.fr/contenu/2021/uploads/2021/05/AGIR-PLUS-EDF-logo.png" 
            alt="AGIR PLUS EDF"
            className="certification-logo"
          />
        </div>
        <div className="certification-item">
          <img 
            src="https://france-renovhabitat.fr/contenu/2021/uploads/2021/05/FRH-logo.png" 
            alt="FRH Environnement"
            className="certification-logo"
          />
        </div>
        <div className="certification-item">
          <img 
            src="https://france-renovhabitat.fr/contenu/2021/uploads/2021/05/MMA-logo.png" 
            alt="MMA Partenaire"
            className="certification-logo"
          />
        </div>
        <div className="certification-item">
          <img 
            src="https://france-renovhabitat.fr/contenu/2021/uploads/2021/05/FFB-logo.png" 
            alt="FFB - Fédération Française du Bâtiment"
            className="certification-logo"
          />
        </div>
      </div>
      
      <button className="start-button" onClick={handleClick}>
        🌞 Commencer l'Étude Solaire Gratuite
      </button>
      
      <div className="benefits">
        <div className="benefit-item">
          <span className="benefit-icon">✓</span>
          <span>Réalisez jusqu'à 70% d'économies sur vos factures d'électricité</span>
        </div>
        <div className="benefit-item">
          <span className="benefit-icon">✓</span>
          <span>Un accompagnement de A à Z pour votre projet solaire</span>
        </div>
        <div className="benefit-item">
          <span className="benefit-icon">✓</span>
          <span>Panneaux garantis 25 ans et garanties de production</span>
        </div>
        <div className="benefit-item">
          <span className="benefit-icon">✓</span>
          <span>Installation fiable et performante par nos installateurs certifiés RGE</span>
        </div>
        <div className="benefit-item">
          <span className="benefit-icon">✓</span>
          <span>Profitez des dispositifs d'aides et de subventions</span>
        </div>
      </div>
    </div>
  );
};

function App() {
  const [currentStep, setCurrentStep] = useState('start');
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    address: '',
    roofSurface: '',
    roofOrientation: '',
    veluxCount: 0,
    heatingSystem: '',
    additionalHeatingSystems: [],
    waterHeatingSystem: '',
    waterHeatingCapacity: '',
    washingMachine: '',
    dryer: '',
    dishwasher: '',
    refrigerator: '',
    electricOven: '',
    cookingPlate: '',
    hood: '',
    vmc: '',
    meterType: '',
    meterPower: '',
    phaseType: '',
    annualConsumption: '',
    monthlyEdfPayment: '',
    annualEdfPayment: '',
    useManualKit: false,
    manualKit: null,
    selectedManualKit: null
  });
  const [calculationResults, setCalculationResults] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleStart = () => {
    setCurrentStep(1);
  };

  const handleNext = () => {
    setCurrentStep(currentStep + 1);
  };

  const handlePrevious = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const validateForm = () => {
    if (currentStep === 1) {
      if (!formData.firstName || !formData.lastName || !formData.address) {
        alert('Veuillez remplir tous les champs obligatoires');
        return false;
      }
    }
    return true;
  };

  const handleCalculate = async () => {
    if (!validateForm()) return;
    
    setIsLoading(true);
    setCurrentStep('calculating');
    
    try {
      const clientData = {
        first_name: formData.firstName,
        last_name: formData.lastName,
        address: formData.address,
        roof_surface: parseFloat(formData.roofSurface),
        roof_orientation: formData.roofOrientation,
        velux_count: parseInt(formData.veluxCount) || 0,
        heating_system: formData.heatingSystem,
        water_heating_system: formData.waterHeatingSystem,
        water_heating_capacity: parseInt(formData.waterHeatingCapacity) || null,
        annual_consumption_kwh: parseFloat(formData.annualConsumption),
        monthly_edf_payment: parseFloat(formData.monthlyEdfPayment),
        annual_edf_payment: parseFloat(formData.annualEdfPayment)
      };
      
      const clientResponse = await fetch(`${API}/clients`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(clientData)
      });
      
      if (!clientResponse.ok) {
        throw new Error('Erreur lors de la création du client');
      }
      
      const client = await clientResponse.json();
      
      const calculationResponse = await fetch(`${API}/calculate/${client.id}`, {
        method: 'POST'
      });
      
      if (!calculationResponse.ok) {
        throw new Error('Erreur lors du calcul');
      }
      
      const calculation = await calculationResponse.json();
      setCalculationResults(calculation);
      setCurrentStep('results');
      
    } catch (error) {
      console.error('Erreur lors du calcul:', error);
      alert('Une erreur s\'est produite lors du calcul. Veuillez réessayer.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  if (currentStep === 'start') {
    return (
      <div className="App">
        <StartScreen onStart={handleStart} />
      </div>
    );
  }

  if (currentStep === 'calculating') {
    return (
      <div className="App">
        <div className="loading-screen">
          <div className="loading-content">
            <div className="loading-spinner"></div>
            <h2>Calcul en cours...</h2>
            <p>Nous analysons votre profil et calculons votre potentiel solaire</p>
          </div>
        </div>
      </div>
    );
  }

  if (currentStep === 'results') {
    return (
      <div className="App">
        <div className="results-screen">
          <h2>Résultats de votre étude solaire</h2>
          {calculationResults && (
            <div className="results-content">
              <div className="result-item">
                <h3>Kit recommandé: {calculationResults.kit_power}kW</h3>
                <p>Nombre de panneaux: {calculationResults.panel_count}</p>
                <p>Production estimée: {calculationResults.estimated_production} kWh/an</p>
                <p>Économies annuelles: {calculationResults.estimated_savings}€</p>
              </div>
              
              <div className="financing-section">
                <h3>💰 Analyse financière complète</h3>
                
                <div className="financial-summary">
                  <div className="financial-item">
                    <span className="financial-label">💳 Investissement:</span>
                    <span className="financial-value">{calculationResults.kit_price?.toLocaleString()} € TTC</span>
                  </div>
                  <div className="financial-item">
                    <span className="financial-label">🎁 Aides totales:</span>
                    <span className="financial-value success">-{Math.round(calculationResults.total_aids)} €</span>
                  </div>
                  <div className="financial-item">
                    <span className="financial-label">💸 Reste à financer:</span>
                    <span className="financial-value">{(calculationResults.kit_price - calculationResults.total_aids).toLocaleString()} €</span>
                  </div>
                </div>

                <div className="aids-breakdown">
                  <h4>🎁 Détail des aides disponibles</h4>
                  <div className="aid-item">
                    <span>Prime autoconsommation EDF:</span>
                    <span className="aid-amount">{calculationResults.autoconsumption_aid} €</span>
                  </div>
                  {calculationResults.tva_refund > 0 && (
                    <div className="aid-item">
                      <span>TVA remboursée 20%:</span>
                      <span className="aid-amount">{Math.round(calculationResults.tva_refund)} €</span>
                    </div>
                  )}
                  <div className="aid-item total-aid">
                    <span><strong>Total des aides:</strong></span>
                    <span className="aid-amount"><strong>{Math.round(calculationResults.total_aids)} €</strong></span>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          <div className="action-buttons">
            <button onClick={() => setCurrentStep('start')} className="restart-button">
              🔄 Nouvelle simulation
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="App">
      <div className="form-container">
        <div className="progress-bar">
          <div className="progress-fill" style={{width: `${(currentStep / 4) * 100}%`}}></div>
        </div>
        
        <div className="step-indicator">
          <span>Étape {currentStep} sur 4</span>
        </div>

        {currentStep === 1 && (
          <div className="form-step">
            <h2>👤 Informations personnelles</h2>
            <div className="form-group">
              <label>Prénom *</label>
              <input 
                type="text" 
                value={formData.firstName}
                onChange={(e) => handleInputChange('firstName', e.target.value)}
                placeholder="Votre prénom"
              />
            </div>
            <div className="form-group">
              <label>Nom *</label>
              <input 
                type="text" 
                value={formData.lastName}
                onChange={(e) => handleInputChange('lastName', e.target.value)}
                placeholder="Votre nom de famille"
              />
            </div>
            <div className="form-group">
              <label>Adresse *</label>
              <input 
                type="text" 
                value={formData.address}
                onChange={(e) => handleInputChange('address', e.target.value)}
                placeholder="Votre adresse complète"
              />
            </div>
          </div>
        )}

        {currentStep === 2 && (
          <div className="form-step">
            <h2>🏠 Informations techniques</h2>
            <div className="form-group">
              <label>Surface de toiture disponible (m²) *</label>
              <input 
                type="number" 
                value={formData.roofSurface}
                onChange={(e) => handleInputChange('roofSurface', e.target.value)}
                placeholder="ex: 50"
              />
            </div>
            <div className="form-group">
              <label>Orientation de la toiture *</label>
              <select 
                value={formData.roofOrientation}
                onChange={(e) => handleInputChange('roofOrientation', e.target.value)}
              >
                <option value="">Choisir l'orientation</option>
                <option value="Sud">Sud</option>
                <option value="Sud-Est">Sud-Est</option>
                <option value="Sud-Ouest">Sud-Ouest</option>
                <option value="Est">Est</option>
                <option value="Ouest">Ouest</option>
              </select>
            </div>
            <div className="form-group">
              <label>Nombre de Velux</label>
              <input 
                type="number" 
                value={formData.veluxCount}
                onChange={(e) => handleInputChange('veluxCount', e.target.value)}
                placeholder="0 si aucun"
              />
            </div>
          </div>
        )}

        {currentStep === 3 && (
          <div className="form-step">
            <h2>🔥 Système de chauffage</h2>
            <div className="form-group">
              <label>Système de chauffage principal *</label>
              <select 
                value={formData.heatingSystem}
                onChange={(e) => handleInputChange('heatingSystem', e.target.value)}
              >
                <option value="">Choisir le système</option>
                <option value="Pompe à chaleur Air-Air">Pompe à chaleur Air-Air</option>
                <option value="Pompe à chaleur Air-Eau">Pompe à chaleur Air-Eau</option>
                <option value="Chaudière gaz">Chaudière gaz</option>
                <option value="Chaudière fioul">Chaudière fioul</option>
                <option value="Radiateurs électriques">Radiateurs électriques</option>
                <option value="Cheminée">Cheminée</option>
                <option value="Poêle">Poêle</option>
                <option value="Chaudière électrique">Chaudière électrique</option>
              </select>
            </div>
            <div className="form-group">
              <label>Système de chauffage de l'eau *</label>
              <select 
                value={formData.waterHeatingSystem}
                onChange={(e) => handleInputChange('waterHeatingSystem', e.target.value)}
              >
                <option value="">Choisir le système</option>
                <option value="Ballon électrique standard">Ballon électrique standard</option>
                <option value="Ballon thermodynamique">Ballon thermodynamique</option>
                <option value="Chaudière gaz">Chaudière gaz</option>
                <option value="Chauffe-eau solaire">Chauffe-eau solaire</option>
              </select>
            </div>
          </div>
        )}

        {currentStep === 4 && (
          <div className="form-step">
            <h2>⚡ Consommation électrique</h2>
            <div className="form-group">
              <label>Consommation annuelle (kWh) *</label>
              <input 
                type="number" 
                value={formData.annualConsumption}
                onChange={(e) => handleInputChange('annualConsumption', e.target.value)}
                placeholder="ex: 6500"
              />
            </div>
            <div className="form-group">
              <label>Mensualité EDF (€) *</label>
              <input 
                type="number" 
                value={formData.monthlyEdfPayment}
                onChange={(e) => {
                  const value = e.target.value;
                  handleInputChange('monthlyEdfPayment', value);
                  if (value) {
                    handleInputChange('annualEdfPayment', (parseFloat(value) * 12).toString());
                  }
                }}
                placeholder="ex: 180"
              />
            </div>
            <div className="form-group">
              <label>Total payé à l'année (€)</label>
              <input 
                type="number" 
                value={formData.annualEdfPayment}
                readOnly
                className="readonly-input"
              />
            </div>
          </div>
        )}

        <div className="navigation-buttons">
          {currentStep > 1 && (
            <button onClick={handlePrevious} className="nav-button prev">
              ← Précédent
            </button>
          )}
          
          {currentStep < 4 ? (
            <button onClick={handleNext} className="nav-button next">
              Suivant →
            </button>
          ) : (
            <button onClick={handleCalculate} className="nav-button calculate">
              Commencer le Calcul
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;