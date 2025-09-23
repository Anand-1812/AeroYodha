import React from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import herodrone from "../../../public/hero-drone.png"

// Fix default marker icon issue in React
// delete L.Icon.Default.prototype._getIconUrl;
// L.Icon.Default.mergeOptions({
//   iconRetinaUrl:
//     'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
//   iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
//   shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
// });

const uavIcon = new L.Icon({
  iconUrl: herodrone, // path to your image
  iconSize: [40, 40],           // size of the icon
  iconAnchor: [20, 40],         // point of the icon which will correspond to marker's location
  popupAnchor: [0, -40]         // where the popup should open relative to the iconAnchor
});


export default function basic_map() {
  return (
    <div className='d-flex' style={{ height: '100vh', width: '100%' }}>
      <MapContainer className='mapcontainer'
       center={[28.6139, 77.209]}
       zoom={13} 
       style={{ height: '100%', width: '100%'}} 
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
        <Marker position={[28.6139, 77.209]} icon={uavIcon}>
          <Popup>Hello Delhi!</Popup>
        </Marker>
      </MapContainer>
    </div>
  );
}
