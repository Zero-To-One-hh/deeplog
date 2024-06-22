from collections import Counter, deque, defaultdict
import httpx
import torch
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from lstm import deeplog
import asyncio
import Parser
import time
import requests
from fastapi import HTTPException

# Config Parameters
options = {
    'train_data': './data/Kylin/train',
    'val_data': './data/Kylin/valid',
    'test_data': './data/Kylin/test',
    'data_dir': './data/',
    'window_size': 10,
    'device': "cpu",
    'sample': "sliding_window",
    'sequentials': True,
    'quantitatives': False,
    'semantics': False,
    'feature_num': 1,  # sum of sequentials, quantitatives, semantics
    'input_size': 1,
    'hidden_size': 64,
    'num_layers': 2,
    'num_classes': 676,
    'batch_size': 2048,
    'accumulation_step': 1,
    'optimizer': 'adam',
    'lr': 0.001,
    'max_epoch': 370,
    'lr_step': (300, 350),
    'lr_decay_ratio': 0.1,
    'resume_path': None,
    'model_name': "deeplog",
    'save_dir': f"./result/deeplog{time.strftime('%Y_%m_%d', time.localtime())}/",
    'model_path': "./result/deeplog2024_06_15/deeplog_bestloss.pth",
    'num_candidates': 9,
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

class Predicter:
    def __init__(self, model, options):
        self.device = options['device']
        self.model = model
        self.model_path = options['model_path']
        self.window_size = options['window_size']
        self.num_candidates = options['num_candidates']
        self.num_classes = options['num_classes']
        self.input_size = options['input_size']
        self.test_data = options['test_data']

        self.model.load_state_dict(torch.load(self.model_path)['state_dict'])
        self.model.to(self.device)
        self.model.eval()

    def process_data(self, data):
        ln = list(map(lambda n: n - 1, map(int, data.strip().split())))
        ln = ln + [-1] * (self.window_size + 1 - len(ln))
        hdfs = {tuple(ln): 1}
        return hdfs

    def predict(self):
        line = self.test_data
        seq0 = line[:self.window_size]

        seq0 = list(map(int, seq0))

        label = line[self.window_size]

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

async def predict_trust_level(deviceId):
    options['test_data'] = list(device_logs[deviceId])
    model = deeplog(input_size=options['input_size'], hidden_size=options['hidden_size'],
                    num_layers=options['num_layers'], num_keys=options['num_classes'])
    predicter = Predicter(model, options)
    loop = asyncio.get_event_loop()
    trust_level = await loop.run_in_executor(None, predicter.predict)
    return trust_level

# async def send_trust_level_result(deviceId, trust_level):
#     callback_url = "https://localhost:8067/deviceTrustLevelResult"
#     callback_data = {"deviceId": deviceId, "trustLevel": trust_level}
#     async with httpx.AsyncClient() as client:
#         response = await client.post(callback_url, json=callback_data)
#         if response.status_code != 200:
#             raise HTTPException(status_code=response.status_code, detail="Callback failed")

# def send_trust_level_result(deviceId, trust_level):
#     callback_url = "https://localhost:8067/deviceTrustLevelResult"
#     callback_data = {"deviceId": deviceId, "trustLevel": trust_level}
#     try:
#         with httpx.Client() as client:
#             response = client.post(callback_url, json=callback_data)
#             if response.status_code != 200:
#                 raise HTTPException(status_code=response.status_code, detail="Callback failed")
#     except httpx.RequestError as exc:
#         raise HTTPException(status_code=500, detail=f"An error occurred while requesting {exc.request.url}") from exc

def send_trust_level_result(deviceId, trust_level):
    callback_url = "http://localhost:8067/deviceTrustLevelResult"  # 注意将 https 改为 http
    callback_data = {"deviceId": deviceId, "trustLevel": trust_level}
    try:
        response = requests.post(callback_url, json=callback_data)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Callback failed")
    except requests.RequestException as exc:
        raise HTTPException(status_code=500, detail=f"An error occurred while requesting {exc.request.url}") from exc


async def process_device_trust_level(deviceId):
    trust_level = await predict_trust_level(deviceId)
    await send_trust_level_result(deviceId, trust_level)

@app.post("/deviceTrustLevelModel", response_model=DeviceTrustLevelResponse)
async def device_trust_level_model(request: DeviceTrustLevelRequest):
    EventId = Parser.process_data(request.logMessage)
    device_logs[request.deviceId].append(EventId)
    if len(device_logs[request.deviceId]) <= window_size:
        return DeviceTrustLevelResponse(code="200", msg="日志条目不足", data={})
    asyncio.create_task(process_device_trust_level(request.deviceId))
    return DeviceTrustLevelResponse(code="200", msg="请求成功", data={})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
