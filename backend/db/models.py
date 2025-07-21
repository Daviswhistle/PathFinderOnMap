from sqlalchemy import Column, BigInteger, Float, String, Integer, Index
from sqlalchemy.ext.declarative import declarative_base
from geoalchemy2 import Geometry

Base = declarative_base()

class Node(Base):
    __tablename__ = 'nodes'

    NODE_ID = Column(BigInteger, primary_key=True)
    NODE_TYPE = Column(String)
    NODE_NAME = Column(String)
    # The geometry column for PostGIS
    geom = Column(Geometry(geometry_type='POINT', srid=5186), index=True)

class Link(Base):
    __tablename__ = 'links'

    LINK_ID = Column(BigInteger, primary_key=True)
    F_NODE = Column(BigInteger)
    T_NODE = Column(BigInteger)
    LENGTH = Column(Float)
    # The geometry column for PostGIS
    geom = Column(Geometry(geometry_type='LINESTRING', srid=5186), nullable=False)

    __table_args__ = (
        # spatial_index=True 로도 가능하지만,
        # 명시적으로 GIST 인덱스를 걸려면:
        Index('ix_links_geom', 'geom', postgresql_using='gist'),
    )
