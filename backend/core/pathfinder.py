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
        "fraction": result[5]
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

def get_path_geometry_and_length(db: Session, path_nodes: list[int]):
    """Constructs the GeoJSON LineString and calculates the length for a path of nodes."""
    if len(path_nodes) < 2:
        return None, 0

    # The path_nodes list is already ordered.
    # We can create segments and find links that match these segments,
    # then order them by the position of their F_NODE in the original path_nodes list.
    sql = text("""
        WITH path_links AS (
            SELECT
                geom,
                "LENGTH",
                array_position(:path_nodes_array, "F_NODE") as pos
            FROM links
            WHERE "F_NODE" = ANY(:path_nodes_array) AND "T_NODE" = ANY(:path_nodes_array)
              AND array_position(:path_nodes_array, "F_NODE") + 1 = array_position(:path_nodes_array, "T_NODE")
        )
        SELECT
            ST_AsGeoJSON(ST_Transform(ST_MakeLine(geom ORDER BY pos), 4326)),
            SUM("LENGTH")
        FROM path_links;
    """)

    result = db.execute(sql, {'path_nodes_array': path_nodes}).first()
    return json.loads(result[0]) if result[0] else None, result[1] or 0

