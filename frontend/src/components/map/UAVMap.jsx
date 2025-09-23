import React, { Component } from "react";
import {
  MapContainer,
  TileLayer,
  Popup,
  Rectangle,
  Polyline,
} from "react-leaflet";
import L from "leaflet";
import herodrone from "../../../public/hero-drone.png";
import ReactLeafletDriftMarker from "react-leaflet-drift-marker";

function gen_position() {
  const minLat = 28.4,
    maxLat = 28.88;
  const minLng = 76.84,
    maxLng = 77.35;
  return {
    lat: parseFloat((Math.random() * (maxLat - minLat) + minLat).toFixed(6)),
    lng: parseFloat((Math.random() * (maxLng - minLng) + minLng).toFixed(6)),
  };
}

const uavIcon = new L.Icon({
  iconUrl: herodrone,
  iconSize: [40, 40],
  iconAnchor: [20, 40],
  popupAnchor: [0, -40],
});

export default function basic_map() {
  const rectangle1 = [
    [28.6, 77.19],
    [28.64, 77.23],
  ];
  const rectangle2 = [
    [28.52, 77.16],
    [28.56, 77.2],
  ];
  const redOptions = { color: "red" };

  class SampleComp extends Component {
    state = {
      latlng: gen_position(),
      trajectory: [],
    };

    componentDidMount() {
      this.interval = setInterval(() => {
        const newPos = gen_position();
        this.setState((prev) => ({
          latlng: newPos,
          trajectory: [...prev.trajectory, newPos].slice(-10), // keep last 10
        }));
      }, 3000);
    }

    componentWillUnmount() {
      clearInterval(this.interval);
    }

    render() {
      const { latlng, trajectory } = this.state;

      return (
        <>
          {/* UAV marker */}
          <ReactLeafletDriftMarker
            position={latlng}
            duration={3000}
            icon={uavIcon}
          >
            <Popup>UAV Live Position</Popup>
          </ReactLeafletDriftMarker>

          {/* UAV trajectory with faster fading effect */}
          {trajectory.length > 1 &&
            trajectory.map((pos, i) => {
              if (i === 0) return null; // skip first point
              const opacity = Math.pow((i + 1) / trajectory.length, 3); // faster fade
              return (
                <Polyline
                  key={i}
                  positions={[
                    [trajectory[i - 1].lat, trajectory[i - 1].lng],
                    [pos.lat, pos.lng],
                  ]}
                  pathOptions={{
                    color: "blue",
                    opacity: opacity, // fade effect
                  }}
                />
              );
            })}
        </>
      );
    }
  }

  return (
    <div className="d-flex" style={{ height: "100vh", width: "100%" }}>
      <MapContainer
        className="mapcontainer"
        center={[28.6139, 77.209]}
        zoom={10}
        style={{ height: "100%", width: "100%" }}
        zoomControl={false}
        scrollWheelZoom={false}
        doubleClickZoom={false}
        touchZoom={false}
        dragging={false}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution="&copy; OpenStreetMap contributors"
        />
        <SampleComp />
        <Rectangle bounds={rectangle1} pathOptions={redOptions} />
        <Rectangle bounds={rectangle2} pathOptions={redOptions} />
      </MapContainer>
    </div>
  );
}
