# -*- coding: utf-8 -*-
import datetime
import httpx
from logger import logger
from config import config
from database import scores_lock

def triplet_key(browserId, deviceMac, serviceId):
    return (browserId, deviceMac, serviceId)

def adjust_scores(triplet, result, scores):
    with scores_lock:
        current_time = datetime.datetime.now()
        reset_interval_seconds = config.get('reset_interval_seconds', 3 * 3600)

        browserId, deviceMac, serviceId = triplet

        for entity_type, entity_id in [('browsers', browserId), ('devices', deviceMac), ('services', serviceId)]:
            entity_scores = scores[entity_type]
            last_reset = entity_scores[entity_id]['last_reset']
            if (current_time - last_reset).total_seconds() >= reset_interval_seconds:
                entity_scores[entity_id]['score'] = 100
                entity_scores[entity_id]['last_reset'] = current_time
            # 如果检测到异常，则降低分数
            if result == "Anomaly":
                decrement = config.get('decrements', {}).get(f"{entity_type[:-1]}Score", 1)
                entity_scores[entity_id]['score'] = max(0, entity_scores[entity_id]['score'] - decrement)
        # 分数的保存由后台任务处理

def send_trust_level_result(triplet, result, scores):
    callback_url = "http://localhost:8067/deviceTrustLevelResult"
    browserId, deviceMac, serviceId = triplet

    current_scores = {
        'browserScore': scores['browsers'][browserId]['score'],
        'deviceScore': scores['devices'][deviceMac]['score'],
        'serviceScore': scores['services'][serviceId]['score']
    }

    callback_data = {
        "browserId": browserId,
        "deviceMac": deviceMac,
        "serviceId": serviceId,
        "browserScore": current_scores['browserScore'],
        "deviceScore": current_scores['deviceScore'],
        "serviceScore": current_scores['serviceScore'],
        "result": result
    }
    try:
        with httpx.Client() as client:
            response = client.post(callback_url, json=callback_data)
            if response.status_code != 200:
                logger.error(f"回调失败，状态码 {response.status_code}")
    except httpx.RequestError as e:
        logger.error(f"请求错误: {e.request.url!r}.")
