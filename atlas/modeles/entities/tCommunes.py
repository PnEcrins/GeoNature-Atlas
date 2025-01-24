# coding: utf-8
from geoalchemy2 import Geometry
from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class LCommune(Base):
    __tablename__ = "l_communes"
    __table_args__ = {"schema": "layers"}

    insee = Column(String(5), primary_key=True)
    area_name = Column(String(50))
    commune_min = Column(String(50))
    the_geom = Column(Geometry)
