# process_data.py
# -*- coding: utf-8 -*-
import logging

from alert_data import AlertData
from forest_train.AnomalyDetectionModel import AnomalyDetectionModel
from score_manager import *
import os

# 配置logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

current_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(current_dir, 'forest_train', 'random_forest_model.pkl')
model = AnomalyDetectionModel(model_path)

def process_data(data_item, config):
    # 创建告警数据对象
    alert = AlertData(data_item)
    
    try:
        # 准备模型输入数据
        model_input = [[
            alert.priority,
            alert.msg,
            alert.dir,
            alert.attack_type,
            alert.action,
            alert.eth_len,
            alert.dst_ap,
            alert.eth_dst,
            alert.dst_addr,
            alert.src_addr,
            alert.rule
        ]]
        
        # 使用模型预测是否为高危日志
        is_high_risk = model.predict(model_input)[0]
        
        # 根据预测结果设置分数减值
        score_decrement = 0.2 if is_high_risk else 0.1
        
    except Exception as e:
        logger.error(f"模型预测失败: {str(e)}")
        # 如果模型预测失败，使用默认值
        score_decrement = 0.1

    # 更新发送设备的分数
    scores_manager_all.update_device_score(alert.src_addr, score_decrement)
    scores_manager_for_netdata.update_device_score(alert.src_addr, score_decrement)

    # 更新接收设备的分数
    scores_manager_all.update_device_score(alert.dst_addr, score_decrement)
    scores_manager_for_netdata.update_device_score(alert.dst_addr, score_decrement)

    # 记录源设备和目标设备的分数变化
    src_score = scores_manager_all.scores['devices'][alert.src_addr]['score']
    dst_score = scores_manager_all.scores['devices'][alert.dst_addr]['score']

    logger.info(
        f"设备分数更新 | "
        f"源设备MAC: {alert.eth_src} | "
        f"源设备IP: {alert.src_addr} | "
        f"源设备分数: {src_score:.2f} | "
        f"目标设备MAC: {alert.eth_dst} | "
        f"目标设备IP: {alert.dst_addr} | "
        f"目标设备分数: {dst_score:.2f} | "
        f"减分: {score_decrement:.2f} | "
        f"是否高危: {'是' if is_high_risk else '否'}"
    )
