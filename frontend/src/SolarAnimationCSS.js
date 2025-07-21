import React, { useState, useEffect } from 'react';
import './SolarAnimationCSS.css';

const SolarAnimationCSS = ({ panelCount = 12, onBack, onNext }) => {
  const [animationStage, setAnimationStage] = useState('ready');
  const [currentPanel, setCurrentPanel] = useState(0);
  const [kwhProduction, setKwhProduction] = useState(0);
  const [producingPanels, setProducingPanels] = useState([]);

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
    setProducingPanels([]);
    
    // Animation des panneaux un par un
    for (let i = 0; i < panelCount; i++) {
      setTimeout(() => {
        setCurrentPanel(i + 1);
        
        // Si c'est le dernier panneau, démarrer la production après l'app
        if (i === panelCount - 1) {
          setTimeout(() => {
            setAnimationStage('app');
            
            setTimeout(() => {
              setAnimationStage('production');
              startProduction();
            }, 2000);
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
        const increment = (panelCount * 0.25); // 0.25 kWh par panneau par tick
        return prev + increment;
      });
    }, 500);

    // Arrêter après 20 secondes et marquer comme terminé
    setTimeout(() => {
      clearInterval(productionTimer);
      setAnimationStage('complete');
    }, 20000);
  };

  const getStatusText = () => {
    switch (animationStage) {
      case 'ready': return 'Prêt à démarrer...';
      case 'panels': return `🔧 Installation panneau ${currentPanel}/${panelCount}...`;
      case 'app': return '📱 Connexion application monitoring...';
      case 'production': return '⚡ Production d\'énergie en cours...';
      case 'complete': return '🎉 Installation terminée ! Système opérationnel !';
      default: return 'Prêt à démarrer...';
    }
  };

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
      
      {/* Compteur Linky */}
      <div className={`linky-counter ${animationStage === 'production' || animationStage === 'complete' ? 'active' : ''}`}>
        <div className="linky-header">LINKY</div>
        <div className="linky-screen">
          <div className="linky-display">{kwhProduction.toFixed(2)}</div>
          <div className="linky-unit">kWh</div>
        </div>
        <div className={`linky-led ${animationStage === 'production' ? 'blinking' : ''}`}></div>
        <div className="linky-label">Production Solaire</div>
      </div>
      
      {/* Application Mobile - AGRANDIE ET CENTRÉE */}
      <div className={`mobile-app ${animationStage === 'app' || animationStage === 'complete' ? 'show' : ''}`}>
        <div className="app-header">Solar Monitor</div>
        <div className="app-production">27.32 kWh</div>
        <div className="app-label">Production aujourd'hui</div>
        <div className="app-consumption">30.02 kWh</div>
        <div className="app-label">Consommation</div>
        <div className="app-chart"></div>
      </div>
      
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