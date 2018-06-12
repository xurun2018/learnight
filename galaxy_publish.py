import urllib.request
import json
from urllib.error import *
import time
import sys

def continue_or_not():
    yn = input ( "\nPlease check the git logs as above:\nDeploy? Please enter 'y' or 'n': " )
    if (yn == "y" or yn == "Y"):
        pass
    elif (yn == "n" or yn == "N"):
        sys.exit ( 0 )
    else:
        print ( "Invalid input..." )
        sys.exit ( 1 )

def get_last_build_result(job_name,param):
    url = "http://" + URL + "/job/" + job_name + "/lastBuild/api/json"
    data = urllib.request.urlopen ( url ).read ()
    data_utf = data.decode ( 'UTF-8' )
    data = json.loads ( data_utf )
    return data[param]


def jenkins_build(job_name):

    url = "http://" + URL + "/job/" + job_name + "/lastBuild/api/json"
    data = urllib.request.urlopen ( url ).read ()
    data_utf = data.decode ( 'UTF-8' )
    data = json.loads ( data_utf )
    estimatedDuration = data["estimatedDuration"]

    # When someone is building this job,you should wait for xxx seconds!
    url_lastJobStatus = "http://" + URL + "/job/" + job_name + "/lastBuild/api/xml?xpath=/freeStyleBuild/result"
    code_status = 0
    flag = True
    while (flag):
        try:
            code_status = urllib.request.urlopen ( url_lastJobStatus ).getcode ()
            flag = False
        except HTTPError as e:
            code_status = e.code
            time.sleep ( 2 )
            print ( "Other is deploying " + " " + job_name + " " + ", you should wait "
                    + str ( estimatedDuration / 1000 ) + " seconds..." )

    # Get last build result and id

    id = get_last_build_result ( job_name,"id" )
    result = get_last_build_result ( job_name,"result" )
    print ( str ( id ) + " " + job_name + " is " + str ( result ) )
    romote_url = "http://" + URL + "/job/" + job_name + "/buildWithParameters"

    # Remote build though HTTP(POST)
    try:
        auth_handler = urllib.request.HTTPBasicAuthHandler ()
        auth_handler.add_password ( realm='jira-core-users',
                                    user=JENKINS_NAME,
                                    passwd=JENKINS_PASSWD,
                                    uri=URL )
        opener = urllib.request.build_opener ( auth_handler )
        urllib.request.install_opener ( opener )
        parameter_dict = {"token": TOKEN_JENKINS}
        parameter_dict["SERVICE_NAME"] = SERVICE_NAME
        parameter_dict["COMMIT_ID"] = COMMIT_ID
        parameter_dict["COMMIT_ID_DEPLOYED"] = COMMIT_ID_DEPLOYED
        params = urllib.parse.urlencode ( parameter_dict ).encode ( 'utf-8' )
        urllib.request.urlopen ( romote_url, params )
    except HTTPError as e:
        print ( "ERROR CODE:" + str ( e.code ) )
        print (
            "Usage: python3 galaxy_publish.py ${SERVICE_NAME} ${COMMIT_ID} ${COMMIT_ID_DEPLOYED} !!!\r\n"
            "${SERVICE_NAME}: must input\r\n"
            "${COMMIT_ID}: default is latest" )
        return False

    id = int ( id ) + 1
    url_log = "http://" + URL + "/job/" + job_name + "/" + str ( id ) + "/logText/progressiveHtml"
    tmp_log = ""
    flag = True

    while flag:
        try:
            response = urllib.request.urlopen ( url_log ).read ()
            data_byte = urllib.request.urlopen ( url_log ).read ()
            data = str ( data_byte, encoding="utf-8" )

            # Additionally output job logs
            if (tmp_log != data):
                if (tmp_log in data):
                    print ( data.replace ( tmp_log, "" ) )
            if ("Finished: " in data):
                flag = False

            tmp_log = data
            time.sleep ( 2 )
        except HTTPError as e:
            time.sleep ( 2 )

    res = get_last_build_result ( job_name,"result" )
    print ( str ( id ) + " " + job_name + " is " + str ( res ) )
    if (res == "SUCCESS"):
        return True
    else:
        return False


def main(service_name, commit_id, commit_id_deploy):
    global SERVICE_NAME
    global COMMIT_ID
    global COMMIT_ID_DEPLOYED
    SERVICE_NAME = service_name
    COMMIT_ID = commit_id
    COMMIT_ID_DEPLOYED = commit_id_deploy


    try:
        res = jenkins_build (JOB_LIST_HISTORY_CHANGES)
        if ( res == False):
            sys.exit(1)
    except Exception as e:
        print ("Usage: python3 galaxy_publish.py "
            "${SERVICE_NAME} ${COMMIT_ID} ${COMMIT_ID_DEPLOYED} !!!")
        sys.exit(1)

    continue_or_not()


    try:
        res = jenkins_build ( JOB_GALAXY_PABULISH )
        if ( res == False ):
            sys.exit(1)
    except Exception as e:
        print ("Usage: python3 galaxy_publish.py "
            "${SERVICE_NAME} ${COMMIT_ID} ${COMMIT_ID_DEPLOYED} !!!")
        sys.exit(1)



JOB_LIST_HISTORY_CHANGES = "list-history-changes"
JOB_GALAXY_PABULISH = "galaxy-publish-clone"
TOKEN_JENKINS = "Appstore"
URL = "jenkins.corp.zgcszkw.com"
try:
    JENKINS_NAME = os.environ["JENKINS_NAME"]
    JENKINS_PASSWD = os.environ["JENKINS_PASSWD"]
except Exception as e:
    print ( "ERROR: CAN'T FIND JENKINS_NAME or JENKINS_PASSWD in ENV!!!" )
    sys.exit ( 1 )
if __name__ == '__main__':
    main(sys.argv[1],  sys.argv[2], sys.argv[3])

