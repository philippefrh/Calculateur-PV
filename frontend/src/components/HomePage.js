import React from 'react';

const HomePage = ({ onStartCalculation }) => {
  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full">
        {/* Logo FRH ENVIRONNEMENT */}
        <div className="text-center mb-6">
          <img 
            src="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCABgAGADASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUWEHInGBEzKRobHBCNHwUnLxFSJicpKS4fL/AABLAVnVkAAAWRiTw=="
            alt="FRH ENVIRONNEMENT" 
            className="mx-auto h-16 w-auto mb-4"
          />
          <h1 className="text-2xl font-bold text-gray-800 mb-2">Installateur Photovoltaïque</h1>
          <p className="text-gray-600 text-sm">FRH ENVIRONNEMENT - Énergie Solaire Professionnel</p>
        </div>

        {/* Statistiques */}
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div className="text-center">
            <div className="text-green-600 font-bold text-lg">+ de 5000</div>
            <div className="text-xs text-gray-500">Installations réalisées</div>
          </div>
          <div className="text-center">
            <div className="text-green-600 font-bold text-lg">86%</div>
            <div className="text-xs text-gray-500">de clients très satisfaits</div>
          </div>
        </div>

        {/* Indicateurs d'autonomie */}
        <div className="space-y-3 mb-6">
          <div className="bg-red-500 text-white px-4 py-2 rounded-lg flex justify-between items-center">
            <span className="text-sm font-medium">POURCENTAGE D'AUTONOMIE DE COULEUR ROUGE</span>
            <span className="bg-red-600 px-2 py-1 rounded text-xs">Négatif</span>
          </div>
          <div className="bg-green-500 text-white px-4 py-2 rounded-lg flex justify-between items-center">
            <span className="text-sm font-medium">POURCENTAGE D'AUTONOMIE DE COULEUR VERT</span>
            <span className="bg-green-600 px-2 py-1 rounded text-xs">Positif</span>
          </div>
        </div>

        {/* Certifications */}
        <div className="text-center mb-6">
          <div className="grid grid-cols-3 gap-2 mb-3">
            <div className="bg-blue-600 text-white px-2 py-1 rounded text-xs font-medium">RGE QualiPV 2025</div>
            <div className="bg-purple-600 text-white px-2 py-1 rounded text-xs font-medium">RGE QualiPac 2025</div>
            <div className="bg-blue-500 text-white px-2 py-1 rounded text-xs font-medium">FFB Adhérent</div>
          </div>
          <div className="bg-green-600 text-white px-3 py-1 rounded text-xs font-medium inline-block">
            Partenaire AGIR PLUS EDF
          </div>
        </div>

        {/* Garantie */}
        <div className="text-center mb-6">
          <div className="flex justify-center items-center space-x-2 mb-2">
            <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold text-sm">M</div>
            <div className="w-8 h-8 bg-green-600 rounded-full flex items-center justify-center text-white font-bold text-sm">M</div>
            <div className="w-8 h-8 bg-orange-600 rounded-full flex items-center justify-center text-white font-bold text-sm">A</div>
          </div>
          <h3 className="font-bold text-gray-800 mb-1">Décennale</h3>
          <p className="text-sm text-gray-600">Toutes nos installations bénéficient d'une garantie de 10 ans.</p>
        </div>

        {/* Bouton principal */}
        <button
          onClick={onStartCalculation}
          className="w-full bg-gradient-to-r from-orange-500 to-red-500 text-white font-bold py-3 px-6 rounded-full hover:from-orange-600 hover:to-red-600 transition-all duration-300 shadow-lg"
        >
          Commencer l'Étude Solaire Gratuite
        </button>

        {/* Avantages */}
        <div className="mt-6 space-y-2">
          <div className="flex items-center text-sm text-gray-700">
            <div className="w-4 h-4 bg-green-500 rounded-full mr-3 flex-shrink-0"></div>
            <span>Réalisez jusqu'à 70% d'économies sur vos factures d'électricité</span>
          </div>
          <div className="flex items-center text-sm text-gray-700">
            <div className="w-4 h-4 bg-green-500 rounded-full mr-3 flex-shrink-0"></div>
            <span>Un accompagnement de A à Z pour votre projet solaire</span>
          </div>
          <div className="flex items-center text-sm text-gray-700">
            <div className="w-4 h-4 bg-green-500 rounded-full mr-3 flex-shrink-0"></div>
            <span>Partenaire garanti 25 ans et garanties de production</span>
          </div>
          <div className="flex items-center text-sm text-gray-700">
            <div className="w-4 h-4 bg-green-500 rounded-full mr-3 flex-shrink-0"></div>
            <span>Installation fiable et performante par nos installateurs certifiés RGE</span>
          </div>
          <div className="flex items-center text-sm text-gray-700">
            <div className="w-4 h-4 bg-green-500 rounded-full mr-3 flex-shrink-0"></div>
            <span>Profitez des dispositifs d'aides et de subventions</span>
          </div>
        </div>

        {/* Contact */}
        <div className="mt-6 text-center text-xs text-gray-500">
          <p>FRH Environnement - 190 Avenue Jean Lebas 59000 Punhin</p>
          <p>05 16 50 50 16 | contact@frhenvironnement.com</p>
        </div>
      </div>
    </div>
  );
};

export default HomePage;