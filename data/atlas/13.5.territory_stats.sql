-- Classic stats
DROP materialized view atlas.vm_territory_stats;
CREATE MATERIALIZED VIEW atlas.vm_territory_stats AS
SELECT                                                                                     
    cas.id_area,
    COUNT(DISTINCT obs.id_observation) AS nb_obs,
    COUNT(DISTINCT obs.cd_ref) AS nb_species,
    COUNT(DISTINCT obs.observateurs) AS nb_observers,
    COUNT(DISTINCT u.id_organisme) AS nb_organism,
    MIN(extract(YEAR FROM obs.dateobs)) AS yearmin,
    MAX(extract(YEAR FROM obs.dateobs)) AS yearmax,
    COUNT(DISTINCT case t.patrimonial when 'oui' then t.cd_ref else null end) AS nb_taxon_patrimonial,
    COUNT(DISTINCT case t.protection_stricte when 'oui' then t.cd_ref else null end) AS nb_taxon_protege,
    area.description,
    ca.id_area_group AS id_parent,
    (SELECT area_name FROM atlas.vm_l_areas WHERE id_area = ca.id_area_group) AS area_parent_name,
    (SELECT type.type_name
     FROM atlas.vm_l_areas l
              JOIN atlas.vm_bib_areas_types type ON type.id_type = l.id_type
     WHERE l.id_area = ca.id_area_group) AS area_parent_type_name
FROM atlas.vm_cor_area_synthese AS cas
         JOIN atlas.vm_observations obs ON cas.id_synthese = obs.id_observation
         LEFT JOIN atlas.vm_taxons t ON t.cd_ref=obs.cd_ref
         LEFT JOIN gn_meta.cor_dataset_actor AS rcda
              ON obs.id_dataset = rcda.id_dataset
         LEFT JOIN utilisateurs.bib_organismes u ON rcda.id_organism = u.id_organisme
         LEFT JOIN atlas.vm_l_areas area ON area.id_area = cas.id_area
         LEFT JOIN atlas.vm_cor_areas ca ON ca.id_area = area.id_area
         JOIN atlas.vm_bib_areas_types AS bat ON  bat.id_type = area.id_type
WHERE bat.type_code = ANY(SELECT * from string_to_table(:type_territoire_species, ','))
group by cas.id_area, area.description, ca.id_area_group;

-- Graph stats by taxonomy_group

DROP materialized view atlas.vm_territory_stats_by_taxonomy_group;
CREATE MATERIALIZED VIEW atlas.vm_territory_stats_by_taxonomy_group AS
SELECT
    cas.id_area,
    COUNT(DISTINCT obs.id_observation) AS nb_obs,
    COUNT(DISTINCT obs.cd_ref)                  AS nb_species,
    t.group2_inpn,
    COUNT(DISTINCT case t.patrimonial when 'oui' then t.cd_ref else null end) AS nb_patrominal,
    (SELECT COUNT(*)
     FROM atlas.vm_taxons taxon
     WHERE taxon.group2_inpn = t.group2_inpn) AS nb_species_in_teritory
FROM atlas.vm_cor_area_synthese AS cas
         JOIN atlas.vm_observations obs ON cas.id_synthese = obs.id_observation
         FULL JOIN atlas.vm_taxons t ON t.cd_ref = obs.cd_ref
WHERE cas.type_code = ANY(SELECT * from string_to_table(:type_territoire_species, ','))
GROUP BY cas.id_area, t.group2_inpn;


-- Graph stats by organism

DROP materialized view atlas.vm_territory_stats_by_organism;
CREATE MATERIALIZED VIEW atlas.vm_territory_stats_by_organism AS
SELECT
    cas.id_area,
    COUNT(DISTINCT obs.cd_ref) AS nb_species,
    COUNT(DISTINCT obs.id_observation) AS nb_obs,
    u.nom_organisme AS nom_organism
FROM atlas.vm_cor_area_synthese AS cas
         JOIN atlas.vm_observations obs ON cas.id_synthese = obs.id_observation
         JOIN gn_meta.cor_dataset_actor AS rcda
              ON obs.id_dataset = rcda.id_dataset
         JOIN utilisateurs.bib_organismes u ON rcda.id_organism = u.id_organisme
WHERE cas.type_code = ANY(SELECT * from string_to_table(:type_territoire_species, ','))
GROUP BY cas.id_area, u.nom_organisme;
