-- Affectation de droits en lecture sur les VM à l'utilisateur de l'application ($user_pg)

SET search_path = public, pg_catalog;

--
-- Name: geometry_columns; Type: ACL; Schema: public; Owner: -
--

--REVOKE ALL ON TABLE geometry_columns FROM PUBLIC;
--REVOKE ALL ON TABLE geometry_columns FROM my_reader_user;
--GRANT ALL ON TABLE geometry_columns TO my_reader_user;

--
-- Name: spatial_ref_sys; Type: ACL; Schema: public; Owner: -
--

/*REVOKE ALL ON TABLE spatial_ref_sys FROM PUBLIC;
REVOKE ALL ON TABLE spatial_ref_sys FROM my_reader_user;
GRANT ALL ON TABLE spatial_ref_sys TO my_reader_user;*/

GRANT USAGE ON SCHEMA atlas TO my_reader_user;

GRANT SELECT ON TABLE atlas.vm_altitudes TO my_reader_user;
GRANT SELECT ON TABLE atlas.vm_communes TO my_reader_user;
GRANT SELECT ON TABLE atlas.vm_observations TO my_reader_user;
GRANT SELECT ON TABLE atlas.vm_taxon_attribute TO my_reader_user;
GRANT SELECT ON TABLE atlas.vm_medias TO my_reader_user;
GRANT SELECT ON TABLE atlas.vm_observations TO my_reader_user;
GRANT SELECT ON TABLE atlas.vm_observations_mailles TO my_reader_user;
GRANT SELECT ON TABLE atlas.vm_search_taxon TO my_reader_user;
GRANT SELECT ON TABLE atlas.vm_taxons TO my_reader_user;
GRANT SELECT ON TABLE atlas.vm_taxons_plus_observes TO my_reader_user;
GRANT SELECT ON TABLE atlas.vm_taxref TO my_reader_user;
GRANT SELECT ON TABLE atlas.vm_mois TO my_reader_user;
GRANT SELECT ON TABLE atlas.vm_altitudes TO my_reader_user;
GRANT SELECT ON TABLE atlas.bib_altitudes TO my_reader_user;
GRANT EXECUTE ON FUNCTION atlas.find_all_taxons_childs(integer) TO my_reader_user;
GRANT SELECT ON TABLE atlas.bib_taxref_rangs TO my_reader_user;
GRANT SELECT ON TABLE atlas.t_mailles_territoire TO my_reader_user;
GRANT SELECT ON TABLE atlas.vm_cor_taxon_organism TO my_reader_user;
