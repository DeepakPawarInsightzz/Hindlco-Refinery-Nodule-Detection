#!/bin/sh

ssh -i ~/.ssh/id_rsa rfserver@169.254.0.31 "/home/rfserver/insightzz/CSM2/code/SHELL_SCRIPT/killFrameScript_CSM2.sh" &
ssh -i ~/.ssh/id_rsa rfserver@169.254.0.31 "/home/rfserver/insightzz/CSM2/code/SHELL_SCRIPT/killDetectionScript_CSM2.sh" &
pkill -9 kill_script.sh
