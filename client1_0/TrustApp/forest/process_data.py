# process_data.py
# -*- coding: utf-8 -*-
from datetime import datetime
from score_manager import scores_manager

def process_data(data_item, config):
    # 加载风险等级配置
    risk_levels = config.get('risk_levels', {})
    msg = data_item.get('msg', '')
    ip = data_item.get('src_addr', '')
    mac = data_item.get('eth_src', '')
    timestamp = data_item.get('timestamp', '')
    # 根据 msg 字段确定风险等级和分数减值
    score_decrement = 0
    for level, details in risk_levels.items():
        if msg in details.get('messages', []):
            score_decrement = details.get('score_decrement', 0)
            break  # 找到匹配的风险等级后退出循环

    if score_decrement == 0:
        score_decrement = 0.1

    # 更新设备的分数（以 IP 地址为唯一标识）
    scores_manager.update_device_score(ip, score_decrement)

    # 可选：打印分数变化日志
    device_score = scores_manager.scores['devices'][ip]['score']
    print(f"已更新设备 {mac} ({ip}) 的分数：{device_score}（降低了 {score_decrement} 分）")
