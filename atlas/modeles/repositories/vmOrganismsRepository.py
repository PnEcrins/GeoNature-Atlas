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


def get_nb_organism_on_area(connection, id_area):
    sql = """SELECT COUNT(DISTINCT cto.nom_organism) AS nb_organism
FROM atlas.vm_observations obs
         JOIN gn_meta.cor_dataset_actor AS rcda
              ON obs.id_dataset = rcda.id_dataset
         JOIN atlas.vm_cor_taxon_organism cto ON rcda.id_organism = cto.id_organism
        JOIN atlas.vm_l_areas area ON st_intersects(obs.the_geom_point, area.the_geom)
WHERE area.id_area = :id_area;
    """
    res = connection.execute(text(sql), id_area=id_area)
    result = dict()
    for r in res:
        result = r.nb_organism
    return result


def get_nb_species_by_organism_on_area(connection, id_area):
    sql = """
SELECT COUNT(DISTINCT obs.cd_ref) AS nb_species, cto.nom_organism
FROM atlas.vm_observations obs
     JOIN gn_meta.cor_dataset_actor AS rcda
          ON obs.id_dataset = rcda.id_dataset
    JOIN atlas.vm_cor_taxon_organism cto ON rcda.id_organism = cto.id_organism
        JOIN atlas.vm_l_areas area ON st_intersects(obs.the_geom_point, area.the_geom)
WHERE area.id_area = :id_area
GROUP BY cto.nom_organism
ORDER BY cto.nom_organism;
    """
    result = connection.execute(text(sql), id_area=id_area)
    list_species_by_organism = list()
    for r in result:
        temp = {"nb": r.nb_species, "label": r.nom_organism}
        list_species_by_organism.append(temp)
    return list_species_by_organism


def get_nb_observations_by_organism_on_area(connection, id_area):
    sql = """
SELECT COUNT(obs.id_observation) AS nb_observations, b.nom_organisme
FROM atlas.vm_observations obs
     JOIN gn_meta.cor_dataset_actor AS rcda ON obs.id_dataset = rcda.id_dataset
    JOIN utilisateurs.bib_organismes b ON b.id_organisme = rcda.id_organism
        JOIN atlas.vm_l_areas area ON st_intersects(obs.the_geom_point, area.the_geom)
WHERE area.id_area = :id_area
GROUP BY b.nom_organisme
ORDER BY b.nom_organisme;
    """
    result = connection.execute(text(sql), id_area=id_area)
    list_observations_by_organism = list()
    for r in result:
        temp = {"nb": r.nb_observations, "label": r.nom_organisme}
        list_observations_by_organism.append(temp)
    return list_observations_by_organism


def get_biodiversity_stats_by_organism_on_area(connection, id_area):
    sql = """
SELECT nb_species,
       nom_organism
FROM atlas.vm_territory_stats_by_organism
WHERE id_area = :id_area;
    """
    result = connection.execute(text(sql), id_area=id_area)
    list_species_by_organism = list()
    for r in result:
        temp = {"nb": r.nb_species, "label": r.nom_organism}
        list_species_by_organism.append(temp)
    return list_species_by_organism


def get_observations_stats_by_organism_on_area(connection, id_area):
    sql = """
    SELECT nb_obs,
           nom_organism
    FROM atlas.vm_territory_stats_by_organism
    WHERE id_area = :id_area;
        """
    result = connection.execute(text(sql), id_area=id_area)
    list_species_by_organism = list()
    for r in result:
        temp = {"nb": r.nb_obs, "label": r.nom_organism}
        list_species_by_organism.append(temp)
    return list_species_by_organism
