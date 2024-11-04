# -*- coding: utf-8 -*-
import json
from datetime import datetime

def load_scores():
    try:
        with open('../config/scores.json', 'r') as f:
            scores = json.load(f)
    except FileNotFoundError:
        scores = {"devices": {}}
    return scores

def save_scores(scores):
    with open('scores.json', 'w') as f:
        json.dump(scores, f, indent=4)

def process_data(data_item, config):
    # 加载风险等级配置
    risk_levels = config.get('risk_levels', {})
    msg = data_item.get('msg', '')
    ip = data_item.get('src_addr', '')
    mac = data_item.get('eth_src', '')
    timestamp = data_item.get('timestamp', '')
    # 根据msg字段确定风险等级和分数减值
    score_decrement = 0
    for level, details in risk_levels.items():
        if msg in details.get('messages', []):
            score_decrement = details.get('score_decrement', 0)
            break  # 找到匹配的风险等级后退出循环

    if score_decrement == 0:
        score_decrement = 0.1

    # 加载现有的分数
    scores = load_scores()

    # 更新设备的分数（以MAC地址为唯一标识）
    devices = scores.get('devices', {})
    device = devices.get(ip, {"score": 100, "last_reset": ""})
    device['score'] = max(0, device.get('score', 100) - score_decrement)
    device['last_reset'] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    devices[ip] = device
    scores['devices'] = devices

    # 保存更新后的分数
    save_scores(scores)

    # 可选：打印分数变化日志
    print(f"已更新设备 {mac} ({ip}) 的分数：{device['score']}（降低了 {score_decrement} 分）")
