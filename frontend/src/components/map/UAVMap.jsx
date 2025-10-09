import React, { useState, useEffect } from "react";
import {
  MapContainer,
  TileLayer,
  Popup,
  Rectangle,
  CircleMarker,
  Marker,
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

// === Utility: Convert matrix coordinates to Delhi coordinates ===
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

// === UAV COMPONENT (smooth movement using trajectory) ===
function UAV({ id, trajectory, speed, running }) {
  const [index, setIndex] = useState(0);
  const [latlng, setLatlng] = useState(() => {
    const [r, c] = trajectory[0];
    return matrixToDelhiCoords(r, c);
  });
  const [duration, setDuration] = useState(0);

  useEffect(() => {
    if (!running) return; // paused
    if (index >= trajectory.length - 1) return; // reached end

    const [r1, c1] = trajectory[index];
    const [r2, c2] = trajectory[index + 1];
    const [lat1, lon1] = matrixToDelhiCoords(r1, c1);
    const [lat2, lon2] = matrixToDelhiCoords(r2, c2);

    const dist = getDistance(lat1, lon1, lat2, lon2);
    const time = (dist / speed) * 1000;

    setLatlng([lat2, lon2]);
    setDuration(time);

    const timer = setTimeout(() => setIndex((p) => p + 1), time);
    return () => clearTimeout(timer);
  }, [index, running, trajectory, speed]);

  return (
    <ReactLeafletDriftMarker position={latlng} duration={duration} icon={uavIcon}>
      <Popup>
        UAV {id} <br />
        Speed: {speed.toFixed(2)} m/s <br />
        Waypoint {index + 1}/{trajectory.length}
      </Popup>
    </ReactLeafletDriftMarker>
  );
}

// === Random geofence generator ===
function generateRandomGeofences(matrixSize, count = 3) {
  const geofences = [];
  for (let i = 0; i < count; i++) {
    const r1 = Math.floor(Math.random() * matrixSize);
    const c1 = Math.floor(Math.random() * matrixSize);
    const r2 = r1 + Math.floor(Math.random() * 10) + 1;
    const c2 = c1 + Math.floor(Math.random() * 10) + 1;

    const [lat1, lon1] = matrixToDelhiCoords(r1, c1, matrixSize);
    const [lat2, lon2] = matrixToDelhiCoords(
      Math.min(r2, matrixSize - 1),
      Math.min(c2, matrixSize - 1),
      matrixSize
    );

    geofences.push([
      [lat1, lon1],
      [lat2, lon2],
    ]);
  }
  return geofences;
}

// === MAIN MAP ===
export default function BasicMap({ running, uavs, noFlyZones = [] }) {
  const matrixSize = 30;
  const rectangleOptions = { color: "black" };
  const [geofences, setGeofences] = useState([]);

  useEffect(() => {
    setGeofences(generateRandomGeofences(matrixSize, 4));
  }, []);

  // Pick a random UAV to show start and end
  const randomUAV = uavs[Math.floor(Math.random() * uavs.length)];
  const startPos = randomUAV ? matrixToDelhiCoords(...randomUAV.path[0]) : null;
  const endPos =
    randomUAV && randomUAV.path.length > 1
      ? matrixToDelhiCoords(...randomUAV.path[randomUAV.path.length - 1])
      : null;

  // Convert noFlyZones from data into Delhi coordinates
  const zoneRects = noFlyZones.map(([r, c]) => {
    const [lat1, lon1] = matrixToDelhiCoords(r, c, matrixSize);
    const [lat2, lon2] = matrixToDelhiCoords(r + 1, c + 1, matrixSize);
    return [
      [lat1, lon1],
      [lat2, lon2],
    ];
  });

  return (
    <div style={{ height: "100vh", width: "100%" }}>
      <MapContainer
        center={[28.6133825, 77.21849369]}
        zoom={16}
        style={{ height: "100%", width: "100%" }}
        zoomControl={true}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution="&copy; OpenStreetMap contributors"
        />

        {/* UAVs */}
        {uavs.map((uav) => (
          <UAV
            key={uav.id}
            trajectory={uav.path} // using real path from data
            speed={80 + Math.random() * 50} // keep speed
            running={running}
          />
        ))}

        {/* Show start and end for random UAV */}
        {startPos && (
          <Marker position={startPos}>
            <Popup>Random UAV Start</Popup>
          </Marker>
        )}
        {endPos && (
          <Marker position={endPos}>
            <Popup>Random UAV Destination</Popup>
          </Marker>
        )}

        {/* Static & Random Geofences */}
        <Rectangle bounds={rectangle1} pathOptions={rectangleOptions} />
        <Rectangle bounds={rectangle2} pathOptions={rectangleOptions} />
        {geofences.map((bounds, idx) => (
          <Rectangle key={idx} bounds={bounds} pathOptions={{ color: "red" }} />
        ))}

        {/* No-Fly Zones from data */}
        {/* {zoneRects.map((bounds, idx) => (
          <Rectangle
            key={`zone-${idx}`}
            bounds={bounds}
            pathOptions={{ color: "orange", fillOpacity: 0.4 }}
          />
        ))} */}

        {/* Optional Grid */}
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
