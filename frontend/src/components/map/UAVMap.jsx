import React, { useState, useEffect } from "react";
import {
  MapContainer,
  TileLayer,
  Popup,
  Rectangle,
  Marker,
  Polyline,
  useMap,
} from "react-leaflet";
import L from "leaflet";
import ReactLeafletDriftMarker from "react-leaflet-drift-marker";
import herodrone from "../../assets/hero-drone.png";
import otherdrone from "../../assets/hero-drone-red.png";

// === Utility: Convert matrix coordinates to city coordinates ===
function matrixToCityCoords(row, col, center = [28.6139, 77.2090], matrixSize = 30) {
  const [baseLat, baseLon] = center;
  const latOffset = (row - matrixSize / 2) * 0.001;
  const lonOffset = (col - matrixSize / 2) * 0.001;
  return [baseLat + latOffset, baseLon + lonOffset];
}

// === UAV COMPONENT ===
function UAV({ id, trajectory, speed, running, isHero, center }) {
  const [index, setIndex] = useState(0);
  const [latlng, setLatlng] = useState(() => {
    const [r, c] = trajectory[0];
    return matrixToCityCoords(r, c, center);
  });
  const [duration, setDuration] = useState(0);
  const [pathTaken, setPathTaken] = useState([latlng]);

  const colors = ["#ff4d00ff", "#ffb300ff", "#80ff00ff", "#3700ffff"];
  const color = colors[id % colors.length];

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

    const dist = Math.sqrt((lat2 - lat1) ** 2 + (lon2 - lon1) ** 2) * 111000;
    const time = (dist / speed) * 1000;

    setLatlng([lat2, lon2]);
    setDuration(time);

    const timer = setTimeout(() => {
      setPathTaken((prev) => [...prev.slice(-30), [lat2, lon2]]);
      setIndex((p) => p + 1);
    }, time);

    return () => clearTimeout(timer);
  }, [index, running, trajectory, speed, center]);

  const fadingSegments = pathTaken.map((_, i, arr) => {
    if (i === arr.length - 1) return null;
    const opacity = (i + 1) / arr.length;
    return (
      <Polyline
        key={i}
        positions={[arr[i], arr[i + 1]]}
        pathOptions={{ color, weight: 4, opacity, smoothFactor: 1 }}
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
          map.flyTo(newCenter, 16, { duration: 2 });
          onCenterUpdate(newCenter);
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

const dotIcon = new L.DivIcon({
  className: "dot-icon",
  html: "<div style='width:6px; height:6px; background:black; border-radius:50%;'></div>",
  iconSize: [6, 6],
  iconAnchor: [3, 3],
});

export default function BasicMap({ running, uavs, noFlyZones = [], city }) {
  const matrixSize = 30;
  const [geofences, setGeofences] = useState([]);
  const [center, setCenter] = useState([28.6133825, 77.21849369]);
  const [gridPoints, setGridPoints] = useState([]);

  // === Generate geofences ===
  useEffect(() => {
    if (!noFlyZones || noFlyZones.length === 0) return;
    const zoneRects = noFlyZones.map(([r, c]) => {
      const cellSize = 0.001;
      const [lat, lon] = matrixToCityCoords(r, c, center, matrixSize);
      return [
        [lat - cellSize / 2, lon - cellSize / 2],
        [lat + cellSize / 2, lon + cellSize / 2],
      ];
    });
    setGeofences(zoneRects);
  }, [noFlyZones, center]);

  //=== Generate 30x30 matrix grid ===
  useEffect(() => {
    const points = [];
    for (let r = 0; r < matrixSize; r++) {
      for (let c = 0; c < matrixSize; c++) {
        points.push(matrixToCityCoords(r, c, center, matrixSize));
      }
    }
    setGridPoints(points);
  }, [center]);

  const resetUAVs = uavs.map((uav) => ({
    ...uav,
    path: uav.path.map(([r, c]) => [r, c]),
  }));

  const heroUAV = resetUAVs.length > 0 ? resetUAVs[0] : null;
  const startPos = heroUAV ? matrixToCityCoords(...heroUAV.path[0], center) : null;
  const endPos =
    heroUAV && heroUAV.path.length > 1
      ? matrixToCityCoords(...heroUAV.path[heroUAV.path.length - 1], center)
      : null;

  return (
    <div style={{ height: "100vh", width: "100%" }}>
      <MapContainer center={center} zoom={14} style={{ height: "100%", width: "100%" }}>
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution="&copy; OpenStreetMap contributors"
        />

        <MapMover city={city} onCenterUpdate={setCenter} />

        {/* UAVs */}
        {resetUAVs.map((uav, idx) => (
          <UAV
            key={`${uav.id}-${center[0]}-${center[1]}`}
            id={uav.id}
            trajectory={uav.path}
            speed={50 + Math.random() * 5}
            running={running}
            isHero={idx === 0}
            center={center}
          />
        ))}

        {/* Start & End markers */}
        {startPos && <Marker position={startPos}><Popup>Hero UAV Start</Popup></Marker>}
        {endPos && <Marker position={endPos}><Popup>Hero UAV Destination</Popup></Marker>}

        {/* Geofences */}
        {geofences.map((bounds, idx) => (
          <Rectangle
            key={idx}
            bounds={bounds}
            pathOptions={{ color: "red", fillColor: "red", fillOpacity: 0.3 }}
          />
        ))}

        {/* ✅ Matrix grid dots */}
        {/* {gridPoints.map((pos, idx) => (
          <Marker key={idx} position={pos} icon={dotIcon} />
        ))} */}
      </MapContainer>
    </div>
  );
}
