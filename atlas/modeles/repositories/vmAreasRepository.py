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

#
# def last_observations_area_maille(session, myLimit, idArea):
#     """Fonction a priori non utilisée à supprimer"""
#     q_last_obs = (
#         session.query(
#             # VmObservations.cd_ref.label("cd_ref"),
#             # VmObservations.dateobs.label("dateobs"),
#             # VmTaxons.lb_nom.label("lb_nom"),
#             # VmTaxons.nom_vern.label("nom_vern"),
#             # VmObservations.the_geom_point.label("the_geom_point"),
#             VmObservations.cd_ref,
#             VmObservations.dateobs,
#             VmTaxons.lb_nom,
#             VmTaxons.nom_vern,
#             VmObservations.the_geom_point,
#         )
#         .join(
#             VmCorAreaObservation,
#             VmObservations.id_observation == VmCorAreaObservation.id_observation,
#         )
#         .join(VmAreas, VmAreas.id_area == VmCorAreaObservation.id_area)
#         .join(VmTaxons, VmTaxons.cd_ref == VmObservations.cd_ref)
#         .filter(VmAreas.id_area == idArea)
#         .order_by(VmObservations.dateobs.desc())
#         .limit(myLimit)
#         .subquery()
#     )
#     current_app.logger.debug(
#         "<last_observations_area_maille> subquery q_last_obs: {}".format(q_last_obs)
#     )
#
#     q_mailles_obs = (
#         session.query(
#             TGrid.id_maille,
#             q_last_obs.c.lb_nom,
#             q_last_obs.c.cd_ref,
#             q_last_obs.c.nom_vern,
#             func.st_asgeojson(TGrid.the_geom).label("geojson_maille"),
#         )
#         .join(q_last_obs, q_last_obs.c.the_geom_point.st_intersects(TGrid.the_geom))
#         .group_by(
#             q_last_obs.c.lb_nom,
#             q_last_obs.c.cd_ref,
#             q_last_obs.c.nom_vern,
#             TGrid.id_maille,
#             TGrid.the_geom,
#         )
#     )
#
#     current_app.logger.debug(
#         "<last_observations_area_maille> query q_mailles_obs: {}".format(q_mailles_obs)
#     )
#     current_app.logger.debug(
#         "<last_observations_area_maille> start query: {}".format(datetime.now())
#     )
#     result = q_mailles_obs.all()
#     current_app.logger.debug(
#         "<last_observations_area_maille> start loop: {}".format(datetime.now())
#     )
#     obsList = list()
#     for o in result:
#         if o.nom_vern:
#             taxon = o.nom_vern + " | </i>" + o.lb_nom + "</i>"
#         else:
#             taxon = "</i>" + o.lb_nom + "</i>"
#         temp = {
#             "cd_ref": o.cd_ref,
#             "taxon": taxon,
#             "geojson_maille": json.loads(o.geojson_maille),
#             "id_maille": o.id_maille,
#         }
#         obsList.append(temp)
#     current_app.logger.debug("<last_observations_area_maille> end loop: {}".format(datetime.now()))
#     return obsList

#
# def get_observers_area(session, idArea):
#     q_list_observers = (
#         session.query(
#             func.trim(func.unnest(func.string_to_array(VmObservations.observateurs, ","))).label(
#                 "observateurs"
#             )
#         )
#         .join(
#             VmCorAreaObservation,
#             VmObservations.id_observation == VmCorAreaObservation.id_observation,
#         )
#         .filter(VmCorAreaObservation.id_area == idArea)
#     ).subquery()
#
#     query = session.query(q_list_observers.c.observateurs).group_by(
#         q_list_observers.c.observateurs
#     )
#     return query.all()


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
    print(limit)
    query = query.limit(limit)
    current_app.logger.debug("<search_area_by_type> query {}".format(query))

    areaList = list()
    for r in query.all():
        temp = {"label": r[1], "value": r[0]}
        areaList.append(temp)
    return areaList

#
# def get_areas_observations(session, id_area):
#     query = (
#         session.query(
#             VmObservations.id_observation,
#             VmTaxref.nom_vern,
#             VmTaxref.lb_nom,
#             VmTaxref.group2_inpn,
#             VmObservations.dateobs,
#             VmObservations.observateurs,
#             func.st_asgeojson(VmObservations.the_geom_point).label("geometry"),
#         )
#         .join(VmTaxref, VmTaxref.cd_nom == VmObservations.cd_ref)
#         .join(
#             VmCorAreaObservation,
#             VmObservations.id_observation == VmCorAreaObservation.id_observation,
#         )
#         .filter(VmCorAreaObservation.id_area == id_area)
#     ).all()
#     result = []
#     for r in query:
#         temp = r._asdict()
#         temp["geometry"] = json.loads(r.geometry or "{}")
#         temp["dateobs"] = str(r.dateobs)
#         temp["group2_inpn"] = utils.deleteAccent(r.group2_inpn)
#         result.append(temp)
#     return result


# def get_areas_observations_by_cdnom(session, id_area):
#     req = (
#         session.query(
#             VmObservations.id_observation,
#             VmTaxref.nom_vern,
#             VmTaxref.lb_nom,
#             VmTaxref.group2_inpn,
#             VmObservations.dateobs,
#             VmObservations.observateurs,
#             func.st_asgeojson(VmObservations.the_geom_point).label("geometry"),
#         )
#         .join(VmTaxref, VmTaxref.cd_nom == VmObservations.cd_ref)
#         .join(
#             VmCorAreaObservation,
#             VmObservations.id_observation == VmCorAreaObservation.id_observation,
#         )
#         .filter(VmCorAreaObservation.id_area == id_area)
#     ).all()
#     result = []
#     for r in req:
#         temp = r._asdict()
#         temp["geometry"] = json.loads(r.geometry or "{}")
#         temp["dateobs"] = str(r.dateobs)
#         temp["group2_inpn"] = utils.deleteAccent(r.group2_inpn)
#         result.append(temp)
#     return result


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


def get_area_taxa(session, id_area):
    query = (
        session.query(
            VmTaxons.cd_ref,
            VmTaxons.nom_vern,
            VmTaxons.nom_complet_html,
            VmTaxons.group2_inpn,
            VmTaxons.patrimonial,
            VmTaxons.protection_stricte,
            VmMedias.url,
            VmMedias.chemin,
            func.count(VmObservations.id_observation).label("nb_obs"),
            func.max(func.extract("year", VmObservations.dateobs)).label("last_obs"),
        )
        .join(VmTaxons, VmTaxons.cd_ref == VmObservations.cd_ref)
        .join(
            VmCorAreaObservation,
            VmObservations.id_observation == VmCorAreaObservation.id_observation,
        )
        .outerjoin(
            VmMedias,
            and_(
                VmMedias.cd_ref == VmObservations.cd_ref,
                VmMedias.id_type == current_app.config["ATTR_MAIN_PHOTO"],
            ),
        )
        .filter(VmCorAreaObservation.id_area == id_area)
        .group_by(
            VmTaxons.cd_ref,
            VmTaxons.nom_vern,
            VmTaxons.nom_complet_html,
            VmTaxons.group2_inpn,
            VmTaxons.patrimonial,
            VmTaxons.protection_stricte,
            VmMedias.url,
            VmMedias.chemin,
        )
        .order_by(-func.count(VmObservations.id_observation))
    )
    current_app.logger.debug("<get_area_taxa> QUERY: {}".format(query))
    current_app.logger.debug("<get_area_taxa> start loop: {}".format(datetime.now()))
    result = []
    nbObsTotal = 0
    for r in query.all():
        temp = r._asdict()
        temp["group2_inpn"] = utils.deleteAccent(r.group2_inpn)
        temp["path"] = utils.findPath(r)
        nbObsTotal = nbObsTotal + r.nb_obs
        result.append(temp)
    current_app.logger.debug("<get_area_taxa> end loop: {}".format(datetime.now()))
    return {"taxons": result, "nbObsTotal": nbObsTotal}


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
    MAX(extract(YEAR FROM o.dateobs)) AS yearmax
    -- z.id_parent,
    -- (SELECT area_name FROM atlas.vm_l_areas WHERE id_area = z.id_parent) AS area_parent_name,
    -- (SELECT type.type_name
    --  FROM atlas.vm_l_areas AS area
    --     JOIN ref_geo.bib_areas_types type
    --         ON type.id_type = area.id_zoning_type
    --  WHERE area.id_area = z.id_parent) AS area_parent_type_name
FROM atlas.vm_observations o JOIN atlas.vm_l_areas z ON z.id_area = o.id_area
WHERE o.id_area = :id_area
--GROUP BY z.id_parent
    """

    result = connection.execute(text(sql), id_area=id_area)
    info_area = dict()
    for r in result:
        info_area = {
            "yearmin": r.yearmin,
            "yearmax": r.yearmax,
            # "id_parent": r.id_parent,
            # "parent_name": r.area_parent_name,
            # "parent_type_name": r.area_parent_type_name,
        }

    return info_area
