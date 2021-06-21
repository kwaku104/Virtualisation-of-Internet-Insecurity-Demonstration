#!/bin/bash

./stop_rogue.sh

echo "Starting rogue AS"
python3 run.py --cmd "/usr/lib/quagga/zebra -f conf/zebra-R8.conf -d -i /tmp/zebra-R8.pid > logs/R8-zebra-stdout"
python3 run.py --cmd "/usr/lib/quagga/bgpd -f conf/bgpd-R8.conf -d -i /tmp/bgpd-R8.pid > logs/R8-bgpd-stdout"