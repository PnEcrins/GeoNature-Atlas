# -*- coding:utf-8 -*-

import ast
import json
from datetime import datetime

from flask import current_app
from sqlalchemy import or_, and_, case
from sqlalchemy.sql.expression import func, text

from atlas.modeles import utils
from atlas.modeles.entities.tGrid import TGrid
from atlas.modeles.entities.vmAreas import VmAreas, VmBibAreasTypes
from atlas.modeles.entities.vmMedias import VmMedias
from atlas.modeles.entities.vmObservations import VmObservations
from atlas.modeles.entities.vmTaxons import VmTaxons
from atlas.modeles.entities.vmTaxref import VmTaxref


def area_types(session):
    query = session.query(
        VmBibAreasTypes.id_type,
        VmBibAreasTypes.type_code,
        VmBibAreasTypes.type_name,
        VmBibAreasTypes.type_desc,
    )
    return query.all()


def get_id_area(session, type_code, area_code):
    try:
        query = (
            session.query(VmAreas.id_area)
            .join(VmBibAreasTypes, VmBibAreasTypes.id_type == VmAreas.id_type)
            .filter(
                and_(
                    VmAreas.area_code.ilike(area_code), VmBibAreasTypes.type_code.ilike(type_code)
                )
            )
        )
        current_app.logger.debug("<get_id_area> query: {}".format(query))
        result = query.one()
        return result.id_area
    except Exception as e:
        current_app.logger.error("<get_id_area> error {}".format(e))


def search_area_by_type(session, search, type_code, limit=50):
    query = (
        session.query(
            VmAreas.area_code,
            func.concat(VmAreas.area_name, " - [code <i>", VmAreas.area_code, "</i>]"),
        )
        .join(VmBibAreasTypes, VmBibAreasTypes.id_type == VmAreas.id_type)
        .filter(
            and_(VmBibAreasTypes.type_code == type_code),
            (
                or_(
                    VmAreas.area_name.ilike("%" + search + "%"),
                    VmAreas.area_code.ilike("%" + search + "%"),
                )
            ),
        )
    )

    query = query.limit(limit)
    current_app.logger.debug("<search_area_by_type> query {}".format(query))

    areaList = list()
    for r in query.all():
        temp = {"label": r[1], "value": r[0]}
        areaList.append(temp)
    return areaList


def get_areas_grid_observations_by_cdnom(session, id_area, cd_nom):
    query = (
        session.query(
            TGrid.id_maille,
            func.extract("year", VmObservations.dateobs).label("annee"),
            func.st_asgeojson(TGrid.the_geom, 4326).label("geojson_maille"),
        )
        .join(VmAreas, VmAreas.the_geom.st_intersects(VmObservations.the_geom_point))
        .join(TGrid, TGrid.the_geom.st_intersects(VmObservations.the_geom_point))
        .filter(and_(VmObservations.cd_ref == cd_nom, VmAreas.area_code == id_area))
        .order_by(TGrid.id_maille)
    )

    current_app.logger.debug("<get_areas_grid_observations_by_cdnom> QUERY: {}".format(query))
    tabObs = list()
    for o in query.all():
        temp = {
            "id_maille": o.id_maille,
            "nb_observations": 1,
            "annee": o.annee,
            "geojson_maille": json.loads(o.geojson_maille),
        }
        tabObs.append(temp)

    return tabObs


def get_surrounding_areas(session, id_area):
    subquery = session.query(VmAreas.the_geom).filter(VmAreas.id_area == id_area).subquery()

    query = (
        session.query(
            VmAreas.id_area,
            VmAreas.area_name,
            VmAreas.area_code,
            VmBibAreasTypes.type_code,
            VmBibAreasTypes.type_name,
        )
        .join(VmBibAreasTypes, VmAreas.id_type == VmBibAreasTypes.id_type)
        .filter(and_(VmAreas.the_geom.st_intersects(subquery.c.the_geom)))
    )

    return query.all()


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
