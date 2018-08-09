#!/bin/bash

python_upgrade_list='()'
go_upgrade_list='(earth|taurus)'
WORKSPACE=‘/home/xr/Galaxy’


function go_upgrade(){
    srv=$1
    CONF=stage bazel run //${srv}/cmd/server:server -- -c ${WORKSPACE}/configset -u
}
    
function python_upgrade(){
    srv=$1
    cd ${WORKSPACE}/${srv}
    ROOT_APP_PATH=‘${WORKSPACE}/${srv}’ python3 db_migration.py db init
    ROOT_APP_PATH=‘${WORKSPACE}/${srv}’ python3 db_migration.py db upgrade

}






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

	
