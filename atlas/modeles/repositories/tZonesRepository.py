

def get_infos_zone(connection, id_zone):
    """
    Get zone info:
    yearmin: fisrt observation year
    yearmax: last observation year
    id_parent: id parent zone
    area_name: name parent zone
    area_type_name: type parent zone
    """
    sql = """
SELECT
    MIN(extract(YEAR FROM o.dateobs)) AS yearmin,
    MAX(extract(YEAR FROM o.dateobs)) AS yearmax,
    z.id_parent,
    (SELECT area_name FROM atlas.zoning WHERE id_zone = z.id_parent) AS area_parent_name,
    (SELECT type.type_name
     FROM atlas.zoning AS zone
        JOIN ref_geo.bib_areas_types type
            ON type.id_type = zone.id_zoning_type
     WHERE zone.id_zone = z.id_parent) AS area_parent_type_name
FROM atlas.vm_observations o
         JOIN atlas.zoning z ON z.id_zone = o.id_zone
WHERE o.id_zone = :id_zone
GROUP BY z.id_parent
    """

    result = connection.execute(text(sql), id_zone=id_zone)
    info_zone = dict()
    for r in result:
        info_zone = {
            "yearmin": r.yearmin,
            "yearmax": r.yearmax,
            "id_parent": r.id_parent,
            "parent_name": r.area_parent_name,
            "parent_type_name": r.area_parent_type_name,
        }

    return info_zone
