# -*- coding: utf-8 -*-
"""
Created on Fri Aug 21 17:14:27 2020

@author: a629112
"""


import requests
import json
import datetime
import pytz
utc = pytz.utc
changenumber="CHG00130930"
incident="INC00504415"
changetask = "TASK"
apikey = "ecb3a657-1573-4581-b320-03d9769608d2"
devapikey = "f90f9084-8ca8-4b98-bcb2-889bb73873d8"

def servicenowvalidation():
    x = datetime.datetime.now(tz=utc)
    nowt=(x.strftime("%d-%m-%Y %H:%M:%S"))        #Time value current time in String 
    nowt1=(x.strftime("%d/%m/%Y %H:%M:%S"))
    nowt=datetime.datetime.strptime(nowt ,"%d-%m-%Y %H:%M:%S")    #Time in again time-delta to compare it with other time values 
    nowtime1=datetime.datetime.strptime(nowt1 ,"%d/%m/%Y %H:%M:%S")   
    nowtime=str(nowtime1)        
    
    endpointurl = "https://gateway.bip.uk.fid-intl.com/api/tis/sn/v2/change?sysparm_query=number="
    devendpointurl="https://apigateway-tisdev.uk.fid-intl.com:15012/api/tis/sn/v2/change?sysparm_query=number="
    endpointurl1 = endpointurl+changenumber
    
    
    data={'apikey': apikey   ,'Content-Type': 'application/json', 'Accept': 'application/json'}
    r = requests.get(endpointurl1 , headers=data ,verify = False )
    res = json.loads(r.text)

    try:
        startt=str(res["result"][0]["start_date"])
        startt=datetime.datetime.strptime(startt ,"%d/%m/%Y %H:%M:%S")  #this is for Timedelta conversion to compare it with now time
        starttime=str(startt)  # this is string to return value 
        print(type(startt))
        endt=str(res["result"][0]["end_date"])
        endt=datetime.datetime.strptime(endt ,"%d/%m/%Y %H:%M:%S")
        endtime=str(endt)
        cstatus=str(res["result"][0]["approval"])
        cstate=str(res["result"][0]["state"])
        cenv=str(res["result"][0]["u_used_for"])
        if res["result"][0]["u_used_for"] == 'lab' and res["result"][0]["approval"] == 'Approved' and res["result"][0]["state"] == 'Implement' and nowt > startt and nowt < endt :
            diffrence = int((endt - nowt).total_seconds())
            endt=str(res["result"][0]["end_date"])
            return ("diffrence= "+str(diffrence) + "\n" + endt )
           
        else:
           return "Your change ="+changenumber+" is not valid Change Environment= "+cenv+"\n Change State ="+cstate+"\n Change Status ="+cstatus+"\n Change Start Time ="+starttime+"\n Current Time ="+nowtime+"\n Change End time ="+endtime
    except IndexError:
        return "Change ticket is not valid , not found in Service Now Please check again "
    
def change_comment_update():
    endurl = "https://gateway.bip.uk.fid-intl.com/api/tis/sn/v2/addcomments/change_request/"
    endurl1 = endurl+change_sys_id
    apikey = "ecb3a657-1573-4581-b320-03d9769608d2"
    headers={'apikey': apikey   ,'Content-Type': 'application/json', 'Accept': 'application/json'}
    comment = "Control-M LAB Break Glass access is Granted to user "+uname+" (AID- "+aid+" ) based on CTASK - "+changetask+" associated to this change , on Control-M application "+appname+"*"
    data={"comments" : comment }
    requests.patch( endurl1 , headers=headers , json=data , verify=False)
    #return redirect("https://filcmems.uk.fid-intl.com:8450/deleteorderjob" , code = 302 )
    return redirect(url_for('deleteorderjob'))


def incidentvalidation():
    #incidenturl = "https://gateway.bip.uk.fid-intl.com/api/tis/sn/v2/incident?sysparm_query=number="+incident
    ticket = "INC00412420"
    devicidenturl="https://apigateway-tisdev.uk.fid-intl.com:15012/api/tis/sn/v2/incident?sysparm_query=number="+ticket
    #changedev="https://apigateway-tisdev.uk.fid-intl.com:15012/api/tis/sn/v2/change?sysparm_query=number=CHG00108002"
    APIKEYDEV="f90f9084-8ca8-4b98-bcb2-889bb73873d8"
    headers1={'apikey': APIKEYDEV  ,'Content-Type': 'application/json', 'Accept': 'application/json'}
    r = requests.get(devicidenturl , headers=headers1 , verify=False)
    res = json.loads(r.text)
    #print(res)
    sysid = str(res["result"][0]["sys_id"])
    impact = int(res["result"][0]["impact"])
    urgency = str(res["result"][0]["urgency"])
    
    if (( impact == 3 and (urgency == "High" or urgency == "Critical")) or impact <= 2 ):
        print("true")
    else:
        print("not high impact ticket")
    
    
    
    print(ticket+"   "+str(impact)+"   "+urgency)
    comment = "Control-M LAB Break Glass access is Granted to user TEST"
    #data={"work_notes" : comment , "u_sys_id" : sysid }
    #endurl ="https://apigateway-tisdev.uk.fid-intl.com:15012/api/tis/sn/v2/incident/"
    
    #r=requests.patch( endurl , headers=headers1 , json=data, verify=False)
    #print(r)
    #print(json.loads(r.text))
    
def incident_note_update():
    ticket = "INC00414801"
    devicidenturl="https://apigateway-tisdev.uk.fid-intl.com:15012/api/tis/sn/v2/incident?sysparm_query=number="+ticket
    APIKEYDEV="f90f9084-8ca8-4b98-bcb2-889bb73873d8"
    headers1={'apikey': APIKEYDEV  ,'Content-Type': 'application/json', 'Accept': 'application/json'}
    r = requests.get(devicidenturl , headers=headers1 , verify=False)
    res = json.loads(r.text)
    #print(res)
    i_sysid = str(res["result"][0]["sys_id"])
    print(i_sysid)
    endurl = "https://apigateway-tisdev.uk.fid-intl.com:15012/api/tis/sn/v2/incident"
    comment = "Control-M LAB Break Glass access is Granted to user "
    data = {"u_sys_id": i_sysid , "work_notes": comment}
    headers1={'apikey': devapikey  ,'Content-Type': 'application/json', 'Accept': 'application/json'}
    requests.patch( endurl , headers=headers1 , json=data, verify=False)
    global sleep_time
    sleep_time = 7200
    #return redirect(url_for('deleteorderjob'))

#incidentvalidation()
incident_note_update()
#print(servicenowvalidation())

    