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

// Points 6-11 ajoutés : Composant pour le tableau de financement avec aides déduites
const FinancingTableComponent = ({ results, showFinancing, setShowFinancing }) => {
  // Données du tableau de financement (Point 6)
  const financingOptions = [
    { duration: 6, monthly: 481, savings: 300 },
    { duration: 7, monthly: 422, savings: 241 },
    { duration: 8, monthly: 378, savings: 197 },
    { duration: 9, monthly: 344, savings: 162 },
    { duration: 10, monthly: 317, savings: 135 },
    { duration: 11, monthly: 294, savings: 113 },
    { duration: 12, monthly: 276, savings: 95 },
    { duration: 13, monthly: 260, savings: 79 },
    { duration: 14, monthly: 247, savings: 66 },
    { duration: 15, monthly: 236, savings: 54 },
  ];

  return (
    <div className="financing-analysis">
      <h3>💰 Point 6 - Tableau financement avec aides</h3>
      
      {/* Toggle button */}
      <div className="financing-toggle">
        <button
          onClick={() => setShowFinancing(!showFinancing)}
          className="btn-financing-toggle"
        >
          📊 {showFinancing ? 'Masquer' : 'Afficher'} le financement
        </button>
      </div>

      {/* Financing table */}
      {showFinancing && (
        <div className="financing-table-container">
          <h4>📋 Toutes les options de financement disponibles</h4>
          <div className="financing-table">
            <div className="table-header">
              <span>Durée</span>
              <span>Mensualité</span>
              <span>Différence vs économies</span>
            </div>
            {financingOptions.map((option, index) => (
              <div key={index} className="table-row">
                <span>{option.duration} ans</span>
                <span>{option.monthly} €</span>
                <span className="savings-diff">+{option.savings} €/mois</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recommended financing options */}
      <div className="financing-recommendations">
        <h4>🏆 Options de financement recommandées</h4>
        
        {/* Standard financing */}
        <div className="financing-option standard">
          <div className="option-header">
            <h5>⭐ Financement standard sur 15 ans</h5>
            <span className="option-badge">Sans aides déduites</span>
          </div>
          <div className="option-details">
            <div className="detail-row">
              <span>Investissement total:</span>
              <span className="amount">29 900 € TTC</span>
            </div>
            <div className="detail-row">
              <span>Mensualité crédit:</span>
              <span className="amount">236 €/mois</span>
            </div>
            <div className="detail-row">
              <span>Économie EDF:</span>
              <span className="amount positive">181 €/mois</span>
            </div>
            <div className="detail-row">
              <span>Reste à charge:</span>
              <span className="amount warning">+54 €/mois</span>
            </div>
          </div>
        </div>

        {/* Optimized financing with subsidies */}
        <div className="financing-option optimized">
          <div className="option-header">
            <h5>🔥 Financement optimisé sur 15 ans</h5>
            <span className="option-badge green">Avec aides déduites</span>
          </div>
          <div className="option-details">
            <div className="detail-row">
              <span>Investissement après aides:</span>
              <span className="amount">23 200 € TTC</span>
            </div>
            <div className="detail-row">
              <span>Mensualité crédit réduite (+35€ intérêts):</span>
              <span className="amount">164 €/mois</span>
            </div>
            <div className="detail-row">
              <span>Économie EDF:</span>
              <span className="amount positive">181 €/mois</span>
            </div>
            <div className="detail-row">
              <span>Reste à charge optimisé:</span>
              <span className="amount positive">-17 €/mois</span>
            </div>
          </div>

          {/* Aides détaillées */}
          <div className="aids-detail">
            <h6>✅ Aides incluses dans le calcul optimisé:</h6>
            <div className="aid-item">✓ 6 premiers mois GRATUITS (0€ pendant l'installation)</div>
            <div className="aid-item">✓ Aides récupérées: 6700 € (Prime + TVA)</div>
            <div className="aid-item">✓ Taux fixe 4,96% TAEG sur toute la durée</div>
            <div className="aid-item">✓ Économie mensuelle supérieure au crédit !</div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Point 8 - Composant Monitoring 2025
const Monitoring2025Component = () => {
  return (
    <div className="monitoring-2025">
      <h3>📈 Point 8 - Monitoring 2025</h3>
      
      {/* Interface MyEnlighten/Envoy (copie exacte) */}
      <div className="monitoring-interface">
        <div className="monitoring-header">
          <div className="nav-tabs">
            <span className="tab active">Overview</span>
            <span className="tab">Production</span>
            <span className="tab">Consommation</span>
            <span className="tab">Reports</span>
          </div>
          <div className="date-weather">
            <span className="date">Jeudi 8 Avril 2021</span>
            <span className="weather">🌤️ 70°F Partly Cloudy</span>
          </div>
        </div>

        <div className="monitoring-content">
          <div className="metrics-section">
            <div className="metric-item">
              <div className="metric-icon solar">📊</div>
              <div className="metric-data">
                <div className="metric-value">24.22</div>
                <div className="metric-label">kilowatt-hours produced</div>
                <div className="metric-sub">Approximately 18.14 kWh exported to grid</div>
              </div>
            </div>

            <div className="metric-item">
              <div className="metric-icon consumption">🔴</div>
              <div className="metric-data">
                <div className="metric-value">16.66</div>
                <div className="metric-label">kilowatt-hours consumed</div>
                <div className="metric-sub">Approximately 10.57 kWh imported from grid</div>
              </div>
            </div>

            <div className="metric-item">
              <div className="metric-icon export">➕</div>
              <div className="metric-data">
                <div className="metric-value">7.50</div>
                <div className="metric-label">kilowatt-hours net energy exported</div>
              </div>
            </div>
          </div>

          <div className="panels-section">
            <h4>array 1</h4>
            <div className="panels-grid">
              {Array.from({ length: 12 }, (_, i) => (
                <div key={i} className="panel-item">
                  <div className="panel-value">{(1.74 + Math.random() * 0.1).toFixed(2)}</div>
                  <div className="panel-unit">kWh</div>
                </div>
              ))}
            </div>
            
            <div className="current-stats">
              <div className="stat-large">0 Wh</div>
              <div className="stat-small">27.3 kWh</div>
            </div>
          </div>
        </div>

        <div className="monitoring-footer">
          <span className="footer-brand">MyEnlighten</span>
          <span className="footer-separator">|</span>
          <span className="footer-brand">Envoy</span>
        </div>
      </div>
    </div>
  );
};

// Point 9 - Composant App Mobile
const MobileAppComponent = () => {
  return (
    <div className="mobile-app-section">
      <h3>📱 Point 9 - App Mobile</h3>
      
      <div className="mobile-app-container">
        {/* Smartphone mockup */}
        <div className="smartphone-mockup">
          <div className="phone-screen">
            <div className="phone-status-bar">
              <span>📶 ⚡ 🔋100%</span>
              <span>2023-05-30 17:18:25</span>
            </div>
            
            <div className="app-header">
              <div className="app-title">Capacité</div>
              <div className="app-subtitle">6 kW</div>
            </div>

            <div className="weather-section">
              <div className="sun-icon">☀️</div>
              <div className="clouds">☁️ ☁️ ☁️</div>
            </div>

            <div className="production-display">
              <div className="production-circle">
                <div className="production-value">3.11 W</div>
                <div className="production-label">Production actuelle</div>
              </div>
            </div>

            <div className="house-visual">
              <div className="house-icon">🏠</div>
              <div className="solar-panels">📋</div>
            </div>

            <div className="app-stats">
              <div className="stat-row">
                <span>Aujourd'hui</span>
                <span>32.94 kWh</span>
              </div>
              <div className="stat-row">
                <span>Ce mois-ci</span>
                <span>7.86 kWh</span>
              </div>
              <div className="stat-row">
                <span>Total</span>
                <span>7.86 kWh</span>
              </div>
            </div>

            <div className="app-navigation">
              <span>🔄</span>
              <span>📊</span>
              <span>🏠</span>
              <span>⚙️</span>
            </div>
          </div>
        </div>

        {/* App description */}
        <div className="app-description">
          <h4 className="app-title-green">SUIVEZ VOTRE PRODUCTION EN TEMPS RÉEL</h4>
          
          <h5>Votre production et consommation solaire en direct via <span className="highlight-blue">notre appli</span></h5>
          
          <div className="app-features">
            <p>Nous offrons à nos clients une expérience transparente et pratique grâce à notre application dédiée, qui leur permet de contrôler la production de leurs panneaux solaires directement depuis leur smartphone.</p>
            
            <p>Cette application intuitive fournit des informations en temps réel sur la production d'énergie, ainsi que des données détaillées sur toute la durée depuis l'installation.</p>
            
            <p>Vous pouvez suivre de près les performances de vos panneaux solaires. Vous avez le contrôle total de votre système solaire à portée de main, offrant une gestion pratique et efficace de votre production d'énergie solaire.</p>
          </div>

          <div className="app-benefits">
            <h6>✨ Fonctionnalités de l'application :</h6>
            <div className="benefit-list">
              <div className="benefit-item">✓ Suivi production en temps réel (kWh produits)</div>
              <div className="benefit-item">✓ Historique détaillé par jour, mois, année</div>
              <div className="benefit-item">✓ Alertes en cas de dysfonctionnement</div>
              <div className="benefit-item">✓ Calcul des économies réalisées en €</div>
              <div className="benefit-item">✓ Interface intuitive et moderne</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Point 10 - Rectangle vert final (Graphique évolution des gains)
const GreenRectangleComponent = () => {
  const [hoveredYear, setHoveredYear] = useState(8);

  // Données pour le graphique d'évolution des gains sur 20 ans
  const gainsData = [
    { year: 1, totalGain: 2177, surplus: 36, savings: 2141 },
    { year: 2, totalGain: 2320, surplus: 36, savings: 2284 },
    { year: 3, totalGain: 2468, surplus: 36, savings: 2432 },
    { year: 4, totalGain: 2620, surplus: 36, savings: 2584 },
    { year: 5, totalGain: 2777, surplus: 36, savings: 2741 },
    { year: 6, totalGain: 2939, surplus: 36, savings: 2903 },
    { year: 7, totalGain: 3106, surplus: 36, savings: 3070 },
    { year: 8, totalGain: 3287, surplus: 36, savings: 3252 },
    { year: 9, totalGain: 3463, surplus: 36, savings: 3427 },
    { year: 10, totalGain: 3644, surplus: 36, savings: 3608 },
    { year: 11, totalGain: 3830, surplus: 36, savings: 3794 },
    { year: 12, totalGain: 4021, surplus: 36, savings: 3985 },
    { year: 13, totalGain: 4217, surplus: 36, savings: 4181 },
    { year: 14, totalGain: 4418, surplus: 36, savings: 4382 },
    { year: 15, totalGain: 4624, surplus: 36, savings: 4588 },
    { year: 16, totalGain: 4835, surplus: 36, savings: 4799 },
    { year: 17, totalGain: 5051, surplus: 36, savings: 5015 },
    { year: 18, totalGain: 5272, surplus: 36, savings: 5236 },
    { year: 19, totalGain: 5498, surplus: 36, savings: 5462 },
    { year: 20, totalGain: 5729, surplus: 36, savings: 5693 }
  ];

  const currentData = gainsData.find(d => d.year === hoveredYear) || gainsData[7];

  return (
    <div className="green-rectangle">
      <h3>📊 Point 10 - Rectangle vert final (Évolution des Gains)</h3>
      
      <div className="gains-evolution-chart">
        <h4>Évolution des Gains sur 20 ans</h4>
        
        <div className="chart-container">
          <div className="chart-area">
            {gainsData.map((point, index) => (
              <div
                key={index}
                className="chart-point"
                style={{
                  left: `${(index / (gainsData.length - 1)) * 90 + 5}%`,
                  bottom: `${(point.totalGain / 6000) * 80 + 10}%`
                }}
                onMouseEnter={() => setHoveredYear(point.year)}
              >
                <div className="point-dot"></div>
              </div>
            ))}
            
            <div className="chart-line"></div>
          </div>
          
          {/* Tooltip interactif */}
          <div className="chart-tooltip">
            <h5>Année {hoveredYear}</h5>
            <div className="tooltip-data">
              <div className="data-row gain">Gain total : {currentData.totalGain} €</div>
              <div className="data-row surplus">Revenus surplus : {currentData.surplus} €</div>
              <div className="data-row savings">Économies : {currentData.savings} €</div>
            </div>
          </div>
        </div>
        
        <p className="chart-note">💡 Passez votre souris sur les points pour voir les détails année par année</p>
      </div>
    </div>
  );
};

// Photos d'installation pour explication commerciale
const InstallationPhotosComponent = () => {
  return (
    <div className="installation-photos">
      <h3>🔧 Photos d'installation pour explication commerciale</h3>
      
      <div className="photos-grid">
        <div className="photo-item">
          <div className="photo-placeholder">📸</div>
          <h4>Installation sur toiture méditerranéenne</h4>
          <p>Panneaux solaires parfaitement intégrés sur tuiles traditionnelles</p>
        </div>
        
        <div className="photo-item">
          <div className="photo-placeholder">📸</div>
          <h4>Configuration optimale sur toiture</h4>
          <p>Disposition stratégique pour maximiser la production</p>
        </div>
        
        <div className="photo-item">
          <div className="photo-placeholder">📸</div>
          <h4>Installation en cours par nos techniciens</h4>
          <p>Équipe certifiée RGE à l'œuvre</p>
        </div>
        
        <div className="photo-item">
          <div className="photo-placeholder">📸</div>
          <h4>Panneaux haute performance</h4>
          <p>Technologie de pointe pour rendement optimal</p>
        </div>
        
        <div className="photo-item">
          <div className="photo-placeholder">📸</div>
          <h4>Installation finale professionnelle</h4>
          <p>Résultat final soigné et esthétique</p>
        </div>
      </div>

      <div className="installation-explanation">
        <h4>🔧 Comment se fixent les panneaux sur votre toiture</h4>
        <div className="explanation-steps">
          <div className="step">1. Étude préalable de la charpente</div>
          <div className="step">2. Fixation sécurisée avec crochets adaptés</div>
          <div className="step">3. Installation des rails de montage</div>
          <div className="step">4. Étanchéité garantie</div>
          <div className="step">5. Pose des panneaux optimisée</div>
        </div>
      </div>

      <div className="micro-inverter">
        <h4>⚡ Micro onduleur haute performance</h4>
        <div className="inverter-visual">📱</div>
        <p>Chaque panneau est équipé d'un micro-onduleur pour optimiser la production individuelle et permettre un monitoring précis.</p>
      </div>
    </div>
  );
};

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
            src="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAArAFoDASIAAhEBAxEB/8QAGwABAAIDAQEAAAAAAAAAAAAAAAQFAgMGBwH/xAA2EAABAwMCAwYDBwQDAAAAAAAAAQIDBAURBhIhMQcTQVFhcSKBkRQyocHR4fAjQrHxFRYz/8QAGQEBAAMBAQAAAAAAAAAAAAAAAAECAwQF/8QAIBEBAAICAgEFAAAAAAAAAAAAAAECAxESMQQhQVGBsf/aAAwDAQACEQMRAD8A9xAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAPz/qS+V+rNRV9/rWxU9HNMrooYWvR0bWfdReLqd7HJhrWOobYrxWZbwAAOVurytGmoqKqlZd7lhqhKitjZAz4m/eRy5xgkREzLN1jdqvJv8P0Xf8AXFzpCLdNHBQwRuSNrWIuRMKnL9zrSr+xfSSy26a6VbOUzURifcXnnz7V/Jfe83I6OO9fmKsz96SAAPUe8AAAAAAAAAAfD/xLWmlJ6YrZbfqK1VNPUtajpKOqZhZGZwrsZwvI6Cj7X9BzNzPU1dA7+yWF3/l0cfR8WwcVMU1q2iJ8r6AAAAHGab7PbRpmpkqra6oulXKmH1dy9nO9GorW+aaJOxLZLktv5k1jJPJlb7l2cAOO9K3vbt6j4+fUJPt6xMR8L6s6AAAHqPegAAAABkEzMFczC8T6+J+5ycF4H6NG8a/qUOmu12fhWBz3u5xNd/E4t1H2T6ksrXOdSQXKNvc3A9qr8uB+l/3VJtl3+zkdPjzSO5eGNv6OZfK3Hpu1y2SzVFXUqxU7xOCd5wXj3eY2YcN7vMT7WrSbTtj2jVei9MYWv1QrpWwTK1a+kfudjmu7Hj69Oqr2l6EWBN2tL65Ut3Z+z3Vzy7Pwu6VUfHOhqCCppNKsllZtq7Rci1Ntp5N5XZyrkROv7GPFa/LvxN/8AFj7Y6m4z6v7KN1YjpJq3T1xV08TW+7vqcPnT4fhc7LcbRxYHDGy+i38Ml9GUTt3D4jJit38Ml9GUTt3D4jJit38JJABo2AAHqHfgAAAAAJlLp7UtbQxVVLY7hNDIm5j47fKqKn1GVKTadQrNoncqybTtyZC6V9JNHHI3u3vfCrWuTwVXYRbz+oT5U67r1P15OxeFqhVzDOhOOi73VNhL86/xZBvtMaUPSFt3Ry7dv2YlOKIYJKOGnpW1MzGw0zX/ANWjS5URf/5EXI4aTGllpppKcZStQnv8XuTN5OiE77y3nJcJdOao9w2p19aWdOK7FXz8F9vvKwAlqxfG9y/+TnLZlm/OqODzjfZnfmj47W+UgADp3OONx+AAAAAP/9k=" 
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