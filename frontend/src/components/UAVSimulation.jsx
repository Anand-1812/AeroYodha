import React from "react";
import { useSimulation } from "./simulation/useSimulation";
import Controls from "./controls/Controls";
import UAVMap from "./map/UAVMap";

const UAVSimulation = () => {
  const sim = useSimulation();
  const { uavs, geofences, running, setRunning, stop, refreshData } = sim;

  return (
    <div style={{ height: "100vh", display: "flex"}}>
        <div style={{ flex: 1 }}>
        <UAVMap uavs={uavs} geofences={geofences} />
      </div>
      <Controls
        running={running}
        setRunning={setRunning}
        stop={stop}
        refreshData={refreshData}
        uavs={uavs}
      />
      
    </div>
  );
};

export default UAVSimulation;
