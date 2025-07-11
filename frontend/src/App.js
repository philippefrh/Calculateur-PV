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
            src="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAArAFoDASIAAhEBAxEB/8QAGwABAAIDAQEAAAAAAAAAAAAAAAQFAgMGBwH/xAA2EAABAwMCAwYDBwQDAAAAAAAAAQIDBAURBhIhMQcTQVFhcSKBkRQyocHR4fAjQrHxFRYz/8QAGQEBAAMBAQAAAAAAAAAAAAAAAAECAwQF/8QAIBEBAAICAgEFAAAAAAAAAAAAAAECAxESMQQhQVGBsf/aAAwDAQACEQMRAD8A9xAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAPz/qS+V+rNRV1/rWxU9HNMrooYWvR0bWfdReLqd7HJhrWOobYrxWZbwAAOVurytGmoqKqlZd7lhqhKitjZAz4m/eRy5xgkREzLN1jdqvJv8P0Xf8AXFzpCLdNHBQwRuSNrWIuRMKnL9zrSr+xfSSy26a6VbOUzURifcXnnz7V/Jfe83I6OO9fmKsz96SAAPUe8AAAAAAAAAAfD/xLWmlJ6YrZbfqK1VNPUtajpKOqZhZGZwrsZwvI6Cj7X9BzNzPU1dA7+yWF3/l0cfR8WwcVMU1q2iJ8r6AAAAHGab7PbRpmpkqra6oulXKmH1dy9nO9GorW+aaJOxLZLktv5k1jJPJlb7l2cAOO9K3vbt6j4+fUJPt6xMR8L6s6AAAHqPegAAAABkEzMFczC8T6+J+5ycF4H6NG8a/qUOmu12fhWBz3u5xNd/E4t1H2T6ksrXOdSQXKNvc3A9qr8uB+l/3VJtl3+zkdPjzSO5eGNv6OZfK3Hpu1y2SzVFXUqxU7xOCd5wXj3eY2YcN7vMT7WrSbTtj2jVei9MYWv1QrpWwTK1a+kfudjmu7Hj69Oqr2l6EWBN2tL65Ut3Z+z3Vzy7Pwu6VUfHOhqCCppNKsllZtq7Rci1Ntp5N5XZyrkROv7GPFa/LvxN/8AFj7Y6m4z6v7KN1YjpJq3T1xV08TW+7vqcPnT4fhc7LcbRxYHDGy+i38Ml9GUTt3D4jJit38JJABo2AAHqHfgAAAAAJlLp7UtbQxVVLY7hNDIm5j47fKqKn1GVKTadQrNoncqybTtyZC6V9JNHHI3u3vfCrWuTwVXYRbz+oT5U67r1P15OxeFqhVzDOhOOi73VNhL86/xZBvtMaUPSFt3Ry7dv2YlOKIYJKOGnpW1MzGw0zX/ANWjS5URf/5EXI4aTGllpppKcZStQnv8XuTN5OiE77y3nJcJdOao9w2p19aWdOK7FXz8F9vvKwAlqxfG9y/+TnLZlm/OqODzjfZnfmj47W+UgADp3OONx+AAAAAP/9k=" 
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

// Formulaire étape 4 - Consommation amélioré
const ConsumptionForm = ({ formData, setFormData, onNext, onPrevious }) => {
  const [errors, setErrors] = useState({});

  const validateForm = () => {
    const newErrors = {};
    if (!formData.annualConsumption || formData.annualConsumption < 1000) {
      newErrors.annualConsumption = "Consommation minimum : 1000 kWh/an";
    }
    if (!formData.monthlyEdfPayment || formData.monthlyEdfPayment < 30) {
      newErrors.monthlyEdfPayment = "Montant minimum : 30 €/mois";
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validateForm()) {
      onNext();
    }
  };

  // Calcul automatique du total annuel
  const calculateAnnualTotal = (monthly) => {
    return monthly * 11; // 11 mois comme spécifié
  };

  const getConsumptionAdvice = (consumption) => {
    if (consumption < 3000) return "🟢 Consommation faible - Kit 3-4 kW recommandé";
    if (consumption < 6000) return "🟡 Consommation moyenne - Kit 5-6 kW recommandé";
    if (consumption < 9000) return "🟠 Consommation élevée - Kit 7-8 kW recommandé";
    return "🔴 Consommation très élevée - Kit 9 kW+ recommandé";
  };

  return (
    <div className="form-container">
      <div className="form-header">
        <h2>⚡ Étape 4/4 - Consommation Électrique</h2>
        <div className="progress-bar">
          <div className="progress-fill" style={{width: '100%'}}></div>
        </div>
      </div>
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>📊 Consommation annuelle en kWh *</label>
          <input
            type="number"
            value={formData.annualConsumption}
            onChange={(e) => setFormData({...formData, annualConsumption: e.target.value})}
            placeholder="ex: 6500"
            min="1000"
            max="20000"
            className={errors.annualConsumption ? 'error' : ''}
            required
          />
          {errors.annualConsumption && <span className="error-message">{errors.annualConsumption}</span>}
          {formData.annualConsumption && (
            <div className="consumption-advice">{getConsumptionAdvice(formData.annualConsumption)}</div>
          )}
          <small>💡 Trouvez cette info sur votre facture EDF ou votre espace client</small>
        </div>
        
        <div className="form-group">
          <label>💳 Mensualité prélevée par EDF (€) *</label>
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
            placeholder="ex: 180"
            min="30"
            max="500"
            className={errors.monthlyEdfPayment ? 'error' : ''}
            required
          />
          {errors.monthlyEdfPayment && <span className="error-message">{errors.monthlyEdfPayment}</span>}
          <small>💡 Montant prélevé chaque mois sur votre compte</small>
        </div>
        
        {formData.monthlyEdfPayment && (
          <div className="form-group">
            <label>💰 Total payé à l'année (€)</label>
            <input
              type="number"
              value={formData.annualEdfPayment}
              readOnly
              className="readonly-field"
            />
            <small>Calculé automatiquement : {formData.monthlyEdfPayment} € × 11 mois = {formData.annualEdfPayment} €/an</small>
          </div>
        )}
        
        <div className="consumption-summary">
          <h4>📋 Résumé de votre profil :</h4>
          <p><strong>🏠</strong> {formData.firstName} {formData.lastName}</p>
          <p><strong>📍</strong> {formData.address}</p>
          <p><strong>📐</strong> {formData.roofSurface} m² - {formData.roofOrientation}</p>
          <p><strong>⚡</strong> {formData.annualConsumption} kWh/an</p>
        </div>
        
        <div className="form-buttons">
          <button type="button" onClick={onPrevious} className="prev-button">⬅️ Précédent</button>
          <button type="submit" className="next-button">🚀 Commencer le Calcul PVGIS</button>
        </div>
      </form>
    </div>
  );
};

// Écran de résultats - Version Premium avec génération PDF
const ResultsScreen = ({ results, onPrevious }) => {
  const [activeTab, setActiveTab] = useState('overview');
  const [showFinancing, setShowFinancing] = useState(false);
  const [isGeneratingPDF, setIsGeneratingPDF] = useState(false);

  const generatePDF = async () => {
    try {
      setIsGeneratingPDF(true);
      
      // Afficher un message de génération
      const notification = document.createElement('div');
      notification.className = 'pdf-notification';
      notification.innerHTML = '📄 Génération du rapport PDF en cours...';
      document.body.appendChild(notification);
      
      // Appel à l'API pour générer le PDF
      const response = await fetch(`${API}/generate-pdf/${results.client_id}`, {
        method: 'GET',
        headers: {
          'Accept': 'application/pdf',
        },
      });
      
      if (response.ok) {
        // Créer un blob et télécharger le fichier
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        
        // Nom du fichier avec date
        const today = new Date().toISOString().split('T')[0].replace(/-/g, '');
        link.download = `etude_solaire_FRH_${today}.pdf`;
        
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
        
        // Message de succès
        notification.innerHTML = '✅ Rapport PDF téléchargé avec succès !';
        notification.style.backgroundColor = '#4caf50';
        
        setTimeout(() => {
          document.body.removeChild(notification);
        }, 3000);
      } else {
        throw new Error('Erreur lors de la génération du PDF');
      }
    } catch (error) {
      console.error('Erreur PDF:', error);
      alert(`❌ Erreur lors de la génération du PDF: ${error.message}\n\nVeuillez réessayer ou contacter le support.`);
    } finally {
      setIsGeneratingPDF(false);
    }
  };

  const getAutonomyColor = (percentage) => {
    if (percentage >= 80) return '#4caf50';
    if (percentage >= 60) return '#ff9800';
    return '#f44336';
  };

  const getOptimalFinancing = () => {
    if (!results.financing_options) return null;
    return results.financing_options.find(option => 
      option.difference_vs_savings >= -20 && option.difference_vs_savings <= 20
    ) || results.financing_options[results.financing_options.length - 1];
  };

  const optimalFinancing = getOptimalFinancing();

  const sendToExpert = () => {
    const subject = encodeURIComponent(`Demande de rendez-vous - Étude solaire ${results.kit_power}kW`);
    const body = encodeURIComponent(`Bonjour,

Suite à mon étude solaire personnalisée, je souhaiterais prendre rendez-vous pour finaliser mon projet d'installation.

Résumé de mon étude :
- Kit recommandé : ${results.kit_power}kW (${results.panel_count} panneaux)
- Production estimée : ${Math.round(results.estimated_production)} kWh/an
- Autonomie : ${Math.round(results.autonomy_percentage)}%
- Économies : ${Math.round(results.estimated_savings)} €/an
- Investissement : ${results.kit_price?.toLocaleString()} € TTC

Je suis disponible pour un rendez-vous dans les prochains jours.

Cordialement`);
    
    window.open(`mailto:contact@francerenovhabitat.com?subject=${subject}&body=${body}`);
  };

  return (
    <div className="results-screen">
      <div className="results-header">
        <h2>🎉 Votre Solution Solaire Personnalisée</h2>
        <p>Étude réalisée avec les données officielles PVGIS Commission Européenne</p>
        
        <div className="success-badges">
          <div className="badge-item">
            <span className="badge-icon">🏆</span>
            <span>RGE QualiPV</span>
          </div>
          <div className="badge-item">
            <span className="badge-icon">🛡️</span>
            <span>Garantie 10 ans</span>
          </div>
          <div className="badge-item">
            <span className="badge-icon">⚡</span>
            <span>PVGIS Officiel</span>
          </div>
        </div>
        
        <div className="results-tabs">
          <button 
            className={`tab-button ${activeTab === 'overview' ? 'active' : ''}`}
            onClick={() => setActiveTab('overview')}
          >
            📊 Vue d'ensemble
          </button>
          <button 
            className={`tab-button ${activeTab === 'technical' ? 'active' : ''}`}
            onClick={() => setActiveTab('technical')}
          >
            🔧 Détails techniques
          </button>
          <button 
            className={`tab-button ${activeTab === 'financial' ? 'active' : ''}`}
            onClick={() => setActiveTab('financial')}
          >
            💰 Analyse financière
          </button>
        </div>
      </div>
      
      {activeTab === 'overview' && (
        <div className="tab-content">
          <div className="results-grid">
            <div className="result-card primary">
              <div className="card-icon">⚡</div>
              <h3>Kit Solaire Optimal</h3>
              <div className="big-number">{results.kit_power} kW</div>
              <p>{results.panel_count} panneaux de 500W</p>
              <p className="price">{results.kit_price?.toLocaleString()} € TTC</p>
              <div className="card-footer">
                <small>Surface nécessaire: {results.panel_count * 2.1} m²</small>
              </div>
            </div>

            <div className="result-card success">
              <div className="card-icon">🔋</div>
              <h3>Autonomie Énergétique</h3>
              <div className="big-number" style={{color: 'white'}}>
                {Math.round(results.autonomy_percentage)}%
              </div>
              <p>Autoconsommation optimisée</p>
              <div className="autonomy-bar">
                <div 
                  className="autonomy-fill" 
                  style={{
                    width: `${results.autonomy_percentage}%`,
                    backgroundColor: getAutonomyColor(results.autonomy_percentage)
                  }}
                ></div>
              </div>
            </div>

            <div className="result-card production">
              <div className="card-icon">☀️</div>
              <h3>Production Annuelle</h3>
              <div className="big-number">{Math.round(results.estimated_production)} kWh</div>
              <p>Données PVGIS officielles</p>
              <p>Orientation: {results.orientation}</p>
              <div className="card-footer">
                <small>Soit {Math.round(results.estimated_production/365)} kWh/jour</small>
              </div>
            </div>

            <div className="result-card savings">
              <div className="card-icon">💰</div>
              <h3>Économies Garanties</h3>
              <div className="big-number">{Math.round(results.estimated_savings)} €</div>
              <p>Soit {Math.round(results.monthly_savings)} €/mois</p>
              <div className="savings-breakdown">
                <small>Autoconsommation: {Math.round(results.autoconsumption_kwh)} kWh</small>
                <small>Surplus vendu: {Math.round(results.surplus_kwh)} kWh</small>
              </div>
            </div>
          </div>

          <div className="impact-section">
            <h3>🌱 Impact Environnemental</h3>
            <div className="impact-grid">
              <div className="impact-card">
                <h4>🌳 CO₂ évité</h4>
                <p className="impact-value">{Math.round(results.estimated_production * 0.0571)} kg/an</p>
                <small>Équivalent à {Math.round(results.estimated_production * 0.0571 / 25)} arbres plantés</small>
              </div>
              <div className="impact-card">
                <h4>🏠 Plus-value immobilière</h4>
                <p className="impact-value">Classe A/B</p>
                <small>Augmentation significative de la valeur du bien</small>
              </div>
              <div className="impact-card">
                <h4>⚡ Indépendance</h4>
                <p className="impact-value">{Math.round(results.autonomy_percentage)}% autonome</p>
                <small>Protection contre la hausse des tarifs</small>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'technical' && (
        <div className="tab-content">
          <div className="technical-details">
            <div className="tech-section">
              <h3>🔧 Spécifications techniques</h3>
              <div className="tech-grid">
                <div className="tech-item">
                  <strong>Panneaux:</strong> {results.panel_count} × 500W monocristallin
                </div>
                <div className="tech-item">
                  <strong>Onduleur:</strong> Hoymiles haute performance (99,8%)
                </div>
                <div className="tech-item">
                  <strong>Garanties:</strong> 25 ans production + 10 ans décennale
                </div>
                <div className="tech-item">
                  <strong>Système:</strong> Anti-surtension intégré + arrêt rapide
                </div>
                <div className="tech-item">
                  <strong>Suivi:</strong> Application mobile temps réel
                </div>
                <div className="tech-item">
                  <strong>Installation:</strong> En surimposition toiture
                </div>
              </div>
            </div>

            <div className="monthly-production">
              <h3>📊 Production mensuelle détaillée</h3>
              <div className="monthly-chart">
                {results.pvgis_monthly_data?.map((month) => (
                  <div key={month.month} className="month-bar">
                    <div 
                      className="bar" 
                      style={{height: `${(month.E_m / Math.max(...results.pvgis_monthly_data.map(m => m.E_m))) * 100}%`}}
                    ></div>
                    <span className="month-label">{['J','F','M','A','M','J','J','A','S','O','N','D'][month.month-1]}</span>
                    <span className="month-value">{Math.round(month.E_m)} kWh</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="coordinates-info">
              <h3>🌍 Données géographiques</h3>
              <p><strong>Coordonnées:</strong> {results.coordinates?.lat.toFixed(4)}°N, {results.coordinates?.lon.toFixed(4)}°E</p>
              <p><strong>Source:</strong> {results.pvgis_source}</p>
              <p><strong>Irradiation globale:</strong> ~{Math.round(results.estimated_production / results.kit_power)} kWh/kWc/an</p>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'financial' && (
        <div className="tab-content">
          <div className="financing-section">
            <h3>💰 Analyse financière complète</h3>
            
            <div className="financial-summary">
              <div className="financial-item">
                <span className="financial-label">💳 Investissement:</span>
                <span className="financial-value">{results.kit_price?.toLocaleString()} € TTC</span>
              </div>
              <div className="financial-item">
                <span className="financial-label">🎁 Aides totales:</span>
                <span className="financial-value success">-{Math.round(results.total_aids)} €</span>
              </div>
              <div className="financial-item">
                <span className="financial-label">💸 Reste à financer:</span>
                <span className="financial-value">{(results.kit_price - results.total_aids).toLocaleString()} €</span>
              </div>
              <div className="financial-item">
                <span className="financial-label">⏱️ Retour sur investissement:</span>
                <span className="financial-value">{Math.round((results.kit_price - results.total_aids) / results.estimated_savings)} ans</span>
              </div>
            </div>

            <div className="aids-breakdown">
              <h4>🎁 Détail des aides disponibles</h4>
              <div className="aid-item">
                <span>Prime autoconsommation EDF (versée à M+6):</span>
                <span className="aid-amount">{results.autoconsumption_aid} €</span>
              </div>
              {results.tva_refund > 0 && (
                <div className="aid-item">
                  <span>TVA remboursée 20% (versée à M+12):</span>
                  <span className="aid-amount">{Math.round(results.tva_refund)} €</span>
                </div>
              )}
              <div className="aid-item total-aid">
                <span><strong>Total des aides récupérables:</strong></span>
                <span className="aid-amount"><strong>{Math.round(results.total_aids)} €</strong></span>
              </div>
            </div>

            {optimalFinancing && (
              <div className="optimal-financing">
                <h4>🏦 Financement optimal recommandé</h4>
                <div className="financing-card highlighted">
                  <div className="financing-header">
                    <h5>⭐ Financement sur {optimalFinancing.duration_years} ans</h5>
                    <span className="recommended-badge">Recommandé</span>
                  </div>
                  <div className="financing-details">
                    <div className="financing-row">
                      <span>Mensualité crédit:</span>
                      <span className="amount">{Math.round(optimalFinancing.monthly_payment)} €/mois</span>
                    </div>
                    <div className="financing-row">
                      <span>Économie EDF:</span>
                      <span className="amount success">{Math.round(results.monthly_savings)} €/mois</span>
                    </div>
                    <div className="financing-row">
                      <span>Reste à charge:</span>
                      <span className={`amount ${optimalFinancing.difference_vs_savings < 0 ? 'success' : 'warning'}`}>
                        {optimalFinancing.difference_vs_savings > 0 ? '+' : ''}{Math.round(optimalFinancing.difference_vs_savings)} €/mois
                      </span>
                    </div>
                  </div>
                  <div className="financing-benefits">
                    <p>✅ 6 premiers mois GRATUITS (0€ pendant l'installation)</p>
                    <p>✅ Remboursement anticipé possible sans pénalités</p>
                    <p>✅ Taux fixe 4,96% TAEG sur toute la durée</p>
                    <p>✅ Possibilité de déduire les aides du capital</p>
                  </div>
                </div>
              </div>
            )}

            <button 
              className="show-all-financing-btn"
              onClick={() => setShowFinancing(!showFinancing)}
            >
              {showFinancing ? '📊 Masquer' : '📊 Voir toutes les options'} de financement
            </button>

            {showFinancing && (
              <div className="all-financing-options">
                <h4>📊 Toutes les options de financement disponibles</h4>
                <div className="financing-table">
                  <div className="table-header">
                    <span>Durée</span>
                    <span>Mensualité</span>
                    <span>Coût total</span>
                    <span>Différence vs économies</span>
                  </div>
                  {results.financing_options?.map((option, index) => (
                    <div key={index} className="table-row">
                      <span>{option.duration_years} ans</span>
                      <span>{Math.round(option.monthly_payment)} €</span>
                      <span>{Math.round(option.total_cost).toLocaleString()} €</span>
                      <span className={Math.abs(option.difference_vs_savings) < 20 ? 'success' : 'warning'}>
                        {option.difference_vs_savings > 0 ? '+' : ''}{Math.round(option.difference_vs_savings)} €/mois
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      <div className="results-footer">
        <div className="action-buttons">
          <button type="button" onClick={onPrevious} className="prev-button">⬅️ Modifier les données</button>
          <button 
            type="button" 
            onClick={generatePDF} 
            className={`pdf-button ${isGeneratingPDF ? 'generating' : ''}`}
            disabled={isGeneratingPDF}
          >
            {isGeneratingPDF ? '⏳ Génération...' : '📄 Télécharger le Rapport PDF Complet'}
          </button>
          <button type="button" onClick={sendToExpert} className="expert-button">
            👨‍💼 Prendre RDV avec un Expert
          </button>
        </div>
        
        <div className="contact-cta">
          <h4>🤝 Prochaines étapes de votre projet</h4>
          <p>Nos experts sont à votre disposition pour finaliser votre installation solaire</p>
          <div className="contact-grid">
            <div className="contact-method">
              <h5>📞 Par téléphone</h5>
              <a href="tel:0985605051" className="contact-btn primary">09 85 60 50 51</a>
              <small>Lun-Ven 8h30-18h30</small>
            </div>
            <div className="contact-method">
              <h5>✉️ Par email</h5>
              <a href="mailto:contact@francerenovhabitat.com" className="contact-btn secondary">contact@francerenovhabitat.com</a>
              <small>Réponse sous 24h</small>
            </div>
            <div className="contact-method">
              <h5>📍 Agence</h5>
              <p className="address">196 Avenue Jean Lolive<br/>93500 Pantin</p>
            </div>
          </div>
          
          <div className="guarantee-section">
            <h5>🛡️ Nos garanties</h5>
            <div className="guarantees">
              <span>✅ Devis gratuit et sans engagement</span>
              <span>✅ Installation par équipes RGE certifiées</span>
              <span>✅ Garantie décennale incluse</span>
              <span>✅ Suivi de production à vie</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
// Écran de calcul avec countdown 4 minutes - Version Premium
const CalculationScreen = ({ formData, onComplete, onPrevious }) => {
  const [countdown, setCountdown] = useState(240); // 4 minutes = 240 secondes
  const [currentPhase, setCurrentPhase] = useState(0);
  const [calculationResults, setCalculationResults] = useState(null);
  const [isCalculating, setIsCalculating] = useState(true);
  const [currentAnimation, setCurrentAnimation] = useState(0);
  const [isDemoMode, setIsDemoMode] = useState(false);

  // Phases d'explication pendant les 4 minutes avec animations
  const phases = [
    {
      title: "🌍 Géolocalisation de votre adresse",
      description: "Nous localisons précisément votre domicile pour obtenir les données d'ensoleillement de la Commission Européenne PVGIS...",
      duration: 60,
      tips: [
        "💡 Nous utilisons les coordonnées GPS exactes",
        "🌞 Calcul de l'irradiation solaire spécifique à votre région", 
        "📊 Données météorologiques sur 15 ans"
      ]
    },
    {
      title: "🔬 Consultation PVGIS Commission Européenne",
      description: "Récupération des données officielles d'ensoleillement et calcul de la production solaire optimale...",
      duration: 60,
      tips: [
        "🏛️ Base de données officielle européenne",
        "⚡ Calcul selon l'orientation " + formData.roofOrientation,
        "📈 Production mensuelle détaillée"
      ]
    },
    {
      title: "🔧 Optimisation de votre installation",
      description: "Analyse de votre consommation (" + formData.annualConsumption + " kWh/an) et sélection du kit optimal...",
      duration: 60,
      tips: [
        "🏠 Surface disponible: " + formData.roofSurface + " m²",
        "⚡ Système: " + formData.heatingSystem,
        "🎯 Recherche du meilleur rapport autonomie/investissement"
      ]
    },
    {
      title: "💰 Calculs financiers et d'amortissement",
      description: "Calcul des économies, du financement optimal et du retour sur investissement...",
      duration: 59,
      tips: [
        "💳 Mensualité actuelle: " + formData.monthlyEdfPayment + " €/mois",
        "🏦 Simulation sur 6 à 15 ans",
        "🎁 Calcul des aides (Prime + TVA)"
      ]
    }
  ];

  useEffect(() => {
    const speed = isDemoMode ? 10 : 1000; // 10ms en mode démo, 1000ms normal
    
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
    }, speed);

    return () => clearInterval(timer);
  }, [isDemoMode]);

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

  useEffect(() => {
    // Animation des tips
    const animTimer = setInterval(() => {
      setCurrentAnimation(prev => (prev + 1) % 3);
    }, 2000);

    return () => clearInterval(animTimer);
  }, []);

  const performCalculation = async () => {
    try {
      setCurrentPhase(phases.length); // Phase finale
      
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

      // Ensuite faire le calcul PVGIS
      const calculationResponse = await axios.post(`${API}/calculate/${clientId}`);
      
      setCalculationResults(calculationResponse.data);
      setTimeout(() => onComplete(calculationResponse.data), 2000);

    } catch (error) {
      console.error('Erreur lors du calcul:', error);
      alert('Erreur lors du calcul. Veuillez vérifier votre adresse et réessayer.');
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const progressPercentage = ((240 - countdown) / 240) * 100;

  const toggleDemoMode = () => {
    setIsDemoMode(!isDemoMode);
  };

  if (!isCalculating && calculationResults) {
    return (
      <div className="calculation-screen success">
        <div className="success-animation">
          <div className="success-circle">✅</div>
          <h2>🎉 Calcul terminé avec succès !</h2>
          <p>Votre solution solaire personnalisée est prête</p>
          
          <div className="quick-results">
            <div className="quick-result-item">
              <span className="quick-number">{calculationResults.kit_power} kW</span>
              <span className="quick-label">Kit recommandé</span>
            </div>
            <div className="quick-result-item">
              <span className="quick-number">{Math.round(calculationResults.autonomy_percentage)}%</span>
              <span className="quick-label">Autonomie</span>
            </div>
            <div className="quick-result-item">
              <span className="quick-number">{Math.round(calculationResults.estimated_savings)} €</span>
              <span className="quick-label">Économies/an</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="calculation-screen">
      <div className="calculation-header">
        <h2>🚀 Calcul de votre solution solaire en cours</h2>
        <p>Analyse PVGIS Commission Européenne - Données officielles</p>
        
        {/* Mode démo pour les démonstrations */}
        <button 
          className="demo-toggle"
          onClick={toggleDemoMode}
          title="Mode démo : accélère le calcul pour les démonstrations"
        >
          {isDemoMode ? '⚡ Mode Démo ON' : '🐌 Mode Normal'}
        </button>
      </div>
      
      <div className="countdown-section">
        <div className="countdown-circle">
          <svg width="200" height="200" className="countdown-svg">
            <circle
              cx="100"
              cy="100"
              r="90"
              stroke="#e0e0e0"
              strokeWidth="8"
              fill="none"
            />
            <circle
              cx="100"
              cy="100"
              r="90"
              stroke="url(#gradient)"
              strokeWidth="8"
              fill="none"
              strokeDasharray={`${progressPercentage * 5.65} 565`}
              strokeLinecap="round"
              className="progress-circle"
            />
            <defs>
              <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#ff6b35" />
                <stop offset="100%" stopColor="#4caf50" />
              </linearGradient>
            </defs>
          </svg>
          <div className="countdown-text">
            <div className="countdown-number">{formatTime(countdown)}</div>
            <div className="countdown-label">restantes</div>
            <div className="countdown-progress">{Math.round(progressPercentage)}%</div>
          </div>
        </div>
      </div>

      <div className="calculation-phase">
        <h3>{phases[currentPhase]?.title}</h3>
        <p>{phases[currentPhase]?.description}</p>
        
        <div className="phase-tips">
          {phases[currentPhase]?.tips.map((tip, index) => (
            <div 
              key={index} 
              className={`tip-item ${index === currentAnimation ? 'active' : ''}`}
            >
              {tip}
            </div>
          ))}
        </div>
      </div>

      <div className="calculation-info">
        <div className="info-section">
          <h4>📋 Récapitulatif de votre demande</h4>
          <div className="info-grid">
            <div className="info-item">
              <span className="info-label">👤 Client :</span>
              <span className="info-value">{formData.firstName} {formData.lastName}</span>
            </div>
            <div className="info-item">
              <span className="info-label">📍 Adresse :</span>
              <span className="info-value">{formData.address}</span>
            </div>
            <div className="info-item">
              <span className="info-label">🏠 Surface :</span>
              <span className="info-value">{formData.roofSurface} m²</span>
            </div>
            <div className="info-item">
              <span className="info-label">🧭 Orientation :</span>
              <span className="info-value">{formData.roofOrientation}</span>
            </div>
            <div className="info-item">
              <span className="info-label">⚡ Consommation :</span>
              <span className="info-value">{formData.annualConsumption} kWh/an</span>
            </div>
            <div className="info-item">
              <span className="info-label">💳 Facture EDF :</span>
              <span className="info-value">{formData.monthlyEdfPayment} €/mois</span>
            </div>
          </div>
        </div>
      </div>

      <div className="calculation-note">
        <div className="note-content">
          <h4>🏛️ Données source PVGIS Commission Européenne</h4>
          <p>Ce temps nous permet d'expliquer le fonctionnement de votre future installation et de calculer précisément votre potentiel solaire selon les données météorologiques officielles européennes.</p>
          {isDemoMode && (
            <p style={{color: '#ff6b35', fontWeight: 'bold'}}>⚡ Mode démo activé - Calcul accéléré pour la démonstration</p>
          )}
        </div>
      </div>

      <div className="form-buttons">
        <button type="button" onClick={onPrevious} className="prev-button">⬅️ Précédent</button>
      </div>
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

  if (currentStep === 'technical') {
    return (
      <div className="App">
        <TechnicalInfoForm 
          formData={formData} 
          setFormData={setFormData} 
          onNext={handleNext} 
          onPrevious={handlePrevious} 
        />
      </div>
    );
  }

  if (currentStep === 'heating') {
    return (
      <div className="App">
        <HeatingSystemForm 
          formData={formData} 
          setFormData={setFormData} 
          onNext={handleNext} 
          onPrevious={handlePrevious} 
        />
      </div>
    );
  }

  if (currentStep === 'consumption') {
    return (
      <div className="App">
        <ConsumptionForm 
          formData={formData} 
          setFormData={setFormData} 
          onNext={handleNext} 
          onPrevious={handlePrevious} 
        />
      </div>
    );
  }

  if (currentStep === 'calculation') {
    return (
      <div className="App">
        <CalculationScreen 
          formData={formData} 
          onComplete={handleCalculationComplete}
          onPrevious={handlePrevious}
        />
      </div>
    );
  }

  if (currentStep === 'results') {
    return (
      <div className="App">
        <ResultsScreen 
          results={calculationResults}
          onPrevious={handlePrevious}
          onNewCalculation={handleNewCalculation}
        />
      </div>
    );
  }

  // Fallback
  return (
    <div className="App">
      <div className="error-screen">
        <h2>⚠️ Erreur de navigation</h2>
        <p>Une erreur s'est produite. Retour à l'accueil...</p>
        <button onClick={handleNewCalculation} className="error-button">
          🏠 Retour à l'accueil
        </button>
      </div>
    </div>
  );
}

export default App;