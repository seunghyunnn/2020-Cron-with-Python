#!/usr/bin/env python3
import os
import sys
import signal
import time
import datetime


#Set addresses of files.
PID_FILE = os.path.expanduser('~/.runner.pid')
STATUS_FILE = os.path.expanduser('~/.runner.status')
CONFIG_FILE = os.path.expanduser('~/.runner.conf')


#Create/Write PID_FILE.
try:
    pid = os.getpid()
    f = open(PID_FILE, 'w')
    f.write(str(pid))
    f.close()
except FileNotFoundError:
    sys.stderr.write('file /.runner.pid not found')
    sys.exit()


#Create STATUS_FILE.
try: 
    f = open(STATUS_FILE, 'w')
    f.close()
except FileNotFoundError:
    sys.stderr.write('file /.runner.status not found')
    sys.exit()


#Check the CONFIG_FILE.
config_ls = []
try: 
    f = open(CONFIG_FILE, 'r')
    config_ls = f.readlines()
    f.close()
except FileNotFoundError:
    sys.stderr.write('configuration file not found')
    sys.exit()


#Check the emptiness CONFIG_FILE.
if os.path.getsize(CONFIG_FILE) == 0:
    sys.stderr.write('configuration file empty')
    sys.exit()
if len(config_ls) == 1 and config_ls[0].strip() == "":
    sys.stderr.write('configuration file empty')
    sys.exit()


#Parse the CONFIG_FILE and build run_at: list of programs.
days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
run_at = []
for i in range(len(config_ls)):
    ls = config_ls[i].rstrip().split() 
    parsed_dic = {'every':'','day':'','hour':-1, 'min':-1,'prog':'',\
                'params':[],'date':'', 'conf_loc':i}
    if len(ls) == 0:#empty line
        sys.stderr.write('error in configuration: ' + config_ls[i])
        sys.exit()
        
    #Set 'every', 'prog, 'params' of parsed_dic.
    if ls[0] == 'every' or ls[0] == 'on':
        if len(ls) < 6: #not enough element
            sys.stderr.write('error in configuration: ' + config_ls[i])
            sys.exit()

        if not(ls[2] == 'at' and ls[4] == 'run'): #incorrect/missing keywords
            sys.stderr.write('error in configuration: ' + config_ls[i])
            sys.exit()

        parsed_dic['every'] = ls[0]
        parsed_dic['prog'] = ls[5]
        parsed_dic['params'] = [ls[5].split('/')[-1]] + ls[6:] 
        temp_day = ls[1].split(',')
        temp_time = ls[3].split(',')  
    
    elif ls[0] =='at':
        if len(ls) < 4: #not enough element
            sys.stderr.write('error in configuration: ' + config_ls[i])
            sys.exit()

        if not(ls[2] =='run'): #incorrect/missing keywords
            sys.stderr.write('error in configuration: ' + config_ls[i])
            sys.exit() 

        parsed_dic['every'] = 'at'
        parsed_dic['prog'] = ls[3]
        parsed_dic['params'] = [ls[3].split('/')[-1]] + ls[4:]
        temp_day = [days[time.localtime().tm_wday]] #temporarily set current day
        temp_time = ls[1].split(',')  

    else:
        sys.stderr.write('error in configuration: ' + config_ls[i])
        sys.exit() 

   
    if not(parsed_dic['prog'][0] == '/'): #check progs format
        sys.stderr.write('error in configuration: ' + config_ls[i])
        sys.exit() 
    
    #Set 'day','hour', 'min of parsed_dic and append it to run_at list.
    for k in temp_day: #check day
        if k not in days:
            sys.stderr.write('error in configuration: ' + config_ls[i])
            sys.exit() 
       
    for k in temp_time:  #check time
        if not(len(k) == 4): 
            sys.stderr.write('error in configuration: ' + config_ls[i])
            sys.exit()
        try:
            hr = int(k[0:2])
            mi = int(k[2:])
        except: 
            sys.stderr.write('error in configuration: ' + config_ls[i])
            sys.exit()

        if (hr < 0) or (hr > 23) or (mi < 0) or (mi > 59):
            sys.stderr.write('error in configuration: ' + config_ls[i])
            sys.exit()

    for k in range(len(temp_day)):
        for t in range(len(temp_time)):
            run_at.append(dict(parsed_dic))
            run_at[-1]['day'] = temp_day[k]
            run_at[-1]['hour'] =int(temp_time[t][0:2])
            run_at[-1]['min'] = int(temp_time[t][2:])


#Adjust 'day' and 'date' of dictionaries in run_at.
now = time.localtime()
dnow = datetime.datetime(*now[:6])
for i in range(len(run_at)):
    run_at[i]['date'] = dnow.replace(hour=run_at[i]['hour'],\
                        minute=run_at[i]['min'], second=0)

    if run_at[i]['every'] != 'at': #adjusting the day in run_at
        delta = -1
        if now.tm_wday <= days.index(run_at[i]['day']):
            delta = days.index(run_at[i]['day']) - now.tm_wday
        else:
            delta = days.index(run_at[i]['day']) + 7 - now.tm_wday
        run_at[i]['date'] += datetime.timedelta(days=delta)

    if time.mktime(run_at[i]['date'].utctimetuple()) < time.mktime(now):#adjusting the 
                                                                        #date in run_at
        if run_at[i]['every'] == 'at':
            run_at[i]['date'] += datetime.timedelta(days = 1)
            run_at[i]['day'] = days[days.index(run_at[i]['day']) + 1]
        else:
            run_at[i]['date'] += datetime.timedelta(days=7)

    run_at[i]['date'] = time.localtime(time.mktime(run_at[i]['date'].utctimetuple()))


#Check duplicate time.
for i in range(len(run_at)):
    for k in range(i+1,len(run_at)):
        if (run_at[i]['day'] == run_at[k]['day'])\
            and (run_at[i]['hour'] == run_at[k]['hour'])\
            and (run_at[i]['min'] == run_at[k]['min']):
            if run_at[i]['conf_loc'] > run_at[k]['conf_loc']:
                sys.stderr.write('error in configuration: '\
                                  +config_ls[run_at[i]['conf_loc']])
                sys.exit()
            else:
                sys.stderr.write('error in configuration: '\
                                 +config_ls[run_at[k]['conf_loc']])
                sys.exit()


#Sort function for run_at by date.
def keyfunc(e):
    return time.mktime(e['date'])

#Sort run_at. 
run_at.sort(key = keyfunc)

#Sort function for status_log.
def keyfunc2(e):
    return time.mktime(time.strptime(e['time']))

#Write initial status_log.
status_log = []
for i in range(len(run_at)):
    temp_dict = {'status':'will run at',\
                'time':time.ctime(time.mktime(run_at[i]['date'])),\
                'prog':run_at[i]['prog'], 'params':run_at[i]['params']}
    status_log.append(dict(temp_dict))


caught = False
#Catch signal and write status file.
def catch(signum, frame):
    global caught
    caught = True
    f = open(STATUS_FILE, 'w')
    for i in range(len(status_log)):
        temp = status_log[i]['status'] + ' ' + status_log[i]['time']\
                              + ' ' + status_log[i]['prog']
        k=1
        while k < len(status_log[i]['params']):
            temp = temp + ' ' + status_log[i]['params'][k]
            k = k + 1
        f.write(temp + '\n')
    f.close()

signal.signal(signal.SIGUSR1, catch)


#Execute the programs, and sort the run_at list again.
count = -1
while True:
    count = count + 1
    if len(run_at) == 0:
        sys.stderr.write('nothing left to run')
        sys.exit()

    running = run_at.pop(0)
    sleep_time = time.mktime(running['date'])-time.mktime(time.localtime())
    time.sleep(sleep_time)
    while caught : 
        caught = False
        if time.mktime(running['date']) > time.mktime(time.localtime()):
            time.sleep(time.mktime(running['date'])-time.mktime(time.localtime()))


    try:
        d_pid = os.fork()
    except:
        status_loc[count]['status'] = 'error'

    if d_pid == -1:
        status_log[count]['status'] = 'error'
    elif d_pid == 0:
        try:
            os.execv(running['prog'], running['params'])
        except: 
            sys.exit(1)
    else:
        check = os.wait()
        if check[1] != 0:
            status_log[count]['status'] = 'error'
        else:
            status_log[count]['status'] = 'ran'


    if running['every'] == 'every':
                temp_date = datetime.datetime(*running['date'][:6])\
                            + datetime.timedelta(days=7)
                running['date'] =  time.localtime(time.mktime(temp_date.utctimetuple()))
                run_at.append(running)
                run_at.sort(key=keyfunc)
                status_log.append(dict({'status':'will run at',\
                                        'time':time.ctime(time.mktime(running['date'])),\
                                        'prog':running['prog'],\
                                        'params':running['params']}))
                status_log.sort(key=keyfunc2)

