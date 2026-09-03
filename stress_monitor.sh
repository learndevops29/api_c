#!/bin/sh
#set -x

# updated email warning message for team 11/07/2019 - Chandramani

TS=$(date '+%Y%m%d %H:%M:%S')
LOG="/controlm/ctmsvprd/custom_scripts/monitor_log/control_m_health.out"
STRESS_LOG="/controlm/ctmsvprd/custom_scripts/monitor_log/stress.log"
maillist="FIL-EnterpriseScheduling@fil.com"
grep -ih "Stress" /controlm/ctmsvprd/ctm_server/proclog/CE*_0.log |tail -n2 > $STRESS_LOG

DUE2_RECORD=$(grep "Due to stress" $STRESS_LOG |tail -n1)
GONE_RECORD=$(grep "Stress is gone" $STRESS_LOG |tail -n1)

DUE2_TIMESTAMP=$(echo "${DUE2_RECORD}" | awk -F',' '{ print $1 }')
GONE_TIMESTAMP=$(echo "${GONE_RECORD}" | awk -F',' '{ print $1 }')

DUE2_TIME=$(echo ${DUE2_TIMESTAMP} | awk -F_ '{print $2}' | awk -F. '{print $1}')
GONE_TIME=$(echo ${GONE_TIMESTAMP} | awk -F_ '{print $2}' | awk -F. '{print $1}')

START_TIME=$(date -u -d "${DUE2_TIME}" +"%s")
FINAL_TIME=$(date -u -d "${GONE_TIME}" +"%s")

CURRENT_TIME=$(date -u -d "$(date '+%H:%M:%S')" +"%s")
INTERVAL=$(( ${FINAL_TIME} - ${START_TIME} ))
LAST_UPDATE_INTERVAL=$(( ${CURRENT_TIME} - ${FINAL_TIME} ))

if [ ${INTERVAL} -ge 0 ]; then
   if [ ${LAST_UPDATE_INTERVAL} -lt 360 -a ${LAST_UPDATE_INTERVAL} -gt 0 ]; then
        if [ ${INTERVAL} -gt 300 ]; then
            echo "$TS Warning: control-m is under stress, stress detected from ${DUE2_TIME} to ${GONE_TIME}, last for ${INTERVAL} seconds." >> $LOG
            echo "$TS Warning: control-m is under stress, stress detected from ${DUE2_TIME} to ${GONE_TIME}, last for ${INTERVAL} seconds." | mailx -a $STRESS_LOG -s "Warning: control-m is under stress started at ${DUE2_TIME}" $maillist
        else
                        echo "$TS Info: Stress started from ${DUE2_TIME} to ${GONE_TIME}, last less than 5mins" >> $LOG
        fi
    else
        echo "$TS Info: Stress not found in last 5mins." >> $LOG
    fi
else
       if [ $(( ${CURRENT_TIME} - ${START_TIME} )) -gt 300 ]; then
            echo  "$TS Warning: control-m is under stress, stress start from ${DUE2_TIME} and not gone now." >> $LOG
            echo  "$TS Warning: control-m is under stress, stress start from ${DUE2_TIME} and not gone now." | mailx -a $STRESS_LOG -s "Warning: control-m is under stress started at ${DUE2_TIME}" $maillist
        else
                        echo "$TS Info: Stress started from ${DUE2_TIME} and gone now." >> $LOG
                fi
fi
