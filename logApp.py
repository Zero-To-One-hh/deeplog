from fastapi import FastAPI, HTTPException, Request
import logging
import uvicorn

app = FastAPI()

# 设置日志记录
log_file_path = "device_trust_level_log.txt"
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filename=log_file_path, filemode='a')
logger = logging.getLogger(__name__)

@app.post("/deviceTrustLevelResult")
async def device_trust_level_result(request: Request):
    try:
        data = await request.json()
        device_id = data.get("deviceId")
        trust_level = data.get("trustLevel")

        if not device_id or not trust_level:
            raise HTTPException(status_code=400, detail="Invalid request: Missing 'deviceId' or 'trustLevel'")

        # 记录日志
        logger.info(f"Received trust level result: deviceId={device_id}, trustLevel={trust_level}")

        return {"status": "success"}
    except Exception as e:
        logger.error(f"Failed to process request: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8067)
