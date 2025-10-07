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
    <div style={{ display: "flex", flexDirection: "column", height: "100vh" }}>
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
      <div style={{ flex: 1 }}>
        <BasicMap running={running} uavs={uavs} />
      </div>
    </div>
  );
}
