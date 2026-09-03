#!/bin/python3

# This script pull data from ALl environment of Control-M for daily status and upload to DWH non prod currently
# V1 - 26/04/2020 - Chandramani Shakya
global lastday
import cx_Oracle
import os
from datetime import datetime, timedelta
lastday=datetime.strftime(datetime.now() - timedelta(1), '%y%m%d')
import csv
filepath="/opt/ctms/em_daily_data/"
print("Data for "+lastday+" getting pull using this script ")
def write_db(filename):
    dwhconn= open(filepath+".dwhconn" , "r")
    dwhconnd=dwhconn.read().rstrip('\n')
    dwhconn.close()
    con = cx_Oracle.connect(dwhconnd)
    cur = con.cursor()
    with open(filepath+filename, "r") as daily_file:
        csv_reader = csv.reader(daily_file, delimiter=",")
        for lines in csv_reader:
            cur.execute("INSERT into EM_DAILY_DATA (APPLICATION , JOB_NAME , ORDER_TABLE , TASK_TYPE , OWNER , ODATE , ORDER_TIME , MAX_WAIT , START_TIME , END_TIME , STATUS ,STATE, ELAPSED_RUNTIME, DELETE_FLAG ,CYCLIC, RERUN_COUNTER,CTM_ENV) values (:1, :2, :3, :4, :5, :6,:7, :8, :9, :10, :11, :12,:13, :14, :15, :16,:17)",
(lines[0], lines[1], lines[2], lines[3], lines[4], lines[5],lines[6], lines[7], lines[8], lines[9], lines[10], lines[11],lines[12], lines[13], lines[14], lines[15], lines[16]))
    cur.close()
    con.commit()
    con.close()


def pulldatauat():
        uatconn= open(filepath+".uatconn" , "r")
        uatconnd=uatconn.read().rstrip('\n')
        uatconn.close()
        UAT="001"
        EBF="003"
        PER="002"
        queryu="select JOB_NAME , APPLICATION ,ORDER_TABLE , TASK_TYPE , OWNER , ODATE , ORDER_TIME , MAX_WAIT , START_TIME , END_TIME , STATUS ,STATE, ELAPSED_RUNTIME, DELETE_FLAG ,CYCLIC, RERUN_COUNTER from A"+lastday+UAT+"_AJOB"
        con = cx_Oracle.connect(uatconnd)

        cur =con.cursor()
        with open(filepath+"filuat1.csv", "w", newline="\n" )  as f_handle:
                writer = csv.writer(f_handle)
        # Add the header/column names
                #iheader = ["JOB_NAME ","APPLICATION","ORDER_TABLE","TASK_TYPE ", "OWNER" , "ODATE ", "ORDER_TIME ", "MAX_WAIT ", "START_TIME ", "END_TIME ", "STATUS" ,"STATE", "ELAPSED_RUNTIME", "DELETE_FLAG ","CYCLIC", "RERUN_COUNTER"]
                #writer.writerow(header)
    # Iterate over `data`  and  write to the csv file
                cur.execute(queryu)
                for row in cur:
                        writer.writerow(row)
        cur.close()
        con.close()

        reader = csv.reader(open(filepath+"filuat1.csv","r"))
        writer = csv.writer(open(filepath+"filuat2.csv","w"))
        #headers = next(reader)
        #headers.append("CTM_ENVIRONMENT")
        #writer.writerow(headers)
        for row in reader:
            row.append("FIL-UAT")
            writer.writerow(row)
        os.remove(filepath+"filuat1.csv")

#This will be for perf environment
        queryper="select JOB_NAME , APPLICATION ,ORDER_TABLE , TASK_TYPE , OWNER , ODATE , ORDER_TIME , MAX_WAIT , START_TIME , END_TIME , STATUS ,STATE, ELAPSED_RUNTIME, DELETE_FLAG ,CYCLIC, RERUN_COUNTER from A"+lastday+PER+"_AJOB"
        con = cx_Oracle.connect(uatconnd)
        cur =con.cursor()
        with open(filepath+"filper1.csv", "w", newline="\n" )  as f_handle:
                writer = csv.writer(f_handle)
        # Add the header/column names
                #header = ["JOB_NAME ","APPLICATION","ORDER_TABLE","TASK_TYPE ", "OWNER" , "ODATE ", "ORDER_TIME ", "MAX_WAIT ", "START_TIME ", "END_TIME ", "STATUS" ,"STATE", "ELAPSED_RUNTIME", "DELETE_FLAG ","CYCLIC", "RERUN_COUNTER","CTM_ENVIRONMENT"]
                #writer.writerow(header)
    # Iterate over `data`  and  write to the csv file
                cur.execute(queryper)
                for row in cur:
                        writer.writerow(row)
        cur.close()
        con.close()

        reader = csv.reader(open(filepath+"filper1.csv","r"))
        writer = csv.writer(open(filepath+"filper2.csv","w"))
        #headers = next(reader)
        #headers.append("CTM_ENVIRONMENT")
        #writer.writerow(headers)
        for row in reader:
            row.append("FIL-PER")
            writer.writerow(row)
        os.remove(filepath+"filper1.csv")

#This section is for EBF environment
        queryebf="select JOB_NAME , APPLICATION ,ORDER_TABLE , TASK_TYPE , OWNER , ODATE , ORDER_TIME , MAX_WAIT , START_TIME , END_TIME , STATUS ,STATE, ELAPSED_RUNTIME, DELETE_FLAG ,CYCLIC, RERUN_COUNTER from A"+lastday+EBF+"_AJOB"
        con = cx_Oracle.connect(uatconnd)
        cur =con.cursor()
        with open(filepath+"filebf1.csv", "w", newline="\n" )  as f_handle:
                writer = csv.writer(f_handle)
                cur.execute(queryebf)
                for row in cur:
                        writer.writerow(row)
        cur.close()
        con.close()

        reader = csv.reader(open(filepath+"filebf1.csv","r"))
        writer = csv.writer(open(filepath+"filebf2.csv","w"))
        for row in reader:
            row.append("FIL-EBF")
            writer.writerow(row)
        os.remove(filepath+"filebf1.csv")

#os.system("cat "+filepath+"filuat2.csv > "+filepath+"finaloutput.csv")
#os.system("cat "+filepath+"filebf2.csv >> "+filepath+"finaloutput.csv")
#os.system("cat "+filepath+"filper2.csv >> "+filepath+"finaloutput.csv")

def pulldatasit():
        sitconn= open(filepath+".sitconn" , "r")
        sitconnd=sitconn.read().rstrip('\n')
        sitconn.close()
        DEV="001"
        QA="003"
        SIT="002"
        DIT="004"
        # This pull data for DEV environment
        querydev="select JOB_NAME , APPLICATION ,ORDER_TABLE , TASK_TYPE , OWNER , ODATE , ORDER_TIME , MAX_WAIT , START_TIME , END_TIME , STATUS ,STATE, ELAPSED_RUNTIME, DELETE_FLAG ,CYCLIC, RERUN_COUNTER from A"+lastday+DEV+"_AJOB"
        con = cx_Oracle.connect(sitconnd)
        cur =con.cursor()
        with open(filepath+"fildev1.csv", "w", newline="\n" )  as f_handle:
                writer = csv.writer(f_handle)
                cur.execute(querydev)
                for row in cur:
                        writer.writerow(row)
        cur.close()
        con.close()
        reader = csv.reader(open(filepath+"fildev1.csv","r"))
        writer = csv.writer(open(filepath+"fildev2.csv","w"))
        for row in reader:
            row.append("FIL-DEV")
            writer.writerow(row)
        os.remove(filepath+"fildev1.csv")
        # This pull data for QA environment
        queryqa="select JOB_NAME , APPLICATION ,ORDER_TABLE , TASK_TYPE , OWNER , ODATE , ORDER_TIME , MAX_WAIT , START_TIME , END_TIME , STATUS ,STATE, ELAPSED_RUNTIME, DELETE_FLAG ,CYCLIC, RERUN_COUNTER from A"+lastday+QA+"_AJOB"
        con = cx_Oracle.connect(sitconnd)
        cur =con.cursor()
        with open(filepath+"filqa1.csv", "w", newline="\n" )  as f_handle:
                writer = csv.writer(f_handle)
                cur.execute(queryqa)
                for row in cur:
                        writer.writerow(row)
        cur.close()
        con.close()
        reader = csv.reader(open(filepath+"filqa1.csv","r"))
        writer = csv.writer(open(filepath+"filqa2.csv","w"))
        for row in reader:
            row.append("FIL-QA")
            writer.writerow(row)
        os.remove(filepath+"filqa1.csv")
        # This pull data for SIT environment
        querysit="select JOB_NAME , APPLICATION ,ORDER_TABLE , TASK_TYPE , OWNER , ODATE , ORDER_TIME , MAX_WAIT , START_TIME , END_TIME , STATUS ,STATE, ELAPSED_RUNTIME, DELETE_FLAG ,CYCLIC, RERUN_COUNTER from A"+lastday+SIT+"_AJOB"
        con = cx_Oracle.connect(sitconnd)
        cur =con.cursor()
        with open(filepath+"filsit1.csv", "w", newline="\n" )  as f_handle:
                writer = csv.writer(f_handle)
                cur.execute(querysit)
                for row in cur:
                        writer.writerow(row)
        cur.close()
        con.close()
        reader = csv.reader(open(filepath+"filsit1.csv","r"))
        writer = csv.writer(open(filepath+"filsit2.csv","w"))
        for row in reader:
            row.append("FIL-SIT")
            writer.writerow(row)
        os.remove(filepath+"filsit1.csv")
        # This pull data for DIT environment
        querydit="select JOB_NAME , APPLICATION ,ORDER_TABLE , TASK_TYPE , OWNER , ODATE , ORDER_TIME , MAX_WAIT , START_TIME , END_TIME , STATUS ,STATE, ELAPSED_RUNTIME, DELETE_FLAG ,CYCLIC, RERUN_COUNTER from A"+lastday+DIT+"_AJOB"
        con = cx_Oracle.connect(sitconnd)
        cur =con.cursor()
        with open(filepath+"fildit1.csv", "w", newline="\n" )  as f_handle:
                writer = csv.writer(f_handle)
                cur.execute(querydit)
                for row in cur:
                        writer.writerow(row)
        cur.close()
        con.close()
        reader = csv.reader(open(filepath+"fildit1.csv","r"))
        writer = csv.writer(open(filepath+"fildit2.csv","w"))
        for row in reader:
            row.append("FIL-DIT")
            writer.writerow(row)
        os.remove(filepath+"fildit1.csv")

#os.system("cat "+filepath+"fildev2.csv > "+filepath+"finaloutput.csv")
#os.system("cat "+filepath+"filsit2.csv >> "+filepath+"finaloutput.csv")
#os.system("cat "+filepath+"filqa2.csv >> "+filepath+"finaloutput.csv")
#os.system("cat "+filepath+"fildit2.csv >> "+filepath+"finaloutput.csv")

def pulldataprd():
        prdconn= open(filepath+".prdconn" , "r")
        prdconnd=prdconn.read().rstrip('\n')
        prdconn.close()
        PRD="001"
        # This pull data for PRD environment
        queryprd="select JOB_NAME , APPLICATION ,ORDER_TABLE , TASK_TYPE , OWNER , ODATE , ORDER_TIME , MAX_WAIT , START_TIME , END_TIME , STATUS ,STATE, ELAPSED_RUNTIME, DELETE_FLAG ,CYCLIC, RERUN_COUNTER from A"+lastday+PRD+"_AJOB"
        con = cx_Oracle.connect(prdconnd)
        cur =con.cursor()
        with open(filepath+"filprd1.csv", "w", newline="\n" )  as f_handle:
                writer = csv.writer(f_handle)
                cur.execute(queryprd)
                for row in cur:
                        writer.writerow(row)
        cur.close()
        con.close()
        reader = csv.reader(open(filepath+"filprd1.csv","r"))
        writer = csv.writer(open(filepath+"filprd2.csv","w"))
        for row in reader:
            row.append("FIL-PRD")
            writer.writerow(row)
        os.remove(filepath+"filprd1.csv")

pulldatauat()
write_db("filuat2.csv")
write_db("filebf2.csv")
write_db("filper2.csv")
pulldatasit()
write_db("filsit2.csv")
write_db("fildev2.csv")
write_db("fildit2.csv")
write_db("filqa2.csv")
pulldataprd()
write_db("filprd2.csv")


