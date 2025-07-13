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

// Écran de démarrage amélioré avec vrais logos
const StartScreen = ({ onStart }) => {
  
  const handleClick = () => {
    console.log("Button clicked!");
    onStart();
  };
  
  return (
    <div className="start-screen">
      {/* Image FRH Environnement réelle */}
      <div className="company-header">
        <div className="company-image">
          <img 
            src="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAArAFoDASIAAhEBAxEB/8QAGwABAAIDAQEAAAAAAAAAAAAAAAQFAwMGBwH/xAA2EAABAwMCAwYDBwQDAAAAAAAAAQIDBAURBhIhMQdTQVFhcSKBkRQyocHR4fAjQrHxFRYz/8QAGQEBAAMBAQAAAAAAAAAAAAAAAAECAwQF/8QAIBEBAAICAgEFAAAAAAAAAAAAAAECAxESMQQhQVGBsf/aAAwDAQACEQMRAD8A9xAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAPz/qS+V+rNRV9/rWxU9HNMrooYWvR0bWfdReLqd7HJhrWOobYrxWZbwAAOVurytGmoqKqlZd7lhqhKitjZAz4m/eRy5xgkREzLN1jdqvJv8P0Xf8AXFzpCLdNHBQwRuSNrWIuRMKnL9zrSr+xfSSy26a6VbOUzURifcXnnz7V/Jfe83I6OO9fmKsz96SAAPUe8AAAAAAAAAAfD/xLWmlJ6YrZbfqK1VNPUtajpKOqZhZGZwrsZwvI6Cj7X9BzNzPU1dA7+yWF3/l0cfR8WwcVMU1q2iJ8r6AAAAHGab7PbRpmpkqra6oulXKmH1dy9nO9GorW+aaJOxLZLktv5k1jJPJlb7l2cAOO9K3vbt6j4+fUJPt6xMR8L6s6AAAHqPegAAAABkEzMFczC8T6+J+5ycF4H6NG8a/qUOmu12fhWBz3u5xNd/E4t1H2T6ksrXOdSQXKNvc3A9qr8uB+l/3VJtl3+zkdPjzSO5eGNv6OZfK3Hpu1y2SzVFXUqxU7xOCd5wXj3eY2YcN7vMT7WrSbTtj2jVei9MYWv1QrpWwTK1a+kfudjmu7Hj69Oqr2l6EWBN2tL65Ut3Z+z3Vzy7Pwu6VUfHOhqCCppNKsllZtq7Rci1Ntp5N5XZyrkROv7GPFa/LvxN/8AFj7Y6m4z6v7KN1YjpJq3T1xV08TW+7vqcPnT4fhc7LcbRxYHDGy+i38Ml9GUTt3D4jJit38Ml9GUTt3D4jJit38JJABo2AAHqHfgAAAAAJlLp7UtbQxVVLY7hNDIm5j47fKqKn1GVKTadQrNoncqybTtyZC6V9JNHHI3u3vfCrWuTwVXYRbz+oT5U67r1P15OxeFqhVzDOhOOi73VNhL86/xZBvtMaUPSFt3Ry7dv2YlOKIYJKOGnpW1MzGw0zX/ANWjS5URf/5EXI4aTGllpppKcZStQnv8XuTN5OiE77y3nJcJdOao9w2p19aWdOK7FXz8F9vvKwAlqxfG9y/+TnLZlm/OqODzjfZnfmj47W+UgADp3OONx+AAAAAP/9k=" 
            alt="FRH Environnement - Installateur Photovoltaïque"
            className="company-logo-image"
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
      
      <AutonomyLogo />
      
      {/* Logos officiels avec MMA Décennale */}
      <div className="certifications">
        <div className="cert-row">
          <div className="cert-badge official rge-qualipv">
            <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGQAAAAyCAYAAACqNX6+AAAACXBIWXMAAAsTAAALEwEAmpwYAAAF8klEQVR4nO2ae0yTVxjGH5D..." alt="RGE QualiPV 2025" />
            <span>RGE QualiPV 2025</span>
          </div>
          <div className="cert-badge official rge-qualipac">
            <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGQAAAAyCAYAAACqNX6+AAAACXBIWXMAAAsTAAALEwEAmpwYAAAG..." alt="RGE QualiPac 2025" />
            <span>RGE QualiPac 2025</span>
          </div>
        </div>
        
        <div className="cert-row">
          <div className="cert-badge official ffb">
            <span>🏢 FFB Adhérent</span>
          </div>
          <div className="cert-badge official edf">
            <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGQAAAAyCAYAAACqNX6+AAAACXBIWXMAAAsTAAALEwEAmpwYAAAH..." alt="Partenaire AGIR PLUS EDF" />
            <span>⚡ Partenaire AGIR PLUS EDF</span>
          </div>
        </div>
        
        <div className="cert-row">
          <div className="cert-badge official mma-decennale">
            <div className="mma-logos">
              <span className="mma-logo blue">M</span>
              <span className="mma-logo green">M</span>
              <span className="mma-logo orange">A</span>
            </div>
            <div className="decennale-text">
              <h4>Décennale</h4>
              <p>Toutes nos installations bénéficient d'une garantie de 10 ans.</p>
            </div>
          </div>
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

      <div className="contact-info">
        <p><strong>🏢 FRH Environnement</strong> - 196 Avenue Jean Lolive 93500 Pantin</p>
        <p><strong>📞</strong> 09 85 60 50 51 | <strong>✉️</strong> contact@francerenovhabitat.com</p>
      </div>
    </div>
  );
};

// Formulaire étape 1 - Informations personnelles amélioré
const PersonalInfoForm = ({ formData, setFormData, onNext, onPrevious }) => {
  const [errors, setErrors] = useState({});

  const validateForm = () => {
    const newErrors = {};
    if (!formData.firstName.trim()) newErrors.firstName = "Le prénom est obligatoire";
    if (!formData.lastName.trim()) newErrors.lastName = "Le nom est obligatoire";
    if (!formData.address.trim()) newErrors.address = "L'adresse est obligatoire";
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validateForm()) {
      onNext();
    }
  };

  return (
    <div className="form-container">
      <div className="form-header">
        <h2>📋 Étape 1/4 - Informations Personnelles</h2>
        <div className="progress-bar">
          <div className="progress-fill" style={{width: '25%'}}></div>
        </div>
      </div>
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>👤 Prénom *</label>
          <input
            type="text"
            value={formData.firstName}
            onChange={(e) => setFormData({...formData, firstName: e.target.value})}
            placeholder="Votre prénom"
            className={errors.firstName ? 'error' : ''}
            required
          />
          {errors.firstName && <span className="error-message">{errors.firstName}</span>}
        </div>
        
        <div className="form-group">
          <label>👤 Nom *</label>
          <input
            type="text"
            value={formData.lastName}
            onChange={(e) => setFormData({...formData, lastName: e.target.value})}
            placeholder="Votre nom de famille"
            className={errors.lastName ? 'error' : ''}
            required
          />
          {errors.lastName && <span className="error-message">{errors.lastName}</span>}
        </div>
        
        <div className="form-group">
          <label>🏠 Adresse exacte de votre domicile *</label>
          <input
            type="text"
            value={formData.address}
            onChange={(e) => setFormData({...formData, address: e.target.value})}
            placeholder="10 Avenue des Champs-Élysées, 75008 Paris"
            className={errors.address ? 'error' : ''}
            required
          />
          {errors.address && <span className="error-message">{errors.address}</span>}
          <small>💡 Cette adresse sera utilisée pour calculer précisément votre potentiel solaire</small>
        </div>
        
        <div className="form-buttons">
          <button type="button" onClick={onPrevious} className="prev-button">⬅️ Précédent</button>
          <button type="submit" className="next-button">Suivant ➡️</button>
        </div>
      </form>
    </div>
  );
};

// Formulaire étape 2 - Informations techniques amélioré
const TechnicalInfoForm = ({ formData, setFormData, onNext, onPrevious }) => {
  const [errors, setErrors] = useState({});

  const validateForm = () => {
    const newErrors = {};
    if (!formData.roofSurface || formData.roofSurface < 10) newErrors.roofSurface = "Surface minimum : 10 m²";
    if (!formData.roofOrientation) newErrors.roofOrientation = "Orientation obligatoire";
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validateForm()) {
      onNext();
    }
  };

  const getOrientationAdvice = (orientation) => {
    const advice = {
      "Sud": "🌟 Excellente orientation ! Production optimale",
      "Sud-Est": "👍 Très bonne orientation, production matinale",
      "Sud-Ouest": "👍 Très bonne orientation, production tardive", 
      "Est": "⚠️ Orientation correcte, production matinale",
      "Ouest": "⚠️ Orientation correcte, production tardive"
    };
    return advice[orientation] || "";
  };

  return (
    <div className="form-container">
      <div className="form-header">
        <h2>🏠 Étape 2/4 - Informations Techniques</h2>
        <div className="progress-bar">
          <div className="progress-fill" style={{width: '50%'}}></div>
        </div>
      </div>
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>📐 Surface de votre toiture la mieux orientée (m²) *</label>
          <input
            type="number"
            value={formData.roofSurface}
            onChange={(e) => setFormData({...formData, roofSurface: e.target.value})}
            placeholder="ex: 50"
            min="10"
            max="200"
            className={errors.roofSurface ? 'error' : ''}
            required
          />
          {errors.roofSurface && <span className="error-message">{errors.roofSurface}</span>}
          <small>💡 Chaque panneau fait 2,1 m² - Surface minimum 10 m² (≈ 5 panneaux)</small>
        </div>
        
        <div className="form-group">
          <label>🧭 Orientation de votre toiture *</label>
          <select
            value={formData.roofOrientation}
            onChange={(e) => setFormData({...formData, roofOrientation: e.target.value})}
            className={errors.roofOrientation ? 'error' : ''}
            required
          >
            <option value="">Sélectionnez une orientation</option>
            <option value="Sud">🌞 Sud (Optimal)</option>
            <option value="Sud-Est">🌅 Sud-Est (Très bon)</option>
            <option value="Sud-Ouest">🌇 Sud-Ouest (Très bon)</option>
            <option value="Est">⬅️ Est (Correct)</option>
            <option value="Ouest">➡️ Ouest (Correct)</option>
          </select>
          {errors.roofOrientation && <span className="error-message">{errors.roofOrientation}</span>}
          {formData.roofOrientation && (
            <div className="orientation-advice">{getOrientationAdvice(formData.roofOrientation)}</div>
          )}
        </div>
        
        <div className="form-group">
          <label>🪟 Nombre de velux sur votre toiture</label>
          <input
            type="number"
            value={formData.veluxCount}
            onChange={(e) => setFormData({...formData, veluxCount: e.target.value})}
            min="0"
            max="10"
            placeholder="0 si aucun"
          />
          <small>💡 Les velux peuvent limiter l'espace disponible pour les panneaux</small>
        </div>
        
        <div className="form-buttons">
          <button type="button" onClick={onPrevious} className="prev-button">⬅️ Précédent</button>
          <button type="submit" className="next-button">Suivant ➡️</button>
        </div>
      </form>
    </div>
  );
};

// Formulaire étape 3 - Système de chauffage amélioré
const HeatingSystemForm = ({ formData, setFormData, onNext, onPrevious }) => {
  const [errors, setErrors] = useState({});

  const validateForm = () => {
    const newErrors = {};
    if (!formData.heatingSystem) newErrors.heatingSystem = "Système de chauffage obligatoire";
    if (!formData.waterHeatingSystem) newErrors.waterHeatingSystem = "Système d'eau chaude obligatoire";
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validateForm()) {
      onNext();
    }
  };

  const getHeatingAdvice = (heating) => {
    if (heating.includes("électrique")) {
      return "⚡ Parfait pour le solaire ! Vous consommez beaucoup d'électricité";
    }
    if (heating.includes("Pompe à chaleur")) {
      return "🔥 Excellente synergie avec le solaire !";
    }
    return "🏠 Installation solaire rentable malgré le chauffage non-électrique";
  };

  return (
    <div className="form-container">
      <div className="form-header">
        <h2>🏠 Étape 3/4 - Chauffage et Eau Chaude</h2>
        <div className="progress-bar">
          <div className="progress-fill" style={{width: '75%'}}></div>
        </div>
      </div>
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>🔥 Système de chauffage actuel *</label>
          <select
            value={formData.heatingSystem}
            onChange={(e) => setFormData({...formData, heatingSystem: e.target.value})}
            className={errors.heatingSystem ? 'error' : ''}
            required
          >
            <option value="">Sélectionnez votre système</option>
            <option value="Radiateurs électriques">⚡ Radiateurs électriques</option>
            <option value="Chauffage électrique avec plancher chauffant">⚡ Plancher chauffant électrique</option>
            <option value="Chaudière Gaz">🔥 Chaudière Gaz</option>
            <option value="Chaudière Fuel">🛢️ Chaudière Fuel</option>
            <option value="Pompe à chaleur Air-Air réversible">❄️🔥 Pompe à chaleur Air-Air (réversible)</option>
            <option value="Pompe à chaleur Air-Eau">💧🔥 Pompe à chaleur Air-Eau</option>
          </select>
          {errors.heatingSystem && <span className="error-message">{errors.heatingSystem}</span>}
          {formData.heatingSystem && (
            <div className="heating-advice">{getHeatingAdvice(formData.heatingSystem)}</div>
          )}
        </div>
        
        <div className="form-group">
          <label>💧 Système d'eau chaude sanitaire *</label>
          <select
            value={formData.waterHeatingSystem}
            onChange={(e) => setFormData({...formData, waterHeatingSystem: e.target.value})}
            className={errors.waterHeatingSystem ? 'error' : ''}
            required
          >
            <option value="">Sélectionnez votre système</option>
            <option value="Ballon électrique standard">⚡ Ballon électrique standard</option>
            <option value="Ballon thermodynamique">🔄 Ballon thermodynamique</option>
          </select>
          {errors.waterHeatingSystem && <span className="error-message">{errors.waterHeatingSystem}</span>}
        </div>
        
        {formData.waterHeatingSystem && (
          <div className="form-group">
            <label>📏 Capacité du ballon (litres)</label>
            <input
              type="number"
              value={formData.waterHeatingCapacity}
              onChange={(e) => setFormData({...formData, waterHeatingCapacity: e.target.value})}
              placeholder="ex: 200"
              min="50"
              max="500"
            />
            <small>💡 Information optionnelle - Capacité standard : 150-300L</small>
          </div>
        )}
        
        <div className="form-buttons">
          <button type="button" onClick={onPrevious} className="prev-button">⬅️ Précédent</button>
          <button type="submit" className="next-button">Suivant ➡️</button>
        </div>
      </form>
    </div>
  );
};

// Composant principal - Version Premium
function App() {
  const [currentStep, setCurrentStep] = useState('start');
  const [calculationResults, setCalculationResults] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
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
      setIsLoading(true);
      setTimeout(() => {
        setCurrentStep(steps[currentIndex + 1]);
        setIsLoading(false);
      }, 300);
    }
  };

  const handlePrevious = () => {
    const steps = ['start', 'personal', 'technical', 'heating', 'consumption', 'calculation'];
    const currentIndex = steps.indexOf(currentStep);
    if (currentIndex > 0) {
      setIsLoading(true);
      setTimeout(() => {
        setCurrentStep(steps[currentIndex - 1]);
        setIsLoading(false);
      }, 300);
    }
  };

  const handleCalculationComplete = (results) => {
    setCalculationResults(results);
    setTimeout(() => {
      setCurrentStep('results');
    }, 1000);
  };

  const handleNewCalculation = () => {
    setCurrentStep('start');
    setCalculationResults(null);
    setFormData({
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
  };

  console.log('Rendering App with currentStep:', currentStep);

  // Loading screen
  if (isLoading) {
    return (
      <div className="App">
        <div className="loading-screen">
          <div className="loading-spinner"></div>
          <p>Chargement...</p>
        </div>
      </div>
    );
  }

  if (currentStep === 'start') {
    return (
      <div className="App">
        <StartScreen onStart={handleStart} />
      </div>
    );
  }

  if (currentStep === 'personal') {
    return (
      <div className="App">
        <PersonalInfoForm 
          formData={formData} 
          setFormData={setFormData} 
          onNext={handleNext} 
          onPrevious={handlePrevious} 
        />
      </div>
    );
  }

  // Pour l'instant, les autres composants ne sont pas encore créés
  // Nous les ajouterons dans les prochaines étapes
  return (
    <div className="App">
      <div className="error-screen">
        <h2>⚠️ Composant en cours de développement</h2>
        <p>Étape actuelle : {currentStep}</p>
        <button onClick={handleNewCalculation} className="error-button">
          🏠 Retour à l'accueil
        </button>
      </div>
    </div>
  );
}

export default App;