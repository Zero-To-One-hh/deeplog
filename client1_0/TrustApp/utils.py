# utils.py
# -*- coding: utf-8 -*-
import datetime
import httpx
from logger import logger
from config import config
from TrustApp.score_manager import scores_manager  # 导入 scores_manager

def triplet_key(browserId, deviceMac, serviceId):
    return (browserId, deviceMac, serviceId)

def adjust_scores(triplet, result):
    browserId, deviceMac, serviceId = triplet

    # 如果检测到异常，减少对应的分数
    if result == "Anomaly":
        decrement_browser = config.get('decrements', {}).get('browserScore', 1)
        decrement_device = config.get('decrements', {}).get('deviceScore', 1)
        decrement_service = config.get('decrements', {}).get('serviceScore', 1)

        scores_manager.update_browser_score(browserId, decrement_browser)
        scores_manager.update_device_score(deviceMac, decrement_device)
        scores_manager.update_service_score(serviceId, decrement_service)

def send_trust_level_result(triplet, result):
    callback_url = "http://localhost:8067/deviceTrustLevelResult"
    browserId, deviceMac, serviceId = triplet

    current_scores = scores_manager.get_scores()

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
