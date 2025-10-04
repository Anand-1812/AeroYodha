import { useState, useEffect, useRef } from "react";

// --- UAV MODEL (updated)
export class UAV {
  constructor(id, lat, lng, priority = false, path = []) {
    this.id = id;
    this.lat = lat;
    this.lng = lng;
    this.priority = priority;
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

// --- Helper to generate random paths ---
const generateRandomPath = (startLat, startLng, numPoints = 3) => {
  const path = [[startLat, startLng]];
  for (let i = 1; i < numPoints; i++) {
    const dx = (Math.random() - 0.5) * 0.02; // small random movement
    const dy = (Math.random() - 0.5) * 0.02;
    const last = path[path.length - 1];
    path.push([last[0] + dx, last[1] + dy]);
  }
  return path;
};

// --- Mock API fetchers ---
const mockFetchUAVs = () => {
  const count = 5 + Math.floor(Math.random() * 5); // 5–10 UAVs
  const list = [];
  for (let i = 1; i <= count; i++) {
    const lat = DEFAULT_CENTER.lat + (Math.random() - 0.5) * 2;
    const lng = DEFAULT_CENTER.lng + (Math.random() - 0.5) * 2;
    const path = generateRandomPath(lat, lng, 3 + Math.floor(Math.random() * 3)); // 3–5 waypoints
    list.push(new UAV(i, lat, lng, i === 1, path)); // first UAV is priority
  }
  return list;
};

const mockFetchGeofences = () => {
  const count = 2 + Math.floor(Math.random() * 2); // 2–3 geofences
  const polys = [];
  for (let i = 0; i < count; i++) {
    const cx = DEFAULT_CENTER.lat + (Math.random() - 0.5) * 2;
    const cy = DEFAULT_CENTER.lng + (Math.random() - 0.5) * 2;
    const radius = 0.2 + Math.random() * 0.3;
    const points = [];
    const segments = 10;
    for (let s = 0; s < segments; s++) {
      const angle = (s / segments) * Math.PI * 2;
      points.push([cx + Math.cos(angle) * radius, cy + Math.sin(angle) * radius]);
    }
    polys.push(points);
  }
  return polys;
};

// --- Hook ---
export const useSimulation = () => {
  const [uavs, setUavs] = useState([]);
  const [geofences, setGeofences] = useState([]);
  const [running, setRunning] = useState(false);
  const rafRef = useRef(null);

  // initial data fetch
  useEffect(() => {
    setUavs(mockFetchUAVs());
    setGeofences(mockFetchGeofences());
  }, []);

  // main loop (simulate UAV updates if running)
  useEffect(() => {
    if (!running) return;
    const loop = () => {
      setUavs((prev) => {
        prev.forEach((u) => u.update());
        return [...prev];
      });
      rafRef.current = requestAnimationFrame(loop);
    };
    rafRef.current = requestAnimationFrame(loop);
    return () => cancelAnimationFrame(rafRef.current);
  }, [running]);

  const refreshData = () => {
    setUavs(mockFetchUAVs());
    setGeofences(mockFetchGeofences());
  };

  const stop = () => {
    setRunning(false);
    if (rafRef.current) cancelAnimationFrame(rafRef.current);
  };

  return {
    uavs,
    geofences,
    running,
    setRunning,
    stop,
    refreshData,
  };
};
