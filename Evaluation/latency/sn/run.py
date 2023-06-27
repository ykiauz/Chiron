import requests
import threading
import random
import string
import json
import time
import subprocess

from OpenFaaS import workflow_OpenFaaS

url = "http://127.0.0.1:31112/function/sn-wrap"

methods = ["OpenFaaS", "SAND", "Faastlane", "Chiron", "Faastlane-P", "Chiron-P", "Faastlane-M", "Chiron-M"]

times = 10

def gen_random_string(i):
    choices = string.ascii_letters + string.digits
    return "".join([choices[random.randint(0, len(choices)-1)] for j in range(i)])

def generate_data():
    user_index = random.randint(1, 1000)
    
    num_user_mentions = random.randint(1, 5)
    num_urls = random.randint(1, 5)
    num_media = random.randint(1, 4)
    text = ""
    
    user_mentions = []
    for i in range(num_user_mentions):
        while True:
            user_mention_id = random.randint(1, 1000)
            if user_mention_id != user_index and user_mention_id not in user_mentions:
                user_mentions.append(user_mention_id)
                break
    
    text += " ".join(["@username_"+str(i) for i in user_mentions])
    text += " "
    
    for i in range(num_urls):
        text += ("http://"+gen_random_string(64)+" ")
    
    media_ids = []
    media_types = ["png"] * num_media
    for i in range(num_media):
        media_ids.append(gen_random_string(5))
    
    data = {
        "username": "username_" + str(user_index),
        "user_id": user_index,
        "post_type": 0,
        "text": text,
        "media_ids": ",".join(media_ids),
        "media_types": ",".join(media_types)
    }

    return json.dumps(data)

def init(not_mpk=True):
    if not_mpk:
        cmd = "faas-cli deploy -f sn-wrap.yml"
    else:
        cmd = "faas-cli deploy -f sn-wrap-mpk.yml"
    subprocess.check_output(cmd, shell=True).strip()
    time.sleep(5)

def deploy(index):
    file_path = f"wraps/{methods[index]}.py"

    if index == 6:
        init(False)

    cmd = "python3 ../../deploy.py sn-wrap %s" % file_path
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