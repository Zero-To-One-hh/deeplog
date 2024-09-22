# -*- coding: utf-8 -*-
import json
import time
import datetime
import logging

CONFIG_FILE = 'config/config.json'

def load_config():
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            # 设置默认值
            config.setdefault('decrements', {'browserScore': 1, 'deviceScore': 1, 'serviceScore': 1})
            config.setdefault('reset_interval_seconds', 3 * 3600)
            config.setdefault('save_interval_seconds', 600)
            config.setdefault('api_request_interval_seconds', 300)
            config.setdefault('window_size', 10)
            config.setdefault('device', "cpu")
            # 其他默认配置...
            config.setdefault('save_dir', f"./result/deeplog{time.strftime('%Y_%m_%d', time.localtime())}/")
            return config
    except FileNotFoundError:
        logging.error("未找到配置文件。")
        raise

config = load_config()
