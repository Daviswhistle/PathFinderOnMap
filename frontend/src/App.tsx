import React, { useState } from 'react';
import axios from 'axios';
import { LatLng, Map, type LatLngExpression } from 'leaflet';
import MapComponent from './components/MapComponent';
import SearchComponent from './components/SearchComponent';
import './index.css';

// Define types for our state
interface Point {
  lat: number;
  lon: number;
}

interface Route {
  total_distance_meters: number;
  path_geometry: GeoJSON.LineString;
}

function App() {
  const [startPoint, setStartPoint] = useState<Point | null>(null);
  const [endPoint, setEndPoint] = useState<Point | null>(null);
  const [route, setRoute] = useState<Route | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [mapCenter, setMapCenter] = useState<LatLngExpression>([37.5665, 126.9780]); // Default center (Seoul)
  const [mapZoom, setMapZoom] = useState<number>(13);

  const handleMapClick = (latlng: { lat: number; lng: number }) => {
    const point = { lat: latlng.lat, lon: latlng.lng };
    setError(null);
    setRoute(null);
    if (!startPoint) {
      setStartPoint(point);
      setEndPoint(null);
    } else if (!endPoint) {
      setEndPoint(point);
    } else {
      setStartPoint(point);
      setEndPoint(null);
    }
  };

  const handleSearchSelect = (point: Point) => {
    setError(null);
    if (!startPoint) {
      setStartPoint(point);
    } else if (!endPoint) {
      setEndPoint(point);
    } else {
      setStartPoint(point);
      setEndPoint(null);
      setRoute(null);
    }
    // Update map center and zoom
    setMapCenter([point.lat, point.lon]);
    setMapZoom(16); // Zoom in to a specific level
  };

  const handleRouteSearch = async () => {
    if (!startPoint || !endPoint) {
      alert('Please select both a start and end point.');
      return;
    }
    setLoading(true);
    setError(null);
    setRoute(null);

    try {
      const response = await axios.post('http://127.0.0.1:8000/route', {
        start_point: startPoint,
        end_point: endPoint,
      });
      setRoute(response.data);
    } catch (err: any) {
      console.error("Error fetching route:", err);
      const detail = err.response?.data?.detail || 'Failed to fetch the route. Please try again.';
      setError(detail);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <div className="sidebar">
        <h2>Route Finder</h2>
        <SearchComponent onPlaceSelect={handleSearchSelect} />
        <div className="point-info">
          <p>Start: {startPoint ? `${startPoint.lat.toFixed(5)}, ${startPoint.lon.toFixed(5)}` : 'Click map or search'}</p>
          <p>End: {endPoint ? `${endPoint.lat.toFixed(5)}, ${endPoint.lon.toFixed(5)}` : 'Click map or search'}</p>
        </div>
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
          routeGeometry={route?.path_geometry || null}
          center={mapCenter}
          zoom={mapZoom}
        />
      </div>
    </div>
  );
}

export default App;
