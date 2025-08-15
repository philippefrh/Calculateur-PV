import React, { useState, useEffect } from 'react';
import './SolarAnimationCSS.css';

const SolarAnimationCSS = ({ panelCount = 12, onBack, onNext, batterySelected = false }) => {
  const [animationStage, setAnimationStage] = useState('ready');
  const [currentPanel, setCurrentPanel] = useState(0);
  const [kwhProduction, setKwhProduction] = useState(0);
  const [kwhConsumption, setKwhConsumption] = useState(0);
  const [producingPanels, setProducingPanels] = useState([]);
  const [moneyBills, setMoneyBills] = useState(0);
  const [batteryChargeLevel, setBatteryChargeLevel] = useState(0); // Nouveau état pour le niveau de charge progressive
  const [batteryCharging, setBatteryCharging] = useState(true); // Nouveau état pour le sens de charge/décharge
  const [isNightMode, setIsNightMode] = useState(false); // Nouveau état pour le mode jour/nuit

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
    setBatteryChargeLevel(0); // Réinitialiser la charge de la batterie
    setBatteryCharging(true);
    
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

    // Démarrer l'animation progressive de la batterie si elle est sélectionnée
    // SYNCHRONISÉ avec le démarrage de la production des panneaux
    if (batterySelected) {
      setTimeout(() => {
        console.log("🔋 Démarrage de l'animation de charge de la batterie...");
        startBatteryChargingCycle();
      }, 1000); // Démarrer 1 seconde après le début de la production
    }

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

  // Nouvelle fonction pour l'animation progressive de charge/décharge de la batterie
  const startBatteryChargingCycle = () => {
    console.log("🔋 Démarrage du cycle de charge/décharge de la batterie");
    let currentLevel = 0;
    let charging = true;
    
    const batteryTimer = setInterval(() => {
      if (charging) {
        // Phase de charge : 0% → 100% par paliers de 5%
        currentLevel += 5;
        console.log(`🔋 Charge: ${currentLevel}%`);
        
        if (currentLevel >= 100) {
          console.log("🔋 Batterie chargée à 100%, passage en décharge dans 2 secondes");
          charging = false;
        }
      } else {
        // Phase de décharge : 100% → 0% par paliers de 5%
        currentLevel -= 5;
        console.log(`🔋 Décharge: ${currentLevel}%`);
        
        if (currentLevel <= 0) {
          console.log("🔋 Batterie déchargée à 0%, passage en charge dans 2 secondes");
          charging = true;
        }
      }
      
      // Mettre à jour les états React
      setBatteryChargeLevel(currentLevel);
      setBatteryCharging(charging);
      
      // Nouveau : Gérer le mode jour/nuit selon l'état de la batterie
      if (charging && currentLevel > 0) {
        // Mode jour pendant la charge
        setIsNightMode(false);
      } else if (!charging && currentLevel < 100) {
        // Mode nuit pendant la décharge
        setIsNightMode(true);
      }
      
    }, 1000); // Changement toutes les 1 seconde

    // Nettoyage du timer après l'animation complète
    setTimeout(() => {
      clearInterval(batteryTimer);
      console.log("🔋 Cycle de batterie terminé");
    }, 30000); // 30 secondes pour voir plusieurs cycles
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
      
      {/* Nouveau badge pour l'autoconsommation */}
      {showEconomyBadge && (
        <div className="economy-badge">
          Autoconsommation = Économies directement sur votre Facture
        </div>
      )}
      
      {/* Nouveau badge pour la batterie de stockage - Affiché seulement si batterie sélectionnée */}
      {showEconomyBadge && batterySelected && (
        <div className="battery-usage-badge">
          Batterie de Stockage = Utilisation pour la Nuit : Climatisation , Lumière , TV , PC , chargeur , Frigo , etc..
        </div>
      )}
      
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
      
      {/* Batterie de stockage - Affichée seulement si sélectionnée */}
      {batterySelected && (
        <div className={`solar-battery ${animationStage === 'production' || animationStage === 'savings' || animationStage === 'complete' ? 'active' : ''}`}>
          <div className="battery-container">
            <div className="battery-body">
              <div className="battery-terminal"></div>
              <div className="battery-level">
                <div 
                  className={`battery-charge ${batteryCharging ? 'charging' : 'discharging'}`}
                  style={{ height: `${batteryChargeLevel}%` }}
                ></div>
              </div>
              <div className="battery-label">🔋 Stockage</div>
            </div>
            
            {/* Indicateur de charge progressive */}
            {(animationStage === 'production' || animationStage === 'savings' || animationStage === 'complete') && (
              <div className="battery-status">
                <div className="charge-percentage">{batteryChargeLevel}%</div>
                <div className="charge-text">{batteryCharging ? 'en charge' : 'en décharge pour utilisation batterie la nuit'}</div>
              </div>
            )}
            
            {/* Flux d'énergie vers la batterie */}
            {producingPanels.length > 0 && (
              <div className="energy-flow-to-battery">
                <div className="energy-particle" style={{animationDelay: '0s'}}>⚡</div>
                <div className="energy-particle" style={{animationDelay: '0.8s'}}>⚡</div>
                <div className="energy-particle" style={{animationDelay: '1.6s'}}>⚡</div>
              </div>
            )}
          </div>
        </div>
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
      
      {/* Section Économies avec de vrais billets d'euros */}
      {(animationStage === 'savings' || animationStage === 'complete') && (
        <div className="savings-section">
          <div className="money-stack">
            {/* Première couche - Billets de base */}
            {moneyBills >= 1 && <div className="euro-bill bill-50" style={{animationDelay: '0s', bottom: '0px', left: '5px', zIndex: 1}}>50</div>}
            {moneyBills >= 2 && <div className="euro-bill bill-20" style={{animationDelay: '1.5s', bottom: '2px', left: '10px', zIndex: 2}}>20</div>}
            
            {/* Deuxième couche */}
            {moneyBills >= 3 && <div className="euro-bill bill-10" style={{animationDelay: '3s', bottom: '4px', left: '0px', zIndex: 3}}>10</div>}
            {moneyBills >= 4 && <div className="euro-bill bill-5" style={{animationDelay: '4.5s', bottom: '6px', left: '15px', zIndex: 4}}>5</div>}
            
            {/* Troisième couche */}
            {moneyBills >= 5 && <div className="euro-bill bill-50" style={{animationDelay: '6s', bottom: '8px', left: '3px', zIndex: 5}}>50</div>}
            {moneyBills >= 6 && <div className="euro-bill bill-20" style={{animationDelay: '7.5s', bottom: '10px', left: '12px', zIndex: 6}}>20</div>}
            
            {/* Quatrième couche - Tas qui grandit */}
            {moneyBills >= 7 && <div className="euro-bill bill-10" style={{animationDelay: '9s', bottom: '12px', left: '7px', zIndex: 7}}>10</div>}
            {moneyBills >= 8 && <div className="euro-bill bill-5" style={{animationDelay: '10.5s', bottom: '14px', left: '2px', zIndex: 8}}>5</div>}
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