import React, { useState } from 'react';

const MonitoringInterface = () => {
  const [activeView, setActiveView] = useState('overview');

  return (
    <div>
      <h2 className="text-xl font-bold text-gray-800 mb-6">📈 Monitoring 2025</h2>
      
      {/* Copie exacte de l'interface MyEnlighten/Envoy */}
      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        {/* Header de navigation */}
        <div className="bg-gray-50 px-6 py-3 border-b flex space-x-8">
          <button 
            onClick={() => setActiveView('overview')}
            className={`font-medium ${activeView === 'overview' ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-600'}`}
          >
            Overview
          </button>
          <button 
            onClick={() => setActiveView('production')}
            className={`font-medium ${activeView === 'production' ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-600'}`}
          >
            Production
          </button>
          <button 
            onClick={() => setActiveView('consumption')}
            className={`font-medium ${activeView === 'consumption' ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-600'}`}
          >
            Consommation
          </button>
          <button 
            onClick={() => setActiveView('reports')}
            className={`font-medium ${activeView === 'reports' ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-600'}`}
          >
            Reports
          </button>
        </div>

        {/* Interface principale */}
        <div className="p-6">
          {/* Header avec date et météo */}
          <div className="flex justify-between items-center mb-8">
            <div className="flex items-center space-x-4">
              <button className="text-gray-400 hover:text-gray-600">‹</button>
              <h3 className="text-xl font-bold text-blue-600">Jeudi 8 Avril 2021</h3>
              <button className="text-gray-400 hover:text-gray-600">›</button>
            </div>
            <div className="flex items-center space-x-2 text-gray-600">
              <span className="text-2xl">🌤️</span>
              <span className="font-medium">70°F Partly Cloudy</span>
            </div>
          </div>

          {/* Métriques principales */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Colonne gauche - Métriques */}
            <div className="space-y-6">
              <div className="flex items-center space-x-4">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center">
                  <div className="w-10 h-10 bg-blue-500 rounded-sm flex items-center justify-center">
                    <div className="w-8 h-6 bg-blue-600 rounded-sm"></div>
                  </div>
                </div>
                <div>
                  <div className="text-3xl font-bold text-gray-800">24.22</div>
                  <div className="text-gray-600">
                    <span className="font-medium">kilowatt-hours produced</span>
                    <span className="ml-2">›</span>
                  </div>
                  <div className="text-sm text-gray-500">Approximately 18.14 kWh exported to grid</div>
                </div>
              </div>

              <div className="flex items-center space-x-4">
                <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center">
                  <div className="w-8 h-8 bg-red-500 rounded-full flex items-center justify-center">
                    <div className="w-4 h-4 bg-red-600 rounded-full"></div>
                  </div>
                </div>
                <div>
                  <div className="text-3xl font-bold text-gray-800">16.66</div>
                  <div className="text-gray-600">
                    <span className="font-medium">kilowatt-hours consumed</span>
                  </div>
                  <div className="text-sm text-gray-500">Approximately 10.57 kWh imported from grid</div>
                </div>
              </div>

              <div className="flex items-center space-x-4">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center">
                  <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold">+</div>
                </div>
                <div>
                  <div className="text-3xl font-bold text-gray-800">7.50</div>
                  <div className="text-gray-600">
                    <span className="font-medium">kilowatt-hours net energy exported</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Colonne droite - Panneaux solaires */}
            <div>
              <div className="mb-4">
                <h4 className="font-medium text-gray-700 mb-2">array 1</h4>
                <div className="grid grid-cols-6 gap-1">
                  {Array.from({ length: 12 }, (_, i) => (
                    <div key={i} className="bg-teal-400 text-white text-xs p-2 rounded text-center">
                      <div className="font-bold">{(1.74 + Math.random() * 0.1).toFixed(2)}</div>
                      <div className="text-xs">kWh</div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="text-right">
                <div className="text-6xl font-bold text-gray-300">0</div>
                <div className="text-lg text-gray-600">Wh</div>
                <div className="text-lg text-gray-600 mt-4">27.3</div>
                <div className="text-sm text-gray-500">kWh</div>
              </div>

              <div className="mt-6 bg-gray-100 p-4 rounded-lg">
                <div className="text-center">
                  <div className="text-sm text-gray-600 mb-2">Jeudi 8 Avril 2021</div>
                  <div className="text-sm text-gray-600">10:45 PM</div>
                  <div className="mt-2">
                    <span className="text-red-600 font-bold">Net Energy</span>
                    <br />
                    <span className="text-red-600 text-lg">-191 Wh</span>
                  </div>
                  <div className="flex justify-center mt-2 space-x-4">
                    <div className="flex items-center">
                      <div className="w-3 h-3 bg-teal-400 mr-1"></div>
                      <span className="text-xs">Produced</span>
                      <span className="text-xs ml-1">0 Wh</span>
                    </div>
                    <div className="flex items-center">
                      <div className="w-3 h-3 bg-red-400 mr-1"></div>
                      <span className="text-xs">Consumed</span>
                      <span className="text-xs ml-1">191 Wh</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Graphique de production quotidienne */}
          <div className="mt-8">
            <div className="h-40 bg-gray-50 rounded-lg relative overflow-hidden">
              {/* Graphique en aires */}
              <svg className="absolute inset-0 w-full h-full" viewBox="0 0 800 160">
                {/* Zone de production (bleu-vert) */}
                <path
                  d="M 0 160 L 50 150 L 100 140 L 150 120 L 200 100 L 250 80 L 300 60 L 350 40 L 400 30 L 450 40 L 500 60 L 550 80 L 600 100 L 650 120 L 700 140 L 750 150 L 800 160 L 800 160 L 0 160 Z"
                  fill="url(#blueGradient)"
                />
                
                {/* Zone de consommation (rouge) */}
                <path
                  d="M 0 160 L 50 155 L 100 150 L 150 145 L 200 140 L 250 145 L 300 150 L 350 155 L 400 160 L 450 155 L 500 150 L 550 145 L 600 140 L 650 145 L 700 150 L 750 155 L 800 160 L 800 160 L 0 160 Z"
                  fill="url(#redGradient)"
                />

                <defs>
                  <linearGradient id="blueGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" style={{stopColor: '#0891b2', stopOpacity: 0.8}} />
                    <stop offset="100%" style={{stopColor: '#0891b2', stopOpacity: 0.3}} />
                  </linearGradient>
                  <linearGradient id="redGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" style={{stopColor: '#dc2626', stopOpacity: 0.8}} />
                    <stop offset="100%" style={{stopColor: '#dc2626', stopOpacity: 0.3}} />
                  </linearGradient>
                </defs>
              </svg>

              {/* Axes et labels */}
              <div className="absolute bottom-2 left-4 text-xs text-gray-500">-320 Wh</div>
              <div className="absolute bottom-2 left-1/2 transform -translate-x-1/2 text-xs text-gray-500">320 Wh</div>
              <div className="absolute bottom-2 right-4 text-xs text-gray-500">640 Wh</div>
              <div className="absolute top-2 left-4 text-xs text-gray-500">640 Wh</div>
              <div className="absolute top-2 right-4 text-xs text-gray-500">0 Wh</div>
            </div>
          </div>

          {/* Footer avec logos */}
          <div className="mt-8 pt-6 border-t flex justify-center space-x-8 text-gray-600">
            <div className="font-bold">MyEnlighten</div>
            <div className="border-l border-gray-300"></div>
            <div className="font-bold">Envoy</div>
          </div>
        </div>
      </div>

      {/* Note explicative */}
      <div className="mt-6 bg-blue-50 border-l-4 border-blue-500 p-4">
        <h4 className="font-bold text-blue-800 mb-2">📊 Interface de monitoring en temps réel</h4>
        <p className="text-sm text-blue-700">
          Cette interface vous permet de suivre en temps réel la production et la consommation de votre installation solaire. 
          Vous pouvez visualiser les performances de chaque panneau individuellement et analyser vos données sur différentes périodes.
        </p>
      </div>
    </div>
  );
};

export default MonitoringInterface;