#!/bin/bash
# para ejecutarlo desde el crontab
# un chmod 755 crontab-5m.sh
# */5 * * * * root /home/tortuga/crypto/prices/tradebot/bitmex/bitmex-python/crontab-5m.sh

FECHA=`/bin/date +%s` 
sleep 20
ANS=$(( FECHA / 60 ))
FECHA=$(( ANS * 60 ))
/usr/bin/python3.4 /home/tortuga/crypto/prices/tradebot/bitmex/bitmex-python/getdata-5m.py $FECHA 
#/usr/bin/python3.5 /usr/src/wolfbot-python/getdata-5m.py $FECHA 


