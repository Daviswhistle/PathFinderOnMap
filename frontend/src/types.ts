
import type { GeoJSON } from 'geojson';

export interface Point {
    lat: number;
    lon: number;
    name?: string;
}

export interface Route {
    total_distance_meters: number;
    path_geometry: GeoJSON.LineString;
}
