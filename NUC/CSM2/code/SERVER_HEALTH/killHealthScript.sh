#!/bin/sh

PATH="$HOME/bin:$HOME/.local/bin:$PATH"
PATH="/home/nuc-ctrl/.local/bin:/opt/spinnaker/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin"

PYTHONPATH=""
export PATH=$PATH
export PYTHONPATH=$PYTHONPATH

cd /home/nuc-ctrl/insightzz/code/SERVER_HEALTH/
nohup python3 killHealthScript.py > /dev/null &
pkill -9 killHealthScript.sh
