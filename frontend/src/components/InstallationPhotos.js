import React, { useState } from 'react';

const InstallationPhotos = () => {
  const [selectedPhoto, setSelectedPhoto] = useState(0);

  // Photos d'installation professionnelles
  const installationPhotos = [
    {
      id: 1,
      title: "Installation sur toiture méditerranéenne",
      description: "Panneaux solaires parfaitement intégrés sur tuiles traditionnelles",
      image: "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCABgAGADASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUWEHInGBEzKRobHBCNHwUnLxFSJicpKS4fL/AABLAVnVkAAAWRiTw=="
    },
    {
      id: 2,
      title: "Configuration optimale sur toiture",
      description: "Disposition stratégique pour maximiser la production",
      image: "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCABgAGADASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUWEHInGBEzKRobHBCNHwUnLxFSJicpKS4fL/AABLAVnVkAAAWRiTw=="
    },
    {
      id: 3,
      title: "Installation en cours par nos techniciens",
      description: "Équipe certifiée RGE à l'œuvre",
      image: "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCABgAGADASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAxQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUWEHInGBEzKRobHBCNHwUnLxFSJicpKS4fL/AABLAVnVkAAAWRiTw=="
    },
    {
      id: 4,
      title: "Panneaux haute performance",
      description: "Technologie de pointe pour rendement optimal",
      image: "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCABgAGADASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUWEHInGBEzKRobHBCNHwUnLxFSJicpKS4fL/AABLAVnVkAAAWRiTw=="
    },
    {
      id: 5,
      title: "Installation finale professionnelle",
      description: "Résultat final soigné et esthétique",
      image: "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCABgAGADASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUWEHInGBEzKRobHBCNHwUnLxFSJicpKS4fL/AABLAVnVkAAAWRiTw=="
    }
  ];

  const currentPhoto = installationPhotos[selectedPhoto];

  return (
    <div>
      <h2 className="text-xl font-bold text-gray-800 mb-6">🔧 Installation</h2>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Photo principale */}
        <div>
          <div className="bg-gray-200 rounded-lg overflow-hidden mb-4 h-80">
            <div className="w-full h-full bg-gradient-to-br from-blue-400 via-blue-500 to-orange-400 flex items-center justify-center">
              <div className="text-center text-white">
                <div className="text-6xl mb-4">📸</div>
                <h3 className="text-xl font-bold mb-2">{currentPhoto.title}</h3>
                <p className="text-sm opacity-90">{currentPhoto.description}</p>
              </div>
            </div>
          </div>

          {/* Thumbnails */}
          <div className="grid grid-cols-5 gap-2">
            {installationPhotos.map((photo, index) => (
              <button
                key={photo.id}
                onClick={() => setSelectedPhoto(index)}
                className={`aspect-square rounded-lg overflow-hidden border-2 transition-all ${
                  selectedPhoto === index ? 'border-orange-500 ring-2 ring-orange-200' : 'border-gray-300'
                }`}
              >
                <div className="w-full h-full bg-gradient-to-br from-blue-300 to-orange-300 flex items-center justify-center text-white text-xs">
                  {index + 1}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Explication technique */}
        <div className="space-y-6">
          <div>
            <h3 className="text-lg font-bold text-gray-800 mb-4">🔧 Comment se fixent les panneaux sur votre toiture</h3>
            
            <div className="space-y-4">
              <div className="bg-blue-50 p-4 rounded-lg">
                <h4 className="font-bold text-blue-800 mb-2">1. Étude préalable</h4>
                <p className="text-sm text-blue-700">
                  Analyse de la charpente, orientation et inclinaison de votre toiture pour optimiser l'installation.
                </p>
              </div>

              <div className="bg-green-50 p-4 rounded-lg">
                <h4 className="font-bold text-green-800 mb-2">2. Fixation sécurisée</h4>
                <p className="text-sm text-green-700">
                  Utilisation de crochets de toiture adaptés au type de couverture (tuiles, ardoises, bac acier).
                </p>
              </div>

              <div className="bg-orange-50 p-4 rounded-lg">
                <h4 className="font-bold text-orange-800 mb-2">3. Rails de montage</h4>
                <p className="text-sm text-orange-700">
                  Installation de rails en aluminium pour supporter les panneaux de manière uniforme.
                </p>
              </div>

              <div className="bg-purple-50 p-4 rounded-lg">
                <h4 className="font-bold text-purple-800 mb-2">4. Étanchéité garantie</h4>
                <p className="text-sm text-purple-700">
                  Mise en place de joints d'étanchéité sous chaque point de fixation.
                </p>
              </div>

              <div className="bg-red-50 p-4 rounded-lg">
                <h4 className="font-bold text-red-800 mb-2">5. Pose des panneaux</h4>
                <p className="text-sm text-red-700">
                  Fixation des panneaux sur les rails avec système de serrage optimisé.
                </p>
              </div>
            </div>
          </div>

          {/* Garanties */}
          <div className="bg-gray-50 p-6 rounded-lg">
            <h4 className="font-bold text-gray-800 mb-4">🛡️ Nos garanties installation</h4>
            <div className="space-y-3">
              <div className="flex items-center">
                <div className="w-3 h-3 bg-green-500 rounded-full mr-3"></div>
                <span className="text-sm text-gray-700">Installation certifiée RGE QualiPV</span>
              </div>
              <div className="flex items-center">
                <div className="w-3 h-3 bg-green-500 rounded-full mr-3"></div>
                <span className="text-sm text-gray-700">Garantie étanchéité 10 ans</span>
              </div>
              <div className="flex items-center">
                <div className="w-3 h-3 bg-green-500 rounded-full mr-3"></div>
                <span className="text-sm text-gray-700">Assurance décennale MMA</span>
              </div>
              <div className="flex items-center">
                <div className="w-3 h-3 bg-green-500 rounded-full mr-3"></div>
                <span className="text-sm text-gray-700">Respect des normes DTU 43.11</span>
              </div>
              <div className="flex items-center">
                <div className="w-3 h-3 bg-green-500 rounded-full mr-3"></div>
                <span className="text-sm text-gray-700">Équipe formée et expérimentée</span>
              </div>
            </div>
          </div>

          {/* Micro onduleur */}
          <div className="bg-gray-800 text-white p-6 rounded-lg">
            <h4 className="font-bold mb-4">⚡ Micro onduleur haute performance</h4>
            <div className="flex items-center space-x-4">
              <div className="w-16 h-12 bg-blue-600 rounded flex items-center justify-center">
                <div className="w-12 h-8 bg-blue-500 rounded border border-blue-400 flex items-center justify-center text-xs">
                  LCD
                </div>
              </div>
              <div className="flex-1">
                <p className="text-sm text-gray-300">
                  Chaque panneau est équipé d'un micro-onduleur pour optimiser la production individuelle 
                  et permettre un monitoring précis.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InstallationPhotos;