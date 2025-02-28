# -*- coding:utf-8 -*-

import ast

from sqlalchemy import distinct
from sqlalchemy.sql import text
from sqlalchemy.sql.expression import func

from flask import current_app

from atlas.modeles.entities.vmAreas import VmAreas, VmBibAreasTypes


def getAllAreas(session):
    req = session.query(distinct(VmAreas.area_name), VmAreas.id_area).all()
    areaList = list()
    for r in req:
        temp = {"label": r[0], "value": r[1]}
        areaList.append(temp)
    return areaList


def searchMunicipalities(session, search, limit=50):
    like_search = "%" + search.replace(" ", "%") + "%"

    query = (
        session.query(
            distinct(VmAreas.area_name),
            VmAreas.id_area,
            func.length(VmAreas.area_name),
        )
        .join(VmBibAreasTypes)
        .filter(func.unaccent(VmAreas.area_name).ilike(func.unaccent(like_search)))
        .filter(VmBibAreasTypes.type_code.in_(current_app.config["TYPE_TERRITOIRE_SHEET"]))
        .order_by(VmAreas.area_name)
        .limit(limit)
    )

    results = query.all()

    return [{"label": r[0], "value": r[1]} for r in results]


def getAreaFromIdArea(connection, id_area):
    sql = """
        SELECT area.area_name,
           area.id_area,
           area.area_geojson,
           bib.type_name
        FROM atlas.vm_l_areas area
        JOIN ref_geo.bib_areas_types bib ON bib.id_type = area.id_type
        WHERE area.id_area = :thisIdArea
    """
    req = connection.execute(text(sql), thisIdArea=id_area)
    area_obj = dict()
    for r in req:
        area_obj = {
            "areaName": r.area_name,
            "areaCode": str(r.id_area),
            "areaGeoJson": ast.literal_eval(r.area_geojson),
            "typeName": r.type_name,
        }
    return area_obj


def getAreasObservationsChilds(connection, cd_ref):
    sql = "SELECT * FROM atlas.find_all_taxons_childs(:thiscdref) AS taxon_childs(cd_nom)"
    results = connection.execute(text(sql), thiscdref=cd_ref)
    taxons = [cd_ref]
    for r in results:
        taxons.append(r.cd_nom)

    sql = """
SELECT
    DISTINCT cas.id_area,
    vla.area_name
FROM atlas.vm_cor_area_synthese AS cas
        JOIN atlas.vm_observations obs ON cas.id_synthese = obs.id_observation
        JOIN atlas.vm_l_areas vla ON cas.id_area = vla.id_area
WHERE cas.type_code = ANY(:list_id_type) AND obs.cd_ref = ANY(:taxonsList)
ORDER BY vla.area_name ASC;
    """

    results = connection.execute(
        text(sql), taxonsList=taxons, list_id_type=current_app.config["TYPE_TERRITOIRE_SHEET"]
    )
    municipalities = list()
    for r in results:
        municipality = {"id_area": r.id_area, "area_name": r.area_name}
        municipalities.append(municipality)
    return municipalities

def get_infos_area(connection, id_area):
    """
    Get area info:
    yearmin: fisrt observation year
    yearmax: last observation year
    id_parent: id parent area
    area_name: name parent area
    area_type_name: type parent area
    """
    sql = """
SELECT
    MIN(extract(YEAR FROM o.dateobs)) AS yearmin,
    MAX(extract(YEAR FROM o.dateobs)) AS yearmax,
    area.description,
    ca.id_area_group AS id_parent,
    (SELECT area_name FROM atlas.vm_l_areas WHERE id_area = ca.id_area_group) AS area_parent_name,
    (SELECT type.type_name
        FROM atlas.vm_l_areas l
        JOIN atlas.vm_bib_areas_types type ON type.id_type = l.id_type
    WHERE l.id_area = ca.id_area_group) AS area_parent_type_name
FROM atlas.vm_observations o
    JOIN atlas.vm_l_areas area ON st_intersects(o.the_geom_point, area.the_geom)
    JOIN atlas.vm_cor_areas ca ON ca.id_area = area.id_area
WHERE area.id_area = :id_area
GROUP BY area.description,ca.id_area_group;
    """

    result = connection.execute(text(sql), id_area=id_area)
    info_area = dict()
    for r in result:
        info_area = {
            "yearmin": r.yearmin,
            "yearmax": r.yearmax,
            "description": r.description,
            "id_parent": r.id_parent,
            "parent_name": r.area_parent_name,
            "parent_type_name": r.area_parent_type_name,
        }

    return info_area


def get_nb_species_by_taxonimy_group(connection, id_area):
    """
    Get number of species by taxonimy group:
    """
    sql = """
    SELECT
     COUNT(DISTINCT o.cd_ref)                  AS nb_species,
     t.group2_inpn,
     COUNT(DISTINCT case t.patrimonial when 'oui' then t.cd_ref else null end) AS nb_patrominal,
     (SELECT COUNT(*)
        FROM atlas.vm_taxons taxon
        WHERE taxon.group2_inpn = t.group2_inpn) AS nb_species_in_teritory
      from atlas.vm_observations o
         JOIN atlas.vm_l_areas area ON st_intersects(o.the_geom_point, area.the_geom)
         FULL JOIN atlas.vm_taxons t ON t.cd_ref = o.cd_ref
WHERE area.id_area = :id_area
GROUP BY t.group2_inpn
        """

    result = connection.execute(text(sql), id_area=id_area)
    info_chart = dict()
    for r in result:
        info_chart[r.group2_inpn] = {
            "nb_species": r.nb_species - r.nb_patrominal,
            "nb_patrimonial": r.nb_patrominal,
            "nb_species_in_teritory": r.nb_species_in_teritory - r.nb_species,
        }
    return info_chart


def get_nb_observations_by_taxonimy_group(connection, id_area):
    """
    Get number of species by taxonimy group:
    """
    sql = """
SELECT COUNT(o.id_observation) AS nb_observations, t.group2_inpn
from atlas.vm_observations o
JOIN atlas.vm_taxons t ON t.cd_ref = o.cd_ref
JOIN atlas.vm_l_areas area ON st_intersects(o.the_geom_point, area.the_geom)
WHERE area.id_area = :id_area
GROUP BY t.group2_inpn, area.id_area
        """

    result = connection.execute(text(sql), id_area=id_area)
    info_chart = dict()
    for r in result:
        info_chart[r.group2_inpn] = r.nb_observations
    return info_chart


def get_biodiversity_stats_by_taxonimy_group(connection, id_area):
    """
    Get number of species by taxonimy group:
    """
    sql = """
SELECT nb_species,
       group2_inpn,
       nb_patrominal,
       nb_species_in_teritory
FROM atlas.vm_territory_stats_by_taxonomy_group
WHERE id_area = :id_area;
        """

    result = connection.execute(text(sql), id_area=id_area)
    info_chart = dict()
    for r in result:
        info_chart[r.group2_inpn] = {
            "nb_species": r.nb_species - r.nb_patrominal,
            "nb_patrimonial": r.nb_patrominal,
            "nb_species_in_teritory": r.nb_species_in_teritory - r.nb_species,
        }
    return info_chart


def get_observations_stats_taxonimy_group(connection, id_area):
    """
    Get number of species by taxonimy group:
    """
    sql = """
SELECT nb_obs,
       group2_inpn
FROM atlas.vm_territory_stats_by_taxonomy_group
WHERE id_area = :id_area;
        """

    result = connection.execute(text(sql), id_area=id_area)
    info_chart = dict()
    for r in result:
        info_chart[r.group2_inpn] = r.nb_obs
    return info_chart


def get_all_id_observation_area(connection, id_area):
    """
    Get all id in area:
    """
    sql = """
    SELECT DISTINCT obs.id_observation, obs.cd_ref
    FROM atlas.vm_cor_area_synthese AS cas
             JOIN atlas.vm_observations obs ON cas.id_synthese = obs.id_observation
    WHERE cas.id_area = :idAreaCode
            """

    result = connection.execute(text(sql), idAreaCode=id_area)
    list_id = list()
    for r in result:
        list_id.append(r.id_observation)
    return tuple(list_id)
