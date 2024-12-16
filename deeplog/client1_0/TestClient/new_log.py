# -*- coding: utf-8 -*-
import json
import os
import threading
import time

import requests
from flask import Flask, jsonify
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

log_file = "../result/output_log.txt"
log_file = os.path.abspath(log_file)
API_URL = "http://localhost:8000/deviceTrustLevelModel"  # The API endpoint to send requests to

# Flask 服务
app = Flask(__name__)

class LogHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_position = 0

    def on_modified(self, event):
        if not event.is_directory and os.path.abspath(event.src_path) == log_file:
            with open(log_file, "r") as file:
                file.seek(self.last_position)
                new_entries = file.readlines()
                self.last_position = file.tell()

                for entry in new_entries:
                    entry = entry.strip()
                    if not entry:
                        continue
                    try:
                        log_data = json.loads(entry)
                        data = {
                            "time_local": log_data.get("time_local", ""),
                            "remote_addr": log_data.get("remote_addr", ""),
                            "remote_user": log_data.get("remote_user", ""),
                            "request": log_data.get("request", ""),
                            "status": log_data.get("status", ""),
                            "body_bytes_sent": log_data.get("body_bytes_sent", ""),
                            "http_referer": log_data.get("http_referer", ""),
                            "http_user_agent": log_data.get("http_user_agent", ""),
                            "http_x_forwarded_for": log_data.get("http_x_forwarded_for", "")
                        }
                        response = requests.post(API_URL, json=data)
                        if response.status_code == 200:
                            print("Request successful.")
                        else:
                            print(f"Request failed with status code {response.status_code}: {response.text}")

                    except json.JSONDecodeError:
                        print(f"Failed to parse log entry as JSON: {entry}")
                    except Exception as e:
                        print(f"An error occurred: {e}")

class LogCollector:
    def __init__(self):
        self.observer = None  # 初始时为 None
        self.event_handler = LogHandler()
        self.is_running = False  # 初始时为 False

    def start(self):
        if not self.is_running:
            self.observer = Observer()  # 每次启动时创建新的 observer 实例
            self.observer.schedule(self.event_handler, path=os.path.dirname(log_file), recursive=False)
            self.observer.start()
            self.is_running = True
            print("日志采集器已启动。")
        else:
            print("日志采集器已经在运行中。")

    def stop(self):
        if self.is_running:
            self.observer.stop()
            self.observer.join()  # 等待线程停止
            self.is_running = False
            print("日志采集器已停止。")
        else:
            print("日志采集器尚未启动。")

    def get_status(self):
        return self.is_running

# 创建日志采集器实例
log_collector = LogCollector()

@app.route("/startcollect", methods=["GET"])
def start_collect():
    if log_collector.get_status():
        return jsonify({"code": 500, "message": "日志采集器已经在运行中！", "status": "start"})

    log_collector.start()
    return jsonify({"code": 200, "message": "日志采集器启动成功！", "status": "start"})

@app.route("/stopcollect", methods=["GET"])
def stop_collect():
    if not log_collector.get_status():
        return jsonify({"code": 500, "message": "日志采集器已停止或未启动！", "status": "stop"})

    log_collector.stop()
    return jsonify({"code": 200, "message": "日志采集器已成功停止！", "status": "stop"})

@app.route("/status", methods=["GET"])
def get_status():
    status = "start" if log_collector.get_status() else "stop"
    return jsonify({"code": 200, "message": "日志采集器状态", "status": status})

def start_flask_server():
    app.run(host="127.0.0.1", port=8083)  # 监听所有 IP

# 在独立线程中启动 Flask 服务
threading.Thread(target=start_flask_server, daemon=True).start()

# 保持日志采集器持续运行
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("日志采集器已终止。")
