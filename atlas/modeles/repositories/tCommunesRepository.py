# -*- coding:utf-8 -*-
import ast

from sqlalchemy.sql import text


def getZonesObservationsChilds(connection, cd_ref):
    sql = """
    SELECT DISTINCT(com.insee) AS insee, com.area_name
    FROM layers.l_communes com
    JOIN atlas.vm_observations obs ON obs.insee = com.insee
    WHERE obs.cd_ref IN (
            SELECT * FROM atlas.find_all_taxons_childs(:thiscdref)
        ) OR obs.cd_ref = :thiscdref
    GROUP BY com.area_name, com.insee
    """.encode(
        "UTF-8"
    )

    return connection.execute(text(sql), thiscdref=cd_ref)
