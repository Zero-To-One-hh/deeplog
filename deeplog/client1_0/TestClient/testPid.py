# -*- coding: utf-8 -*-
import requests

def get_service_pid():
    try:
        response = requests.get("http://127.0.0.1:8000/pid")
        if response.status_code == 200:
            print("Service PID:", response.json()["data"])
        else:
            print("Failed to retrieve PID.")
    except requests.ConnectionError:
        print("Unable to connect to the service.")

# get_service_pid()


def get_config():
    try:
        response = requests.get("http://127.0.0.1:8000/bj/config")
        if response.status_code == 200:
            print("配置信息:", response.json()["data"])
        else:
            print("Failed to retrieve config.")
    except requests.ConnectionError:
        print("Unable to connect to the service.")

# get_config()

def reappraise():
    try:
        response = requests.get("http://127.0.0.1:8000/bj/reappraise")
        if response.status_code == 200:
            print("重新评估:", response.json()["message"])
    except requests.ConnectionError:
        print("Unable to connect to the service.")

# reappraise()

def sendScore():
    try:
        response = requests.get("http://127.0.0.1:8000/bj/sendScore")
        if response.status_code == 200:
            print("发送评估结果:", response.json()["message"])
    except requests.ConnectionError:
        print("Unable to connect to the service.")

# sendScore()

def startSample():
    try:
        response = requests.get("http://127.0.0.1:8000/bj/startcollect")
        print("code:",response.status_code)
        print("启动结果:", response.json()["message"])
        print("code:", response.json()["code"])
    except requests.ConnectionError:
        print("Unable to connect to the service.")



def stopSample():
    try:
        response = requests.get("http://127.0.0.1:8000/bj/stopcollect")

        print("停止结果:", response.json()["message"])
    except requests.ConnectionError:
        print("Unable to connect to the service.")
get_service_pid()
# startSample()
stopSample()
