from sqlalchemy.orm import Session
from sqlalchemy import func, text
from geoalchemy2.functions import ST_Transform, ST_SetSRID, ST_MakePoint, ST_AsGeoJSON, ST_LineLocatePoint, ST_LineSubstring, ST_Length, ST_ClosestPoint
import networkx as nx
import json

from ..db.models import Node, Link
from ..schemas.route import Point

def find_nearest_link_and_snapped_point(db: Session, point: Point):
    """
    Finds the nearest link to a given point, and returns information 
    about the link and the snapped point on it.
    """
    # Directly create the WKT string for the point in WGS84
    wgs84_wkt = f"SRID=4326;POINT({point.lon} {point.lat})"

    # The SQL query will now handle the transformation and all PostGIS operations.
    sql = text("""
        SELECT 
            "LINK_ID",
            "F_NODE",
            "T_NODE",
            "LENGTH",
            ST_AsText(ST_ClosestPoint(geom, ST_Transform(ST_GeomFromEWKT(:wgs84_wkt), 5186))) as snapped_point_wkt,
            ST_LineLocatePoint(geom, ST_Transform(ST_GeomFromEWKT(:wgs84_wkt), 5186)) as fraction
        FROM links
        ORDER BY geom <-> ST_Transform(ST_GeomFromEWKT(:wgs84_wkt), 5186)
        LIMIT 1;
    """)
    
    result = db.execute(sql, {'wgs84_wkt': wgs84_wkt}).first()

    if not result:
        return None

    return {
        "link_id": result[0],
        "f_node": result[1],
        "t_node": result[2],
        "link_length": result[3],
        "snapped_point_wkt": result[4],
        "fraction": result[5],
        "user_point_wkt": wgs84_wkt  # Return the original point WKT as well
    }

def find_shortest_path(graph: nx.DiGraph, start_node: int, end_node: int) -> tuple[list, float]:
    """Finds the shortest path using A* algorithm."""
    try:
        path_nodes = nx.astar_path(graph, start_node, end_node, weight='weight')
        path_length = nx.astar_path_length(graph, start_node, end_node, weight='weight')
        print(f"Debug (pathfinder): Path found from {start_node} to {end_node}. Nodes: {path_nodes}, Length: {path_length}")
        return path_nodes, path_length
    except nx.NetworkXNoPath:
        print(f"Debug (pathfinder): No path found from {start_node} to {end_node}.")
        return None, 0

def get_full_path_geometry_and_length(db: Session, start_info: dict, end_info: dict, main_path_nodes: list[int]):
    """
    Constructs the full path geometry including the snapped start/end segments 
    and the main path, returning it as a single GeoJSON LineString.
    """
    if not main_path_nodes:
        # This case should ideally be handled before calling, but as a safeguard:
        # Handle case where start and end are on the same link, but snapped points are different.
        if start_info['link_id'] == end_info['link_id']:
            sql_same_link = text("""
                SELECT ST_AsGeoJSON(ST_Transform(ST_LineSubstring(geom, :start_frac, :end_frac), 4326))
                FROM links WHERE "LINK_ID" = :link_id;
            """)
            start_frac, end_frac = sorted([start_info['fraction'], end_info['fraction']])
            geom_json, = db.execute(sql_same_link, {
                'start_frac': start_frac,
                'end_frac': end_frac,
                'link_id': start_info['link_id']
            }).first()
            return json.loads(geom_json) if geom_json else None

    # SQL query to construct the three parts of the geometry and combine them
    sql_full_path = text("""
        WITH main_path_geom AS (
            -- Geometry of the main path connecting the nodes
            SELECT ST_MakeLine(geom ORDER BY array_position(:main_path_nodes_array, "F_NODE")) as geom
            FROM links
            WHERE "F_NODE" = ANY(:main_path_nodes_array) AND "T_NODE" = ANY(:main_path_nodes_array)
              AND array_position(:main_path_nodes_array, "F_NODE") + 1 = array_position(:main_path_nodes_array, "T_NODE")
        ),
        start_link_geom AS (
            -- Partial geometry of the start link
            SELECT ST_LineSubstring(geom, :start_fraction, CASE WHEN :start_node = "F_NODE" THEN 0 ELSE 1 END) as geom
            FROM links
            WHERE "LINK_ID" = :start_link_id
        ),
        end_link_geom AS (
            -- Partial geometry of the end link
            SELECT ST_LineSubstring(geom, CASE WHEN :end_node = "F_NODE" THEN 0 ELSE 1 END, :end_fraction) as geom
            FROM links
            WHERE "LINK_ID" = :end_link_id
        )
        -- Collect all parts into a single LineString
        SELECT ST_AsGeoJSON(ST_Transform(ST_LineMerge(ST_Collect(
            ARRAY[
                (SELECT geom FROM start_link_geom),
                (SELECT geom FROM main_path_geom),
                (SELECT geom FROM end_link_geom)
            ]
        )), 4326));
    """)

    # Determine which node on the start/end link is part of the main path
    start_node_on_path = main_path_nodes[0]
    end_node_on_path = main_path_nodes[-1]

    params = {
        'start_fraction': start_info['fraction'],
        'start_link_id': start_info['link_id'],
        'start_node': start_node_on_path,
        'main_path_nodes_array': main_path_nodes,
        'end_link_id': end_info['link_id'],
        'end_fraction': end_info['fraction'],
        'end_node': end_node_on_path,
    }
    
    full_geom_json, = db.execute(sql_full_path, params).first()
    
    return json.loads(full_geom_json) if full_geom_json else None


