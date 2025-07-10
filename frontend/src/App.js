import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Logo d'autonomie - Composant principal demandé
const AutonomyLogo = () => (
  <div className="autonomy-logo-container">
    <div className="autonomy-logo">
      <div className="autonomy-section red">
        <span className="autonomy-text">POURCENTAGE D'AUTONOMIE DE COULEUR ROUGE</span>
        <span className="autonomy-status negative">Négatif</span>
      </div>
      <div className="autonomy-section green">
        <span className="autonomy-text">POURCENTAGE D'AUTONOMIE DE COULEUR VERT</span>
        <span className="autonomy-status positive">Positif</span>
      </div>
    </div>
  </div>
);

// Écran de démarrage
const StartScreen = ({ onStart }) => (
  <div className="start-screen">
    <div className="company-header">
      <h1 className="company-title">FRH ENVIRONNEMENT</h1>
      <p className="company-subtitle">Énergie Solaire - Professionnel</p>
    </div>
    
    <AutonomyLogo />
    
    <div className="certifications">
      <div className="cert-badge">RGE QualiPV 2025</div>
      <div className="cert-badge">RGE QualiPac 2025</div>
      <div className="cert-badge">FFB Adhérent</div>
      <div className="cert-badge">Partenaire AGIR PLUS EDF</div>
    </div>
    
    <button className="start-button" onClick={onStart}>
      Commencer l'Étude Solaire
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
    </div>
  </div>
);

// Formulaire étape 1 - Informations personnelles
const PersonalInfoForm = ({ formData, setFormData, onNext }) => {
  const handleSubmit = (e) => {
    e.preventDefault();
    if (formData.firstName && formData.lastName && formData.address) {
      onNext();
    }
  };

  return (
    <div className="form-container">
      <h2>Informations Personnelles</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Prénom *</label>
          <input
            type="text"
            value={formData.firstName}
            onChange={(e) => setFormData({...formData, firstName: e.target.value})}
            required
          />
        </div>
        <div className="form-group">
          <label>Nom *</label>
          <input
            type="text"
            value={formData.lastName}
            onChange={(e) => setFormData({...formData, lastName: e.target.value})}
            required
          />
        </div>
        <div className="form-group">
          <label>Adresse exacte de votre maison *</label>
          <input
            type="text"
            value={formData.address}
            onChange={(e) => setFormData({...formData, address: e.target.value})}
            placeholder="Adresse complète avec code postal et ville"
            required
          />
        </div>
        <button type="submit" className="next-button">Suivant</button>
      </form>
    </div>
  );
};

// Formulaire étape 2 - Informations techniques
const TechnicalInfoForm = ({ formData, setFormData, onNext, onPrevious }) => {
  const handleSubmit = (e) => {
    e.preventDefault();
    if (formData.roofSurface && formData.roofOrientation) {
      onNext();
    }
  };

  return (
    <div className="form-container">
      <h2>Informations Techniques</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Surface de votre toiture la mieux orientée (m²) *</label>
          <input
            type="number"
            value={formData.roofSurface}
            onChange={(e) => setFormData({...formData, roofSurface: e.target.value})}
            min="10"
            max="200"
            required
          />
        </div>
        <div className="form-group">
          <label>Orientation de votre toiture *</label>
          <select
            value={formData.roofOrientation}
            onChange={(e) => setFormData({...formData, roofOrientation: e.target.value})}
            required
          >
            <option value="">Sélectionnez une orientation</option>
            <option value="Sud">Sud</option>
            <option value="Sud-Est">Sud-Est</option>
            <option value="Sud-Ouest">Sud-Ouest</option>
            <option value="Est">Est</option>
            <option value="Ouest">Ouest</option>
          </select>
        </div>
        <div className="form-group">
          <label>Y a-t-il des velux sur votre toiture ?</label>
          <input
            type="number"
            value={formData.veluxCount}
            onChange={(e) => setFormData({...formData, veluxCount: e.target.value})}
            min="0"
            max="10"
            placeholder="Nombre de velux (0 si aucun)"
          />
        </div>
        <div className="form-buttons">
          <button type="button" onClick={onPrevious} className="prev-button">Précédent</button>
          <button type="submit" className="next-button">Suivant</button>
        </div>
      </form>
    </div>
  );
};

// Formulaire étape 3 - Système de chauffage
const HeatingSystemForm = ({ formData, setFormData, onNext, onPrevious }) => {
  const handleSubmit = (e) => {
    e.preventDefault();
    if (formData.heatingSystem && formData.waterHeatingSystem) {
      onNext();
    }
  };

  return (
    <div className="form-container">
      <h2>Système de Chauffage et Eau Chaude</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Système de chauffage actuel *</label>
          <select
            value={formData.heatingSystem}
            onChange={(e) => setFormData({...formData, heatingSystem: e.target.value})}
            required
          >
            <option value="">Sélectionnez votre système</option>
            <option value="Radiateurs électriques">Radiateurs électriques</option>
            <option value="Chauffage électrique avec plancher chauffant">Chauffage électrique avec plancher chauffant</option>
            <option value="Chaudière Gaz">Chaudière Gaz</option>
            <option value="Chaudière Fuel">Chaudière Fuel</option>
            <option value="Pompe à chaleur Air-Air réversible">Pompe à chaleur Air-Air réversible (chauffage et climatisation)</option>
            <option value="Pompe à chaleur Air-Eau">Pompe à chaleur Air-Eau</option>
          </select>
        </div>
        <div className="form-group">
          <label>Système d'eau chaude sanitaire *</label>
          <select
            value={formData.waterHeatingSystem}
            onChange={(e) => setFormData({...formData, waterHeatingSystem: e.target.value})}
            required
          >
            <option value="">Sélectionnez votre système</option>
            <option value="Ballon électrique standard">Ballon électrique standard</option>
            <option value="Ballon thermodynamique">Ballon thermodynamique</option>
          </select>
        </div>
        {formData.waterHeatingSystem && (
          <div className="form-group">
            <label>Capacité du ballon (litres)</label>
            <input
              type="number"
              value={formData.waterHeatingCapacity}
              onChange={(e) => setFormData({...formData, waterHeatingCapacity: e.target.value})}
              placeholder="ex: 200"
              min="50"
              max="500"
            />
          </div>
        )}
        <div className="form-buttons">
          <button type="button" onClick={onPrevious} className="prev-button">Précédent</button>
          <button type="submit" className="next-button">Suivant</button>
        </div>
      </form>
    </div>
  );
};

// Formulaire étape 4 - Consommation
const ConsumptionForm = ({ formData, setFormData, onNext, onPrevious }) => {
  const handleSubmit = (e) => {
    e.preventDefault();
    if (formData.annualConsumption && formData.monthlyEdfPayment) {
      onNext();
    }
  };

  // Calcul automatique du total annuel
  const calculateAnnualTotal = (monthly) => {
    return monthly * 11; // 11 mois comme spécifié
  };

  return (
    <div className="form-container">
      <h2>Consommation Électrique</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Consommation annuelle en kWh *</label>
          <input
            type="number"
            value={formData.annualConsumption}
            onChange={(e) => setFormData({...formData, annualConsumption: e.target.value})}
            placeholder="ex: 4850"
            min="1000"
            max="20000"
            required
          />
        </div>
        <div className="form-group">
          <label>Mensualité prélevée chaque mois par EDF (€) *</label>
          <input
            type="number"
            value={formData.monthlyEdfPayment}
            onChange={(e) => {
              const monthly = e.target.value;
              setFormData({
                ...formData, 
                monthlyEdfPayment: monthly,
                annualEdfPayment: calculateAnnualTotal(monthly)
              });
            }}
            placeholder="ex: 150"
            min="30"
            max="500"
            required
          />
        </div>
        {formData.monthlyEdfPayment && (
          <div className="form-group">
            <label>Total payé à l'année (€)</label>
            <input
              type="number"
              value={formData.annualEdfPayment}
              readOnly
              className="readonly-field"
            />
            <small>Calculé automatiquement : {formData.monthlyEdfPayment} € × 11 mois</small>
          </div>
        )}
        <div className="form-buttons">
          <button type="button" onClick={onPrevious} className="prev-button">Précédent</button>
          <button type="submit" className="next-button">Commencer le Calcul</button>
        </div>
      </form>
    </div>
  );
};

// Composant principal
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
    waterHeatingSystem: '',
    waterHeatingCapacity: '',
    annualConsumption: '',
    monthlyEdfPayment: '',
    annualEdfPayment: ''
  });

  const handleStart = () => {
    console.log('Starting form...');
    setCurrentStep('personal');
  };

  const handleNext = () => {
    const steps = ['personal', 'technical', 'heating', 'consumption', 'calculation'];
    const currentIndex = steps.indexOf(currentStep);
    if (currentIndex < steps.length - 1) {
      setCurrentStep(steps[currentIndex + 1]);
    }
  };

  const handlePrevious = () => {
    const steps = ['personal', 'technical', 'heating', 'consumption'];
    const currentIndex = steps.indexOf(currentStep);
    if (currentIndex > 0) {
      setCurrentStep(steps[currentIndex - 1]);
    }
  };

  const renderStep = () => {
    switch (currentStep) {
      case 'start':
        return <StartScreen onStart={handleStart} />;
      case 'personal':
        return <PersonalInfoForm formData={formData} setFormData={setFormData} onNext={handleNext} />;
      case 'technical':
        return <TechnicalInfoForm formData={formData} setFormData={setFormData} onNext={handleNext} onPrevious={handlePrevious} />;
      case 'heating':
        return <HeatingSystemForm formData={formData} setFormData={setFormData} onNext={handleNext} onPrevious={handlePrevious} />;
      case 'consumption':
        return <ConsumptionForm formData={formData} setFormData={setFormData} onNext={handleNext} onPrevious={handlePrevious} />;
      case 'calculation':
        return <div className="calculation-screen">Calcul en cours...</div>;
      default:
        return <StartScreen onStart={handleStart} />;
    }
  };

  return (
    <div className="App">
      {renderStep()}
    </div>
  );
}

export default App;