# coding: utf-8
from geoalchemy2.types import Geometry
from sqlalchemy import Column, Date, Integer, MetaData, String, Table, Text, ARRAY
from sqlalchemy.ext.declarative import declarative_base

from atlas.env import db

metadata = MetaData()
Base = declarative_base()


class VmObservations(Base):
    __table__ = Table(
        "vm_observations",
        metadata,
        Column("id_observation", Integer, primary_key=True, unique=True),
        Column("id_area", String(5), index=True),
        Column("dateobs", Date, index=True),
        Column("type_code", Integer),
        Column("observateurs", String(255)),
        Column("altitude_retenue", Integer, index=True),
        Column("cd_ref", Integer, index=True),
        Column("the_geom_point", Geometry(geometry_type="POINT", srid=4326)),
        Column("geojson_point", Text),
        Column("cd_sensitivity"),
        schema="atlas",
        autoload=True,
        autoload_with=db.engine,
    )


class VmObservationsMailles(Base):
    """
    Table des observations par maille
    """

    __table__ = Table(
        "vm_observations_mailles",
        metadata,
        Column("cd_ref", Integer, primary_key=True, index=True),
        Column("annee", String(1000), primary_key=True, index=True),
        Column("id_maille", Integer, primary_key=True, index=True),
        Column("nbr", Integer),
        Column("id_observations", ARRAY(Integer)),
        schema="atlas",
        autoload=True,
        autoload_with=db.engine,
    )
