# forestApp.py
# -*- coding: utf-8 -*-
import requests
import json
import time
from datetime import datetime
from process_data import process_data


def load_config(url: str = '../config/config.json'):
    with open(url, 'r') as f:
        config = json.load(f)
    return config


import requests


def fetch_data(config):
    params = {}
    if config.get('start_time'):
        params['startTime'] = config['start_time']
    if config.get('end_time'):
        params['endTime'] = config['end_time']
    if config.get('count'):
        params['count'] = config['count']

    try:
        response = requests.get(config['api_endpoint'], params=params)
        response.encoding = 'utf-8'  # 明确设置编码为 'utf-8' 或其他所需编码
        response.raise_for_status()

        data = response.json()

        if data['code'] == '200':
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


def schedule_task(config):
    interval = config.get('schedule_interval', 5)
    while True:
        data_list = fetch_data(config)
        for data_item in data_list:
            process_data(data_item, config)
        time.sleep(interval)


if __name__ == "__main__":
    config = load_config()
    schedule_task(config)
