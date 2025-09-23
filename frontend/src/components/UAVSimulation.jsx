import React from "react";
import { useSimulation } from "./simulation/useSimulation";
import Controls from "./controls/Controls";
import UAVMap from "./map/UAVMap";

const UAVSimulation = () => {
  const sim = useSimulation();
  const { uavs, geofences, running, setRunning, stop, refreshData } = sim;

  return (
  <div className="container-fluid h-100">
    <div className="row h-100 g-0">
      <div className="col-9">
        <UAVMap uavs={uavs} geofences={geofences} />
      </div>
      <div className="col-3">
        <Controls
          running={running}
          setRunning={setRunning}
          stop={stop}
          refreshData={refreshData}
          uavs={uavs}
        />
      </div>
    </div>
  </div>
);
};

export default UAVSimulation;
