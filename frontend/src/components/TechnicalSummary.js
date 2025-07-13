import React from 'react';

const TechnicalSummary = ({ calculatedData, formData }) => {
  return (
    <div>
      <h2 className="text-xl font-bold text-gray-800 mb-6">⚙️ Détails techniques</h2>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Spécifications du kit */}
        <div className="bg-blue-50 p-6 rounded-lg">
          <h3 className="text-lg font-bold text-blue-800 mb-4">📦 Spécifications du kit solaire</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-blue-700">Puissance totale:</span>
              <span className="font-bold text-blue-800">{calculatedData.kitPower} kWc</span>
            </div>
            <div className="flex justify-between">
              <span className="text-blue-700">Nombre de panneaux:</span>
              <span className="font-bold text-blue-800">{calculatedData.panelCount} unités</span>
            </div>
            <div className="flex justify-between">
              <span className="text-blue-700">Puissance par panneau:</span>
              <span className="font-bold text-blue-800">500 Wc</span>
            </div>
            <div className="flex justify-between">
              <span className="text-blue-700">Surface nécessaire:</span>
              <span className="font-bold text-blue-800">{calculatedData.surfaceRequired} m²</span>
            </div>
            <div className="flex justify-between">
              <span className="text-blue-700">Type de panneaux:</span>
              <span className="font-bold text-blue-800">Monocristallin</span>
            </div>
            <div className="flex justify-between">
              <span className="text-blue-700">Garantie panneaux:</span>
              <span className="font-bold text-blue-800">25 ans</span>
            </div>
          </div>
        </div>

        {/* Données de production */}
        <div className="bg-green-50 p-6 rounded-lg">
          <h3 className="text-lg font-bold text-green-800 mb-4">☀️ Données de production PVGIS</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-green-700">Production annuelle:</span>
              <span className="font-bold text-green-800">{calculatedData.annualProduction.toLocaleString()} kWh</span>
            </div>
            <div className="flex justify-between">
              <span className="text-green-700">Production mensuelle moy.:</span>
              <span className="font-bold text-green-800">{Math.round(calculatedData.annualProduction/12)} kWh</span>
            </div>
            <div className="flex justify-between">
              <span className="text-green-700">Irradiation optimale:</span>
              <span className="font-bold text-green-800">1.215 kWh/m²/jour</span>
            </div>
            <div className="flex justify-between">
              <span className="text-green-700">Orientation:</span>
              <span className="font-bold text-green-800">{formData.orientationToiture || 'Sud'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-green-700">Inclinaison optimale:</span>
              <span className="font-bold text-green-800">30°</span>
            </div>
            <div className="flex justify-between">
              <span className="text-green-700">Facteur de performance:</span>
              <span className="font-bold text-green-800">86%</span>
            </div>
          </div>
        </div>

        {/* Autoconsommation */}
        <div className="bg-orange-50 p-6 rounded-lg">
          <h3 className="text-lg font-bold text-orange-800 mb-4">🔋 Autoconsommation</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-orange-700">Taux d'autoconsommation:</span>
              <span className="font-bold text-orange-800">{calculatedData.autonomy}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-orange-700">Énergie autoconsommée:</span>
              <span className="font-bold text-orange-800">{Math.round(calculatedData.annualProduction * 0.7)} kWh/an</span>
            </div>
            <div className="flex justify-between">
              <span className="text-orange-700">Surplus revendu:</span>
              <span className="font-bold text-orange-800">{Math.round(calculatedData.annualProduction * 0.3)} kWh/an</span>
            </div>
            <div className="flex justify-between">
              <span className="text-orange-700">Prix de rachat EDF:</span>
              <span className="font-bold text-orange-800">0,1297 €/kWh</span>
            </div>
            <div className="flex justify-between">
              <span className="text-orange-700">Consommation actuelle:</span>
              <span className="font-bold text-orange-800">{formData.consommationAnnuelle || '4500'} kWh/an</span>
            </div>
            <div className="flex justify-between">
              <span className="text-orange-700">Couverture des besoins:</span>
              <span className="font-bold text-orange-800">{Math.round((calculatedData.annualProduction * 0.7) / (formData.consommationAnnuelle || 4500) * 100)}%</span>
            </div>
          </div>
        </div>

        {/* Équipements */}
        <div className="bg-purple-50 p-6 rounded-lg">
          <h3 className="text-lg font-bold text-purple-800 mb-4">🔧 Équipements inclus</h3>
          <div className="space-y-3">
            <div className="flex items-center">
              <div className="w-3 h-3 bg-purple-500 rounded-full mr-3"></div>
              <span className="text-purple-700">Micro-onduleurs Enphase IQ8+</span>
            </div>
            <div className="flex items-center">
              <div className="w-3 h-3 bg-purple-500 rounded-full mr-3"></div>
              <span className="text-purple-700">Monitoring en temps réel</span>
            </div>
            <div className="flex items-center">
              <div className="w-3 h-3 bg-purple-500 rounded-full mr-3"></div>
              <span className="text-purple-700">Coffret de protection AC/DC</span>
            </div>
            <div className="flex items-center">
              <div className="w-3 h-3 bg-purple-500 rounded-full mr-3"></div>
              <span className="text-purple-700">Compteur de production</span>
            </div>
            <div className="flex items-center">
              <div className="w-3 h-3 bg-purple-500 rounded-full mr-3"></div>
              <span className="text-purple-700">Système de fixation aluminium</span>
            </div>
            <div className="flex items-center">
              <div className="w-3 h-3 bg-purple-500 rounded-full mr-3"></div>
              <span className="text-purple-700">Câbles et connecteurs MC4</span>
            </div>
          </div>
        </div>
      </div>

      {/* Performance garantie */}
      <div className="mt-8 bg-gradient-to-r from-green-500 to-blue-500 text-white p-6 rounded-lg">
        <h3 className="text-lg font-bold mb-4">🎯 Performance garantie</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="text-3xl font-bold">{calculatedData.guaranteedSavings} €</div>
            <div className="text-sm opacity-90">Économies annuelles garanties</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold">25 ans</div>
            <div className="text-sm opacity-90">Garantie de performance</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold">85%</div>
            <div className="text-sm opacity-90">Rendement minimum garanti à 25 ans</div>
          </div>
        </div>
      </div>

      {/* Note technique */}
      <div className="mt-6 bg-gray-50 border-l-4 border-gray-400 p-4">
        <p className="text-sm text-gray-700">
          <strong>📋 Note technique:</strong> Ces calculs sont basés sur les données PVGIS (Photovoltaic Geographical Information System) 
          de la Commission Européenne, référence mondiale pour l'estimation du potentiel solaire. L'installation sera dimensionnée 
          précisément selon votre consommation réelle et l'orientation de votre toiture.
        </p>
      </div>
    </div>
  );
};

export default TechnicalSummary;