import React, { useState } from 'react';

const GainsEvolution = () => {
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

  const maxGain = Math.max(...gainsData.map(d => d.totalGain));
  const currentData = gainsData.find(d => d.year === hoveredYear) || gainsData[7];

  return (
    <div className="bg-gray-50 p-6 rounded-xl">
      <h3 className="text-lg font-bold text-gray-800 mb-4 text-center">Évolution des Gains sur 20 ans</h3>
      
      {/* Graphique interactif */}
      <div className="relative h-64 bg-white p-4 rounded-lg border mb-4">
        {/* Grille */}
        <div className="absolute inset-4 grid grid-cols-10 grid-rows-6 opacity-20">
          {Array.from({ length: 60 }, (_, i) => (
            <div key={i} className="border border-gray-300"></div>
          ))}
        </div>

        {/* Axes */}
        <div className="absolute bottom-4 left-4 right-4 flex justify-between text-xs text-gray-500">
          <span>Année 2</span>
          <span>Année 4</span>
          <span>Année 6</span>
          <span>Année 8</span>
          <span>Année 10</span>
          <span>Année 12</span>
          <span>Année 14</span>
          <span>Année 16</span>
          <span>Année 18</span>
          <span>Année 20</span>
        </div>

        <div className="absolute left-0 top-4 bottom-4 flex flex-col justify-between text-xs text-gray-500">
          <span>6000</span>
          <span>4500</span>
          <span>3000</span>
          <span>1500</span>
          <span>0</span>
        </div>

        {/* Courbe des gains */}
        <svg className="absolute inset-4 w-full h-full" viewBox="0 0 400 200">
          {/* Ligne des gains */}
          <path
            d={gainsData.map((point, index) => {
              const x = (index / (gainsData.length - 1)) * 380 + 10;
              const y = 190 - (point.totalGain / maxGain) * 180;
              return `${index === 0 ? 'M' : 'L'} ${x} ${y}`;
            }).join(' ')}
            stroke="#ef4444"
            strokeWidth="3"
            fill="none"
          />

          {/* Points interactifs */}
          {gainsData.map((point, index) => {
            const x = (index / (gainsData.length - 1)) * 380 + 10;
            const y = 190 - (point.totalGain / maxGain) * 180;
            return (
              <circle
                key={index}
                cx={x}
                cy={y}
                r={hoveredYear === point.year ? "8" : "4"}
                fill="#ef4444"
                className="cursor-pointer transition-all duration-200"
                onMouseEnter={() => setHoveredYear(point.year)}
              />
            );
          })}

          {/* Ligne bleue (revenus surplus) */}
          <line
            x1="10"
            y1="185"
            x2="390"
            y2="185"
            stroke="#3b82f6"
            strokeWidth="2"
          />
          {gainsData.map((point, index) => {
            const x = (index / (gainsData.length - 1)) * 380 + 10;
            return (
              <circle
                key={`surplus-${index}`}
                cx={x}
                cy="185"
                r="3"
                fill="#3b82f6"
                className="cursor-pointer"
                onMouseEnter={() => setHoveredYear(point.year)}
              />
            );
          })}
        </svg>

        {/* Tooltip */}
        {hoveredYear && (
          <div className="absolute top-4 left-1/2 transform -translate-x-1/2 bg-white border border-gray-300 rounded-lg p-3 shadow-lg">
            <h4 className="font-bold text-center mb-2">Année {hoveredYear}</h4>
            <div className="text-sm space-y-1">
              <div className="text-red-600">Gain total : {currentData.totalGain} €</div>
              <div className="text-blue-600">Revenus surplus : {currentData.surplus} €</div>
              <div className="text-green-600">Économies : {currentData.savings} €</div>
            </div>
          </div>
        )}
      </div>

      {/* Légende */}
      <div className="flex justify-center space-x-6 text-sm">
        <div className="flex items-center">
          <div className="w-4 h-1 bg-red-500 mr-2"></div>
          <span>Gains cumulés</span>
        </div>
        <div className="flex items-center">
          <div className="w-4 h-1 bg-blue-500 mr-2"></div>
          <span>Revenus surplus</span>
        </div>
      </div>

      <p className="text-xs text-gray-600 text-center mt-4">
        💡 Passez votre souris sur les points pour voir les détails année par année
      </p>
    </div>
  );
};

export default GainsEvolution;