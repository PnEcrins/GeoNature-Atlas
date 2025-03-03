import json

from geojson import Feature, FeatureCollection
from sqlalchemy.sql import text, func, any_, extract

from atlas.modeles.entities.vmObservations import VmObservations, VmObservationsMailles
from atlas.modeles.entities.vmAreas import VmAreas
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
            VmAreas.area_geojson,
            func.max(extract("year", VmObservations.dateobs)).label("last_obs_year"),
            VmObservationsMailles.nbr.label("obs_nbr"),
            VmObservationsMailles.type_code,
        )
        .join(
            VmObservations,
            VmObservations.id_observation == any_(VmObservationsMailles.id_observations),
        )
        .join(
            VmAreas,
            VmAreas.id_area == VmObservationsMailles.id_maille,
        )
        .filter(VmObservations.cd_ref == any_(taxons_ids))
        .group_by(
            VmObservationsMailles.id_maille,
            VmAreas.area_geojson,
            VmObservationsMailles.nbr,
            VmObservationsMailles.type_code,
        )
    )

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
            func.max(extract("year", VmObservations.dateobs)).label("last_obs_year"),
            func.count(VmObservations.id_observation).label("obs_nbr"),
            VmObservationsMailles.type_code,
        )
        .join(
            VmObservations,
            VmObservations.id_observation == any_(VmObservationsMailles.id_observations),
        )
        .join(
            VmAreas,
            VmAreas.id_area == VmObservationsMailles.id_maille,
        )
        .filter(VmObservations.cd_ref == any_(taxons_ids))
        .group_by(
            VmObservationsMailles.id_maille,
            VmAreas.area_geojson,
            VmObservationsMailles.nbr,
            VmObservationsMailles.type_code,
        )
    )
    if year_min and year_max:
        query = query.filter(
            VmObservations.dateobs.between(str(year_min) + "-01-01", str(year_max) + "-12-31")
        )

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
SELECT
    obs.id_maille,
    obs.nbr AS obs_nbr,
    obs.type_code,
    area.area_geojson,
    MAX(extract(YEAR FROM o.dateobs)) AS last_observation
FROM atlas.vm_observations_mailles obs
        JOIN atlas.vm_l_areas area ON area.id_area=obs.id_maille
        JOIN atlas.vm_observations AS o ON o.id_observation = ANY(obs.id_observations)
GROUP BY obs.id_maille, obs.nbr, obs.type_code, area.area_geojson
  """

    observations = connection.execute(text(sql))
    return FeatureCollection(
        [
            Feature(
                id=o.id_maille,
                geometry=json.loads(o.area_geojson),
                properties={
                    "id_maille": o.id_maille,
                    "type_code": o.type_code,
                    "nb_observations": int(o.obs_nbr),
                    "last_observation": o.last_observation,
                },
            )
            for o in observations
        ]
    )


# last observation for index.html
def lastObservationsMailles(connection, mylimit, idPhoto):
    sql = """
        SELECT obs.*,
        tax.lb_nom, tax.nom_vern, tax.group2_inpn,
        o.dateobs, o.altitude_retenue, o.id_observation, o.cd_ref,
        medias.url, medias.chemin, medias.id_media,
        vla.area_geojson
        FROM atlas.vm_observations_mailles obs
        JOIN atlas.vm_observations o ON o.id_observation=ANY(obs.id_observations)
        JOIN atlas.vm_taxons tax ON tax.cd_ref = o.cd_ref
        JOIN atlas.vm_l_areas vla ON vla.id_area=obs.id_maille
        LEFT JOIN atlas.vm_medias medias
            ON medias.cd_ref = o.cd_ref AND medias.id_type = :thisID
        WHERE  o.dateobs >= (CURRENT_TIMESTAMP - INTERVAL :thislimit)
        ORDER BY o.dateobs DESC
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


def lastObservationsAreaMaille(connection, obs_limit, id_area):
    sql = """
WITH obs_in_area AS (
    SELECT
        obs.id_observation,
        obs.cd_ref,
        date_part('year', obs.dateobs) AS annee
    FROM atlas.vm_observations obs
             JOIN atlas.vm_cor_area_synthese AS cas  ON cas.id_synthese = obs.id_observation
    WHERE cas.id_area = :idAreaCode
)
SELECT
    obs_in_area.id_observation,
    obs_in_area.cd_ref,
    COALESCE(t.nom_vern || ' | ', '') || t.lb_nom  AS display_name,
    obs_in_area.annee,
    obs.type_code,
    obs.id_maille,
    vla.area_geojson AS geojson_4326
FROM obs_in_area
         JOIN atlas.vm_observations_mailles obs ON obs_in_area.id_observation = ANY(obs.id_observations)
         JOIN atlas.vm_l_areas vla ON vla.id_area=obs.id_maille
         JOIN atlas.vm_taxons AS t ON t.cd_ref = obs_in_area.cd_ref
ORDER BY annee DESC
LIMIT :obsLimit;
    """
    results = connection.execute(text(sql), idAreaCode=id_area, obsLimit=obs_limit)
    observations = list()
    for r in results:
        infos = {
            "cd_ref": r.cd_ref,
            "taxon": r.display_name,
            "geojson_maille": json.loads(r.geojson_4326),
            "id_maille": r.id_maille,
            "id_observation": r.id_observation,
            "type_code": r.type_code,
        }
        observations.append(infos)
    return observations


# Use for API
def getObservationsTaxonAreaMaille(connection, id_area, cd_ref):
    sql = """
WITH obs_in_area AS (
    SELECT
        obs.id_observation,
        obs.cd_ref,
        date_part('year', obs.dateobs) AS annee
    FROM atlas.vm_observations obs
             JOIN atlas.vm_cor_area_synthese AS cas  ON cas.id_synthese = obs.id_observation
    WHERE cas.id_area = :thisIdArea AND obs.cd_ref = :thiscdref
)
SELECT
    obs_in_area.cd_ref,
    obs_in_area.annee,
    obs.type_code,
    obs.id_maille,
    vla.area_geojson,
    t.nom_vern,
    t.lb_nom
FROM obs_in_area
         JOIN atlas.vm_observations_mailles obs ON obs_in_area.id_observation = ANY(obs.id_observations)
         JOIN atlas.vm_l_areas vla ON vla.id_area=obs.id_maille
         JOIN atlas.vm_taxons AS t ON t.cd_ref = obs_in_area.cd_ref
ORDER BY annee DESC;
    """
    observations = connection.execute(text(sql), thisIdArea=id_area, thiscdref=cd_ref)
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
