import React, { Component } from "react";
import {
  MapContainer,
  TileLayer,
  Popup,
  Rectangle,
} from "react-leaflet";
import L from "leaflet";
import herodrone from "../../../public/hero-drone.png";
import ReactLeafletDriftMarker from "react-leaflet-drift-marker";

function gen_position() {
  const minLat = 28.4, maxLat = 28.88;
  const minLng = 76.84, maxLng = 77.35;
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
    state = { latlng: gen_position() };

    componentDidMount() {
      this.interval = setInterval(() => {
        this.setState({ latlng: gen_position() });
      }, 3000);
    }

    componentWillUnmount() {
      clearInterval(this.interval);
    }

    render() {
      return (
        <ReactLeafletDriftMarker
          position={this.state.latlng}
          duration={1000}
          icon={uavIcon}
        >
          <Popup>Hello Delhi!</Popup>
        </ReactLeafletDriftMarker>
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
