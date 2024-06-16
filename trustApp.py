from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from parse import single_log_match
import httpx
import asyncio

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


# 提交设备信任级别数据的接口
@app.post("/deviceTrustLevelModel", response_model=DeviceTrustLevelResponse)
async def device_trust_level_model(request: DeviceTrustLevelRequest):
    # 这里可以添加处理逻辑，例如保存数据或调用其他服务
    print(f"Received request data: {request}")

    logMessage = request.logMessage
    single_log_match.process_log(logMessage)

    # 模拟异步处理，假设处理完成后返回结果
    await asyncio.sleep(1)

    # 模拟处理结果 todo:接入自学习模块
    trust_level = "正常"  # 根据实际处理逻辑生成信任评估等级

    # 异步调用自学习结果回调的接口
    callback_url = "https://ip:端口/deviceTrustLevelResult"
    callback_data = {
        "deviceId": request.deviceId,
        "trustLevel": trust_level
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(callback_url, json=callback_data)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Callback failed")

    response = DeviceTrustLevelResponse(code="200", msg="请求成功", data={})
    return response


# 运行应用程序
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
