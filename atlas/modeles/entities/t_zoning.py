# coding: utf-8
from geoalchemy2.types import Geometry
from sqlalchemy import Column, MetaData, String, Table, Sequence, Integer, Text
from sqlalchemy.ext.declarative import declarative_base

from atlas.env import db

metadata = MetaData()
Base = declarative_base()


class t_zoning(Base):
    __table__ = Table(
        "zoning",
        metadata,
        Column("id", Sequence("zoning_id_seq"), primary_key=True, unique=True),
        Column("id_zone", Integer()),
        Column("area_name", String(50)),
        Column("the_geom", Geometry("MULTIPOLYGON"), index=True),
        Column("zone_geojson", Text),
        Column("id_zoning_type", Integer()),
        Column("id_parent", Integer()),
        schema="atlas",
        autoload=True,
        autoload_with=db.engine,
    )
