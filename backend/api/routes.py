import requests
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
import json

from ..db.session import get_db
from ..schemas.route import RouteRequest, RouteResponse
from ..schemas.search import SearchResultItem, SearchResponse
from ..core.graph import graph_manager
from ..core.pathfinder import find_nearest_link_and_snapped_point, find_shortest_path, get_path_geometry_and_length

router = APIRouter()

@router.post("/route", response_model=RouteResponse)
def get_route(request: RouteRequest, db: Session = Depends(get_db)):
    """
    Calculates the shortest route between two points using Snap-to-Road logic.
    """
    graph = graph_manager.get_graph()
    if graph is None:
        raise HTTPException(status_code=503, detail="Graph not loaded yet.")

    # 1. Find nearest links and snapped points for start and end
    print(f"Debug (routes): Request start_point: lat={request.start_point.lat}, lon={request.start_point.lon}")
    print(f"Debug (routes): Request end_point: lat={request.end_point.lat}, lon={request.end_point.lon}")
    start_info = find_nearest_link_and_snapped_point(db, request.start_point)
    end_info = find_nearest_link_and_snapped_point(db, request.end_point)

    print(f"Debug (routes): Start Info: {start_info}")
    print(f"Debug (routes): End Info: {end_info}")

    if not start_info or not end_info:
        raise HTTPException(status_code=404, detail="Could not snap points to the road network.")

    # --- Handle special cases ---
    # Case 1: Start and end points are on the same link
    if start_info['link_id'] == end_info['link_id']:
        sql = text("""
            SELECT ST_AsGeoJSON(ST_Transform(ST_LineSubstring(geom, :start_frac, :end_frac), 4326)),
                   "LENGTH" * abs(:start_frac - :end_frac)
            FROM links WHERE "LINK_ID" = :link_id;
        """)
        start_frac, end_frac = sorted([start_info['fraction'], end_info['fraction']])
        geom, length = db.execute(sql, {
            'start_frac': start_frac, 
            'end_frac': end_frac, 
            'link_id': start_info['link_id']
        }).first()

        geom_dict = json.loads(geom)
        # If ST_LineSubstring returns a POINT (e.g., start_frac == end_frac), convert to LineString format
        if geom_dict["type"] == "Point":
            geom_dict["type"] = "LineString"
            geom_dict["coordinates"] = [geom_dict["coordinates"]]

        return RouteResponse(total_distance_meters=length, path_geometry=geom_dict)

    # --- Standard pathfinding logic ---
    # Determine the nodes for the main path calculation
    start_node_main = start_info['t_node']
    end_node_main = end_info['f_node']

    main_path_nodes, main_path_length = find_shortest_path(graph, start_node_main, end_node_main)
    
    print(f"Debug: Main path nodes (initial): {main_path_nodes}")
    print(f"Debug: Main path length (initial): {main_path_length}")

    if main_path_nodes is None:
        # Try the other direction as a fallback
        start_node_main_fallback = start_info['f_node']
        end_node_main_fallback = end_info['t_node']
        main_path_nodes, main_path_length = find_shortest_path(graph, start_node_main_fallback, end_node_main_fallback)
        
        print(f"Debug: Main path nodes (fallback): {main_path_nodes}")
        print(f"Debug: Main path length (fallback): {main_path_length}")

        if main_path_nodes is None:
            raise HTTPException(status_code=404, detail="No path found between the road segments.")

    # Calculate costs for the partial segments
    cost_start = start_info['link_length'] * (1 - start_info['fraction'])
    cost_end = end_info['link_length'] * end_info['fraction']
    
    total_distance = cost_start + main_path_length + cost_end

    print(f"Debug: cost_start: {cost_start}")
    print(f"Debug: cost_end: {cost_end}")
    print(f"Debug: total_distance: {total_distance}")

    # For simplicity, we are currently returning the geometry of the main path only.
    # A full implementation would require stitching the three geometry parts together.
    main_path_geom, _ = get_path_geometry_and_length(db, main_path_nodes)

    if not main_path_geom:
        raise HTTPException(status_code=500, detail="Could not construct the main path geometry.")

    return RouteResponse(total_distance_meters=total_distance, path_geometry=main_path_geom)


@router.get("/search", response_model=SearchResponse)
def search_places(q: str = Query(None, min_length=2)):
    """
    Searches for places using the Nominatim API.
    """
    if not q:
        return {"results": []}

    NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
    params = {
        'q': q,
        'format': 'json',
        'addressdetails': 1,
        'limit': 10,
        'countrycodes': 'kr',
    }
    headers = {
        'User-Agent': 'KDH-Map-Project/1.0 (https://github.com/Daviswhistle/PathFinderOnMap)',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
    }

    try:
        response = requests.get(NOMINATIM_URL, params=params, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        results = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Nominatim API request failed: {e}")
        raise HTTPException(status_code=503, detail="Could not connect to the search service.")

    search_results = []
    for item in results:
        address_parts = item.get('address', {})
        address = ", ".join(filter(None, [
            address_parts.get('road'),
            address_parts.get('city'),
            address_parts.get('county'),
            address_parts.get('state'),
            address_parts.get('country')
        ]))

        search_results.append(
            SearchResultItem(
                name=item.get('display_name'),
                category=item.get('type'),
                address=address,
                location={"lat": float(item.get('lat')), "lon": float(item.get('lon'))}
            )
        )
    
    return {"results": search_results}