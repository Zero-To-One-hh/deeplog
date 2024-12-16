import httpx

def send_post_request(url, payload, timeout=10.0):  # 设置超时时间为10秒
    try:
        response = httpx.post(url, json=payload, timeout=timeout)
        response.raise_for_status()  # 如果状态码不是200，抛出异常
        return response
    except httpx.RequestError as exc:
        print(f"An error occurred while requesting {exc.request.url!r}: {exc}")
    except httpx.HTTPStatusError as exc:
        print(f"Error response {exc.response.status_code} while requesting {exc.request.url!r}: {exc}")
    return None

def main():
    url = "http://192.168.83.136:8000/deviceTrustLevelModel"  # 将 <麒麟系统的IP地址> 替换为实际的IP地址
    payload = {
        "deviceId": "device123",
        "appId": "app456",
        "targetIp": "192.168.0.1",
        "targetPort": 8080,
        "status": "active",
        "userId": "user789",
        "level": "high",
        "agreement": "agreement123",
        "logMessage": "Jan 1 00:00:00 device123 log message example"
    }

    print(f"Sending payload: {payload}")  # 打印发送的 payload
    response = send_post_request(url, payload)

    if response is not None:
        print(f"Response: {response.status_code}")
        try:
            response_json = response.json()
            print(f"Response JSON: {response_json}")
        except ValueError:
            print(f"Response is not valid JSON: {response.text}")

if __name__ == "__main__":
    main()
