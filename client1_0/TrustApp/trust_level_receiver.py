import logging
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

# 设置日志记录
logging.basicConfig(filename='../result/received_trust_level.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')

app = FastAPI()

# 请求模型
class TrustLevelResult(BaseModel):
    deviceId: str
    trustLevel: str

# 接收信任级别结果并记录
@app.post("/deviceTrustLevelResult")
async def receive_trust_level_result(result: TrustLevelResult, request: Request):
    try:
        # 记录接收到的信息
        logging.info(f"Received data from {request.client.host}: {result.json()}")
        return {"code": "200", "msg": "接收成功", "data": result.dict()}
    except Exception as e:
        logging.error(f"Failed to process received data: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# 运行应用程序
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8067)
