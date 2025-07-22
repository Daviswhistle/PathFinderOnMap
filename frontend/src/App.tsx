import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { type LatLngExpression } from 'leaflet';
import MapComponent from './components/MapComponent';
import SearchComponent from './components/SearchComponent';
import InfoCard from './components/InfoCard'; // We will create this component
import './index.css';

import { type Point, type Route } from './types';

function App() {
  const [startPoint, setStartPoint] = useState<Point | null>(null);
  const [endPoint, setEndPoint] = useState<Point | null>(null);
  const [selectedPoint, setSelectedPoint] = useState<Point | null>(null);
  const [route, setRoute] = useState<Route | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [mapCenter, setMapCenter] = useState<LatLngExpression>([37.5665, 126.9780]);
  const [mapZoom, setMapZoom] = useState<number>(13);

  const handleMapClick = async (latlng: { lat: number; lng: number }) => {
    setLoading(true);
    try {
      const response = await axios.get(`http://127.0.0.1:8000/reverse?lat=${latlng.lat}&lon=${latlng.lng}`);
      const point: Point = { lat: latlng.lat, lon: latlng.lng, name: response.data.name };
      setSelectedPoint(point);
      setMapCenter([point.lat, point.lon]);
      setMapZoom(16);
    } catch (err) {
      console.error("Reverse geocoding failed:", err);
      const point: Point = { lat: latlng.lat, lon: latlng.lng, name: `좌표: ${latlng.lat.toFixed(5)}, ${latlng.lng.toFixed(5)}` };
      setSelectedPoint(point);
    } finally {
      setLoading(false);
    }
  };

  const handleSearchSelect = (result: { name: string, location: { lat: number, lon: number }}) => {
    const point: Point = { ...result.location, name: result.name };
    setSelectedPoint(point);
    setMapCenter([point.lat, point.lon]);
    setMapZoom(16);
  };

  const setPointRole = (role: 'start' | 'end') => {
    if (!selectedPoint) return;
    if (role === 'start') {
      setStartPoint(selectedPoint);
    } else {
      setEndPoint(selectedPoint);
    }
    setSelectedPoint(null); // Clear selection after setting role
    setRoute(null);
    setError(null);
  };

  const clearPoint = (role: 'start' | 'end') => {
    if (role === 'start') setStartPoint(null);
    else setEndPoint(null);
    setRoute(null);
    setError(null);
  };

  const handleRouteSearch = async () => {
    if (!startPoint || !endPoint) {
      alert('Please set both start and end points.');
      return;
    }
    setLoading(true);
    setError(null);
    setRoute(null);
    try {
      const response = await axios.post('http://127.0.0.1:8000/route', { start_point: startPoint, end_point: endPoint });
      setRoute(response.data);
    } catch (err: any) {
      const detail = err.response?.data?.detail || 'Failed to fetch route.';
      setError(detail);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (startPoint && endPoint) {
      handleRouteSearch();
    }
  }, [startPoint, endPoint]);

  return (
    <div className="App">
      <div className="sidebar">
        <h2>Route Finder</h2>
        <SearchComponent onPlaceSelect={handleSearchSelect} />
        
        <div className="point-display">
          <div className="point-info">
            <span>출발</span>
            <p>{startPoint?.name || 'Not set'}</p>
            {startPoint && <button onClick={() => clearPoint('start')}>X</button>}
          </div>
          <div className="point-info">
            <span>도착</span>
            <p>{endPoint?.name || 'Not set'}</p>
            {endPoint && <button onClick={() => clearPoint('end')}>X</button>}
          </div>
        </div>

        {selectedPoint && <InfoCard point={selectedPoint} setPointRole={setPointRole} />}

        <button onClick={handleRouteSearch} disabled={loading || !startPoint || !endPoint}>
          {loading ? 'Searching...' : 'Get Route'}
        </button>
        
        {error && <p className="error-message">Error: {error}</p>}
        
        {route && (
          <div className="route-info">
            <p>Total Distance: {(route.total_distance_meters / 1000).toFixed(2)} km</p>
          </div>
        )}
      </div>
      <div className="map-container">
        <MapComponent 
          onMapClick={handleMapClick} 
          startPoint={startPoint} 
          endPoint={endPoint} 
          selectedPoint={selectedPoint} // Pass selected point to map
          routeGeometry={route?.path_geometry || null}
          center={mapCenter}
          zoom={mapZoom}
        />
      </div>
    </div>
  );
}

export default App;
