# utils.py
# -*- coding: utf-8 -*-
import json
import os
import re

import httpx
import requests

from logger import logger
from score_manager import scores_manager_all, scores_manager_for_log  # 导入 scores_manager


def triplet_key(browserId, deviceMac, serviceId):
    return (browserId, deviceMac, serviceId)


def adjust_scores(triplet, result):
    browserId, deviceMac, serviceId = triplet

    # 如果检测到异常，减少对应的分数
    if result == "Anomaly":
        scores_manager_all.update_browser_score(browserId)
        #scores_manager_all.update_device_score(deviceMac)
        scores_manager_all.update_service_score(serviceId)

        scores_manager_for_log.update_browser_score(browserId)
        #scores_manager_for_log.update_device_score(deviceMac)
        scores_manager_for_log.update_service_score(serviceId)


def send_trust_level_result(triplet, result):
    callback_url = "http://localhost:8067/deviceTrustLevelResult"
    browserId, deviceMac, serviceId = triplet

    current_scores = scores_manager_all.get_scores()

    browser_score = current_scores['browsers'].get(browserId, {}).get('score', 100)
    device_score = current_scores['devices'].get(deviceMac, {}).get('score', 100)
    service_score = current_scores['services'].get(serviceId, {}).get('score', 100)

    callback_data = {
        "browserId": browserId,
        "deviceMac": deviceMac,
        "serviceId": serviceId,
        "browserScore": browser_score,
        "deviceScore": device_score,
        "serviceScore": service_score,
        "result": result
    }
    try:
        with httpx.Client() as client:
            response = client.post(callback_url, json=callback_data)
            if response.status_code != 200:
                logger.error(f"回调失败，状态码 {response.status_code}")
    except httpx.RequestError as e:
        logger.error(f"请求错误: {e.request.url!r}.")


# 计算总页数
def get_total_pages(total_items, page_size):
    return (total_items + page_size - 1) // page_size


#解析日志信息为json格式
def parse_log_entry(log_entry):
    """Parse a single log entry and extract required information."""
    log_pattern = r'(\d+\.\d+\.\d+\.\d+).*\[(.*?)\] "(.*?)" \d+ \d+ "-" "(.*?)"'
    match = re.match(log_pattern, log_entry)

    if match:
        ip = match.group(1)
        timestamp = match.group(2)
        service = match.group(3)
        browser = match.group(4)
        return {
            "ip": ip,
            "timestamp": timestamp,
            "service": service,
            "browser": browser
        }
    return None


#解析日志文件
def parse_log_file(filename, jsonfile):
    #filename = 源日志信息
    #jsonfile = 解析后的日志信息
    """Parse the log file and return a list of entries, total logs count, and unique device count."""
    ip_set = set()
    total_logs = 0
    parsed_entries = []

    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            entry = parse_log_entry(line.strip())
            if entry:
                parsed_entries.append(entry)
                ip_set.add(entry["ip"])
                total_logs += 1
        # 将解析后的日志条目保存到 JSON 文件
    with open(jsonfile, 'w', encoding='utf-8') as json_file:
        json.dump({"data": parsed_entries}, json_file, ensure_ascii=False, indent=4)

    return total_logs, len(ip_set)


#更新日志统计数据
def update_statistics_in_file(stats_filename, total_logs, unique_devices):
    """Update log count and unique device count in an existing JSON file."""
    try:
        # 读取现有的 JSON 文件
        with open(stats_filename, 'r', encoding='gbk') as file:
            data = json.load(file)

        # 更新指定的字段
        data['totalCount'] = total_logs
        data['deviceCount'] = unique_devices
        # 请求采集器状态
        try:
            response = requests.get("http://127.0.0.1:8083/status")
            if response.status_code == 200 and response.json().get("code") == 200:
                data['status'] = response.json().get("status")  # 默认状态为"unknown"如果没有返回状态
        except requests.RequestException:
            print("Unable to connect to the collector, status not updated.")
        # 将更新后的内容写回文件
        with open(stats_filename, 'w', encoding='gbk') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

        print(f"Updated {stats_filename}: totalCount={total_logs}, deviceCount={unique_devices}")
        return data
    except FileNotFoundError:
        print(f"Error: {stats_filename} not found.")
    except json.JSONDecodeError:
        print(f"Error: Failed to parse {stats_filename} as JSON.")
    except Exception as e:
        print(f"An error occurred: {e}")


# 从 JSON 文件读取日志数据
def load_logs_from_file(file_path: str):
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            try:
                data = json.load(file)
                return data.get("data", [])  # 读取 JSON 文件中的 "data" 字段
            except json.JSONDecodeError as e:
                print(f"Error reading JSON file: {e}")
                return []
    else:
        print(f"File {file_path} not found.")
        return []


def updateTopic(file_path, topic):
    try:
        # 读取文件
        with open(file_path, 'r', encoding='gbk') as file_obj:
            data = json.load(file_obj)

        result = False

        # 提取并更新
        if topic == 3:
            result = data.get("topic3", False)
            data['topic3'] = False
        elif topic == 4:
            result = data.get("topic4", False)
            data['topic4'] = False
        else:
            print(f"无效的主题编号: {topic}")
            return f"无效的主题编号: {topic}"

        # 在写入之前先检查文件内容是否为有效的JSON
        with open(file_path, 'w', encoding='gbk') as file_obj:
            json.dump(data, file_obj, ensure_ascii=False, indent=4)

        return result

    except FileNotFoundError:
        print(f"文件未找到: {file_path}")
        return f"文件未找到: {file_path}"
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {file_path} - {e}")
        return f"JSON解析错误: {file_path}"
    except IOError as e:
        print(f"写入文件时发生错误: {e}")
        return f"写入文件时发生错误: {e}"


def writeTopic(file_path, topic):
    try:
        # 读取文件内容
        with open(file_path, 'r', encoding='gbk') as file:
            data = json.load(file)
    except FileNotFoundError:
        return f"File not found: {file_path}"
    except json.JSONDecodeError as e:
        return f"JSON decode error: {e}"

    # 提取并更新
    if topic == 3:
        data['topic3'] = True
    elif topic == 4:
        data['topic4'] = True

    # 将更新后的内容写回文件
    try:
        with open(file_path, 'w', encoding='gbk') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
    except IOError as e:
        return f"IO error: {e}"

    return True
