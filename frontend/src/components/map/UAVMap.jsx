import React, { useState, useEffect } from "react";
import {
  MapContainer,
  TileLayer,
  Popup,
  Rectangle,
  CircleMarker,
} from "react-leaflet";
import L from "leaflet";
import ReactLeafletDriftMarker from "react-leaflet-drift-marker";
import herodrone from "../../assets/hero-drone.png";

// === Rectangle bounds ===
const rectangle1 = [
  [28.6188961, 77.2103825],
  [28.6078898, 77.2267138],
];

const rectangle2 = [
  [28.52, 77.16],
  [28.56, 77.2],
];

// === Utility: Convert N{row}_{col} → [lat, lon] ===
function matrixToDelhiCoords(row, col, matrixSize = 30) {
  const [lat1, lon1] = rectangle1[0];
  const [lat2, lon2] = rectangle1[1];

  row = Math.max(0, Math.min(matrixSize - 1, row));
  col = Math.max(0, Math.min(matrixSize - 1, col));

  const lat = lat1 + (row / (matrixSize - 1)) * (lat2 - lat1);
  const lon = lon1 + (col / (matrixSize - 1)) * (lon2 - lon1);

  return [lat, lon];
}

// === Utility: Haversine distance in meters ===
function getDistance(lat1, lon1, lat2, lon2) {
  const R = 6371e3;
  const φ1 = (lat1 * Math.PI) / 180;
  const φ2 = (lat2 * Math.PI) / 180;
  const Δφ = ((lat2 - lat1) * Math.PI) / 180;
  const Δλ = ((lon2 - lon1) * Math.PI) / 180;
  const a =
    Math.sin(Δφ / 2) ** 2 +
    Math.cos(φ1) * Math.cos(φ2) * Math.sin(Δλ / 2) ** 2;
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}

// === UAV icon ===
const uavIcon = new L.Icon({
  iconUrl: herodrone,
  iconSize: [40, 40],
  iconAnchor: [20, 40],
  popupAnchor: [0, -40],
});

// === UAV COMPONENT (follows predefined path) ===
function UAV({ id, path, speed }) {
  const [index, setIndex] = useState(0);
  const [latlng, setLatlng] = useState(() => {
    const [r, c] = path[0].match(/\d+/g).map(Number);
    return matrixToDelhiCoords(r, c);
  });
  const [duration, setDuration] = useState(0);

  useEffect(() => {
    if (index >= path.length - 1) return; // reached destination

    const [r1, c1] = path[index].match(/\d+/g).map(Number);
    const [r2, c2] = path[index + 1].match(/\d+/g).map(Number);
    const [lat1, lon1] = matrixToDelhiCoords(r1, c1);
    const [lat2, lon2] = matrixToDelhiCoords(r2, c2);

    const dist = getDistance(lat1, lon1, lat2, lon2);
    const speedMs = speed; // already in m/s
    const time = (dist / speedMs) * 1000; // ms

    setLatlng([lat2, lon2]);
    setDuration(time);

    const timer = setTimeout(() => setIndex((prev) => prev + 1), time);
    return () => clearTimeout(timer);
  }, [index, path, speed]);

  return (
    <ReactLeafletDriftMarker position={latlng} duration={duration} icon={uavIcon}>
      <Popup>
        UAV {id}
        <br />
        Speed: {speed.toFixed(2)} m/s
        <br />
        Waypoint {index + 1}/{path.length}
      </Popup>
    </ReactLeafletDriftMarker>
  );
}

// === MOCK DATA ===
const mockData = {
  uavs: [
    {
      id: 0,
      start: "N2_26",
      goal: "N17_10",
      speed: 100,
      path: [
        "N2_26",
        "N2_25",
        "N2_24",
        "N3_24",
        "N3_23",
        "N4_23",
        "N4_22",
        "N5_22",
        "N5_21",
        "N6_21",
        "N6_20",
        "N7_20",
        "N7_19",
        "N8_19",
        "N8_18",
        "N9_18",
        "N9_17",
        "N10_17",
        "N10_16",
        "N11_16",
        "N11_15",
        "N12_15",
        "N12_14",
        "N13_14",
        "N13_13",
        "N14_13",
        "N14_12",
        "N15_12",
        "N15_11",
        "N16_11",
        "N16_10",
        "N17_10",
        "N30_20",
      ],
    },
  ],
};

// === MAIN MAP ===
export default function BasicMap() {
  const matrixSize = 30;
  const rectangleOptions = { color: "black" };

  return (
    <div style={{ height: "100vh", width: "100%" }}>
      <MapContainer
        center={[28.6133825, 77.21849369]}
        zoom={16}
        style={{ height: "100%", width: "100%" }}
        zoomControl={false}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution="&copy; OpenStreetMap contributors"
        />

        {/* UAVs following their path */}
        {mockData.uavs.map((uav) => (
          <UAV key={uav.id} {...uav} />
        ))}

        {/* Geofences */}
        <Rectangle bounds={rectangle1} pathOptions={rectangleOptions} />
        <Rectangle bounds={rectangle2} pathOptions={rectangleOptions} />

        {/* Render matrix points (optional visual grid) */}
        {Array.from({ length: matrixSize }).map((_, r) =>
          Array.from({ length: matrixSize }).map((_, c) => {
            const [lat, lon] = matrixToDelhiCoords(r, c, matrixSize);
            return (
              <CircleMarker
                key={`${r}-${c}`}
                center={[lat, lon]}
                radius={0.1}
                color="red"
                fillOpacity={0.0}
              />
            );
          })
        )}
      </MapContainer>
    </div>
  );
}
