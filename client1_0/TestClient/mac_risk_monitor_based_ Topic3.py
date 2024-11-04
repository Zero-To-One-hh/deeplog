# -*- coding: utf-8 -*-
import threading
import time
import datetime
import httpx
import logging

logger = logging.getLogger(__name__)

class MacRiskMonitor(threading.Thread):
    def __init__(self, scores, scores_lock, config):
        super().__init__(daemon=True)
        self.scores = scores
        self.scores_lock = scores_lock
        self.config = config
        self.interval = config.get('api_request_interval_seconds', 60)
        self.api_url = "http://127.0.0.1:8089/apispace/public/snort/list/bytime"

    def run(self):
        while True:
            try:
                self.check_risk_macs()
            except Exception as e:
                logger.error(f"检查风险MAC地址时出错: {e}")
            time.sleep(self.interval)

    def check_risk_macs(self):
        end_time = datetime.datetime.now()
        start_time = end_time - datetime.timedelta(minutes=1)  # 查询过去1分钟的数据
        params = {
            'startTime': start_time.strftime("%Y-%m-%d %H:%M:%S"),
            'endTime': end_time.strftime("%Y-%m-%d %H:%M:%S"),
            'count': 10000
        }
        try:
            with httpx.Client() as client:
                response = client.get(self.api_url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('code') == 1:
                        self.process_risk_data(data.get('data', []))
                        logger.info("获取数据成功")
                    else:
                        logger.error(f"API返回错误：{data.get('message')}")
                else:
                    logger.error(f"API请求失败，状态码：{response.status_code}")
        except httpx.RequestError as e:
            logger.error(f"请求错误: {e.request.url!r}.")

    def process_risk_data(self, data_list):
        with self.scores_lock:
            for item in data_list:
                eth_src = item.get('eth_src')
                eth_dst = item.get('eth_dst')

                # 对源MAC地址降低分数
                if eth_src:
                    device_scores = self.scores['devices']
                    last_reset = device_scores[eth_src]['last_reset']
                    current_time = datetime.datetime.now()
                    reset_interval_seconds = self.config.get('reset_interval_seconds', 3 * 3600)
                    if (current_time - last_reset).total_seconds() >= reset_interval_seconds:
                        device_scores[eth_src]['score'] = 100
                        device_scores[eth_src]['last_reset'] = current_time

                    decrement = self.config.get('decrements', {}).get('deviceScore', 1)
                    device_scores[eth_src]['score'] = max(0, device_scores[eth_src]['score'] - decrement)

                # 对目的MAC地址降低分数
                if eth_dst:
                    device_scores = self.scores['devices']
                    last_reset = device_scores[eth_dst]['last_reset']
                    current_time = datetime.datetime.now()
                    reset_interval_seconds = self.config.get('reset_interval_seconds', 3 * 3600)
                    if (current_time - last_reset).total_seconds() >= reset_interval_seconds:
                        device_scores[eth_dst]['score'] = 100
                        device_scores[eth_dst]['last_reset'] = current_time

                    decrement = self.config.get('decrements', {}).get('deviceScore', 1)
                    device_scores[eth_dst]['score'] = max(0, device_scores[eth_dst]['score'] - decrement)

            logger.info("已处理风险MAC地址，分数已调整。")
