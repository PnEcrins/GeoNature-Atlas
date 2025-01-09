from sqlalchemy.sql import text


def fctSortDict(value):
    return value['cd_type_statut']


def get_taxons_statut_bdc(connection, cd_ref):
    sql = "SELECT * FROM atlas.vm_bdc_statut WHERE cd_ref = :thiscdref"
    result = connection.execute(text(sql), thiscdref=cd_ref)
    statuts = list()
    for row in result:
        statut = {
            'code_statut': row.code_statut,
            'label_statut': row.label_statut,
            'cd_type_statut': row.cd_type_statut,
            'lb_type_statut': row.lb_type_statut,
            'lb_adm_tr': row.lb_adm_tr
        }
        statuts.append(statut)
    return sorted(statuts, key=fctSortDict)
