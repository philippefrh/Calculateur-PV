import React, { useState } from 'react';
import HomePage from './HomePage';
import MultiStepForm from './MultiStepForm';
import Results from './Results';

const SolarCalculator = () => {
  const [currentView, setCurrentView] = useState('home');
  const [formData, setFormData] = useState({});

  const handleStartCalculation = () => {
    setCurrentView('form');
  };

  const handleFormComplete = (data) => {
    setFormData(data);
    setCurrentView('results');
  };

  const handleBackToHome = () => {
    setCurrentView('home');
    setFormData({});
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-400 via-orange-500 to-yellow-500">
      {currentView === 'home' && (
        <HomePage onStartCalculation={handleStartCalculation} />
      )}
      {currentView === 'form' && (
        <MultiStepForm 
          onComplete={handleFormComplete}
          onBack={handleBackToHome}
        />
      )}
      {currentView === 'results' && (
        <Results 
          formData={formData}
          onBack={handleBackToHome}
        />
      )}
    </div>
  );
};

export default SolarCalculator;