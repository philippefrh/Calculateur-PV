import React, { useState, useEffect, useRef } from "react";
import SolarAnimationCSS from './SolarAnimationCSS';
import "./App.css";
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Logo d'autonomie - Composant principal demandé
const AutonomyLogo = () => (
  <div className="autonomy-logo-container">
    <div className="autonomy-logo">
      <div className="autonomy-section red">
        <span className="autonomy-text">POURCENTAGE D'AUTONOMIE DE COULEUR ROUGE TROUVÉ = Ne permet pas l'envois de votre dossier en commission</span>
        <span className="autonomy-status negative">Négatif</span>
      </div>
      <div className="autonomy-section green">
        <span className="autonomy-text">POURCENTAGE D'AUTONOMIE DE COULEUR VERT TROUVÉ = Permet l'envois de votre dossier en commission</span>
        <span className="autonomy-status positive">Positif</span>
      </div>
    </div>
  </div>
);

// Composant sélecteur de région
const RegionSelector = ({ selectedRegion, onRegionChange, regionConfig }) => {
  return (
    <div className="region-selector">
      <div className="region-options">
        <button 
          className={`region-btn ${selectedRegion === 'france' ? 'active' : ''}`}
          onClick={() => onRegionChange('france')}
        >
          🇫🇷 France
        </button>
        <button 
          className={`region-btn ${selectedRegion === 'martinique' ? 'active' : ''}`}
          onClick={() => onRegionChange('martinique')}
        >
          🇲🇶 Martinique
        </button>
      </div>
    </div>
  );
};

// Composant sélecteur de mode de calcul
const CalculationModeSelector = ({ selectedMode, onModeChange, calculationModes }) => {
  if (!calculationModes) return null;
  
  return (
    <div className="calculation-mode-selector">
      <div className="mode-options">
        {Object.entries(calculationModes).map(([modeKey, modeInfo]) => (
          <button 
            key={modeKey}
            className={`mode-btn ${selectedMode === modeKey ? 'active' : ''}`}
            onClick={() => onModeChange(modeKey)}
          >
            <div className="mode-title">{modeInfo.name}</div>
          </button>
        ))}
      </div>
    </div>
  );
};

// Écran de démarrage amélioré avec vrais logos
const StartScreen = ({ onStart, regionConfig }) => {
  
  console.log('StartScreen rendered with regionConfig:', regionConfig);
  
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
          {regionConfig?.logo_subtitle && (
            <div className="region-subtitle">{regionConfig.logo_subtitle}</div>
          )}
        </div>
        <h1 className="company-title">Installateur Photovoltaïque</h1>
        <p className="company-subtitle">{regionConfig?.company_info?.subtitle || "FRH ENVIRONNEMENT - Énergie Solaire Professionnel"}</p>
        {regionConfig?.company_info?.address && (
          <p className="company-address">{regionConfig.company_info.address}</p>
        )}
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
      
      {/* Logos officiels des certifications */}
      <div className="certifications">
        <div className="cert-row">
          <div className="cert-badge official rge-qualipv">
            <img src="https://www.qualit-enr.org/wp-content/uploads/2024/12/logo-QualiPV-2025-RGE_sc.png" alt="RGE QualiPV 2025" className="rge-logo-small" />
            <span>RGE QualiPV 2025</span>
          </div>
          <div className="cert-badge official rge-qualipac">
            <img src="https://www.qualit-enr.org/wp-content/uploads/2024/12/logo-QualiPAC-2025-RGE_sc.png" alt="RGE QualiPac 2025" className="rge-logo-small" />
            <span>RGE QualiPac 2025</span>
          </div>
        </div>
        
        <div className="cert-row">
          <div className="cert-badge official ffb">
            <img src="https://www.ffbatiment.fr/-/media/Project/FFB/shared/Logos/logo-federation-francaise-du-batiment.png?h=196&iar=0&w=240&rev=f33feb1bc41b4da682356e6820f4cf36&hash=89C478B0995E262614796430902176D4" alt="FFB Adhérent" className="ffb-logo" />
            <span>FFB Adhérent</span>
          </div>
          <div className="cert-badge official edf">
            <img src="https://www.dometis.re/wp-content/uploads/2025/05/agir-plus.png" alt="Partenaire AGIR PLUS EDF" className="agir-plus-logo" />
            <span>⚡ Partenaire AGIR PLUS EDF</span>
          </div>
        </div>
        
        <div className="cert-row">
          <div className="cert-badge official mma-decennale centered">
            <img src="https://www.mma.fr/files/live/sites/mmafr/files/divers/logo_mma.png" alt="MMA Assurance Décennale" className="mma-logo-centered" />
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
    if (!formData.phone.trim()) newErrors.phone = "Le téléphone est obligatoire";
    if (!formData.email.trim()) newErrors.email = "L'email est obligatoire";
    else if (!/\S+@\S+\.\S+/.test(formData.email)) newErrors.email = "Format email invalide";
    
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
        
        <div className="form-group">
          <label>📞 Téléphone *</label>
          <input
            type="tel"
            value={formData.phone}
            onChange={(e) => setFormData({...formData, phone: e.target.value})}
            placeholder="0659597690"
            className={errors.phone ? 'error' : ''}
            required
          />
          {errors.phone && <span className="error-message">{errors.phone}</span>}
          <small>💡 Votre numéro de téléphone pour vous contacter</small>
        </div>
        
        <div className="form-group">
          <label>📧 Email *</label>
          <input
            type="email"
            value={formData.email}
            onChange={(e) => setFormData({...formData, email: e.target.value})}
            placeholder="votre.email@example.com"
            className={errors.email ? 'error' : ''}
            required
          />
          {errors.email && <span className="error-message">{errors.email}</span>}
          <small>💡 Votre email pour recevoir le devis et la documentation</small>
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
    if (!formData.meterType) newErrors.meterType = "Type de compteur obligatoire";
    if (!formData.meterPower) newErrors.meterPower = "Puissance compteur obligatoire";
    if (!formData.phaseType) newErrors.phaseType = "Type de phase obligatoire";
    
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
    if (heating.includes("Cheminée") || heating.includes("Poêle")) {
      return "🔥 Chauffage au bois - Le solaire complètera parfaitement votre système";
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
          <label>🔥 Système(s) de chauffage actuel(s) *</label>
          
          {/* Système principal */}
          <div className="heating-system-selector">
            <label className="system-label">Système principal :</label>
            <select
              value={formData.heatingSystem || ''}
              onChange={(e) => setFormData({...formData, heatingSystem: e.target.value})}
              className={errors.heatingSystem ? 'error' : ''}
              required
            >
              <option value="">Sélectionnez votre système principal</option>
              <option value="Radiateurs électriques">⚡ Radiateurs électriques</option>
              <option value="Chauffage électrique avec plancher chauffant">⚡ Plancher chauffant électrique</option>
              <option value="Chaudière Gaz">🔥 Chaudière Gaz</option>
              <option value="Chaudière Fuel">🛢️ Chaudière Fuel</option>
              <option value="Chaudière électrique">⚡ Chaudière électrique</option>
              <option value="Pompe à chaleur Air-Air réversible">❄️🔥 Pompe à chaleur Air-Air (réversible)</option>
              <option value="Pompe à chaleur Air-Eau">💧🔥 Pompe à chaleur Air-Eau</option>
              <option value="Cheminée">🔥 Cheminée</option>
              <option value="Poêle à bois">🪵 Poêle à bois</option>
              <option value="Poêle à granulé">🌾 Poêle à granulé</option>
            </select>
          </div>
          
          {/* Systèmes d'appoint */}
          <div className="heating-system-additional">
            <label className="system-label">Système(s) d'appoint :</label>
            <select
              value=""
              onChange={(e) => {
                if (e.target.value) {
                  const additionalSystems = formData.additionalHeatingSystems || [];
                  if (!additionalSystems.includes(e.target.value)) {
                    setFormData({
                      ...formData, 
                      additionalHeatingSystems: [...additionalSystems, e.target.value]
                    });
                  }
                  e.target.value = '';
                }
              }}
            >
              <option value="">+ Ajouter un système d'appoint</option>
              <option value="Radiateurs électriques">⚡ Radiateurs électriques</option>
              <option value="Chauffage électrique avec plancher chauffant">⚡ Plancher chauffant électrique</option>
              <option value="Chaudière Gaz">🔥 Chaudière Gaz</option>
              <option value="Chaudière Fuel">🛢️ Chaudière Fuel</option>
              <option value="Chaudière électrique">⚡ Chaudière électrique</option>
              <option value="Pompe à chaleur Air-Air réversible">❄️🔥 Pompe à chaleur Air-Air (réversible)</option>
              <option value="Pompe à chaleur Air-Eau">💧🔥 Pompe à chaleur Air-Eau</option>
              <option value="Cheminée">🔥 Cheminée</option>
              <option value="Poêle à bois">🪵 Poêle à bois</option>
              <option value="Poêle à granulé">🌾 Poêle à granulé</option>
            </select>
          </div>
          
          {/* Affichage des systèmes d'appoint sélectionnés */}
          {formData.additionalHeatingSystems && formData.additionalHeatingSystems.length > 0 && (
            <div className="selected-additional-systems">
              <p className="additional-systems-label">Systèmes d'appoint sélectionnés :</p>
              <div className="additional-systems-list">
                {formData.additionalHeatingSystems.map((system, index) => (
                  <div key={index} className="additional-system-item">
                    <span>{system}</span>
                    <button
                      type="button"
                      className="remove-system-btn"
                      onClick={() => {
                        const updatedSystems = formData.additionalHeatingSystems.filter((_, i) => i !== index);
                        setFormData({
                          ...formData,
                          additionalHeatingSystems: updatedSystems
                        });
                      }}
                    >
                      ✕
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
          
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
        
        <div className="form-group">
          <label>🧺 Machine à laver</label>
          <select
            value={formData.washingMachine || ''}
            onChange={(e) => setFormData({...formData, washingMachine: e.target.value})}
          >
            <option value="">Sélectionnez le nombre</option>
            <option value="1">1 machine à laver</option>
            <option value="2">2 machines à laver</option>
            <option value="3">3 machines à laver</option>
          </select>
        </div>
        
        <div className="form-group">
          <label>🌬️ Sèche linge</label>
          <select
            value={formData.dryer || ''}
            onChange={(e) => setFormData({...formData, dryer: e.target.value})}
          >
            <option value="">Avez-vous un sèche linge ?</option>
            <option value="oui">Oui</option>
            <option value="non">Non</option>
          </select>
        </div>
        
        <div className="form-group">
          <label>🍽️ Lave vaisselle</label>
          <select
            value={formData.dishwasher || ''}
            onChange={(e) => setFormData({...formData, dishwasher: e.target.value})}
          >
            <option value="">Avez-vous un lave vaisselle ?</option>
            <option value="oui">Oui</option>
            <option value="non">Non</option>
          </select>
        </div>
        
        <div className="form-group">
          <label>🧊 Frigo</label>
          <select
            value={formData.refrigerator || ''}
            onChange={(e) => setFormData({...formData, refrigerator: e.target.value})}
          >
            <option value="">Sélectionnez le nombre</option>
            <option value="1">1 frigo</option>
            <option value="2">2 frigos</option>
            <option value="3">3 frigos</option>
          </select>
        </div>
        
        <div className="form-group">
          <label>🔥 Four électrique</label>
          <select
            value={formData.electricOven || ''}
            onChange={(e) => setFormData({...formData, electricOven: e.target.value})}
          >
            <option value="">Avez-vous un four électrique ?</option>
            <option value="oui">Oui</option>
            <option value="non">Non</option>
          </select>
        </div>
        
        <div className="form-group">
          <label>🍳 Plaque de cuisson</label>
          <select
            value={formData.cookingPlate || ''}
            onChange={(e) => setFormData({...formData, cookingPlate: e.target.value})}
          >
            <option value="">Sélectionnez le type</option>
            <option value="electrique">⚡ Électrique</option>
            <option value="gaz">🔥 Gaz</option>
          </select>
        </div>
        
        <div className="form-group">
          <label>💨 Hotte aspirante</label>
          <select
            value={formData.hood || ''}
            onChange={(e) => setFormData({...formData, hood: e.target.value})}
          >
            <option value="">Avez-vous une hotte aspirante ?</option>
            <option value="oui">Oui</option>
            <option value="non">Non</option>
          </select>
        </div>
        
        <div className="form-group">
          <label>🌀 VMC (Ventilation Mécanique Contrôlée)</label>
          <select
            value={formData.vmc || ''}
            onChange={(e) => setFormData({...formData, vmc: e.target.value})}
          >
            <option value="">Sélectionnez le type de VMC</option>
            <option value="simple_flux">🌀 Simple flux</option>
            <option value="double_flux">🌀🌀 Double flux</option>
            <option value="non">Non</option>
          </select>
        </div>
        
        <div className="form-group">
          <label>🔌 Quel type de compteur *</label>
          <select
            value={formData.meterType}
            onChange={(e) => setFormData({...formData, meterType: e.target.value})}
            className={errors.meterType ? 'error' : ''}
            required
          >
            <option value="">Sélectionnez votre type de compteur</option>
            <option value="Compteur classique">⚙️ Compteur classique</option>
            <option value="Compteur LINKY">📡 Compteur LINKY</option>
          </select>
          {errors.meterType && <span className="error-message">{errors.meterType}</span>}
        </div>
        
        <div className="form-group">
          <label>⚡ Puissance compteur (kW) *</label>
          <input
            type="number"
            value={formData.meterPower}
            onChange={(e) => setFormData({...formData, meterPower: e.target.value})}
            placeholder="ex: 6, 9, 12, 14, 18, 22"
            min="3"
            max="36"
            step="1"
            className={errors.meterPower ? 'error' : ''}
            required
          />
          {errors.meterPower && <span className="error-message">{errors.meterPower}</span>}
          <small>💡 Puissance standard : 6kW, 9kW, 12kW, 14kW, 18kW, 22kW</small>
        </div>
        
        <div className="form-group">
          <label>🔌 Monophasé - Triphasé *</label>
          <select
            value={formData.phaseType}
            onChange={(e) => setFormData({...formData, phaseType: e.target.value})}
            className={errors.phaseType ? 'error' : ''}
            required
          >
            <option value="">Sélectionnez le type de phase</option>
            <option value="Monophasé">🔌 Monophasé</option>
            <option value="Triphasé">🔌🔌🔌 Triphasé</option>
          </select>
          {errors.phaseType && <span className="error-message">{errors.phaseType}</span>}
        </div>
        
        <div className="form-buttons">
          <button type="button" onClick={onPrevious} className="prev-button">⬅️ Précédent</button>
          <button type="submit" className="next-button">Suivant ➡️</button>
        </div>
      </form>
    </div>
  );
};

// Formulaire étape 4 - Consommation amélioré
const ConsumptionForm = ({ 
  formData, 
  setFormData, 
  onNext, 
  onPrevious, 
  selectedRegion = "france"
}) => {
  const [errors, setErrors] = useState({});
  const [showKitSelection, setShowKitSelection] = useState(false);
  const [availableKits, setAvailableKits] = useState([]);
  const [selectedKit, setSelectedKit] = useState(null);
  const [loadingKits, setLoadingKits] = useState(false);

  // Recharger les kits quand la région change
  useEffect(() => {
    if (showKitSelection) {
      setAvailableKits([]);
      fetchAvailableKits();
    }
  }, [selectedRegion]);

  // Récupérer les kits solaires disponibles selon la région
  const fetchAvailableKits = async () => {
    if (availableKits.length > 0) return; // Déjà chargés
    
    setLoadingKits(true);
    try {
      const response = await fetch(`${API}/regions/${selectedRegion}/kits`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      const kits = data.kits;
      
      // Transformer les données selon la région
      if (selectedRegion === "martinique") {
        // Pour Martinique, utiliser les données directement
        const kitsWithDetails = kits.map(kit => ({
          power: kit.power,
          panels: Math.round(kit.power / 0.5), // Estimé à 0.5kW par panneau
          priceTTC: kit.price_ttc,
          priceHT: kit.price_ttc, // Prix TTC en Martinique
          commission: Math.round(kit.co2_savings), // 15% du prix TTC
          surface: kit.surface,
          autoconsumptionAid: kit.aid_amount,
          tvaRefund: 0, // Pas de TVA en Martinique
          totalAids: kit.aid_amount,
          priceWithAids: kit.price_ttc - kit.aid_amount,
          description: kit.name
        }));
        
        setAvailableKits(kitsWithDetails);
      } else {
        // Pour France, utiliser la logique existante
        const kitsWithDetails = Object.entries(kits).map(([power, info]) => {
          const kitPower = parseInt(power);
          const priceHT = info.price / 1.2; // Prix HT (TTC / 1.2)
          const commission = priceHT * 0.15; // Commission 15%
          const surfaceTotal = info.panels * 2.1; // Surface par panneau: 2.1m²
          
          // Calcul des aides
          const autoconsumptionAid = kitPower * 80; // 80€/kW
          const tvaRefund = kitPower > 3 ? info.price * 0.2 : 0; // TVA 20% si > 3kW
          const totalAids = autoconsumptionAid + tvaRefund;
          const priceWithAids = info.price - totalAids;
          
          return {
            power: kitPower,
            panels: info.panels,
            priceTTC: info.price,
            priceHT: Math.round(priceHT),
            commission: Math.round(commission),
            surface: surfaceTotal,
            autoconsumptionAid,
            tvaRefund: Math.round(tvaRefund),
            totalAids: Math.round(totalAids),
            priceWithAids: Math.round(priceWithAids)
          };
        });
        
        setAvailableKits(kitsWithDetails);
      }
      
      // Trier les kits par puissance
      setAvailableKits(prev => [...prev].sort((a, b) => a.power - b.power));
    } catch (error) {
      console.error('Erreur lors du chargement des kits:', error);
      alert('Erreur lors du chargement des kits. Veuillez réessayer.');
    }
    setLoadingKits(false);
  };

  const handleShowKitSelection = () => {
    setShowKitSelection(true);
    fetchAvailableKits();
  };

  const handleSelectKit = (kit) => {
    setSelectedKit(kit);
    // Mettre à jour le formData avec le kit sélectionné
    setFormData(prev => ({
      ...prev,
      selectedManualKit: kit
    }));
  };

  const handleConfirmKitSelection = () => {
    if (selectedKit) {
      setFormData(prev => ({
        ...prev,
        useManualKit: true,
        manualKit: selectedKit
      }));
      setShowKitSelection(false);
      alert(`Kit ${selectedKit.power}kW sélectionné avec succès !`);
    }
  };

  const handleCancelKitSelection = () => {
    setShowKitSelection(false);
    setSelectedKit(null);
    setFormData(prev => ({
      ...prev,
      useManualKit: false,
      manualKit: null,
      selectedManualKit: null
    }));
  };

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
    return monthly * 12; // 12 mois pour calcul annuel
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
          </div>
        )}

        {/* Section de sélection manuelle des kits */}
        {formData.monthlyEdfPayment && (
          <div className="kit-selection-section">
            {!showKitSelection ? (
              <div className="kit-selection-toggle">
                <button 
                  type="button" 
                  className="show-kits-button"
                  onClick={handleShowKitSelection}
                >
                  📋 Voir tous les kits disponibles avec puissances et surfaces
                </button>
                <small>Cliquez pour voir la liste complète des kits et sélectionner manuellement</small>
              </div>
            ) : (
              <div className="kit-selection-panel">
                <div className="kit-selection-header">
                  <h4>🔧 Sélection manuelle du kit solaire</h4>
                  <button 
                    type="button" 
                    className="close-kits-button"
                    onClick={handleCancelKitSelection}
                  >
                    ✕ Fermer
                  </button>
                </div>
                
                {loadingKits ? (
                  <div className="loading-kits">
                    <div className="loading-spinner"></div>
                    <p>Chargement des kits disponibles...</p>
                  </div>
                ) : (
                  <div className="kits-grid">
                    {availableKits.map((kit) => (
                      <div 
                        key={kit.power} 
                        className={`kit-card ${selectedKit?.power === kit.power ? 'selected' : ''}`}
                        onClick={() => handleSelectKit(kit)}
                      >
                        <div className="kit-header">
                          <h5>Kit {kit.power}kW</h5>
                          <span className="kit-panels">{kit.panels} panneaux</span>
                        </div>
                        
                        <div className="kit-details">
                          <div className="kit-detail-row">
                            <span>Surface totale:</span>
                            <span>{kit.surface}m²</span>
                          </div>
                          <div className="kit-detail-row">
                            <span>Prix TTC:</span>
                            <span>{kit.priceTTC.toLocaleString()}€</span>
                          </div>
                          <div className="kit-detail-row">
                            <span>Prix avec aides:</span>
                            <span className="price-with-aids">{kit.priceWithAids.toLocaleString()}€</span>
                          </div>
                          <div className="kit-detail-row commission">
                            <span>CO2 économisé:</span>
                            <span>{kit.commission} kilos/an</span>
                          </div>
                        </div>
                        
                        {selectedKit?.power === kit.power && (
                          <div className="kit-selected-indicator">
                            ✓ Sélectionné
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
                
                {selectedKit && !loadingKits && (
                  <div className="kit-selection-actions">
                    <button 
                      type="button" 
                      className="confirm-kit-button"
                      onClick={handleConfirmKitSelection}
                    >
                      ✓ Confirmer la sélection du Kit {selectedKit.power}kW
                    </button>
                    <button 
                      type="button" 
                      className="cancel-kit-button"
                      onClick={handleCancelKitSelection}
                    >
                      ✕ Annuler et utiliser la recommandation automatique
                    </button>
                  </div>
                )}
                
                <div className="kit-selection-note">
                  <p><strong>ℹ️ Mode commercial :</strong> Cette sélection remplacera la recommandation automatique pour les calculs suivants.</p>
                </div>
              </div>
            )}
            
            {formData.useManualKit && formData.manualKit && (
              <div className="manual-kit-selected">
                <div className="selected-kit-info">
                  <h5>🎯 Kit sélectionné manuellement</h5>
                  <div className="selected-kit-details">
                    <span>Kit {formData.manualKit.power}kW ({formData.manualKit.panels} panneaux)</span>
                    <span>Prix avec aides: {formData.manualKit.priceWithAids.toLocaleString()}€</span>
                  </div>
                  <button 
                    type="button" 
                    className="change-kit-button"
                    onClick={handleShowKitSelection}
                  >
                    🔄 Changer de kit
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
        
        <div className="consumption-summary">
          <h4>📋 Résumé de votre profil :</h4>
          <p><strong>🏠</strong> {formData.firstName} {formData.lastName}</p>
          <p><strong>📍</strong> {formData.address}</p>
          <p><strong>📞</strong> {formData.phone}</p>
          <p><strong>📧</strong> {formData.email}</p>
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
const ResultsScreen = ({ results, onPrevious, selectedRegion, setCurrentStep }) => {
  const [activeTab, setActiveTab] = useState('overview');
  const [showFinancing, setShowFinancing] = useState(false);
  const [isGeneratingPDF, setIsGeneratingPDF] = useState(false);
  const [isGeneratingDevis, setIsGeneratingDevis] = useState(false);

  // Protection contre les résultats null/undefined
  if (!results) {
    return (
      <div className="App">
        <div className="results-container">
          <div className="loading-message">
            <p>Chargement des résultats...</p>
          </div>
        </div>
      </div>
    );
  }

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
      console.error('Erreur génération PDF:', error);
      // Message d'erreur
      const notification = document.querySelector('.pdf-notification');
      if (notification) {
        notification.innerHTML = '❌ Erreur lors de la génération du PDF';
        notification.style.backgroundColor = '#f44336';
        
        setTimeout(() => {
          document.body.removeChild(notification);
        }, 3000);
      }
    } finally {
      setIsGeneratingPDF(false);
    }
  };

  const generateDevis = async () => {
    try {
      setIsGeneratingDevis(true);
      
      // Afficher un message de génération
      const notification = document.createElement('div');
      notification.className = 'devis-notification';
      notification.innerHTML = '📄 Génération du devis en cours...';
      document.body.appendChild(notification);
      
      // Appel à l'API pour générer le devis
      const response = await fetch(`${API}/generate-devis/${results.client_id}?region=${selectedRegion}`, {
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
        link.download = `devis_FRH_${today}.pdf`;
        
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
        
        // Message de succès
        notification.innerHTML = '✅ Devis PDF téléchargé avec succès !';
        notification.style.backgroundColor = '#4caf50';
        
        setTimeout(() => {
          document.body.removeChild(notification);
        }, 3000);
      } else {
        throw new Error('Erreur lors de la génération du devis');
      }
    } catch (error) {
      console.error('Erreur génération devis:', error);
      // Message d'erreur
      const notification = document.querySelector('.devis-notification');
      if (notification) {
        notification.innerHTML = '❌ Erreur lors de la génération du devis';
        notification.style.backgroundColor = '#f44336';
        
        setTimeout(() => {
          document.body.removeChild(notification);
        }, 3000);
      }
    } finally {
      setIsGeneratingDevis(false);
    }
  };

  const getAutonomyColor = (percentage) => {
    if (percentage >= 80) return '#4caf50';
    if (percentage >= 60) return '#ff9800';
    return '#f44336';
  };

  const getOptimalFinancing = () => {
    if (!results || !results.financing_options) return null;
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
          {/* Indicateur du mode de calcul */}
          {results.calculation_mode && (
            <div className="calculation-mode-indicator">
              <span className="mode-icon">📊</span>
              <span className="mode-text">
                SYNTHESE et RESULTAT FINAL DES CALCULS
              </span>
            </div>
          )}
          
          {/* Nouvelle vignette avec le design demandé */}
          <div className="project-summary-table">
            <div className="summary-row">
              <div className="summary-cell dark">
                <div className="cell-title">Coût du projet</div>
                <div className="cell-value">{results.kit_price?.toLocaleString()} € TTC</div>
              </div>
              <div className="summary-cell dark">
                <div className="cell-title">KAP Photovoltaïque</div>
                <div className="cell-value">0,00 €</div>
              </div>
              <div className="summary-cell dark">
                <div className="cell-title">Prime à l'autoconsommation</div>
                <div className="cell-value">{results.total_aids?.toLocaleString()} €</div>
              </div>
              <div className="summary-cell green">
                <div className="cell-title">Coût réel du projet</div>
                <div className="cell-value">{results.financing_with_aids?.financed_amount?.toLocaleString()} €</div>
              </div>
            </div>
            <div className="summary-row">
              <div className="summary-cell dark">
                <div className="cell-title">Production annuelle du PV</div>
                <div className="cell-value">{Math.round(results.estimated_production).toLocaleString()} kWh</div>
              </div>
              <div className="summary-cell dark">
                <div className="cell-title">Durée d'amortissement *</div>
                <div className="cell-value">{Math.round(results.financing_with_aids?.duration_years)} années</div>
              </div>
              <div className="summary-cell dark">
                <div className="cell-title">Pourcentage d'économies réel</div>
                <div className="cell-value">{Math.round(results.real_savings_percentage || results.autonomy_percentage)} %</div>
              </div>
              <div className="summary-cell green">
                <div className="cell-title">Économies moyenne mensuelle</div>
                <div className="cell-value">{Math.round(results.monthly_savings)} €/mois</div>
              </div>
            </div>
          </div>

          {/* Résumé financier sous le tableau */}
          <div className="financial-summary">
            <div className="financial-item">
              <span className="financial-icon">💰</span>
              <span className="financial-label">Investissement:</span>
              <span className="financial-value">{results.kit_price?.toLocaleString()} € TTC</span>
            </div>
            <div className="financial-item">
              <span className="financial-icon">🎁</span>
              <span className="financial-label">Aides totales:</span>
              <span className="financial-value aides">-{results.total_aids?.toLocaleString()} €</span>
            </div>
            <div className="financial-item">
              <span className="financial-icon">💳</span>
              <span className="financial-label">Reste à financer:</span>
              <span className="financial-value">{results.financing_with_aids?.financed_amount?.toLocaleString()} €</span>
            </div>
            <div className="financial-item">
              <span className="financial-icon">⏱️</span>
              <span className="financial-label">Retour sur investissement:</span>
              <span className="financial-value">{Math.round(results.financing_with_aids?.duration_years)} ans</span>
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
                <h4>🏦 Options de financement recommandées</h4>
                
                {/* Financement sans aides déduites */}
                <div className="financing-card highlighted">
                  <div className="financing-header">
                    <h5>⭐ Financement standard sur {optimalFinancing.duration_years} ans</h5>
                    <span className="financing-type">Sans aides déduites</span>
                  </div>
                  <div className="financing-details">
                    <div className="financing-row">
                      <span>Investissement total:</span>
                      <span className="amount">{results.kit_price?.toLocaleString()} € TTC</span>
                    </div>
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
                </div>

                {/* Financement avec aides déduites */}
                <div className="financing-card highlighted-green">
                  <div className="financing-header">
                    <h5>💰 Financement optimisé sur {results.financing_with_aids?.duration_years?.toFixed(1)} ans</h5>
                    <span className="recommended-badge green">Avec aides déduites</span>
                  </div>
                  <div className="financing-details">
                    <div className="financing-row">
                      <span>Investissement après aides:</span>
                      <span className="amount">{results.financing_with_aids?.financed_amount?.toLocaleString()} € TTC</span>
                    </div>
                    <div className="financing-row">
                      <span>Mensualité crédit réduite:</span>
                      <span className="amount success">{Math.round(results.financing_with_aids?.monthly_payment)} €/mois</span>
                    </div>
                    <div className="financing-row">
                      <span>Économie EDF:</span>
                      <span className="amount success">{Math.round(results.monthly_savings)} €/mois</span>
                    </div>
                    <div className="financing-row">
                      <span>Reste à charge optimisé:</span>
                      <span className="amount success">
                        {Math.round(results.financing_with_aids?.difference_vs_savings)} €/mois
                      </span>
                    </div>
                  </div>
                  <div className="financing-benefits">
                    <p>✅ 6 premiers mois GRATUITS (Rien à débourser pendant les 6 premiers mois)</p>
                    <p>✅ Aides récupérées: {Math.round(results.total_aids)} € (Aides et Subventions)</p>
                    <p>✅ Réinjection des Aides et Subventions récupérées entre le 7ème et 12ème mois</p>
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
                    <span>Différence vs économies</span>
                  </div>
                  {results.financing_options?.map((option, index) => (
                    <div key={index} className="table-row">
                      <span>{option.duration_years} ans</span>
                      <span>{Math.round(option.monthly_payment)} €</span>
                      <span className={Math.abs(option.difference_vs_savings) < 20 ? 'success' : 'warning'}>
                        {option.difference_vs_savings > 0 ? '+' : ''}{Math.round(option.difference_vs_savings)} €/mois
                      </span>
                    </div>
                  ))}
                </div>

                {/* Nouveau tableau avec aides déduites */}
                <div className="all-financing-options" style={{marginTop: '30px'}}>
                  <h4>💰 Toutes les options de financement disponibles avec aides déduites</h4>
                  <div className="financing-table">
                    <div className="table-header">
                      <span>Durée</span>
                      <span>Mensualité</span>
                      <span>Différence vs économies</span>
                    </div>
                    {results.all_financing_with_aids?.map((option, index) => (
                      <div key={index} className="table-row">
                        <span>{option.duration_years} ans</span>
                        <span>{Math.round(option.monthly_payment)} €</span>
                        <span className={Math.abs(option.difference_vs_savings) < 20 ? 'success' : 'warning'}>
                          {option.difference_vs_savings > 0 ? '+' : ''}{Math.round(option.difference_vs_savings)} €/mois
                        </span>
                      </div>
                    ))}
                  </div>
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
          <button 
            type="button" 
            onClick={generateDevis} 
            className={`devis-button ${isGeneratingDevis ? 'generating' : ''}`}
            disabled={isGeneratingDevis}
          >
            {isGeneratingDevis ? '⏳ Génération...' : '📋 Générer le Devis PDF'}
          </button>
          <button type="button" onClick={sendToExpert} className="expert-button">
            👨‍💼 Prendre RDV avec un Expert
          </button>
        </div>
        
        <div className="contact-cta">
          <h4>📋 Création du dossier - Pièces à fournir</h4>
          <p>Pour finaliser votre installation solaire, nous aurons besoin des documents suivants :</p>
          
          <div className="documents-list">
            <div className="document-category">
              <h5>💡 Énergie & Consommation</h5>
              <ul>
                <li>• Votre dernière facture d'énergie (de moins de 3 mois)</li>
                <li>• EDF - Total Energie - Engie etc...</li>
                <li>• Factures box internet, téléphone portable, eau</li>
              </ul>
            </div>

            <div className="document-category">
              <h5>🆔 Identité & Situation</h5>
              <ul>
                <li>• Justificatif d'identité (CNI recto verso, Passeport, Carte de séjour)</li>
                <li>• Votre dernier avis d'imposition (les 4 volets)</li>
                <li>• Taxe foncière (les 2 volets)</li>
              </ul>
            </div>

            <div className="document-category">
              <h5>💰 Revenus & Finances</h5>
              <ul>
                <li>• Vos 2 dernières fiches de paye</li>
                <li>• Un RIB</li>
              </ul>
            </div>

            <div className="document-category">
              <h5>🏠 Propriété</h5>
              <ul>
                <li>• Votre acte notarié (2 premières feuilles seulement)</li>
                <li>• Requis si propriétaire de moins d'un an</li>
              </ul>
            </div>
          </div>
          
          <div className="next-steps-note">
            <p><strong>📞 Nos experts vous contacteront</strong> dans les 24h pour :</p>
            <ul>
              <li>✓ Valider votre étude personnalisée</li>
              <li>✓ Planifier la visite technique</li>
              <li>✓ Finaliser votre dossier de financement</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

// Pages explicatives pendant le calcul PVGIS
const EducationalPages = ({ currentPhase, countdown, formData }) => {
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  
  // Images d'installations réelles FRH Environnement
  const installations = [
    {
      id: 1,
      title: "Installation sur toiture méditerranéenne",
      description: "Installation 6kW sur tuiles rouges - Région PACA",
      features: ["12 panneaux 500W", "Orientation Sud", "Production: 8200 kWh/an"],
      image: "https://images.unsplash.com/photo-1733578234132-f40198e27f8b"
    },
    {
      id: 2,
      title: "Installation résidentielle moderne",
      description: "Installation 9kW avec système de monitoring",
      features: ["18 panneaux haute performance", "Onduleur micro", "Suivi temps réel"],
      image: "https://images.unsplash.com/photo-1720610784599-18c02b1cc9ee"
    },
    {
      id: 3,
      title: "Installation sur ardoise",
      description: "Installation 6kW sur toiture traditionnelle",
      features: ["Fixations renforcées", "Étanchéité parfaite", "Garantie 20 ans"],
      image: "https://images.unsplash.com/flagged/photo-1566838616631-f2618f74a6a2"
    },
    {
      id: 4,
      title: "Maison contemporaine avec véranda",
      description: "Installation 7kW design moderne",
      features: ["Intégration architecturale", "Performance optimisée", "Design premium"],
      image: "https://images.unsplash.com/photo-1591710369924-0dcd50436306"
    },
    {
      id: 5,
      title: "Installation professionnelle",
      description: "Équipe certifiée RGE en action",
      features: ["Installation sécurisée", "Équipe experte", "Matériel premium"],
      image: "https://images.unsplash.com/photo-1624397640148-949b1732bb0a"
    },
    {
      id: 6,
      title: "Détail fixations toiture",
      description: "Système de fixation haute qualité",
      features: ["Étanchéité garantie", "Fixation renforcée", "Longévité 25 ans"],
      image: "https://images.unsplash.com/photo-1703287209219-57f5045c1536"
    }
  ];

  const monitoringFeatures = [
    {
      title: "📱 Application mobile dédiée",
      description: "Suivez votre production en temps réel depuis votre smartphone",
      icon: "📱"
    },
    {
      title: "📊 Interface web complète", 
      description: "Tableau de bord détaillé avec historiques et analyses",
      icon: "💻"
    },
    {
      title: "📈 Rapports automatiques",
      description: "Recevez vos bilans mensuels et annuels par email", 
      icon: "📧"
    }
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentImageIndex(prev => (prev + 1) % installations.length);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  if (currentPhase === 0) {
    return (
      <div className="educational-page">
        <div className="page-header">
          <h3>🏠 Nos installations réelles FRH Environnement</h3>
          <p>Découvrez nos réalisations sur différents types de toitures</p>
        </div>
        
        <div className="installations-carousel">
          <div className="carousel-container">
            <div className="installation-showcase">
              <div className="installation-image">
                <img 
                  src={installations[currentImageIndex].image}
                  alt={installations[currentImageIndex].title}
                  className="real-installation-photo"
                />
              </div>
              <div className="installation-info">
                <h4>{installations[currentImageIndex].title}</h4>
                <p>{installations[currentImageIndex].description}</p>
                <div className="features-list">
                  {installations[currentImageIndex].features.map((feature, index) => (
                    <div key={index} className="feature-item">✅ {feature}</div>
                  ))}
                </div>
              </div>
            </div>
          </div>
          
          <div className="carousel-indicators">
            {installations.map((_, index) => (
              <div 
                key={index} 
                className={`indicator ${index === currentImageIndex ? 'active' : ''}`}
                onClick={() => setCurrentImageIndex(index)}
              />
            ))}
          </div>
        </div>
        
        <div className="installation-types">
          <div className="type-card">
            <h4>🏛️ Tous types de toitures</h4>
            <ul>
              <li>Tuiles traditionnelles</li>
              <li>Ardoise naturelle</li>
              <li>Tôle bac acier</li>
              <li>Toiture plate</li>
            </ul>
          </div>
          <div className="type-card">
            <h4>🔧 Installation professionnelle</h4>
            <ul>
              <li>Équipe certifiée RGE</li>
              <li>Matériel premium</li>
              <li>Garantie 20 ans</li>
              <li>SAV dédié</li>
            </ul>
          </div>
        </div>
      </div>
    );
  }

  if (currentPhase === 1) {
    return (
      <div className="educational-page">
        <div className="page-header">
          <h3>⚡ Comment fonctionnent vos panneaux solaires ?</h3>
          <p>Comprendre la technologie photovoltaïque en 3 étapes simples</p>
        </div>
        
        <div className="solar-explanation">
          <div className="explanation-step">
            <div className="step-number">1</div>
            <div className="step-content">
              <h4>☀️ Captation de la lumière</h4>
              <p>Les cellules photovoltaïques transforment la lumière du soleil en électricité continue</p>
              <div className="step-details">
                <span>• Technologie silicium monocristallin</span>
                <span>• Rendement jusqu'à 22%</span>
                <span>• Fonctionne même par temps nuageux</span>
              </div>
            </div>
          </div>

          <div className="explanation-step">
            <div className="step-number">2</div>
            <div className="step-content">
              <h4>🔄 Conversion en courant alternatif</h4>
              <p>L'onduleur transforme le courant continu en courant alternatif compatible avec votre maison</p>
              <div className="step-details">
                <span>• Onduleur intelligent inclus</span>
                <span>• Optimisation automatique</span>
                <span>• Monitoring intégré</span>
              </div>
            </div>
          </div>

          <div className="explanation-step">
            <div className="step-number">3</div>
            <div className="step-content">
              <h4>🏠 Utilisation dans votre foyer</h4>
              <p>L'électricité produite alimente directement vos appareils, le surplus est revendu à EDF</p>
              <div className="step-details">
                <span>• Autoconsommation prioritaire</span>
                <span>• Revente automatique du surplus</span>
                <span>• Économies immédiates</span>
              </div>
            </div>
          </div>
        </div>

        <div className="production-simulation">
          <h4>📊 Exemple de production journalière</h4>
          <div className="daily-curve">
            <div className="curve-container">
              <div className="production-curve"></div>
              <div className="time-markers">
                <span>6h</span><span>9h</span><span>12h</span><span>15h</span><span>18h</span><span>21h</span>
              </div>
            </div>
            <p>Production maximale entre 11h et 15h - Vos panneaux produisent de l'électricité du lever au coucher du soleil</p>
          </div>
        </div>
      </div>
    );
  }

  if (currentPhase === 2) {
    return (
      <div className="educational-page">
        <div className="page-header">
          <h3>📱 Suivez votre production en temps réel</h3>
          <p>Interface de monitoring professionnel incluse avec votre installation</p>
        </div>
        
        <div className="monitoring-showcase">
          <div className="monitoring-devices">
            <div className="device-card">
              <div className="device-image">
                <img 
                  src="https://images.unsplash.com/photo-1653022056328-913942485324"
                  alt="Application mobile de monitoring solaire"
                  className="monitoring-screenshot"
                />
              </div>
              <h4>📱 Application mobile</h4>
              <p>Surveillez votre installation depuis n'importe où</p>
            </div>

            <div className="device-card">
              <div className="device-image">
                <img 
                  src="https://images.unsplash.com/photo-1662601311150-c20f76b7cb20"
                  alt="Interface web de monitoring"
                  className="monitoring-screenshot"
                />
              </div>
              <h4>💻 Interface web</h4>
              <p>Analyses détaillées et historiques complets</p>
            </div>
          </div>

          <div className="monitoring-features">
            {monitoringFeatures.map((feature, index) => (
              <div key={index} className="feature-card">
                <div className="feature-icon">{feature.icon}</div>
                <div className="feature-content">
                  <h4>{feature.title}</h4>
                  <p>{feature.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="monitoring-benefits">
          <h4>🎯 Avantages du monitoring</h4>
          <div className="benefits-grid">
            <div className="benefit-item">
              <span className="benefit-icon">📈</span>
              <span>Optimisez votre consommation</span>
            </div>
            <div className="benefit-item">
              <span className="benefit-icon">⚠️</span>
              <span>Détection automatique des pannes</span>
            </div>
            <div className="benefit-item">
              <span className="benefit-icon">💰</span>
              <span>Maximisez vos économies</span>
            </div>
            <div className="benefit-item">
              <span className="benefit-icon">📊</span>
              <span>Bilans de performance</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (currentPhase === 3) {
    return (
      <div className="educational-page">
        <div className="page-header">
          <h3>💰 Votre investissement rentable</h3>
          <p>Comprendre la rentabilité de votre installation solaire</p>
        </div>
        
        <div className="investment-explanation">
          <div className="investment-step">
            <h4>📉 Réduction immédiate de votre facture</h4>
            <div className="cost-comparison">
              <div className="before-after">
                <div className="before">
                  <h5>Avant</h5>
                  <div className="bill-amount">{formData.monthlyEdfPayment}€/mois</div>
                  <p>Facture EDF complète</p>
                </div>
                <div className="arrow">→</div>
                <div className="after">
                  <h5>Après</h5>
                  <div className="bill-amount estimate">~{Math.round(formData.monthlyEdfPayment * 0.3)}€/mois</div>
                  <p>Facture EDF réduite</p>
                </div>
              </div>
            </div>
          </div>

          <div className="investment-step">
            <h4>🏦 Financement adapté à votre budget</h4>
            <div className="financing-options">
              <div className="financing-card">
                <h5>Sans aides déduites</h5>
                <div className="monthly-payment">~{Math.round(formData.monthlyEdfPayment * 1.2)}€/mois</div>
                <p>Sur 15 ans - Taux 4,96%</p>
              </div>
              <div className="financing-card recommended">
                <h5>Avec aides déduites ⭐</h5>
                <div className="monthly-payment">~{Math.round(formData.monthlyEdfPayment * 0.8)}€/mois</div>
                <p>Sur 15 ans - Taux 3,25%</p>
                <div className="recommendation">Recommandé</div>
              </div>
            </div>
          </div>

          <div className="investment-step">
            <h4>🎁 Aides financières intégrées</h4>
            <div className="aids-breakdown">
              <div className="aid-item">
                <span className="aid-icon">⚡</span>
                <span className="aid-name">Prime autoconsommation EDF</span>
                <span className="aid-amount">80€/kWc installé</span>
              </div>
              <div className="aid-item">
                <span className="aid-icon">💰</span>
                <span className="aid-name">TVA remboursée (20%)</span>
                <span className="aid-amount">Pour installation &gt; 3kW</span>
              </div>
              <div className="aid-item total">
                <span className="aid-icon">🎯</span>
                <span className="aid-name">Total aides estimées</span>
                <span className="aid-amount">~4000-6000€</span>
              </div>
            </div>
          </div>
        </div>

        <div className="roi-timeline">
          <h4>⏰ Retour sur investissement</h4>
          <div className="timeline">
            <div className="timeline-point">
              <div className="year">Année 1-6</div>
              <div className="status">Remboursement crédit</div>
            </div>
            <div className="timeline-point">
              <div className="year">Année 7-25</div>
              <div className="status benefit">Bénéfices purs</div>
            </div>
            <div className="timeline-point">
              <div className="year">25 ans</div>
              <div className="status total">Gain total: ~25 000€</div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return null;
};

// Écran de calcul avec countdown 4 minutes - Version Premium
const CalculationScreen = ({ formData, onComplete, onPrevious, selectedRegion = "france", selectedCalculationMode = "optimistic", setCurrentStep }) => {
  const [countdown, setCountdown] = useState(120); // 2 minutes = 120 secondes
  const [currentPhase, setCurrentPhase] = useState(0);
  const [calculationResults, setCalculationResults] = useState(null);
  const [isCalculating, setIsCalculating] = useState(true);
  const [currentAnimation, setCurrentAnimation] = useState(0);
  const [isDemoMode, setIsDemoMode] = useState(false);
  const successTimerRef = useRef(null);

  // Phases d'explication pendant les 2 minutes avec animations
  const phases = [
    {
      title: "🌍 Géolocalisation de votre adresse",
      description: "Nous localisons précisément votre domicile pour obtenir les données d'ensoleillement de la Commission Européenne PVGIS...",
      duration: 30,
      tips: [
        "💡 Nous utilisons les coordonnées GPS exactes",
        "🌞 Calcul de l'irradiation solaire spécifique à votre région", 
        "📊 Données météorologiques sur 15 ans"
      ]
    },
    {
      title: "🔬 Consultation PVGIS Commission Européenne",
      description: "Récupération des données officielles d'ensoleillement et calcul de la production solaire optimale...",
      duration: 30,
      tips: [
        "🏛️ Base de données officielle européenne",
        "⚡ Calcul selon l'orientation " + formData.roofOrientation,
        "📈 Production mensuelle détaillée"
      ]
    },
    {
      title: "🔧 Optimisation de votre installation",
      description: "Analyse de votre consommation (" + formData.annualConsumption + " kWh/an) et sélection du kit optimal...",
      duration: 30,
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
        "💳 Mensualité actuelle: " + (formData.monthlyEdfPayment || '0') + " €/mois",
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
    const elapsed = 120 - countdown;
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
        phone: formData.phone,
        email: formData.email,
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

      // Ensuite faire le calcul PVGIS avec la région et le mode de calcul sélectionnés
      const calculationResponse = await axios.post(`${API}/calculate/${clientId}?region=${selectedRegion}&calculation_mode=${selectedCalculationMode}`);
      
      setCalculationResults(calculationResponse.data);
      
      // Transmettre les résultats au composant parent
      onComplete(calculationResponse.data);

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

  const progressPercentage = ((120 - countdown) / 120) * 100;

  const toggleDemoMode = () => {
    setIsDemoMode(!isDemoMode);
  };

  // Timer de 20 secondes pour l'écran de succès - VA VERS L'ANIMATION
  useEffect(() => {
    if (!isCalculating && calculationResults && !successTimerRef.current) {
      successTimerRef.current = setTimeout(() => {
        setCurrentStep(6); // Aller vers l'animation au lieu des résultats
      }, 20000);
    }
    
    return () => {
      if (successTimerRef.current) {
        clearTimeout(successTimerRef.current);
        successTimerRef.current = null;
      }
    };
  }, [isCalculating, calculationResults]);

  if (!isCalculating && calculationResults) {
    return (
      <div className="calculation-screen success">
        <div className="success-animation">
          <div className="success-circle">✅</div>
          <div className="success-text">
            <h2>🎉 Calcul terminé avec succès !</h2>
            <p>Votre solution solaire personnalisée est prête</p>
            <p className="commission-text">Ce % d'économie et d'autonomie de couleur verte permet le dépôt de votre dossier aux différentes commissions pour qu'il puisse être validé</p>
          </div>
        </div>
        
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
    );
  }

  return (
    <div className="calculation-screen">
      <div className="calculation-header">
        <h2>Calcul de votre solution solaire en cours</h2>
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
          <svg width="300" height="300" className="countdown-svg">
            <circle
              cx="150"
              cy="150"
              r="130"
              stroke="#e0e0e0"
              strokeWidth="8"
              fill="none"
            />
            <circle
              cx="150"
              cy="150"
              r="130"
              stroke="url(#gradient)"
              strokeWidth="8"
              fill="none"
              strokeDasharray={`${progressPercentage * 8.17} 817`}
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
        {/* Intégration des pages éducatives avec vraies photos */}
        <EducationalPages 
          currentPhase={currentPhase} 
          countdown={countdown} 
          formData={formData}
        />
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
              <span className="info-label">📞 Téléphone :</span>
              <span className="info-value">{formData.phone}</span>
            </div>
            <div className="info-item">
              <span className="info-label">📧 Email :</span>
              <span className="info-value">{formData.email}</span>
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
  const [selectedRegion, setSelectedRegion] = useState('france');
  const [regionConfig, setRegionConfig] = useState(null);
  const [selectedCalculationMode, setSelectedCalculationMode] = useState('realistic');
  const [calculationModes, setCalculationModes] = useState(null);
  
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    address: '',
    phone: '',
    email: '',
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

  // Charger la configuration de la région
  useEffect(() => {
    const fetchRegionConfig = async () => {
      try {
        console.log('Fetching region config for:', selectedRegion);
        const response = await axios.get(`${API}/regions/${selectedRegion}`);
        console.log('Region config loaded:', response.data.config);
        setRegionConfig(response.data.config);
      } catch (error) {
        console.error('Erreur lors du chargement de la configuration de région:', error);
      }
    };
    
    fetchRegionConfig();
  }, [selectedRegion]);

  // Charger les modes de calcul disponibles
  useEffect(() => {
    const fetchCalculationModes = async () => {
      try {
        console.log('Fetching calculation modes');
        const response = await axios.get(`${API}/calculation-modes`);
        console.log('Calculation modes loaded:', response.data.modes);
        setCalculationModes(response.data.modes);
      } catch (error) {
        console.error('Erreur lors du chargement des modes de calcul:', error);
      }
    };
    
    fetchCalculationModes();
  }, []);

  const handleRegionChange = (region) => {
    setSelectedRegion(region);
    // Réinitialiser les résultats de calcul si on change de région
    setCalculationResults(null);
  };

  const handleCalculationModeChange = (mode) => {
    setSelectedCalculationMode(mode);
    // Réinitialiser les résultats de calcul si on change de mode
    setCalculationResults(null);
  };

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
    const steps = ['start', 'personal', 'technical', 'heating', 'consumption', 'calculation', 'results'];
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
    // Ne pas rediriger automatiquement - laisser le timer de 20 secondes du CalculationScreen faire son travail
    // pour afficher l'écran de succès pendant 20 secondes puis aller vers l'animation
  };

  const handleNewCalculation = () => {
    setCurrentStep('start');
    setCalculationResults(null);
    setFormData({
      firstName: '',
      lastName: '',
      address: '',
      phone: '',
      email: '',
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
        {/* Particules flottantes animées */}
        <div className="particles">
          <div className="particle"></div>
          <div className="particle"></div>
          <div className="particle"></div>
          <div className="particle"></div>
          <div className="particle"></div>
          <div className="particle"></div>
          <div className="particle"></div>
          <div className="particle"></div>
          <div className="particle"></div>
        </div>
        
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
        {/* Particules flottantes animées */}
        <div className="particles">
          <div className="particle"></div>
          <div className="particle"></div>
          <div className="particle"></div>
          <div className="particle"></div>
          <div className="particle"></div>
          <div className="particle"></div>
          <div className="particle"></div>
          <div className="particle"></div>
          <div className="particle"></div>
        </div>
        
        <RegionSelector 
          selectedRegion={selectedRegion} 
          onRegionChange={handleRegionChange}
          regionConfig={regionConfig}
        />
        <CalculationModeSelector 
          selectedMode={selectedCalculationMode} 
          onModeChange={handleCalculationModeChange}
          calculationModes={calculationModes}
        />
        <StartScreen 
          onStart={handleStart} 
          regionConfig={regionConfig} 
          key={selectedRegion}
        />
      </div>
    );
  }

  if (currentStep === 'personal') {
    return (
      <div className="App">
        <RegionSelector 
          selectedRegion={selectedRegion} 
          onRegionChange={handleRegionChange}
          regionConfig={regionConfig}
        />
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
        <RegionSelector 
          selectedRegion={selectedRegion} 
          onRegionChange={handleRegionChange}
          regionConfig={regionConfig}
        />
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
        <RegionSelector 
          selectedRegion={selectedRegion} 
          onRegionChange={handleRegionChange}
          regionConfig={regionConfig}
        />
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
        <RegionSelector 
          selectedRegion={selectedRegion} 
          onRegionChange={handleRegionChange}
          regionConfig={regionConfig}
        />
        <ConsumptionForm 
          formData={formData} 
          setFormData={setFormData} 
          onNext={handleNext} 
          onPrevious={handlePrevious} 
          selectedRegion={selectedRegion}
        />
      </div>
    );
  }

  if (currentStep === 'calculation') {
    return (
      <div className="App">
        <RegionSelector 
          selectedRegion={selectedRegion} 
          onRegionChange={handleRegionChange}
          regionConfig={regionConfig}
        />
        <CalculationScreen 
          formData={formData} 
          onComplete={handleCalculationComplete}
          onPrevious={handlePrevious}
          selectedRegion={selectedRegion}
          selectedCalculationMode={selectedCalculationMode}
          setCurrentStep={setCurrentStep}
        />
      </div>
    );
  }

  if (currentStep === 'results') {
    return (
      <div className="App">
        <RegionSelector 
          selectedRegion={selectedRegion} 
          onRegionChange={handleRegionChange}
          regionConfig={regionConfig}
        />
        <ResultsScreen 
          results={calculationResults}
          onPrevious={handlePrevious}
          selectedRegion={selectedRegion}
          setCurrentStep={setCurrentStep}
        />
      </div>
    );
  }
  
  // Résultats (Étape 5) - PAGE ORIGINALE RESTAURÉE
  if (currentStep === 5) {
    return (
      <div className="App">
        <ResultsScreen 
          results={calculationResults}
          onPrevious={handlePrevious}
          selectedRegion={selectedRegion}
          setCurrentStep={setCurrentStep}
        />
      </div>
    );
  }

  // Synthèse financière et technique (Étape 7)
  if (currentStep === 7) {
    return (
      <div className="App">
        <div style={{ padding: '40px', maxWidth: '1200px', margin: '0 auto' }}>
          <h1 style={{ textAlign: 'center', color: '#2ecc71', marginBottom: '30px' }}>
            📊 Synthèse Financière et Technique
          </h1>
          
          {calculationResults && (
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '30px', marginBottom: '30px' }}>
              
              {/* Synthèse Technique */}
              <div style={{ background: '#f8f9fa', padding: '25px', borderRadius: '12px', border: '1px solid #e9ecef' }}>
                <h3 style={{ color: '#2c3e50', marginBottom: '20px' }}>🔧 Synthèse Technique</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span>Puissance installée:</span>
                    <strong>{calculationResults.kit_power} kW</strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span>Nombre de panneaux:</span>
                    <strong>{calculationResults.recommended_kit?.panels || (formData.useManualKit ? formData.manualKit?.panels : 12)} panneaux</strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span>Surface totale:</span>
                    <strong>{((calculationResults.recommended_kit?.panels || (formData.useManualKit ? formData.manualKit?.panels : 12)) * 2.11).toFixed(1)} m²</strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span>Production annuelle:</span>
                    <strong>{Math.round(calculationResults.annual_production)} kWh/an</strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span>Autonomie énergétique:</span>
                    <strong style={{ color: '#2ecc71' }}>{Math.round(calculationResults.autonomy_percentage)}%</strong>
                  </div>
                </div>
              </div>

              {/* Synthèse Financière */}
              <div style={{ background: '#f8f9fa', padding: '25px', borderRadius: '12px', border: '1px solid #e9ecef' }}>
                <h3 style={{ color: '#2c3e50', marginBottom: '20px' }}>💰 Synthèse Financière</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span>Prix installation:</span>
                    <strong>{calculationResults.total_price?.toLocaleString()} €</strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span>Économies annuelles:</span>
                    <strong style={{ color: '#2ecc71' }}>+{Math.round(calculationResults.estimated_savings)} €/an</strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span>Retour sur investissement:</span>
                    <strong>{calculationResults.payback_years} ans</strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span>Gain sur 20 ans:</span>
                    <strong style={{ color: '#27ae60' }}>+{Math.round(calculationResults.estimated_savings * 20).toLocaleString()} €</strong>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Boutons de navigation */}
          <div style={{ display: 'flex', justifyContent: 'center', gap: '20px', marginTop: '40px' }}>
            <button 
              onClick={() => setCurrentStep('results')}
              style={{ 
                backgroundColor: '#e74c3c', 
                color: 'white', 
                border: 'none', 
                padding: '15px 30px', 
                borderRadius: '8px', 
                fontSize: '16px', 
                fontWeight: 'bold',
                cursor: 'pointer'
              }}
            >
              ← Retour aux Résultats
            </button>
            <button 
              onClick={() => setCurrentStep(1)}
              style={{ 
                backgroundColor: '#2ecc71', 
                color: 'white', 
                border: 'none', 
                padding: '15px 30px', 
                borderRadius: '8px', 
                fontSize: '16px', 
                fontWeight: 'bold',
                cursor: 'pointer'
              }}
            >
              🏠 Nouvelle Étude
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Animation 3D (Étape 6)
  if (currentStep === 6) {
    // CORRECTION : Prendre le nombre de panneaux choisi par l'utilisateur
    let panelCount = 12; // Par défaut
    
    if (formData.useManualKit && formData.manualKit) {
      // Si l'utilisateur a choisi manuellement
      panelCount = formData.manualKit.panels;
      console.log(`🔧 Panneau manuel choisi: ${panelCount}`);
    } else if (calculationResults?.recommended_kit?.panels) {
      // Si c'est automatique
      panelCount = calculationResults.recommended_kit.panels;
      console.log(`🤖 Panneau automatique: ${panelCount}`);
    }
    
    return (
      <div className="App">
        <SolarAnimationCSS 
          panelCount={panelCount}
          onBack={() => setCurrentStep(5)} // Retour aux résultats
          onNext={() => setCurrentStep(5)} // Retour vers les VRAIS résultats (votre page originale)
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