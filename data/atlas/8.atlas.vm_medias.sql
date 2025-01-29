-- Médias de chaque taxon

CREATE MATERIALIZED VIEW atlas.vm_medias AS
   SELECT t_medias.id_media,
      t_medias.cd_ref,
      t_medias.titre,
      t_medias.url,
      t_medias.chemin,
      t_medias.auteur,
      t_medias.desc_media,
      t_medias.date_media,
      t_medias.id_type,
      t_medias.licence,
      t_medias.source
   FROM taxonomie.t_medias;

CREATE UNIQUE INDEX ON atlas.vm_medias(id_media);
