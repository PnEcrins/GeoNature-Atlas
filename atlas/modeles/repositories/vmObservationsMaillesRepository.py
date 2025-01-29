import json

from geojson import Feature, FeatureCollection
from sqlalchemy.sql import text, func, any_

from atlas.modeles.entities.vmObservations import VmObservationsMailles
from atlas.modeles.entities.tMaillesTerritoire import TMaillesTerritoire
from atlas.modeles.utils import deleteAccent, findPath


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
            TMaillesTerritoire.geojson_maille,
            func.max(VmObservationsMailles.annee).label("last_obs_year"),
            func.sum(VmObservationsMailles.nbr).label("obs_nbr"),
        )
        .join(
            TMaillesTerritoire,
            TMaillesTerritoire.id_maille == VmObservationsMailles.id_maille,
        )
        .filter(VmObservationsMailles.cd_ref == any_(taxons_ids))
        .group_by(
            VmObservationsMailles.id_maille,
            TMaillesTerritoire.geojson_maille,
        )
    )
    if year_min and year_max:
        query = query.filter(VmObservationsMailles.annee.between(year_min, year_max))

    return FeatureCollection(
        [
            Feature(
                id=o.id_maille,
                geometry=json.loads(o.geojson_maille),
                properties={
                    "id_maille": o.id_maille,
                    "nb_observations": int(o.obs_nbr),
                    "last_observation": o.last_obs_year,
                },
            )
            for o in query.all()
        ]
    )


# last observation for index.html
def lastObservationsMailles(connection, mylimit, idPhoto):
    sql = """
        SELECT obs.*,
        tax.lb_nom, tax.nom_vern, tax.group2_inpn,
        o.dateobs, o.altitude_retenue, o.id_observation,
        medias.url, medias.chemin, medias.id_media,
        m.geojson_maille
        FROM atlas.vm_observations_mailles obs
        JOIN atlas.vm_taxons tax ON tax.cd_ref = obs.cd_ref
        JOIN atlas.vm_observations o ON o.id_observation=ANY(obs.id_observations)
        JOIN atlas.t_mailles_territoire m ON m.id_maille=obs.id_maille
        LEFT JOIN atlas.vm_medias medias
            ON medias.cd_ref = obs.cd_ref AND medias.id_type = :thisID
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
            "cd_ref": o.cd_ref,
            "dateobs": o.dateobs,
            "altitude_retenue": o.altitude_retenue,
            "taxon": taxon,
            "geojson_maille": json.loads(o.geojson_maille),
            "group2_inpn": deleteAccent(o.group2_inpn),
            "pathImg": findPath(o),
            "id_media": o.id_media,
        }
        obsList.append(temp)
    return obsList


def lastObservationsZoneMaille(connection, obs_limit, id_zone):
    sql = """
    WITH last_obs AS (
        SELECT
            obs.id_observation, obs.cd_ref, obs.dateobs,
            COALESCE(t.nom_vern || ' | ', '') || t.lb_nom  AS display_name,
            obs.the_geom_point AS l_geom
        FROM atlas.vm_observations AS obs
            JOIN atlas.zoning AS zone
                ON ST_Intersects(obs.the_geom_point, zone.the_geom_4326)
            JOIN atlas.vm_taxons AS t
                ON obs.cd_ref = t.cd_ref
        WHERE zone.id_zone = :idZoneCode
        ORDER BY obs.dateobs DESC
        LIMIT :obsLimit
    )
    SELECT
        l.id_observation, l.cd_ref, l.display_name, m.id_maille, m.geojson_maille
    FROM atlas.t_mailles_territoire AS m
        JOIN last_obs AS l
            ON st_intersects(m.the_geom, l.l_geom)
    GROUP BY l.id_observation, l.cd_ref, l.display_name, m.id_maille, m.geojson_maille
    ORDER BY l.display_name
    """
    results = connection.execute(text(sql), idZoneCode=id_zone, obsLimit=obs_limit)
    observations = list()
    for r in results:
        # taxon = (r.nom_vern + " | " + r.lb_nom) if r.nom_vern else r.lb_nom
        infos = {
            "cd_ref": r.cd_ref,
            "taxon": r.display_name,
            "geojson_maille": json.loads(r.geojson_maille),
            "id_maille": r.id_maille,
            "id_observation": r.id_observation,
        }
        observations.append(infos)
    return observations


# Use for API
def getObservationsTaxonZoneMaille(connection, id_zone, cd_ref):
    sql = """
        SELECT
            o.cd_ref,
            t.id_maille,
            t.geojson_maille,
            extract(YEAR FROM o.dateobs)::INT AS annee
        FROM atlas.vm_observations AS o
            JOIN atlas.zoning AS c
                ON ST_INTERSECTS(o.the_geom_point, c.the_geom_4326)
            JOIN atlas.t_mailles_territoire AS t
                ON ST_INTERSECTS(t.the_geom, o.the_geom_point)
        WHERE o.cd_ref = :thiscdref
            AND c.id_zone = :thisIdZone
        ORDER BY id_maille
    """
    observations = connection.execute(text(sql), thisIdZone=id_zone, thiscdref=cd_ref)
    tabObs = list()
    for o in observations:
        temp = {
            "id_maille": o.id_maille,
            "nb_observations": 1,
            "annee": o.annee,
            "geojson_maille": json.loads(o.geojson_maille),
        }
        tabObs.append(temp)

    return tabObs
