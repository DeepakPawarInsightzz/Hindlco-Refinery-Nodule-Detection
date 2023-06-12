#!/bin/sh

PATH="$HOME/bin:$HOME/.local/bin:$PATH"
PATH="/opt/spinnaker/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/snap/bin"

PYTHONPATH=""
export PATH=$PATH
export PYTHONPATH=$PYTHONPATH

cd /home/rfserver/insightzz/CSM2/code/PLC/
nohup python3 killlightplc.py > /dev/null &
pkill -9 killlightplc.sh
