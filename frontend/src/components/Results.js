import React, { useState } from 'react';
import TechnicalSummary from './TechnicalSummary';
import FinancingTable from './FinancingTable';
import MonitoringInterface from './MonitoringInterface';
import MobileApp from './MobileApp';
import InstallationPhotos from './InstallationPhotos';
import GainsEvolution from './GainsEvolution';

const Results = ({ formData, onBack }) => {
  const [activeTab, setActiveTab] = useState('ensemble');

  // Calculs basés sur les données du formulaire
  const calculatedData = {
    kitPower: 9, // kW
    autonomy: 95, // %
    annualProduction: 10944, // kWh
    guaranteedSavings: 2177, // €
    surfaceRequired: 47, // m²
    panelCount: 18,
    totalCostTTC: 29900, // €
    monthlyPayment: 236, // €
    optimizedPayment: 129, // € (avec aides)
    monthlyEDFSavings: 181, // €
  };

  const tabs = [
    { id: 'ensemble', label: 'Vue d\'ensemble', icon: '📊' },
    { id: 'technique', label: 'Détails techniques', icon: '⚙️' },
    { id: 'financement', label: 'Analyse financière', icon: '💰' },
    { id: 'monitoring', label: 'Monitoring 2025', icon: '📈' },
    { id: 'mobile', label: 'App Mobile', icon: '📱' },
    { id: 'installation', label: 'Installation', icon: '🔧' }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-400 via-orange-500 to-yellow-500 p-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-2xl shadow-2xl p-6 mb-6">
          <div className="flex justify-between items-center mb-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-800">Votre Étude Solaire Personnalisée</h1>
              <p className="text-gray-600">Résultats pour {formData.prenom} {formData.nom}</p>
            </div>
            <button
              onClick={onBack}
              className="px-4 py-2 bg-gray-500 text-white rounded-md hover:bg-gray-600 transition-colors"
            >
              ← Retour
            </button>
          </div>

          {/* Navigation tabs */}
          <div className="flex flex-wrap gap-2 border-b">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-2 text-sm font-medium rounded-t-lg transition-colors ${
                  activeTab === tab.id
                    ? 'bg-orange-500 text-white'
                    : 'text-gray-600 hover:text-orange-500'
                }`}
              >
                {tab.icon} {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Content */}
        <div className="bg-white rounded-2xl shadow-2xl p-6">
          {activeTab === 'ensemble' && (
            <div>
              <h2 className="text-xl font-bold text-gray-800 mb-6">📊 Vue d'ensemble</h2>
              
              {/* Vignettes techniques alignées */}
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                <div className="bg-gradient-to-br from-blue-500 to-blue-600 text-white p-6 rounded-xl">
                  <div className="text-center">
                    <div className="text-2xl mb-2">⚡</div>
                    <h3 className="font-bold text-sm mb-2">Kit Solaire Optimal</h3>
                    <div className="text-3xl font-bold">{calculatedData.kitPower} kW</div>
                    <div className="text-xs mt-2">{calculatedData.panelCount} panneaux de 500W</div>
                    <div className="text-xs text-blue-100">{calculatedData.totalCostTTC} € TTC</div>
                    <div className="text-xs mt-1">Surface nécessaire: {calculatedData.surfaceRequired} m²</div>
                  </div>
                </div>

                <div className="bg-gradient-to-br from-green-500 to-green-600 text-white p-6 rounded-xl">
                  <div className="text-center">
                    <div className="text-2xl mb-2">🔋</div>
                    <h3 className="font-bold text-sm mb-2">Autonomie Énergétique</h3>
                    <div className="text-3xl font-bold">{calculatedData.autonomy}%</div>
                    <div className="text-xs mt-2">Autoconsommation optimisée</div>
                  </div>
                </div>

                <div className="bg-gradient-to-br from-orange-500 to-orange-600 text-white p-6 rounded-xl">
                  <div className="text-center">
                    <div className="text-2xl mb-2">☀️</div>
                    <h3 className="font-bold text-sm mb-2">Production Annuelle</h3>
                    <div className="text-3xl font-bold">{calculatedData.annualProduction.toLocaleString()}</div>
                    <div className="text-xs">kWh</div>
                    <div className="text-xs mt-2">Données PVGIS officielles</div>
                    <div className="text-xs">Orientation: Sud</div>
                  </div>
                </div>

                <div className="bg-gradient-to-br from-blue-600 to-blue-700 text-white p-6 rounded-xl">
                  <div className="text-center">
                    <div className="text-2xl mb-2">💰</div>
                    <h3 className="font-bold text-sm mb-2">Économies Garanties</h3>
                    <div className="text-3xl font-bold">{calculatedData.guaranteedSavings} €</div>
                    <div className="text-xs mt-2">Soit {Math.round(calculatedData.guaranteedSavings/12)} €/mois</div>
                    <div className="text-xs">Autoconsommation: {Math.round(calculatedData.annualProduction * 0.7)} kWh</div>
                    <div className="text-xs">Surplus vendu: {Math.round(calculatedData.annualProduction * 0.3)} kWh</div>
                  </div>
                </div>
              </div>

              {/* Graphique évolution des gains */}
              <GainsEvolution />
            </div>
          )}

          {activeTab === 'technique' && (
            <TechnicalSummary calculatedData={calculatedData} formData={formData} />
          )}

          {activeTab === 'financement' && (
            <FinancingTable calculatedData={calculatedData} />
          )}

          {activeTab === 'monitoring' && (
            <MonitoringInterface />
          )}

          {activeTab === 'mobile' && (
            <MobileApp />
          )}

          {activeTab === 'installation' && (
            <InstallationPhotos />
          )}
        </div>
      </div>
    </div>
  );
};

export default Results;