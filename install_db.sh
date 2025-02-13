#!/bin/bash
SECONDS=0

# FR: S'assurer que le script n'est pas lancer en root (utilisation de whoami)
# EN: Make sure the script is not runn with root (use whoami)
if [ "$(id -u)" == "0" ];
    then
        echo -e "\e[91m\e[1mThis script should NOT be run as root\e[0m" >&2
        exit 1
fi

# FR: sudo ls pour demander le mot de passe une fois
# EN: sudo ls to request the password once
sudo ls

if [ ! -d 'log' ]
  then
        mkdir log
fi

. atlas/configuration/settings.ini
sudo mkdir /tmp/atlas
sudo cp data/atlas/* /tmp/atlas/

function print_time () {
    echo $(date +'%H:%M:%S')
}

function database_exists () {
    # /!\ Will return false if psql can't list database. Edit your pg_hba.conf as appropriate.
    if [ -z $1 ]
        then
        # Argument is null
            return 0
    else
        # Grep db name in the list of database
        sudo -u postgres -s -- psql -tAl | grep -q "^$1|"
        return $?
    fi
}

function test_settings() {
    fields=('owner_atlas' 'user_pg' 'altitudes' 'time' 'attr_desc' 'attr_commentaire' 'attr_milieu' 'attr_chorologie')
    echo "Checking the validity of settings.ini"
    for i in "${!fields[@]}"
    do
        if [ -z ${!fields[$i]} ];
            then
                echo -e "\033\033[31m Error : \033[0m attribut ${fields[$i]} manquant dans settings.ini"
                exit
        fi
    done
}

test_settings

# FR: Suppression du fichier de log d'installation s'il existe déjà puis création de ce fichier vide.
# EN: Delete the install log file if it already exists and create this empty file.

rm  -f ./log/install_db.log
touch ./log/install_db.log


# FR: Si la BDD existe, je verifie le parametre qui indique si je dois la supprimer ou non
# EN: If the DB exists, I check the parameter that indicates whether I should delete it or not
if database_exists $db_name
    then
        if $drop_apps_db
            then
                echo "Deleting DB..."
                sudo -u postgres -s dropdb $db_name  &>> log/install_db.log
        else
            echo "The database exists and the settings file says not to delete it."
        fi
fi

# FR: Sinon je créé la BDD
# EN: Else I create the DB
if ! database_exists $db_name
    then
        print_time
        echo "Creating DB..."

        sudo -u postgres psql -c "CREATE USER $owner_atlas WITH PASSWORD '$owner_atlas_pass' "  &>> log/install_db.log
        sudo -u postgres psql -c "CREATE USER $user_pg WITH PASSWORD '$user_pg_pass' "  &>> log/install_db.log
        sudo -u postgres -s createdb -O $owner_atlas $db_name
        echo "Adding postGIS and  pgSQL to DB"
        sudo -u postgres -s psql -d $db_name -c "CREATE EXTENSION IF NOT EXISTS postgis;"  &>> log/install_db.log
        sudo -u postgres -s psql -d $db_name -c "CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog; COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';"  &>> log/install_db.log
        sudo -u postgres -s psql -d $db_name -c "CREATE EXTENSION IF NOT EXISTS pg_trgm;" &>> log/install_db.log
        sudo -u postgres -s psql -d $db_name -c "CREATE EXTENSION IF NOT EXISTS unaccent;"  &>> log/install_db.log
        # FR: Si j'utilise GeoNature ($geonature_source = True), alors je créé les connexions en FWD à la BDD GeoNature
        # EN: If I use GeoNature ($geonature_source = True), then I create the connections in FWD to the GeoNature DB
        if $geonature_source
            then
                echo "Adding FDW and connection to the GeoNature parent DB"
                sudo -u postgres -s psql -d $db_name -c "CREATE EXTENSION IF NOT EXISTS postgres_fdw;"  &>> log/install_db.log
                sudo -u postgres -s psql -d $db_name -c "CREATE SERVER geonaturedbserver FOREIGN DATA WRAPPER postgres_fdw OPTIONS (host '$db_source_host', dbname '$db_source_name', port '$db_source_port');"  &>> log/install_db.log
                sudo -u postgres -s psql -d $db_name -c "ALTER SERVER geonaturedbserver OWNER TO $owner_atlas;"  &>> log/install_db.log
                sudo -u postgres -s psql -d $db_name -c "CREATE USER MAPPING FOR $owner_atlas SERVER geonaturedbserver OPTIONS (user '$atlas_source_user', password '$atlas_source_pass') ;"  &>> log/install_db.log
        fi

        # FR: Création des schémas de la BDD
        # EN: Creating DB schemes
        sudo -u postgres -s psql -d $db_name -c "CREATE SCHEMA atlas AUTHORIZATION "$owner_atlas";"  &>> log/install_db.log
        sudo -u postgres -s psql -d $db_name -c "CREATE SCHEMA synthese AUTHORIZATION "$owner_atlas";"  &>> log/install_db.log
        sudo -u postgres -s psql -d $db_name -c "CREATE SCHEMA utilisateurs AUTHORIZATION "$owner_atlas";"  &>> log/install_db.log
        sudo -u postgres -s psql -d $db_name -c "CREATE SCHEMA gn_meta AUTHORIZATION "$owner_atlas";"  &>> log/install_db.log

        if [ $install_taxonomie = "false" ] # Pourquoi ce if ? TODO
            then
                sudo -u postgres -s psql -d $db_name -c "CREATE SCHEMA taxonomie AUTHORIZATION "$owner_atlas";"  &>> log/install_db.log
        fi

        if $geonature_source
            then
                echo "Creating FDW from GN2"
                echo "--------------------" &>> log/install_db.log #en double non? TODO
                echo "Creating FDW from GN2" &>> log/install_db.log
                echo "--------------------" &>> log/install_db.log
                export PGPASSWORD=$owner_atlas_pass;psql -d $db_name -U $owner_atlas -h $db_host -p $db_port -f data/gn2/atlas_gn2.sql  &>> log/install_db.log
        fi

        ###########################
        ######   REF_GEO
        ###########################
        if $use_ref_geo_gn2
            then
                echo "Creation of geographic tables from the ref_geo schema of the geonature database"
                echo "--------------------" &>> log/install_db.log
                echo "Creation of layers table from ref_geo of geonaturedb" &>> log/install_db.log
                echo "--------------------" &>> log/install_db.log
                export PGPASSWORD=$owner_atlas_pass; psql -d $db_name -U $owner_atlas -h $db_host -p $db_port \
                    -v type_maille=$type_maille \
                    -v type_territoire=$type_territoire \
                    -f data/gn2/atlas_ref_geo.sql &>> log/install_db.log
        else
            # FR: Import du shape des limites du territoire ($limit_shp) dans la BDD / atlas.t_layer_territoire
            # EN: Import of the shape of the territory limits ($limit_shp) in the BDD / atlas.t_layer_territory
            ogr2ogr -f "PostgreSQL" \
                -t_srs EPSG:4326 \
                -lco GEOMETRY_NAME=the_geom \
                PG:"host=$db_host port=$db_port dbname=$db_name user=$owner_atlas password=$owner_atlas_pass schemas=atlas" \
                -nln t_layer_territoire $limit_shp
 
            # FR: Import du shape des communes ($communes_shp) dans la BDD (si parametre import_commune_shp = TRUE) / atlas.l_communes
            # EN: Import of the shape of the communes ($communes_shp) in the DB (if parameter import_commune_shp = TRUE) / atlas.l_communes
            file_name=`echo $(basename $communes_shp) | cut -d "." -f1`
            ogr2ogr -f "PostgreSQL" \
            -t_srs EPSG:4326 \
            -lco GEOMETRY_NAME=the_geom \
            -sql "SELECT $colonne_nom_commune AS commune_maj, $colonne_insee AS insee FROM $file_name" \
            PG:"host=$db_host port=$db_port dbname=$db_name user=$owner_atlas password=$owner_atlas_pass schemas=atlas" \
            -nln l_communes $communes_shp 

            # FR: Mise en place des mailles
            # EN: Setting up the meshes
            echo "Cutting of meshes and creation of the mesh table"
            
            # FR: Si je suis en métropole (metropole=true), alors j'utilise les mailles fournies par l'INPN
            # EN: If I am in metropolitan France (metropole=true), then I use the grids provided by the INPN, comments are only in french here
            if $metropole
                then
                    # Je dézippe mailles fournies par l'INPN aux 3 échelles
                    unzip data/ref/L93_${taillemaille}K.zip 

                    if [ $taillemaille = 1 ] 
                    then
                        file_name="data/ref/L93_1x1.shp"
                    else
                        file_name="data/ref/L93_${taillemaille}K.shp"
                    fi 
            else     
                file_name=$chemin_custom_maille
            fi

            # J'importe dans la BDD le SHP des mailles à l'échelle définie en parametre ($taillemaille)
            ogr2ogr -f "PostgreSQL" \
                -t_srs EPSG:4326 \
                -lco GEOMETRY_NAME=geom \
                PG:"host=$db_host port=$db_port dbname=$db_name user=$owner_atlas password=$owner_atlas_pass schemas=atlas" \
                -nln t_mailles_source  $file_name
            
            # Run sql files
            export PGPASSWORD=$owner_atlas_pass;psql -d $db_name -U $owner_atlas -h $db_host -p $db_port -f /tmp/atlas/without_ref_geo.sql &>> log/install_db.log

        fi

        # FR: Conversion des limites du territoire en json
        # EN: Conversion of territory boundaries to json
        rm  -f ./atlas/static/custom/territoire.json
        ogr2ogr -f "GeoJSON" -t_srs "EPSG:4326" -s_srs "EPSG:4326" ./atlas/static/custom/territoire.json \
            PG:"host=$db_host user=$owner_atlas dbname=$db_name port=$db_port password=$owner_atlas_pass" "atlas.t_layer_territoire"

        ###########################
        ######    TAXHUB 
        ###########################
        # FR: Creation des tables filles en FWD
        # EN: Creation of daughter tables in FWD
        echo "Creating the connection to GeoNature for the taxonomy" 
        export PGPASSWORD=$owner_atlas_pass;psql -d $db_name -U $owner_atlas -h $db_host -p $db_port -f data/gn2/atlas_ref_taxonomie.sql  &>> log/install_db.log
         

        ###########################
        ######    Occurence data 
        ###########################
        echo "Creating DB structure"
        # FR: Si j'utilise GeoNature ($geonature_source = True), alors je créé les tables filles en FDW connectées à la BDD de GeoNature
        # EN: If I use GeoNature ($geonature_source = True), then I create the child tables in FDW connected to the GeoNature DB
        if $geonature_source
            then
                sudo cp data/gn2/atlas_synthese.sql /tmp/atlas/atlas_synthese_extended.sql
                sudo sed -i "s/myuser;$/$owner_atlas;/" /tmp/atlas/atlas_synthese_extended.sql
                export PGPASSWORD=$owner_atlas_pass;psql -d $db_name -U $owner_atlas -h $db_host -p $db_port -f /tmp/atlas/atlas_synthese_extended.sql  &>> log/install_db.log
        # FR: Sinon je créé une table synthese.syntheseff avec 2 observations exemple
        # EN: Otherwise I created a table synthese.syntheseff with 2 observations example
        else
            echo "Creating syntheseff example table"
            export PGPASSWORD=$owner_atlas_pass;psql -d $db_name -U $owner_atlas -h $db_host -p $db_port -f /tmp/atlas/without_geonature.sql &>> log/install_db.log
        fi


        ###########################
        ######   ATLAS
        ###########################
        # FR: Creation des Vues Matérialisées (et remplacement éventuel des valeurs en dur par les paramètres)
        # EN: Creation of Materialized Views (and possible replacement of hard values by parameters)
        echo "----- Creating materialized views ------"

        sudo sed -i "s/date - 15$/date - $time/" /tmp/atlas/10.atlas.vm_taxons_plus_observes.sql
        sudo sed -i "s/date + 15$/date - $time/" /tmp/atlas/10.atlas.vm_taxons_plus_observes.sql

        # FR: customisation de l'altitude
        # EN: customisation of altitude
        insert=""
        for i in "${!altitudes[@]}"
            do
                if [ $i -gt 0 ];
                then
                    let max=${altitudes[$i]}-1
                    sql="INSERT INTO atlas.bib_altitudes VALUES ($i,${altitudes[$i-1]},$max);"
                    insert="${insert}\n${sql}"
                fi
            done

        sudo sed -i "s/INSERT_ALTITUDE/${insert}/" /tmp/atlas/4.atlas.vm_altitudes.sql
        sudo sed -i "s/WHERE id_attribut IN (100, 101, 102, 103);$/WHERE id_attribut  IN ($attr_desc, $attr_commentaire, $attr_milieu, $attr_chorologie);/" /tmp/atlas/9.atlas.vm_cor_taxon_attribut.sql
        

        # FR: Execution des scripts sql de création des vm de l'atlas
        # EN: Run sql scripts : build atlas vm
        scripts_sql=( 
            "1.atlas.vm_taxref.sql"
            "11.vm_cor_area_synthese.sql"
            "2.atlas.vm_observations.sql"
            "3.atlas.vm_taxons.sql"
            "4.atlas.vm_altitudes.sql"
            "5.atlas.vm_search_taxon.sql"
            "6.atlas.vm_mois.sql"
            "7.atlas.vm_communes.sql"
            "8.atlas.vm_medias.sql"
            "9.atlas.vm_cor_taxon_attribut.sql"
            "10.atlas.vm_taxons_plus_observes.sql"
            "11.atlas.vm_cor_taxon_organism.sql"
            "atlas.refresh_materialized_view_data.sql"
        )
        for script in "${scripts_sql[@]}"
        do 
            echo "[$(date +'%H:%M:%S')] Creating ${script}..."
            time_temp=$SECONDS
            export PGPASSWORD=$owner_atlas_pass;psql -d $db_name -U $owner_atlas -h $db_host -p $db_port \
             -v sensibility0=$sensibility0 \
             -v sensibility1=$sensibility1 \
             -v sensibility2=$sensibility2 \
             -v sensibility3=$sensibility3  \
             -f /tmp/atlas/${script}  &>> log/install_db.log
            echo "[$(date +'%H:%M:%S')] Passed - Duration : $((($SECONDS-$time_temp)/60))m$((($SECONDS-$time_temp)%60))s"
        done
  
        if $use_ref_geo_gn2
        then
            echo "[$(date +'%H:%M:%S')] Creating atlas.t_mailles_territoire..."
            time_temp=$SECONDS
            export PGPASSWORD=$owner_atlas_pass;psql -d $db_name -U $owner_atlas -h $db_host -p $db_port  \
            -f data/atlas/12.atlas.t_mailles_territoire.sql \
            -v type_maille=$type_maille &>> log/install_db.log
            echo "[$(date +'%H:%M:%S')] Passed - Duration : $((($SECONDS-$time_temp)/60))m$((($SECONDS-$time_temp)%60))s"
        fi

        # FR: Création de la vue matérialisée vm_mailles_observations (nombre d'observations par maille et par taxon)
        # EN: Creation of the materialized view vm_meshes_observations (number of observations per mesh and per taxon)
        echo "[$(date +'%H:%M:%S')] Creating atlas.vm_observations_mailles..."
        time_temp=$SECONDS
        export PGPASSWORD=$owner_atlas_pass;psql -d $db_name -U $owner_atlas -h $db_host -p $db_port -f /tmp/atlas/13.atlas.vm_observations_mailles.sql  &>> log/install_db.log
        echo "[$(date +'%H:%M:%S')] Passed - Duration : $((($SECONDS-$time_temp)/60))m$((($SECONDS-$time_temp)%60))s"
 
        # FR: Affectation de droits en lecture sur les VM à l'utilisateur de l'application ($user_pg)
        # EN: Assign read rights on VMs to the application user ($user_pg)
        echo "Grant..."
        sudo sed -i "s/my_reader_user;$/$user_pg;/" /tmp/atlas/14.grant.sql
        sudo -n -u postgres -s psql -d $db_name -f /tmp/atlas/14.grant.sql &>> log/install_db.log

        # Clean file
        echo "Cleaning files..."
        cd data/ref
        rm -f L*.shp L*.dbf L*.prj L*.sbn L*.sbx L*.shx output_clip.*
        cd ../..
        sudo -n rm -r /tmp/atlas 

        echo "Install finished - Duration :$(($SECONDS/60))m$(($SECONDS%60))s"
fi

