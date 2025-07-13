import React, { useState } from 'react';

const MultiStepForm = ({ onComplete, onBack }) => {
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState({
    // Étape 1 - Informations personnelles
    prenom: '',
    nom: '',
    adresse: '',
    
    // Étape 2 - Informations logement
    typeLogement: '',
    surfaceToiture: '',
    orientationToiture: '',
    
    // Étape 3 - Consommation électrique
    consommationAnnuelle: '',
    factureMensuelle: '',
    
    // Étape 4 - Contact
    telephone: '',
    email: '',
    horairesContact: ''
  });

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const nextStep = () => {
    if (currentStep < 4) {
      setCurrentStep(currentStep + 1);
    } else {
      onComplete(formData);
    }
  };

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    } else {
      onBack();
    }
  };

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return (
          <div>
            <h2 className="text-xl font-bold text-gray-800 mb-4">📋 Étape 1/4 - Informations Personnelles</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  👤 Prénom *
                </label>
                <input
                  type="text"
                  value={formData.prenom}
                  onChange={(e) => handleInputChange('prenom', e.target.value)}
                  placeholder="Votre prénom"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  👤 Nom *
                </label>
                <input
                  type="text"
                  value={formData.nom}
                  onChange={(e) => handleInputChange('nom', e.target.value)}
                  placeholder="Votre nom de famille"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  🏠 Adresse exacte de votre domicile *
                </label>
                <input
                  type="text"
                  value={formData.adresse}
                  onChange={(e) => handleInputChange('adresse', e.target.value)}
                  placeholder="15 Avenue des Champs-Élysées, 75008 Paris"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500"
                />
              </div>
              <p className="text-xs text-gray-500">💡 Cette adresse sera utilisée pour calculer précisément votre potentiel solaire.</p>
            </div>
          </div>
        );

      case 2:
        return (
          <div>
            <h2 className="text-xl font-bold text-gray-800 mb-4">🏠 Étape 2/4 - Votre Logement</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Type de logement</label>
                <select
                  value={formData.typeLogement}
                  onChange={(e) => handleInputChange('typeLogement', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500"
                >
                  <option value="">Sélectionnez votre type de logement</option>
                  <option value="maison">Maison individuelle</option>
                  <option value="appartement">Appartement</option>
                  <option value="villa">Villa</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Surface approximative de votre toiture (m²)</label>
                <input
                  type="number"
                  value={formData.surfaceToiture}
                  onChange={(e) => handleInputChange('surfaceToiture', e.target.value)}
                  placeholder="Ex: 80"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Orientation principale de votre toiture</label>
                <select
                  value={formData.orientationToiture}
                  onChange={(e) => handleInputChange('orientationToiture', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500"
                >
                  <option value="">Sélectionnez l'orientation</option>
                  <option value="sud">Sud (optimal)</option>
                  <option value="sud-est">Sud-Est</option>
                  <option value="sud-ouest">Sud-Ouest</option>
                  <option value="est">Est</option>
                  <option value="ouest">Ouest</option>
                  <option value="nord">Nord</option>
                </select>
              </div>
            </div>
          </div>
        );

      case 3:
        return (
          <div>
            <h2 className="text-xl font-bold text-gray-800 mb-4">⚡ Étape 3/4 - Consommation Électrique</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Consommation électrique annuelle (kWh)</label>
                <input
                  type="number"
                  value={formData.consommationAnnuelle}
                  onChange={(e) => handleInputChange('consommationAnnuelle', e.target.value)}
                  placeholder="Ex: 4500"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Montant moyen de votre facture mensuelle d'électricité (€)</label>
                <input
                  type="number"
                  value={formData.factureMensuelle}
                  onChange={(e) => handleInputChange('factureMensuelle', e.target.value)}
                  placeholder="Ex: 120"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500"
                />
              </div>
              <p className="text-xs text-gray-500">💡 Ces informations nous permettront de dimensionner parfaitement votre installation.</p>
            </div>
          </div>
        );

      case 4:
        return (
          <div>
            <h2 className="text-xl font-bold text-gray-800 mb-4">📞 Étape 4/4 - Contact</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Numéro de téléphone *</label>
                <input
                  type="tel"
                  value={formData.telephone}
                  onChange={(e) => handleInputChange('telephone', e.target.value)}
                  placeholder="06 12 34 56 78"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Adresse email</label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => handleInputChange('email', e.target.value)}
                  placeholder="votre.email@exemple.com"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Créneaux de contact préférés</label>
                <select
                  value={formData.horairesContact}
                  onChange={(e) => handleInputChange('horairesContact', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500"
                >
                  <option value="">Sélectionnez vos préférences</option>
                  <option value="matin">Matin (8h-12h)</option>
                  <option value="apres-midi">Après-midi (14h-18h)</option>
                  <option value="soir">Soir (18h-20h)</option>
                  <option value="weekend">Week-end</option>
                </select>
              </div>
              <p className="text-xs text-gray-500">💡 Un de nos conseillers vous contactera dans les 24h pour finaliser votre étude personnalisée.</p>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full">
        {/* Progress bar */}
        <div className="mb-6">
          <div className="flex justify-between mb-2">
            {[1, 2, 3, 4].map((step) => (
              <div
                key={step}
                className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                  step <= currentStep
                    ? 'bg-orange-500 text-white'
                    : 'bg-gray-200 text-gray-500'
                }`}
              >
                {step}
              </div>
            ))}
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-orange-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${(currentStep / 4) * 100}%` }}
            ></div>
          </div>
        </div>

        {renderStep()}

        {/* Navigation buttons */}
        <div className="flex justify-between mt-8">
          <button
            onClick={prevStep}
            className="px-6 py-2 bg-gray-500 text-white rounded-md hover:bg-gray-600 transition-colors"
          >
            Précédent
          </button>
          <button
            onClick={nextStep}
            className="px-6 py-2 bg-orange-500 text-white rounded-md hover:bg-orange-600 transition-colors"
          >
            {currentStep === 4 ? 'Suivant →' : 'Suivant →'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default MultiStepForm;