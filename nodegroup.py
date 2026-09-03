#!/bin/python
#coding=utf-8
import sys
import os
import requests
import json
import collections
from getpass import getpass
#import cx_Oracle
from numpy import base_repr
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
#passfile="/opt/controlm/ctmagdev/api_testing/deployemnet_jsons/"
baseurl="https://filcmems.uk.fid-intl.com:8443/automation-api/"
#baseurl="https://ukx10400.uk.fid-intl.com:8443/automation-api/"
#username="A629112"
#username="apiuser"
username="demo_user"
#username = input("enter your user name =")
#myfile= open(".passfile" , "r")
#password=myfile.read().rstrip('\n')
#myfile.close()
#password="EMDEV90#"
#password="@piu$£r"
password="demo_user"
#password=r'Hclindia\"6789'

def tokengen():
    global token
    global data
    loginurl = baseurl + 'session/login'  # The login url
    print(loginurl)
    #body = json.loads('{ "password": "' + password + '", "username": "' + username + '"}')  # create a json object to use as the body of the post to the login url
    body={"password": password, "username": username}
    json.dumps(body)
    r = requests.post(loginurl, json=body, verify="J:\\Chandramani\\JOb_deployemnet_CIcd\\filcmems_dev.pem")
    #r = requests.post(loginurl, json=body, verify="J:\\Chandramani\\JOb_deployemnet_CIcd\\em_ldap_ssl.pem")
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
    body = json.loads('{ "token": "' + token + '", "username": "' + username + '"}') #  logout url needs json with the token and username
    try:
        r4 = requests.post(logouturl, data=body,verify=False)  # a post on this url invalidates the token with the above json as the post data
        resultslogout=json.loads(r4.text)["message"]
        if "Successfully" in resultslogout:
            print("you are logged out" )
        
    except KeyError:
        print('session already expired')
        
def nodegrouplist():
    nodegroupurl = baseurl + "config/server/FIL-DEV/hostgroups"
    data=json.loads('{"Authorization": "Bearer ' + token + '"}')
    r = requests.get(nodegroupurl , headers=data , verify=False)
    print(json.loads(r.text))
    a=json.loads(r.text)
    #for x in range(len(a)):
    #    print((a[x]["name"] ,a[x]["description"]))
        
    #print(a[5])

def authgrouplist():
    authgroupurl = baseurl + "config/authorization/roles"
    data=json.loads('{"Authorization": "Bearer ' + token + '"}')
    r = requests.get(authgroupurl , headers=data , verify=False)
    print(json.loads(r.text))
    a=json.loads(r.text)
    for x in range(len(a)):
        print((a[x]["name"] ,a[x]["description"]))
        
def addnodegroup():
    addnodegroupurl = baseurl + "config/server/FIL-DEV/hostgroup/MANITEST/agent"
    headers={'Authorization': 'Bearer'  + token   ,'Content-Type': 'application/json', 'Accept': 'application/json'}
    data={'host' : 'filcmems6' }
    data1={'host' : 'filcmems5'}
    r = requests.post(addnodegroupurl , headers=headers , json=data , verify=False)
    r = requests.post(addnodegroupurl , headers=headers , json=data1 , verify=False)
    print(json.loads(r.text))

def listagentingroup():
    listagentingroupurl = baseurl + "config/server/FIL-DEV/hostgroup/AIML/agents"
    data=json.loads('{"Authorization": "Bearer ' + token + '"}')
    r= requests.get(listagentingroupurl , headers=data , verify=False)
    print(json.loads(r.text))
    a=json.loads(r.text)
    for x in range(len(a)):
        print(a[x]["host"])
        
def deletenodeingroup():
    ctm = input("enter CTM server name like FIL-DEV=")
    nodeg1 = input("enter node group to be updated= ")
    hostname1 = input("agent to be deleted from nodegroup=")
    deletenodeingroupurl = baseurl + "config/server/"+ ctm +"/hostgroup/"+ nodeg1 +"/agent/"+ hostname1 + ""
    data=json.loads('{"Authorization": "Bearer ' + token + '"}')
    r= requests.delete(deletenodeingroupurl , headers=data , verify=False)
    print(r.text)    
tokengen()
#
#authgrouplist()
#addnodegroup()
#nodegrouplist()
#listagentingroup() 
#deletenodeingroup()
#listagentingroup() 
logouturl()

    