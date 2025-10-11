import React, { useState, useEffect } from "react";
import Controls from "./controls/Controls";
import BasicMap from "./map/UAVMap";

export default function UAVSimulation() {
  const [running, setRunning] = useState(false);
  const [uavs, setUavs] = useState([]);
  const [uavCount, setUavCount] = useState(0);
  const [noFlyZones, setNoFlyZones] = useState([]);
  const [data, setData] = useState(null);
  const [city, setCity] = useState(""); // Current city or location
  const [mapCenter, setMapCenter] = useState([20.5937, 78.9629]); // Default center (India)

  // ✅ Utility to filter UAV paths that collide with no-fly zones
  const filterUavPaths = (uavs, noFlyZones) => {
    const nfSet = new Set(noFlyZones.map(([r, c]) => `${r},${c}`));
    return uavs.map((uav) => ({
      ...uav,
      path: uav.path.filter(([r, c]) => !nfSet.has(`${r},${c}`)),
    }));
  };

  // Load initial UAV data from API
  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/v1/uavs/steps");
      if (!res.ok) throw new Error("Failed to fetch UAV data");
      const json = await res.json();

      console.log("✅ Full API response:", json.docs[0]);

      setData(json);
      const snapshot = json.docs[0];

      console.log("🟢 Snapshot ------>", snapshot);
      console.log("📌 UAVs:", snapshot.uavs || []);
      console.log("🚫 No-Fly Zones:", snapshot.noFlyZones || []);

      // Filter UAV paths to avoid no-fly zones 🚫✈️
      const filteredUavs = filterUavPaths(snapshot.uavs || [], snapshot.noFlyZones || []);

      // Optional: log UAV paths after filtering
      filteredUavs.forEach((uav) => {
        console.log(`✅ Safe path for UAV ${uav.id}:`, uav.path);
      });

      setNoFlyZones(snapshot.noFlyZones || []);
      setUavs(filteredUavs);
      setUavCount(filteredUavs.length || 0);
    } catch (err) {
      console.error("Error loading UAV data:", err);
    }
  };

  const handleStart = () => setRunning(true);
  const stop = () => setRunning(false);

  const refreshData = () => {
    if (!data) return;
    const snapshot = data.docs ? data.docs[0] : data;
    const filteredUavs = filterUavPaths(snapshot.uavs || [], snapshot.noFlyZones || []);
    setNoFlyZones(snapshot.noFlyZones || []);
    setUavs(filteredUavs);
  };

  // 🔍 Handle location search + full reset
  const handleLocationSearch = async (cityName) => {
    if (!cityName.trim()) return;
    setCity(cityName);

    try {
      const response = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${cityName}`
      );
      const results = await response.json();

      if (results.length > 0) {
        const { lat, lon } = results[0];
        const newCenter = [parseFloat(lat), parseFloat(lon)];
        setMapCenter(newCenter);

        // 🧭 Reset entire system at new location
        setRunning(false);
        setUavs([]);
        setUavCount(0);
        setNoFlyZones([]);
        setData(null);

        // Reload API data
        loadInitialData();

        console.log(`✅ Map reset to ${cityName}:`, newCenter);
      } else {
        alert("Location not found. Try another city name.");
      }
    } catch (err) {
      console.error("Error finding location:", err);
    }
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
            city={city}
            mapCenter={mapCenter}
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
            handleLocationSearch={handleLocationSearch}
          />
        </div>
      </div>
    </div>
  );
}
