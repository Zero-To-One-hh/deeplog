import logging
import sys

sys.path.append("..")
# 配置日志记录到文件
logging.basicConfig(level=logging.INFO, filename='../app.log', filemode='a',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 你的代码
from collections import Counter, deque, defaultdict
import torch
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import Parser
from lstm import deeplog
import time
import httpx

# 配置参数
options = {'window_size': 10, 'device': "cpu", 'sample': "sliding_window", 'sequentials': True, 'quantitatives': False,
           'semantics': False, 'feature_num': 1, 'input_size': 1, 'hidden_size': 64, 'num_layers': 2,
           'num_classes': 676, 'batch_size': 2048, 'accumulation_step': 1, 'optimizer': 'adam', 'lr': 0.001,
           'max_epoch': 370, 'lr_step': (300, 350), 'lr_decay_ratio': 0.1, 'resume_path': None, 'model_name': "deeplog",
           'save_dir': f"./result/deeplog{time.strftime('%Y_%m_%d', time.localtime())}/",
           'model_path': "../deeplog2024_06_15/deeplog_bestloss.pth", 'num_candidates': 9}

# Model Parameters

# Predict Parameters

app = FastAPI()


# 请求和响应模型
class DeviceTrustLevelRequest(BaseModel):
    deviceId: str
    appId: str
    targetIp: str
    targetPort: int
    status: str
    userId: str
    level: str
    agreement: str
    logMessage: str


class DeviceTrustLevelResponse(BaseModel):
    code: str
    msg: str
    data: dict


# 全局存储每个设备的日志序列，使用队列管理
device_logs = defaultdict(lambda: deque(maxlen=11))  # 窗口大小为10，加1用于预测下一条
window_size = 10

month = {
    'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
}

class Predicter:
    def __init__(self, model, options):
        self.device = options['device']
        self.model = model
        self.window_size = options['window_size']
        self.num_candidates = options['num_candidates']
        self.num_classes = options['num_classes']
        self.input_size = options['input_size']

        self.model.to(self.device)
        self.model.eval()

    def process_data(self, data):
        ln = list(map(lambda n: n - 1, map(int, data.strip().split())))
        ln = ln + [-1] * (self.window_size + 1 - len(ln))
        hdfs = {tuple(ln): 1}
        return hdfs

    def predict(self, data):
        try:
            seq0 = data[:self.window_size]
            seq0 = list(map(int, seq0))
            label = data[self.window_size]
            seq1 = [0] * self.num_classes
            log_counter = Counter(seq0)
            for key in log_counter:
                seq1[key] = log_counter[key]
            seq0 = torch.tensor(seq0, dtype=torch.float).view(-1, self.window_size, self.input_size).to(self.device)
            seq1 = torch.tensor(seq1, dtype=torch.float).view(-1, self.num_classes, self.input_size).to(self.device)
            label = torch.tensor(label).view(-1).to(self.device)
            output = self.model(features=[seq0, seq1], device=self.device)
            predicted = torch.argsort(output, 1)[0][-self.num_candidates:]
            return "异常" if label not in predicted else "正常"
        except Exception as e:
            logger.error(f"Error in predict: {e}")
            raise


# 预先加载模型
try:
    Model = deeplog(input_size=options['input_size'],
                    hidden_size=options['hidden_size'],
                    num_layers=options['num_layers'],
                    num_keys=options['num_classes'])
    Model.load_state_dict(torch.load(options['model_path'])['state_dict'])
    Model.to(options['device'])
    Model.eval()
    logger.info("Model loaded successfully")
except Exception as e:
    logger.error(f"Error loading model: {e}")
    raise


def predict_single_log(log):
    if len(log) != 11:
        raise ValueError("The input log must be a list of length 11.")

    window_size = options['window_size']
    seq = list(map(lambda n: n - 1, log))
    for i in range(len(seq) - window_size):
        seq0 = seq[i:i + window_size]
        label = seq[i + window_size]
        seq1 = [0] * options['num_classes']
        log_counter = Counter(seq0)
        for key in log_counter:
            seq1[key] = log_counter[key]

        seq0 = torch.tensor(seq0, dtype=torch.float).view(-1, window_size, options['input_size']).to(options['device'])
        seq1 = torch.tensor(seq1, dtype=torch.float).view(-1, options['num_classes'], options['input_size']).to(
            options['device'])
        label = torch.tensor(label).view(-1).to(options['device'])
        output = Model(features=[seq0, seq1], device=options['device'])
        predicted = torch.argsort(output, 1)[0][-options['num_candidates']:]
        if label not in predicted:
            return "Anomaly"
    return "Normal"


def predict_trust_level(deviceId):
    try:
        options['test_data'] = list(device_logs[deviceId])
        trust_level = predict_single_log(options['test_data'])
        return trust_level
    except Exception as e:
        logger.error(f"Error in predict_trust_level: {e}")
        raise HTTPException(status_code=500, detail="Prediction failed")


def send_trust_level_result(deviceId, trust_level):
    callback_url = "http://localhost:8067/deviceTrustLevelResult"  # 注意将 https 改为 http
    callback_data = {"deviceId": deviceId, "trustLevel": trust_level}
    try:
        with httpx.Client() as client:
            response = client.post(callback_url, json=callback_data)
            if response.status_code != 200:
                logger.error(f"Callback failed with status code {response.status_code}")
                raise HTTPException(status_code=response.status_code, detail="Callback failed")
    except httpx.RequestError as e:
        logger.error(f"An error occurred while requesting {e.request.url!r}.")
        raise HTTPException(status_code=500, detail="Callback request failed")


def process_device_trust_level(deviceId):
    try:
        trust_level = predict_trust_level(deviceId)
        send_trust_level_result(deviceId, trust_level)
    except Exception as e:
        logger.error(f"Error in process_device_trust_level: {e}")
        raise


@app.post("/deviceTrustLevelModel", response_model=DeviceTrustLevelResponse)
async def device_trust_level_model(request: DeviceTrustLevelRequest):
    try:
        logMessage = request.logMessage
        tmp = logMessage.strip()  # 移出首尾空格
        tmp1 = tmp.split()
        if len(tmp1) == 0 or tmp1[0] not in month:
            return DeviceTrustLevelResponse(code="200", msg="非日志message", data={})

        EventId = Parser.process_data(logMessage)

        with open('event_ids.txt', 'a') as file:
            file.write(f'{EventId}\n')

        device_logs[request.deviceId].append(EventId)

        print(device_logs[request.deviceId])

        if len(device_logs[request.deviceId]) <= window_size:
            return DeviceTrustLevelResponse(code="200", msg="日志条目不足", data={})
        process_device_trust_level(request.deviceId)
        return DeviceTrustLevelResponse(code="200", msg="请求成功", data={})
    except Exception as e:
        logger.error(f"Error in device_trust_level_model: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)
