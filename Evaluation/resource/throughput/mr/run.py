import requests
import threading
import random
import string
import json
import time
import subprocess

from OpenFaaS import workflow_OpenFaaS

url = "http://127.0.0.1:31112/function/mr-wrap"

methods = ["OpenFaaS", "SAND", "Faastlane", "Chiron", "Faastlane-P", "Chiron-P", "Faastlane-M", "Chiron-M"]

CPUs =        [9,   4,   4,   1,   4,   2,  4,  2]

times = 10

th_time = 10

TIME_FLAG = True

def timer():
    global TIME_FLAG
    time.sleep(th_time)
    TIME_FLAG = False

def gen_random_string(i):
    choices = string.ascii_letters + string.digits
    return "".join([choices[random.randint(0, len(choices)-1)] for j in range(i)])

movie_titles = []
with open("movie_titles.csv", "r") as f:
    movie_titles = f.readlines()

def generate_data():
    user_index = str(random.randint(1, 1000))
    review = {
        "username": "username_" + user_index,
        "password": "password_" + user_index,
        "title": movie_titles[random.randint(0, len(movie_titles)-1)].strip(),
        "rating": random.randint(0, 10),
        "text": gen_random_string(256) 
    }

    return json.dumps(review)

def init(not_mpk=True):
    if not_mpk:
        cmd = "faas-cli deploy -f mr-wrap.yml"
    else:
        cmd = "faas-cli deploy -f mr-wrap-mpk.yml"
    subprocess.check_output(cmd, shell=True).strip()
    time.sleep(5)

def deploy(index):
    file_path = f"wraps/{methods[index]}.py"

    if index == 6:
        init(False)

    cmd = "python3 ../../../deploy.py mr-wrap %s" % file_path
    subprocess.check_output(cmd, shell=True).strip()
    time.sleep(5)

def get_ths():
    global TIME_FLAG
    init()

    for index, method in enumerate(methods):
        if index > 0:
            deploy(index)

        n = 100
        reqs = []
        for i in range(n):
            reqs.append(generate_data())

        count = 0
        timer_th = threading.Thread(target=timer)
        timer_th.start()

        while TIME_FLAG:
            if index > 0:
                res = requests.post(url, data=reqs[index % n]).text
            else:
                res = workflow_OpenFaaS(reqs[index % n])
            count += 1

        timer_th.join()

        print("%s: %.2f reqs in 1s with %d CPUs" % (method, count * 1.0 / th_time, CPUs[index]))

        TIME_FLAG = True

    init()

if __name__ == '__main__':
    get_ths()