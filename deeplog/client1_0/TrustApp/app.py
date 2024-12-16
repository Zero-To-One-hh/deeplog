# app.py
# -*- coding: utf-8 -*-
import datetime
import json
import os
from collections import defaultdict, deque
from datetime import datetime, timedelta

import requests
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from Parser import parse_url
from config import config
from forestApp import load_config, schedule_task, get_data, post_once_topic3
from logger import logger
from models import DeviceTrustLevelResponse
from prediction import predict_single_log
from score_manager import scores_manager_all, scores_manager_for_log, scores_manager_for_netdata
from utils import triplet_key, adjust_scores, get_total_pages, load_logs_from_file, \
    parse_log_file, update_statistics_in_file, writeTopic, updateTopic


# from utilClass import SearchLogRequest

class SearchLogRequest(BaseModel):
    pageSize: int
    pageNum: int


# 全局日志队列
window_size = config['window_size']
device_logs = defaultdict(lambda: deque(maxlen=window_size + 1))

# 创建 FastAPI 应用
app = FastAPI()


# 预测结果，调整分数
def process_and_predict_triplet_logs(triplet):
    try:
        # 获取日志序列并预测
        log_sequence = list(device_logs[triplet])
        result = predict_single_log(log_sequence)
        # 根据预测结果调整分数
        adjust_scores(triplet, result)

        return result

    except Exception as e:
        logger.error(f"处理和预测三元组日志时出错: {e}")
        raise HTTPException(status_code=500, detail="预测或处理失败")


#时间解析
def parse_time(time_str: str) -> datetime:
    try:
        if time_str:
            if len(time_str) == 10:  # 仅日期
                return datetime.strptime(time_str, "%Y-%m-%d")
            else:  # 日期 + 时间
                return datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        return None
    except ValueError:
        raise HTTPException(status_code=400,
                            detail="Invalid datetime format. Use 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS'")


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

        # 将 logId 写入文件，调试使用
        # with open('event_ids.txt', 'a') as file:
        #     file.write(f'{logId} ')

        # 生成三元组
        triplet = triplet_key(user_agent, source_ip, serviceId)
        device_logs[triplet].append(logId)

        print(device_logs[triplet])

        # 检查日志条目是否足够
        if len(device_logs[triplet]) <= window_size:
            return DeviceTrustLevelResponse(code="200", msg="日志条目不足", data={})

        # 处理三元组日志
        process_and_predict_triplet_logs(triplet)

        return DeviceTrustLevelResponse(code="200", msg="请求成功", data={})

    except ValueError as e:
        logger.error(f"URL解析失败: {e}")
        raise HTTPException(status_code=400, detail="无效的URL")
    except Exception as e:
        logger.error(f"处理日志条目时出错: {e}")
        raise HTTPException(status_code=500, detail="内部服务器错误")


# 给课题四的评分接口，根据类型
@app.post("/TrustLevelResult", response_model=dict)
async def get_trust_level_result(
        result_type: int = Query(None),  # 0: browserScore, 1: deviceScore, 2: serviceScore
):
    try:
        # 获取当前分数
        scores_data = scores_manager_all.get_scores()

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
            result1 = writeTopic("./config/updateTopic.json", 4)
            if result1 != True:
                print("更新配置文件失败")
            return {
                "code": "200",
                "message": "OK",
                "browserScores": browser_scores,
                "deviceScores": device_scores,
                "serviceScores": service_scores
            }
        elif result_type == 0:
            result1 = writeTopic("./config/updateTopic.json", 4)
            if result1 != True:
                print("更新配置文件失败")
            return {
                "code": "200",
                "message": "OK",
                "browserScores": browser_scores
            }
        elif result_type == 1:
            result1 = writeTopic("./config/updateTopic.json", 4)
            if result1 != True:
                print("更新配置文件失败")
            return {
                "code": "200",
                "message": "OK",
                "deviceScores": device_scores
            }
        elif result_type == 2:
            result1 = writeTopic("./config/updateTopic.json", 4)
            if result1 != True:
                print("更新配置文件失败")
            return {
                "code": "200",
                "message": "OK",
                "serviceScores": service_scores
            }
        else:
            raise HTTPException(status_code=400, detail="无效的 result_type 参数，必须是 0, 1 或 2")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"内部服务器错误: {e}")


#给课题四的评分接口，根据时间
@app.post("/TrustLevelByTime", response_model=dict)
async def get_trust_level_by_time(
        start_time: str = Query(None),
        end_time: str = Query(None),
):
    try:
        # 获取当前分数
        scores_data = scores_manager_all.get_scores()

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
        # result1=writeTopic("./config/updateTopic.json",4)
        # if result1!=True:
        #     print("更新配置文件失败")

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


#展示课题三告警信息
@app.post("/bj/searchTopic3", response_model=dict)
def search_topic3(
        start_time: str = Query(None),
        end_time: str = Query(None),
        count: int = Query(None)
):
    try:
        # 处理默认时间
        end_time = parse_time(end_time) or datetime.now()
        start_time = parse_time(start_time) or (end_time - timedelta(days=1))

        # 验证 count 参数（最大值10000）
        count = min(count, 10000)

        config = load_config('./config/config.json')
        #请求课题三数据
        data = get_data(config, start_time, end_time, count)

        # 过滤数据
        # 定义需要保留的字段
        fields_to_keep = ['seconds', 'action', 'class', 'dir', 'dst_addr', 'dst_ap', 'eth_dst', 'eth_src', 'iface',
                          'msg', 'priority', 'src_addr', 'src_ap', 'timestamp']

        # 使用列表推导式进行字段过滤
        filtered_data = [
            {key: item[key] for key in fields_to_keep if key in item}
            for item in data
        ]

        return {
            "code": 0,
            "status": True,
            "message": "OK",
            "data": filtered_data
        }

    except HTTPException as e:
        logger.error(f"请求错误: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"内部服务器错误: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


#展示日志信息,解析日志文件,生成日志json
@app.post("/bj/searchLog", response_model=dict)
def search_Log(
        pageSize: int = Query(None),
        pageNum: int = Query(None),
):
    try:
        # 获取请求中的 pageSize 和 pageNum
        #pageSize = request.pageSize
        #pageNum = request.pageNum

        # 验证 pageSize 和 pageNum 是否有效
        if pageSize <= 0 or pageNum <= 0:
            raise HTTPException(status_code=400, detail="pageSize 和 pageNum 必须为正整数")

        # 计算分页
        start_index = (pageNum - 1) * pageSize
        end_index = start_index + pageSize
        log_path = "../TestClient/generated_logs.txt"
        log_json_path = './config/parsed_logs.json'

        # 重新解析日志json
        parse_log_file(log_path, log_json_path)

        # 加载日志数据
        mock_logs = load_logs_from_file(log_json_path)

        # 获取分页数据
        paginated_logs = mock_logs[start_index:end_index]
        total_logs = len(mock_logs)
        total_pages = get_total_pages(total_logs, pageSize)

        response = {
            "code": 0,
            "status": True,
            "message": "OK",
            "data": paginated_logs,
            "totalPagenum": total_pages
        }

        return response

    except HTTPException as e:
        logger.error(f"请求错误: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"内部服务器错误: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")  # #展示日志状态信息


# 定义日志采集状态展示接口
@app.get("/bj/LogStatus")
def get_log_status():
    stats_file = './config/log_statistics.json'
    log_path = "../TestClient/generated_logs.txt"
    log_json_path = './config/parsed_logs.json'
    # 重新解析日志json
    total_logs, unique_devices = parse_log_file(log_path, log_json_path)
    # 更新 JSON 文件中的统计信息
    log_status = update_statistics_in_file(stats_file, total_logs, unique_devices)

    if log_status:
        response = {
            "code": 0,
            "status": True,
            "message": "OK",
            "data": [log_status]
        }
    else:
        response = {
            "code": 0,
            "status": False,
            "message": "读取日志采集状态失败",
            "data": []
        }

    return response


# 定义返回PID的接口
@app.get("/pid")
def get_pid():
    # 获取当前服务的进程ID
    pid = os.getpid()

    # 构建响应
    if pid:
        response = {
            "code": 200,
            "message": "OK",
            "data": [{"pid": pid}]
        }
    else:
        response = {
            "code": 500,
            "message": "获取PID失败",
            "data": []
        }

    return response


# 课题三更新提示
@app.get("/bj/updateTopic3")
def get_update_topic3():
    if updateTopic("./config/updateTopic.json", 3):
        response = {
            "code": 0,
            "status": True,
            "message": "课题三告警信息已更新！",
            "data": []
        }
    else:
        response = {
            "code": 0,
            "status": False,
            "message": "课题三告警信息尚未更新！",
            "data": []
        }
    return response


# 课题四更新提示
@app.get("/bj/updateTopic4")
def get_update_topic4():
    if updateTopic("./config/updateTopic.json", 4):
        response = {
            "code": 0,
            "status": True,
            "message": "已向课题四发送新的评估结果！",
            "data": []
        }
    else:
        response = {
            "code": 0,
            "status": False,
            "message": "未向课题四发送新的评估结果！",
            "data": []
        }
    return response


# 定义告警信息重新评估
@app.get("/bj/reappraise")
def reappraise():
    config = load_config('./config/config.json')
    result = post_once_topic3(config)

    if result:
        result1 = writeTopic("./config/updateTopic.json", 3)
        if result1 != True:
            print("更新配置文件失败")
        response = {
            "code": 0,
            "status": True,
            "message": "重新评估成功！",
        }
    else:
        response = {
            "code": 0,
            "status": False,
            "message": "重新评估失败！",
        }

    return response


# 向课题四发送评估数据
@app.get("/bj/sendScore")
def sendScore():
    if True:
        result = writeTopic("./config/updateTopic.json", 4)
        if result != True:
            print("更新配置文件失败")
            print(result)
        response = {
            "code": 0,
            "status": True,
            "message": "评估结果发送成功！",
        }
    else:
        response = {
            "code": 0,
            "status": False,
            "message": "评估结果发送失败！",
        }

    return response


#启用采集器
@app.get("/bj/startcollect")
def start_collect():
    stats_filename = './config/log_statistics.json'
    # 读取现有的 JSON 文件
    try:
        with open(stats_filename, 'r', encoding='gbk') as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        return {
            "code": 0,
            "status": False,
            "message": f"配置文件读取失败: {str(e)}"
        }

    if data['status'] == 'stop':
        try:
            response = requests.get("http://127.0.0.1:8083/startcollect", timeout=5)
            if response.status_code == 200:
                if response.json().get("code") == 200:
                    return {
                        "code": 0,
                        "status": True,
                        "message": "采集器启动成功！"
                    }
                data['status'] = response.json().get("status", "unknown")
        except requests.exceptions.RequestException as e:
            return {
                "code": 0,
                "status": False,
                "message": f"启动请求失败: {str(e)}"
            }

        # 将更新后的内容写回文件
        try:
            with open(stats_filename, 'w', encoding='gbk') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
        except IOError as e:
            return {
                "code": 0,
                "status": False,
                "message": f"更新配置文件失败: {str(e)}"
            }

    return {
        "code": 0,
        "status": False,
        "message": "启动失败，采集器已经启动!"
    }


#关闭采集器
@app.get("/bj/stopcollect")
def stop_collect():
    stats_filename = './config/log_statistics.json'

    # 读取现有的 JSON 文件
    try:
        with open(stats_filename, 'r', encoding='gbk') as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        return {
            "code": 0,
            "status": False,
            "message": f"配置文件读取失败: {str(e)}"
        }

    if data['status'] == 'start':
        try:
            response = requests.get("http://127.0.0.1:8083/stopcollect", timeout=5)
            if response.status_code == 200:
                if response.json().get("code") == 200:
                    return {
                        "code": 0,
                        "status": True,
                        "message": "采集器关闭成功！"
                    }
                data['status'] = response.json().get("status", "unknown")
        except requests.exceptions.RequestException as e:
            return {
                "code": 0,
                "status": False,
                "message": f"关闭请求失败: {str(e)}"
            }

        # 将更新后的内容写回文件
        try:
            with open(stats_filename, 'w', encoding='gbk') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
        except IOError as e:
            return {
                "code": 0,
                "status": False,
                "message": f"更新配置文件失败: {str(e)}"
            }

    return {
        "code": 0,
        "status": False,
        "message": "关闭失败，采集器已经关闭!"
    }


# 定义自学习引擎配置展示接口
@app.get("/bj/config")
def get_engine_config():
    file_path = './config/config.json'
    config_data = load_config(file_path)
    data = {}
    data["window_size"] = config_data["window_size"]
    data["num_classes"] = config_data["num_classes"]
    data["lr"] = config_data["lr"]
    data["max_epoch"] = config_data["max_epoch"]
    data["save_dir"] = config_data["save_dir"]
    data["model_path"] = config_data["model_path"]
    data["device"] = config_data["device"]
    data["sample"] = config_data["sample"]
    data["optimizer"] = config_data["optimizer"]
    data["lr_decay_ratio"] = config_data["lr_decay_ratio"]
    if config_data:
        response = {
            "code": 0,
            "status": True,
            "message": "OK",
            "data": data
        }
    else:
        response = {
            "code": 0,
            "status": False,
            "message": "读取配置失败",
            "data": {}
        }

    return response


import subprocess


# 定义打开文件夹的接口
@app.get("/bj/openFolder")
def open_folder():
    config = load_config('./config/config.json')
    folderPath = config['save_dir']
    try:
        # 检查文件夹是否存在
        if not os.path.isdir(folderPath):
            raise HTTPException(status_code=400, detail="指定的路径不是有效的文件夹" + folderPath)
        if os.name == 'nt':  # Windows
            os.startfile(folderPath)
        elif os.name == 'posix':  # Linux / macOS
            subprocess.run(['xdg-open', folderPath])
        # 返回文件夹路径
        return {
            "code": 0,
            "status": True,
            "message": "OK",
            "folderPath": folderPath
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"内部服务器错误: {str(e)}")


# 应用关闭时保存分数
@app.on_event("shutdown")
def on_shutdown():
    scores_manager_all.save_scores()
    scores_manager_for_log.save_scores()
    scores_manager_for_netdata.save_scores()
    logger.info("程序关闭，分数已保存。")


# 主程序入口
if __name__ == "__main__":
    import uvicorn
    from threading import Thread


    # 请求课题三并评分
    def run_tasks():
        config = load_config('./config/config.json')
        schedule_task(config)


    # 启动一个新线程来运行任务
    Thread(target=run_tasks).start()

    # 启动uvicorn服务器
    uvicorn.run(app, host="localhost", port=8000)
