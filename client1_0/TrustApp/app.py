# app.py
# -*- coding: utf-8 -*-
import datetime
from datetime import datetime
from fastapi import FastAPI, HTTPException, Query
from collections import defaultdict, deque
from pydantic import BaseModel

from models import DeviceTrustLevelResponse
from config import config
from logger import logger
from utils import triplet_key, adjust_scores, send_trust_level_result
from prediction import predict_single_log
from Parser import parse_url
from TrustApp.score_manager import scores_manager

from TrustApp.forestApp import load_config, schedule_task

# 全局日志队列
window_size = config['window_size']
device_logs = defaultdict(lambda: deque(maxlen=window_size + 1))

# 创建 FastAPI 应用
app = FastAPI()


def process_triplet_logs(triplet):
    try:
        result = predict_triplet_log_sequence(triplet)
        adjust_scores(triplet, result)
        #send_trust_level_result(triplet, result)
    except Exception as e:
        logger.error(f"处理三元组日志时出错: {e}")
        raise


def predict_triplet_log_sequence(triplet):
    try:
        log_sequence = list(device_logs[triplet])
        result = predict_single_log(log_sequence)
        return result  # "Anomaly" 或 "Normal"
    except Exception as e:
        logger.error(f"预测三元组日志序列时出错: {e}")
        raise HTTPException(status_code=500, detail="预测失败")


class LogEntry(BaseModel):
    time_local: str
    remote_addr: str
    remote_user: str
    request: str
    status: str
    body_bytes_sent: str
    http_referer: str
    http_user_agent: str
    http_x_forwarded_for: str


@app.post("/deviceTrustLevelModel", response_model=DeviceTrustLevelResponse)
async def process_log_entry(request: LogEntry):
    try:
        # 获取请求的 URL 和 user-agent
        url = str(request.request)
        user_agent = str(request.http_user_agent)
        source_ip = request.remote_addr

        # 调用你的 URL 解析逻辑
        parts = url.split(' ')
        serviceId, logId = parse_url(parts[1])

        # 将 logId 写入文件
        with open('event_ids.txt', 'a') as file:
            file.write(f'{logId}\n')

        # 生成三元组
        triplet = triplet_key(user_agent, source_ip, serviceId)
        device_logs[triplet].append(logId)

        print(device_logs[triplet])

        # 检查日志条目是否足够
        if len(device_logs[triplet]) <= window_size:
            return DeviceTrustLevelResponse(code="200", msg="日志条目不足", data={})

        # 处理三元组日志
        process_triplet_logs(triplet)

        return DeviceTrustLevelResponse(code="200", msg="请求成功", data={})

    except ValueError as e:
        logger.error(f"URL解析失败: {e}")
        raise HTTPException(status_code=400, detail="无效的URL")
    except Exception as e:
        logger.error(f"处理日志条目时出错: {e}")
        raise HTTPException(status_code=500, detail="内部服务器错误")


@app.post("/TrustLevelResult", response_model=dict)
async def get_trust_level_result(
        result_type: int = Query(None),  # 0: browserScore, 1: deviceScore, 2: serviceScore
):
    try:
        # 获取当前分数
        scores_data = scores_manager.get_scores()

        # 初始化三个列表，用于存储结果
        browser_scores = []
        device_scores = []
        service_scores = []

        # 获取并处理浏览器评分
        for browser_id, data in scores_data.get('browsers', {}).items():
            browser_scores.append({
                "browserId": browser_id,
                "browserScore": data["score"],
                "last_reset": data["last_reset"]
            })

        # 获取并处理设备评分
        for device_id, data in scores_data.get('devices', {}).items():
            device_scores.append({
                "deviceIp": device_id,
                "deviceScore": data["score"],
                "last_reset": data["last_reset"]
            })

        # 获取并处理服务评分
        for service_id, data in scores_data.get('services', {}).items():
            service_scores.append({
                "serviceId": service_id,
                "serviceScore": data["score"],
                "last_reset": data["last_reset"]
            })

        # 根据 result_type 返回指定的分数类型
        if result_type is None:
            return {
                "code": "200",
                "message": "OK",
                "browserScores": browser_scores,
                "deviceScores": device_scores,
                "serviceScores": service_scores
            }
        elif result_type == 0:
            return {
                "code": "200",
                "message": "OK",
                "browserScores": browser_scores
            }
        elif result_type == 1:
            return {
                "code": "200",
                "message": "OK",
                "deviceScores": device_scores
            }
        elif result_type == 2:
            return {
                "code": "200",
                "message": "OK",
                "serviceScores": service_scores
            }
        else:
            raise HTTPException(status_code=400, detail="无效的 result_type 参数，必须是 0, 1 或 2")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"内部服务器错误: {e}")


@app.post("/TrustLevelByTime", response_model=dict)
async def get_trust_level_by_time(
        start_time: str = Query(None),
        end_time: str = Query(None),
):
    try:
        # 获取当前分数
        scores_data = scores_manager.get_scores()

        # 如果提供了起始时间和结束时间，则转换为 datetime 对象
        start_dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S") if start_time else None
        end_dt = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S") if end_time else None

        # 初始化结果列表
        result_list = []

        # 获取并处理浏览器评分
        for browser_id, data in scores_data.get('browsers', {}).items():
            last_reset_dt = datetime.strptime(data["last_reset"], "%Y-%m-%d %H:%M:%S")
            if (not start_dt or start_dt <= last_reset_dt) and (not end_dt or last_reset_dt <= end_dt):
                result_list.append({
                    "uuid": browser_id,
                    "type": "browser",
                    "id": browser_id,
                    "score": data["score"],
                    "last_reset": data["last_reset"]
                })

        # 获取并处理设备评分
        for device_id, data in scores_data.get('devices', {}).items():
            last_reset_dt = datetime.strptime(data["last_reset"], "%Y-%m-%d %H:%M:%S")
            if (not start_dt or start_dt <= last_reset_dt) and (not end_dt or last_reset_dt <= end_dt):
                result_list.append({
                    "uuid": device_id,
                    "type": "device",
                    "id": device_id,
                    "score": data["score"],
                    "last_reset": data["last_reset"]
                })

        # 获取并处理服务评分
        for service_id, data in scores_data.get('services', {}).items():
            last_reset_dt = datetime.strptime(data["last_reset"], "%Y-%m-%d %H:%M:%S")
            if (not start_dt or start_dt <= last_reset_dt) and (not end_dt or last_reset_dt <= end_dt):
                result_list.append({
                    "uuid": service_id,
                    "type": "service",
                    "id": service_id,
                    "score": data["score"],
                    "last_reset": data["last_reset"]
                })

        # 返回查询结果
        return {
            "code": "200",
            "message": "OK",
            "data": result_list
        }
    except ValueError as e:
        logger.error(f"时间参数解析失败: {e}")
        raise HTTPException(status_code=400, detail="无效的时间参数格式，应为 'YYYY-MM-DD HH:MM:SS'")
    except Exception as e:
        logger.error(f"处理时间查询请求时出错: {e}")
        raise HTTPException(status_code=500, detail=f"内部服务器错误: {e}")


# 应用关闭时保存分数
@app.on_event("shutdown")
def on_shutdown():
    scores_manager.save_scores()
    logger.info("程序关闭，分数已保存。")


# 主程序入口
if __name__ == "__main__":
    import uvicorn
    from threading import Thread

    def run_tasks():
        config = load_config('config/config.json')
        schedule_task(config)

    # 启动一个新线程来运行任务
    Thread(target=run_tasks).start()

    # 启动uvicorn服务器
    uvicorn.run(app, host="localhost", port=8000)

