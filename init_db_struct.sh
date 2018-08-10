#!/bin/bash

python_upgrade_list='(antlia|cassiopeia|circini|grus|)'
go_upgrade_list='(aquarius|capricorn|aries|earth|hydra|leo|neptune|pisces|polaris)'
#WORKSPACE='${HOME}/Galaxy'
WORKSPACE="${HOME}/Desktop/xurun/Galaxy"


function go_upgrade(){
    srv=$1
    CONF_LEVEL=stage bazel run //${srv}/cmd/server:server -- -c ${WORKSPACE}/configset -u
}

function get_snapshot(){

    LUPUS_PATH=‘${WORKSPACE}/configset/corp/lupus.json’
    user=`cat lupus.json | jq -r .Database.User`
    password=`cat lupus.json | jq -r .Database.Password`
    database=`cat lupus.json | jq -r .Database.Database`
    host=`cat lupus.json | jq -r .Database.Host`
    port=`cat lupus.json | jq -r .Database.Port`
    sql="select url from snapshot where type='SNAP_SHOT_CLOUD' order by created_time desc limit 1;"

    return=`PGPASSWORD=${password} psql -h ${host} -U ${user} -d ${database} -p ${port} -c "${sql}"`

    snap_shot=`echo ${res} | sed -e 's/-//g' | awk '{print $2}'`
    export CIRCINI_SNAPSHOT_URL="${snap_shot}"

}
   
function python_upgrade(){
    srv=$1
    cd ${WORKSPACE}/${srv}
    ROOT_APP_PATH='${WORKSPACE}/${srv}' python3 db_migration.py db init
    ROOT_APP_PATH='${WORKSPACE}/${srv}' python3 db_migration.py db upgrade

}




cd ${WORKSPACE}

for l in $@
do
    service=`echo $l | awk -F '.' '{print $1}'`

    if echo "${go_upgrade_list[@]}" | grep -w "${service}"> /dev/null; then
        go_upgrade ${service}
    elif echo "${python_upgrade_list[@]}" | grep -w "${service}"> /dev/null; then
        python_upgrade ${service}
    else
        echo_err "ERROR: NOT FOUND ${service} SERVICES !!!"
    fi

    
 
done

	
