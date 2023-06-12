#!/bin/sh

PATH="$HOME/bin:$HOME/.local/bin:$PATH"
PATH="/opt/spinnaker/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/snap/bin"

PYTHONPATH=""
export PATH=$PATH
export PYTHONPATH=$PYTHONPATH

cd /home/rfserver/insightzz/CSM2/code/FRAME_CAPTURE/
# nohup python3 mvrecordobj_v17_all_cams2.py > /dev/null &
# pkill -9 startFrameScript_CSM2.sh
