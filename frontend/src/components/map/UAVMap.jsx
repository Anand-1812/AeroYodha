import React from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
// import 'leaflet/dist/leaflet.css';

// Fix default marker icon issue in React
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl:
    'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

export default function basic_map() {
  return (
    <div className='d-flex' style={{ height: '100vh', width: '100%' }}>
      <MapContainer className='mapcontainer'
       center={[28.6139, 77.209]}
       zoom={13} 
       style={{ height: '100%', width: '100%', border: "1px solid black"}} 
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
        <Marker position={[28.6139, 77.209]}>
          <Popup>Hello Delhi!</Popup>
        </Marker>
      </MapContainer>
      <div className='right_panel ms-5'> 
        <h2>Aeroyodha</h2>
      </div>
    </div>
  );
}
