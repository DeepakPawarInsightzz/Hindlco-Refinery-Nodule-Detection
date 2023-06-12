#!/bin/sh

PATH="$HOME/bin:$HOME/.local/bin:$PATH"
PATH="/opt/spinnaker/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/snap/bin"

PYTHONPATH=""
export PATH=$PATH
export PYTHONPATH=$PYTHONPATH

cd /home/rfserver/insightzz/CSM2/code/DETECTION/
nohup python3 /home/rfserver/insightzz/CSM2/code/DETECTION/detection2_cam1_V3.py > /dev/null &
nohup python3 /home/rfserver/insightzz/CSM2/code/DETECTION/detection2_cam2_V3.py > /dev/null &
nohup python3 detection2_cam3_V3.py > /dev/null &
pkill -9 startDetectionScript_CSM2.sh
