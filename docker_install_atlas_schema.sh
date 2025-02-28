set -eof pipefail

# test env
if [ -z "$ATLAS_TYPE_MAILLE" ]; then
echo la variable ATLAS_TYPE_MAILLE n''est pas définie
fi

if [ -z "$ATLAS_TYPE_TERRITOIRE" ]; then
echo la variable ATLAS_TYPE_TERRITOIRE n''est pas définie
fi

if [ -z "$ATLAS_ALTITUDES" ]; then
echo la variable ATLAS_ALTITUDES $ATLAS_ALTITUDES n''est pas définie
fi

if [ -z "$ATLAS_TYPE_MAILLE" ] || [ -z "$ATLAS_TYPE_TERRITOIRE" ] || [ -z "$ATLAS_ALTITUDES" ]; then
    exit 1
fi

export PGPASSWORD=${POSTGRES_PASSWORD}
psql -d ${POSTGRES_DB} -U ${POSTGRES_USER} -h ${POSTGRES_HOST} -p ${POSTGRES_PORT} -c "CREATE SCHEMA atlas";
psql -d ${POSTGRES_DB} -U ${POSTGRES_USER} -h ${POSTGRES_HOST} -p ${POSTGRES_PORT} -c "CREATE SCHEMA synthese";


# SCRIPTS

# - ALTITUDES

altitudes=$(echo ${ATLAS_ALTITUDES} | sed 's/[\(\)]//g')
altitude_max=0
id_altitude=0
insert=""
for altitude in $(echo "${altitudes}"); do
    if [ ! -z "$last_altitude" ]; then
        id_altitude=$((id_altitude+1))
        sql="INSERT INTO atlas.bib_altitudes VALUES ($id_altitude,$last_altitude,$altitude);"
        insert="${insert}\n${sql}"
    fi
    last_altitude=$altitude
done

sed "s/INSERT_ALTITUDE/${insert}/" data/atlas/4.atlas.vm_altitudes.sql > /tmp/4.atlas.vm_altitudes.sql

sed "s/utilisateurs.reduced_cor_dataset_actor/atlas.reduced_cor_dataset_actor/g" data/atlas/11.atlas.vm_cor_taxon_organism.sql > /tmp/11.atlas.vm_cor_taxon_organism.sql

# REFGEO


psql -v ON_ERROR_STOP=1 -d ${POSTGRES_DB} -U ${POSTGRES_USER} -h ${POSTGRES_HOST} -p ${POSTGRES_PORT} \
    -v type_maille=$ATLAS_TYPE_MAILLE \
    -v type_territoire=$ATLAS_TYPE_TERRITOIRE \
    -f data/gn2/atlas_ref_geo.sql

# SYNTHESE
psql -d ${POSTGRES_DB} -U ${POSTGRES_USER} -h ${POSTGRES_HOST} -p ${POSTGRES_PORT} -c "CREATE VIEW synthese.cor_area_synthese AS SELECT * FROM gn_synthese.cor_area_synthese"
psql -d ${POSTGRES_DB} -U ${POSTGRES_USER} -h ${POSTGRES_HOST} -p ${POSTGRES_PORT} -c "CREATE VIEW synthese.synthese AS SELECT * FROM gn_synthese.synthese"
psql -d ${POSTGRES_DB} -U ${POSTGRES_USER} -h ${POSTGRES_HOST} -p ${POSTGRES_PORT} -c "CREATE VIEW synthese.t_nomenclatures AS SELECT * FROM ref_nomenclatures.t_nomenclatures"
psql -v ON_ERROR_STOP=1 -d ${POSTGRES_DB} -U ${POSTGRES_USER} -h ${POSTGRES_HOST} -p ${POSTGRES_PORT} -f data/gn2/atlas_synthese.sql

# SCRIPTS
psql -v ON_ERROR_STOP=1 -d ${POSTGRES_DB} -U ${POSTGRES_USER} -h ${POSTGRES_HOST} -p ${POSTGRES_PORT} -f data/atlas/1.atlas.vm_taxref.sql
psql -v ON_ERROR_STOP=1 -d ${POSTGRES_DB} -U ${POSTGRES_USER} -h ${POSTGRES_HOST} -p ${POSTGRES_PORT} -f data/atlas/2.atlas.vm_observations.sql
psql -v ON_ERROR_STOP=1 -d ${POSTGRES_DB} -U ${POSTGRES_USER} -h ${POSTGRES_HOST} -p ${POSTGRES_PORT} -f data/atlas/3.atlas.vm_taxons.sql

psql -v ON_ERROR_STOP=1 -d ${POSTGRES_DB} -U ${POSTGRES_USER} -h ${POSTGRES_HOST} -p ${POSTGRES_PORT} -f /tmp/4.atlas.vm_altitudes.sql > /tmp/atlas.log

psql -v ON_ERROR_STOP=1 -d ${POSTGRES_DB} -U ${POSTGRES_USER} -h ${POSTGRES_HOST} -p ${POSTGRES_PORT} -f data/atlas/5.atlas.vm_search_taxon.sql
psql -v ON_ERROR_STOP=1 -d ${POSTGRES_DB} -U ${POSTGRES_USER} -h ${POSTGRES_HOST} -p ${POSTGRES_PORT} -f data/atlas/6.atlas.vm_mois.sql
psql -v ON_ERROR_STOP=1 -d ${POSTGRES_DB} -U ${POSTGRES_USER} -h ${POSTGRES_HOST} -p ${POSTGRES_PORT} -f data/atlas/8.atlas.vm_medias.sql
psql -v ON_ERROR_STOP=1 -d ${POSTGRES_DB} -U ${POSTGRES_USER} -h ${POSTGRES_HOST} -p ${POSTGRES_PORT} -f data/atlas/9.atlas.vm_cor_taxon_attribut.sql
psql -v ON_ERROR_STOP=1 -d ${POSTGRES_DB} -U ${POSTGRES_USER} -h ${POSTGRES_HOST} -p ${POSTGRES_PORT} -f data/atlas/10.atlas.vm_taxons_plus_observes.sql
psql -v ON_ERROR_STOP=1 -d ${POSTGRES_DB} -U ${POSTGRES_USER} -h ${POSTGRES_HOST} -p ${POSTGRES_PORT} -f /tmp/11.atlas.vm_cor_taxon_organism.sql

psql -v ON_ERROR_STOP=1 -d ${POSTGRES_DB} -U ${POSTGRES_USER} -h ${POSTGRES_HOST} -p ${POSTGRES_PORT} -f data/atlas/13.atlas.vm_observations_mailles.sql
psql -v ON_ERROR_STOP=1 -d ${POSTGRES_DB} -U ${POSTGRES_USER} -h ${POSTGRES_HOST} -p ${POSTGRES_PORT} -f data/atlas/atlas.refresh_materialized_view_data.sql
