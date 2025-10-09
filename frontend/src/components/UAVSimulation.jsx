import React, { useState } from "react";
import Controls from "./controls/Controls";
import BasicMap from "./map/UAVMap";

export default function UAVSimulation() {
  const [running, setRunning] = useState(false);
  const [uavs, setUavs] = useState([]);
  const [uavCount, setUavCount] = useState(1);

  const generateRandomUavs = (count = 1) => {
    const arr = Array.from({ length: count }).map((_, i) => ({
      id: i,
      speed: 80 + Math.random() * 50,
      trajectory: Array.from({ length: 30 }).map((_, j) => [
        Math.random() * 30,
        Math.random() * 30,
      ]),
    }));
    setUavs(arr);
  };

  const handleAddUavs = () => generateRandomUavs(Number(uavCount));
  const refreshData = () => generateRandomUavs(uavCount);
  const stop = () => {
    setRunning(false);
    setUavs([]);
  };

  return (
    <div className="container-fluid p-0" style={{ height: "100vh" }}>
      <div className="row g-0" style={{ height: "100%" }}>
        {/* Map Section */}
        <div className="col-12 col-lg-9" style={{ height: "100%" }}>
          <BasicMap running={running} uavs={uavs} />
        </div>

        {/* Controls Section (static, full height) */}
        <div
          className="col-12 col-lg-3"
          style={{
            height: "100vh",
            overflowY: "auto",
            padding: "12px",
          }}
        >
          <Controls
            running={running}
            setRunning={setRunning}
            stop={stop}
            refreshData={refreshData}
            uavs={uavs}
            uavCount={uavCount}
            setUavCount={setUavCount}
            handleAddUavs={handleAddUavs}
          />
        </div>
      </div>
    </div>
  );
}
