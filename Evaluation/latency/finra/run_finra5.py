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

times = 10

def init(not_mpk=True):
    if not_mpk:
        cmd = "faas-cli deploy -f finra-wrap.yml"
    else:
        cmd = "faas-cli deploy -f finra-wrap-mpk.yml"
    subprocess.check_output(cmd, shell=True).strip()
    time.sleep(5)

def deploy(index):
    file_path = f"wraps/{methods[index]}.py"

    if index == 6:
        init(False)

    cmd = "python3 ../../deploy.py finra-wrap %s" % file_path
    subprocess.check_output(cmd, shell=True).strip()
    time.sleep(5)

def get_lats():
    init()

    for index, method in enumerate(methods):
        lats = []
        if index > 0:
            deploy(index)
            for i in range(times+1):
                res = requests.post(url, data=data).text
                res_j = json.loads(res)
                lats.append((res_j["time"]["workflow"]["end"] - res_j["time"]["workflow"]["start"])*1000)
        else:
            for i in range(times+1):
                lats.append(workflow_OpenFaaS(data, 1))

        print("%s: %f" % (method, sum(lats[1:])/(len(lats)-1)))

    init()

if __name__ == '__main__':
    get_lats()