import logging
import sys
import time
from collections import Counter, deque, defaultdict

import torch
import torch.nn as nn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx

from TrustApp import Parser

sys.path.append("..")


# 配置日志记录到文件
logging.basicConfig(level=logging.INFO, filename='../app.log', filemode='a',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 配置参数
options = {
    'window_size': 10,
    'device': "cpu",
    'sample': "sliding_window",
    'feature_num': 1,
    'input_size': 1,
    'hidden_size': 64,
    'num_layers': 2,
    'num_classes': 676,
    'accumulation_step': 1,
    'optimizer': 'adam',
    'lr': 0.001,
    'max_epoch': 370,
    'lr_step': (300, 350),
    'lr_decay_ratio': 0.1,
    'resume_path': None,
    'model_name': "deeplog",
    'save_dir': f"./result/deeplog{time.strftime('%Y_%m_%d', time.localtime())}/",
    'model_path': "../deeplog2024_06_15/deeplog_bestloss.pth",
    'data_dir': './data',
    'num_candidates': 9,
    'sequentials': True,
    'quantitatives': True,
    'semantics': True,
    'batch_size': 32,
    'test_data': './test_data.txt'
}

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
        self.data_dir = options['data_dir']
        self.device = options['device']
        self.model = model
        self.model_path = options['model_path']
        self.window_size = options['window_size']
        self.num_candidates = options['num_candidates']
        self.num_classes = options['num_classes']
        self.input_size = options['input_size']
        self.sequentials = options['sequentials']
        self.quantitatives = options['quantitatives']
        self.semantics = options['semantics']
        self.batch_size = options['batch_size']
        self.test_data = options['test_data']

    def load_model(self):
        self.model.to(self.device)
        self.model.load_state_dict(torch.load(self.model_path)['state_dict'])
        self.model.eval()

    def predict(self, logs):
        model = self.model
        window_size = self.window_size
        input_size = self.input_size
        num_classes = self.num_classes
        num_candidates = self.num_candidates

        results = []
        with torch.no_grad():
            for line in logs:
                line = list(map(lambda n: n - 1, line))
                for i in range(len(line) - window_size):
                    seq0 = line[i:i + window_size]
                    label = line[i + window_size]
                    seq1 = [0] * num_classes
                    log_counter = Counter(seq0)
                    for key in log_counter:
                        seq1[key] = log_counter[key]

                    print(f"Window {i}: {seq0}, Label: {label}")

                    seq0 = torch.tensor(seq0, dtype=torch.float).view(-1, window_size, input_size).to(self.device)
                    seq1 = torch.tensor(seq1, dtype=torch.float).view(-1, num_classes, input_size).to(self.device)
                    label = torch.tensor(label).view(-1).to(self.device)
                    output = model(features=[seq0, seq1], device=self.device)
                    predicted = torch.argsort(output, 1)[0][-num_candidates:]
                    if label not in predicted:
                        results.append('abnormal')
                        break
                else:
                    results.append('normal')
        return results

# 示例代码，创建模型并加载它
class DummyModel(nn.Module):
    def __init__(self):
        super(DummyModel, self).__init__()
        # 你的模型定义

    def forward(self, features, device):
        # 你的模型前向传播逻辑
        return torch.randn(1, 676)  # 返回模拟输出

# 创建预测器实例
model = DummyModel()
predicter = Predicter(model, options)
predicter.load_model()

def predict_trust_level(deviceId):
    try:
        options['test_data'] = list(device_logs[deviceId])
        trust_level = predicter.predict(options['test_data'])
        return trust_level
    except Exception as e:
        logger.error(f"Error in predict_trust_level: {e}")
        raise HTTPException(status_code=500, detail="Prediction failed")

def send_trust_level_result(deviceId, trust_level):
    callback_url = "http://localhost:8067/deviceTrustLevelResult"
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
        tmp = logMessage.strip()
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
