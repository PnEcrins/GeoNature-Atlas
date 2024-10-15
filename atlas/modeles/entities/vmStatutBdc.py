# -*- coding:utf-8 -*-

from sqlalchemy import Column, Integer, MetaData, String, Table, Float
from sqlalchemy.ext.declarative import declarative_base

from atlas.utils import engine

Base = declarative_base()
metadata = MetaData()

class VmStatutBdc(Base):
    __table__ = Table(
        'vm_taxons', metadata,
        Column('cd_ref', Integer),
        Column('code_statut', String(50)),
        Column('label_statut', String(250)),
        Column('cd_type_statut', String(50)),
        Column('lb_type_statut', String(250)),
        schema='atlas', autoload=True, autoload_with=engine
    )
