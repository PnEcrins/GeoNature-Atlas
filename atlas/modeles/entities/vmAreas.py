# coding: utf-8
from geoalchemy2.types import Geometry
from sqlalchemy import Column, MetaData, String, Table, Integer, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from atlas.env import db

metadata = MetaData()
Base = declarative_base()


class VmBibAreasTypes(Base):
    __table__ = Table(
        "vm_bib_areas_types",
        metadata,
        Column("id_type", Integer(), primary_key=True, unique=True),
        Column("type_code", String(50)),
        Column("type_name", String(250)),
        Column("type_desc", Text()),
        schema="atlas",
        autoload=True,
        autoload_with=db.engine,
        extend_existing=True,
    )
    areas = relationship("VmAreas")


class VmAreas(Base):
    __table__ = Table(
        "vm_l_areas",
        metadata,
        Column("id_area", Integer(), primary_key=True, unique=True),
        Column("area_code", String(50)),
        Column("area_name", String(50)),
        Column("id_type", Integer(), ForeignKey("atlas.vm_bib_areas_types.id_type")),
        Column("the_geom", Geometry("MULTIPOLYGON", 4326), index=True),
        Column("area_geojson", Text()),
        schema="atlas",
        autoload=True,
        autoload_with=db.engine,
        extend_existing=True,
    )


class VmCorAreaObservation(Base):
    __table__ = Table(
        "vm_cor_area_observation",
        metadata,
        Column("id_observation", Integer()),
        Column("id_area", Integer()),
        schema="atlas",
        autoload=True,
        autoload_with=db.engine,
        extend_existing=True,
        primary_key=False,
    )
    __mapper_args__ = {"primary_key": [__table__.c.id_observation, __table__.c.id_area]}
    observation = relationship("VmObservations", foreign_keys=[__table__.c.id_observation])
    area = relationship("VmAreas", foreign_keys=[__table__.c.id_area])
