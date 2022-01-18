#!/usr/bin/env python3
import os
import sys
import signal
import time


#Set the address of files.
PID_FILE = os.path.expanduser('~/.runner.pid')
STATUS_FILE = os.path.expanduser('~/.runner.status')


#Check the existence of files.
if os.path.exists(PID_FILE) == False:
    sys.stderr.write('file ~/.runner.pid not found')
    sys.exit()
if os.path.exists(STATUS_FILE) == False: 
    sys.stderr.write('file ~/.runner.status not found')
    sys.exit()


#Read the PID_FILE and get pid.
f = open(PID_FILE, 'r')
pid = int(f.readline())
f.close()


#Send signal to runner.py.
try: 
    os.kill(pid, signal.SIGUSR1)
except:
    sys.stderr.write('file ~/.runner.pid bad pid')
    sys.exit()


#Check the size of the STATUS_FILE.
count = 0
while count < 5:
    if os.path.getsize(STATUS_FILE) == 0:
        count += 1 
        time.sleep(1) 
    else : 
        break
if count == 5:
    sys.stderr.write('status timeout')
    sys.exit()


#Read STATUS_FILE and print it.
f = open(STATUS_FILE, 'r')
while True: 
    line = f.readline()
    if not line:
        break
    print(line, end='')
f.close()


#Empty the STATUS_FILE.
f = open(STATUS_FILE, 'w')
f.close()


sys.exit()




