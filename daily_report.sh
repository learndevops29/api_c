#!/bin/ksh
#################################################################################################################################
#                                                                                                                                                                                        #
# 27/10/2018 - Updated as per V9 configuration -- Chandramani                                                                                                                            #
# 19/09/20119 - This is updated to generate report for FDW_SASA
#################################################################################################################################
set -x

FDW_SASA()
{
Temp_File_Ok=/controlm/ctmsvprd/local/reports/FDW_SASA_Stats_report/ajf_details_ok.txt
final=/controlm/ctmsvprd/local/reports/FDW_SASA_Stats_report/final_ok.txt
Date=`date '+%m%d%y'`
Date1=`date +"%m%d%Y" --date="1 days ago"`
HOME=/controlm/ctmsvprd/local/reports/FDW_SASA_Stats_report
finalcsv=/controlm/ctmsvprd/local/reports/FDW_SASA_Stats_report/Stats_$Date.csv
finalcsv_mail=/controlm/ctmsvprd/local/reports/FDW_SASA_Stats_report/FDW_SASA_PRD_$Date.csv
Mail_Body=/controlm/ctmsvprd/local/reports/FDW_SASA_Stats_report/message.txt
#MAIL="a629112@fil.com"
html_file=/controlm/ctmsvprd/local/reports/FDW_SASA_Stats_report/html_report.html
cd $HOME
set -x
(
SQL << EOF
set feedback off
set HEADING OFF
set linesize 5500
set pagesize 20000
set colsep " ; "
select TRIM(CYCLIC),TRIM(JOBNAME),TRIM(APPLIC),TRIM(STATUS),TRIM(STATE),to_char(to_date(trim(cmr_ajf.startrun), 'YYYYMMDDHH24MISS'), 'DD-MM-YYYY HH24:MI:SS')"START TIME",to_char(to_date(trim(cmr_ajf.endrun), 'YYYYMMDDHH24MISS'), 'DD-MM-YYYY HH24:MI:SS')"END TIME",trim(ELAPTIME/100) as ELAPTIME ,trim(ODATE),trim(ORDERNO),trim(MAXWAIT),trim(HOLDFLAG),trim(DESCRIPT),TRIM(APPLGROUP) from cmr_ajf where APPLIC='FDW_SASA' order by ODATE DESC, APPLIC, JOBNAME;
EOF
)| sed '1,11d'|grep -v "SQL>"|grep -v "Partitioning," | grep -v "and Real Application Testing options" > ${Temp_File_Ok}
echo "CYCLIC|JOBNAME|APPLICATION|STATUS|STATE|START_TIME|END_TIME|ELAPSED_TIME|ORDER_DATE|ORDER_ID|AJF_RETENSION|HOLD|DESCRIPTION|SUB_APPLICATION" > ${final}
cat ${Temp_File_Ok} >> ${final}
sed 's/;/,/g' ${final} > ${Temp_File_Ok}
sed 's/, Y  ,/,COMPLETED SUCESSFULLY, /g' ${Temp_File_Ok} > ${finalcsv}
sed 's/, N  ,/,NOT COMPLETED, /g' ${finalcsv} > ${Temp_File_Ok}
sed 's/,  8  ,/,COMPLETED, /g' ${Temp_File_Ok} > ${finalcsv}
sed 's/,  C  ,/,WAIT CONDITION, /g' ${finalcsv} > ${Temp_File_Ok}
sed 's/, 4  ,/,EXECUTING, /g' ${Temp_File_Ok} > ${finalcsv}
sed 's/,  B  ,/,WAIT TIME, /g' ${finalcsv} > ${Temp_File_Ok}
sed 's/,  1  ,/,WAIT USER CONFIRMATION, /g' ${Temp_File_Ok} > ${finalcsv}
sed 's/,  2  ,/,SUBMITTED, /g' ${finalcsv} > ${Temp_File_Ok}
sed 's/,  5  ,/,ENDED, /g' ${Temp_File_Ok} > ${finalcsv}
sed 's/,  7  ,/,DISAPPEARED, /g' ${finalcsv} > ${Temp_File_Ok}
sed 's/,  D  ,/,WAIT RESOURCE, /g' ${Temp_File_Ok} > ${finalcsv}
sed 's/,  6  ,/,ANALYZED, /g' ${finalcsv} > ${Temp_File_Ok}
sed 's/,  0  ,/,WAIT SHELDULING, /g' ${Temp_File_Ok} > ${finalcsv}
sed 's/,  3  ,/,NOT SUBMITTED, /g' ${finalcsv} > ${Temp_File_Ok}
sed 's/,  9  ,/,NOT FOUND, /g' ${Temp_File_Ok} > ${finalcsv}
sed 's/,  A  ,/,WAIT RERUN, /g' ${finalcsv} > ${Temp_File_Ok}
sed 's/,  E  ,/,WAIT SUBMISSION, /g' ${Temp_File_Ok} > ${finalcsv}
sed 's/,  G  ,/,RETRY SUBMIT, /g' ${finalcsv} > ${Temp_File_Ok}
sed 's/,  K  ,/,POST ODAT, /g' ${Temp_File_Ok} > ${finalcsv}
sed 's/,  F  ,/,NOT KNOWN, /g' ${finalcsv} > ${Temp_File_Ok}
sed 's/,  G  ,/,RETRY SUBMIT, /g' ${Temp_File_Ok} > ${finalcsv}
sed 's/,  H  ,/,WAIT GROUP SCHEDULE, /g' ${finalcsv} > ${Temp_File_Ok}
sed 's/,  I  ,/,FAIL SUBMIT, /g' ${Temp_File_Ok} > ${finalcsv}
sed 's/,  J  ,/,WAIT ODAT, /g' ${finalcsv} > ${Temp_File_Ok}
sed 's/,  Z  ,/,UNKNOWN, /g' ${Temp_File_Ok} > ${finalcsv}
sed 's/,NOT COMPLETED,COMPLETED,/,FAILED,COMPLETED, /g' ${finalcsv} > ${Temp_File_Ok}
sed 's/N  ,/NO, /g' ${Temp_File_Ok} > ${finalcsv}
sed 's/Y  ,/YES, /g' ${finalcsv} > ${Temp_File_Ok}
cat ${Temp_File_Ok} | awk -F"," '{print $2,","$3,","$1,","$4,","$5,","$6,","$7,","$8,","$9,","$10,","$11,","$12,","$13,","$14}' > ${finalcsv}
sed 's/,T   ,/,CYCLIC FLAG SET TO ZERO, /g' ${finalcsv} > ${Temp_File_Ok}
sed 's/,NO ,NOT COMPLETED ,/,NO , , /g' ${Temp_File_Ok} > ${finalcsv}
cat ${finalcsv} > ${Temp_File_Ok}
sed 's/, Y/,Yes/g' ${Temp_File_Ok} > ${finalcsv}
sed 's/, N/,No/g' ${finalcsv} > ${Temp_File_Ok}
cat ${Temp_File_Ok} > ${finalcsv}
echo "JOBNAME,APPLICATION,CYCLIC,STATUS,STATE,START_TIME,END_TIME,ELAPSED_TIME,ORDER_DATE,ORDER_ID,AJF_RETENSION,HOLD,DESCRIPTION,SUB_APPLICATION" > ${finalcsv_mail}
tail -n +2 "${finalcsv}" >> ${finalcsv_mail}
x=`cat ${finalcsv} | grep ",Yes" | wc -l`
if [ $x -ne 0 ]; then
cat ${finalcsv} | grep ,Yes | awk -F"," '{print $2,"|"$4,"|"$5,"|"$9}' > ${final}
echo " Please find the attached Report " > $Mail_Body
echo " Number of Jobs on External Hold - $x " >> $Mail_Body
echo " List Of Held Jobs " >> $Mail_Body
echo " JOBNAME | STATUS | STATE  |ORDER_DATE" >> $Mail_Body
cat ${final} >> $Mail_Body
else
echo " Please find the attached Report " > $Mail_Body
echo " No Jobs are on External Hold" >> $Mail_Body
fi
print "<H3> <font color =black> CONTROL-M STATUS REPORT $Date1 </font> </H3>" > ${html_file}
print "<H3> <font color =black> JOBS ON EXTERNAL HOLD - $x </font> </H3>" >> ${html_file}
print "<H3> <font color =black> LIST OF TOTAL JOBS for $Date1 </font> </H3>" >> ${html_file}
printf "<br style="margin-bottom:240px;"/>" >> ${html_file}
echo "JOBNAME,APPLICATION,CYCLIC,STATUS,STATE,START_TIME,END_TIME,ELAPSED_TIME,ORDER_DATE,ORDER_ID,AJF_RETENSION,HOLD,DESCRIPTION,SUB_APPLICATION" > ${Temp_File_Ok}
tail -n +2 "${finalcsv}" >> ${Temp_File_Ok}
awk -F"," '{print $9,","$2,","$1,","$3,","$4,","$5,","$6,","$7,","$8,","$10,","$11,","$12,","$13,","$14}' ${Temp_File_Ok} |sed 's/,/;/g' > ${final}
awk 'BEGIN{
  FS=";"
  cols=14
  print "<HTML><body text=blue><TABLE border=2>"
}
NF==cols{
  if(NR>1)
    print "</font></TD></TR>"
    printf "<tr>"
#   printf "<tr bgcolor=yellow face="Tahoma">"
  printf "<tr font color=#808080>"
  for(i=1;i<NF;i++)
    printf "<TD>%s</font></TD>", $i
  printf "<TD>%s", $NF
}
NF==1{
  printf "\n%s", $0
}
END{
  print "</TD></TR>\n</TABLE></body>"
}
' ${final} >> ${html_file}
sed 's/FAILED/<font color =red> FAILED/' ${html_file} > ${Temp_File_Ok}
sed 's/COMPLETED SUCESSFULLY/<font color =green> COMPLETED SUCESSFULLY/' ${Temp_File_Ok} > ${html_file}
sed 's/EXECUTING/<font color =orange> EXECUTING/' ${html_file} > ${Temp_File_Ok}
sed 's/WAIT CONDITION/<font color =grey> WAIT CONDITION/' ${Temp_File_Ok} > ${html_file}
sed 's/WAIT TIME/<font color =grey> WAIT TIME/' ${html_file} > ${Temp_File_Ok}
sed 's/WAIT RESOURCE/<font color =grey> WAIT RESOURCE/' ${Temp_File_Ok} > ${html_file}
sed 's/WAIT USER CONFIRMATION/<font color =#FE2EC8> WAIT USER CONFIRMATION/' ${html_file} > ${Temp_File_Ok}
cat ${Temp_File_Ok} > ${html_file}
cat ${html_file} > FDW_SASA_PRD_$Date1.html
cat ${finalcsv_mail} | awk -F"," '{print $9,","$2,","$1,","$3,","$4,","$5,","$6,","$7,","$8,","$10,","$11,","$12,","$13,","$14}' > FDW_SASA_PRD_$Date1.csv
#cat $Mail_Body | mailx -s "FDW_SASA_PRD Control M Daily Stats Report_PERF $Date" -a FDW_SASA_PRD_STATUS_DAILY.html -a FDW_SASA_PRD_JOBS_STATUS_DAILY.csv $MAIL
cd $HOME
find $HOME -name "Stats_*.csv" -type f -mtime +4 -exec rm -f {} \;
find $HOME -name "FDW*"  -type f -mtime +4 -exec rm -f {} \;

scp $HOME/FDW_SASA_PRD_$Date1.html $HOME/FDW_SASA_PRD_$Date1.csv finints@ukx10454:/opt/finints/dashboard/
#echo "test" | mail -s "report" -a $HOME/FDW_SASA_PRD_$Date1.html $HOME/FDW_SASA_PRD_$Date1.csv a629112@fil.com

}
FDW_SASA
