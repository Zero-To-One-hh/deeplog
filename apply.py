import asyncio
import httpx

async def submit_device_trust_level(log_message: str, device_id: str):
    url = "http://your-server-url/deviceTrustLevelModel"  # 替换为实际服务器的URL
    payload = {
        "logMessage": log_message,
        "deviceId": device_id
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
        if response.status_code == 200:
            print("Request successful!")
            print("Response data:", response.json())
        else:
            print("Request failed with status code:", response.status_code)
            print("Error detail:", response.text)

# 示例日志消息和设备ID
log_message = "- 1117989506 2005.06.05 R30-M0-N1-C:J05-U01 2005-06-05-09.38.26.892021 R30-M0-N1-C:J05-U01 RAS KERNEL INFO generating core.1587"
device_id = "device123"

# 调用函数
asyncio.run(submit_device_trust_level(log_message, device_id))
