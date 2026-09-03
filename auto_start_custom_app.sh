#/bin/bash

#this script is auto startup

maillist="mani@mani.com"
wdir="/opt/controlm/emservertest/custom_scripts/Auto_start_custom_app"

app1="receiver.py"
wdir1="/opt/controlm/emservertest/custom_scripts/Alert_automation"

app2="myapp.py"
wdir2="mylocacatiop"

#appuser=`whoami` # limitation of username with 8 character only hence using hardcoded in this example
appuser="emserv"

appstatus_fun()  #reusable function
{
 appname=$1
 wdir=$2
 `ps -ef | grep $appname | grep $appuser > $wdir/tempstatus`
  count=`cat $wdir/tempstatus | wc -l`
  cat $wdir/tempstatus
  if [ $count == 1 ]
      then
         python3 $wdir/$appname &
         if [ $? == 0 ]
             then
               echo " app started succesfully "
              else
                  echo "$appname not running on `hostname` , please check " | mailx -s "$appname custom app down " $maillist
             fi
  else
    echo " app is already running no action "
  fi

#  rm -rf $wdir/tempstatus

 }

 appstatus_fun $app1 $wdir1
