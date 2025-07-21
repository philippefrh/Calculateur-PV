import React, { useState, useEffect } from 'react';
import './SolarAnimationCSS.css';

const SolarAnimationCSS = ({ panelCount = 12, onBack, onNext }) => {
  const [animationStage, setAnimationStage] = useState('ready');
  const [currentPanel, setCurrentPanel] = useState(0);

  useEffect(() => {
    // Démarrer l'animation automatiquement après 2 secondes
    const timer = setTimeout(() => {
      startAnimation();
    }, 2000);

    return () => clearTimeout(timer);
  }, []);

  const startAnimation = () => {
    setAnimationStage('panels');
    
    // Animation des panneaux un par un
    for (let i = 0; i < panelCount; i++) {
      setTimeout(() => {
        setCurrentPanel(i + 1);
        
        // Si c'est le dernier panneau, passer directement à l'app (sans onduleur)
        if (i === panelCount - 1) {
          setTimeout(() => {
            setAnimationStage('app');
            
            setTimeout(() => {
              setAnimationStage('complete');
            }, 2000);
          }, 1000);
        }
      }, i * 300);
    }
  };

  const getStatusText = () => {
    switch (animationStage) {
      case 'ready': return 'Prêt à démarrer...';
      case 'panels': return `🔧 Installation panneau ${currentPanel}/${panelCount}...`;
      case 'app': return '📱 Connexion application monitoring...';
      case 'complete': return '🎉 Installation terminée ! Système opérationnel !';
      default: return 'Prêt à démarrer...';
    }
  };

  return (
    <div className="solar-animation-container" data-panels={panelCount}>
      <h1 className="animation-title">🎬 Installation de {panelCount} Panneaux Solaires</h1>
      <div className="animation-status">{getStatusText()}</div>
      
      <div className="animation-ground"></div>
      
      {/* Panneaux Solaires - Nombre variable */}
      {Array.from({ length: panelCount }, (_, index) => (
        <div 
          key={index}
          className={`solar-panel panel-${index + 1} ${currentPanel > index ? 'show' : ''}`}
        >
          <div className="panel-number">{index + 1}</div>
        </div>
      ))}
      
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
        <button onClick={() => window.history.back()} className="back-btn">
          ← Retour aux Résultats
        </button>
        <button onClick={onNext} className="next-btn">
          Continuer →
        </button>
      </div>
    </div>
  );
};

export default SolarAnimationCSS;