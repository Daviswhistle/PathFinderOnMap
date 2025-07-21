import os
import sys
import shapefile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Add the parent directory to the path to allow relative imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.models import Base, Node, Link

# --- CONFIGURATION ---
# IMPORTANT: Update these paths to point to your actual Shapefiles
NODE_SHAPEFILE_PATH = "/home/jskim/kdh/map/[2025-05-12]NODELINKDATA/MOCT_NODE.shp"
LINK_SHAPEFILE_PATH = "/home/jskim/kdh/map/[2025-05-12]NODELINKDATA/MOCT_LINK.shp"

def main():
    """Main function to import shapefile data into the database."""
    load_dotenv()
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("Error: DATABASE_URL not found in .env file.")
        return

    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Drop only nodes and links tables, if they exist
    Node.__table__.drop(engine, checkfirst=True)
    Link.__table__.drop(engine, checkfirst=True)

    print("Creating database tables (if they don't exist)...")
    Base.metadata.create_all(engine)

    try:
        # --- Import Nodes ---
        print(f"Reading nodes from {NODE_SHAPEFILE_PATH}...")
        with shapefile.Reader(NODE_SHAPEFILE_PATH, encoding="euc-kr") as sf:
            nodes_to_insert = []
            for shape_rec in sf.iterShapeRecords():
                node = Node(
                    NODE_ID=shape_rec.record['NODE_ID'],
                    NODE_TYPE=shape_rec.record['NODE_TYPE'],
                    NODE_NAME=shape_rec.record['NODE_NAME'],
                    geom=f'SRID=5186;POINT({shape_rec.shape.points[0][0]} {shape_rec.shape.points[0][1]})'
                )
                nodes_to_insert.append(node)
        
        print(f"Importing {len(nodes_to_insert)} nodes into the database...")
        session.bulk_save_objects(nodes_to_insert)
        session.commit()
        print("Nodes imported successfully.")

        # --- Import Links ---
        print(f"Reading links from {LINK_SHAPEFILE_PATH}...")
        with shapefile.Reader(LINK_SHAPEFILE_PATH, encoding="euc-kr") as sf:
            links_to_insert = []
            for shape_rec in sf.iterShapeRecords():
                # WKT representation for LineString
                points_str = ", ".join([f"{p[0]} {p[1]}" for p in shape_rec.shape.points])
                link = Link(
                    LINK_ID=shape_rec.record['LINK_ID'],
                    F_NODE=shape_rec.record['F_NODE'],
                    T_NODE=shape_rec.record['T_NODE'],
                    LENGTH=shape_rec.record['LENGTH'],
                    geom=f'SRID=5186;LINESTRING({points_str})'
                )
                links_to_insert.append(link)

        print(f"Importing {len(links_to_insert)} links into the database...")
        session.bulk_save_objects(links_to_insert)
        session.commit()
        print("Links imported successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    if "/path/to/your" in NODE_SHAPEFILE_PATH:
        print("\n*** ACTION REQUIRED ***")
        print("Please update the NODE_SHAPEFILE_PATH and LINK_SHAPEFILE_PATH variables in")
        print(f"'{__file__}' to the correct location of your shapefiles.")
        print("***********************\n")
    else:
        main()
