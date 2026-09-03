#/bin/bash
LOG_FILE=/opt/controlm/emservertest/custom_scripts/Alert_automation/log/alarm_log_`date '+%Y-%m-%d'`.txt

logdir="/opt/controlm/emservertest/custom_scripts"
params=$@

call_type=${2}
alert_id=${4}
data_center=${6}
memname=${8}
order_id=${10}
severity=${12}
status=${14}
send_time=${16}
last_user=${18}
last_time=${20}
message=${22}
run_as=${24}
sub_application=${26}
application=${28}
job_name=${30}
host_id=${32}
alert_type=${34}
closed_from_em=${36}
ticket_number=${38}
run_counter=${40}

body="{\"call_type\":\"${call_type:=''}\" ,
       \"alert_id\":\"${alert_id:=''}\" ,
       \"data_center\":\"${data_center:=''}\" ,
       \"memname\":\"${memname:=''}\" ,
       \"order_id\":\"${order_id:=''}\" ,
       \"severity\":\"${severity:=''}\" ,
       \"status\":\"${status:=''}\" ,
       \"send_time\":\"${send_time:=''}\" ,
       \"last_user\":\"${last_user:=''}\" ,
       \"last_time\":\"${last_time:=''}\" ,
       \"message\":\"${message:=''}\" ,
       \"run_as\":\"${run_as:=''}\" ,
       \"sub_application\":\"${sub_application:=''}\" ,
       \"application\":\"${application:=''}\" ,
       \"job_name\":\"${job_name:=''}\" ,
       \"host_id\":\"${host_id:=''}\" ,
       \"alert_type\":\"${alert_type:=''}\" ,
       \"closed_from_em\":\"${closed_from_em:=''}\" ,
       \"ticket_number\":\"${ticket_number:=''}\" ,
       \"run_counter\":\"${run_counter:=''}\"}"




curl -k -X POST 'https://manitest.controlm.com:8445/alert' --header 'Content-Type: application/json' --data "${body}" >> $LOG_FILE
#curl --cacert ctmtest.pem -i -X POST -sSo >(echo "${alert_id}:: `echo ${body} | tr '\n' ' ' `:: " `cat` >> $LOG_FILE) --header 'Content-Type: application/json' --data "${body} 'https://manitest.controlm.com:8445/alert'