# -*- coding:utf-8 -*-

import ast

from sqlalchemy import distinct
from sqlalchemy.sql import text
from sqlalchemy.sql.expression import func
from flask import current_app

from atlas.modeles.entities.vmAreas import VmAreas


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
        .filter(func.unaccent(VmAreas.area_name).ilike(func.unaccent(like_search)))
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
        SELECT DISTINCT
            area.area_name,
            area.id_area
        FROM atlas.vm_observations AS obs
            JOIN atlas.vm_l_areas AS area
                ON st_intersects(obs.the_geom_point, area.the_geom)
        WHERE obs.cd_ref = ANY(:taxonsList) AND area.id_type IN 
            (SELECT id_type FROM atlas.vm_bib_areas_types 
            WHERE type_code = ANY(:list_id_type))
        ORDER BY area.area_name ASC
    """
    results = connection.execute(
        text(sql), taxonsList=taxons, list_id_type=current_app.config["TYPE_TERRITOIRE"]
    )
    municipalities = list()
    for r in results:
        municipality = {"id_area": r.id_area, "area_name": r.area_name}
        municipalities.append(municipality)
    return municipalities
