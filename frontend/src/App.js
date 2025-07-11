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
const StartScreen = ({ onStart }) => {
  
  const handleClick = () => {
    console.log("Button clicked!");
    onStart();
  };
  
  return (
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
      
      <button className="start-button" onClick={handleClick}>
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
};

// Formulaire étape 1 - Informations personnelles
const PersonalInfoForm = ({ formData, setFormData, onNext, onPrevious }) => {
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
        <div className="form-buttons">
          <button type="button" onClick={onPrevious} className="prev-button">Précédent</button>
          <button type="submit" className="next-button">Suivant</button>
        </div>
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

// Écran de calcul avec countdown 4 minutes
const CalculationScreen = ({ formData, onComplete, onPrevious }) => {
  const [countdown, setCountdown] = useState(240); // 4 minutes = 240 secondes
  const [currentPhase, setCurrentPhase] = useState(0);
  const [calculationResults, setCalculationResults] = useState(null);
  const [isCalculating, setIsCalculating] = useState(true);

  // Phases d'explication pendant les 4 minutes
  const phases = [
    {
      title: "Géolocalisation de votre adresse",
      description: "Nous localisons précisément votre domicile pour obtenir les données d'ensoleillement...",
      duration: 30
    },
    {
      title: "Consultation PVGIS Commission Européenne",
      description: "Récupération des données officielles d'ensoleillement et de production solaire...",
      duration: 60
    },
    {
      title: "Calcul de la production optimale",
      description: "Analyse de votre consommation et optimisation du kit solaire...",
      duration: 60
    },
    {
      title: "Calculs financiers et d'amortissement",
      description: "Calcul des économies, du financement et du retour sur investissement...",
      duration: 90
    }
  ];

  useEffect(() => {
    const timer = setInterval(() => {
      setCountdown(prev => {
        if (prev <= 1) {
          clearInterval(timer);
          setIsCalculating(false);
          performCalculation();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    // Changement de phase selon le temps écoulé
    const elapsed = 240 - countdown;
    let currentPhaseIndex = 0;
    let totalDuration = 0;
    
    for (let i = 0; i < phases.length; i++) {
      totalDuration += phases[i].duration;
      if (elapsed < totalDuration) {
        currentPhaseIndex = i;
        break;
      }
    }
    
    setCurrentPhase(currentPhaseIndex);
  }, [countdown]);

  const performCalculation = async () => {
    try {
      // D'abord créer le client
      const clientResponse = await axios.post(`${API}/clients`, {
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
      });

      const clientId = clientResponse.data.id;

      // Ensuite faire le calcul
      const calculationResponse = await axios.post(`${API}/calculate/${clientId}`);
      
      setCalculationResults(calculationResponse.data);
      onComplete(calculationResponse.data);

    } catch (error) {
      console.error('Erreur lors du calcul:', error);
      alert('Erreur lors du calcul. Veuillez réessayer.');
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const progressPercentage = ((240 - countdown) / 240) * 100;

  if (!isCalculating && calculationResults) {
    return <ResultsScreen results={calculationResults} onPrevious={onPrevious} />;
  }

  return (
    <div className="calculation-screen">
      <h2>Calcul en cours de votre solution solaire</h2>
      
      <div className="countdown-circle">
        <svg width="200" height="200" className="countdown-svg">
          <circle
            cx="100"
            cy="100"
            r="90"
            stroke="#e0e0e0"
            strokeWidth="10"
            fill="none"
          />
          <circle
            cx="100"
            cy="100"
            r="90"
            stroke="#ff6b35"
            strokeWidth="10"
            fill="none"
            strokeDasharray={`${progressPercentage * 5.65} 565`}
            strokeLinecap="round"
            className="progress-circle"
          />
        </svg>
        <div className="countdown-text">
          <div className="countdown-number">{formatTime(countdown)}</div>
          <div className="countdown-label">minutes</div>
        </div>
      </div>

      <div className="calculation-phase">
        <h3>{phases[currentPhase]?.title}</h3>
        <p>{phases[currentPhase]?.description}</p>
      </div>

      <div className="calculation-info">
        <div className="info-item">
          <strong>Client :</strong> {formData.firstName} {formData.lastName}
        </div>
        <div className="info-item">
          <strong>Adresse :</strong> {formData.address}
        </div>
        <div className="info-item">
          <strong>Surface toiture :</strong> {formData.roofSurface} m²
        </div>
        <div className="info-item">
          <strong>Orientation :</strong> {formData.roofOrientation}
        </div>
        <div className="info-item">
          <strong>Consommation :</strong> {formData.annualConsumption} kWh/an
        </div>
      </div>

      <div className="calculation-note">
        <p><strong>Données source PVGIS Commission Européenne</strong></p>
        <p>Ce temps nous permet d'expliquer le fonctionnement de votre future installation</p>
      </div>

      <div className="form-buttons">
        <button type="button" onClick={onPrevious} className="prev-button">Précédent</button>
      </div>
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

  useEffect(() => {
    console.log('App useEffect - Current step:', currentStep);
  }, [currentStep]);

  const handleStart = () => {
    console.log('handleStart called at:', new Date().toISOString());
    setCurrentStep('personal');
    console.log('State should be changed to: personal');
  };

  const handleNext = () => {
    const steps = ['personal', 'technical', 'heating', 'consumption', 'calculation'];
    const currentIndex = steps.indexOf(currentStep);
    if (currentIndex < steps.length - 1) {
      setCurrentStep(steps[currentIndex + 1]);
    }
  };

  const handlePrevious = () => {
    const steps = ['start', 'personal', 'technical', 'heating', 'consumption'];
    const currentIndex = steps.indexOf(currentStep);
    if (currentIndex > 0) {
      setCurrentStep(steps[currentIndex - 1]);
    }
  };

  console.log('Rendering App with currentStep:', currentStep);

  if (currentStep === 'start') {
    return (
      <div className="App">
        <div style={{position: 'fixed', top: '10px', left: '10px', background: 'black', color: 'white', padding: '5px', zIndex: 1000}}>
          Debug: {currentStep}
        </div>
        <StartScreen onStart={handleStart} />
      </div>
    );
  }

  if (currentStep === 'personal') {
    return (
      <div className="App">
        <div style={{position: 'fixed', top: '10px', left: '10px', background: 'black', color: 'white', padding: '5px', zIndex: 1000}}>
          Debug: {currentStep}
        </div>
        <PersonalInfoForm formData={formData} setFormData={setFormData} onNext={handleNext} onPrevious={handlePrevious} />
      </div>
    );
  }

  if (currentStep === 'technical') {
    return (
      <div className="App">
        <div style={{position: 'fixed', top: '10px', left: '10px', background: 'black', color: 'white', padding: '5px', zIndex: 1000}}>
          Debug: {currentStep}
        </div>
        <TechnicalInfoForm formData={formData} setFormData={setFormData} onNext={handleNext} onPrevious={handlePrevious} />
      </div>
    );
  }

  if (currentStep === 'heating') {
    return (
      <div className="App">
        <div style={{position: 'fixed', top: '10px', left: '10px', background: 'black', color: 'white', padding: '5px', zIndex: 1000}}>
          Debug: {currentStep}
        </div>
        <HeatingSystemForm formData={formData} setFormData={setFormData} onNext={handleNext} onPrevious={handlePrevious} />
      </div>
    );
  }

  if (currentStep === 'consumption') {
    return (
      <div className="App">
        <div style={{position: 'fixed', top: '10px', left: '10px', background: 'black', color: 'white', padding: '5px', zIndex: 1000}}>
          Debug: {currentStep}
        </div>
        <ConsumptionForm formData={formData} setFormData={setFormData} onNext={handleNext} onPrevious={handlePrevious} />
      </div>
    );
  }

  if (currentStep === 'calculation') {
    return (
      <div className="App">
        <div style={{position: 'fixed', top: '10px', left: '10px', background: 'black', color: 'white', padding: '5px', zIndex: 1000}}>
          Debug: {currentStep}
        </div>
        <div className="calculation-screen">
          <h2>Calcul en cours...</h2>
          <p>Veuillez patienter pendant que nous analysons vos données</p>
          <div className="form-buttons">
            <button type="button" onClick={handlePrevious} className="prev-button">Précédent</button>
          </div>
        </div>
      </div>
    );
  }

  // Fallback
  return (
    <div className="App">
      <div style={{position: 'fixed', top: '10px', left: '10px', background: 'black', color: 'white', padding: '5px', zIndex: 1000}}>
        Debug: {currentStep} (fallback)
      </div>
      <StartScreen onStart={handleStart} />
    </div>
  );
}

export default App;