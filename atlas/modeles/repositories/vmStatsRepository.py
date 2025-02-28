# -*- coding:utf-8 -*-

from flask import current_app
from sqlalchemy.sql import text

from atlas.modeles import utils


def getStatsTerritory(connection, id_area):
    sql = """
select id_area,
       nb_obs,
       nb_species,
       nb_observers,
       nb_organism,
       yearmin,
       yearmax,
       nb_taxon_patrimonial,
       nb_taxon_protege,
       description,
       id_parent,
       area_parent_name,
       area_parent_type_name
FROM atlas.vm_territory_stats
WHERE id_area = :id_area;
  """
    result = connection.execute(text(sql), id_area=id_area)
    stats = list()
    for r in result:
        stats = {
            "id_area": r.id_area,
            "nb_obs": r.nb_obs,
            "nb_species": r.nb_species,
            "nb_observers": r.nb_observers,
            "nb_organism": r.nb_organism,
            "yearmin": r.yearmin,
            "yearmax": r.yearmax,
            "nb_taxon_patrimonial": r.nb_taxon_patrimonial,
            "nb_taxon_protege": r.nb_taxon_protege,
            "description": r.description,
            "id_parent": r.id_parent,
            "area_parent_name": r.area_parent_name,
            "area_parent_type_name": r.area_parent_type_name,
        }
    return stats
