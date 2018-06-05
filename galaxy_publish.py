#encoding:UTF-8
import urllib.request
import json
from urllib.error import *
import time
import sys

#URL = "jenkins.corp.zgcszkw.com"
URL = "192.168.223.194:8080"

#JOB = "galaxy-publish-clone"
JOB = "galaxy-publish"

TOKEN_JENKINS = "1234"
#TOKEN_JENKINS = "Appstore"
PARAMETER = ["SERVICE_NAME","COMMIT_ID","COMMIT_ID_DEPLOYED"]
PARAMETER_DICT = {"token":TOKEN_JENKINS}

romote_build_url = "http://"+URL+"/job/"+JOB+"/buildWithParameters"

def jenkins_build_push(service_name, deploy_ver, image_ver):
    
    PARAMETER_DICT["SERVICE_NAME"] = service_name
    PARAMETER_DICT["COMMIT_ID"] = deploy_ver
    PARAMETER_DICT["COMMIT_ID_DEPLOYED"] = image_ver

    print(PARAMETER_DICT)

    #Get last job should take how many seconds
    url = "http://"+URL+"/job/"+JOB+"/lastBuild/api/json"
    data = urllib.request.urlopen ( url ).read ()
    data_utf = data.decode ( 'UTF-8' )
    data = json.loads(data_utf)
    estimatedDuration = data["estimatedDuration"]

    #When someone is building this job,you should wait for xxx seconds!
    url_lastJobStatus = "http://"+URL+"/job/"+JOB+"/lastBuild/api/xml?xpath=/freeStyleBuild/result"
    code_status = 0
    flag = True
    while(flag):
        try:
            code_status = urllib.request.urlopen(url_lastJobStatus).getcode()
            flag = False
        except HTTPError as e:
            code_status = e.code
            time.sleep(2)
            print ("Other is deploying "+" "+JOB+" "+", you should wait "
                +str(estimatedDuration/1000)+" seconds...")

    #Get last build result and id
    url = "http://"+URL+"/job/"+JOB+"/lastBuild/api/json"
    data = urllib.request.urlopen ( url ).read ()
    data_utf = data.decode ( 'UTF-8' )
    data = json.loads(data_utf)
    id = data["id"]
    result = data["result"]
    print (str(id)+" "+JOB+" is "+result)

    #Remote build though HTTP(POST)
    try:
        params = urllib.parse.urlencode ( PARAMETER_DICT ).encode('utf-8')
        urllib.request.urlopen(romote_build_url,params)
    except HTTPError as e:
        print ("ERROR CODE:"+str(e.code))
        print ("Usage: python3 galaxy_publish.py ${SERVICE_NAME} ${COMMIT_ID} ${COMMIT_ID_DEPLOYED} !!!\r\n"
            "${SERVICE_NAME}: must input\r\n"
            "${COMMIT_ID}: default is latest\r\n"
            "${COMMIT_ID_DEPLOYED}: the deployed image version")
        sys.exit(1)

    id  = int(id) + 1
    url_log =  "http://"+URL+"/job/"+JOB+"/"+str(id)+"/logText/progressiveHtml"
    tmp_log = ""
    flag = True

    while flag:
        try:
            response = urllib.request.urlopen(url_log).read()
            data_byte = urllib.request.urlopen( url_log ).read()
            data = str(data_byte,encoding="utf-8")

            # Additionally output job logs
            if(tmp_log != data):
                if(tmp_log in data):
                    print (data.replace(tmp_log,""))
            if("Finished: " in data):
                flag = False

            tmp_log = data
            time.sleep(2)
        except HTTPError as e:
            time.sleep(2)


if __name__ == '__main__':

    jenkins_build_push(sys.argv[1], sys.argv[2], sys.argv[3])
