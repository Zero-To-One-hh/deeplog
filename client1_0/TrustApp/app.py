# -*- coding: utf-8 -*-
import json
import sys
import datetime
from fastapi import FastAPI, HTTPException, Request, Query
from collections import defaultdict, deque
from models import DeviceTrustLevelRequest, DeviceTrustLevelResponse
from config import config
from logger import logger
from database import load_scores, scores_lock, scores, save_scores
from utils import triplet_key, adjust_scores, send_trust_level_result
from prediction import predict_single_log
from background_tasks import start_background_tasks
from Parser import parse_url

# 初始化分数并加载已有数据
scores_data = load_scores()
for entity_type in ['browsers', 'devices', 'services']:
    scores[entity_type].update(scores_data.get(entity_type, {}))

# 启动后台任务
start_background_tasks()

# 全局日志队列
window_size = config['window_size']
device_logs = defaultdict(lambda: deque(maxlen=window_size + 1))

# 创建FastAPI应用
app = FastAPI()


def process_triplet_logs(triplet):
    try:
        result = predict_triplet_log_sequence(triplet)
        adjust_scores(triplet, result, scores)
        send_trust_level_result(triplet, result, scores)
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


@app.post("/deviceTrustLevelModel", response_model=DeviceTrustLevelResponse)
async def process_log_entry(request: Request):
    try:
        url = request.url.path
        serviceId, logId = parse_url(url)

        with open('event_ids.txt', 'a') as file:
            file.write(f'{logId}\n')

        triplet = triplet_key(request.headers.get('browserId'), request.client.host, serviceId)
        device_logs[triplet].append(logId)

        print(device_logs[triplet])

        if len(device_logs[triplet]) <= window_size:
            return DeviceTrustLevelResponse(code="200", msg="日志条目不足", data={})

        process_triplet_logs(triplet)
        return DeviceTrustLevelResponse(code="200", msg="请求成功", data={})
    except ValueError as e:
        logger.error(f"URL解析失败: {e}")
        raise HTTPException(status_code=400, detail="无效的URL")
    except Exception as e:
        logger.error(f"处理日志条目时出错: {e}")
        raise HTTPException(status_code=500, detail="内部服务器错误")


# 新增接口，提供基于查询参数的评分信息返回
@app.post("/TrustLevelResult", response_model=DeviceTrustLevelResponse)
async def get_trust_level_result(
        result_type: int = Query(None),  # 0: browserScore, 1: deviceScore, 2: serviceScore
        startTime: str = Query(None),
        endTime: str = Query(None)
):
    try:
        # 初始化三个列表，用于存储结果
        browser_scores = []
        device_scores = []
        service_scores = []

        for triplet, logs in device_logs.items():
            # 添加时间范围过滤逻辑，如果没有传入 startTime 和 endTime，默认返回所有数据
            # 假设 logs 是保存了时间信息的日志数据结构
            if startTime and endTime:
                filtered_logs = [log for log in logs if startTime <= log['time'] <= endTime]
            else:
                filtered_logs = logs

            for log in filtered_logs:
                # 计算并加入相应的分数，假设分数是基于日志的某种计算逻辑
                browser_scores.append({
                    "browserId": triplet[0],
                    "browserScore": "normal",  # 示例值，根据实际逻辑修改
                    "time": log['time'],
                    "returnTime": datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
                })

                device_scores.append({
                    "deviceIp": triplet[1],
                    "deviceScore": "normal",  # 示例值，根据实际逻辑修改
                    "time": log['time'],
                    "returnTime": datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
                })

                service_scores.append({
                    "serviceId": triplet[2],
                    "serviceScore": "normal",  # 示例值，根据实际逻辑修改
                    "time": log['time'],
                    "returnTime": datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
                })

        # 根据 result_type 返回指定的分数类型
        if result_type is None:
            return DeviceTrustLevelResponse(code="200", message="OK", data={
                "browserScores": browser_scores,
                "deviceScores": device_scores,
                "serviceScores": service_scores
            })
        elif result_type == 0:
            return DeviceTrustLevelResponse(code="200", message="OK", data={
                "browserScores": browser_scores
            })
        elif result_type == 1:
            return DeviceTrustLevelResponse(code="200", message="OK", data={
                "deviceScores": device_scores
            })
        elif result_type == 2:
            return DeviceTrustLevelResponse(code="200", message="OK", data={
                "serviceScores": service_scores
            })
        else:
            raise HTTPException(status_code=400, detail="无效的 result_type 参数，必须是 0, 1 或 2")
    except Exception as e:
        logger.error(f"查询信任等级时出错: {e}")
        raise HTTPException(status_code=500, detail="内部服务器错误")


SCORES_FILE_PATH = "config/scores.json"


def load_scores():
    try:
        with open(SCORES_FILE_PATH, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="分数文件未找到")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="分数文件解析错误")


# 创建 FastAPI 应用
app = FastAPI()

# 加载分数数据
scores_data = load_scores()


@app.post("/TrustLevelResult", response_model=dict)
async def get_trust_level_result(
        result_type: int = Query(None),  # 0: browserScore, 1: deviceScore, 2: serviceScore
):
    try:
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


# 应用关闭时保存分数
@app.on_event("shutdown")
def on_shutdown():
    save_scores()
    logger.info("程序关闭，分数已保存。")


# 主程序入口
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)
