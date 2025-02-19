import json

from geojson import Feature, FeatureCollection
from sqlalchemy.sql import text, func, any_

from atlas.modeles.entities.vmObservations import VmObservationsMailles
from atlas.modeles.entities.vmAreas import VmAreas
from atlas.modeles.entities.tMaillesTerritoire import TMaillesTerritoire
from atlas.modeles.entities.vmTaxons import VmTaxons
from atlas.modeles.utils import deleteAccent, findPath


def getObservationsMaillesTerritorySpecies(session, cd_ref):
    """
    Retourne les mailles et le nombre d'observation par maille pour un taxon et ses enfants
    sous forme d'un geojson
    """
    query = func.atlas.find_all_taxons_childs(cd_ref)
    taxons_ids = session.scalars(query).all()
    taxons_ids.append(cd_ref)

    query = (
        session.query(
            VmObservationsMailles.id_maille,
            TMaillesTerritoire.geojson_maille,
            func.max(VmObservationsMailles.annee).label("last_obs_year"),
            func.sum(VmObservationsMailles.nbr).label("obs_nbr"),
            VmObservationsMailles.type_code,
            VmTaxons.cd_ref,
            VmTaxons.nom_vern,
            VmTaxons.lb_nom,
        )
        .join(
            TMaillesTerritoire,
            TMaillesTerritoire.id_maille == VmObservationsMailles.id_maille,
        )
        .join(
            VmTaxons,
            VmTaxons.cd_ref == VmObservationsMailles.cd_ref,
        )
        .filter(VmObservationsMailles.cd_ref == any_(taxons_ids))
        .group_by(
            VmObservationsMailles.id_maille,
            TMaillesTerritoire.geojson_maille,
            VmObservationsMailles.type_code,
            VmTaxons.cd_ref,
            VmTaxons.nom_vern,
            VmTaxons.lb_nom,
        )
    )

    return FeatureCollection(
        [
            Feature(
                id=o.id_maille,
                geojson_maille=json.loads(o.geojson_maille),
                id_maille=o.id_maille,
                type_code=o.type_code,
                nb_observations=int(o.obs_nbr),
                last_observation=o.last_obs_year,
                cd_ref=o.cd_ref,
                taxon=format_taxon_name(o),
            )
            for o in query.all()
        ]
    )


def format_taxon_name(observation):
    if observation.nom_vern:
        inter = observation.nom_vern.split(",")
        taxon_name_formated = inter[0] + " | <i>" + observation.lb_nom + "</i>"
    else:
        taxon_name_formated = "<i>" + observation.lb_nom + "</i>"
    return taxon_name_formated


def getObservationsMaillesChilds(session, cd_ref, year_min=None, year_max=None):
    """
    Retourne les mailles et le nombre d'observation par maille pour un taxon et ses enfants
    sous forme d'un geojson
    """
    query = func.atlas.find_all_taxons_childs(cd_ref)
    taxons_ids = session.scalars(query).all()
    taxons_ids.append(cd_ref)

    query = (
        session.query(
            VmObservationsMailles.id_maille,
            VmAreas.area_geojson,
            func.max(VmObservationsMailles.annee).label("last_obs_year"),
            func.sum(VmObservationsMailles.nbr).label("obs_nbr"),
            VmObservationsMailles.type_code,
        )
        .join(
            VmAreas,
            VmAreas.id_area == VmObservationsMailles.id_maille,
        )
        .filter(VmObservationsMailles.cd_ref == any_(taxons_ids))
        .group_by(
            VmObservationsMailles.id_maille,
            VmAreas.area_geojson,
            VmObservationsMailles.type_code,
        )
    )
    if year_min and year_max:
        query = query.filter(VmObservationsMailles.annee.between(year_min, year_max))

    return FeatureCollection(
        [
            Feature(
                id=o.id_maille,
                geometry=json.loads(o.area_geojson),
                properties={
                    "id_maille": o.id_maille,
                    "type_code": o.type_code,
                    "nb_observations": int(o.obs_nbr),
                    "last_observation": o.last_obs_year,
                },
            )
            for o in query.all()
        ]
    )


def territoryObservationsMailles(connection):
    sql = """
SELECT obs.cd_ref, obs.id_maille, obs.nbr, obs.type_code,
       tax.lb_nom, tax.nom_vern, tax.group2_inpn,
       medias.url, medias.chemin, medias.id_media,
       st_asgeojson(m.geojson_maille) AS geom
FROM atlas.vm_observations_mailles obs
         JOIN atlas.vm_taxons tax ON tax.cd_ref = obs.cd_ref
         JOIN atlas.t_mailles_territoire m ON m.id_maille=obs.id_maille
         LEFT JOIN atlas.vm_medias medias
                   ON medias.cd_ref = obs.cd_ref AND medias.id_type = 1
GROUP BY obs.cd_ref, obs.id_maille, obs.nbr,
         tax.lb_nom, tax.nom_vern, tax.group2_inpn,
         medias.url, medias.chemin, medias.id_media,
         m.geojson_maille,
         obs.type_code
  """

    observations = connection.execute(text(sql))
    obsList = list()
    for o in observations:
        if o.nom_vern:
            inter = o.nom_vern.split(",")
            taxon = inter[0] + " | <i>" + o.lb_nom + "</i>"
        else:
            taxon = "<i>" + o.lb_nom + "</i>"
        temp = {
            "id_maille": o.id_maille,
            "type_code": o.type_code,
            "cd_ref": o.cd_ref,
            "nb_observations": o.nbr,
            "taxon": taxon,
            "geojson_maille": json.loads(o.geom),
            "group2_inpn": deleteAccent(o.group2_inpn),
            "pathImg": findPath(o),
        }
        obsList.append(temp)
    return obsList


# last observation for index.html
def lastObservationsMailles(connection, mylimit, idPhoto):
    sql = """
        SELECT obs.*,
        tax.lb_nom, tax.nom_vern, tax.group2_inpn,
        o.dateobs, o.altitude_retenue, o.id_observation,
        medias.url, medias.chemin, medias.id_media,
        vla.area_geojson
        FROM atlas.vm_observations_mailles obs
        JOIN atlas.vm_taxons tax ON tax.cd_ref = obs.cd_ref
        JOIN atlas.vm_observations o ON o.id_observation=ANY(obs.id_observations)
        JOIN atlas.vm_cor_area_synthese m ON m.id_synthese=o.id_observation
        JOIN atlas.vm_l_areas vla ON vla.id_area=m.id_area
        LEFT JOIN atlas.vm_medias medias
            ON medias.cd_ref = obs.cd_ref AND medias.id_type = 1
        WHERE  o.dateobs >= (CURRENT_TIMESTAMP - INTERVAL :thislimit) AND vla.id_type = 34
        ORDER BY o.dateobs DESC
        LIMIT 1000
    """

    observations = connection.execute(text(sql), thislimit=mylimit, thisID=idPhoto)
    obsList = list()
    for o in observations:
        if o.nom_vern:
            inter = o.nom_vern.split(",")
            taxon = inter[0] + " | <i>" + o.lb_nom + "</i>"
        else:
            taxon = "<i>" + o.lb_nom + "</i>"
        temp = {
            "id_observation": o.id_observation,
            "id_maille": o.id_maille,
            "type_code": o.type_code,
            "cd_ref": o.cd_ref,
            "dateobs": o.dateobs,
            "altitude_retenue": o.altitude_retenue,
            "taxon": taxon,
            "geojson_maille": json.loads(o.area_geojson),
            "group2_inpn": deleteAccent(o.group2_inpn),
            "pathImg": findPath(o),
            "id_media": o.id_media,
        }
        obsList.append(temp)

    return obsList


def lastObservationsCommuneMaille(connection, obs_limit, insee_code):
    sql = """
        SELECT
            obs.id_observations, obs.cd_ref, obs.type_code, obs.nbr, c.insee,
            COALESCE(t.nom_vern || ' | ', '') || t.lb_nom  AS display_name,
            vla.the_geom AS l_geom,
            t.nom_vern,
            vla.area_geojson, obs.id_maille
        FROM atlas.vm_observations_mailles obs
            JOIN atlas.vm_l_areas AS vla ON vla.id_area = obs.id_maille
            JOIN atlas.vm_communes AS c
                  ON ST_Intersects(vla.the_geom, c.the_geom) AND NOT ST_Touches(vla.the_geom, c.the_geom)
            JOIN atlas.vm_taxons AS t
                ON obs.cd_ref = t.cd_ref
        WHERE c.insee = :inseeCode
        LIMIT :obsLimit
    """
    results = connection.execute(text(sql), inseeCode=insee_code, obsLimit=obs_limit)
    observations = list()
    for r in results:
        infos = {
            "cd_ref": r.cd_ref,
            "insee": r.insee,
            "taxon": r.display_name,
            "geojson_maille": json.loads(r.area_geojson),
            "id_maille": r.id_maille,
            "id_observation": r.id_observations,
            "nb_observations": r.nbr,
            "type_code": r.type_code,
        }
        observations.append(infos)
    return observations


# Use for API
def getObservationsTaxonCommuneMaille(connection, insee, cd_ref):
    sql = """
        SELECT
            o.cd_ref,
            o.id_maille,
            o.type_code,
            o.annee,
            vla.area_geojson,
            vla.the_geom,
            t.cd_ref,
            t.nom_vern,
            t.lb_nom
        FROM atlas.vm_observations_mailles AS o
            JOIN atlas.vm_taxons AS t ON t.cd_ref = o.cd_ref
            JOIN atlas.vm_l_areas AS vla ON vla.id_area = o.id_maille
            JOIN atlas.vm_communes AS c ON c.insee = :thisInsee AND st_intersects(c.the_geom, vla.the_geom) AND NOT st_touches(c.the_geom, vla.the_geom)
        WHERE o.cd_ref = :thiscdref
        ORDER BY id_maille
    """
    observations = connection.execute(text(sql), thisInsee=insee, thiscdref=cd_ref)
    tabObs = list()
    for o in observations:
        temp = {
            "id_maille": o.id_maille,
            "cd_ref": o.cd_ref,
            "taxon": format_taxon_name(o),
            "type_code": o.type_code,
            "nb_observations": 1,
            "annee": o.annee,
            "geojson_maille": json.loads(o.area_geojson),
        }
        tabObs.append(temp)

    return tabObs
