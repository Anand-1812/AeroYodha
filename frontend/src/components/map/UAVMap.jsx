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
function UAV({ id, trajectory, speed }) {
  const [index, setIndex] = useState(0);
  const [latlng, setLatlng] = useState(() => {
    const [r, c] = trajectory[0];
    return matrixToDelhiCoords(r, c);
  });
  const [duration, setDuration] = useState(0);

  useEffect(() => {
    if (index >= trajectory.length - 1) return; // reached end of trajectory

    const [r1, c1] = trajectory[index];
    const [r2, c2] = trajectory[index + 1];
    const [lat1, lon1] = matrixToDelhiCoords(r1, c1);
    const [lat2, lon2] = matrixToDelhiCoords(r2, c2);

    const dist = getDistance(lat1, lon1, lat2, lon2);
    const time = (dist / speed) * 1000; // duration in ms

    setLatlng([lat2, lon2]);
    setDuration(time);

    const timer = setTimeout(() => setIndex((prev) => prev + 1), time);
    return () => clearTimeout(timer);
  }, [index, trajectory, speed]);

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
function generateRandomGeofences(matrixSize, count = 3) {
  const geofences = [];
  for (let i = 0; i < count; i++) {
    const r1 = Math.floor(Math.random() * matrixSize);
    const c1 = Math.floor(Math.random() * matrixSize);
    const r2 = r1 + Math.floor(Math.random() * 10) + 1; // random rectangle size
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

// === MOCK DATA ===
const mockData = {
  uavs: [
    {
      id: 0,
      start: "N2_26",
      goal: "N17_10",
      speed: 100,
      trajectory: [
        [2.0,26.0],[2.0,25.605059782962673],[2.0,25.210119565925346],[2.0,25.0],[2.0,24.605059782962673],[2.0,24.210119565925346],[2.0,24.0],[2.3949402170373277,24.0],[2.7898804340746555,24.0],[3.0,24.0],[3.0,23.605059782962673],[3.0,23.210119565925346],[3.0,23.0],[3.3949402170373277,23.0],[3.7898804340746555,23.0],[4.0,23.0],[4.0,22.605059782962673],[4.0,22.210119565925346],[4.0,22.0],[4.394940217037328,22.0],[4.7898804340746555,22.0],[5.0,22.0],[5.0,21.605059782962673],[5.0,21.210119565925346],[5.0,21.0],[5.394940217037328,21.0],[5.7898804340746555,21.0],[6.0,21.0],[6.0,20.605059782962673],[6.0,20.210119565925346],[6.0,20.0],[6.394940217037328,20.0],[6.7898804340746555,20.0],[7.0,20.0],[7.0,19.605059782962673],[7.0,19.210119565925346],[7.0,19.0],[7.394940217037328,19.0],[7.7898804340746555,19.0],[8.0,19.0],[8.0,18.605059782962673],[8.0,18.210119565925346],[8.0,18.0],[8.394940217037329,18.0],[8.789880434074657,18.0],[9.0,18.0],[9.0,17.605059782962673],[9.0,17.210119565925346],[9.0,17.0],[9.394940217037329,17.0],[9.789880434074657,17.0],[10.0,17.0],[10.0,16.605059782962673],[10.0,16.210119565925346],[10.0,16.0],[10.394940217037329,16.0],[10.789880434074657,16.0],[11.0,16.0],[11.0,15.605059782962671],[11.0,15.210119565925343],[11.0,15.0],[11.394940217037329,15.0],[11.789880434074657,15.0],[12.0,15.0],[12.0,14.605059782962671],[12.0,14.210119565925343],[12.0,14.0],[12.394940217037329,14.0],[12.789880434074657,14.0],[13.0,14.0],[13.0,13.605059782962671],[13.0,13.210119565925343],[13.0,13.0],[13.394940217037329,13.0],[13.789880434074657,13.0],[14.0,13.0],[14.0,12.605059782962671],[14.0,12.210119565925343],[14.0,12.0],[14.394940217037329,12.0],[14.789880434074657,12.0],[15.0,12.0],[15.0,11.605059782962671],[15.0,11.210119565925343],[15.0,11.0],[15.394940217037329,11.0],[15.789880434074657,11.0],[16.0,11.0],[16.0,10.605059782962671],[16.0,10.210119565925343],[16.0,10.0],[16.394940217037327,10.0],[16.789880434074654,10.0],[17.0,10.0]
      ]
    }
  ]
};

// === MAIN MAP ===
export default function BasicMap() {
  const matrixSize = 30;
  const rectangleOptions = { color: "black" };

  const [geofences, setGeofences] = useState([]);

  useEffect(() => {
    setGeofences(generateRandomGeofences(matrixSize, 4)); // generate 4 random geofences
  }, []);

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

        {/* UAVs following their trajectory */}
        {mockData.uavs.map((uav) => (
          <UAV key={uav.id} trajectory={uav.trajectory} speed={uav.speed} />
        ))}

        {/* Static Geofences */}
        <Rectangle bounds={rectangle1} pathOptions={rectangleOptions} />
        <Rectangle bounds={rectangle2} pathOptions={rectangleOptions} />

        {/* Random Red Geofences */}
        {geofences.map((bounds, idx) => (
          <Rectangle key={idx} bounds={bounds} pathOptions={{ color: "red" }} />
        ))}

        {/* Optional grid points */}
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
