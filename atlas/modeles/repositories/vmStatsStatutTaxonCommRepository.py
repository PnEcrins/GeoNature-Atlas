# -*- coding:utf-8 -*-

from sqlalchemy.sql import text


# get nombre taxons protégés et nombre taxons patrimoniaux par communes
def get_nb_taxon_pro_pat_zone(connection, id_zone):
    sql = """
SELECT
    COUNT(t.patrimonial) AS nb_taxon_patrimonial, COUNT(t.protection_stricte) AS nb_taxon_protege
FROM atlas.vm_observations o
         JOIN atlas.vm_taxons t ON t.cd_ref=o.cd_ref
         JOIN atlas.zoning zone ON st_intersects(o.the_geom_point, zone.the_geom_4326)
WHERE zone.id_zone = :thisIdZone
    """
    req = connection.execute(text(sql), thisIdZone=id_zone)
    taxonProPatri = dict()
    for r in req:
        taxonProPatri = {"nbTaxonPro": r.nb_taxon_protege, "nbTaxonPatri": r.nb_taxon_patrimonial}
    return taxonProPatri


# # get stats sur les statuts des taxons par communes
# def getStatsStatutsTaxonsCommunes(connection, insee):
#     sql = """
#         SELECT
#         nb_taxon_que_pro,
#         nb_taxon_que_patri,
#         nb_taxon_pro_et_patri,
#         nb_taxon_sans_statut
#         FROM atlas.vm_stats_statut_taxon_comm a
#         WHERE a.insee = :thisinsee
#     """.encode('UTF-8')
#
#     mesStatutsTaxons = connection.execute(text(sql), thisinsee=insee)
#     for inter in mesStatutsTaxons:
#         return [
#             {'label': "Taxons protégés", 'y': inter.nb_taxon_que_pro},
#             {'label': "Taxons patrimoniaux", 'y': inter.nb_taxon_que_patri},
#             {'label': "Taxons protégés et patrimoniaux", 'y': inter.nb_taxon_pro_et_patri},
#             {'label': "Autres taxons", 'y': inter.nb_taxon_sans_statut},
#         ]
#
