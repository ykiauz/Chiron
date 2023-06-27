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

times = 10

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

    cmd = "python3 ../../deploy.py mr-wrap %s" % file_path
    subprocess.check_output(cmd, shell=True).strip()
    time.sleep(5)

def get_lats():
    init()

    for index, method in enumerate(methods):
        lats = []
        if index > 0:
            deploy(index)
            for i in range(times+1):
                data = generate_data()
                res = requests.post(url, data=data).text
                res_j = json.loads(res)
                lats.append((res_j["time"]["workflow"]["end"] - res_j["time"]["workflow"]["start"])*1000)
        else:
            for i in range(times+1):
                data = generate_data()
                lats.append(workflow_OpenFaaS(data))

        print("%s: %f" % (method, sum(lats[1:])/(len(lats)-1)))

    init()

if __name__ == '__main__':
    get_lats()