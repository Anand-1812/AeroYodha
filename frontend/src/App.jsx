import React, { useState, useEffect } from 'react';
import './index.css';
import 'leaflet/dist/leaflet.css';
import UAVsimulation from './components/UAVSimulation';
import Splash from "./components/splash/splash";

function App() {
  const [showSplash, setShowSplash] = useState(() => {
    return sessionStorage.getItem('splashShown') !== 'true';
  });

  useEffect(() => {
    if (!showSplash) return;
    sessionStorage.setItem('splashShown', 'true');
  }, [showSplash]);

  return (
    <>
      {showSplash ? <Splash onFinish={() => setShowSplash(false)} /> : <UAVsimulation />}
    </>
  );
}

export default App;
