#!/bin/sh

PATH="$HOME/bin:$HOME/.local/bin:$PATH"
PATH="/opt/spinnaker/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/snap/bin"

PYTHONPATH=""
export PATH=$PATH
export PYTHONPATH=$PYTHONPATH

cd /home/rfserver/insightzz/CSM2/code/FRAME_CAPTURE
nohup python3 /home/rfserver/insightzz/CSM2/code/FRAME_CAPTURE/killRawFrame.py > /dev/null &
pkill -9 killFrameScript_CSM1.sh

sleep 2

cd /home/rfserver/insightzz/CSM2/code/FRAME_CAPTURE/BackUp/
nohup python3 mvrecordobj_v17_all_saveVideo.py > /dev/null &
pkill -9 restartrawFrame.sh

