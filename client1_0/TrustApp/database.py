# -*- coding: utf-8 -*-
import json
import datetime
import threading
from collections import defaultdict
from logger import logger

SCORES_FILE = 'config/scores.json'
scores_lock = threading.Lock()

# 定义 scores 变量
scores = {
    'browsers': defaultdict(lambda: {'score': 100, 'last_reset': datetime.datetime.now()}),
    'devices': defaultdict(lambda: {'score': 100, 'last_reset': datetime.datetime.now()}),
    'services': defaultdict(lambda: {'score': 100, 'last_reset': datetime.datetime.now()})
}

def load_scores():
    try:
        with open(SCORES_FILE, 'r') as f:
            data = json.load(f)
            # 将时间戳字符串转换为 datetime 对象
            for entity_type in ['browsers', 'devices', 'services']:
                if entity_type in data:
                    for entity_id in data[entity_type]:
                        data[entity_type][entity_id]['last_reset'] = datetime.datetime.fromisoformat(
                            data[entity_type][entity_id]['last_reset'])
            return data
    except FileNotFoundError:
        logger.info("未找到分数文件，初始化为空数据。")
        return {
            'browsers': {},
            'devices': {},
            'services': {}
        }

def save_scores():
    with scores_lock:
        with open(SCORES_FILE, 'w') as f:
            data = {
                'browsers': {},
                'devices': {},
                'services': {}
            }
            for entity_type in ['browsers', 'devices', 'services']:
                for entity_id in scores[entity_type]:
                    entity_data = scores[entity_type][entity_id].copy()
                    entity_data['last_reset'] = entity_data['last_reset'].isoformat()
                    data[entity_type][entity_id] = entity_data
            json.dump(data, f)
