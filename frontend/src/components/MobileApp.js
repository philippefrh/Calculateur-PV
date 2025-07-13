import React from 'react';

const MobileApp = () => {
  return (
    <div>
      <h2 className="text-xl font-bold text-gray-800 mb-6">📱 App Mobile</h2>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Smartphone mockup */}
        <div className="flex justify-center">
          <div className="relative">
            {/* iPhone frame */}
            <div className="w-80 h-[600px] bg-black rounded-[3rem] p-2">
              <div className="w-full h-full bg-gradient-to-b from-teal-300 to-teal-400 rounded-[2.5rem] relative overflow-hidden">
                {/* Status bar */}
                <div className="flex justify-between items-center px-6 py-2 text-black text-sm">
                  <div className="flex space-x-1">
                    <div className="w-1 h-1 bg-black rounded-full"></div>
                    <div className="w-1 h-1 bg-black rounded-full"></div>
                    <div className="w-1 h-1 bg-black rounded-full"></div>
                    <div className="w-1 h-1 bg-black rounded-full"></div>
                    <div className="w-1 h-1 bg-gray-400 rounded-full"></div>
                  </div>
                  <div>2023-05-30 17:18:25</div>
                  <div className="flex space-x-1">
                    <div className="w-6 h-3 border border-black rounded-sm"></div>
                    <div className="text-xs">100%</div>
                  </div>
                </div>

                {/* App header */}
                <div className="text-center py-4">
                  <div className="text-lg font-bold text-black">Capacité</div>
                  <div className="text-sm text-black">6 kW</div>
                </div>

                {/* Sun and clouds */}
                <div className="flex justify-center mb-4">
                  <div className="w-16 h-16 bg-yellow-300 rounded-full flex items-center justify-center text-2xl">☀️</div>
                </div>
                <div className="flex justify-center space-x-2 mb-8">
                  <div className="w-8 h-6 bg-white rounded-full opacity-80"></div>
                  <div className="w-12 h-8 bg-white rounded-full opacity-60"></div>
                  <div className="w-6 h-4 bg-white rounded-full opacity-70"></div>
                </div>

                {/* Production indicator */}
                <div className="text-center mb-8">
                  <div className="inline-block bg-white bg-opacity-20 rounded-full px-6 py-3">
                    <div className="text-3xl font-bold text-black">3.11 W</div>
                    <div className="text-sm text-black opacity-80">Production actuelle</div>
                  </div>
                </div>

                {/* House illustration */}
                <div className="flex justify-center mb-6">
                  <div className="relative">
                    {/* House */}
                    <div className="w-32 h-20 bg-green-500 rounded-lg relative">
                      {/* Roof */}
                      <div className="absolute -top-4 left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-[32px] border-r-[32px] border-b-[16px] border-l-transparent border-r-transparent border-b-green-600"></div>
                      {/* Solar panels on roof */}
                      <div className="absolute -top-2 left-1/2 transform -translate-x-1/2 w-20 h-3 bg-blue-800 rounded"></div>
                      {/* Door */}
                      <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 w-6 h-12 bg-green-700 rounded-t"></div>
                      {/* Windows */}
                      <div className="absolute top-2 left-2 w-4 h-4 bg-yellow-200 rounded"></div>
                      <div className="absolute top-2 right-2 w-4 h-4 bg-yellow-200 rounded"></div>
                    </div>
                  </div>
                </div>

                {/* Stats */}
                <div className="px-6 space-y-3">
                  <div className="bg-white bg-opacity-20 rounded-lg p-3 flex justify-between">
                    <span className="text-black text-sm">Aujourd'hui</span>
                    <span className="text-black font-bold">32.94 kWh</span>
                  </div>
                  <div className="bg-white bg-opacity-20 rounded-lg p-3 flex justify-between">
                    <span className="text-black text-sm">Ce mois-ci</span>
                    <span className="text-black font-bold">7.86 kWh</span>
                  </div>
                  <div className="bg-white bg-opacity-20 rounded-lg p-3 flex justify-between">
                    <span className="text-black text-sm">Total</span>
                    <span className="text-black font-bold">7.86 kWh</span>
                  </div>
                </div>

                {/* Bottom navigation */}
                <div className="absolute bottom-6 left-6 right-6 flex justify-around">
                  <div className="text-center">
                    <div className="w-8 h-8 bg-white bg-opacity-30 rounded-full mb-1"></div>
                    <div className="text-xs text-black">🔄</div>
                  </div>
                  <div className="text-center">
                    <div className="w-8 h-8 bg-white bg-opacity-30 rounded-full mb-1"></div>
                    <div className="text-xs text-black">📊</div>
                  </div>
                  <div className="text-center">
                    <div className="w-8 h-8 bg-white bg-opacity-30 rounded-full mb-1"></div>
                    <div className="text-xs text-black">🏠</div>
                  </div>
                  <div className="text-center">
                    <div className="w-8 h-8 bg-white bg-opacity-30 rounded-full mb-1"></div>
                    <div className="text-xs text-black">⚙️</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* App description */}
        <div className="space-y-6">
          <div>
            <h3 className="text-2xl font-bold text-green-600 mb-4">SUIVEZ VOTRE PRODUCTION EN TEMPS RÉEL</h3>
            
            <h4 className="text-lg font-medium text-gray-800 mb-3">
              Votre production et consommation solaire en direct via <span className="text-blue-600 font-bold">notre appli</span>
            </h4>
            
            <div className="space-y-4 text-gray-700">
              <p>
                Nous offrons à nos clients une expérience transparente et pratique grâce à notre application dédiée, qui leur 
                permet de contrôler la production de leurs panneaux solaires directement depuis leur smartphone.
              </p>
              
              <p>
                Cette application intuitive fournit des informations en temps réel sur la production d'énergie, ainsi que des 
                données détaillées sur toute la durée depuis l'installation.
              </p>
              
              <p>
                Vous pouvez suivre de près les performances de vos panneaux solaires. Vous avez le contrôle total de votre 
                système solaire à portée de main, offrant une gestion pratique et efficace de votre production d'énergie 
                solaire.
              </p>
            </div>
          </div>

          {/* Features */}
          <div className="bg-green-50 p-6 rounded-lg">
            <h4 className="font-bold text-green-800 mb-4">✨ Fonctionnalités de l'application :</h4>
            <div className="space-y-3">
              <div className="flex items-start">
                <div className="w-2 h-2 bg-green-500 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                <span className="text-sm text-green-700">Suivi production en temps réel (kWh produits)</span>
              </div>
              <div className="flex items-start">
                <div className="w-2 h-2 bg-green-500 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                <span className="text-sm text-green-700">Historique détaillé par jour, mois, année</span>
              </div>
              <div className="flex items-start">
                <div className="w-2 h-2 bg-green-500 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                <span className="text-sm text-green-700">Alertes en cas de dysfonctionnement</span>
              </div>
              <div className="flex items-start">
                <div className="w-2 h-2 bg-green-500 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                <span className="text-sm text-green-700">Calcul des économies réalisées en €</span>
              </div>
              <div className="flex items-start">
                <div className="w-2 h-2 bg-green-500 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                <span className="text-sm text-green-700">Interface intuitive et moderne</span>
              </div>
            </div>
          </div>

          {/* Download buttons */}
          <div className="flex space-x-4">
            <div className="bg-black text-white px-6 py-3 rounded-lg text-center flex-1">
              <div className="text-xs">Télécharger sur</div>
              <div className="font-bold">App Store</div>
            </div>
            <div className="bg-green-600 text-white px-6 py-3 rounded-lg text-center flex-1">
              <div className="text-xs">Télécharger sur</div>
              <div className="font-bold">Google Play</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MobileApp;