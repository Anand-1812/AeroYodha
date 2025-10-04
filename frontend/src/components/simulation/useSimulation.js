import { useState, useEffect } from "react";

// --- UAV MODEL ---
export class UAV {
  constructor(id, lat, lng, path = []) {
    this.id = id;
    this.lat = lat;
    this.lng = lng;
    this.path = path.length ? path : [[lat, lng]];
  }

  update() {
    // Example drift update (simulates motion)
    const dx = (Math.random() - 0.5) * 0.001;
    const dy = (Math.random() - 0.5) * 0.001;
    this.lat += dx;
    this.lng += dy;
    this.path.push([this.lat, this.lng]);
  }
}

const DEFAULT_CENTER = { lat: 28.6139, lng: 77.209 }; // Delhi-ish

// --- Mock API fetchers ---
const mockFetchUAVs = () => {
  return [
    new UAV(1, DEFAULT_CENTER.lat, DEFAULT_CENTER.lng, [
      [DEFAULT_CENTER.lat, DEFAULT_CENTER.lng],
    ]),
  ];
};

// --- Hook ---
export const useSimulation = () => {
  const [uavs, setUavs] = useState([]);
  const [running, setRunning] = useState(false);

  // initial data fetch
  useEffect(() => {
    setUavs(mockFetchUAVs());
  }, []);

  // main loop (simulate UAV updates if running)
  useEffect(() => {
    if (!running) return;
    const interval = setInterval(() => {
      setUavs((prev) => {
        prev.forEach((u) => u.update());
        return [...prev];
      });
    }, 1000);
    return () => clearInterval(interval);
  }, [running]);

  return {
    uavs,
    setRunning,
  };
};
