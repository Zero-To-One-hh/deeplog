# -*- coding: utf-8 -*-

import logging
import sys
import datetime
import time
import torch
import httpx
import json
import threading
from collections import Counter, deque, defaultdict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

sys.path.append("..")

# 配置日志记录
logging.basicConfig(level=logging.INFO, filename='../app.log', filemode='a',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 常量文件路径
SCORES_FILE = '../TrustApp/config/scores.json'
CONFIG_FILE = '../TrustApp/config/config.json'

# 从 config.json 加载配置
def load_config():
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            # 如果配置文件中未指定，设置默认值
            config.setdefault('decrements', {'browserScore': 1, 'deviceScore': 1, 'serviceScore': 1})
            config.setdefault('reset_interval_seconds', 3 * 3600)
            config.setdefault('save_interval_seconds', 600)  # 新增：分数保存间隔，默认10分钟
            config.setdefault('api_request_interval_seconds', 300)  # 新增：API请求间隔，默认5分钟
            config.setdefault('window_size', 10)
            config.setdefault('device', "cpu")
            config.setdefault('sample', "sliding_window")
            config.setdefault('sequentials', True)
            config.setdefault('quantitatives', False)
            config.setdefault('semantics', False)
            config.setdefault('feature_num', 1)
            config.setdefault('input_size', 1)
            config.setdefault('hidden_size', 64)
            config.setdefault('num_layers', 2)
            config.setdefault('num_classes', 676)
            config.setdefault('batch_size', 2048)
            config.setdefault('accumulation_step', 1)
            config.setdefault('optimizer', 'adam')
            config.setdefault('lr', 0.001)
            config.setdefault('max_epoch', 370)
            config.setdefault('lr_step', (300, 350))
            config.setdefault('lr_decay_ratio', 0.1)
            config.setdefault('resume_path', None)
            config.setdefault('model_name', "deeplog")
            config.setdefault('save_dir', f"./result/deeplog{time.strftime('%Y_%m_%d', time.localtime())}/")
            config.setdefault('model_path', "../deeplog2024_06_15/deeplog_bestloss.pth")
            config.setdefault('num_candidates', 9)
            return config
    except FileNotFoundError:
        logger.error("未找到配置文件。")
        raise

config = load_config()

window_size = config['window_size']

app = FastAPI()

# 请求和响应模型
class DeviceTrustLevelRequest(BaseModel):
    browserId: str
    logId: str
    deviceMac: str
    deviceIp: str
    accessPort: int
    serviceId: str
    accessedIp: str
    rawLog: str
    timestamp: str

class DeviceTrustLevelResponse(BaseModel):
    code: str
    msg: str
    data: dict

# 辅助函数，用于创建三元组键
def triplet_key(browserId, deviceMac, serviceId):
    return (browserId, deviceMac, serviceId)

# 从 scores.json 加载分数
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
        logger.info("分数文件未找到，初始化为空的分数数据。")
        return {
            'browsers': {},
            'devices': {},
            'services': {}
        }

# 保存分数到 scores.json
def save_scores():
    with scores_lock:
        with open(SCORES_FILE, 'w') as f:
            # 将 datetime 对象转换为字符串
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

# 初始化分数并加载已有数据
scores_lock = threading.Lock()
scores_data = load_scores()
scores = {
    'browsers': defaultdict(lambda: {'score': 100, 'last_reset': datetime.datetime.now()}),
    'devices': defaultdict(lambda: {'score': 100, 'last_reset': datetime.datetime.now()}),
    'services': defaultdict(lambda: {'score': 100, 'last_reset': datetime.datetime.now()})
}

for entity_type in ['browsers', 'devices', 'services']:
    scores[entity_type].update(scores_data.get(entity_type, {}))

# 定期保存分数的线程
def periodic_save_scores():
    save_interval = config.get('save_interval_seconds', 600)
    while True:
        time.sleep(save_interval)
        save_scores()
        logger.info("分数已定期保存。")

# 启动定期保存分数的线程
save_thread = threading.Thread(target=periodic_save_scores, daemon=True)
save_thread.start()

# 全局日志队列
device_logs = defaultdict(lambda: deque(maxlen=window_size + 1))  # 窗口大小 +1 用于预测

# 辅助函数
def adjust_scores(triplet, result):
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
        # 注释掉立即保存分数，改为定期保存
        # save_scores()

def send_trust_level_result(triplet, result):
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
                raise HTTPException(status_code=response.status_code, detail="回调失败")
    except httpx.RequestError as e:
        logger.error(f"请求错误: {e.request.url!r}.")
        raise HTTPException(status_code=500, detail="回调请求失败")

def process_triplet_logs(triplet):
    try:
        result = predict_triplet_log_sequence(triplet)
        adjust_scores(triplet, result)
        send_trust_level_result(triplet, result)
    except Exception as e:
        logger.error(f"处理三元组日志时出错: {e}")
        raise

def predict_triplet_log_sequence(triplet):
    try:
        config['test_data'] = list(device_logs[triplet])
        result = predict_single_log(config['test_data'])
        return result  # "Anomaly" 或 "Normal"
    except Exception as e:
        logger.error(f"预测三元组日志序列时出错: {e}")
        raise HTTPException(status_code=500, detail="预测失败")

def predict_single_log(log):
    if len(log) != window_size + 1:
        raise ValueError(f"输入日志长度必须为 {window_size + 1}.")

    seq = list(map(lambda n: n - 1, log))
    seq0 = seq[:window_size]
    label = seq[window_size]
    seq1 = [0] * config['num_classes']
    log_counter = Counter(seq0)
    for key in log_counter:
        seq1[key] = log_counter[key]

    seq0 = torch.tensor(seq0, dtype=torch.float).view(-1, window_size, config['input_size']).to(config['device'])
    seq1 = torch.tensor(seq1, dtype=torch.float).view(-1, config['num_classes'], config['input_size']).to(config['device'])
    label = torch.tensor(label).view(-1).to(config['device'])
    output = Model(features=[seq0, seq1], device=config['device'])
    predicted = torch.argsort(output, 1)[0][-config['num_candidates']:]
    if label not in predicted:
        return "Anomaly"
    return "Normal"

# 加载模型
try:
    sys.path.append('path_to_model_directory')  # 更新为正确的路径
    from lstm import deeplog

    Model = deeplog(input_size=config['input_size'],
                    hidden_size=config['hidden_size'],
                    num_layers=config['num_layers'],
                    num_keys=config['num_classes'])
    Model.load_state_dict(torch.load(config['model_path'])['state_dict'])
    Model.to(config['device'])
    Model.eval()
    logger.info("模型加载成功")
except Exception as e:
    logger.error(f"加载模型时出错: {e}")
    raise

# 日志采集接口
@app.post("/deviceTrustLevelModel", response_model=DeviceTrustLevelResponse)
async def process_log_entry(request: DeviceTrustLevelRequest):
    try:
        EventId = int(request.logId)

        with open('event_ids.txt', 'a') as file:
            file.write(f'{EventId}\n')

        triplet = triplet_key(request.browserId, request.deviceMac, request.serviceId)
        device_logs[triplet].append(EventId)

        print(device_logs[triplet])

        if len(device_logs[triplet]) <= window_size:
            return DeviceTrustLevelResponse(code="200", msg="日志条目不足", data={})

        process_triplet_logs(triplet)
        return DeviceTrustLevelResponse(code="200", msg="请求成功", data={})
    except Exception as e:
        logger.error(f"处理日志条目时出错: {e}")
        raise HTTPException(status_code=500, detail="内部服务器错误")

# 应用关闭时保存分数
def on_shutdown():
    save_scores()
    logger.info("程序关闭，分数已保存。")

# 主程序入口
if __name__ == "__main__":
    import uvicorn
    import atexit

    # 注册程序退出时的回调函数
    atexit.register(on_shutdown)

    # # 启动定期请求风险MAC地址的线程
    # from mac_risk_monitor import MacRiskMonitor
    # mac_monitor = MacRiskMonitor(scores, scores_lock, config)
    # mac_monitor.start()

    uvicorn.run(app, host="localhost", port=8000)
