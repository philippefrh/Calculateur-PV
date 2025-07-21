import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';

const SolarAnimation3D = ({ panelCount = 12, onBack }) => {
  const mountRef = useRef(null);
  const sceneRef = useRef(null);
  const rendererRef = useRef(null);
  const cameraRef = useRef(null);
  const panelsRef = useRef([]);
  const inverterRef = useRef(null);
  const appRef = useRef(null);
  
  const [animationStage, setAnimationStage] = useState('panels'); // 'panels', 'inverter', 'app', 'complete'
  const [currentPanelIndex, setCurrentPanelIndex] = useState(0);

  useEffect(() => {
    if (!mountRef.current) return;

    // Initialiser la scène 3D
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x87CEEB); // Ciel bleu
    
    // Caméra
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.set(0, 5, 10);
    camera.lookAt(0, 0, 0);
    
    // Renderer
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    mountRef.current.appendChild(renderer.domElement);
    
    // Lumières
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);
    
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(10, 10, 5);
    directionalLight.castShadow = true;
    directionalLight.shadow.mapSize.width = 2048;
    directionalLight.shadow.mapSize.height = 2048;
    scene.add(directionalLight);

    // Sol
    const groundGeometry = new THREE.PlaneGeometry(50, 50);
    const groundMaterial = new THREE.MeshLambertMaterial({ color: 0x90EE90 });
    const ground = new THREE.Mesh(groundGeometry, groundMaterial);
    ground.rotation.x = -Math.PI / 2;
    ground.receiveShadow = true;
    scene.add(ground);

    // Stocker les références
    sceneRef.current = scene;
    rendererRef.current = renderer;
    cameraRef.current = camera;

    // Fonction d'animation
    const animate = () => {
      requestAnimationFrame(animate);
      
      // Rotation des panneaux qui apparaissent
      panelsRef.current.forEach((panel, index) => {
        if (panel && index <= currentPanelIndex) {
          panel.rotation.y += 0.02; // Rotation continue
        }
      });

      // Rotation de l'onduleur
      if (inverterRef.current && animationStage === 'inverter') {
        inverterRef.current.rotation.y += 0.03;
      }

      // Rotation de l'application
      if (appRef.current && animationStage === 'app') {
        appRef.current.rotation.y += 0.02;
      }

      renderer.render(scene, camera);
    };
    animate();

    // Démarrer l'animation des panneaux
    startPanelAnimation();

    // Nettoyage
    return () => {
      if (mountRef.current && renderer.domElement) {
        mountRef.current.removeChild(renderer.domElement);
      }
      renderer.dispose();
    };
  }, []);

  const createPanelTexture = () => {
    // Création de la texture du panneau avec l'image fournie
    const canvas = document.createElement('canvas');
    canvas.width = 512;
    canvas.height = 256;
    const ctx = canvas.getContext('2d');
    
    // Fond noir mat (comme votre photo de panneau)
    ctx.fillStyle = '#1a1a1a';
    ctx.fillRect(0, 0, 512, 256);
    
    // Lignes de cellules photovoltaïques
    ctx.strokeStyle = '#333333';
    ctx.lineWidth = 2;
    
    // Grille 3x6 comme un vrai panneau
    for (let i = 1; i < 6; i++) {
      ctx.beginPath();
      ctx.moveTo(i * (512/6), 0);
      ctx.lineTo(i * (512/6), 256);
      ctx.stroke();
    }
    
    for (let j = 1; j < 3; j++) {
      ctx.beginPath();
      ctx.moveTo(0, j * (256/3));
      ctx.lineTo(512, j * (256/3));
      ctx.stroke();
    }

    // Cadre aluminium
    ctx.strokeStyle = '#888888';
    ctx.lineWidth = 6;
    ctx.strokeRect(0, 0, 512, 256);

    return new THREE.CanvasTexture(canvas);
  };

  const createInverterTexture = () => {
    // Création de la texture de l'onduleur
    const canvas = document.createElement('canvas');
    canvas.width = 256;
    canvas.height = 256;
    const ctx = canvas.getContext('2d');
    
    // Fond gris clair (comme votre onduleur Hoymiles)
    ctx.fillStyle = '#e0e0e0';
    ctx.fillRect(0, 0, 256, 256);
    
    // Logo Hoymiles (approximation)
    ctx.fillStyle = '#2ecc71';
    ctx.font = 'bold 20px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('Hoymiles', 128, 40);
    
    // Connecteurs (rectangles noirs)
    ctx.fillStyle = '#000000';
    ctx.fillRect(50, 80, 30, 15);
    ctx.fillRect(176, 80, 30, 15);
    ctx.fillRect(50, 160, 30, 15);
    ctx.fillRect(176, 160, 30, 15);
    
    // LED verte (statut)
    ctx.fillStyle = '#00ff00';
    ctx.beginPath();
    ctx.arc(128, 128, 5, 0, Math.PI * 2);
    ctx.fill();

    return new THREE.CanvasTexture(canvas);
  };

  const createAppTexture = () => {
    // Création de la texture de l'application
    const canvas = document.createElement('canvas');
    canvas.width = 256;
    canvas.height = 512;
    const ctx = canvas.getContext('2d');
    
    // Fond d'écran mobile (noir)
    ctx.fillStyle = '#000000';
    ctx.fillRect(0, 0, 256, 512);
    
    // Interface de l'app (approximation de votre capture)
    ctx.fillStyle = '#1e3a5f';
    ctx.fillRect(10, 50, 236, 400);
    
    // Titre
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 16px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('Solar Monitor', 128, 80);
    
    // Données de production
    ctx.font = '24px Arial';
    ctx.fillText('27.32 kWh', 128, 120);
    ctx.font = '12px Arial';
    ctx.fillText('Solar generation', 128, 140);
    
    ctx.font = '24px Arial';
    ctx.fillText('30.02 kWh', 128, 180);
    ctx.font = '12px Arial';
    ctx.fillText('Consumption', 128, 200);
    
    // Graphique (rectangle vert)
    ctx.fillStyle = '#2ecc71';
    ctx.fillRect(30, 250, 196, 100);
    
    // Boutons
    ctx.fillStyle = '#4a90e2';
    ctx.fillRect(30, 370, 60, 30);
    ctx.fillRect(166, 370, 60, 30);
    
    ctx.fillStyle = '#ffffff';
    ctx.font = '10px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('Solar', 60, 387);
    ctx.fillText('Grid', 196, 387);

    return new THREE.CanvasTexture(canvas);
  };

  const startPanelAnimation = () => {
    const panelTexture = createPanelTexture();
    
    // Calculer la disposition des panneaux
    const panelsPerRow = panelCount <= 6 ? 3 : panelCount <= 12 ? 4 : 6;
    const rows = Math.ceil(panelCount / panelsPerRow);
    
    // Créer chaque panneau
    for (let i = 0; i < panelCount; i++) {
      setTimeout(() => {
        const row = Math.floor(i / panelsPerRow);
        const col = i % panelsPerRow;
        
        // Géométrie du panneau
        const panelGeometry = new THREE.BoxGeometry(2, 0.1, 1);
        const panelMaterial = new THREE.MeshLambertMaterial({ map: panelTexture });
        const panel = new THREE.Mesh(panelGeometry, panelMaterial);
        
        // Position initiale (au-dessus, invisible)
        panel.position.set(
          (col - panelsPerRow/2 + 0.5) * 2.5,  // X: espacement horizontal
          10,                                    // Y: haut dans le ciel
          (row - rows/2 + 0.5) * 1.5            // Z: espacement vertical
        );
        
        // Position finale
        const finalY = 0.05;
        const finalPosition = {
          x: (col - panelsPerRow/2 + 0.5) * 2.5,
          y: finalY,
          z: (row - rows/2 + 0.5) * 1.5
        };
        
        panel.castShadow = true;
        panel.receiveShadow = true;
        sceneRef.current.add(panel);
        panelsRef.current[i] = panel;
        
        // Animation de chute et rotation
        const startTime = Date.now();
        const duration = 2000; // 2 secondes
        
        const animatePanel = () => {
          const elapsed = Date.now() - startTime;
          const progress = Math.min(elapsed / duration, 1);
          
          // Easing (rebond)
          const easeProgress = progress < 0.5 
            ? 2 * progress * progress 
            : 1 - Math.pow(-2 * progress + 2, 3) / 2;
          
          // Position
          panel.position.y = 10 + (finalPosition.y - 10) * easeProgress;
          
          // Rotation spectaculaire
          panel.rotation.x = Math.sin(progress * Math.PI * 4) * 0.5;
          panel.rotation.z = Math.sin(progress * Math.PI * 6) * 0.3;
          
          if (progress < 1) {
            requestAnimationFrame(animatePanel);
          } else {
            panel.rotation.x = 0;
            panel.rotation.z = 0;
          }
        };
        
        animatePanel();
        setCurrentPanelIndex(i);
        
        // Si c'est le dernier panneau, passer à l'onduleur
        if (i === panelCount - 1) {
          setTimeout(() => {
            setAnimationStage('inverter');
            showInverter();
          }, 2500);
        }
      }, i * 500); // Délai entre chaque panneau
    }
  };

  const showInverter = () => {
    const inverterTexture = createInverterTexture();
    
    // Géométrie de l'onduleur (boîtier rectangulaire)
    const inverterGeometry = new THREE.BoxGeometry(1.5, 0.8, 0.3);
    const inverterMaterial = new THREE.MeshLambertMaterial({ map: inverterTexture });
    const inverter = new THREE.Mesh(inverterGeometry, inverterMaterial);
    
    // Position à droite des panneaux
    inverter.position.set(8, 5, 0);
    inverter.castShadow = true;
    inverter.receiveShadow = true;
    
    sceneRef.current.add(inverter);
    inverterRef.current = inverter;
    
    // Animation d'apparition avec rotation
    const startTime = Date.now();
    const duration = 2000;
    
    const animateInverter = () => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / duration, 1);
      
      // Descente
      inverter.position.y = 5 + (0.5 - 5) * progress;
      
      // Rotation spectaculaire
      inverter.rotation.y = progress * Math.PI * 4;
      inverter.rotation.x = Math.sin(progress * Math.PI * 3) * 0.5;
      
      if (progress < 1) {
        requestAnimationFrame(animateInverter);
      } else {
        inverter.rotation.x = 0;
        setTimeout(() => {
          setAnimationStage('app');
          showApp();
        }, 1000);
      }
    };
    
    animateInverter();
  };

  const showApp = () => {
    const appTexture = createAppTexture();
    
    // Géométrie du téléphone
    const phoneGeometry = new THREE.BoxGeometry(0.8, 1.6, 0.1);
    const phoneMaterial = new THREE.MeshLambertMaterial({ map: appTexture });
    const phone = new THREE.Mesh(phoneGeometry, phoneMaterial);
    
    // Position à gauche
    phone.position.set(-8, 5, 0);
    phone.castShadow = true;
    phone.receiveShadow = true;
    
    sceneRef.current.add(phone);
    appRef.current = phone;
    
    // Animation d'apparition
    const startTime = Date.now();
    const duration = 2000;
    
    const animateApp = () => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / duration, 1);
      
      // Descente
      phone.position.y = 5 + (1 - 5) * progress;
      
      // Rotation
      phone.rotation.y = progress * Math.PI * 3;
      phone.rotation.z = Math.sin(progress * Math.PI * 2) * 0.3;
      
      if (progress < 1) {
        requestAnimationFrame(animateApp);
      } else {
        phone.rotation.z = 0;
        setAnimationStage('complete');
      }
    };
    
    animateApp();
  };

  return (
    <div style={{ position: 'relative', width: '100vw', height: '100vh', overflow: 'hidden' }}>
      <div ref={mountRef} style={{ width: '100%', height: '100%' }} />
      
      {/* Interface overlay */}
      <div style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        background: 'linear-gradient(180deg, rgba(0,0,0,0.8) 0%, rgba(0,0,0,0) 50%)',
        padding: '20px',
        color: 'white',
        textAlign: 'center'
      }}>
        <h1 style={{ margin: 0, fontSize: '2em', textShadow: '2px 2px 4px rgba(0,0,0,0.8)' }}>
          🎬 Votre Installation Solaire 3D
        </h1>
        <p style={{ fontSize: '1.2em', textShadow: '1px 1px 2px rgba(0,0,0,0.8)' }}>
          {animationStage === 'panels' && `Installation des panneaux... (${currentPanelIndex + 1}/${panelCount})`}
          {animationStage === 'inverter' && 'Installation de l\'onduleur Hoymiles...'}
          {animationStage === 'app' && 'Connexion de l\'application de monitoring...'}
          {animationStage === 'complete' && 'Installation terminée ! ✅'}
        </p>
      </div>

      {/* Bouton de retour */}
      <button
        onClick={onBack}
        style={{
          position: 'absolute',
          bottom: '30px',
          right: '30px',
          backgroundColor: 'rgba(46, 204, 113, 0.9)',
          color: 'white',
          border: 'none',
          padding: '15px 25px',
          borderRadius: '50px',
          fontSize: '16px',
          fontWeight: 'bold',
          cursor: 'pointer',
          boxShadow: '0 4px 15px rgba(46, 204, 113, 0.4)',
          backdropFilter: 'blur(10px)'
        }}
      >
        ← Retour aux Résultats
      </button>

      {/* Contrôles de caméra */}
      <div style={{
        position: 'absolute',
        bottom: '30px',
        left: '30px',
        color: 'white',
        fontSize: '14px',
        textShadow: '1px 1px 2px rgba(0,0,0,0.8)'
      }}>
        💡 Déplacez la souris pour regarder autour
      </div>
    </div>
  );
};

export default SolarAnimation3D;