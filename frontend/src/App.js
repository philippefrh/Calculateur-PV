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

// Écran de démarrage amélioré avec vrais logos
const StartScreen = ({ onStart, clientMode, setClientMode }) => {
  
  const handleClick = () => {
    console.log("Button clicked!");
    console.log("Client mode:", clientMode);
    onStart();
  };
  
  const handleModeChange = (mode) => {
    setClientMode(mode);
    console.log("Mode changed to:", mode);
  };
  
  return (
    <div className="start-screen">
      {/* Toggle Mode Selection */}
      <div className="mode-selector">
        <div className="mode-toggle-container">
          <div className="mode-toggle">
            <button 
              className={`mode-toggle-btn ${clientMode === 'particuliers' ? 'active' : ''}`}
              onClick={() => handleModeChange('particuliers')}
            >
              👥 Particuliers
            </button>
            <button 
              className={`mode-toggle-btn ${clientMode === 'professionnels' ? 'active' : ''}`}
              onClick={() => handleModeChange('professionnels')}
            >
              🏢 Professionnels
            </button>
          </div>
          <div className="mode-description">
            {clientMode === 'particuliers' ? (
              <p>🏠 Calculateur spécialisé pour les particuliers et résidences privées</p>
            ) : (
              <p>🏢 Calculateur spécialisé pour les entreprises et professionnels</p>
            )}
          </div>
        </div>
      </div>

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
        <p className="company-subtitle">
          FRH ENVIRONNEMENT - Énergie Solaire {clientMode === 'particuliers' ? 'Résidentiel' : 'Professionnel'}
        </p>
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
        {clientMode === 'particuliers' ? 
          '🌞 Commencer l\'Étude Solaire Gratuite' : 
          '🏢 Commencer l\'Étude Solaire Professionnelle'
        }
      </button>
      
      <div className="benefits">
        <div className="benefit-item">
          <span className="benefit-icon">✓</span>
          <span>
            {clientMode === 'particuliers' ? 
              'Réalisez jusqu\'à 70% d\'économies sur vos factures d\'électricité' :
              'Réduisez vos coûts énergétiques et bénéficiez d\'avantages fiscaux'
            }
          </span>
        </div>
        <div className="benefit-item">
          <span className="benefit-icon">✓</span>
          <span>Un accompagnement de A à Z pour votre projet solaire</span>
        </div>
        <div className="benefit-item">
          <span className="benefit-icon">✓</span>
          <span>
            {clientMode === 'particuliers' ? 
              'Panneaux garantis 25 ans et garanties de production' :
              'Solutions professionnelles avec garanties étendues'
            }
          </span>
        </div>
        <div className="benefit-item">
          <span className="benefit-icon">✓</span>
          <span>Installation fiable et performante par nos installateurs certifiés RGE</span>
        </div>
        <div className="benefit-item">
          <span className="benefit-icon">✓</span>
          <span>
            {clientMode === 'particuliers' ? 
              'Profitez des dispositifs d\'aides et de subventions' :
              'Amortissement accéléré et avantages fiscaux pour entreprises'
            }
          </span>
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
const ConsumptionForm = ({ formData, setFormData, onNext, onPrevious }) => {
  const [errors, setErrors] = useState({});
  const [showKitSelection, setShowKitSelection] = useState(false);
  const [availableKits, setAvailableKits] = useState([]);
  const [selectedKit, setSelectedKit] = useState(null);
  const [loadingKits, setLoadingKits] = useState(false);

  // Récupérer les kits solaires disponibles
  const fetchAvailableKits = async () => {
    if (availableKits.length > 0) return; // Déjà chargés
    
    setLoadingKits(true);
    try {
      // Utiliser le nouvel endpoint qui prend en compte le mode client
      const clientMode = formData.clientMode || 'particuliers';
      const response = await fetch(`${API}/solar-kits/${clientMode}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const kits = await response.json();
      
      // Transformer les données pour inclure les informations calculées
      const kitsWithDetails = Object.entries(kits).map(([power, info]) => {
        const kitPower = parseInt(power);
        
        if (clientMode === 'professionnels') {
          // Pour les professionnels, utiliser les données du tableau
          return {
            power: kitPower,
            panels: info.panels,
            surface: info.surface,
            prime: info.prime,
            priceTTC: info.tarif_base_ht, // Prix de base HT
            priceHT: info.tarif_base_ht,
            priceRemise: info.tarif_remise_ht,
            priceRemiseMax: info.tarif_remise_max_ht,
            commissionNormale: info.commission_normale,
            commissionRemiseMax: info.commission_remise_max,
            priceWithAids: info.tarif_base_ht - info.prime, // Prix base - prime
            commission: info.commission_normale // Commission par défaut
          };
        } else {
          // Pour les particuliers, calcul traditionnel
          const priceHT = info.price / 1.2; // Prix HT (TTC / 1.2)
          const commission = priceHT * 0.15; // Commission 15%
          const surfaceTotal = info.panels * 2.1; // Surface par panneau: 2.1m²
          
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
        }
      });
      
      setAvailableKits(kitsWithDetails.sort((a, b) => a.power - b.power));
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
                          
                          {formData.clientMode === 'professionnels' ? (
                            <>
                              <div className="kit-detail-row">
                                <span>Prix de base HT:</span>
                                <span>{kit.priceHT.toLocaleString()}€</span>
                              </div>
                              <div className="kit-detail-row">
                                <span>Prix remisé HT:</span>
                                <span>{kit.priceRemise.toLocaleString()}€</span>
                              </div>
                              <div className="kit-detail-row">
                                <span>Prix remisé MAX HT:</span>
                                <span className="price-remise-max">{kit.priceRemiseMax.toLocaleString()}€</span>
                              </div>
                              <div className="kit-detail-row">
                                <span>Prime subvention:</span>
                                <span className="prime-amount">{kit.prime.toLocaleString()}€</span>
                              </div>
                              <div className="kit-detail-row">
                                <span>Commission normale:</span>
                                <span className="commission">{kit.commissionNormale.toLocaleString()}€</span>
                              </div>
                              <div className="kit-detail-row">
                                <span>Commission remise MAX:</span>
                                <span className="commission-max">{kit.commissionRemiseMax.toLocaleString()}€</span>
                              </div>
                            </>
                          ) : (
                            <>
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
                            </>
                          )}
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
          {/* Affichage conditionnel selon le mode client */}
          {results.client_mode === 'professionnels' ? (
            <div className="professional-results">
              {/* Section MEILLEUR KITS OPTIMISE */}
              {results.optimal_kit && (
                <div className="optimal-kit-section">
                  <h3>🎯 MEILLEUR KITS OPTIMISE</h3>
                  <div className="optimal-kit-card">
                    <div className="optimal-kit-header">
                      <h4>Kit {results.optimal_kit.kit_power}kW - Leasing {results.optimal_kit.duration_months} mois</h4>
                      <span className="optimal-badge">RECOMMANDÉ</span>
                    </div>
                    <div className="optimal-kit-details">
                      <div className="optimal-detail-row">
                        <span>Mensualité leasing :</span>
                        <span className="leasing-payment">{results.optimal_kit.monthly_payment?.toFixed(2)}€/mois</span>
                      </div>
                      <div className="optimal-detail-row">
                        <span>Économies mensuelles :</span>
                        <span className="monthly-savings">{results.optimal_kit.monthly_savings?.toFixed(2)}€/mois</span>
                      </div>
                      <div className="optimal-detail-row benefit">
                        <span>Bénéfice mensuel :</span>
                        <span className="monthly-benefit">+{results.optimal_kit.monthly_benefit?.toFixed(2)}€/mois</span>
                      </div>
                      <div className="optimal-detail-row">
                        <span>Niveau de prix :</span>
                        <span className="price-level">{results.optimal_kit.price_level || 'base'}</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}
              
              {/* Section Options de Leasing */}
              {results.leasing_options && results.leasing_options.length > 0 && (
                <div className="leasing-options-section">
                  <h3>💰 Options de Leasing Disponibles</h3>
                  <div className="leasing-options-grid">
                    {results.leasing_options.map((option, index) => (
                      <div key={index} className="leasing-option-card">
                        <div className="leasing-option-header">
                          <h4>{option.duration_months} mois</h4>
                          <span className="leasing-rate">{option.rate}%</span>
                        </div>
                        <div className="leasing-option-details">
                          <div className="leasing-detail-row">
                            <span>Mensualité :</span>
                            <span className="monthly-payment">{option.monthly_payment?.toFixed(2)}€</span>
                          </div>
                          <div className="leasing-detail-row">
                            <span>Total payé :</span>
                            <span className="total-payment">{option.total_payment?.toFixed(2)}€</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Section Analyse Financière Professionnelle */}
              <div className="professional-financial-analysis">
                <h3>📊 Analyse Financière Professionnelle</h3>
                <div className="financial-cards">
                  <div className="financial-card">
                    <h4>🏭 Avantages Professionnels</h4>
                    <div className="financial-details">
                      <div className="financial-row">
                        <span>Prime subvention :</span>
                        <span className="prime-amount">{results.autoconsumption_aid?.toFixed(2)}€</span>
                      </div>
                      <div className="financial-row">
                        <span>TVA récupérée :</span>
                        <span className="tva-benefit">Oui (par l'entreprise)</span>
                      </div>
                      <div className="financial-row">
                        <span>Amortissement accéléré :</span>
                        <span className="amortissement">30% première année</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="financial-card">
                    <h4>⚡ Consommation Professionnelle</h4>
                    <div className="financial-details">
                      <div className="financial-row">
                        <span>Autoconsommation :</span>
                        <span className="autoconsumption">{results.autoconsumption_kwh?.toFixed(0)} kWh (80%)</span>
                      </div>
                      <div className="financial-row">
                        <span>Surplus revendu :</span>
                        <span className="surplus">{results.surplus_kwh?.toFixed(0)} kWh (20%)</span>
                      </div>
                      <div className="financial-row">
                        <span>Tarif EDF pro :</span>
                        <span className="edf-rate">0.26€/kWh</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            // Affichage traditionnel pour les particuliers
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
              </div>
            </div>
          )}
        </div>
      )}

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
                    <h5>💰 Financement optimisé sur {results.financing_with_aids?.duration_years} ans</h5>
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
                    <p>✅ Aides récupérées: {Math.round(results.total_aids)} € (Prime + TVA)</p>
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
      </div>

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
      </div>
    </div>
  );
};

export default App;
