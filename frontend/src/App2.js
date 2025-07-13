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