CREATE MATERIALIZED VIEW IF NOT EXISTS atlas.vm_bdc_statut AS
SELECT s.cd_ref,
       s.rq_statut,
       v.code_statut,
       v.label_statut,
       t.cd_type_statut,
       ty.lb_type_statut,
       t.cd_sig,
       t.lb_adm_tr
FROM taxonomie.bdc_statut_taxons AS s
         JOIN taxonomie.bdc_statut_cor_text_values AS c
              ON s.id_value_text = c.id_value_text
         JOIN taxonomie.bdc_statut_text AS t
              ON t.id_text = c.id_text
         JOIN taxonomie.bdc_statut_values AS v
              ON v.id_value = c.id_value
         JOIN taxonomie.bdc_statut_type AS ty
              ON ty.cd_type_statut = t.cd_type_statut
WHERE t.ENABLE = true;

GRANT SELECT ON TABLE atlas.vm_bdc_statut TO my_reader_user;

CREATE INDEX ON atlas.vm_bdc_statut
    USING btree (cd_ref);
