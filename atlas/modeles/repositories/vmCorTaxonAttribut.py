# -*- coding:utf-8 -*-

from sqlalchemy.sql import text
import markdown


def getAttributesTaxon(connection, cd_ref, attrDesc, attrComment, attrMilieu, attrChoro):
    sql = """
        SELECT *
        FROM atlas.vm_cor_taxon_attribut
        WHERE id_attribut IN (:thisattrDesc, :thisattrComment, :thisattrMilieu, :thisattrChoro)
        AND cd_ref = :thiscdref
    """
    req = connection.execute(
        text(sql),
        thiscdref=cd_ref,
        thisattrDesc=attrDesc,
        thisattrComment=attrComment,
        thisattrMilieu=attrMilieu,
        thisattrChoro=attrChoro,
    )

    descTaxon = {"description": None, "commentaire": None, "milieu": None, "chorologie": None}
    for r in req:
        html_value = markdown.markdown(r.valeur_attribut)
        if r.id_attribut == attrDesc:
            descTaxon["description"] = html_value
        elif r.id_attribut == attrComment:
            descTaxon["commentaire"] = html_value
        elif r.id_attribut == attrMilieu:
            descTaxon["milieu"] = r.valeur_attribut.replace("&", " | ")
        elif r.id_attribut == attrChoro:
            descTaxon["chorologie"] = html_value
    return descTaxon
