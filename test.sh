#!/bin/bash

echo every Friday at 1457 run /bin/echo Hi > ~/.runner.conf

python3 ./runner.py > outputfile &
sleep 2 
python3 ./runstatus.py | diff - status_1
sleep 60
python3 ./runstatus.py | diff - status_2 
diff outputfile output_1
kill -9 `ps -aux |grep "python3 ./runner.py" |head -1| awk {'print $2'}`
