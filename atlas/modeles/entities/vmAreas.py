# coding: utf-8
from geoalchemy2.types import Geometry
from sqlalchemy import Column, MetaData, String, Table, Integer, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from atlas.env import db

metadata = MetaData()
Base = declarative_base()



class VmAreas(Base):
    __table__ = Table(
        "vm_l_areas",
        metadata,
        Column("id_area", Integer(), primary_key=True, unique=True),
        Column("area_code", String(50)),
        Column("area_name", String(50)),
        Column("id_type", Integer()),
        Column("the_geom", Geometry("MULTIPOLYGON", 4326), index=True),
        Column("area_geojson", Text()),
        Column("description", Text()),
        schema="atlas",
        autoload=True,
        autoload_with=db.engine,
        extend_existing=True,
    )
