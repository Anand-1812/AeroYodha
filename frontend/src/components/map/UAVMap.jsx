import React, { useState } from "react";
import {
  MapContainer,
  TileLayer,
  Popup,
  Rectangle,
  CircleMarker,
} from "react-leaflet";
import L from "leaflet";
import herodrone from "../../assets/hero-drone.png";
import ReactLeafletDriftMarker from "react-leaflet-drift-marker";

// Rectangle bounds
const rectangle1 = [
  [28.6188961, 77.2103825], // top-left
  [28.6078898, 77.2267138], // bottom-right
];

const rectangle2 = [
  [28.52, 77.16],
  [28.56, 77.2],
];

// Generate random UAV position inside rectangle
function gen_position() {
  const [lat1, lng1] = rectangle1[0];
  const [lat2, lng2] = rectangle1[1];

  const minLat = Math.min(lat1, lat2),
    maxLat = Math.max(lat1, lat2);
  const minLng = Math.min(lng1, lng2),
    maxLng = Math.max(lng1, lng2);

  return {
    lat: parseFloat((Math.random() * (maxLat - minLat) + minLat).toFixed(6)),
    lng: parseFloat((Math.random() * (maxLng - minLng) + minLng).toFixed(6)),
  };
}

// Haversine distance (m)
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

// UAV Icon
const uavIcon = new L.Icon({
  iconUrl: herodrone,
  iconSize: [40, 40],
  iconAnchor: [20, 40],
  popupAnchor: [0, -40],
});

// UAV Component
class UAV extends React.Component {
  state = {
    latlng: gen_position(),
    duration: 3000,
  };

  componentDidMount() {
    this.moveUAV();
  }

  componentWillUnmount() {
    clearTimeout(this.timer);
  }

  moveUAV = () => {
    const newPos = gen_position();
    const { latlng } = this.state;

    const dist = getDistance(latlng.lat, latlng.lng, newPos.lat, newPos.lng);
    const speedKmh = this.props.speedKmh || 120;
    const speedMs = (speedKmh * 1000) / 2500;
    const duration = (dist / speedMs) * 1000;

    this.setState({ latlng: newPos, duration });
    this.timer = setTimeout(this.moveUAV, duration);
  };

  render() {
    const { latlng, duration } = this.state;
    const { id, speedKmh } = this.props;

    return (
      <ReactLeafletDriftMarker
        position={latlng}
        duration={duration}
        icon={uavIcon}
      >
        <Popup>{`UAV ${id} - Speed: ${speedKmh} km/h`}</Popup>
      </ReactLeafletDriftMarker>
    );
  }
}

// Convert matrix coordinate to Delhi coordinates within rectangle1
function matrixToDelhiCoords(row, col, matrixSize = 30) {
  const [lat1, lon1] = rectangle1[0];
  const [lat2, lon2] = rectangle1[1];

  row = Math.max(0, Math.min(matrixSize - 1, row));
  col = Math.max(0, Math.min(matrixSize - 1, col));

  const lat = lat1 + (row / (matrixSize - 1)) * (lat2 - lat1);
  const lon = lon1 + (col / (matrixSize - 1)) * (lon2 - lon1);

  return [lat, lon];
}

// Main Map Component
export default function BasicMap() {
  const [activeUavs] = useState([2, 3]); // default 2 UAVs
  const rectangleOptions = { color: "black" };
  const matrixSize = 30;

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

        {/* Render UAVs */}
        {activeUavs.map((id) => (
          <UAV key={id} id={id} speedKmh={60} />
        ))}

        {/* Geofences */}
        <Rectangle bounds={rectangle1} pathOptions={rectangleOptions} />
        <Rectangle bounds={rectangle2} pathOptions={rectangleOptions} />

        {/* Render 30x30 matrix points inside rectangle1 */}
        {Array.from({ length: matrixSize }).map((_, r) =>
          Array.from({ length: matrixSize }).map((_, c) => {
            const [lat, lon] = matrixToDelhiCoords(r, c, matrixSize);
            return (
              <CircleMarker
                key={`${r}-${c}`}
                center={[lat, lon]}
                radius={1}
                color="red"
                fillOpacity={0.1}
              />
            );
          })
        )}
      </MapContainer>
    </div>
  );
}
