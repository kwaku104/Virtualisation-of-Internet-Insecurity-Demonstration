#!/bin/bash

echo "Killing any existing rogue AS"

python3 run.py --cmd "pgrep -f [z]ebra | xargs kill -9"
python3 run.py --cmd "pgrep -f [b]gpd | xargs kill -9"

