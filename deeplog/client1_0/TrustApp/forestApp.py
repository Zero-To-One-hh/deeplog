# forestApp.py
# -*- coding: utf-8 -*-
import json
import time
from datetime import datetime, timedelta

import requests

from process_data import process_data
from utils import writeTopic


def load_config(url: str = './config/config.json'):
    with open(url, 'r') as f:
        config = json.load(f)
    return config


def fetch_data(config, start_time=None, interval=None, max_count=None):
    params = {}
    
    if False:
        # 测试环境为了保证每次都是新的数据读入，使用数量限制，不再设置起始时间
        # 如果没有传入开始时间，使用当前时间
        if start_time:
            params['startTime'] = start_time
        else:
            params['startTime'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 如果传入了时间间隔，计算结束时间
        if interval:
            end_time = datetime.strptime(params['startTime'], '%Y-%m-%d %H:%M:%S')
            end_time = end_time + timedelta(seconds=interval)
            params['endTime'] = end_time.strftime('%Y-%m-%d %H:%M:%S')
        elif config.get('end_time'):
            params['endTime'] = config['end_time']
        
        # 设置获取数据的最大数量
        if max_count:
            params['count'] = min(max_count, 10000)  # 限制最大数量为10000
        elif config.get('count'):
            params['count'] = config['count']

    try:
        response = requests.get("http://127.0.0.1:8011/test", params=params)
        response.encoding = response.apparent_encoding
        response.raise_for_status()

        data = response.json()

        if data['code'] == 1:
            result = writeTopic("./config/updateTopic.json", 3)
            if result != True:
                print("更新配置文件失败")
            return data['data']
        else:
            print(f"Error in response: {data['message']}")
            return []
    except requests.exceptions.RequestException as req_e:
        print(f"HTTP error: {req_e}")
        return []
    except ValueError as json_e:
        print(f"JSON decode error: {json_e}")
        return []
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []


def get_data(config, startTime, endTime, count):
    params = {}
    params['startTime'] = startTime
    params['endTime'] = endTime
    count = min(count, 10000)
    params['count'] = count

    try:
        # response = requests.get(config['api_endpoint'], params=params)
        response = requests.get("http://127.0.0.1:8011/test", params=params)
        # response.encoding = 'gbk'  # 明确设置编码为 'utf-8' 或其他所需编码
        response.encoding = response.apparent_encoding
        response.raise_for_status()

        data = response.json()

        if data['code'] == 1:
            print(data)
            return data['data']
        else:
            print(f"Error in response: {data['message']}")
            return []
    except requests.exceptions.RequestException as req_e:
        print(f"HTTP error: {req_e}")
        return []
    except ValueError as json_e:
        print(f"JSON decode error: {json_e}")
        return []
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []

# 5秒读一次，最大读100条
def schedule_task(config):
    interval = config.get('schedule_interval', 15)
    max_count = config.get('max_count', 100)
    time_window = config.get('time_window', 5)  # 默认5秒钟的时间窗口
    
    while True:
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data_list = fetch_data(config, 
                             start_time=current_time, 
                             interval=time_window, 
                             max_count=max_count)
        
        for data_item in data_list:
            process_data(data_item, config)
            
        time.sleep(interval)  # 将秒转换为分钟


# 避免重复读，暂时禁用
def post_once_topic3(config):
    data_list = fetch_data(config)
    if data_list:
        # for data_item in data_list:
        #     process_data(data_item, config)
        return True
    else:
        return False


if __name__ == "__main__":
    config = load_config()
    schedule_task(config)
