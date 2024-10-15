from flask import current_app
from sqlalchemy.sql import text

from atlas.modeles import utils

def fctSortDict(value):
    return value['cd_type_statut']

def getTaxonsStatutBdc(connection, cd_ref):
    sql="SELECT * FROM atlas.vm_statut_bdc WHERE cd_ref = :thiscdref"
    req = connection.execute(text(sql), thiscdref=cd_ref)
    tsb = list()
    for r in req:
        temp = {
            'code_statut':r.code_statut,
            'label_statut':r.label_statut,
            'cd_type_statut':r.cd_type_statut,
            'lb_type_statut':r.lb_type_statut,
            'lb_adm_tr':r.lb_adm_tr
        }
        tsb.append(temp)
    taxonStatutBdc = sorted(tsb, key=fctSortDict)
    
    return taxonStatutBdc
