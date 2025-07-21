import React from 'react';
import { MapContainer, TileLayer, Marker, Popup, GeoJSON, useMapEvents, useMap } from 'react-leaflet';
import { LatLngExpression, Map } from 'leaflet';

// Define types for props
interface Point {
  lat: number;
  lon: number;
}

interface MapComponentProps {
  onMapClick: (latlng: { lat: number; lng: number }) => void;
  startPoint: Point | null;
  endPoint: Point | null;
  routeGeometry: GeoJSON.LineString | null;
  center: LatLngExpression;
  zoom: number;
}

// A custom component to handle map click events and view changes
const MapController = ({ onClick, center, zoom }: { onClick: (latlng: { lat: number; lng: number }) => void; center: LatLngExpression; zoom: number }) => {
  const map = useMap();

  useMapEvents({
    click(e) {
      onClick(e.latlng);
    },
  });

  // Update map view when center or zoom props change
  map.setView(center, zoom);

  return null;
};

const MapComponent: React.FC<MapComponentProps> = ({ onMapClick, startPoint, endPoint, routeGeometry, center, zoom }) => {
  return (
    <MapContainer center={center} zoom={zoom} scrollWheelZoom={true}>
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <MapController onClick={onMapClick} center={center} zoom={zoom} />

      {startPoint && (
        <Marker position={[startPoint.lat, startPoint.lon]}>
          <Popup>Start Point</Popup>
        </Marker>
      )}

      {endPoint && (
        <Marker position={[endPoint.lat, endPoint.lon]}>
          <Popup>End Point</Popup>
        </Marker>
      )}

      {routeGeometry && (
        <GeoJSON data={routeGeometry} />
      )}
    </MapContainer>
  );
};

export default MapComponent;
