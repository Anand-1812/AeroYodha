import React, { useState, useEffect } from "react";
import Controls from "./controls/Controls";
import BasicMap from "./map/UAVMap";

export default function UAVSimulation() {
  const [running, setRunning] = useState(false);
  const [uavs, setUavs] = useState([]);
  const [uavCount, setUavCount] = useState(0);
  const [noFlyZones, setNoFlyZones] = useState([]);
  const [data, setData] = useState(null);
  const [city, setCity] = useState(""); // <-- added for map search

  // Load the JSON file (place uavdata.json in your /public directory)
  useEffect(() => {
    fetch("/uavdata.json")
      .then((res) => res.json())
      .then((json) => {
        setData(json);
        const snapshot = json.docs[0]; // first frame (step 0)
        setNoFlyZones(snapshot.noFlyZones);
        setUavs(snapshot.uavs);
        setUavCount(snapshot.uavs.length);
      })
      .catch((err) => console.error("Error loading UAV data:", err));
  }, []);

  const handleStart = () => setRunning(true);
  const stop = () => setRunning(false);

  const refreshData = () => {
    if (!data) return;
    const snapshot = data.docs[0];
    setNoFlyZones(snapshot.noFlyZones);
    setUavs(snapshot.uavs);
  };

  // 🔍 Handle city search (from Controls input)
  const handleLocationSearch = (cityName) => {
    setCity(cityName);
  };

  return (
    <div className="container-fluid p-0" style={{ height: "100vh" }}>
      <div className="row g-0" style={{ height: "100%" }}>
        {/* Map Section */}
        <div className="col-12 col-lg-9" style={{ height: "100%" }}>
          <BasicMap
            running={running}
            uavs={uavs}
            noFlyZones={noFlyZones}
            city={city} // <-- added for dynamic map movement
          />
        </div>

        {/* Controls Section */}
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
            handleAddUavs={() => {}}
            handleStart={handleStart}
            handleLocationSearch={handleLocationSearch} // <-- new prop for location input
          />
        </div>
      </div>
    </div>
  );
}
