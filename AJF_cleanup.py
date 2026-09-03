#/usr/bin/python3
import os
import sys
import requests
import json
import cx_Oracle
from numpy import base_repr
import multiprocessing
import time
# below is to disable insecure warning
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings()

# above line is to disable insecure warning of HTTPS /SSL

filepath="/opt/ctms/AJF_CLEANUP/"
baseurl="https://filcmems.uk.fid-intl.com:8443/automation-api/"
username="apiuser"
myfile= open(filepath+".passfile" , "r")
password=myfile.read().rstrip('\n')
myfile.close()

global odate1
global DC
a=list(sys.argv)
if len(a) < 2:
        sys.exit(" Please pass parameter 1 as Order date YYYYMMDD  ")
else:
        odate1 =str(a[1])

def tokengen():
    global token
    global data
    loginurl = baseurl + 'session/login'  # The login url
    body={"password": password, "username": username}
    json.dumps(body)
    r = requests.post(loginurl, json=body, verify=False)
    loginresponce = json.loads(r.text)
    if 'errors' in loginresponce:
        print(json.dumps(loginresponce['errors'][0]['message']))
        quit(1)
    if 'token' in loginresponce:  # If token exists in the json response set the value to the variable token
        token = json.loads(r.text)['token']
    else:
         print("Failed to get token for unknown reason, exiting...")
         quit(2)

    print('Token: ' + token)
    data=json.loads('{"Authorization": "Bearer ' + token + '"}')

def logouturl():
    logouturl = baseurl + "session/logout"
#    body = json.loads('{ "token": "' + token + '", "username": "' + username + '"}') #  logout url needs json with the token and username  -- old
    r = requests.post(logouturl, headers=data ,verify=False)
    print(r)
    print(r.text)

def sitcleanup():
    DC = "FIL-SIT"
    query="select orderno from cmr_ajf where state in('0','1','4','5','6','8','A','B','C','D','G','H') and order_time<"+odate1+"070000"+" and to_date(odate,'yyyymmdd')+maxwait<to_date("+odate1+",'yyyymmdd')-1 and holdflag!='D' "
    sitcon = open(filepath+".sitconn")
    sitconn = sitcon.read().rstrip('\n')
    sitcon.close()
    con = cx_Oracle.connect(sitconn)
    cur = con.cursor()
    cur.execute(query)
    for oid in cur:
        oid=str(oid)
        oid= oid.strip("(),")
        oid=int(oid)
        oid_s=base_repr(oid , 36)
        oid_s=oid_s.lower()
        while len(oid_s) < 5:
            oid_s = "0"+oid_s
        statusurl= baseurl + "run/jobs/status?jobid="+DC+":"+oid_s+""
        deleteurl  = baseurl + "run/job/"+DC+":"+oid_s+"/delete"
        killurl = baseurl + "run/job/"+DC+":"+oid_s+"/kill"
        holdurl = baseurl + "run/job/"+DC+":"+oid_s+"/hold"
        freeurl = baseurl + "run/job/"+DC+":"+oid_s+"/free"
        r1 = requests.get(statusurl , headers=data , verify=False)
        res = json.loads(r1.text)
        res = res["statuses"][-1]
        if res["held"] == True and res["status"] != "Executing":
            print(" secnario 1 - Held and not executing hence action Delete oid = "+oid_s)
            r1 = requests.post(deleteurl , headers=data , verify=False)
        elif res["type"] != "Folder" and res["type"] != "Sub-Table" and res["status"] == "Executing":
            print( " scenario 2 - Not folder/sub folder , status = executing , may be hung - needto kill -hold-delete oid= "+oid_s)
            r1 = requests.post(killurl , headers=data , verify=False)
            if "successfully" in r1.text:
                if res["held"] == True:
                    r1 = requests.post(freeurl , headers=data , verify=False)
                    time.sleep(1)
                    r1 = requests.post(holdurl , headers=data , verify=False)
                    time.sleep(1)
                    r1 = requests.post(deleteurl , headers=data , verify=False)
                else:
                    r1 = requests.post(holdurl , headers=data , verify=False)
                    time.sleep(1)
                    r1 = requests.post(deleteurl , headers=data , verify=False)
            else:
                r1 = requests.post('http://ukx10648:5050/kill?oid='+oid_s+'' , verify=False)
                if "JOB FORCED TO END" not in r1.text:
                    r1 = requests.post('http://ukx10649:5050/kill?oid='+oid_s+'' , verify=False)
                if res["held"] == True:
                    r1 = r1 = requests.post(freeurl , headers=data , verify=False)
                    time.sleep(1)
                    r1 = requests.post(holdurl , headers=data , verify=False)
                    time.sleep(1)
                    r1 = requests.post(deleteurl , headers=data , verify=False)
                else:
                    r1 = requests.post(holdurl , headers=data , verify=False)
                    time.sleep(1)
                    r1 = requests.post(deleteurl , headers=data , verify=False)

        elif (res["type"] == "Folder" or res["type"] == "Sub-Table") and res["status"] == "Executing" and res["held"] == True :
            print( " scenario 3 - type folder/sub folder , status = executing , may be hung - free and release= "+oid_s)
            r1 = requests.post(freeurl , headers=data , verify=False)
            time.sleep(2)
            r1 = requests.post(holdurl , headers=data , verify=False)
            time.sleep(1)
            r1 = requests.post(deleteurl , headers=data , verify=False)
        elif res["type"] != "Folder" and res["type"] != "Sub-Table" and res["status"] == "Ended Not OK" :
            print("scenario 4 :  Folder/sub-folder NO , Job failed - -hold and delete "+oid_s)
            r1 = requests.post(holdurl , headers=data , verify=False)
            time.sleep(1)
            r1 = requests.post(deleteurl , headers=data , verify=False)
        else:
            print("No Action Taken Detail -  status= ",res["status"],"name = " , res["name"], "type = ",res["type"], "jobID= ",res["jobId"] )

def ditcleanup():
    DC = "FIL-DIT"
    query="select orderno from cmr_ajf where state in('0','1','4','5','6','8','A','B','C','D','G','H') and order_time<"+odate1+"070000"+" and to_date(odate,'yyyymmdd')+maxwait<to_date("+odate1+",'yyyymmdd')-1 and holdflag!='D' "
    ditcon = open(filepath+".ditconn")
    ditconn = ditcon.read().rstrip('\n')
    ditcon.close()
    con = cx_Oracle.connect(ditconn)
    cur = con.cursor()
    cur.execute(query)
    for oid in cur:
        oid=str(oid)
        oid= oid.strip("(),")
        oid=int(oid)
        oid_s=base_repr(oid , 36)
        oid_s=oid_s.lower()
        while len(oid_s) < 5:
            oid_s = "0"+oid_s
        statusurl= baseurl + "run/jobs/status?jobid="+DC+":"+oid_s+""
        deleteurl  = baseurl + "run/job/"+DC+":"+oid_s+"/delete"
        killurl = baseurl + "run/job/"+DC+":"+oid_s+"/kill"
        holdurl = baseurl + "run/job/"+DC+":"+oid_s+"/hold"
        freeurl = baseurl + "run/job/"+DC+":"+oid_s+"/free"
        r2 = requests.get(statusurl , headers=data , verify=False)
        res = json.loads(r2.text)
        res = res["statuses"][-1]
        if res["held"] == True and res["status"] != "Executing":
            print(" secnario 1 - Held and not executing hence action Delete oid = "+oid_s)
            r2 = requests.post(deleteurl , headers=data , verify=False)
        elif res["type"] != "Folder" and res["type"] != "Sub-Table" and res["status"] == "Executing":
            print( " scenario 2 - Not folder/sub folder , status = executing , may be hung - needto kill -hold-delete oid= "+oid_s)
            r2 = requests.post(killurl , headers=data , verify=False)
            if "successfully" in r2.text:
                if res["held"] == True:
                    r2 = requests.post(freeurl , headers=data , verify=False)
                    time.sleep(1)
                    r2 = requests.post(holdurl , headers=data , verify=False)
                    time.sleep(1)
                    r2 = requests.post(deleteurl , headers=data , verify=False)
                else:
                    r2 = requests.post(holdurl , headers=data , verify=False)
                    time.sleep(1)
                    r2 = requests.post(deleteurl , headers=data , verify=False)
            else:
                r2 = requests.post('http://ukx10648:5070/kill?oid='+oid_s+'' , verify=False)
                if "JOB FORCED TO END" not in r2.text:
                    r2 = requests.post('http://ukx10649:5070/kill?oid='+oid_s+'' , verify=False)
                if res["held"] == True:
                    r2 = requests.post(freeurl , headers=data , verify=False)
                    time.sleep(1)
                    r2 = requests.post(holdurl , headers=data , verify=False)
                    time.sleep(1)
                    r2 = requests.post(deleteurl , headers=data , verify=False)
                else:
                    r2 = requests.post(holdurl , headers=data , verify=False)
                    time.sleep(1)
                    r2 = requests.post(deleteurl , headers=data , verify=False)

        elif (res["type"] == "Folder" or res["type"] == "Sub-Table") and res["status"] == "Executing" and res["held"] == True :
            print( " scenario 3 - type folder/sub folder , status = executing , may be hung - free and release= "+oid_s)
            r2 = requests.post(freeurl , headers=data , verify=False)
            time.sleep(2)
            r2 = requests.post(holdurl , headers=data , verify=False)
            time.sleep(1)
            r2 = requests.post(deleteurl , headers=data , verify=False)
        elif res["type"] != "Folder" and res["type"] != "Sub-Table" and res["status"] == "Ended Not OK" :
            print("scenario 4 :  Folder/sub-folder NO , Job failed - -hold and delete "+oid_s)
            r2 = requests.post(holdurl , headers=data , verify=False)
            time.sleep(1)
            r2 = requests.post(deleteurl , headers=data , verify=False)
        else:
            print("No Action Taken Detail -  status= ",res["status"],"name = " , res["name"], "type = ",res["type"], "jobID= ",res["jobId"] )
def devcleanup():
    DC = "FIL-DEV"
    query="select orderno from cmr_ajf where state in('0','1','4','5','6','8','A','B','C','D','G','H') and order_time<"+odate1+"070000"+" and to_date(odate,'yyyymmdd')+maxwait<to_date("+odate1+",'yyyymmdd')-1 and holdflag!='D' "
    devcon = open(filepath+".devconn")
    devconn = devcon.read().rstrip('\n')
    devcon.close()
    con = cx_Oracle.connect(devconn)
    cur = con.cursor()
    cur.execute(query)
    for oid in cur:
        oid=str(oid)
        oid= oid.strip("(),")
        oid=int(oid)
        oid_s=base_repr(oid , 36)
        oid_s=oid_s.lower()
        while len(oid_s) < 5:
            oid_s = "0"+oid_s
        statusurl= baseurl + "run/jobs/status?jobid="+DC+":"+oid_s+""
        deleteurl  = baseurl + "run/job/"+DC+":"+oid_s+"/delete"
        killurl = baseurl + "run/job/"+DC+":"+oid_s+"/kill"
        holdurl = baseurl + "run/job/"+DC+":"+oid_s+"/hold"
        freeurl = baseurl + "run/job/"+DC+":"+oid_s+"/free"
        r3 = requests.get(statusurl , headers=data , verify=False)
        res = json.loads(r3.text)
        res = res["statuses"][-1]
        if res["held"] == True and res["status"] != "Executing":
            print(" secnario 1 - Held and not executing hence action Delete oid = "+oid_s)
            r3 = requests.post(deleteurl , headers=data , verify=False)
        elif res["type"] != "Folder" and res["type"] != "Sub-Table" and res["status"] == "Executing":
            print( " scenario 2 - Not folder/sub folder , status = executing , may be hung - needto kill -hold-delete oid= "+oid_s)
            r3 = requests.post(killurl , headers=data , verify=False)
            if "successfully" in r3.text:
                if res["held"] == True:
                    r3 = requests.post(freeurl , headers=data , verify=False)
                    time.sleep(1)
                    r3 = requests.post(holdurl , headers=data , verify=False)
                    time.sleep(1)
                    r3 = requests.post(deleteurl , headers=data , verify=False)
                else:
                    r3 = requests.post(holdurl , headers=data , verify=False)
                    time.sleep(1)
                    r3 = requests.post(deleteurl , headers=data , verify=False)
            else:
                r3 = requests.post('http://ukx10648:5060/kill?oid='+oid_s+'' , verify=False)
                if "JOB FORCED TO END" not in r3.text:
                    r3 = requests.post('http://ukx10649:5060/kill?oid='+oid_s+'' , verify=False)
                if res["held"] == True:
                    r3 = requests.post(freeurl , headers=data , verify=False)
                    time.sleep(1)
                    r3 = requests.post(holdurl , headers=data , verify=False)
                    time.sleep(1)
                    r3 = requests.post(deleteurl , headers=data , verify=False)
                else:
                    r3 = requests.post(holdurl , headers=data , verify=False)
                    time.sleep(1)
                    r3 = requests.post(deleteurl , headers=data , verify=False)

        elif (res["type"] == "Folder" or res["type"] == "Sub-Table") and res["status"] == "Executing" and res["held"] == True :
            print( " scenario 3 - type folder/sub folder , status = executing , may be hung - free and release= "+oid_s)
            r3 = requests.post(freeurl , headers=data , verify=False)
            time.sleep(2)
            r3 = requests.post(holdurl , headers=data , verify=False)
            time.sleep(1)
            r3 = requests.post(deleteurl , headers=data , verify=False)
        elif res["type"] != "Folder" and res["type"] != "Sub-Table" and res["status"] == "Ended Not OK" :
            print("scenario 4 :  Folder/sub-folder NO , Job failed - -hold and delete "+oid_s)
            r3 = requests.post(holdurl , headers=data , verify=False)
            time.sleep(1)
            r3 = requests.post(deleteurl , headers=data , verify=False)
        else:
            print("No Action Taken Detail -  status= ",res["status"],"name = " , res["name"], "type = ",res["type"], "jobID= ",res["jobId"] )

def qacleanup():
    DC = "FIL-QA"
    query="select orderno from cmr_ajf where state in('0','1','4','5','6','8','A','B','C','D','G','H') and order_time<"+odate1+"070000"+" and to_date(odate,'yyyymmdd')+maxwait<to_date("+odate1+",'yyyymmdd')-1 and holdflag!='D' "
    qacon = open(filepath+".qaconn")
    qaconn = qacon.read().rstrip('\n')
    qacon.close()
    con = cx_Oracle.connect(qaconn)
    cur = con.cursor()
    cur.execute(query)
    for oid in cur:
        oid=str(oid)
        oid= oid.strip("(),")
        oid=int(oid)
        oid_s=base_repr(oid , 36)
        oid_s=oid_s.lower()
        while len(oid_s) < 5:
            oid_s = "0"+oid_s
        statusurl= baseurl + "run/jobs/status?jobid="+DC+":"+oid_s+""
        deleteurl  = baseurl + "run/job/"+DC+":"+oid_s+"/delete"
        killurl = baseurl + "run/job/"+DC+":"+oid_s+"/kill"
        holdurl = baseurl + "run/job/"+DC+":"+oid_s+"/hold"
        freeurl = baseurl + "run/job/"+DC+":"+oid_s+"/free"
        r4 = requests.get(statusurl , headers=data , verify=False)
        res = json.loads(r4.text)
        res = res["statuses"][-1]
        if res["held"] == True and res["status"] != "Executing":
            print(" secnario 1 - Held and not executing hence action Delete oid = "+oid_s)
            r4 = requests.post(deleteurl , headers=data , verify=False)
        elif res["type"] != "Folder" and res["type"] != "Sub-Table" and res["status"] == "Executing":
            print( " scenario 2 - Not folder/sub folder , status = executing , may be hung - needto kill -hold-delete oid= "+oid_s)
            r4 = requests.post(killurl , headers=data , verify=False)
            if "successfully" in r4.text:
                if res["held"] == True:
                    r4 = requests.post(freeurl , headers=data , verify=False)
                    time.sleep(1)
                    r4 = requests.post(holdurl , headers=data , verify=False)
                    time.sleep(1)
                    r4 = requests.post(deleteurl , headers=data , verify=False)
                else:
                    r4 = requests.post(holdurl , headers=data , verify=False)
                    time.sleep(1)
                    r4 = requests.post(deleteurl , headers=data , verify=False)
            else:
                r4 = requests.post('http://ukx10648:5080/kill?oid='+oid_s+'' , verify=False)
                if "JOB FORCED TO END" not in r4.text:
                    r4 = requests.post('http://ukx10649:5080/kill?oid='+oid_s+'' , verify=False)
                if res["held"] == True:
                    r4 = requests.post(freeurl , headers=data , verify=False)
                    time.sleep(1)
                    r4 = requests.post(holdurl , headers=data , verify=False)
                    time.sleep(1)
                    r4 = requests.post(deleteurl , headers=data , verify=False)
                else:
                    r4 = requests.post(holdurl , headers=data , verify=False)
                    time.sleep(1)
                    r4 = requests.post(deleteurl , headers=data , verify=False)

        elif (res["type"] == "Folder" or res["type"] == "Sub-Table") and res["status"] == "Executing" and res["held"] == True :
            print( " scenario 3 - type folder/sub folder , status = executing , may be hung - free and release= "+oid_s)
            r4 = requests.post(freeurl , headers=data , verify=False)
            time.sleep(2)
            r4 = requests.post(holdurl , headers=data , verify=False)
            time.sleep(1)
            r4 = requests.post(deleteurl , headers=data , verify=False)
        elif res["type"] != "Folder" and res["type"] != "Sub-Table" and res["status"] == "Ended Not OK" :
            print("scenario 4 :  Folder/sub-folder NO , Job failed - -hold and delete "+oid_s)
            r4 = requests.post(holdurl , headers=data , verify=False)
            time.sleep(1)
            r4 = requests.post(deleteurl , headers=data , verify=False)
        else:
            print("No Action Taken Detail -  status= ",res["status"],"name = " , res["name"], "type = ",res["type"], "jobID= ",res["jobId"] )

tokengen()
startt = time.perf_counter()
p1 = multiprocessing.Process(target=sitcleanup)
p2 = multiprocessing.Process(target=ditcleanup)
p3 = multiprocessing.Process(target=devcleanup)
p4 = multiprocessing.Process(target=qacleanup)

p1.start()
p2.start()
p3.start()
p4.start()

p1.join()
p2.join()
p3.join()
p4.join()

finished = time.perf_counter()
print("finished in "+str(round(finished - startt , 4 ))+" seconds")

