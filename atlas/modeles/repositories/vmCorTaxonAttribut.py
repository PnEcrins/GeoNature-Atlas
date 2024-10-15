# -*- coding:utf-8 -*-

from sqlalchemy.sql import text


def getAttributesTaxon(connection, cd_ref, displayed_attr):
    sql = """
        SELECT *
        FROM atlas.vm_taxon_attribute
        WHERE code = ANY(:displayedAttr)
            AND cd_ref = :cdRef
    """
    results = connection.execute(text(sql), displayedAttr=displayed_attr, cdRef=cd_ref)

    desc_taxon = []
    for row in results:
        desc_taxon.append({"code": row.code, "title": row.title, "value": row.value})
    return desc_taxon
