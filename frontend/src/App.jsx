import React, { useState } from 'react';
import CanvasView from './components/CanvasView';
import Controls from './components/Controls';
import Dashboard from './components/Dashboard';
import PriorityQueue from './components/PriorityQueue';
import { useSocket } from './hooks/useSocket';
import './index.css';

function App() {
  const { uavs, obstacles, geofences, paths, alerts } = useSocket();
  const [scenario, setScenario] = useState('urban');

  const handleAddUAV = () => {
    // Emit to back-end or add locally
  };

  const handleSwitchScenario = (e) => setScenario(e.target.value);

  return (
    <>
      <CanvasView uavs={uavs} obstacles={obstacles} geofences={geofences} paths={paths} />
      <Controls onAddUAV={handleAddUAV} onSwitchScenario={handleSwitchScenario} />
      <Dashboard uavs={uavs} alerts={alerts} />
      <PriorityQueue uavs={uavs} />
    </>
  );
}

export default App;