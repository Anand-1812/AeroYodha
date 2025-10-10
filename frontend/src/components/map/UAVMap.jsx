import React, { useState, useEffect } from "react";
import {
  MapContainer,
  TileLayer,
  Popup,
  Rectangle,
  CircleMarker,
  Marker,
  Polyline,
  useMap,
} from "react-leaflet";
import L from "leaflet";
import ReactLeafletDriftMarker from "react-leaflet-drift-marker";
import herodrone from "../../assets/hero-drone.png";
import otherdrone from "../../assets/hero-drone-red.png"; // <-- New marker for first drone

// === Rectangle bounds ===
const rectangle1 = [
  [28.6188961, 77.2103825],
  [28.6078898, 77.2267138],
];

const rectangle2 = [
  [28.52, 77.16],
  [28.56, 77.2],
];

// === Utility: Convert matrix coordinates to city coordinates (dynamic center) ===
function matrixToCityCoords(row, col, center = [28.6139, 77.2090], matrixSize = 30) {
  const [baseLat, baseLon] = center;
  const latOffset = (row - matrixSize / 2) * 0.001; // scale grid to ~3km box
  const lonOffset = (col - matrixSize / 2) * 0.001;
  return [baseLat + latOffset, baseLon + lonOffset];
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

// === UAV COMPONENT (smooth movement + glowing fading path) ===
function UAV({ id, trajectory, speed, running, isHero, center }) {
  const [index, setIndex] = useState(0);
  const [latlng, setLatlng] = useState(() => {
    const [r, c] = trajectory[0];
    return matrixToCityCoords(r, c, center);
  });
  const [duration, setDuration] = useState(0);
  const [pathTaken, setPathTaken] = useState([latlng]);

  // Different color for each UAV trail
  const colors = ["#ff4d00ff", "#ff4d00ff", "#ffb300ff", "#80ff00ff", "#3700ffff"];
  const color = colors[id % colors.length];

  // Icon: hero UAV gets a different marker
  const icon = new L.Icon({
    iconUrl: isHero ? otherdrone : herodrone,
    iconSize: [40, 40],
    iconAnchor: [20, 40],
    popupAnchor: [0, -40],
  });

  useEffect(() => {
    if (!running) return;
    if (index >= trajectory.length - 1) return;

    const [r1, c1] = trajectory[index];
    const [r2, c2] = trajectory[index + 1];
    const [lat1, lon1] = matrixToCityCoords(r1, c1, center);
    const [lat2, lon2] = matrixToCityCoords(r2, c2, center);

    const dist = getDistance(lat1, lon1, lat2, lon2);
    const time = (dist / speed) * 1000;

    setLatlng([lat2, lon2]);
    setDuration(time);

    const timer = setTimeout(() => {
      setPathTaken((prev) => [...prev.slice(-30), [lat2, lon2]]);
      setIndex((p) => p + 1);
    }, time);

    return () => clearTimeout(timer);
  }, [index, running, trajectory, speed, center]);

  // Fading trail segments
  const fadingSegments = pathTaken.map((_, i, arr) => {
    if (i === arr.length - 1) return null;
    const opacity = (i + 1) / arr.length;
    return (
      <Polyline
        key={i}
        positions={[arr[i], arr[i + 1]]}
        pathOptions={{
          color,
          weight: 4,
          opacity,
          smoothFactor: 1,
        }}
      />
    );
  });

  return (
    <>
      {fadingSegments}
      <ReactLeafletDriftMarker position={latlng} duration={duration} icon={icon}>
        <Popup>
          UAV {id} <br />
          Speed: {speed.toFixed(2)} m/s <br />
          Waypoint {index + 1}/{trajectory.length}
        </Popup>
      </ReactLeafletDriftMarker>
    </>
  );
}

// === Random geofence generator ===
function generateRandomGeofences(center, matrixSize, count = 3) {
  const geofences = [];
  for (let i = 0; i < count; i++) {
    const r1 = Math.floor(Math.random() * matrixSize);
    const c1 = Math.floor(Math.random() * matrixSize);
    const r2 = r1 + Math.floor(Math.random() * 10) + 1;
    const c2 = c1 + Math.floor(Math.random() * 10) + 1;

    const [lat1, lon1] = matrixToCityCoords(r1, c1, center, matrixSize);
    const [lat2, lon2] = matrixToCityCoords(
      Math.min(r2, matrixSize - 1),
      Math.min(c2, matrixSize - 1),
      center,
      matrixSize
    );

    geofences.push([
      [lat1, lon1],
      [lat2, lon2],
    ]);
  }
  return geofences;
}

// === Move map to searched city ===
function MapMover({ city, onCenterUpdate }) {
  const map = useMap();

  useEffect(() => {
    if (!city) return;

    const fetchCoords = async () => {
      try {
        const res = await fetch(
          `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(city)}`
        );
        const data = await res.json();
        if (data && data.length > 0) {
          const { lat, lon } = data[0];
          const newCenter = [parseFloat(lat), parseFloat(lon)];
          map.flyTo(newCenter, 12, { duration: 2 });
          onCenterUpdate(newCenter); // tell parent to reset drones/zones
        } else {
          alert("City not found. Try another name.");
        }
      } catch (err) {
        console.error("Geocoding error:", err);
      }
    };

    fetchCoords();
  }, [city, map, onCenterUpdate]);

  return null;
}

// === MAIN MAP ===
export default function BasicMap({ running, uavs, noFlyZones = [], city }) {
  const matrixSize = 30;
  const rectangleOptions = { color: "black" };
  const [geofences, setGeofences] = useState([]);
  const [center, setCenter] = useState([28.6133825, 77.21849369]); // default Delhi

  // generate fences around current center
  useEffect(() => {
    setGeofences(generateRandomGeofences(center, matrixSize, 4));
  }, [center]);

  // rebuild UAVs whenever center changes (full reset)
  const resetUAVs = uavs.map((uav) => ({
    ...uav,
    path: uav.path.map(([r, c]) => [r, c]), // keep structure, new coords handled inside UAV
  }));

  const heroUAV = resetUAVs.length > 0 ? resetUAVs[0] : null;
  const startPos = heroUAV ? matrixToCityCoords(...heroUAV.path[0], center) : null;
  const endPos =
    heroUAV && heroUAV.path.length > 1
      ? matrixToCityCoords(...heroUAV.path[heroUAV.path.length - 1], center)
      : null;

  return (
    <div style={{ height: "100vh", width: "100%" }}>
      <MapContainer
        center={center}
        zoom={16}
        style={{ height: "100%", width: "100%" }}
        zoomControl={true}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution="&copy; OpenStreetMap contributors"
        />

        {/* City mover */}
        <MapMover city={city} onCenterUpdate={setCenter} />

        {resetUAVs.map((uav, idx) => (
          <UAV
            key={uav.id}
            id={uav.id}
            trajectory={uav.path}
            speed={10 + Math.random() * 5}
            running={running}
            isHero={idx === 0}
            center={center}
          />
        ))}

        {startPos && (
          <Marker position={startPos}>
            <Popup>Hero UAV Start</Popup>
          </Marker>
        )}
        {endPos && (
          <Marker position={endPos}>
            <Popup>Hero UAV Destination</Popup>
          </Marker>
        )}

        <Rectangle bounds={rectangle1} pathOptions={rectangleOptions} />
        {/* <Rectangle bounds={rectangle2} pathOptions={rectangleOptions} />
        {geofences.map((bounds, idx) => (
          <Rectangle key={idx} bounds={bounds} pathOptions={{ color: "red" }} />
        ))} */}

        {Array.from({ length: matrixSize }).map((_, r) =>
          Array.from({ length: matrixSize }).map((_, c) => {
            const [lat, lon] = matrixToCityCoords(r, c, center, matrixSize);
            // return (
            //   <CircleMarker
            //     key={`${r}-${c}`}
            //     center={[lat, lon]}
            //     radius={0.1}
            //     color="red"
            //     fillOpacity={0.0}
            //   />
            // );
          })
        )}
      </MapContainer>
    </div>
  );
}
