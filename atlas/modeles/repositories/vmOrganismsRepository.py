import json

from geojson import Feature, FeatureCollection
from sqlalchemy.sql import text, func, or_

from atlas.modeles.entities import vmOrganisms


def statOrganism(connection, id_organism):
    # Fiche organism
    sql = """SELECT count(DISTINCT cd_ref) AS nb_taxons, SUM(nb_observations) AS nb_obs,
    nom_organism, url_organism, url_logo, adresse_organism, cp_organism, ville_organism,
    tel_organism, email_organism
    FROM atlas.vm_cor_taxon_organism o
    WHERE o.id_organism = :thisidorganism
    GROUP BY nom_organism, url_organism, url_logo, adresse_organism, cp_organism, ville_organism,
    tel_organism, email_organism"""
    req = connection.execute(text(sql), thisidorganism=id_organism)
    StatsOrga = dict()
    for r in req:
        StatsOrga = {
            "nb_taxons": r.nb_taxons,
            "nb_obs": r.nb_obs,
            "nom_organism": r.nom_organism,
            "url_organism": r.url_organism,
            "url_logo": r.url_logo,
            "adresse_organism": r.adresse_organism,
            "cp_organism": r.cp_organism,
            "ville_organism": r.ville_organism,
            "tel_organism": r.tel_organism,
            "email_organism": r.email_organism,
        }

    return StatsOrga


def topObsOrganism(connection, id_organism):
    # Stats avancées organism
    sql = """SELECT cd_ref, nb_observations as nb_obs_taxon 
    FROM atlas.vm_cor_taxon_organism o
    WHERE o.id_organism = :thisidorganism
    ORDER BY nb_observations DESC
    LIMIT 3
    """
    req = connection.execute(text(sql), thisidorganism=id_organism)
    topSpecies = list()
    for r in req:
        temp = {"cd_ref": r.cd_ref, "nb_obs_taxon": r.nb_obs_taxon}
        topSpecies.append(temp)
    return topSpecies


def getListOrganism(connection, cd_ref):
    # Fiche espèce : Liste des organismes pour un taxon
    sql = """SELECT SUM(nb_observations) AS nb_observations, id_organism, nom_organism, url_organism, url_logo
             FROM atlas.vm_cor_taxon_organism o 
             WHERE cd_ref in (
                SELECT * FROM atlas.find_all_taxons_childs(:thiscdref)
                )
                OR cd_ref = :thiscdref
             GROUP by id_organism, nom_organism, url_organism, url_logo            
             ORDER BY nb_observations DESC"""
    req = connection.execute(text(sql), thiscdref=cd_ref)
    ListOrganism = list()
    for r in req:
        temp = {
            "nb_observation": r.nb_observations,
            "id_organism": r.id_organism,
            "nom_organism": r.nom_organism,
            "url_organism": r.url_organism,
            "url_logo": r.url_logo,
        }
        ListOrganism.append(temp)
    return ListOrganism


def getTaxonRepartitionOrganism(connection, id_organism):
    # Fiche organism : réparition du type d'observations
    sql = """SELECT  SUM(o.nb_observations) as nb_obs_group, g.group2_inpn
    FROM atlas.vm_cor_taxon_organism o
    JOIN atlas.vm_taxref g on g.cd_nom=o.cd_ref
    WHERE o.id_organism = :thisidorganism
   	GROUP BY g.group2_inpn, o.id_organism
    """
    req = connection.execute(text(sql), thisidorganism=id_organism)
    ListGroup = list()
    for r in req:
        temp = {"group2_inpn": r.group2_inpn, "nb_obs_group": int(r.nb_obs_group)}
        ListGroup.append(temp)
    return ListGroup


def get_nb_organism_on_zone(connection, id_zone):
    sql = """SELECT DISTINCT COUNT(cto.nom_organism) AS nb_organism
FROM atlas.vm_observations o
JOIN atlas.vm_cor_taxon_organism cto ON cto.cd_ref = o.cd_ref
WHERE o.id_zone = :id_zone
    """
    res = connection.execute(text(sql), id_zone=id_zone)
    result = dict()
    for r in res:
        result = r.nb_organism
    return result
