import networkx as nx
from sqlalchemy.orm import Session
from ..db.models import Link

class GraphManager:
    def __init__(self):
        self._graph = None

    def load_graph(self, db: Session):
        if self._graph is None:
            print("Loading graph from database...")
            G = nx.DiGraph()
            links = db.query(Link.F_NODE, Link.T_NODE, Link.LENGTH).all()
            for link in links:
                G.add_edge(link.F_NODE, link.T_NODE, weight=link.LENGTH)
            self._graph = G
            print(f"Graph loaded: {self._graph.number_of_nodes()} nodes, {self._graph.number_of_edges()} edges.")

    def get_graph(self):
        if self._graph is None:
            raise RuntimeError("Graph is not loaded. Call load_graph first.")
        return self._graph

# Create a single instance of the graph manager
graph_manager = GraphManager()
