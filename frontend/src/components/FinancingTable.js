import React, { useState } from 'react';

const FinancingTable = ({ calculatedData }) => {
  const [showFinancing, setShowFinancing] = useState(true);

  // Données du tableau de financement
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
    <div>
      <h2 className="text-xl font-bold text-gray-800 mb-6">💰 Analyse financière</h2>

      {/* Toggle button */}
      <div className="mb-6">
        <button
          onClick={() => setShowFinancing(!showFinancing)}
          className="bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600 transition-colors"
        >
          📊 {showFinancing ? 'Masquer' : 'Afficher'} le financement
        </button>
      </div>

      {/* Financing table */}
      {showFinancing && (
        <div className="mb-8">
          <h3 className="text-lg font-bold text-gray-800 mb-4">📋 Toutes les options de financement disponibles</h3>
          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr className="bg-orange-500 text-white">
                  <th className="border px-4 py-3 text-left">Durée</th>
                  <th className="border px-4 py-3 text-left">Mensualité</th>
                  <th className="border px-4 py-3 text-left">Différence vs économies</th>
                </tr>
              </thead>
              <tbody>
                {financingOptions.map((option, index) => (
                  <tr key={index} className="border-b hover:bg-gray-50">
                    <td className="border px-4 py-3 font-medium">{option.duration} ans</td>
                    <td className="border px-4 py-3">{option.monthly} €</td>
                    <td className="border px-4 py-3 text-orange-600 font-medium">+{option.savings} €/mois</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Recommended financing options */}
      <div className="space-y-6">
        <h3 className="text-lg font-bold text-gray-800">🏆 Options de financement recommandées</h3>
        
        {/* Standard financing */}
        <div className="border-2 border-orange-200 rounded-lg p-6 bg-orange-50">
          <div className="flex items-center justify-between mb-4">
            <h4 className="font-bold text-gray-800 flex items-center">
              ⭐ Financement standard sur 15 ans
            </h4>
            <span className="bg-gray-200 text-gray-700 px-3 py-1 rounded-full text-sm">Sans aides déduites</span>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div className="flex justify-between">
              <span>Investissement total:</span>
              <span className="font-bold">29 900 € TTC</span>
            </div>
            <div className="flex justify-between">
              <span>Mensualité crédit:</span>
              <span className="font-bold">236 €/mois</span>
            </div>
            <div className="flex justify-between">
              <span>Économie EDF:</span>
              <span className="font-bold text-green-600">181 €/mois</span>
            </div>
            <div className="flex justify-between">
              <span>Reste à charge:</span>
              <span className="font-bold text-orange-600">+54 €/mois</span>
            </div>
          </div>
        </div>

        {/* Optimized financing with subsidies */}
        <div className="border-2 border-green-500 rounded-lg p-6 bg-green-50">
          <div className="flex items-center justify-between mb-4">
            <h4 className="font-bold text-gray-800 flex items-center">
              🔥 Financement optimisé sur 15 ans
            </h4>
            <span className="bg-green-500 text-white px-3 py-1 rounded-full text-sm">Avec aides déduites</span>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div className="flex justify-between">
              <span>Investissement après aides:</span>
              <span className="font-bold">23 200 € TTC</span>
            </div>
            <div className="flex justify-between">
              <span>Mensualité crédit réduite:</span>
              <span className="font-bold">129 €/mois</span>
            </div>
            <div className="flex justify-between">
              <span>Économie EDF:</span>
              <span className="font-bold text-green-600">181 €/mois</span>
            </div>
            <div className="flex justify-between">
              <span>Reste à charge optimisé:</span>
              <span className="font-bold text-green-600">-53 €/mois</span>
            </div>
          </div>

          {/* Aides détaillées */}
          <div className="mt-6 bg-green-100 p-4 rounded-lg">
            <h5 className="font-bold text-green-800 mb-3">✅ Aides incluses dans le calcul optimisé:</h5>
            <div className="space-y-2 text-sm">
              <div className="flex items-center">
                <span className="w-4 h-4 bg-green-500 rounded mr-2"></span>
                <span>6 premiers mois GRATUITS (0€ pendant l'installation)</span>
              </div>
              <div className="flex items-center">
                <span className="w-4 h-4 bg-green-500 rounded mr-2"></span>
                <span>Aides récupérées: 6700 € (Prime + TVA)</span>
              </div>
              <div className="flex items-center">
                <span className="w-4 h-4 bg-green-500 rounded mr-2"></span>
                <span>Taux fixe 4,96% TAEG sur toute la durée</span>
              </div>
              <div className="flex items-center">
                <span className="w-4 h-4 bg-green-500 rounded mr-2"></span>
                <span>Économie mensuelle supérieure au crédit !</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Note importante */}
      <div className="mt-6 bg-blue-50 border-l-4 border-blue-500 p-4">
        <p className="text-sm text-blue-800">
          <strong>💡 Note importante:</strong> Les mensualités incluent désormais les +35€ d'intérêts qui étaient omis dans le calcul précédent. 
          Le financement optimisé permet une économie immédiate dès le premier mois d'installation.
        </p>
      </div>
    </div>
  );
};

export default FinancingTable;