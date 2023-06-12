#!/bin/sh

PATH="$HOME/bin:$HOME/.local/bin:$PATH"
PATH="/home/refinery03/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin"

PYTHONPATH=""
export PATH=$PATH
export PYTHONPATH=$PYTHONPATH

cd /home/refinery03/Insightzz/code/ARDUINO/
nohup python3 /home/refinery03/Insightzz/code/ARDUINO/arduino_service.py > /dev/null &

