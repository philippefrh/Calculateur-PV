import React, { useState, useEffect } from 'react';
import './SolarAnimationCSS.css';

const SolarAnimationCSS = ({ panelCount = 12, onBack, onNext }) => {
  const [animationStage, setAnimationStage] = useState('ready');
  const [currentPanel, setCurrentPanel] = useState(0);
  const [kwhProduction, setKwhProduction] = useState(0);
  const [kwhConsumption, setKwhConsumption] = useState(0);
  const [producingPanels, setProducingPanels] = useState([]);
  const [moneyBills, setMoneyBills] = useState(0);

  useEffect(() => {
    // Démarrer l'animation automatiquement après 2 secondes
    const timer = setTimeout(() => {
      startAnimation();
    }, 2000);

    return () => clearTimeout(timer);
  }, []);

  const startAnimation = () => {
    setAnimationStage('panels');
    setKwhProduction(0);
    setKwhConsumption(0);
    setProducingPanels([]);
    setMoneyBills(0);
    
    // Animation des panneaux un par un
    for (let i = 0; i < panelCount; i++) {
      setTimeout(() => {
        setCurrentPanel(i + 1);
        
        // Si c'est le dernier panneau, démarrer la production après l'app
        if (i === panelCount - 1) {
          setTimeout(() => {
            setAnimationStage('production');
            startProduction();
          }, 1000);
        }
      }, i * 300);
    }
  };

  const startProduction = () => {
    // Activer tous les panneaux en production
    const allPanels = Array.from({ length: panelCount }, (_, i) => i + 1);
    setProducingPanels(allPanels);
    
    // Démarrer le comptage des kWh
    const productionTimer = setInterval(() => {
      setKwhProduction(prev => {
        const increment = (panelCount * 0.35); // Production rapide
        return prev + increment;
      });
      
      setKwhConsumption(prev => {
        const increment = (panelCount * 0.15); // Consommation plus lente
        return prev + increment;
      });
    }, 500);

    // Démarrer l'animation des billets après 8 secondes
    setTimeout(() => {
      setAnimationStage('savings');
      const billsTimer = setInterval(() => {
        setMoneyBills(prev => prev + 1);
      }, 1500);
      
      // Arrêter les billets après 12 secondes
      setTimeout(() => {
        clearInterval(billsTimer);
      }, 12000);
    }, 8000);

    // Arrêter après 25 secondes et marquer comme terminé
    setTimeout(() => {
      clearInterval(productionTimer);
      setAnimationStage('complete');
    }, 25000);
  };

  const getStatusText = () => {
    switch (animationStage) {
      case 'ready': return 'Prêt à démarrer...';
      case 'panels': return `🔧 Installation panneau ${currentPanel}/${panelCount}...`;
      case 'production': return '⚡ Production d\'énergie en cours...';
      case 'savings': return '💰 Calcul des économies...';
      case 'complete': return '🎉 Installation terminée ! Système opérationnel !';
      default: return 'Prêt à démarrer...';
    }
  };

  // Nouveau badge pour l'autoconsommation
  const showEconomyBadge = animationStage === 'savings' || animationStage === 'complete';

  return (
    <div className="solar-animation-container" data-panels={panelCount}>
      <h1 className="animation-title">🎬 Installation de {panelCount} Panneaux Solaires</h1>
      <div className="animation-status">{getStatusText()}</div>
      
      <div className="animation-ground"></div>
      
      {/* Soleil Animé en haut à gauche */}
      <div className="animated-sun">
        <div className="sun-core"></div>
        <div className="sun-rays">
          {Array.from({ length: 8 }, (_, index) => (
            <div key={index} className={`sun-ray ray-${index + 1}`}></div>
          ))}
        </div>
        <div className="sun-glow"></div>
      </div>
      
      {/* Panneaux Solaires - Nombre variable */}
      {Array.from({ length: panelCount }, (_, index) => (
        <div 
          key={index}
          className={`solar-panel panel-${index + 1} ${currentPanel > index ? 'show' : ''} ${producingPanels.includes(index + 1) ? 'producing' : ''}`}
        >
          <div className="panel-number">{index + 1}</div>
          
          {/* kWh flottants produits par ce panneau */}
          {producingPanels.includes(index + 1) && (
            <div className="kwh-production">
              <div className="kwh-floating">kWh</div>
              <div className="kwh-floating" style={{animationDelay: '1s'}}>kWh</div>
              <div className="kwh-floating" style={{animationDelay: '2s'}}>kWh</div>
            </div>
          )}
        </div>
      ))}
      
      {/* Câble de raccordement du dernier panneau au compteur */}
      {producingPanels.length > 0 && (
        <div className="power-cable"></div>
      )}
      
      {/* Compteur Linky - AGRANDI */}
      <div className={`linky-counter ${animationStage === 'production' || animationStage === 'savings' || animationStage === 'complete' ? 'active' : ''}`}>
        <div className="linky-header">LINKY</div>
        <div className="linky-screen">
          <div className="linky-display">{kwhProduction.toFixed(2)}</div>
          <div className="linky-unit">kWh</div>
        </div>
        <div className={`linky-led ${animationStage === 'production' || animationStage === 'savings' ? 'blinking' : ''}`}></div>
        <div className="linky-label">Production Solaire</div>
      </div>
      
      {/* Application Mobile - PERMANENTE ET MISE À JOUR */}
      <div className={`mobile-app ${animationStage === 'production' || animationStage === 'savings' || animationStage === 'complete' ? 'show' : ''}`}>
        <div className="app-header">Solar Monitor</div>
        <div className="app-production">{kwhProduction.toFixed(1)} kWh</div>
        <div className="app-label">Production aujourd'hui</div>
        <div className="app-consumption">{kwhConsumption.toFixed(1)} kWh</div>
        <div className="app-label">Consommation</div>
        <div className="app-chart">
          <div className="chart-bar production" style={{height: `${Math.min(80, (kwhProduction/50) * 80)}%`}}></div>
          <div className="chart-bar consumption" style={{height: `${Math.min(80, (kwhConsumption/50) * 80)}%`}}></div>
        </div>
      </div>
      
      {/* Section Économies */}
      {(animationStage === 'savings' || animationStage === 'complete') && (
        <div className="savings-section">
          <div className="savings-text">
            Autoconsommation = Économies<br />
            <span>directement sur votre Facture</span>
          </div>
          <div className="money-stack">
            {Array.from({ length: Math.min(moneyBills, 8) }, (_, index) => (
              <div 
                key={index} 
                className="money-bill"
                style={{
                  animationDelay: `${index * 1.5}s`,
                  zIndex: 10 + index,
                  bottom: `${index * 3}px`
                }}
              >
                💶
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* Boutons de contrôle */}
      <div className="animation-controls">
        <button onClick={startAnimation} className="restart-btn">
          🔄 Recommencer
        </button>
        <button onClick={onBack} className="back-btn">
          ← Retour aux Résultats
        </button>
        <button onClick={onNext} className="next-btn">
          📋 Voir les Résultats Détaillés
        </button>
      </div>
    </div>
  );
};

export default SolarAnimationCSS;