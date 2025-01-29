# -*- coding:utf-8 -*-

import ast

from sqlalchemy import distinct
from sqlalchemy.sql import text
from sqlalchemy.sql.expression import func

from atlas.modeles.entities.t_zoning import t_zoning


def getAllZones(session):
    req = session.query(distinct(t_zoning.area_name), t_zoning.id_zone).all()
    zoneList = list()
    for r in req:
        temp = {"label": r[0], "value": r[1]}
        zoneList.append(temp)
    return zoneList


def searchMunicipalities(session, search, limit=50):
    like_search = "%" + search.replace(" ", "%") + "%"

    query = (
        session.query(
            distinct(t_zoning.area_name),
            t_zoning.id_zone,
            func.length(t_zoning.area_name),
        )
        .filter(func.unaccent(t_zoning.area_name).ilike(func.unaccent(like_search)))
        .order_by(t_zoning.area_name)
        .limit(limit)
    )
    results = query.all()

    return [{"label": r[0], "value": r[1]} for r in results]


def getZoneFromIdZone(connection, id_zone):
    sql = """
        SELECT c.area_name,
           c.id_zone,
           c.zone_geojson,
           bib.type_name
        FROM atlas.zoning c
        JOIN ref_geo.bib_areas_types bib ON bib.id_type = c.id_zoning_type
        WHERE c.id_zone = :thisIdZone
    """
    req = connection.execute(text(sql), thisIdZone=id_zone)
    zone_obj = dict()
    for r in req:
        zone_obj = {
            "areaName": r.area_name,
            "areaCode": str(r.id_zone),
            "areaGeoJson": ast.literal_eval(r.zone_geojson),
            "typeName": r.type_name,
        }
    return zone_obj


def getZonesObservationsChilds(connection, cd_ref):
    sql = "SELECT * FROM atlas.find_all_taxons_childs(:thiscdref) AS taxon_childs(cd_nom)"
    results = connection.execute(text(sql), thiscdref=cd_ref)
    taxons = [cd_ref]
    for r in results:
        taxons.append(r.cd_nom)

    sql = """
        SELECT DISTINCT
            zone.area_name,
            zone.id_zone
        FROM atlas.vm_observations AS obs
            JOIN atlas.zoning AS zone
                ON st_intersects(obs.the_geom_point, zone.the_geom_4326)
        WHERE obs.cd_ref = ANY(:taxonsList)
        ORDER BY zone.area_name ASC
    """
    results = connection.execute(text(sql), taxonsList=taxons)
    municipalities = list()
    for r in results:
        municipality = {"id_zone": r.id_zone, "area_name": r.area_name}
        municipalities.append(municipality)
    return municipalities


def get_infos_zone(connection, id_zone):
    """
    Get zone info:
    yearmin: fisrt observation year
    yearmax: last observation year
    id_parent: id parent zone
    area_name: name parent zone
    area_type_name: type parent zone
    """
    sql = """
SELECT
    MIN(extract(YEAR FROM o.dateobs)) AS yearmin,
    MAX(extract(YEAR FROM o.dateobs)) AS yearmax,
    z.id_parent,
    (SELECT area_name FROM atlas.zoning WHERE id_zone = z.id_parent) AS area_parent_name,
    (SELECT type.type_name
     FROM atlas.zoning AS zone
        JOIN ref_geo.bib_areas_types type
            ON type.id_type = zone.id_zoning_type
     WHERE zone.id_zone = z.id_parent) AS area_parent_type_name
FROM atlas.vm_observations o
         JOIN atlas.zoning z ON z.id_zone = o.id_zone
WHERE o.id_zone = :id_zone
GROUP BY z.id_parent
    """

    result = connection.execute(text(sql), id_zone=id_zone)
    info_zone = dict()
    for r in result:
        info_zone = {
            "yearmin": r.yearmin,
            "yearmax": r.yearmax,
            "id_parent": r.id_parent,
            "parent_name": r.area_parent_name,
            "parent_type_name": r.area_parent_type_name,
        }

    return info_zone
