#!/bin/bash
ROOT_PATH=`pwd`
GIT_VERSION_LATEST=`git describe --always`
REPOS_ADDRESS="127.0.0.1:5000"
#REPOS_ADDRESS="registry.cn-beijing.aliyuncs.com"

sed -i '' '6,9d' ../.bazelrc

SERVICE=$1      
COMMIT_ID=$2
COMMIT_ID_DEPLOYED=$3

SERVICE_LIST=("earth" "mars" "pisces" "neptune" "capricorn" "aquarius" "leo" "polaris" "taurus" "phoenix" "lupus" "circini" "solar" "moon" "filestore" "scorpio" "draco")

function echo_err(){
        echo -e "\033[31m\033[01m\033[05m[ $1 ]\033[0m"
}

function check_service_effective(){
	
        	if echo "${SERVICE_LIST[@]}" | grep -w "${SERVICE}"> /dev/null; then
               		echo "" > /dev/null
        	else 
                	echo_err "ERROR: NOT FOUND ${SERVICE} SERVICES !!!"
                	exit 0   
       		 fi  

}

function check_commitId_effective(){
        
	if [[ ${GIT_VERSION} != "latest" ]]; then 

		git log | grep "$COMMIT_ID" > /dev/null

        	if [[ $? != 0 ]]; then
                	echo_err "ERROR: COMMITID IS ERROR !!!"
                	exit 0
		fi
	fi

}

function tag_push_images(){
	
	sudo docker tag ${SERVICE}:latest ${REPOS_ADDRESS}/cszk/${SERVICE}:${GIT_VERSION}
	sudo docker push ${REPOS_ADDRESS}/cszk/${SERVICE}:${GIT_VERSION}
	
	
}

if [[ ${COMMIT_ID} == "latest" || ${COMMIT_ID} == "" ]]; then
        GIT_VERSION="latest"
else
        GIT_VERSION=${COMMIT_ID:0:7}
fi

check_commitId_effective
check_service_effective

if [[ ${GIT_VERSION} != "latest" ]]; then
	git checkout -b ${COMMIT_ID}
fi

echo_err "GIT VERSION: ${GIT_VERSION}"

case ${SERVICE} in
	
	solar | moon )
		sudo tar -cf - ${SERVICE} | sudo docker build -f ../${SERVICE}/dockerfile -t ${SERVICE}:latest -
		tag_push_images
	;;

	earth | mars | pisces | neptune | capricorn | aquarius | leo | polaris | taurus | phoenix | lupus )
		bazel run :push_${SERVICE}_image_${GIT_VERSION}
	;;

	filestore )
		sudo tar -cf - neptune | sudo docker build -f ./neptune/nginx/dockerfile -t filestore:latest .
		tag_push_images
	;;
	
	scorpio )
		sudo tar --exclude node_modules -cf  - scorpio taurus sagittarius | sudo docker build -t scorpio -f scorpio/dockerfile -
		tag_push_images
	;;

	draco )
	
		sudo tar --exclude node_modules -cf  - draco phoenix sagittarius leo lupus | sudo docker build -t draco -f draco/dockerfile -
		tag_push_images
		
	;;

	circini )
		
		sudo docker build -f ./circini/dockerfile -t circini:latest .
		tag_push_images
	;;

esac

sudo docker images | grep 'cszk'| awk '{print $3}' | sudo xargs docker rmi -f

if [[ ${COMMIT_ID} == "latest" ]]; then
    git log --oneline ${COMMIT_ID_DEPLOYED}...HEAD
else
    git log --oneline ${COMMIT_ID_DEPLOYED}...${COMMIT_ID}
fi

git checkout master
git branch -D ${COMMIT_ID}
