from pydantic import BaseModel

# --- Request Schemas ---

class Point(BaseModel):
    lat: float
    lon: float

class RouteRequest(BaseModel):
    start_point: Point
    end_point: Point

# --- Response Schemas ---

class GeoJSONLineString(BaseModel):
    type: str = "LineString"
    coordinates: list[list[float]]

class RouteResponse(BaseModel):
    total_distance_meters: float
    path_geometry: GeoJSONLineString
