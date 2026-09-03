##########################################################################################################################
# This Script provide break glass acecss , you need to run thie script as backgroup process by some job                  #
# supporting script (delete_user_role.py ) run which is for delting user / group and kicking user session from EM        #
#                                                                                                                        #
# Version # DATE # Author # Description                                                                                  #
# V1.0   9-July-20 - Chandramani  -- initial_version                                                                     #
# V1.1   11-Aug-20 - Chandramani -- updated script for handling Change end time
                                        #
# V2.0    21-Aug-20 - Chandramani - updated Roles name tag with user id e.g TEMP_<APPID>_<AID>_Admin
# V2.1    24-Aug-20 - Chandramani - updated now time to convert it in absolute GMT as SNOW uses GMT when fetch from back-end #
# V4.0    10-Sept-20 - Chandramani - Updated scrip to capture ICTECH ID and put it while ordering job to update status in ICTECH#
# V5.0    14-Sept-20 - Chandramani - Updated scrip to WORK WITH HIGH IMPACT INCIDENT ALSO   #
# V6.0     15-Sep-20 -  Chandramani - Updated to test against servicenow DEV instance                                         
# v7.0     18-Sep-20  - Chandramani -- Updated to take 3/4 character as APPNAME and restricted all SPECIAL CHARACTER 
##########################################################################################################################
#!/bin/python3
wdir="/controlm/ctmemprd/customscripts/Break_glass_access/"
tempdir="/controlm/ctmemprd/customscripts/Break_glass_access/temp_access_files/"
from flask import Flask , render_template , redirect , url_for
from flask import request
import requests
import json
import re
import datetime
import pytz     #thsi module is for timezone calculation
utc = pytz.utc  # defining utc = gmt
baseurl="https://filcmemp.uk.fid-intl.com:8443/automation-api/"
ctms="FIL-PRD"
username = 'ctmadmin_api'
myfile= open(wdir+".pass" , "r")
password=myfile.read().rstrip('\n')
myfile.close()
apikey = "ecb3a657-1573-4581-b320-03d9769608d2"
#devapikey = "f90f9084-8ca8-4b98-bcb2-889bb73873d8"
#apikey = "f90f9084-8ca8-4b98-bcb2-889bb73873d8"
app = Flask(__name__)

@app.route('/')
def index():
    return "This is API endpoint method POST , /authorization "

@app.route('/authorization',methods=['POST'])
def authorization():
    global changetask
    global appname
    global aid
    global ctmbgid
    appname = request.args.get('appname')
    aid = request.args.get("aid")
    changetask = request.args.get("changetask")
    ctmbgid = request.args.get("ctmbgid")
    changetask = str(changetask).upper()
    regex = re.compile('[@!#$%^&*()<>?/\|}{~:]')  # added for avoid special character in application name
    if regex.search(appname) == None:
        if (len(appname)) == 3 or (len(appname)) == 4:
            endurl = "https://filcmemp.uk.fid-intl.com:8445/authorization_start?appname="+appname+"&aid="+aid+"&changetask="+changetask
            r = requests.post(endurl , verify=False)
            return r.text
        else:
            return "++Input Error - Application name must be 3 or 4 character only !!! Please try again "
    else:
        return "++Input Error - Application name contain Special character [@_!#$%^&*()<>?/\|}{~:] "
@app.route('/authorization_start',methods=['POST'])
def authorization_start():
    print(ctmbgid)
    return redirect(url_for('uservalidation'))

@app.route('/uservalidation',methods=["GET","POST"])
def uservalidation():
    global uname
    global agroup
    global i_sysid
    global changenumber
    userurl = "https://gateway.bip.uk.fid-intl.com/api/tis/sn/v2/user?sysparm_query=user_name="
    userurl1 = userurl+aid
    headers={'apikey': apikey   ,'Content-Type': 'application/json', 'Accept': 'application/json'}
    r = requests.get(userurl1 , headers=headers , verify=False )
    #print(r.text)
    res = json.loads(r.text)
    try:
        uname=res["result"][0]["name"]
        print(uname)
        if (changetask[:3]).upper() == "INC":
            incidenturl = "https://gateway.bip.uk.fid-intl.com/api/tis/sn/v2/incident?sysparm_query=number="+changetask
            data={'apikey': devapikey   ,'Content-Type': 'application/json', 'Accept': 'application/json'}
            r = requests.get(incidenturl , headers=data ,verify = False )
            res = json.loads(r.text)
            try:
                resolvedat=res["result"][0]["resolved_at"]
                i_sysid = str(res["result"][0]["sys_id"])
                impact = int(res["result"][0]["impact"])
                urgency = str(res["result"][0]["urgency"])
                agroup = str(res["result"][0]["assignment_group"])
                if resolvedat != '':
                    return "Inicident Ticket "+changetask+" is not active, Please use right High Impact ticket"
                if (( impact == 3 and (urgency == "High" or urgency == "Critical")) or impact <= 2 ):
                    changenumber = changetask
                    return redirect(url_for('user_group_validation'))
                else:
                    return "Incident Ticket "+changetask+" is not High priority incident Ticket"
            except IndexError:
                return "Incident Ticket "+changetask+" is not found in ServiceNow , please check "
        else:
            return redirect(url_for('ctask_detail'))
    except IndexError:
        return "User ID "+aid+" is not valid Please check - its not found in ServiceNow"

@app.route('/ctask_detail',methods=['GET','POST'])
def ctask_detail():
    global changenumber
    global agroup
    ctaskurl = "https://gateway.bip.uk.fid-intl.com/api/tis/sn/v2/ctask?sysparm_query=number="
    ctaskurl1 = ctaskurl+changetask
    headers={'apikey': apikey   ,'Content-Type': 'application/json', 'Accept': 'application/json'}
    r = requests.get(ctaskurl1 , headers=headers , verify=False )
    res = json.loads(r.text)
    if len(res["result"]) == 0 :
        return "CTASK -"+changetask+" not found - Please check "
    else:
        agroup=res["result"][0]["assignment_group"]
        changenumber=res["result"][0]["parent"]
        #return redirect('https://filcmemp.uk.fid-intl.com:8450/servicenowvalidation',code = 302 )
        return redirect(url_for('servicenowvalidation'))

@app.route('/servicenowvalidation',methods=['GET','POST'])
def servicenowvalidation():
    #global agroup
    global change_sys_id
    global sleep_time
    #x = datetime.datetime.now()
    x = datetime.datetime.now(tz=utc)   #timezone in UTC/GMT
    nowt=(x.strftime("%d-%m-%Y %H:%M:%S"))
    nowt1=(x.strftime("%d/%m/%Y %H:%M:%S"))
    nowt=datetime.datetime.strptime(nowt ,"%d-%m-%Y %H:%M:%S")
    nowtime1=datetime.datetime.strptime(nowt1 ,"%d/%m/%Y %H:%M:%S")
    nowtime=str(nowtime1)
    print(nowt)
    endpointurl = "https://gateway.bip.uk.fid-intl.com/api/tis/sn/v2/change?sysparm_query=number="
    endpointurl1 = endpointurl+changenumber
    data={'apikey': apikey   ,'Content-Type': 'application/json', 'Accept': 'application/json'}
    r = requests.get(endpointurl1 , headers=data ,verify = False )
    res = json.loads(r.text)

    try:
        startt=str(res["result"][0]["start_date"])
        startt=datetime.datetime.strptime(startt ,"%d/%m/%Y %H:%M:%S")
        starttime=str(startt)
        print(type(startt))
        endt=str(res["result"][0]["end_date"])
        endt=datetime.datetime.strptime(endt ,"%d/%m/%Y %H:%M:%S")
        endtime=str(endt)
        cstatus=str(res["result"][0]["approval"])
        cstate=str(res["result"][0]["state"])
        cenv=str(res["result"][0]["u_used_for"])
        sleep_time= (endt-nowt).seconds
        if res["result"][0]["u_used_for"] == 'lab' and res["result"][0]["approval"] == 'Approved' and res["result"][0]["state"] == 'Implement' and nowt > startt and nowt < endt :
           #agroup=res["result"][0]["assignment_group"]
           #return redirect("https://filcmemp.uk.fid-intl.com:8450/filcreate" , code = 302)
           change_sys_id=str(res["result"][0]["sys_id"])
           #return "change is valid env is "+str(res["result"][0]["u_environment"])
           #return redirect("https://filcmemp.uk.fid-intl.com:8450/user_group_validation" , code = 302)
           return redirect(url_for('user_group_validation'))
           #return "Servicenow validationOK moving to Group validation"
        else:
           return "Your change ="+changenumber+" is not valid associated to CTASK ="+changetask+"\n"+"Change Environment= "+cenv+"\n Change State ="+cstate+"\n Change Status ="+cstatus+"\n Change Start Time(GMT) ="+starttime+"\n Current Time(GMT) ="+nowtime+"\n Change End time(GMT) ="+endtime
    except IndexError:
        return "Change changetask is not valid , not found in Service Now Please check again "
@app.route ('/user_group_validation',methods=['GET','POST'])
def user_group_validation():
    snowurl = "https://gateway.bip.uk.fid-intl.com/api/tis/sn/v2/groupmembers?sysparm_query=group.name="
    snowurl1 = snowurl+agroup
    data={'apikey': apikey   ,'Content-Type': 'application/json', 'Accept': 'application/json'}
    r = requests.get( snowurl1 , headers=data , verify=False)
    res = json.loads(r.text)
    if len(res["result"]) == 0 :
        return "group "+agroup+" not found"
    else:
        res = str(res["result"])
        if uname in res:
           #return redirect("https://filcmemp.uk.fid-intl.com:8450/filcreate" , code = 302)
           return redirect(url_for('filecreate'))
        else:
            return "User "+uname+" is not part of Implementation/assignment group -"+agroup+" of Change task or Incident ticket"

@app.route('/filcreate',methods=['GET','POST'])
def filecreate():
    #print("aid=",aid)
    with open(wdir+"REFRENCE_Admin.json", "r") as sourcerole:
        lines = sourcerole.readlines()
    with open(tempdir+appname+"_temp_Admin1.json", "w") as targetrole:
        for line in lines:
            targetrole.write(re.sub(r'REFRENCE', appname , line))
    with open(tempdir+appname+"_temp_Admin1.json", "r") as sourcerole:
        lines = sourcerole.readlines()
    with open(tempdir+appname+"_temp_Admin.json", "w") as targetrole:
        for line in lines:
            targetrole.write(re.sub(r'AIDN', aid , line))
    with open(wdir+"REFRENCE_User.json", "r") as sourceuser:
        lines = sourceuser.readlines()
    with open(tempdir+aid+"_"+appname+"_temp_Admin.json", "w") as targetuser:
        for line in lines:
            targetuser.write(re.sub(r'AIDN', aid , line ))
    with open(tempdir+aid+"_"+appname+"_temp_Admin.json", "r") as sourceuser:
        lines = sourceuser.readlines()
    with open(tempdir+aid+"_"+appname+"_temp_Admin.json", "w") as targetuser:
       for line in lines:
           targetuser.write(re.sub(r'REFRENCE', appname , line ))
    with open(tempdir+aid+"_"+appname+"_temp_Admin.json", "r") as sourceuser:
        lines = sourceuser.readlines()
    with open(tempdir+aid+"_"+appname+"_temp_Admin.json", "w") as targetuser:
       for line in lines:
            targetuser.write(re.sub(r'DESC_D', "Temp access for "+appname+"change "+changenumber , line ))

    return redirect(url_for('tokengen'))

@app.route("/tokengen",methods=["GET","POST"])
def tokengen():
    global token
    global data
    loginurl = baseurl + 'session/login'  # The login url
    body={"password": password, "username": username}
    json.dumps(body)
    r = requests.post(loginurl, json=body, verify=False)


    loginresponce = json.loads(r.text)
    if 'errors' in loginresponce:
        #print(json.dumps(loginresponce['errors'][0]['message']))
        return render_template ("fatal_error.html")
    if 'token' in loginresponce:  # If token exists in the json response set the value to the variable token
        token = json.loads(r.text)['token']
    else:
        return "Fatal Error !!!! Please contact Control-M admin team for assitance, Please share error code : ++tokegen failed !"

    print('Token: ' + token)
    data=json.loads('{"Authorization": "Bearer ' + token + '"}')
    #return redirect("https://filcmemp.uk.fid-intl.com:8450/createrole" , code = 302)
    return redirect(url_for('createrole'))

@app.route("/createrole",methods=["GET","POST"])
def createrole():
    print("4. calling role creation")
    createroleurl = baseurl + "config/authorization/role"
    data={"Authorization": "Bearer " + token ,"Annotation-Subject" : aid+"_"+appname+"_temp_access"  , "Annotation-Description" : changenumber }
    uploaded_files = [
        ("roleFile", ("roleDefinition.json", open(tempdir+appname+"_temp_Admin.json", "rb") , "application/json"))
        ]
    r2= requests.post( createroleurl , files=uploaded_files ,headers=data , verify=False  )
    print(r2)
    print(r2.text)
    if "Role was created successfully." or "already exists" in r2.text:
        #return redirect("https://filcmemp.uk.fid-intl.com:8450/createuser", code = 302)
        return redirect(url_for('createuser'))
        #createuser()
    else:
        return "Fatal Error !!!! Please contact Control-M admin team for assitance, Please share error Code: ++groupcreation failed!"
@app.route("/createuser",methods=["GET","POST"])
def createuser():
    print("5. adding user to role")
    addusereurl = baseurl + "config/authorization/user"
    data={"Authorization": "Bearer " + token ,"Annotation-Subject" : aid+"_"+appname+"_temp_access"  , "Annotation-Description" : changenumber }
    uploaded_files = [
        ("userFile", ("userDefinition.json", open(tempdir+aid+"_"+appname+"_temp_Admin.json", "rb") , "application/json"))
        ]
    #Service
    r2= requests.post( addusereurl , files=uploaded_files ,headers=data , verify=False  )
    print(r2)
    print(r2.text)
    if ("User was created successfully." in r2.text or "already exists" in r2.text ):
        #return redirect("https://filcmemp.uk.fid-intl.com:8450/change_comment_update" , code = 302 )
        if (changetask[:3]).upper() == "INC":
            return redirect(url_for("incident_note_update"))
        else:
            return redirect(url_for('change_comment_update'))

    else:
        #return "operation failled please contact admin team "
        return "Fatal Error !!!! Please contact Control-M admin team for assitance , Please share error Code: ++usercreation failed !"

@app.route("/change_comment_update",methods=["GET","POST"] )
def change_comment_update():
    endurl = "https://gateway.bip.uk.fid-intl.com/api/tis/sn/v2/addcomments/change_request/"
    endurl1 = endurl+change_sys_id

    headers={'apikey': apikey   ,'Content-Type': 'application/json', 'Accept': 'application/json'}
    comment = "Control-M LAB Break Glass access is Granted to user "+uname+" (AID- "+aid+" ) based on CTASK - "+changetask+" associated to this change , on Control-M application "+appname+"*"
    data={"comments" : comment }
    requests.patch( endurl1 , headers=headers , json=data , verify=False)
    #return redirect("https://filcmemp.uk.fid-intl.com:8450/deleteorderjob" , code = 302 )
    return redirect(url_for('deleteorderjob'))

@app.route("/incident_note_update",methods=["GET","POST"] )
def incident_note_update():
    endurl = "https://gateway.bip.uk.fid-intl.com/api/tis/sn/v2/incident"
    comment = "Control-M LAB Break Glass access is Granted to user "+uname+" (AID- "+aid+" ) based on High Impact incident- "+changetask+" on Control-M application "+appname+"*"
    data = {"u_sys_id": i_sysid , "work_notes": comment}
    headers1 ={'apikey': devapikey  ,'Content-Type': 'application/json', 'Accept': 'application/json'}
    requests.patch( endurl , headers=headers1 , json=data, verify=False)
    global sleep_time
    sleep_time = 7200
    return redirect(url_for('deleteorderjob'))

@app.route("/deleteorderjob",methods=["GET","POST"])
def deleteorderjob():
       orderurl = baseurl + "run/order"
       headers={"Authorization": "Bearer"  + token   ,"Content-Type": "application/json", "Accept": "application/json"}
       data={
        "folder": "CTM_USER_MAINT",
        "hold": "false",
        "jobs": "CTM_TEMP_USER_CLEANUP",
        "ctm": ctms,
        "variables": [{
                "PARM1": aid },
                {"PARM2": appname + "_TEMP_"+aid+"_Admin"},
                {"PARM3": changenumber}, {"PARM4": ctmbgid },
                {"PARM5": sleep_time }]
}

       print(data)
       r = requests.post(orderurl, headers=headers , json=data  ,verify=False )
       print(json.loads(r.text))
       print(type(r))
       if r.status_code == 200:
           return "Hi "+uname+" Access granted to your ID "+aid
       else:
           return "Hi "+uname+" Access granted to your ID "+aid
           print(" error in ordering job ")

if __name__ == "__main__":
    context = (wdir+'filemprd.pem', wdir+'filemprd.key')#certificate and key files
    app.run( host="filcmemp.uk.fid-intl.com" , port=8445,  ssl_context=context)

