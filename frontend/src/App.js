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

// Écran de démarrage amélioré
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
      
      <div className="certifications">
        <div className="cert-badge rge">🏆 RGE QualiPV 2025</div>
        <div className="cert-badge rge">🏆 RGE QualiPac 2025</div>
        <div className="cert-badge ffb">🏢 FFB Adhérent</div>
        <div className="cert-badge edf">⚡ Partenaire AGIR PLUS EDF</div>
        <div className="cert-badge decennale">🛡️ Garantie Décennale 10 ans</div>
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

// Écran de résultats
const ResultsScreen = ({ results, onPrevious }) => {
  const generatePDF = () => {
    // TODO: Implémenter la génération PDF
    alert('Génération PDF - À implémenter');
  };

  return (
    <div className="results-screen">
      <h2>✅ Votre Solution Solaire Personnalisée</h2>
      
      <div className="results-grid">
        <div className="result-card primary">
          <h3>Kit Recommandé</h3>
          <div className="big-number">{results.kit_power} kW</div>
          <p>{results.panel_count} panneaux de 500W</p>
          <p className="price">{results.kit_price?.toLocaleString()} € TTC</p>
        </div>

        <div className="result-card">
          <h3>Production Annuelle</h3>
          <div className="big-number">{Math.round(results.estimated_production)} kWh</div>
          <p>Données source PVGIS Commission Européenne</p>
          <p>Orientation: {results.orientation}</p>
        </div>

        <div className="result-card">
          <h3>Autonomie</h3>
          <div className="big-number">{Math.round(results.autonomy_percentage)}%</div>
          <p>Autoconsommation estimée</p>
        </div>

        <div className="result-card success">
          <h3>Économies Annuelles</h3>
          <div className="big-number">{Math.round(results.estimated_savings)} €</div>
          <p>Soit {Math.round(results.monthly_savings)} €/mois</p>
        </div>
      </div>

      <div className="financing-section">
        <h3>💰 Financement et Aides</h3>
        <div className="financing-grid">
          <div className="financing-card">
            <h4>Aides Disponibles</h4>
            <p>Prime autoconsommation: <strong>{results.autoconsumption_aid} €</strong></p>
            {results.tva_refund > 0 && (
              <p>TVA remboursée: <strong>{Math.round(results.tva_refund)} €</strong></p>
            )}
            <p className="total-aids">Total aides: <strong>{Math.round(results.total_aids)} €</strong></p>
          </div>
          
          <div className="financing-card">
            <h4>Financement Optimal</h4>
            {results.financing_options && results.financing_options.length > 0 && (
              <div>
                <p>Durée recommandée: <strong>{results.financing_options[0].duration_years} ans</strong></p>
                <p>Mensualité: <strong>{Math.round(results.financing_options[0].monthly_payment)} €</strong></p>
                <p>Économie mensuelle: <strong>{Math.round(results.monthly_savings)} €</strong></p>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="form-buttons">
        <button type="button" onClick={onPrevious} className="prev-button">Précédent</button>
        <button type="button" onClick={generatePDF} className="pdf-button">📄 Générer le Rapport PDF</button>
      </div>
    </div>
  );
};
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
  const [calculationResults, setCalculationResults] = useState(null);
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
    const steps = ['start', 'personal', 'technical', 'heating', 'consumption', 'calculation'];
    const currentIndex = steps.indexOf(currentStep);
    if (currentIndex > 0) {
      setCurrentStep(steps[currentIndex - 1]);
    }
  };

  const handleCalculationComplete = (results) => {
    setCalculationResults(results);
    setCurrentStep('results');
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
        <div style={{position: 'fixed', top: '10px', left: '10px', background: 'black', color: 'white', padding: '5px', zIndex: 1000}}>
          Debug: {currentStep}
        </div>
        <ResultsScreen 
          results={calculationResults}
          onPrevious={handlePrevious}
        />
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