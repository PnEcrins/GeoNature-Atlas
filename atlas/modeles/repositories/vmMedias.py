# -*- coding:utf-8 -*-


from flask import current_app
from sqlalchemy.sql import text

from atlas.modeles import utils


def _format_media(r):
    """
    Return a dict from request of the t_media table
    """
    return {
        "id_media": r.id_media,
        "cd_ref": r.cd_ref,
        "path": utils.findPath(r),
        "title": deleteNone(r.titre),
        "author": deleteNone(r.auteur),
        "description": deleteNone(r.desc_media),
        "id_type": r.id_type,
        "date": str(r.date_media),
        "licence": r.licence,
        "source": r.source,
    }


def deleteNone(r):
    if r is None:
        return ""
    else:
        return r


def getFirstPhoto(connection, cd_ref, id):
    sql = """
        SELECT *
        FROM atlas.vm_medias
        WHERE (
                cd_ref IN (
                    SELECT * FROM atlas.find_all_taxons_childs(:thiscdref)
                )
                OR cd_ref = :thiscdref
            )
                AND id_type=:thisid
        LIMIT 1
    """
    req = connection.execute(text(sql), thiscdref=cd_ref, thisid=id)
    for r in req:
        return _format_media(r)


def getPhotoCarousel(connection, cd_ref, id):
    sql = """
        SELECT *
        FROM atlas.vm_medias
        WHERE (
                cd_ref IN (
                    SELECT * FROM atlas.find_all_taxons_childs(:thiscdref)
                )
                OR cd_ref = :thiscdref
            )
            AND id_type= :thisid
    """
    req = connection.execute(text(sql), thiscdref=cd_ref, thisid=id)

    return [_format_media(r) for r in req]


def switchMedia(row):
    media_template = {  # noqa
        current_app.config["ATTR_AUDIO"]: "{path}",
        current_app.config["ATTR_VIDEO_HEBERGEE"]: "{path}",
        current_app.config[
            "ATTR_YOUTUBE"
        ]: """
            <iframe
                width='100%'
                height='315'
                src='https://www.youtube.com/embed/{path}'
                frameborder='0'
                allowfullscreen>
            </iframe>""",
        current_app.config[
            "ATTR_DAILYMOTION"
        ]: """
            <iframe
                frameborder='0'
                width='100%'
                height='315'
                src='//www.dailymotion.com/embed/video/{path}'
                allowfullscreen>
            </iframe>""",
        current_app.config[
            "ATTR_VIMEO"
        ]: """
            <iframe
                src='https://player.vimeo.com/video/{path}?color=ffffff&title=0&byline=0&portrait=0'
                width='640'
                height='360'
                frameborder='0'
                webkitallowfullscreen
                mozallowfullscreen
                allowfullscreen>
            </iframe>""",
    }

    goodPath = str()
    if not row.chemin and not row.url:
        return None
    elif row.chemin:
        goodPath = row.chemin
    else:
        goodPath = row.url

    if not goodPath:
        return None
    return media_template[row.id_type].format(path=goodPath)


def getVideo_and_audio(connection, cd_ref, id5, id6, id7, id8, id9):
    sql = """
        SELECT *
        FROM atlas.vm_medias
        WHERE id_type IN (:id5, :id6, :id7, :id8, :id9) AND cd_ref = :thiscdref
        ORDER BY date_media DESC
    """
    req = connection.execute(
        text(sql), thiscdref=cd_ref, id5=id5, id6=id6, id7=id7, id8=id8, id9=id9
    )
    tabMedias = {"audio": list(), "video": list()}
    for r in req:
        path = switchMedia(r)
        if path is not None:
            temp = {
                "id_type": r.id_type,
                "path": path,
                "title": r.titre,
                "author": deleteNone(r.auteur),
                "description": deleteNone(r.desc_media),
                "id_media": r.id_media,
                "source": r.source,
                "licence": r.licence,
            }
            if r.id_type == current_app.config["ATTR_AUDIO"]:
                tabMedias["audio"].append(temp)
            else:
                tabMedias["video"].append(temp)
    return tabMedias


def getLinks_and_articles(connection, cd_ref, id3, id4):
    sql = """
        SELECT *
        FROM atlas.vm_medias
        WHERE id_type IN (:id3, :id4) AND cd_ref = :thiscdref
        ORDER BY date_media DESC
    """
    req = connection.execute(text(sql), thiscdref=cd_ref, id3=id3, id4=id4)
    return [_format_media(r) for r in req]


def get_liens_importants(connection, cd_ref, media_ids):
    sql = """
        SELECT *
        FROM atlas.vm_medias
        WHERE id_type = ANY(:media_ids) AND cd_ref = :thiscdref
        ORDER BY date_media DESC
    """
    req = connection.execute(text(sql), thiscdref=cd_ref, media_ids=media_ids)
    return [_format_media(r) for r in req]


def getPhotosGallery(connection, id1, id2):
    sql = """
        SELECT m.*, t.nom_vern, t.lb_nom, t.nb_obs
        FROM atlas.vm_medias m
        JOIN atlas.vm_taxons t ON t.cd_ref = m.cd_ref
        WHERE m.id_type IN (:thisID1, :thisID2)
        ORDER BY RANDOM()
    """
    req = connection.execute(text(sql), thisID1=id1, thisID2=id2)
    tab_photos = []
    for r in req:
        if r.nom_vern:
            nom_verna = r.nom_vern.split(",")
            taxonName = nom_verna[0] + " | <i>" + r.lb_nom + "</i>"
        else:
            taxonName = "<i>" + r.lb_nom + "</i>"

        photo = _format_media(r)
        photo["name"] = taxonName
        photo["nb_obs"] = r.nb_obs
        tab_photos.append(photo)
    return tab_photos


def getPhotosGalleryByGroup(connection, id1, id2, INPNgroup):
    sql = """
        SELECT m.*, t.nom_vern, t.lb_nom, t.nb_obs
        FROM atlas.vm_medias m
        JOIN atlas.vm_taxons t ON t.cd_ref = m.cd_ref
        WHERE m.id_type IN  (:thisID1, :thisID2) AND t.group2_inpn = :thisGroup
        ORDER BY RANDOM()"""
    req = connection.execute(text(sql), thisID1=id1, thisID2=id2, thisGroup=INPNgroup)
    tab_photos = []
    for r in req:
        photo = _format_media(r)
        if r.nom_vern:
            nom_verna = r.nom_vern.split(",")
            taxonName = nom_verna[0] + " | <i>" + r.lb_nom + "</i>"
        else:
            taxonName = "<i>" + r.lb_nom + "</i>"

        photo["name"] = taxonName
        photo["nb_obs"] = r.nb_obs
        tab_photos.append(photo)
    return tab_photos
