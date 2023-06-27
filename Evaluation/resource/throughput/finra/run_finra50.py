import requests
import threading
import random
import string
import json
import time
import subprocess

from OpenFaaS import workflow_OpenFaaS

url = "http://127.0.0.1:31112/function/finra-wrap"
data = '{"body":{ "portfolioType":"S&P", "portfolio":"1234"}}'

methods = ["OpenFaaS", "SAND", "Faastlane", "Chiron", "Faastlane-P", "Chiron-P", "Faastlane-M", "Chiron-M"]
num_wraps = [0, 1, 1, 1, 1, 1, 1, 6]

CPUs =  [51,  50,  50,   6,  50,  11, 50,  6]

times = 10

th_time = 10

TIME_FLAG = True

def timer():
    global TIME_FLAG
    time.sleep(th_time)
    TIME_FLAG = False

def init(not_mpk=True):
    if not_mpk:
        cmd = "faas-cli deploy -f finra-wrap.yml"
    else:
        cmd = "faas-cli deploy -f finra-wrap-mpk-50.yml"
    subprocess.check_output(cmd, shell=True).strip()
    time.sleep(5)

def deploy(index):
    if index == 6:
        init(False)

    num_wrap = num_wraps[index]
    for i in range(1, num_wrap + 1):
        file_path = f"wraps/{methods[index]}-50-wrap{i}.py"
        if i == 1:
            cmd = "python3 ../../../deploy.py finra-wrap %s" % file_path
        else:
            cmd = "python3 ../../../deploy.py finra-wrap%d %s" % (i, file_path)
        subprocess.check_output(cmd, shell=True).strip()
    time.sleep(5)

def get_ths():
    global TIME_FLAG
    init()

    for index, method in enumerate(methods):
        if index > 0:
            deploy(index)

        count = 0
        timer_th = threading.Thread(target=timer)
        timer_th.start()

        while TIME_FLAG:
            if index > 0:
                res = requests.post(url, data=data).text
            else:
                res = workflow_OpenFaaS(data, 10)
            count += 1

        timer_th.join()

        print("%s: %.2f reqs in 1s with %d CPUs" % (method, count * 1.0 / th_time, CPUs[index]))

        TIME_FLAG = True

    init()

if __name__ == '__main__':
    get_ths()