from sqlalchemy.sql import text


def get_taxons_statut_bdc(connection, cd_ref):
    sql = "SELECT * FROM atlas.vm_bdc_statut WHERE cd_ref = :thiscdref"
    result = connection.execute(text(sql), thiscdref=cd_ref)
    statuts = list()
    for row in result:
        statut = {
            "rq_statut": row.rq_statut,
            "code_statut": row.code_statut,
            "label_statut": row.label_statut,
            "cd_type_statut": row.cd_type_statut,
            "lb_type_statut": row.lb_type_statut,
            "lb_adm_tr": row.lb_adm_tr,
            "cd_sig": row.cd_sig,
        }
        statuts.append(statut)
    return statuts
