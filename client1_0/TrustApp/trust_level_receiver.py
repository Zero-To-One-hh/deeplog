import logging
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import datetime

# 设置日志记录
logging.basicConfig(filename='../result/received_trust_level.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI()

# 请求模型
class TrustLevelResult(BaseModel):
    browserId: str
    deviceMac: str
    serviceId: str
    browserScore: int
    deviceScore: int
    serviceScore: int
    result: str

# 接收信任级别结果并记录
@app.post("/deviceTrustLevelResult")
async def receive_trust_level_result(result: TrustLevelResult, request: Request):
    try:
        # 记录接收到的信息
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        logger.info(f"[{timestamp}] Received data from {request.client.host}: {result.json()}")

        # 返回成功响应
        return {"code": "200", "msg": "接收成功", "data": result.dict()}
    except Exception as e:
        logger.error(f"Failed to process received data: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# 运行应用程序
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8067)
