#!/bin/csh

logdir="/controlm/ctmemprd/customscripts/Break_glass_access"
id_dir="/controlm/ctmemprd/customscripts/Break_glass_access/session_id"
temp_file="/controlm/ctmemprd/customscripts/Break_glass_access/temp_access_files"

em ctl -pf $logdir/.empf -C GUI_Server -M `hostname` -cmdstr PGUI | grep -i $1 | awk '{print $1}' > $id_dir/session_$1.txt

for user in $(cat $id_dir/session_$1.txt)
do
em ctl -pf $logdir/.empf -C GUI_Server -M `hostname` -cmdstr "KICK $user" -timeout 120
done

if [ $? == 0 ]
then
 echo " session killed ok "
else
 echo " user $user not kiced"
fi

find $id_dir -name "*" -type f -mtime +15 -print0 | xargs -0 rm -rf ; date # deleting temp session files

find $temp_file -name "*" -type -f -mtime +1 -print0 | xargs -0 rm -rf ; date #deleting temp useraccess files after 1 day
