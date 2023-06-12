#!/bin/sh

ssh -i ~/.ssh/id_rsa rfserver@169.254.0.31 "/home/rfserver/insightzz/CSM2/code/HEALTH_MONITORING/check_lan_health.sh" &
ssh -i ~/.ssh/id_rsa rfserver@169.254.0.31 "/home/rfserver/insightzz/CSM2/code/SHELL_SCRIPT/startPlcCode.sh" &
pkill -9 start_health_script.sh
