# -*- coding:utf-8 -*-

import ast

from sqlalchemy import distinct
from sqlalchemy.sql import text
from sqlalchemy.sql.expression import func

from atlas.modeles.entities.vmCommunes import VmCommunes


def getAllCommunes(session):
    req = session.query(distinct(VmCommunes.commune_maj), VmCommunes.insee).all()
    communeList = list()
    for r in req:
        temp = {"label": r[0], "value": r[1]}
        communeList.append(temp)
    return communeList


def searchMunicipalities(session, search, limit=50):
    like_search = "%" + search.replace(" ", "%") + "%"

    query = (
        session.query(
            distinct(VmCommunes.commune_maj),
            VmCommunes.insee,
            func.length(VmCommunes.commune_maj),
        )
        .filter(func.unaccent(VmCommunes.commune_maj).ilike(func.unaccent(like_search)))
        .order_by(VmCommunes.commune_maj)
        .limit(limit)
    )
    results = query.all()

    return [{"label": r[0], "value": r[1]} for r in results]


def getCommuneFromInsee(connection, insee):
    sql = """
        SELECT c.commune_maj,
           c.insee,
           c.commune_geojson
        FROM atlas.vm_communes c
        WHERE c.insee = :thisInsee
    """
    req = connection.execute(text(sql), thisInsee=insee)
    communeObj = dict()
    for r in req:
        communeObj = {
            "areaName": r.commune_maj,
            "areaCode": str(r.insee),
            "areaGeoJson": ast.literal_eval(r.commune_geojson),
        }
    return communeObj


def getCommunesObservationsChilds(connection, cd_ref):
    sql = "SELECT * FROM atlas.find_all_taxons_childs(:thiscdref) AS taxon_childs(cd_nom)"
    results = connection.execute(text(sql), thiscdref=cd_ref)
    taxons = [cd_ref]
    for r in results:
        taxons.append(r.cd_nom)

    sql = """
        SELECT DISTINCT
            com.commune_maj,
            com.insee
        FROM atlas.vm_observations AS obs
            JOIN atlas.vm_communes AS com
                ON obs.insee = com.insee
        WHERE obs.cd_ref = ANY(:taxonsList)
        ORDER BY com.commune_maj ASC
    """
    results = connection.execute(text(sql), taxonsList=taxons)
    municipalities = list()
    for r in results:
        municipality = {"insee": r.insee, "commune_maj": r.commune_maj}
        municipalities.append(municipality)
    return municipalities


def getCommunesObservationsChildsMailles(connection, cd_ref):
    sql = """
SELECT
    DISTINCT vla.area_code AS insee,
             vla.area_name
FROM atlas.vm_observations obs
         JOIN atlas.vm_cor_area_synthese AS cas ON cas.id_synthese = obs.id_observation
         JOIN atlas.vm_l_areas vla ON cas.id_area = vla.id_area
WHERE cas.type_code = 'COM'
  AND (obs.cd_ref = ANY(SELECT * FROM atlas.find_all_taxons_childs(:thiscdref) AS taxon_childs(cd_nom))
           OR obs.cd_ref = :thiscdref)
ORDER BY vla.area_name ASC;
    """
    req = connection.execute(text(sql), thiscdref=cd_ref)
    listCommunes = list()
    for r in req:
        temp = {"insee": r.insee, "commune_maj": r.area_name}
        listCommunes.append(temp)
    return listCommunes
