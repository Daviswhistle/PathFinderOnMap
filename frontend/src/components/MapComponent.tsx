import React from 'react';
import { MapContainer, TileLayer, Marker, Popup, GeoJSON, useMapEvents, useMap } from 'react-leaflet';
import { LatLngExpression, Map } from 'leaflet';
import type { Point } from '../types';

// Define types for props
interface MapComponentProps {
  onMapClick: (latlng: { lat: number; lng: number }) => void;
  startPoint: Point | null;
  endPoint: Point | null;
  selectedPoint: Point | null; // Add selectedPoint prop
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

const MapComponent: React.FC<MapComponentProps> = ({ onMapClick, startPoint, endPoint, selectedPoint, routeGeometry, center, zoom }) => {
  return (
    <MapContainer center={center} zoom={zoom} scrollWheelZoom={true}>
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <MapController onClick={onMapClick} center={center} zoom={zoom} />

      {startPoint && (
        <Marker position={[startPoint.lat, startPoint.lon]}>
          <Popup>출발지: {startPoint.name}</Popup>
        </Marker>
      )}

      {endPoint && (
        <Marker position={[endPoint.lat, endPoint.lon]}>
          <Popup>도착지: {endPoint.name}</Popup>
        </Marker>
      )}

      {selectedPoint && (
        <Marker position={[selectedPoint.lat, selectedPoint.lon]} opacity={0.6}>
          <Popup>선택됨: {selectedPoint.name}</Popup>
        </Marker>
      )}

      {routeGeometry && (
        <GeoJSON data={routeGeometry} />
      )}
    </MapContainer>
  );
};

export default MapComponent;
