#!/bin/sh

ssh -i ~/.ssh/id_rsa rfserver@169.254.0.31 "/home/rfserver/insightzz/CSM2/code/HEALTH_MONITORING/kill_health_script.sh" &
ssh -i ~/.ssh/id_rsa rfserver@169.254.0.31 "/home/rfserver/insightzz/CSM2/code/SHELL_SCRIPT/killPlcCode.sh" &
pkill -9 kill_health_script.sh
