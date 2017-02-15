#!/usr/bin/env python
import os
import subprocess
import logging
import sys
import re
import time
import datetime

SPEEDTEST_CMD = 'C:\Anaconda2\Lib\site-packages\speedtest_cli.py'
sleepTime = 1500
if len(sys.argv) < 2:
    logFolder = raw_input('Please enter the folder that you would like to save the speedtest.log file in\n')
    sleepTime = int(raw_input("How many seconds would you like the program to wait befor running again?\n"))
else:
    logFolder = sys.argv[1]
LOG_FILE = str(logFolder) + '\Log Files\speedtest.log'
print LOG_FILE
if not os.path.exists(LOG_FILE):
    os.makedirs(logFolder + '\Log Files')
def main():
    while True:
        setup_logging()
        computerName = os.environ['COMPUTERNAME']
        try:
            ISP, ping, download, upload = get_speedtest_results()
        except ValueError as err:
            logging.info("%s %s", computerName, err)
            next
        else:
            logging.info("%s %s %s %s %s", ISP, computerName, ping, download, upload)
        time.sleep(sleepTime)

def setup_logging():
    logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    datefmt="%Y-%m-%d %H:%M",
)

def get_speedtest_results():
    ISP = ping = download = upload = None
    speedtest_output = subprocess.check_output('python ' + SPEEDTEST_CMD)
    #with subprocess.check_output('python ' + SPEEDTEST_CMD + ' --simple') as speedtest_output:
    #print speedtest_output
    #print len(speedtest_output)
    speedtest_output_clean = speedtest_output.split('\n')
    #print(speedtest_output_clean)
    for line in speedtest_output_clean:
        lineSplit = line.split()
        # print lineSplit
        try:
            if 'Hosted' in lineSplit:
                for i in lineSplit[0:]:
                    if ping == None:
                        if find_Ping_Regex(i) == None:
                            next
                        else:
                            ping = find_Ping_Regex(i)
            elif 'Download:' in lineSplit:
                label, value, unit = line.split()
                download = str(value)
            elif 'Upload:' in lineSplit:
                label, value, unit = line.split()
                upload = str(value)
            elif 'from' in lineSplit:
                for i in lineSplit[0:]:
                    if ISP == None:
                        if find_IP_Regex(i) == None:
                            next
                        else:
                            ISP = find_IP_Regex(i)
        except:
            next
    #print(ISP, ping, download, upload)
    if all((ISP, ping, download, upload)): # if all values were parsed
        print (str(datetime.datetime.now()), ISP, ping, download, upload)
        return ISP, ping, download, upload
    else:
        raise ValueError('TEST FAILED')

def find_IP_Regex(txt):
    re1='(\\d+)'	# Integer Number 1
    re2='(.)'	# Any Single Character 1
    re3='(\\d+)'	# Integer Number 2
    re4='(.)'	# Any Single Character 2
    re5='(\\d+)'	# Integer Number 3
    re6='(.)'	# Any Single Character 3
    re7='(\\d+)'	# Integer Number 4

    rg = re.compile(re1+re2+re3+re4+re5+re6+re7,re.IGNORECASE|re.DOTALL)
    m = rg.search(txt)
    if m:
        int1=m.group(1)
        c1=m.group(2)
        int2=m.group(3)
        c2=m.group(4)
        int3=m.group(5)
        c3=m.group(6)
        int4=m.group(7)
        return (str(int1) + str(c1) + str(int2) + str(c2) + str(int3) + str(c3) + str(int4))
    else:
        return None

def find_Ping_Regex(txt):
    re1='(\\d{2})'	# Integer Number 1
    re2='(.)'	# Any Single Character 1
    re3='(\\d{3})'	# Integer Number 2

    rg = re.compile(re1+re2+re3,re.IGNORECASE|re.DOTALL)
    m = rg.search(txt)
    if m:
        int1=m.group(1)
        c1=m.group(2)
        int2=m.group(3)
        return (str(int1) + str(c1) + str(int2))
    else:
        return None

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        next 
