import httpx
import asyncio


async def send_post_request(client, url, payload):
    response = await client.post(url, json=payload)
    return response


async def main():
    url = "http://localhost:8000/deviceTrustLevelModel"
    payload_template = {
        "deviceId": "device123",
        "appId": "app456",
        "targetIp": "192.168.0.1",
        "targetPort": 8080,
        "status": "active",
        "userId": "user789",
        "level": "high",
        "agreement": "agreement123",
        "logMessage": ""
    }

    # 读取日志文件，指定编码为 utf-8
    log_file_path = "messages.txt"
    with open(log_file_path, "r", encoding="utf-8") as file:
        log_lines = file.readlines()

    # 限制只发送前100行
    log_lines = log_lines[:30]

    async with httpx.AsyncClient() as client:
        tasks = []
        for log_message in log_lines:
            payload = payload_template.copy()
            payload["logMessage"] = log_message.strip()
            tasks.append(send_post_request(client, url, payload))

        responses = await asyncio.gather(*tasks)

        for i, response in enumerate(responses):
            print(f"Response {i + 1}: {response.status_code}, {response.json()}")


if __name__ == "__main__":
    asyncio.run(main())
